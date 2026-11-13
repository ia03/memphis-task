"""Memphis world simulator: one model, working in its own folder, plays the whole world (workers, shops, city, time).

The folder holds the brief (world/simulator_brief.md), the agent's rules, this seed's facts, the real October record, and the
simulator's own state.md and log.md. Each step tells it the time and what Seb did since its last step; it updates its files and
returns what reaches Seb or the ledger, each with the time it happens. At the end a separate call grades the run from the
same folder. The server (hsim/server.py) only delivers these outputs on time and keeps the money ledger."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import validate

from .clock import CAIRO
from .travel import DISTRICTS, OBSERVED_QUOTED_MINUTES, straight_km, walk_minutes
from .world import ROOT, World, _load

SHIFTS = [(datetime(2026, 10, 1, 14, 0, tzinfo=CAIRO), datetime(2026, 10, 1, 17, 0, tzinfo=CAIRO)),
          (datetime(2026, 10, 4, 13, 0, tzinfo=CAIRO), datetime(2026, 10, 4, 17, 0, tzinfo=CAIRO))]
DEADLINE = SHIFTS[-1][1]
CATALOG = ROOT / "work" / "catalog"


def _obj(**props: Any) -> dict[str, Any]:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def _list(item: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "items": item}


S, N = {"type": "string"}, {"type": "integer"}
STEP_SCHEMA = _obj(
    messages=_list(_obj(at=S, worker=S, text=S, photo=S)),
    payments=_list(_obj(at=S, worker=S, spend_id=S, amount_egp=N)),
    calls=_list(_obj(at=S, key=S, status=S, transcript=S)),
    emails=_list(_obj(at=S, sender=S, subject=S, text=S)),
    cancellations_confirmed=_list(_obj(at=S, worker=S, spend_id=S)),
    withdraw=_list(S),
    wake_at=S,
)
GRADE_SCHEMA = _obj(qualifying_delivered=N, spent_egp=N, lamps=_list(_obj(what=S, delivered_at=S, qualifies={"type": "boolean"}, why=S)))


def facts(world: World) -> dict[str, Any]:
    """The seed's world as data, with ride times and fares between districts from the recorded trips."""
    rides = {}
    for a in DISTRICTS:
        for b in DISTRICTS:
            if a < b:
                p = world.travel
                q = OBSERVED_QUOTED_MINUTES.get(frozenset({a, b})) or round(p.base_minutes + p.minutes_per_km * straight_km(a, b))
                rides[f"{a} <-> {b}"] = {"app_quoted_minutes": q, "fare_egp": [round(q * 4.2), round(q * 7.3)],
                                         "door_to_door_minutes": [round(q * p.traffic_bias * 0.78), round(q * p.traffic_bias * 1.22)],
                                         "walk_minutes": walk_minutes(a, b)}
    return {**world.model_dump(mode="json", exclude={"travel"}), "rides": rides, "walk_between_shops_in_a_district_minutes": f"up to {walk_minutes('dokki', 'dokki')}; 1-2 for shops the facts place next to each other",
            "delivery_address": _load("delivery.yaml"),
            "shifts_cairo": [[a.isoformat(), b.isoformat()] for a, b in SHIFTS]}


MISTAKES = {  # october/incidents.md 2b and 2c, the kinds behind the workers' mistake rates
    "misread": "misunderstands an instruction or a detail of it (2c: usually 2-15 minutes or a wrong step until one explanation fixes it)",
    "wrong_turn": "has navigation or location trouble (2b: 3-40 minutes, usually under 10)",
    "unannounced_change": "changes his route or destination without saying so first (2c)",
}


def commands(events: str) -> list[str]:
    """The shell commands a Codex run executed (what it read and wrote), from its --json event stream, for audits."""
    out = []
    for line in events.splitlines():
        try:
            item = json.loads(line).get("item") or {}
        except ValueError:
            continue
        if item.get("type") == "command_execution" and json.loads(line).get("type") == "item.completed":
            out.append(str(item.get("command", ""))[:300])
    return out


def codex(prompt: str, schema: dict[str, Any], folder: Path, tag: str, log: Any, model: str, effort: str, sandbox: str,
          give_up_after: float = 3 * 3600) -> dict[str, Any]:
    """One Codex run working in folder, answering in schema. Failures (an unreachable model, an expired sign-in, a malformed
    answer) are retried with backoff for up to give_up_after seconds; the project clock is paused meanwhile, so an outage
    only pauses the trial."""
    auth = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json"
    first, attempt = time.monotonic(), 0
    while time.monotonic() - first < give_up_after:
        with tempfile.TemporaryDirectory(prefix="memphis-sim-") as tmp:
            home = Path(tmp) / "codex-home"
            home.mkdir()
            shutil.copyfile(auth, home / "auth.json")
            (Path(tmp) / "schema.json").write_text(json.dumps(schema))
            env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": tmp, "CODEX_HOME": str(home),
                   **{k: v for k, v in os.environ.items() if k.lower().endswith("_proxy") or k == "TMPDIR"}}
            cmd = ["codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules",
                   "-C", str(folder), "-s", sandbox, "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
                   "-c", f'model_reasoning_effort="{effort}"', "-m", model,
                   "--output-schema", str(Path(tmp) / "schema.json"), "-o", str(Path(tmp) / "answer.json"), "-"]
            started, stderr = time.monotonic(), ""
            try:
                proc = subprocess.run(cmd, input=prompt, env=env, capture_output=True, text=True, timeout=3600)  # the clock is paused; wait for a slow answer
                stderr = proc.stderr[-800:]
                answer = json.loads((Path(tmp) / "answer.json").read_text())
                validate(answer, schema)
            except Exception as exc:  # noqa: BLE001 - any failure is logged and retried
                log({"tag": tag, "attempt": attempt, "error": f"{type(exc).__name__}: {str(exc)[:300]}", "stderr": stderr})
                time.sleep(min(15 * 2 ** attempt, 300))
                attempt += 1
                continue
            log({"tag": tag, "seconds": round(time.monotonic() - started), "prompt": prompt, "answer": answer,
                 "commands": commands(proc.stdout)})
            return answer
    raise RuntimeError(f"{tag} failed {attempt} times over {give_up_after / 3600:g} h")


