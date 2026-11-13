"""Simulated friction rates in a round against the October counts (Table 1 of the paper).

Usage, from paper/: python3 friction_check.py friction_coded   (or another folder of coded trials)
friction_coded/ holds one JSON file per final-round trial, coded from the trial's world log, chat and calls with
friction_guide.md. Intervals are the central 90% of a Beta(k+1, n-k+1) posterior, as in Table 1. A kind matches
October when the two intervals overlap.

The guide gave "we can join it in under an hour" as a K1 example, so coders filed shops that broke such a promise under K1
only. October counted that case under both K1 and K4, so here a broken "within/under an hour" claim also counts under K4.
"""
import json, random, re, sys
from pathlib import Path

OCTOBER = {  # kind: (label, events, opportunities, Table 1 interval); K3 and K7 count the good outcome
    "K1": ("A phone or counter claim is wrong when acted on", 4, 9, (0.22, 0.70)),
    "K2": ("The first ask for a specific item fails", 12, 19, (0.44, 0.78)),
    "K3": ("A shop does small custom electrical work within one or two days", 2, 8, (0.10, 0.55)),
    "K4": ("A technician's time promise slips or breaks", 3, 5, (0.27, 0.85)),
    "K5": ("A technician's join fails", 0, 2, (0.02, 0.63)),
    "K6": ("A long car ride takes longer than the app's estimate", 4, 6, (0.34, 0.87)),
    "K7": ("A remote call or email gives a usable quote", 0, 30, (0.00, 0.09)),
    "K9": ("A worker photo needs a redo or a follow-up question", 9, 53, (0.10, 0.27)),
}

def interval(k, n, draws=200_000, seed=7):
    rng = random.Random(seed)
    xs = sorted(rng.betavariate(k + 1, n - k + 1) for _ in range(draws))
    return xs[int(0.05 * draws)], xs[int(0.95 * draws)]

def main():
    coded = [json.loads(p.read_text()) for p in sorted(Path(sys.argv[1]).glob("*.json")) if p.name != "summary.json"]
    print(f"{len(coded)} trials coded\n")
    rows = []
    for kind, (label, ok, on, oi) in OCTOBER.items():
        k = n = 0
        for c in coded:
            items = c["kinds"].get(kind, {}).get("items", [])
            if kind == "K6":
                items = [i for i in items if i.get("long")]
            if kind == "K4":
                items = items + [i for i in c["kinds"].get("K1", {}).get("items", [])
                                 if i.get("happened") is True and re.search(r"(within|under) an hour", i.get("what", ""), re.I)]
            k += sum(1 for i in items if i.get("happened") is True)
            n += sum(1 for i in items if i.get("happened") in (True, False))
        lo, hi = interval(k, n) if n else (None, None)
        rate = k / n if n else None
        inside = n > 0 and lo <= oi[1] and hi >= oi[0]
        rows.append((kind, label, ok, on, oi, k, n, rate, lo, hi, inside))
        sim = f"{k} of {n} = {rate:.2f} (90% {lo:.2f} to {hi:.2f})" if n else "no opportunities"
        print(f"{kind} {label}\n   October {ok} of {on} = {ok/on:.2f} (90% {oi[0]:.2f} to {oi[1]:.2f}) | simulated {sim} | "
              f"{'overlaps October' if inside else 'does NOT overlap October'}")
    ratios = [i["actual_min"] / i["quoted_min"] for c in coded for i in c["kinds"].get("K6", {}).get("items", [])
              if i.get("long") and i.get("quoted_min") and i.get("actual_min")]
    if ratios:
        ratios.sort()
        print(f"\nLong rides, actual over quoted time: median {ratios[len(ratios)//2]:.2f}, range {ratios[0]:.2f} to {ratios[-1]:.2f} (October 1.5 to 2)")
    json.dump([dict(zip(["kind", "label", "oct_k", "oct_n", "oct_interval", "sim_k", "sim_n", "sim_rate", "sim_lo", "sim_hi", "inside"], r)) for r in rows],
              open(Path(sys.argv[1]) / "summary.json", "w"), indent=1)

if __name__ == "__main__":
    main()
