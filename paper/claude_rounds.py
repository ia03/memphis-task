"""The Claude Code rounds on the frozen version together (c1, and the replicates c2 and c3): three trials per seed and condition.

    python3 claude_rounds.py AUDITS_DIR ROUND=JOB[,JOB...] [ROUND=JOB[,JOB...] ...]

    e.g. python3 claude_rounds.py ../audits c1=../jobs/c1,../jobs/c1b-10-hinted \\
             c2=../jobs/c2a,../jobs/c2,../jobs/c2b-* c3=../jobs/c3,../jobs/c3b-*

For each round, the valid trial of each task is taken from its jobs (a later job replaces a void trial, as in
scripts/round_trials.py). Prints, per condition: lamps and mean score over all trials; the mean of the per-seed means with a
95% bootstrap interval that resamples seeds and keeps each seed's trials together; how much of the variance in scores lies
within a seed (between repeats of the same task) rather than between seeds; and the hint gap per seed, with how many seeds show
a positive, zero or negative gap. Audit verdicts are counted from the audits' closing JSON blocks.
"""

import glob
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scripts"))
from agent_round import rows_for  # noqa: E402
from check_trials import problems, trial_dirs  # noqa: E402

SEEDS = (10, 11, 12, 13, 14)


def task(trial: Path) -> tuple:
    name = Path(json.loads((trial / "config.json").read_text())["task"]["path"]).name
    seed, cond = name.removeprefix("memphis-seed").split("-", 1)
    return int(seed), cond


def valid_trials(jobs: list) -> list:
    chosen = {}
    for job in jobs:
        for trial in trial_dirs(Path(job)):
            if not problems(trial):
                chosen[task(trial)] = trial
    return [chosen[k] for k in sorted(chosen)]


def seed_bootstrap(per_seed: dict, n: int = 10000, rng=random.Random(20261104)) -> tuple:
    seeds = sorted(per_seed)
    draws = []
    for _ in range(n):
        pick = [rng.choice(seeds) for _ in seeds]
        draws.append(statistics.mean(statistics.mean(per_seed[s]) for s in pick))
    draws.sort()
    return draws[int(0.025 * n)], draws[int(0.975 * n) - 1]


def main() -> None:
    audits = Path(sys.argv[1])
    rows = []
    for spec in sys.argv[2:]:
        rnd, jobs = spec.split("=", 1)
        paths = [p for j in jobs.split(",") for p in (glob.glob(j) or [j])]
        rows += rows_for(audits, valid_trials(paths), rnd)
    by = defaultdict(list)
    for r in rows:
        by[(r["cond"], r["seed"])].append(r["score"])
    rounds = sorted({r["round"] for r in rows})
    print(f"rounds {', '.join(rounds)}: {len(rows)} valid trials")
    verdicts = defaultdict(int)
    for r in rows:
        verdicts[r["fair"]] += 1
    print("audit verdicts:", dict(verdicts))
    means = {}
    for cond in ("hinted", "unhinted"):
        rs = [r for r in rows if r["cond"] == cond]
        per_seed = {s: by[(cond, s)] for s in SEEDS if by[(cond, s)]}
        if not per_seed:
            continue
        m = statistics.mean(statistics.mean(v) for v in per_seed.values())
        lo, hi = seed_bootstrap(per_seed)
        means[cond] = per_seed
        within = [statistics.pvariance(v) for v in per_seed.values() if len(v) > 1]
        total = statistics.pvariance([x for v in per_seed.values() for x in v])
        share = (statistics.mean(within) / total) if within and total else float("nan")
        print(f"{cond}: {sum(r['lamps'] for r in rs)} lamps in {len(rs)} trials; mean of seed means {m:.2f} "
              f"(95% seed bootstrap {lo:.2f} to {hi:.2f}); share of variance within seeds {share:.2f}")
        for s in SEEDS:
            if per_seed.get(s):
                print(f"  seed {s}: scores {per_seed[s]}")
    if len(means) == 2:
        gaps = {s: statistics.mean(means["hinted"][s]) - statistics.mean(means["unhinted"][s])
                for s in SEEDS if s in means["hinted"] and s in means["unhinted"]}
        pos = sum(g > 0 for g in gaps.values())
        neg = sum(g < 0 for g in gaps.values())
        diff = {s: [h - u for h in means["hinted"][s] for u in means["unhinted"][s]] for s in gaps}
        lo, hi = seed_bootstrap(diff)
        print(f"hint gap: {statistics.mean(gaps.values()):+.2f} (95% seed bootstrap {lo:+.2f} to {hi:+.2f}); "
              f"seeds with the hint ahead {pos}, behind {neg}, equal {len(gaps) - pos - neg}")


if __name__ == "__main__":
    main()
