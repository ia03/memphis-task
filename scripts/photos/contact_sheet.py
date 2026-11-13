"""Contact sheets of the photo library grouped by label type, for review.

Usage: PYTHONPATH=. .venv/bin/python scripts/photos/contact_sheet.py OUT_DIR [--per-row 3] [--rows 1] [--only SUBSTR]
Writes OUT_DIR/<group>-NN.jpg; every thumbnail is captioned with its file name (and lamp key where relevant).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
PHOTOS = ROOT / "world" / "photos"


def groups() -> dict[str, list[tuple[str, str]]]:
    m = json.loads((ROOT / "world" / "photo_manifest.json").read_text())
    out: dict[str, list[tuple[str, str]]] = {"items": [], "lamps": [], "heads": [], "parts": [], "scene": [], "neutral": [], "backdrops": []}
    for key, files in m["items"].items():
        out["items"] += [(f, key) for f in files]
    for key, files in m["lamps"].items():
        out["lamps"] += [(f, key) for f in files]
    for light, sizes in m["heads"].items():
        for size, files in sizes.items():
            out["heads"] += [(f, f"{light} {size}") for f in files]
    for key, files in m["parts"].items():
        out["parts"] += [(f, key) for f in files]
    out["scene"] = [(f, "scene") for f in m["scene"]]
    out["neutral"] = [(f, "neutral") for f in m["neutral"]]
    out["backdrops"] = [(f, "backdrop") for f in m["invoice_backdrops"]]
    return out


def sheet(entries: list[tuple[Path, str]], per_row: int, out: Path) -> None:
    tw, th, cap = 480, 853, 54
    rows = (len(entries) + per_row - 1) // per_row
    img = Image.new("RGB", (tw * per_row, (th + cap) * rows), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(ROOT / "world" / "fonts" / "NotoSans-Variable.ttf"), 17)
    for i, (path, caption) in enumerate(entries):
        x, y = (i % per_row) * tw, (i // per_row) * (th + cap)
        if path.exists():
            t = Image.open(path).convert("RGB")
            t.thumbnail((tw - 6, th - 6))
            img.paste(t, (x + (tw - t.width) // 2, y + (th - t.height) // 2))
        else:
            d.text((x + 20, y + th // 2), "MISSING", fill="red", font=font)
        d.text((x + 6, y + th + 2), path.name[:52], fill="black", font=font)
        d.text((x + 6, y + th + 26), caption[:52], fill="#444", font=font)
    img.save(out, "JPEG", quality=82)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("--per-row", type=int, default=3)
    p.add_argument("--rows", type=int, default=1)
    p.add_argument("--only", default="")
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = a.per_row * a.rows
    for group, entries in groups().items():
        entries = [(PHOTOS / f, k) for f, k in entries if a.only in f]
        for i in range(0, len(entries), n):
            sheet(entries[i:i + n], a.per_row, out / f"{group}-{i // n + 1:02d}.jpg")


if __name__ == "__main__":
    main()
