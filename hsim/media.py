"""Worker attachments: real run photos where they exist, generated phone photos otherwise (world/photo_manifest.json),
and rendered ride-app screenshots and shop receipts for transaction-specific images.

Labels (Media.make):
  item:<item_key>
  lamp:<structure_key>[:<light_key>:<state>]      state: ok | misfold | low | cannot_hold | unstable
  heads:<n>[:<light_key>]
  ride-quote:<origin>:<destination>:<price_egp>:<minutes>[:<provider>]
  invoice:<supplier_key>:<item_key>:<n>:<cost>
  scene
Anything else gets a neutral photo. A photo never shows facts beyond the label: lamp photos match the structure, the kind of light
and the state; receipts and screenshots print only the label's numbers.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .world import World

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "world" / "photos"
FONTS = ROOT / "world" / "fonts"
MANIFEST = ROOT / "world" / "photo_manifest.json"
DEFAULT_LIGHT = "led-module-2835-12v-1w5-white"

PLACES = {
    "downtown_bab_el_louk": "Bab El Louk, Downtown Cairo",
    "dokki": "Dokki, Giza",
    "manial": "El Manial, Cairo",
    "new_maadi": "New Maadi, Cairo",
    "maadi_degla": "Degla, Maadi, Cairo",
    "hadayek_october": "Hadayek October, 6th of October",
    "sixth_october": "6th of October City, Giza",
    "abbasiya": "Abbasiya, Cairo",
    "helwan": "Helwan, Cairo",
    "hadayek_el_ahram": "Hadayek El Ahram, Giza",
    "mokattam": "Mokattam, Cairo",
    "delivery_area": "Maadi Ring Road, Maadi",
}
ARABIC = re.compile(r"[؀-ۿ][؀-ۿ\s]*[؀-ۿ]|[؀-ۿ]")


def place(key: str) -> str:
    return PLACES.get(key, key.replace("_", " ").title())


def _font(size: int, weight: int = 400, arabic: bool = False) -> ImageFont.FreeTypeFont:
    if arabic:
        f = ImageFont.truetype(str(FONTS / "NotoNaskhArabic-Variable.ttf"), size)
        f.set_variation_by_axes([min(max(weight, 400), 700)])
    else:
        f = ImageFont.truetype(str(FONTS / "NotoSans-Variable.ttf"), size)
        f.set_variation_by_axes([weight, 100])
    return f


def shape_arabic(text: str) -> str:
    """Visual-order Arabic for Pillow without raqm: join letter forms, then reverse (lines here hold Arabic words only)."""
    import arabic_reshaper
    return arabic_reshaper.reshape(text)[::-1]


def split_name(name: str) -> tuple[str, str]:
    """('Arabic part', 'Latin part') of a supplier name such as 'حاربي تيك (Harby Tech) electrician'."""
    arabic = " ".join(m.strip() for m in ARABIC.findall(name))
    latin = ARABIC.sub("", name)
    latin = re.sub(r"\(\s*\d+\s*\)", "", latin)          # walk-in index "(3)" is a sim key, not part of the shop's name
    latin = re.sub(r"\(\s*\)", "", latin).replace("(", "").replace(")", "")
    latin = re.sub(r"\s+,", ",", re.sub(r"\s+", " ", latin)).strip(" ,")
    return arabic, latin


def short_item(name: str) -> str:
    return re.split(r",", name)[0].strip()


def _wrap(text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        if lines and font.getlength(lines[-1] + " " + word) <= width:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines or [""]


# ---------- ride-app screenshot ----------
THEMES = {
    "Uber": {"bg": "#ffffff", "fg": "#111111", "muted": "#6b6b6b", "accent": "#111111", "button_fg": "#ffffff", "sheet": "#ffffff",
             "route": "#111111", "map": "#eef0f2", "road": "#ffffff", "block": "#e2e5e8", "car": "Economy", "title": "Choose a trip",
             "button": "Confirm Economy", "radius": 10},
    "DiDi": {"bg": "#ffffff", "fg": "#1f1f1f", "muted": "#8a8a8a", "accent": "#ff7a2f", "button_fg": "#ffffff", "sheet": "#ffffff",
             "route": "#ff7a2f", "map": "#f3efe9", "road": "#ffffff", "block": "#e8e1d6", "car": "Express", "title": "Select a ride",
             "button": "Confirm", "radius": 34},
    "inDrive": {"bg": "#16181c", "fg": "#f2f2f2", "muted": "#9aa0a6", "accent": "#b8e62e", "button_fg": "#16181c", "sheet": "#1f2227",
                "route": "#b8e62e", "map": "#2a2e33", "road": "#3a3f45", "block": "#30353b", "car": "Ride", "title": "Recommended fare",
                "button": "Find a driver", "radius": 18},
}


def render_ride_quote(origin: str, destination: str, price: str, minutes: str, provider: str, rng: random.Random) -> tuple[Image.Image, list[str]]:
    t = THEMES.get(provider, THEMES["Uber"])
    W, H = 720, 1560
    img = Image.new("RGB", (W, H), t["map"])
    d = ImageDraw.Draw(img)
    # map: block grid, a few roads, a river band
    for _ in range(70):
        x, y = rng.randint(-40, W), rng.randint(60, 980)
        d.rounded_rectangle([x, y, x + rng.randint(40, 140), y + rng.randint(30, 110)], 6, fill=t["block"])
    for _ in range(9):
        x0, y0 = rng.randint(-100, W), rng.randint(40, 1000)
        ang = rng.uniform(0, math.pi)
        d.line([x0 - 900 * math.cos(ang), y0 - 900 * math.sin(ang), x0 + 900 * math.cos(ang), y0 + 900 * math.sin(ang)], fill=t["road"],
               width=rng.choice([10, 14, 22]))
    rx = rng.randint(200, 520)
    river = [(rx + 60 * math.sin(y / 180.0), y) for y in range(40, 1020, 20)]
    d.line(river, fill="#a9cbe8" if provider != "inDrive" else "#25425a", width=46)
    # route
    a = (rng.randint(110, 280), rng.randint(720, 900))
    b = (rng.randint(440, 620), rng.randint(200, 380))
    pts = [a]
    x, y = a
    while abs(x - b[0]) > 30 or abs(y - b[1]) > 30:
        if rng.random() < 0.5:
            x += max(-90, min(90, b[0] - x))
        else:
            y += max(-90, min(90, b[1] - y))
        pts.append((x, y))
    pts.append(b)
    d.line(pts, fill=t["route"], width=9, joint="curve")
    d.ellipse([a[0] - 16, a[1] - 16, a[0] + 16, a[1] + 16], fill="#1fa463", outline="white", width=5)
    d.rectangle([b[0] - 15, b[1] - 15, b[0] + 15, b[1] + 15], fill=t["fg"] if provider != "inDrive" else t["accent"], outline="white", width=5)
    # status bar (no clock: the photo must not invent a time)
    d.rectangle([0, 0, W, 54], fill=t["bg"])
    for i in range(4):
        d.rectangle([590 + i * 9, 36 - i * 6, 595 + i * 9, 40], fill=t["fg"])
    d.rounded_rectangle([640, 22, 684, 40], 4, outline=t["fg"], width=2)
    d.rectangle([643, 25, 672, 37], fill=t["fg"])
    d.rectangle([685, 27, 688, 35], fill=t["fg"])
    # top bar: back arrow + provider name in plain text
    d.ellipse([24, 76, 92, 144], fill=t["sheet"])
    d.line([(68, 98), (48, 110), (68, 122)], fill=t["fg"], width=5)
    d.text((112, 92), provider, font=_font(30, 700), fill=t["fg"] if provider != "inDrive" else t["accent"])
    # bottom sheet
    top = 930
    d.rounded_rectangle([0, top, W, H + 40], 36, fill=t["sheet"])
    d.rounded_rectangle([W // 2 - 40, top + 14, W // 2 + 40, top + 22], 4, fill=t["muted"])
    pick, drop = place(origin), place(destination)
    f_row = _font(28, 500)
    d.ellipse([40, top + 58, 60, top + 78], fill="#1fa463")
    d.text((84, top + 48), pick, font=f_row, fill=t["fg"])
    d.line([(50, top + 84), (50, top + 118)], fill=t["muted"], width=3)
    d.rectangle([41, top + 124, 59, top + 142], fill=t["fg"] if provider != "inDrive" else t["accent"])
    d.text((84, top + 114), drop, font=f_row, fill=t["fg"])
    d.line([(40, top + 172), (W - 40, top + 172)], fill=t["muted"] if provider == "inDrive" else "#e4e4e4", width=2)
    d.text((40, top + 192), t["title"], font=_font(30, 700), fill=t["fg"])
    # selected ride row
    ry = top + 252
    d.rounded_rectangle([28, ry, W - 28, ry + 132], t["radius"] // 2 + 6, outline=t["accent"], width=4)
    d.rounded_rectangle([52, ry + 36, 140, ry + 92], 14, fill=t["block"])
    d.ellipse([62, ry + 78, 82, ry + 98], fill=t["fg"])
    d.ellipse([110, ry + 78, 130, ry + 98], fill=t["fg"])
    d.text((164, ry + 24), t["car"], font=_font(32, 700), fill=t["fg"])
    trip = f"{minutes} min"
    d.text((164, ry + 74), f"Trip time {trip}", font=_font(26, 400), fill=t["muted"])
    price_text = f"EGP {price}"
    f_price = _font(36, 700)
    d.text((W - 52 - f_price.getlength(price_text), ry + 40), price_text, font=f_price, fill=t["fg"])
    d.text((40, ry + 160), "Cash", font=_font(26, 500), fill=t["fg"])
    d.rounded_rectangle([28, H - 170, W - 28, H - 70], t["radius"], fill=t["accent"])
    f_btn = _font(32, 700)
    d.text(((W - f_btn.getlength(t["button"])) / 2, H - 140), t["button"], font=f_btn, fill=t["button_fg"])
    d.rounded_rectangle([W // 2 - 110, H - 22, W // 2 + 110, H - 14], 4, fill=t["fg"])
    return img, [provider, pick, drop, t["car"], f"Trip time {trip}", price_text, "Cash", t["button"]]


# ---------- shop receipt photo ----------
def render_receipt(shop: str, item_name: str, n: str, cost: str, rng: random.Random) -> tuple[Image.Image, list[str]]:
    W = 470
    arabic, latin = split_name(shop)
    item = short_item(item_name)
    f_ar_title, f_ar = _font(46, 700, arabic=True), _font(32, 500, arabic=True)
    f_head, f_body, f_bold = _font(26, 700), _font(23, 400), _font(27, 700)
    lines: list[tuple[str, ImageFont.FreeTypeFont, str, str]] = []  # text, font, align, kind
    lines.append(("فاتورة", f_ar_title, "center", "ar"))
    if arabic:
        lines.append((arabic, f_ar, "center", "ar"))
    for ln in _wrap(latin, f_head, W - 60):
        lines.append((ln, f_head, "center", "en"))
    lines.append((f"No. {rng.randint(10000, 99999)}", f_body, "center", "en"))
    lines.append(("-", f_body, "rule", "en"))
    lines.append(("Item|Qty|Amount", f_head, "cols", "en"))
    item_lines = _wrap(item, f_body, 220)
    lines.append((f"{item_lines[0]}|{n}|{cost}", f_body, "cols", "en"))
    for ln in item_lines[1:]:
        lines.append((ln, f_body, "left", "en"))
    lines.append(("-", f_body, "rule", "en"))
    lines.append((f"Total|EGP {cost}", f_bold, "total", "en"))
    lines.append(("-", f_body, "rule", "en"))
    lines.append(("شكرا لزيارتكم", f_ar, "center", "ar"))
    heights = {"ar": 58, "en": 38}
    H = 50 + sum(heights[k] + (10 if a == "rule" else 0) for _, _, a, k in lines) + 40
    paper = Image.new("RGB", (W, H), (246, 244, 236))
    noise = Image.frombytes("L", (W, H), rng.randbytes(W * H)).convert("RGB")  # seeded, so receipts replay byte for byte
    paper = Image.blend(paper, noise, 0.04)
    shade = Image.linear_gradient("L").rotate(rng.choice([0, 90, 180, 270])).resize((W, H)).point(lambda v: 200 + v // 5)
    paper = Image.composite(paper, Image.new("RGB", (W, H), (205, 202, 192)), shade)
    d = ImageDraw.Draw(paper)
    ink = (38, 38, 42)
    y = 40
    for text, font, align, kind in lines:
        shown = shape_arabic(text) if kind == "ar" else text
        if align == "rule":
            d.line([(24, y + 18), (W - 24, y + 18)], fill=(90, 90, 90), width=2)
            y += 10
        elif align == "cols":
            a, q, amt = text.split("|")
            d.text((26, y), a, font=font, fill=ink)
            d.text((292 - font.getlength(q) / 2, y), q, font=font, fill=ink)
            d.text((W - 26 - font.getlength(amt), y), amt, font=font, fill=ink)
        elif align == "total":
            a, amt = text.split("|")
            d.text((26, y), a, font=font, fill=ink)
            d.text((40 + font.getlength(a), y - 12), shape_arabic("الإجمالي"), font=f_ar, fill=ink)
            d.text((W - 26 - font.getlength(amt), y), amt, font=font, fill=ink)
        elif align == "center":
            d.text(((W - font.getlength(shown)) / 2, y), shown, font=font, fill=ink)
        elif align == "right":
            d.text((W - 26 - font.getlength(shown), y), shown, font=font, fill=ink)
        else:
            d.text((26, y), shown, font=font, fill=ink)
        y += heights[kind]
    # torn top edge as transparency
    alpha = Image.new("L", (W, H), 255)
    edge = [(x, rng.randint(0, 7)) for x in range(0, W + 12, 12)]
    ImageDraw.Draw(alpha).polygon([(0, 0)] + edge + [(W, 0)], fill=0)
    paper.putalpha(alpha)
    texts = ["فاتورة", arabic, latin, item, n, cost, f"EGP {cost}"]
    return paper, texts


def place_receipt(paper: Image.Image, backdrop: Image.Image, rng: random.Random) -> Image.Image:
    bg = backdrop.convert("RGB").resize((720, 1280))
    mask = paper.getchannel("A")
    paper = paper.convert("RGB")
    scale = min(1.0, 1150 / paper.height)
    if scale < 1:
        paper = paper.resize((round(paper.width * scale), round(paper.height * scale)), Image.LANCZOS)
        mask = mask.resize(paper.size)
    angle = rng.uniform(-6, 6)
    p = paper.rotate(angle, resample=Image.BICUBIC, expand=True)
    m = mask.rotate(angle, resample=Image.BICUBIC, expand=True)
    x = (720 - p.width) // 2 + rng.randint(-25, 25)
    y = max(10, (1280 - p.height) // 2 + rng.randint(-30, 30))
    shadow = Image.new("L", bg.size, 0)
    shadow.paste(m, (x + 10, y + 14))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.55))
    bg = Image.composite(Image.new("RGB", bg.size, (0, 0, 0)), bg, shadow)
    bg.paste(p, (x, y), m)
    # uneven light and a little softness, as from a phone held over a counter
    grad = Image.linear_gradient("L").rotate(rng.choice([0, 90, 180, 270])).resize(bg.size)
    bg = Image.composite(bg, Image.blend(bg, Image.new("RGB", bg.size, (0, 0, 0)), 0.22), grad)
    return bg.filter(ImageFilter.GaussianBlur(0.6))


class Media:
    def __init__(self, world: World, out_dir: Path) -> None:
        self.world = world
        self.out = out_dir
        self.out.mkdir(parents=True, exist_ok=True)
        self.manifest = json.loads(MANIFEST.read_text())
        self.calls: Counter[tuple[str, str]] = Counter()
        self.last_text: list[str] = []  # strings drawn on the last rendered image (tests and audits)

    # ---- choosing a photo ----
    def _rng(self, worker_id: str, label: str, n: int) -> random.Random:
        h = hashlib.sha256(f"{self.world.seed}:{worker_id}:{label}:{n}".encode()).hexdigest()
        return random.Random(int(h, 16))

    def resolve(self, label: str) -> list[str]:
        """Candidate photo files for a photo label (empty for rendered labels)."""
        m = self.manifest
        kind, _, rest = label.partition(":")
        if kind == "item":
            item = self.world.items.get(rest)
            if rest in m.get("real_item_overrides", {}):
                return m["real_item_overrides"][rest]  # cleaned copy of a real photo (no price sticker, no other items)
            if item is not None and item.photo:
                return [f"{item.photo}.jpg"]
            return m["items"].get(rest) or m["neutral"]
        if kind == "lamp":
            return self._lamp(rest.split(":"))
        if kind == "heads":
            parts = rest.split(":")
            n = int(parts[0]) if parts[0].isdigit() else 1
            light = parts[1] if len(parts) > 1 and parts[1] else DEFAULT_LIGHT
            sizes = m["heads"].get(light)
            if sizes:
                size = "1" if n <= 1 else "few" if n <= 5 else "many"
                return sizes.get(size) or sizes["few"]
            item = self.world.items.get(light)
            if item is not None and item.photo:
                return [f"{item.photo}.jpg"]
            return m["items"].get(light) or m["parts"].get(m["light_groups"].get(light, ""), []) or m["neutral"]
        if kind == "scene":
            return m["scene"]
        return m["neutral"]

    def _lamp(self, parts: list[str]) -> list[str]:
        m = self.manifest
        structure = parts[0]
        light = parts[1] if len(parts) > 1 and parts[1] else DEFAULT_LIGHT
        sgroup = m["structure_groups"].get(structure)
        lgroup = m["light_groups"].get(light)
        if sgroup is None or lgroup is None:
            return m["parts"].get(lgroup or "", []) or m["neutral"]
        reachable = m["reachable_states"][sgroup]
        # Old two-field label: no state given, so use the structure's own outcome (ok where ok is reachable).
        state = parts[2] if len(parts) > 2 and parts[2] else ("ok" if "ok" in reachable else reachable[0])
        return m["lamps"].get(f"{sgroup}|{lgroup}|{state}") or m["parts"][lgroup]

    # ---- public ----
    def make(self, worker_id: str, label: str) -> str:
        n = self.calls[(worker_id, label)]
        self.calls[(worker_id, label)] += 1
        rng = self._rng(worker_id, label, n)
        name = hashlib.sha256(f"{self.world.seed}:{worker_id}:{label}:{n}".encode()).hexdigest()[:16] + ".jpg"
        path = self.out / name
        kind, _, rest = label.partition(":")
        self.last_text = []
        if kind == "ride-quote" and len(rest.split(":")) >= 4:
            p = rest.split(":")
            provider = p[4] if len(p) > 4 and p[4] else rng.choice(["Uber", "DiDi", "inDrive"])
            img, self.last_text = render_ride_quote(p[0], p[1], p[2], p[3], provider, rng)
            img.save(path, "JPEG", quality=90)
            return str(path)
        if kind == "invoice" and len(rest.split(":")) >= 4:
            supplier, item, n_items, cost = rest.split(":")[:4]
            s = self.world.suppliers.get(supplier)
            it = self.world.items.get(item)
            paper, self.last_text = render_receipt(s.name if s else supplier.replace("-", " ").title(), it.name if it else item.replace("-", " "),
                                                   n_items, cost, rng)
            backdrop = Image.open(PHOTOS / rng.choice(self.manifest["invoice_backdrops"]))
            place_receipt(paper, backdrop, rng).save(path, "JPEG", quality=85)
            return str(path)
        files = self.resolve(label)
        shutil.copyfile(PHOTOS / files[rng.randrange(len(files))], path)
        return str(path)
