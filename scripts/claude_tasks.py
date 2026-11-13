"""Build the final round's tasks for a Claude Code agent: the frozen v12.0-rc17 tasks with only the agent's side changed.

    .venv/bin/python scripts/claude_tasks.py OUT_DIR [--auth ~/.codex/auth.json] [--job NAME --seeds 10 11 --conds unhinted]

The tag's own build_task.py builds each task, so the world (environment/sim) is what round r18 ran; the script prints each
task's sim checksum to compare with the r18 tasks built from the same tag (the released copies are redacted, so theirs
differ). Two files change: the agent container also installs Claude Code, and the egress proxy also lets it reach Anthropic's
API. It also writes a Harbor job config for the tasks it built.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

from dirhash import dirhash

ROOT = Path(__file__).resolve().parent.parent
TAG = "v12.0-rc17"
CLAUDE_CODE = "2.1.311"  # npm "stable" tag on 2 Nov 2026
CODEX_LINE = "    && codex --version\n"
SQUID_LINE = "acl openai_api dstdomain .chatgpt.com auth.openai.com api.openai.com\n"
JOB = """jobs_dir: ./jobs/{job}
job_name: {job}
n_attempts: 1
n_concurrent_trials: {n}
agents:
- import_path: harbor_ext.memphis_claude:MemphisClaude
  model_name: anthropic/claude-opus-5-5
  kwargs:
    reasoning_effort: medium
tasks:
{tasks}
"""


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one {old.strip()!r}")
    path.write_text(text.replace(old, new))


def for_claude(task: Path) -> None:
    replace_once(task / "environment" / "Dockerfile", CODEX_LINE,
                 f"    && codex --version \\\n    && npm install -g @anthropic-ai/claude-code@{CLAUDE_CODE} \\\n"
                 "    && claude --version\n")
    replace_once(task / "environment" / "proxy" / "squid.conf", SQUID_LINE,
                 SQUID_LINE.rstrip("\n") + " api.anthropic.com\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--auth", type=Path, default=Path.home() / ".codex" / "auth.json")
    p.add_argument("--job", default="claude")
    p.add_argument("--seeds", type=int, nargs="+", default=[10, 11, 12, 13, 14])
    p.add_argument("--conds", nargs="+", default=["unhinted", "hinted"])
    a = p.parse_args()
    out = a.out.resolve()
    built = []
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp)
        archive = subprocess.run(["git", "archive", TAG], cwd=ROOT, check=True, capture_output=True).stdout
        subprocess.run(["tar", "-x", "-C", str(src)], input=archive, check=True)
        for seed in a.seeds:
            for cond in a.conds:
                task = out / f"memphis-seed{seed}-{cond}"
                cmd = [sys.executable, str(src / "build_task.py"), "--seed", str(seed), "--target", "9", "--out", str(task),
                       "--auth", str(a.auth)]
                if cond == "hinted":
                    cmd += ["--hint-file", str(src / "world" / "hint_note_v3.md")]
                subprocess.run(cmd, check=True)
                for_claude(task)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    print(f"{task.name}: sim {dirhash(task / 'environment' / 'sim', 'sha256')}")
                built.append(task)
    tasks = "\n".join(f"- path: {t}" for t in built)
    config = out / f"{a.job}.yaml"
    config.write_text(JOB.format(job=a.job, n=len(built), tasks=tasks))
    print(f"{config}: {len(built)} tasks")


if __name__ == "__main__":
    main()
