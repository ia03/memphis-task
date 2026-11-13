"""Compare a person's answers from the audit review page with the auditor's reports.

    python3 paper/audit_review/score_review.py paper/audit_review/answers/reviewer_1.json

Reads each reviewed trial's audit (audits/audit-<trial>.md, its JSON block) for the auditor's verdict and the class of each
finding, and prints the agreement on verdicts, on the account of why lamps were lost, and on each finding by class.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCALE = ["yes", "mostly", "partly", "no"]  # fair, mostly fair, partly fair, not fair


def audit(trial: str) -> dict:
    text = (ROOT / "audits" / f"audit-{trial}.md").read_text()
    block = json.loads(re.search(r"```json\s*(\{.*?\})\s*```", text, re.S).group(1))
    classes = {}
    for value in block.values():
        if isinstance(value, list):
            for f in value:
                if isinstance(f, dict) and "id" in f:
                    classes.setdefault(f["id"], f["class"])
    return {"fair": block["fair"], "classes": classes}


def main(path: str) -> None:
    trials = json.loads(Path(path).read_text())["trials"]
    same, causes, marks = 0, Counter(), Counter()
    for trial, r in sorted(trials.items()):
        a = audit(trial)
        steps = SCALE.index(r["verdict"]) - SCALE.index(a["fair"])
        same += steps == 0
        causes[r["cause"]] += 1
        unmarked = set(a["classes"]) - set(r["findings"])
        for fid, m in r["findings"].items():
            marks[(a["classes"][fid], m["mark"])] += 1
        print(f"{trial}: auditor {a['fair']}, reviewer {r['verdict']} ({steps:+d} steps), cause {r['cause']}, "
              f"findings " + ", ".join(f"{fid} {a['classes'][fid]} {m['mark']}" for fid, m in sorted(r["findings"].items()))
              + (f", not marked: {sorted(unmarked)}" if unmarked else ""))
    n = sum(marks.values())
    print(f"\nSame verdict: {same} of {len(trials)}. Account of why lamps were lost: {dict(causes)}.")
    print(f"Findings: {n}; " + ", ".join(f"{k} {v}" for k, v in sorted(Counter(m for _, m in marks.elements()).items())))
    for cls in sorted({c for c, _ in marks}):
        print(f"  class {cls}: " + ", ".join(f"{m} {v}" for (c, m), v in sorted(marks.items()) if c == cls))


if __name__ == "__main__":
    main(sys.argv[1])
