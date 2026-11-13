import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image, ImageStat

from hsim.media import MANIFEST, PHOTOS, Media, place, shape_arabic, split_name
from hsim.world import build

M = json.loads(MANIFEST.read_text())
STATES = ("ok", "misfold", "low", "cannot_hold", "unstable")
REAL = {p.name for p in PHOTOS.glob("file-*.jpg") if "-" not in p.stem[5:]}


@pytest.fixture(scope="module")
def world():
    return build(7)


def is_photo(path: str) -> bool:
    """A JPEG with photo-like content, not a white card with black text."""
    img = Image.open(path)
    if img.format != "JPEG" or min(img.size) < 640:
        return False
    rgb = img.convert("RGB").resize((90, 160))
    hist = rgb.convert("L").histogram()
    white_share = sum(hist[235:]) / (90 * 160)
    colours = len(set(rgb.getdata()))
    return white_share < 0.7 and colours > 400 and max(ImageStat.Stat(rgb).stddev) > 12


def lamp_key(files: list[str]) -> str | None:
    for key, fs in M["lamps"].items():
        if files == fs:
            return key
    return None


def test_manifest_files_exist_and_are_photos() -> None:
    files = set()
    for fs in M["items"].values():
        files.update(fs)
    for fs in M["lamps"].values():
        files.update(fs)
    for fs in M["parts"].values():
        files.update(fs)
    for sizes in M["heads"].values():
        for fs in sizes.values():
            files.update(fs)
    files.update(M["scene"] + M["neutral"] + M["invoice_backdrops"])
    for fs in M["real_item_overrides"].values():
        files.update(fs)
    missing = [f for f in files if not (PHOTOS / f).exists()]
    assert not missing
    for f in files:
        assert is_photo(str(PHOTOS / f)), f


def test_real_photos_are_untouched() -> None:
    assert len(REAL) == 14


def test_every_reachable_lamp_combo_maps_to_its_own_lamp_photos(world, tmp_path: Path) -> None:
    media = Media(world, tmp_path)
    structures = [k for k, it in world.items.items() if it.role in ("structure", "structure_material")]
    assert set(structures) == set(M["structure_groups"])
    for s in structures:
        sgroup = M["structure_groups"][s]
        for light, lgroup in M["light_groups"].items():
            for state in STATES:
                label = f"lamp:{s}:{light}:{state}"
                files = media.resolve(label)
                if state in M["reachable_states"][sgroup]:
                    assert lamp_key(files) == f"{sgroup}|{lgroup}|{state}", label
                    assert is_photo(media.make("worker-a", label)), label
                else:
                    assert files == M["parts"][lgroup], label  # unreachable: parts on the desk, never a lamp photo


def test_real_lamp_photos_only_for_their_exact_combo() -> None:
    for key, files in M["lamps"].items():
        for f in files:
            if f == "file-000453.jpg":
                assert key == "folding-stand|module|ok"
            if f == "file-001157.jpg":
                assert key == "card-fold|module|ok"


def test_old_lamp_and_heads_labels(world, tmp_path: Path) -> None:
    media = Media(world, tmp_path)
    assert lamp_key(media.resolve("lamp:phone-stand-folding-180")) == "folding-stand|module|ok"
    assert lamp_key(media.resolve("lamp:canson-300g-ribbed-100x70")) == "card-fold|module|ok"
    # no 'ok' state is reachable on these: the old label falls back to the structure's own outcome, never an ok-looking lamp
    assert lamp_key(media.resolve("lamp:display-stand-clear-10pack")) == "clear-easel|module|cannot_hold"
    assert lamp_key(media.resolve("lamp:card-a3-300g-loose")) == "a3-fold|module|low"
    assert media.resolve("heads:1") == M["heads"]["led-module-2835-12v-1w5-white"]["1"]
    assert is_photo(media.make("worker-b", "heads:4"))


def test_items_use_real_photos_first(world, tmp_path: Path) -> None:
    media = Media(world, tmp_path)
    for key, item in world.items.items():
        files = media.resolve(f"item:{key}")
        if key in M["real_item_overrides"]:
            # A cleaned copy of the real photo, or a generated replacement when the real one misleads (the UK-plug charger).
            assert files == M["real_item_overrides"][key] and (files[0].startswith(f"{item.photo}-") or files[0].startswith(f"gen-item-{key}-"))
        elif item.photo:
            assert files == [f"{item.photo}.jpg"]
        else:
            assert files == M["items"][key] and all(f.startswith("gen-item-") for f in files)
        assert is_photo(media.make("worker-a", f"item:{key}"))


