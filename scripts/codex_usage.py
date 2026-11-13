"""Print the ChatGPT plan's Codex usage as JSON: percent used of the short (5-hour) and the weekly window.

    python3 scripts/codex_usage.py

Sends one tiny Codex request, then reads the rate-limit snapshot Codex saves in that session's rollout file. Prints {} when no
snapshot is found, so the caller stops and asks a person instead of guessing.
"""

import json
import subprocess
import time
from pathlib import Path

SESSIONS = Path.home() / ".codex" / "sessions"


def snapshots(node):
    if isinstance(node, dict):
        if isinstance(node.get("rate_limits"), dict):
            yield node["rate_limits"]
        for value in node.values():
            yield from snapshots(value)
    elif isinstance(node, list):
        for value in node:
            yield from snapshots(value)


def main() -> None:
    start = time.time()
    subprocess.run(["codex", "exec", "--skip-git-repo-check", "-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=low",
                    "Reply with the single word OK."], capture_output=True, timeout=300)
    latest = {}
    for rollout in sorted(SESSIONS.rglob("rollout-*.jsonl"), key=lambda p: p.stat().st_mtime):
        if rollout.stat().st_mtime < start:
            continue
        for line in rollout.read_text().splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            for snap in snapshots(event):
                latest = snap
    windows = {}
    for name in ("primary", "secondary"):
        w = latest.get(name) or {}
        if "used_percent" in w:
            windows[name] = {"used_percent": w["used_percent"], "window_minutes": w.get("window_minutes")}
    print(json.dumps(windows))


if __name__ == "__main__":
    main()
