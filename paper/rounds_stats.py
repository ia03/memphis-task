"""The hint's effect across the three audited rounds on the one-model design (r13, r16, r18), and in the three Claude rounds on
the frozen version (c1, c2, c3) set against r18: sign tests and bootstrap intervals.

    python3 rounds_stats.py ../RESULTS.md

Reads each round's per-seed lamp counts from RESULTS.md. A trial's score is its number of lamps. For each round it gives the
mean score per condition, the hinted-minus-unhinted gap with a paired bootstrap interval over the five seeds, and an exact sign
test on the five seed pairs. Pooled over the rounds it resamples seeds, keeping all three rounds of a seed together, because the
rounds share seeds and so are not independent. For c1, c2 and c3 it gives the same per-round figures, the same figures pooled
over the three rounds, and, in each condition, GPT-6.1 Sol (r18) minus Claude Opus 5.5 (the mean of its three rounds) paired by
seed. paper/claude_rounds.py gives the pooled Claude figures from the trial folders themselves.
"""

import random
import re
import sys
from math import comb

B = 20000
ROUND_HEADINGS = {"r18": "## Final round", "r16": "### Round r16", "r13": "### Round r13"}
CLAUDE_HEADINGS = {"c1": "### Round c1", "c2": "### Round c2", "c3": "### Round c3"}


def counts(text: str, heading: str) -> dict:
    """Per-seed (hinted, unhinted) lamp counts from the first table after a heading."""
    block = text.split(heading, 1)[1]
    rows = {}
    for line in block.splitlines():
        m = re.match(r"\|\s*(1[0-4])\s*\|\s*(\d+)[^|]*\|[^|]*\|[^|]*\|\s*(\d+)", line)
        if m:
            rows[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
        elif rows and not line.startswith("|"):
            break
    assert sorted(rows) == [10, 11, 12, 13, 14], (heading, rows)
    return rows


def score(lamps: int) -> float:
    return float(lamps)


def sign_p(wins: int, n: int) -> tuple:
    """Exact sign test with no ties: one-sided and two-sided p."""
    one = sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n
    return one, min(1.0, 2 * one)


def interval(values: list, level: float = 0.95) -> tuple:
    values = sorted(values)
    lo = values[int((1 - level) / 2 * len(values))]
    hi = values[int((1 + level) / 2 * len(values)) - 1]
    return lo, hi


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def main(path: str) -> None:
    text = open(path).read()
    rounds = {r: counts(text, h) for r, h in ROUND_HEADINGS.items()}
    seeds = [10, 11, 12, 13, 14]
    rng = random.Random(0)

    print(f"{'round':6} {'hinted':>7} {'unhinted':>9} {'gap':>6}  95% bootstrap   wins  sign p (one, two-sided)")
    for r in ("r13", "r16", "r18"):
        gaps = [score(rounds[r][s][0]) - score(rounds[r][s][1]) for s in seeds]
        boot = [mean(rng.choice(gaps) for _ in seeds) for _ in range(B)]
        lo, hi = interval(boot)
        wins = sum(g > 0 for g in gaps)
        one, two = sign_p(wins, len(seeds))
        h = mean(score(rounds[r][s][0]) for s in seeds)
        u = mean(score(rounds[r][s][1]) for s in seeds)
        print(f"{r:6} {h:7.2f} {u:9.2f} {mean(gaps):6.2f}  {lo:.2f} to {hi:.2f}   {wins}/5   {one:.3f}, {two:.3f}")
        for cond, i in (("hinted", 0), ("unhinted", 1)):
            vals = [score(rounds[r][s][i]) for s in seeds]
            clo, chi = interval([mean(rng.choice(vals) for _ in seeds) for _ in range(B)])
            print(f"       {cond} mean 95% bootstrap: {clo:.2f} to {chi:.2f}")

    pairs = [(r, s) for r in rounds for s in seeds]
    gap = {(r, s): score(rounds[r][s][0]) - score(rounds[r][s][1]) for r, s in pairs}
    wins = sum(g > 0 for g in gap.values())
    one, two = sign_p(wins, len(pairs))
    boot = []
    for _ in range(B):
        draw = [rng.choice(seeds) for _ in seeds]
        boot.append(mean(gap[r, s] for s in draw for r in rounds))
    lo, hi = interval(boot)
    seed_wins = sum(all(gap[r, s] > 0 for r in rounds) for s in seeds)
    print(f"\npooled over 3 rounds: gap {mean(gap.values()):.2f}, 95% bootstrap over seeds {lo:.2f} to {hi:.2f}")
    print(f"trial pairs with hinted above unhinted: {wins}/{len(pairs)} (sign p {one:.1e} one-sided, {two:.1e} two-sided,"
          " treating pairs as independent)")
    print(f"seeds with hinted above unhinted in every round: {seed_wins}/5 (sign p {sign_p(seed_wins, 5)[0]:.3f} one-sided)")
    print(f"smallest single gap: {min(gap.values()):.2f} at {min(gap, key=gap.get)}")

    claude = {r: counts(text, h) for r, h in CLAUDE_HEADINGS.items()}
    print()
    for r, c in claude.items():
        gaps = [score(c[s][0]) - score(c[s][1]) for s in seeds]
        lo, hi = interval([mean(rng.choice(gaps) for _ in seeds) for _ in range(B)])
        print(f"{r} (Claude Opus 5.5): hinted {mean(score(c[s][0]) for s in seeds):.2f}, unhinted "
              f"{mean(score(c[s][1]) for s in seeds):.2f}, gap {mean(gaps):.2f}, 95% bootstrap {lo:.2f} to {hi:.2f}; hinted above "
              f"unhinted on {sum(g > 0 for g in gaps)}/5 seeds, below on {sum(g < 0 for g in gaps)}/5")
    for cond, i in (("hinted", 0), ("unhinted", 1)):
        per_seed = {s: mean(score(c[s][i]) for c in claude.values()) for s in seeds}
        diff = [score(rounds["r18"][s][i]) - per_seed[s] for s in seeds]
        lo, hi = interval([mean(rng.choice(diff) for _ in seeds) for _ in range(B)])
        print(f"  {cond}: Claude over c1-c3 {mean(per_seed.values()):.2f}; r18 minus Claude {mean(diff):.2f}, 95% bootstrap "
              f"{lo:.2f} to {hi:.2f}; GPT higher on {sum(d > 0 for d in diff)}/5 seeds, lower on {sum(d < 0 for d in diff)}/5")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../RESULTS.md")