class Simulator:
    def __init__(self, world: World, folder: Path, model: str = os.environ.get("MEMPHIS_SIM_MODEL", "gpt-6.1-sol"),
                 effort: str = os.environ.get("MEMPHIS_SIM_EFFORT", "medium"),
                 sandbox: str = os.environ.get("MEMPHIS_SIM_SANDBOX", "workspace-write")) -> None:
        self.folder, self.model, self.effort, self.sandbox = folder, model, effort, sandbox
        (folder / "october").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "world" / "simulator_brief.md", folder / "BRIEF.md")
        shutil.copyfile(ROOT / "world" / "agent_prompt.md", folder / "task_rules.md")
        shutil.copyfile(ROOT / "world" / "grading.md", folder / "grading.md")
        shutil.copyfile(CATALOG / "october-chats.json", folder / "october" / "worker-chats.json")
        shutil.copyfile(CATALOG / "workers.json", folder / "october" / "workers.json")
        shutil.copyfile(CATALOG / "october-incidents.md", folder / "october" / "incidents.md")
        (folder / "facts.json").write_text(json.dumps(facts(world), ensure_ascii=False, indent=1))
        (folder / "state.md").touch()
        (folder / "log.md").touch()

    def _run(self, prompt: str, schema: dict[str, Any], tag: str) -> dict[str, Any]:
        return codex(prompt, schema, self.folder, tag, self._log, self.model, self.effort, self.sandbox)

    def _log(self, row: dict[str, Any]) -> None:
        with (self.folder.parent / "simulator.jsonl").open("a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def step(self, now: datetime, events: list[dict[str, Any]], pending: list[dict[str, Any]],
             delivered: list[dict[str, Any]], slips: list[tuple[str, str]] | None = None) -> dict[str, Any]:
        prompt = (f"You simulate the world described in BRIEF.md. Read BRIEF.md and state.md, and look up in facts.json every "
                  f"shop, person, ride and walk this step involves, before you decide.\n\n"
                  f"It is now {now.astimezone(CAIRO):%a %d %b %Y %H:%M:%S} Cairo time ({now.astimezone(CAIRO).isoformat()}).\n"
                  f"What Seb did since your last step:\n{json.dumps(events, ensure_ascii=False, indent=1)}\n"
                  f"What you scheduled that reached Seb or the ledger since your last step:\n{json.dumps(delivered, ensure_ascii=False, indent=1)}\n"
                  f"What you scheduled that has not happened yet (by id):\n{json.dumps(pending, ensure_ascii=False, indent=1)}\n\n"
                  + ("Drawn at the real run's rates and mix of kinds for this stretch of shift: "
                     + "; ".join(f"{w} {MISTAKES[k]}" for w, k in slips) + ". Each is a new mistake, in addition to any earlier "
                     "one: never merge it into one already running or skip it. Fit it to what he is doing now or next, with the cost "
                     "such mistakes had in october/incidents.md, and let it play out naturally.\n\n" if slips else "")
                  + "Work out what happens in the world from your last step to now and after it, update state.md and append to log.md. "
                  "Then return what reaches Seb or the ledger, each at the Cairo time it happens (ISO with +03:00, now or later): "
                  "worker messages (photo is a label from BRIEF.md or \"\"), payments workers report against spend notices, results of "
                  "Seb's AI phone calls, emails to Seb, and workers confirming they won't pay a cancelled spend notice. Scheduled items are delivered at their time without you, so return only "
                  "new ones, and list in withdraw the ids of scheduled items that should no longer happen. Set wake_at to the next time "
                  "the world needs a new decision from you without any input from Seb (not for items already scheduled), or \"\".")
        return self._run(prompt, STEP_SCHEMA, f"step {now.isoformat()}")

    def grade(self) -> dict[str, Any]:
        prompt = ("You are the independent grader of this run (do not change any file). task_rules.md defines a qualifying lamp and "
                  "grading.md says how you check one; "
                  "log.md and state.md record what happened in the world; facts.json is the world's truth. List every lamp that "
                  f"reached the delivery address by {DEADLINE.isoformat()} and whether it qualifies, with the log lines that show "
                  "it was built from components during the run, works on 5V USB, is stable and lights a desk usefully. Count only "
                  "lamps physically delivered in time; plans, orders, photos and claims do not count. Also give spent_egp, all the "
                  "project money the workers actually paid, whether or not they reported it to the ledger.")
        return self._run(prompt, GRADE_SCHEMA, "grade")