@pytest.mark.parametrize("n,size", [(1, "1"), (3, "few"), (5, "few"), (6, "many"), (14, "many")])
def test_heads_pick_by_count(world, tmp_path: Path, n: int, size: str) -> None:
    media = Media(world, tmp_path)
    for light in ("led-module-2835-12v-1w5-white", "led-pcb-round-6x7530", "touch-led-board-ttp223-5730"):
        assert media.resolve(f"heads:{n}:{light}") == M["heads"][light][size]
        assert is_photo(media.make("worker-a", f"heads:{n}:{light}"))


def test_ride_quote_prints_exact_numbers(world, tmp_path: Path) -> None:
    media = Media(world, tmp_path)
    for provider in ("Uber", "DiDi", "inDrive"):
        path = media.make("worker-b", f"ride-quote:downtown_bab_el_louk:delivery_area:137:29:{provider}")
        assert "EGP 137" in media.last_text and "Trip time 29 min" in media.last_text and provider in media.last_text
        assert "Maadi Ring Road, Maadi" in media.last_text and "Bab El Louk, Downtown Cairo" in media.last_text
        assert Image.open(path).size == (720, 1560) and is_photo(path)
    path = media.make("worker-b", "ride-quote:dokki:manial:64:11")  # old label without provider
    assert "EGP 64" in media.last_text and Image.open(path).format == "JPEG"


def test_invoice_prints_exact_numbers(world, tmp_path: Path) -> None:
    media = Media(world, tmp_path)
    for supplier in world.suppliers:
        offers = world.suppliers[supplier].offers
        item = offers[0].item if offers else "insulating-tape"
        path = media.make("worker-a", f"invoice:{supplier}:{item}:7:31.5")
        assert "7" in media.last_text and "EGP 31.5" in media.last_text
        assert is_photo(path)
    media.make("worker-a", "invoice:harby-tech:led-module-2835-12v-1w5-white:12:54")
    assert media.last_text[1] == "حاربي تيك" and media.last_text[2] == "Harby Tech electrician"


def test_arabic_helpers() -> None:
    assert split_name("Lampatronics (لاماترونكس), Downtown branch") == ("لاماترونكس", "Lampatronics, Downtown branch")
    assert split_name("محل إلكترونيات (3)") == ("محل إلكترونيات", "")
    assert shape_arabic("فاتورة") != "فاتورة"[::-1]  # letters joined into presentation forms
    assert place("delivery_area") == "Maadi Ring Road, Maadi"


def test_scene_and_unknown_labels(world, tmp_path: Path) -> None:
    media = Media(world, tmp_path)
    for label in ("scene", "mystery", "item:", "item:not-an-item", "lamp:not-a-structure", "heads:x:unknown-light", ""):
        assert is_photo(media.make("worker-a", label)), label


def test_deterministic_with_counter(tmp_path: Path) -> None:
    labels = ["item:dc-female-jack-5521-20cm", "lamp:metal-arm-tablet-stand:usb-led-strip-ikea:ok", "scene",
              "ride-quote:dokki:new_maadi:150:26:DiDi", "invoice:lampatronics-downtown:dc-female-jack-5521-20cm:5:20", "heads:9"] * 3

    def run(seed: int, out: Path) -> list[str]:
        media = Media(build(seed), out)
        return [hashlib.sha256(Path(media.make(w, lab)).read_bytes()).hexdigest() for lab in labels for w in ("worker-a", "worker-b")]

    a, b = run(3, tmp_path / "a"), run(3, tmp_path / "b")
    assert a == b
    media = Media(build(3), tmp_path / "c")
    paths = {media.make("worker-a", "scene") for _ in range(4)}
    assert len(paths) == 4  # each repeated photo gets its own file


def test_library_size() -> None:
    total = sum(p.stat().st_size for p in PHOTOS.glob("gen-*.jpg"))
    assert total < 26 * 1024 * 1024
