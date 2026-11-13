"""Check that each trial ran on a working world before it is audited or scored. A void trial is run again, never reported.

A trial is void when the agent run ended in an error, when it has no grade, or when one simulator call took longer than
STALL_SECONDS. The project clock stops during simulator calls, but the agent still waits for its tools in real time; a world that
stalls for many minutes (the model refusing or failing requests) is something no real field team shows, and agents react to it.

    python scripts/check_trials.py jobs/r16 [jobs/r16b ...]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STALL_SECONDS = 600  # rounds r12 and r13: 3,556 calls, longest 352 s, 95% under 90 s


def problems(trial: Path) -> list[str]:
    found = []
    result = json.loads((trial / "result.json").read_text()) if (trial / "result.json").exists() else {}
    if not result:
        found.append("no run record (result.json)")
    elif result.get("exception_info"):
        found.append(f"agent run ended with {result['exception_info']['exception_type']}")
    if not (trial / "verifier" / "score.json").exists():
        found.append("no grade")
    log = trial / "artifacts" / "out" / "simulator.jsonl"
    seconds = [json.loads(line).get("seconds", 0) for line in log.read_text().splitlines() if line.strip()] if log.exists() else []
    if not seconds:
        found.append("no simulator log")
    elif max(seconds) > STALL_SECONDS:
        found.append(f"the world stalled {max(seconds) / 60:.0f} min on one simulator call")
    return found


def trial_dirs(job: Path) -> list[Path]:
    return sorted(p.parent for p in job.glob("*/*__*/config.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("jobs", nargs="+", type=Path)
    void = 0
    for job in parser.parse_args().jobs:
        for trial in trial_dirs(job):
            found = problems(trial)
            void += bool(found)
            print(f"{trial.name}: {'VOID: ' + '; '.join(found) if found else 'valid'}")
    return 1 if void else 0


if __name__ == "__main__":
    sys.exit(main())
