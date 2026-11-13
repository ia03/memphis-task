"""Build scripts/photos/prompts.json (what to generate) and world/photo_manifest.json (label -> photo files).

Run: PYTHONPATH=. .venv/bin/python scripts/photos/build_library.py
Then: PYTHONPATH=. .venv/bin/python scripts/photos/generate.py   (only generates files that are missing)

Every description below follows world/items.yaml. Lamp photos cover the lamp states the simulator can name (ok, unstable, misfold, low, cannot_hold).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PHOTOS = ROOT / "world" / "photos"

STYLE = ("Style: a casual, slightly soft Android phone snapshot (vertical 9:16 portrait) taken by a hired worker in Cairo, Egypt; "
         "realistic everyday clutter, imperfect framing, mild sensor noise and slight blur, mixed fluorescent or warm indoor light; "
         "not a studio, catalogue or advertising photo. No faces (only a hand or forearm if any person is visible). "
         "No text overlays, captions, watermarks, readable brand names or logos, price tags, or written numbers anywhere in the image.")
STYLE_BOOST = STYLE.replace("No text overlays, captions, watermarks, readable brand names or logos, price tags, or written numbers anywhere in the image.",
                            "No text overlays, captions, watermarks, brand names, logos or price tags. The only printed text anywhere in the image is "
                            "the small white print 'OUTPUT DC-12V' on the black plug body.")

# ---- parts, exactly as world/items.yaml describes them ----
MODULE = ("a white injection-moulded plastic LED module about 6 cm long and 1.3 cm wide, with three round domed lenses in a row "
          "and two short thin white wires coming out of its end (it is a sealed white plastic module, not a bare aluminium strip)")
JACK = "a female DC barrel jack (black plastic sleeve, 5.5x2.1 mm socket) on a 20 cm red-and-black two-core wire ending in bare tinned tips"
BOOST = ("a black USB-A cable about 1 m long with a small black rectangular plug body at the USB end printed in small white letters "
         "'OUTPUT DC-12V', and a male 5.5x2.1 mm DC barrel plug at the other end")
ROUND_PCB = ("a small round white aluminium LED board about 3 cm across with a hole in the middle and six small rectangular yellow SMD LEDs "
             "spaced in a ring, two tiny resistors and two bare solder pads")
TOUCH = ("a small round circuit board about 2.5 cm across with a few small warm-white rectangular SMD LEDs, a tiny black six-pin chip and a "
         "small touch pad area, bare solder pads, no wires")
HEAD_MODULE = (f"a prepared LED head: {MODULE}, its wires joined to the red/black lead of a female DC barrel jack, "
               "the joints wrapped in black insulating tape")
HEAD_PCB = f"{ROUND_PCB}, with a red and a black wire soldered to its pads; the wires run into a black cable ending in a USB-A plug"
HEAD_TOUCH = (f"a small round circuit board about 2.5 cm across with a few warm-white SMD LEDs and a tiny black chip, with a red and a black wire "
              "soldered to its pads; the wires run into a black cable ending in a USB-A plug")

ITEM_NOTE = "Only this one piece of the item is in view; no piles, stacks, bags or boxes of the same item anywhere in the photo."
PACKS = {"rubber-bands", "display-stand-clear-10pack", "canson-sketch-pad-a3-300g-10"}
ITEMS: dict[str, list[str]] = {
    "led-module-2835-12v-1w5-white": [
        f"At the cluttered glass counter of a small electronics parts shop in Bab El Louk, Downtown Cairo, a hand holds up one single {MODULE}.",
        f"One single {MODULE} lies on a scratched glass shop counter in a Downtown Cairo electronics shop, small parts drawers and coiled cables blurred behind it.",
        f"Close-up of an open palm in an electronics shop holding one single {MODULE}; glass counter with resistors and connectors in the background.",
    ],
    "dc-female-jack-5521-20cm": [
        f"At the cluttered glass counter of an electronics shop in Bab El Louk, Downtown Cairo, a hand holds up {JACK}.",
        f"{JACK[0].upper() + JACK[1:]} lies on a glass counter of a Downtown Cairo electronics shop beside small trays of connectors.",
    ],
    "usb-5v-12v-boost-cable-5521": [
        f"In an electronics shop in Downtown Cairo, an open hand holds {BOOST}; the cable is loosely coiled across the palm and the printed plug body faces the camera.",
        f"{BOOST[0].upper() + BOOST[1:]} lies loosely coiled on a glass shop counter; the printed plug body is in focus.",
        f"A hand holds {BOOST} up against a background of a cluttered electronics shop; the barrel plug end dangles below.",
    ],
    "touch-led-board-ttp223-5730": [
        f"In an electronics shop in Downtown Cairo, fingertips hold {TOUCH}, glass counter blurred behind.",
        f"{TOUCH[0].upper() + TOUCH[1:]} lies on a dark glass shop counter next to a small open anti-static bag.",
    ],
    "usb-led-strip-ikea": [
        "In a large home-furnishing store in 6th of October, a hand holds a coiled thin flexible LED strip, about 1 m, with a short cable, "
        "a small inline control module and a USB-A plug; the strip is plugged into a demo socket on the shelf and glows saturated purple and "
        "blue (it is a colour-changing RGB strip); plain packaging tray behind; no logos.",
        "A coiled thin colour-changing LED strip with a USB-A plug and small inline controller lies on a white store shelf, plugged in as a "
        "display sample and glowing magenta-pink and blue; plain unbranded packaging beside it.",
    ],
    "usb-led-strip-5v-white-1m": [
        "In a mobile-accessories shop in Dokki, Cairo, a hand holds a coiled 1 m thin white flexible LED strip with small white SMD LEDs; "
        "one end has a short cable with a USB-A plug. Glass counter with phone cases behind.",
        "A coiled thin white LED strip with small white SMD LEDs and a short USB-A plug lead lies on a glass counter of a phone-accessories shop.",
    ],
    "insulating-tape": [
        "A hand holds one roll of black PVC electrical insulating tape at the counter of a small electrical shop in Cairo.",
        "One roll of black PVC electrical insulating tape on a dusty glass counter of a Cairo electrical shop, wires and switches blurred behind.",
    ],
    "phone-stand-simple-30": [
        "On the glass counter of a phone-accessories shop in Dokki, Cairo, a very simple small one-piece plastic desk phone stand: a low tilted "
        "cradle about 8-10 cm tall, no column, no phone on it. Phone cases on the wall behind.",
        "A hand holds a very simple small one-piece plastic desk phone stand with a low tilted cradle (under 10 cm tall) in a phone-accessories shop.",
    ],
    "mic-stand-mobile-holder-30cm": [
        "On a shop counter, a small black adjustable desk microphone stand about 30 cm tall (round weighted base, thin telescoping pole) "
        "with a spring phone-holder clamp at the top instead of a microphone. Phone-accessories shop in Cairo, no phone in the clamp.",
        "A hand holds a small black 30 cm adjustable desk microphone stand with a phone-holder clamp at the top, in a cluttered phone-accessories shop.",
    ],
    "display-stand-clear-10pack": [
        "On a shop counter, one small clear transparent plastic folding plate easel (display stand about 15 cm tall), opened, next to a few "
        "more folded ones in a plain clear bag. Housewares/stationery shop in Cairo.",
        "A hand holds one small clear plastic folding plate easel (about 15 cm tall), opened, inside a cluttered Cairo shop.",
    ],
    "card-300g-plain-100x70": [
        "In a small stationery shop in Downtown Cairo, a hand holds up the edge of one single large plain smooth white 300 gsm drawing "
        "card sheet (100x70 cm, nearly as wide as the counter), lying flat on the wooden counter.",
        "A large plain white drawing card sheet (100x70 cm, thick 300 gsm) held up by a hand in a cluttered stationery shop, rolls of paper behind.",
    ],
    "card-a3-300g-loose": [
        "In a stationery shop in Downtown Cairo, a hand holds one single thick stiff white A3 card sheet (300 gsm), ready-cut; shelves of paper behind.",
        "One single thick white A3 card sheet lies on a stationery-shop counter, a hand pressing its corner to show it is stiff.",
    ],
    "canson-sketch-pad-a3-300g-10": [
        "In a stationery shop in Cairo, a hand holds an A3 sketch pad of thick white drawing paper with a plain cover (cover text blurred, no readable brand).",
        "An A3 sketch pad, opened to show a thick white sheet, lies on a stationery-shop counter; cover plain, no readable brand.",
    ],
    "card-a3-150g": [
        "In a stationery shop in Cairo, a hand holds one thin floppy sheet of white A3 paper (150 gsm); it bends under its own weight.",
        "One thin white A3 paper sheet lies on a stationery-shop counter, its corner curling up; light shows through it slightly.",
    ],
    "pvc-conduit-20mm": [
        "In a small electrical shop in Dokki, Cairo, a hand holds up one single long length of rigid grey 20 mm plastic electrical conduit pipe "
        "(about 3 m, it runs out of the frame); no other conduit pipes are visible anywhere.",
        "One single long length of rigid grey 20 mm plastic electrical conduit lies across a shop counter in a Cairo electrical shop; "
        "no other conduit pipes or bundles are visible.",
    ],
    "conduit-t-elbow-fittings": [
        "An open palm in an electrical shop holds exactly two grey push-fit fittings for 20 mm conduit: one T fitting and one elbow fitting; "
        "no other fittings visible anywhere.",
        "Exactly two grey push-fit fittings for 20 mm plastic conduit, one T and one elbow, lie on a dusty shop counter in Cairo; no bins, "
        "piles or other fittings in view.",
    ],
    "usb-cable-bare-leads-5v": [
        "In an electronics shop in Downtown Cairo, a hand holds a black USB-A cable whose other end splits into a bare red and a bare black wire with tinned tips.",
        "A black USB-A cable with bare red and black wire ends lies loosely on a glass counter in a Cairo electronics shop.",
    ],
    "dc-female-jack-screw-terminal": [
        "At the glass counter of an electronics shop in Bab El Louk, Downtown Cairo, a hand holds one female DC barrel jack adapter "
        "(5.5x2.1 mm socket) whose back end is a small black two-screw terminal block with two tiny screws for clamping wires; no wires attached.",
        "One female DC barrel jack adapter with a small black two-screw terminal block (CCTV-style, no wires attached) lies on a glass "
        "counter in a Cairo electronics shop.",
    ],
    "terminal-block-strip-12": [
        "In an electrical-supplies shop in Cairo, a hand holds one white plastic 12-way electrical terminal strip ('domino' connector strip) "
        "with small brass screws in each way.",
        "One white plastic 12-way electrical terminal strip with brass screws lies on a dusty shop counter in a Cairo electrical shop.",
    ],
    "bottled-water": [
        "At a small street kiosk in Cairo, a hand holds one 1.5 litre plastic bottle of water with a plain blank label (no brand), drinks fridge behind.",
        "One 1.5 litre plastic bottle of water with a plain unbranded label stands on the counter of a small Cairo grocery.",
    ],
    "rubber-bands": [
        "In a stationery shop in Cairo, a hand holds one small clear plastic bag of rubber bands (assorted colours).",
        "One small clear plastic bag of rubber bands lies on a stationery-shop counter in Cairo.",
    ],
    "ruler-30cm": [
        "A hand holds a plain clear plastic 30 cm ruler with centimetre markings in a small stationery shop in Cairo; no brand.",
        "A plain clear plastic 30 cm ruler lies on a stationery-shop counter beside pens; no brand.",
    ],
}

# ---- lamps ----
LIGHTS = {  # light group -> how it looks when mounted (and lit)
    "module": ("the light is one to three small white rectangular plastic LED modules (each about 6 cm long with three round lenses) fixed with tape, "
               "their thin wires taped with black insulating tape to a red/black lead with a small black DC barrel jack, plugged into a thin "
               "black USB cable that runs off to a charger; the modules glow bright cool white"),
    "strip": ("the light is a thin white flexible LED strip (a row of small SMD LEDs) taped along the underside, its thin cable with a USB plug "
              "running off to a charger; it glows bright cool white"),
    "colour": ("the light is a thin flexible LED strip (a row of small SMD LEDs) taped along the underside, its thin cable with a USB plug and a "
               "small inline controller running off to a charger; it glows saturated purple-pink (a colour-changing RGB strip), so everything "
               "it lights is tinted purple-pink, clearly not white light"),
    "round": ("the light is a small round white LED board about 3 cm across (a ring of tiny yellow SMD LEDs) fixed with tape, with thin red "
              "and black wires running into a black USB cable that goes off to a charger; the board is NOT lit: its LEDs are dark and give no "
              "light at all, the room is lit only by an ordinary ceiling or side lamp, the notebook is not lit by the board"),
}
LIGHT_GROUPS = {
    "led-module-2835-12v-1w5-white": "module",
    "usb-led-strip-5v-white-1m": "strip",
    "usb-led-strip-ikea": "colour",
    "led-pcb-round-6x7530": "round",
    "touch-led-board-ttp223-5730": "round",
}
STRUCTURE_GROUPS = {
    "phone-stand-folding-180": "folding-stand",
    "phone-stand-simple-30": "simple-stand",
    "metal-arm-tablet-stand": "metal-arm",
    "mic-stand-mobile-holder-30cm": "mic-stand",
    "display-stand-clear-10pack": "clear-easel",
    "canson-300g-ribbed-100x70": "card-fold",
    "card-300g-plain-100x70": "card-fold",
    "card-a3-300g-loose": "a3-fold",
    "canson-sketch-pad-a3-300g-10": "a3-fold",
    "card-a3-150g": "thin-paper",
    "black-plumbing-pipe": "pipe",
    "pvc-conduit-20mm": "conduit",
    "bottled-water": "bottle",
}
# Reachable states per structure group: card_fold -> ok/misfold; card_fold_small -> low; method none / conduit
# -> unstable; stands by holds_head/height_ok.
REACHABLE = {
    "folding-stand": ["ok"], "metal-arm": ["ok"], "mic-stand": ["ok"], "simple-stand": ["low"], "clear-easel": ["cannot_hold"],
    "card-fold": ["ok", "misfold"], "a3-fold": ["low"], "thin-paper": ["unstable"], "pipe": ["unstable"], "conduit": ["unstable"],
    "bottle": ["unstable"],
}
DARK_DESK = ("At night in a dim room of a Cairo apartment (any window shows only ordinary apartment blocks, no landmarks and no pyramids), "
             "on a home desk (glass-topped or wooden, some everyday clutter around), no phone or tablet placed on any stand: ")
SCENES = {
    ("folding-stand", "ok"): (
        "a black plastic folding desk phone holder (rectangular flat base with two square cut-outs, a telescopic column extended to about 25 cm, "
        "a tilting plate on top with two small lower hooks) stands upright; the light is fixed under the tilted top plate and shines down onto "
        "an open notebook on the desk below, making a bright pool of light on the page. It works as a small desk lamp."),
    ("metal-arm", "ok"): (
        "a black metal spring-arm tablet stand is clamped to the desk edge, its arm raised and bent so the tablet holder hangs about 35 cm "
        "above the desk; the light is taped to the holder, facing down, lighting an open notebook below with a bright pool of light. "
        "It works as a desk lamp."),
    ("mic-stand", "ok"): (
        "a small black adjustable desk microphone stand about 30 cm tall (round weighted base, thin pole) with a phone-holder clamp at the top "
        "stands upright; the light is clamped and taped in the phone holder facing down, lighting an open notebook on the desk with a bright "
        "pool of light. It works as a small desk lamp."),
    ("card-fold", "ok"): (
        "a large sheet of thick white card is folded into a sturdy upright box-like stand about 30 cm high with a flat top that overhangs the "
        "front, the folded edge held with one small black binder clip; the light is fixed under the overhanging top and shines down, brightly "
        "lighting the front of the card and the desk/page below. It stands firmly and works as a desk lamp."),
    ("card-fold", "misfold"): (
        "a large sheet of thick white card has been folded wrongly: the creases are in the wrong places, the card sags and leans over to one side "
        "and has collapsed onto the desk, it does not stand up; a small black binder clip hangs off one edge; the light is lit but lies tilted "
        "on the desk under the slumped card, shining sideways. Clearly a failed fold, not a working lamp."),
    ("a3-fold", "low"): (
        "a single A3 sheet of thick white card is folded into a small, low tent-like shelf only about 15 cm high, held with a small black binder "
        "clip; the light is fixed under its low top, very close to the desk, making only a small bright hot spot right underneath; an open "
        "notebook next to it stays mostly dark. It stands, but it is obviously far too low to light a page from above."),
    ("simple-stand", "low"): (
        "a very simple small one-piece plastic phone stand (a low tilted cradle under 10 cm tall); the light is taped onto the low cradle, only "
        "a few centimetres above the desk, shining forward at a low angle; the desk and an open notebook in front are barely lit. It stands, "
        "but it is obviously too low to light a page from above."),
    ("clear-easel", "cannot_hold"): (
        "a small clear transparent plastic plate easel (display stand about 15 cm tall) stands on the desk; the light could not be mounted on "
        "it: the lit light lies flat on the desk, leaning against the foot of the clear easel and shining sideways along the desk surface. "
        "Nothing is held up above the desk."),
    ("thin-paper", "unstable"): (
        "a thin floppy A3 sheet of white paper was folded into a tent but has buckled and collapsed under the weight of the light; the paper is "
        "bent and creased and lies almost flat on the desk; the lit light lies on the desk among the collapsed folds, shining sideways. "
        "It does not stand."),
    ("pipe", "unstable"): (
        "a long uncut thin black plastic plumbing pipe, only about 2 cm in diameter (thin, like a rigid garden hose; not a wide drain pipe), well over a metre long, has fallen over and lies diagonally across the floor beside the desk; "
        "the lit light is taped to one end of the pipe and lies on the floor, shining along the floor tiles. Nothing stands up."),
    ("conduit", "unstable"): (
        "a long uncut length of rigid grey 20 mm plastic electrical conduit, about 2 metres long, has slid down and lies across the floor and "
        "the edge of the desk; the lit light is taped to one end and lies on the floor, shining sideways. Nothing stands up; it is not a lamp stand."),
    ("bottle", "unstable"): (
        "a 1.5 litre plastic water bottle (plain label) has the light taped and wrapped around its neck with tape; the bottle has tipped over and "
        "lies on its side on the desk, the lit light pointing sideways along the desk surface, an open notebook beside it barely lit. "
        "It is not a lamp stand; nothing holds the light over the desk."),
}
# Round boards are shown mounted but unlit: the sim never verifies that they work on 5V USB.
LIGHT_ROOM = ("In the evening in a Cairo apartment room lit by an ordinary ceiling lamp (any window shows only ordinary apartment blocks, "
              "no landmarks and no pyramids), on a home desk (wooden or glass-topped, some everyday clutter around), no phone or tablet on "
              "any stand: ")
SCENES_UNLIT = {
    ("folding-stand", "ok"): "a black plastic folding desk phone holder (rectangular flat base with two square cut-outs, a telescopic column extended to about 25 cm, a tilting plate on top with two small lower hooks) stands upright over an open notebook; the light is taped under the tilted top plate, facing down.",
    ("metal-arm", "ok"): "a black metal spring-arm tablet stand is clamped to the desk edge, its arm raised so the tablet holder hangs about 35 cm above an open notebook; the light is taped to the holder, facing down.",
    ("mic-stand", "ok"): "a small black adjustable desk microphone stand about 30 cm tall (round weighted base, thin pole) with a phone-holder clamp at the top stands upright beside an open notebook; the light is taped in the phone holder, facing down.",
    ("card-fold", "ok"): "a large sheet of thick white card is folded into a sturdy upright box-like stand about 30 cm high with a flat top that overhangs the front, the folded edge held with one small black binder clip; the light is taped under the overhanging top, facing down. It stands firmly.",
    ("card-fold", "misfold"): "a large sheet of thick white card has been folded wrongly: the creases are in the wrong places, the card sags and has collapsed to one side onto the desk, it does not stand up; a small black binder clip hangs off one edge; the light lies tilted on the desk under the slumped card. Clearly a failed fold.",
    ("a3-fold", "low"): "a single A3 sheet of thick white card is folded into a small, low tent-like shelf only about 15 cm high, held with a small black binder clip; the light is taped under its low top, very close to the desk; an open notebook lies next to it. Obviously far too low to be a desk lamp.",
    ("simple-stand", "low"): "a very simple small one-piece plastic phone stand (a low tilted cradle under 10 cm tall); the light is taped onto the low cradle, only a few centimetres above the desk, facing forward; an open notebook lies in front. Obviously too low to be a desk lamp.",
    ("clear-easel", "cannot_hold"): "a small clear transparent plastic plate easel (display stand about 15 cm tall) stands on the desk; the light could not be mounted on it and lies flat on the desk, leaning against the foot of the clear easel. Nothing is held up above the desk.",
    ("thin-paper", "unstable"): "a thin floppy A3 sheet of white paper was folded into a tent but has buckled and collapsed under the weight of the light; the paper lies almost flat and creased on the desk, the light lying among the collapsed folds. It does not stand.",
    ("pipe", "unstable"): "a long uncut thin black plastic plumbing pipe, only about 2 cm in diameter (like a rigid garden hose; not a wide drain pipe), well over a metre long, has fallen over and lies diagonally across the floor beside the desk; the light is taped to one end of the pipe, lying on the floor tiles. Nothing stands up.",
    ("conduit", "unstable"): "a long uncut length of rigid grey 20 mm plastic electrical conduit, about 2 metres long, has slid down and lies across the floor and the edge of the desk; the light is taped to one end and lies on the floor. Nothing stands up; it is not a lamp stand.",
    ("bottle", "unstable"): "a 1.5 litre plastic water bottle (plain label) has the light taped around its neck; the bottle has tipped over and lies on its side on the desk next to an open notebook. Nothing holds the light over the desk.",
}
# Derived copies of real photos that show more than the sim states (a price sticker; other items in frame). items.yaml keeps the
# original id; media uses these instead. file-000054-nosticker: crop x>=478 of file-000054. file-000693-clipsbox: crop (318,96,568,346)
# of file-000693 upscaled to 720x720.
REAL_ITEM_OVERRIDES = {"metal-arm-tablet-stand": ["file-000054-nosticker.jpg"], "binder-clips-19mm-box12": ["file-000693-clipsbox.jpg"],
                       # The real charger photo shows a UK plug at home; a bought charger is a local two-pin one (r21 S3, r1-s11-unhinted D15).
                       "usb-charger-5v": ["gen-item-usb-charger-5v-1.jpg", "gen-item-usb-charger-5v-2.jpg"]}
REAL_LAMPS = {("folding-stand", "module", "ok"): ["file-000453.jpg"], ("card-fold", "module", "ok"): ["file-001157.jpg"]}
PARTS = {
    "module": f"Lying loose together on a home desk, unassembled and unlit: {HEAD_MODULE}; and {BOOST}. Nothing is mounted on a stand.",
    "strip": "Lying loose on a home desk, unlit and unassembled: a coiled thin white LED strip with a USB-A plug lead, and a roll of black insulating tape. Nothing is mounted.",
    "colour": "Lying loose on a home desk, unlit and unassembled: a coiled thin LED strip with a small inline controller and USB-A plug, and a roll of black insulating tape. Nothing is mounted.",
    "round": f"Lying loose on a home desk, unlit and unassembled: {HEAD_PCB}; and a roll of black insulating tape. Nothing is mounted.",
}
HEADS = {
    "led-module-2835-12v-1w5-white": {
        "1": [f"A hand holds up {HEAD_MODULE}. Outdoors on a dusty Cairo pavement or in a shop."],
        "few": [f"A hand holds three prepared LED heads together; each is {HEAD_MODULE}.",
                f"Four prepared LED heads lie side by side on a workshop counter; each is {HEAD_MODULE}."],
        "many": [f"About ten prepared LED heads lie in a loose tangled pile on a technician's workbench in a Cairo electronics shop; each is {HEAD_MODULE}.",
                 f"A clear plastic bag holding about a dozen prepared LED heads, held up by a hand; each head is {HEAD_MODULE}."],
    },
    "led-pcb-round-6x7530": {
        "1": [f"A hand holds one prepared light: {HEAD_PCB}."],
        "few": [f"Three prepared lights lie side by side on a technician's bench: each is {HEAD_PCB}."],
        "many": [f"About ten prepared lights lie in a tangled pile on a technician's bench: each is {HEAD_PCB}."],
    },
    "touch-led-board-ttp223-5730": {
        "1": [f"A hand holds one prepared light: {HEAD_TOUCH}."],
        "few": [f"Three prepared lights lie side by side on a technician's bench: each is {HEAD_TOUCH}."],
        "many": [f"About ten prepared lights lie in a tangled pile on a technician's bench: each is {HEAD_TOUCH}."],
    },
}
REAL_HEADS = {"led-module-2835-12v-1w5-white": {"1": ["file-000400.jpg"], "few": ["file-001085.jpg"]}}
SCENE = [
    "A busy street in Bab El Louk, Downtown Cairo, seen from the pavement: old buildings, small electronics shops with out-of-focus signs, parked cars, afternoon light.",
    "A narrow side street in Dokki, Cairo, with phone-accessory and electrical shops, motorbikes parked, shop signs blurred and unreadable.",
    "Cairo traffic seen through a car's side window from the back seat: microbuses, a flyover, hazy sky.",
    "Inside a crowded passage of small electronics stalls in Downtown Cairo, glass display cases and hanging cables, signs out of focus.",
    "A worn pavement and shopfronts with rolled-up shutters on a Cairo street, a kiosk with drinks, evening light.",
    "A view along a street in Maadi, Cairo, with trees, parked cars and apartment blocks, late afternoon.",
]
NEUTRAL = [
    "An accidental, slightly blurry photo of a tiled shop floor and the edge of a glass counter.",
    "A slightly blurry photo of a cluttered home desk with a glass of tea, a notebook and a charger cable.",
    "An out-of-focus photo of a shop counter with small boxes and cables, taken in a hurry.",
]
BACKDROPS = [
    "Top-down view of an empty area of a scratched dark glass shop counter with a pegboard visible through the glass, a few small electronic parts at the very edges; the middle is empty.",
    "Top-down view of an empty worn wooden desk surface in a Cairo apartment, a pen at the edge; the middle is empty.",
    "Top-down view of an empty light glass counter in a stationery shop, some pens and paper at the edges; the middle is empty.",
    "Top-down view of an empty scratched glass counter of a phone-accessories shop under fluorescent light, small boxes at the edges; the middle is empty.",
]


def main() -> None:
    prompts: list[dict[str, str]] = []

    def add(file: str, kind: str, key: str, text: str, style: str = STYLE) -> str:
        prompts.append({"file": file, "kind": kind, "key": key, "prompt": f"{text} {style}"})
        return file

    manifest: dict[str, object] = {"version": 1, "items": {}, "lamps": {}, "parts": {}, "heads": {}, "scene": [], "neutral": [],
                                   "invoice_backdrops": [], "light_groups": LIGHT_GROUPS, "structure_groups": STRUCTURE_GROUPS,
                                   "reachable_states": REACHABLE,
                                   "real_item_overrides": REAL_ITEM_OVERRIDES}
    for key, texts in ITEMS.items():
        style = STYLE_BOOST if key == "usb-5v-12v-boost-cable-5521" else STYLE
        note = "" if key in PACKS else " " + ITEM_NOTE
        manifest["items"][key] = [add(f"gen-item-{key}-{i + 1}.jpg", "item", key, t + note, style) for i, t in enumerate(texts)]
    for (sgroup, state), scene in SCENES.items():
        for lgroup, light in LIGHTS.items():
            files = list(REAL_LAMPS.get((sgroup, lgroup, state), []))
            for i in range(2):
                angle = ["", " Photo taken from a slightly different angle, a bit closer."][i]
                text = (f"{LIGHT_ROOM}{SCENES_UNLIT[(sgroup, state)]} In this photo {light}.{angle}" if lgroup == "round"
                        else f"{DARK_DESK}{scene} In this photo {light}.{angle}")
                files.append(add(f"gen-lamp-{sgroup}-{lgroup}-{state}-{i + 1}.jpg", "lamp", f"{sgroup}|{lgroup}|{state}", text))
            manifest["lamps"][f"{sgroup}|{lgroup}|{state}"] = files
    for lgroup, text in PARTS.items():
        manifest["parts"][lgroup] = [add(f"gen-parts-{lgroup}-1.jpg", "parts", lgroup, text)]
    for light, sizes in HEADS.items():
        manifest["heads"][light] = {}
        for size, texts in sizes.items():
            files = list(REAL_HEADS.get(light, {}).get(size, []))
            files += [add(f"gen-heads-{light}-{size}-{i + 1}.jpg", "heads", f"{light}|{size}", t) for i, t in enumerate(texts)]
            manifest["heads"][light][size] = files
    manifest["scene"] = [add(f"gen-scene-{i + 1}.jpg", "scene", "scene", t) for i, t in enumerate(SCENE)]
    manifest["neutral"] = [add(f"gen-neutral-{i + 1}.jpg", "neutral", "neutral", t) for i, t in enumerate(NEUTRAL)]
    manifest["invoice_backdrops"] = [add(f"gen-backdrop-{i + 1}.jpg", "backdrop", "backdrop", t) for i, t in enumerate(BACKDROPS)]
    (ROOT / "scripts" / "photos" / "prompts.json").write_text(json.dumps(prompts, indent=1, ensure_ascii=False) + "\n")
    (ROOT / "world" / "photo_manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(prompts)} prompts")


if __name__ == "__main__":
    main()
