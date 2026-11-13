"""Ride-hailing times and fares calibrated on the 24 recorded Memphis trips (the constants below), as data for the facts.

Quoted minutes use the observed median for recorded district pairs and a fitted road model otherwise. Fares are quoted minutes times a
per-quote rate (observed 3.5-8.1 EGP per quoted minute, median 5.8). Actual car time is the quote times a
narrow seed-level traffic bias and a wide per-trip spread: the observed car ratios 1.35-2.13 all came from one week,
so most of the spread is per trip (sim mean 1.68, p10 1.36, p90 2.0). A long departure slip (about 35 minutes, once) is extra. The paid amount stays within about 10% of the quote, as observed.
"""

from __future__ import annotations

import math
import random

from pydantic import BaseModel

DISTRICTS: dict[str, tuple[float, float]] = {
    "downtown_bab_el_louk": (30.0444, 31.2400),
    "dokki": (30.0380, 31.2120),
    "manial": (30.0200, 31.2290),
    "new_maadi": (29.9750, 31.2850),
    "maadi_degla": (29.9600, 31.2570),
    "hadayek_october": (29.9660, 31.0050),
    "sixth_october": (29.9550, 30.9300),
    "delivery_area": (29.9650, 31.3100),
    "helwan": (29.8500, 31.3340),
    "hadayek_el_ahram": (29.9930, 31.1050),
    "abbasiya": (30.0720, 31.2830),
    "mokattam": (30.0110, 31.3010),
}


OBSERVED_QUOTED_MINUTES: dict[frozenset[str], int] = {
    frozenset({"new_maadi", "downtown_bab_el_louk"}): 30,
    frozenset({"dokki", "downtown_bab_el_louk"}): 12,
    frozenset({"dokki", "hadayek_october"}): 54,
    frozenset({"downtown_bab_el_louk", "hadayek_october"}): 59,
    frozenset({"new_maadi", "maadi_degla"}): 18,
    frozenset({"hadayek_october", "delivery_area"}): 51,
    frozenset({"manial", "downtown_bab_el_louk"}): 27,
    frozenset({"new_maadi", "sixth_october"}): 57,
    frozenset({"hadayek_october", "new_maadi"}): 39,
    frozenset({"new_maadi", "delivery_area"}): 13,
}


def straight_km(a: str, b: str) -> float:
    (la1, lo1), (la2, lo2) = DISTRICTS[a], DISTRICTS[b]
    dy = (la2 - la1) * 111.0
    dx = (lo2 - lo1) * 111.0 * math.cos(math.radians((la1 + la2) / 2))
    return math.hypot(dx, dy)


class TravelProfile(BaseModel):
    traffic_bias: float
    trip_spread: float
    base_minutes: float
    minutes_per_km: float


def sample_profile(rng: random.Random) -> TravelProfile:
    return TravelProfile(traffic_bias=rng.uniform(1.5, 1.85), trip_spread=0.22, base_minutes=12.0, minutes_per_km=1.45)


def walk_minutes(origin: str, destination: str) -> int | None:
    if origin == destination:
        return 8
    km = straight_km(origin, destination)
    return round(km * 1.3 * 13) if km <= 2.5 else None
