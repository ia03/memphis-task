"""World facts: observed facts from world/*.yaml, unobserved facts sampled once per seed."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from .travel import TravelProfile, sample_profile

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "world"

Scalar = int | float | str | bool | None
Raw = Scalar | dict[str, "Raw"] | list["Raw"]


class ItemType(BaseModel):
    key: str
    name: str
    short: str = ""
    role: str
    input: dict[str, Scalar] = Field(default_factory=dict)
    output: dict[str, Scalar] = Field(default_factory=dict)
    joining_required: bool = False
    structure: dict[str, Scalar] = Field(default_factory=dict)
    photo: str | None = None
    assumption: str | None = None


class Offer(BaseModel):
    item: str
    price_egp: float
    count: int
    defective: int = 0
    web_price_egp: float | None = None
    bulk_price_egp: float | None = None
    bulk_min: int | None = None
    delivery_days: int | None = None
    trader_only: bool = False


class Claim(BaseModel):
    about: str
    says: str
    truthful: bool


class JoinService(BaseModel):
    offered: bool
    price_per_head_egp: float | None = None
    minutes_per_head: int | None = None
    busy_until_minutes_after_arrival: int = 0
    max_heads_per_day: int = 0
    earliest_delivery_days: int | None = None
    promised_vs_actual_minutes: int = 0
    phone_claim: str | None = None
    in_person_claim: str | None = None
    claim_when: str = "a worker asks in person about joining, assembling or preparing the parts, or who can do it"
    referral: str | None = None
    receipt: bool = True
    claim_minutes: int = 0
    keeps_finished_work_for_pickup_later: bool = True  # the real technicians did (Panatek overnight, PCBZone for days)
    takes_work_for_later_days: bool = True  # same evidence: a batch beyond a day's capacity is worked through on the next open days
    tests_heads: bool = False  # the real ones did not; the workers tested the heads they collected


class Supplier(BaseModel):
    key: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    category: str
    district: str
    address: str | None = None
    public_address: str | None = None
    finding_minutes: int = 0
    phone: str | None = None
    email: str | None = None
    web_domain: str | None = None
    discover: list[str]
    open_hhmm: str = "10:00"
    close_hhmm: str = "21:00"
    open_days: str = "every day"  # the record shows no closed days; Friday and Saturday hours were never observed
    signal_inside: bool = True
    phone_answers: bool = True
    phone_knowledge: str = "knows"
    email_channel: str = "silent"
    ai_call: str = "busy"
    delivery_offers: bool = False
    delivery_claims_by_phone: bool | None = None
    delivery_price_egp: float | None = None
    delivery_minutes: int | None = None
    offers: list[Offer] = Field(default_factory=list)
    not_stocked: list[str] = Field(default_factory=list)
    join: JoinService | None = None
    phone_claims: list[Claim] = Field(default_factory=list)
    web_claims: list[Claim] = Field(default_factory=list)
    online_only: bool = False
    no_cutting_service: bool = False
    observed: bool = True
    note: str | None = None


class WorkerSpec(BaseModel):
    id: str
    name: str
    home: str
    second_base: str | None = None
    start_location: dict[str, str]
    home_has_table: bool
    hosts_other_worker_at_home: bool
    owns_usb_charger: bool
    tells_home_when_asked_current_area: bool
    reply_minutes: dict[str, int]
    start_late_minutes: list[int]
    asks_before_fare_overrun: float
    overtime_on_open_errand_minutes: list[int]
    reports_counts_at_errand_end: float
    paid_command: dict[str, float]
    needs_script_for_new_supplier_type: bool
    relays_supplier_claims_without_probing: bool
    first_technical_misread: float
    asks_what_next_share: float = 0.0
    asks_nearby_alternatives: float = 0.2
    relays_shop_alternatives: float = 0.15
    confirms_cancellation: float = 0.75
    treats_planning_info_as_instruction: bool = False
    slips_per_shift_hour: float = 0.0
    mistake_kinds: dict[str, float]  # kind -> weight, the record's mix


class World(BaseModel):
    seed: int
    items: dict[str, ItemType]
    suppliers: dict[str, Supplier]
    workers: dict[str, WorkerSpec]
    travel: TravelProfile
    cafe_search_minutes: int
    cafe_cost_egp: int


def _load(name: str) -> Raw:
    return yaml.safe_load((WORLD / name).read_text())


def _draw(value: Raw, rng: random.Random) -> Scalar:
    if isinstance(value, dict) and "sample" in value:
        lo, hi = value["sample"]
        if isinstance(lo, int) and isinstance(hi, int):
            return rng.randint(lo, hi)
        return round(rng.uniform(float(lo), float(hi)), 2)
    if isinstance(value, dict) and "sample_bool" in value:
        return rng.random() < float(value["sample_bool"])
    if isinstance(value, (dict, list)):
        raise ValueError(f"Expected a scalar or sample, got {value!r}")
    return value


def _range(pair: list[int | float], rng: random.Random) -> int | float:
    lo, hi = pair
    if isinstance(lo, int) and isinstance(hi, int):
        return rng.randint(lo, hi)
    return round(rng.uniform(float(lo), float(hi)), 2)


def _supplier(raw: dict[str, Raw], rng: random.Random) -> Supplier:
    hours = raw.get("hours") or {}
    phone = raw.get("phone_channel") or {}
    delivery = raw.get("delivery") or {}
    offers = [Offer(item=o["item"], price_egp=float(_draw(o["price_egp"], rng)), count=int(_draw(o["count"], rng)),
                    defective=int(o.get("defective", 0)), web_price_egp=o.get("web_price_egp"),
                    bulk_price_egp=o.get("bulk_price_egp"), bulk_min=o.get("bulk_min"),
                    delivery_days=None if o.get("delivery_days") is None else int(_draw(o["delivery_days"], rng)),
                    trader_only=bool(_draw(o.get("trader_only", False), rng)))
              for o in raw.get("offers") or []]
    join = None
    for s in raw.get("services") or []:
        if s["kind"] != "join_head":
            raise ValueError(f"Unknown service {s['kind']}")
        join = JoinService(
            offered=bool(_draw(s["offered"], rng)),
            price_per_head_egp=None if s.get("price_per_head_egp") is None else float(_draw(s["price_per_head_egp"], rng)),
            minutes_per_head=None if s.get("minutes_per_head") is None else int(_draw(s["minutes_per_head"], rng)),
            busy_until_minutes_after_arrival=int(_draw(s.get("busy_until_minutes_after_arrival", 0), rng)),
            max_heads_per_day=int(_draw(s.get("max_heads_per_day", 0), rng)),
            earliest_delivery_days=None if s.get("earliest_delivery_days") is None else int(_draw(s["earliest_delivery_days"], rng)),
            promised_vs_actual_minutes=int(_draw(s.get("promised_vs_actual_minutes", 0), rng)),
            phone_claim=s.get("phone_claim"), in_person_claim=s.get("in_person_claim"),
            referral=s.get("referral"), receipt=bool(s.get("receipt", True)),
            claim_minutes=int(_draw(s.get("claim_minutes", 0), rng)))
    return Supplier(
        key=raw["key"], name=raw["name"], aliases=list(raw.get("aliases") or []), category=raw["category"], district=raw["district"],
        address=raw.get("address"), public_address=raw.get("public_address"), finding_minutes=int(_draw(raw.get("finding_minutes", 0), rng)),
        phone=raw.get("phone"), email=raw.get("email"), web_domain=raw.get("web_domain"),
        discover=list(raw["discover"]), open_hhmm=hours.get("open", "10:00"), close_hhmm=hours.get("close", "21:00"),
        signal_inside=bool(raw.get("signal_inside", True)), phone_answers=bool(_draw(phone.get("answers", True), rng)),
        phone_knowledge=str(phone.get("knowledge", "knows")), email_channel=str(raw.get("email_channel", "silent")),
        ai_call=str(raw.get("ai_call", "busy")), delivery_offers=bool(delivery.get("offers", False)),
        delivery_claims_by_phone=delivery.get("claims_by_phone"), delivery_price_egp=delivery.get("price_egp"),
        delivery_minutes=delivery.get("minutes"), offers=offers, not_stocked=list(raw.get("not_stocked") or []),
        join=join, phone_claims=[Claim(**c) for c in raw.get("phone_claims") or []],
        web_claims=[Claim(**c) for c in raw.get("web_claims") or []], online_only=bool(raw.get("online_only", False)),
        no_cutting_service=bool(raw.get("no_cutting_service", False)), observed=True, note=raw.get("note"))


SHOP_NAMES = {
    "electronics_retail": "محل إلكترونيات",
    "electrician": "محل كهربائي",
    "stationery": "مكتبة وأدوات مكتبية",
    "mobile_accessories": "محل إكسسوارات موبايل",
    "grocery": "بقالة",
    "housewares": "محل أدوات منزلية",
    "plumbing_hardware": "محل حدايد وأدوات سباكة",
}


ADDED_CATEGORIES = ("grocery", "housewares", "plumbing_hardware")


def _walk_in(district: str, category: str, n: int, priors: dict[str, Raw], rng: random.Random) -> Supplier:
    stock = (priors["stock"] or {}).get(category) or {}
    offers = []
    for item, p in stock.items():
        if rng.random() < float(p["p"]):
            offers.append(Offer(item=item, count=int(_range(p["count"], rng)), price_egp=float(_range(p["price_egp"], rng))))
    join = None
    service = ((priors["services"] or {}).get(category) or {}).get("join_head")
    if service is not None:
        offered = rng.random() < float(service["p_offered"])
        join = JoinService(offered=offered, price_per_head_egp=float(_range(service["price_per_head_egp"], rng)),
                           minutes_per_head=int(_range(service["minutes_per_head"], rng)),
                           busy_until_minutes_after_arrival=int(_range(service["busy_until_minutes_after_arrival"], rng)),
                           max_heads_per_day=int(_range(service["max_heads_per_day"], rng)), receipt=rng.random() < 0.5)
    channels = priors["channels"]
    knowledge = channels["phone_knowledge"]
    return Supplier(
        key=f"walkin-{district}-{category}-{n}", name=f"{SHOP_NAMES[category]} ({n})", category=category,
        district=district, discover=["walk"], address=f"shop {n} on the main market street, {district.replace('_', ' ')}", signal_inside=rng.random() < float(channels["signal_inside"]),
        phone=f"01{rng.randint(0, 2)}{rng.randint(10000000, 99999999)}",
        phone_answers=rng.random() < float(channels["phone_by_worker"]["answers"]),
        phone_knowledge=rng.choices(list(knowledge), weights=[float(v) for v in knowledge.values()])[0],
        offers=offers, join=join, observed=False)


def build(seed: int) -> World:
    rng = random.Random(seed)
    items = {i["key"]: ItemType(**i) for i in _load("items.yaml")}
    suppliers: dict[str, Supplier] = {}
    # Entities added after the first measured worlds draw from their own stream, so every seed keeps its earlier world unchanged.
    extra = random.Random(seed * 7919 + 1)
    added: set[str] = set()
    v10 = random.Random(seed * 104729 + 7)
    for raw in _load("suppliers.yaml"):
        s = _supplier(raw, v10 if raw.get("added") == "v10" else extra if raw.get("added") else rng)
        if raw.get("added"):
            added.add(s.key)
        for o in s.offers:
            if o.item not in items:
                raise ValueError(f"{s.key} offers unknown item {o.item}")
        suppliers[s.key] = s
    priors = _load("priors.yaml")
    for s in suppliers.values():
        stock = (priors["stock"] or {}).get(s.category) or {}
        have = {o.item for o in s.offers} | set(s.not_stocked)
        for item, pr in stock.items():
            r = extra if s.key in added or s.category in ADDED_CATEGORIES else rng
            if item not in have and not s.online_only and r.random() < float(pr["p"]):
                s.offers.append(Offer(item=item, count=int(_range(pr["count"], r)), price_egp=float(_range(pr["price_egp"], r))))
    for district, cats in priors["walk_in_shops"].items():
        for category, expected in cats.items():
            r = extra if category in ADDED_CATEGORIES or district == "delivery_area" else rng
            n = max(0, round(expected + r.uniform(-1, 1)))
            for i in range(1, n + 1):
                s = _walk_in(district, category, i, priors, r)
                suppliers[s.key] = s
    for s in suppliers.values():
        for o in s.offers:
            if o.item not in items:
                raise ValueError(f"{s.key} offers unknown item {o.item}")
        for k in s.not_stocked:
            if k not in items:
                raise ValueError(f"{s.key} lists unknown not_stocked item {k}")
    for s in suppliers.values():
        stock = (priors.get("stock_v10") or {}).get(s.category) or {}
        have = {o.item for o in s.offers} | set(s.not_stocked)
        for item, pr in stock.items():
            if item not in have and not s.online_only and v10.random() < float(pr["p"]):
                s.offers.append(Offer(item=item, count=int(_range(pr["count"], v10)), price_egp=float(_range(pr["price_egp"], v10))))
    for cat in [*(priors["stock"] or {}).values(), *(priors.get("stock_v10") or {}).values()]:
        for k in cat:
            if k not in items:
                raise ValueError(f"prior lists unknown item {k}")
    workers = {w["id"]: WorkerSpec(**w) for w in _load("workers.yaml")}
    ws = priors["workspaces"]
    return World(seed=seed, items=items, suppliers=suppliers, workers=workers, travel=sample_profile(rng),
                 cafe_search_minutes=int(_range(ws["cafe_search_minutes"], rng)),
                 cafe_cost_egp=int(_range(ws["cafe_cost_egp"], rng)))
