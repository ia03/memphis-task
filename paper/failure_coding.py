"""Score the blind failure coding against the authors' mapping (Section 6.3 of the paper).

    python3 paper/failure_coding.py

failure_coding/trials/T01-T30.txt are the timeline and cause sections of the thirty unhinted audits, with round names removed
and the order shuffled; key.json maps each id to its trial and holds the authors' labels. T01-T20 (rounds r13, r16, r18 and
the Claude round c1) were coded first, from instructions.md (codes_claude.json, codes_gpt.json). T21-T30 (the Claude rounds c2
and c3) were coded later in the same way, from batch2/instructions.md, which differs only in the trial ids
(codes_claude_batch2.json, codes_gpt_batch2.json). Each batch was coded by a fresh Claude instance and a fresh GPT instance
that did not see key.json; the authors' labels for T21-T30 were written before the coders' answers were read.
"""
import json
from pathlib import Path

D = Path(__file__).resolve().parent / "failure_coding"
NAMES = {"A": "stands", "B": "heads late", "C": "stops looking", "D": "no margin"}


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    key = json.loads((D / "key.json").read_text())
    coders = {name: {x["trial"]: x for f in (f"codes_{name}.json", f"codes_{name}_batch2.json")
                     for x in json.loads((D / f).read_text())} for name in ("claude", "gpt")}
    trials = sorted(key)

    def labels(src, ts):
        if src == "ours":
            return [c in key[t]["ours"] for t in ts for c in NAMES]
        return [bool(coders[src][t][c]) for t in ts for c in NAMES]

    for x, y in (("ours", "claude"), ("ours", "gpt"), ("claude", "gpt")):
        a, b = labels(x, trials), labels(y, trials)
        print(f"{x} vs {y}: agree {sum(p == q for p, q in zip(a, b))}/{len(a)}, kappa {kappa(a, b):.2f}")
    for rounds, title in (({"r13", "r16", "r18"}, "GPT rounds"), ({"c1", "c2", "c3"}, "Claude rounds")):
        ts = [t for t in trials if key[t]["round"] in rounds]
        for src in ("ours", "claude", "gpt"):
            lab = labels(src, ts)
            counts = {NAMES[c]: sum(lab[i * 4 + j] for i in range(len(ts))) for j, c in enumerate(NAMES)}
            print(f"{title} ({len(ts)} trials), {src}: {counts}")


if __name__ == "__main__":
    main()
