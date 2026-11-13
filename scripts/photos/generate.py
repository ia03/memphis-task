"""Generate missing photos in world/photos from scripts/photos/prompts.json with Codex CLI's image tool.

Usage: PYTHONPATH=. .venv/bin/python scripts/photos/generate.py [--jobs 6] [--only SUBSTR ...] [--force]
Each image: `codex exec` in a scratch dir writes out.png; it is center-cropped to 9:16, resized to 720x1280, saved as JPEG q78 with no metadata.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PHOTOS = ROOT / "world" / "photos"
SIZE = (720, 1280)


def finish(png: Path, out: Path) -> None:
    img = Image.open(png).convert("RGB")
    w, h = img.size
    tw, th = (SIZE if h >= w else SIZE[::-1])
    scale = max(tw / w, th / h)
    img = img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    left, top = (img.width - tw) // 2, (img.height - th) // 2
    img = img.crop((left, top, left + tw, top + th))
    clean = Image.new("RGB", img.size)
    clean.paste(img)
    clean.save(out, "JPEG", quality=78, optimize=True, progressive=True)


def run(entry: dict[str, str], scratch: Path) -> str:
    out = PHOTOS / entry["file"]
    work = Path(tempfile.mkdtemp(prefix=out.stem + "-", dir=scratch))
    prompt = ("Generate exactly one image with your image generation tool, portrait 9:16 aspect ratio. Image description: "
              f"{entry['prompt']} Then copy the resulting PNG into the current directory as out.png and print its path. Do nothing else.")
    for attempt in range(2):
        try:
            subprocess.run(["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write", prompt], cwd=work,
                           capture_output=True, text=True, timeout=420)
        except subprocess.TimeoutExpired:
            continue
        if (work / "out.png").exists():
            finish(work / "out.png", out)
            return f"ok {entry['file']}"
    return f"FAILED {entry['file']}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--jobs", type=int, default=6)
    p.add_argument("--only", nargs="*", default=[])
    p.add_argument("--force", action="store_true")
    p.add_argument("--scratch", default=tempfile.gettempdir())
    a = p.parse_args()
    entries = json.loads((ROOT / "scripts" / "photos" / "prompts.json").read_text())
    todo = [e for e in entries if (not a.only or any(s in e["file"] for s in a.only)) and (a.force or not (PHOTOS / e["file"]).exists())]
    print(f"{len(todo)} to generate", flush=True)
    scratch = Path(a.scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(a.jobs) as pool:
        for msg in pool.map(lambda e: run(e, scratch), todo):
            print(msg, flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
