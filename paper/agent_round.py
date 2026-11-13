"""One row per trial of a Claude Code round: lamps, score, spend, the agent's API-equivalent cost and tokens, the audit verdict.

    python3 agent_round.py [--round c1] AUDITS_DIR TRIAL_DIR...

TRIAL_DIR is a Harbor trial folder whose agent ran under harbor_ext/memphis_claude.py. Cost and tokens come from the closing
stream-json result event of each session part (agent/claude-code-part*.txt). The verdict, fair range and best estimate come
from the JSON block that ends the trial's audit (AUDITS_DIR/audit-<round>-s<seed>-<cond>.md), when it exists.
"""

import json
import re
import sys
from pathlib import Path

TARGET = 9


def closing(part: Path) -> dict:
    last = {}
    for line in part.read_text(errors="ignore").splitlines():
        if line.startswith("{") and '"type":"result"' in line.replace(" ", ""):
            last = json.loads(line)
    return last


def audit(path: Path) -> dict:
    if not path.exists():
        return {}
    blocks = re.findall(r"\{[^{}]*\"fair\"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", path.read_text(), flags=re.S)
    for block in reversed(blocks):
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    return {}


def rows_for(audits: Path, trials: list, rnd: str = "c1") -> list:
    rows = []
    for d in trials:
        name = Path(json.loads((d / "config.json").read_text())["task"]["path"]).name
        seed, cond = name.removeprefix("memphis-seed").split("-", 1)
        score = json.loads((d / "verifier" / "score.json").read_text())
        parts = sorted((d / "agent").glob("claude-code-part*.txt")) or [d / "agent" / "claude-code.txt"]
        cost, tokens = 0.0, {"cache_read": 0, "output": 0}
        for part in parts:
            end = closing(part)
            cost += end.get("total_cost_usd") or 0
            for usage in (end.get("modelUsage") or {}).values():
                tokens["cache_read"] += usage.get("cacheReadInputTokens", 0)
                tokens["output"] += usage.get("outputTokens", 0)
        a = audit(audits / f"audit-{rnd}-s{seed}-{cond}.md")
        lamps = score["qualifying_delivered"]
        rows.append(dict(seed=int(seed), cond=cond, lamps=lamps, score=round(min(lamps / TARGET, 1), 2), spent=score["spent_egp"],
                         cost_usd=round(cost, 2), cache_read_m=round(tokens["cache_read"] / 1e6, 1),
                         output_k=round(tokens["output"] / 1e3), parts=len(parts), fair=a.get("fair"),
                         fair_range=a.get("fair_lamp_range"), expected=a.get("expected_fair_lamps"), trial=d.name,
                         round=rnd))
    return rows


def main() -> None:
    args = sys.argv[1:]
    rnd = "c1"
    if args[:1] == ["--round"]:
        rnd, args = args[1], args[2:]
    rows = rows_for(Path(args[0]), [Path(p) for p in args[1:]], rnd)
    for r in sorted(rows, key=lambda r: (r["cond"] != "hinted", r["seed"])):
        print(json.dumps(r))
    for cond in ("hinted", "unhinted"):
        rs = [r for r in rows if r["cond"] == cond]
        if rs:
            print(f"{cond}: {sum(r['lamps'] for r in rs)} lamps in {len(rs)} trials, mean score "
                  f"{sum(r['score'] for r in rs) / len(rs):.2f}, mean agent cost ${sum(r['cost_usd'] for r in rs) / len(rs):.2f}")


if __name__ == "__main__":
    main()
