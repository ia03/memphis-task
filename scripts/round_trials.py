"""List a round's trials for scripts/claude_round.sh, using the validity check in scripts/check_trials.py.

    python3 scripts/round_trials.py count JOB         number of trials in the job
    python3 scripts/round_trials.py void JOB          "SEED COND" of each void trial
    python3 scripts/round_trials.py valid [--round c1] JOB...
        "TRIAL_DIR SLUG" of each task's valid trial (the last job listed wins); SLUG is ROUND-sSEED-COND
    python3 scripts/round_trials.py gate BEFORE AFTER JOB [PLANNED]
        how many trials may run at once (0: the round must not start) and why, from the Codex usage before and after the
        test trial (scripts/codex_usage.py) and the Claude plan usage its agent log reports

The gate refuses the round when the PLANNED trials still to run (10 by default; and, for Claude, their audits too) would pass
about 95% of a weekly limit, and runs fewer at once when one trial alone fills much of a short (5-hour) window.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_trials import problems, trial_dirs  # noqa: E402


def task(trial: Path) -> tuple[str, str]:
    name = Path(json.loads((trial / "config.json").read_text())["task"]["path"]).name  # memphis-seed10-unhinted
    seed, cond = name.removeprefix("memphis-seed").split("-", 1)
    return seed, cond


def codex_window(usage: dict, weekly: bool) -> float | None:
    for w in usage.values():
        minutes = w.get("window_minutes") or 0
        if (weekly and minutes >= 10080) or (not weekly and 0 < minutes <= 720):
            return float(w["used_percent"])
    return None


def claude_windows(job: Path) -> list[dict]:
    """Percent used of the Claude plan's windows, from each rate_limit_event in the job's agent logs, in order."""
    seen = []
    for trial in trial_dirs(job):
        for line in (trial / "agent" / "claude-code.txt").read_text(errors="ignore").splitlines():
            if '"rate_limit_event"' not in line:
                continue
            try:
                windows = json.loads(line)["rate_limit_info"]["unifiedWindows"]
                seen.append({k: 100 * float(v["utilization"]) for k, v in windows.items()})
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
    return seen


def gate(before: dict, after: dict, job: Path, planned: int = 10) -> tuple[int, str]:
    week0, week1 = codex_window(before, True), codex_window(after, True)
    if week0 is None or week1 is None:
        return 0, "Codex did not report its weekly usage"
    codex_trial = max(week1 - week0, 0.1)
    if week1 + planned * codex_trial > 95:
        return 0, f"{planned} trials would pass the Codex weekly limit ({codex_trial:.1f}% per trial, {week1:.0f}% used)"
    n, why = 10, [f"Codex {codex_trial:.1f}% of the week per trial, {week1:.0f}% used"]
    short = codex_window(after, False)
    if short:
        n = min(n, int(90 // short))
    claude = claude_windows(job)
    if claude:
        c_week0, c_week1 = claude[0].get("seven_day", 0), claude[-1].get("seven_day", 0)
        claude_trial = max(c_week1 - c_week0, 0)
        # 1.3: the audits and friction counts also run on the Claude plan
        if c_week1 + 1.3 * planned * claude_trial > 95:
            return 0, f"{planned} trials and their audits would pass the Claude weekly limit ({claude_trial:.1f}% per trial, {c_week1:.0f}% used)"
        c_short = claude[-1].get("five_hour", 0)
        if c_short:
            n = min(n, int(90 // c_short))
        why.append(f"Claude {claude_trial:.1f}% of the week per trial, {c_week1:.0f}% used, {c_short:.0f}% of 5 hours")
    else:
        why.append("Claude reported no usage")
    return max(1, n), "; ".join(why)


def main() -> None:
    cmd = sys.argv[1]
    if cmd == "gate":
        planned = int(sys.argv[5]) if len(sys.argv) > 5 else 10
        n, why = gate(json.loads(sys.argv[2]), json.loads(sys.argv[3]), Path(sys.argv[4]), planned)
        print(n, why)
        return
    args = sys.argv[2:]
    rnd = "c1"
    if args[:1] == ["--round"]:
        rnd, args = args[1], args[2:]
    jobs = [Path(j) for j in args]
    if cmd == "count":
        print(len(trial_dirs(jobs[0])))
    elif cmd == "void":
        for trial in trial_dirs(jobs[0]):
            if problems(trial):
                print(*task(trial))
    elif cmd == "valid":
        chosen = {}
        for job in jobs:
            for trial in trial_dirs(job):
                if not problems(trial):
                    chosen[task(trial)] = trial
        for (seed, cond), trial in sorted(chosen.items()):
            print(trial, f"{rnd}-s{seed}-{cond}")


if __name__ == "__main__":
    main()
