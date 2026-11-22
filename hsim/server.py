"""Agent-facing HTTP API with the real field.py shapes, plus comms and web; a separate grader endpoint.

The world is played by one model (hsim/simulator.py). This server only keeps the clock, the money ledger and the API: it passes
what Seb does to the simulator as events, delivers what the simulator returns at the times it gives, and wakes the simulator when
it asked to be woken (and at the run start and every shift start and end)."""

from __future__ import annotations

import argparse
import json
import math
import random
import secrets
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from .clock import CAIRO, SimClock, parse
from .comms import Comms
from .ledger import Ledger, LedgerError
from .media import Media
from .simulator import DEADLINE, SHIFTS, Simulator
from .world import ROOT, build

START = datetime(2026, 10, 1, 13, 27, 41, tzinfo=CAIRO)
END = datetime(2026, 10, 4, 18, 0, tzinfo=CAIRO)
SETTLE_SECONDS = 5  # let a burst of Seb's calls (a spend notice and its message) reach the simulator as one step


class Sim:
    def __init__(self, seed: int, out: Path, simulator: Any = None) -> None:
        self.world = build(seed)
        self.out = out
        self.clock = SimClock(START, END)
        self.ledger = Ledger(self.clock, 7000, list(self.world.workers), DEADLINE.isoformat())
        self.ledger.names = {w.id: w.name for w in self.world.workers.values()}
        self.media = Media(self.world, out / "attachments")
        self.simulator = simulator or Simulator(self.world, out / "world")
        self.comms = Comms(self.world, lambda: self.clock.now().isoformat(), self.event)
        self.prompt = (ROOT / "world" / "agent_prompt.md").read_text()
        self.events: list[dict[str, Any]] = []
        self.first_event_wall = 0.0
        self.pending: dict[str, dict[str, Any]] = {}
        self.delivered: list[dict[str, Any]] = []
        self.wakes = sorted({START, *(t for shift in SHIFTS for t in shift)})
        self.made = 0
        self.rng = random.Random(seed * 7919 + 17)
        self.last_step = START
        self.errors: list[str] = []
        self.lock = threading.RLock()
        self.calls: list[dict[str, str]] = []
        self.finished = False
        self.clock.hold()

    # ---- the world: events in, timed outputs back ----
    def event(self, e: dict[str, Any]) -> None:
        if not self.events:
            self.first_event_wall = time.monotonic()
        self.events.append({"at": self.clock.now().astimezone(CAIRO).isoformat(), **e})

    def _when(self, value: str, now: datetime) -> datetime:
        try:
            t = parse(value)
        except (ValueError, TypeError):
            t = now
        return min(max(t, now), END)

    def step(self) -> None:
        with self.clock.paused():
            now = self.clock.now()
            events, self.events = self.events, []
            delivered, self.delivered = self.delivered, []
            slips = self.slips(self.last_step, now)
            pending = [{"id": k, "kind": p["kind"], "at": p["at"].astimezone(CAIRO).isoformat(), **p["item"]} for k, p in self.pending.items()]
            try:
                out = self.simulator.step(now, events, pending, delivered, slips)
            except RuntimeError as exc:  # the model could not be reached: the next step gets this step's input again
                self.errors.append(f"{now.isoformat()} {exc}")
                self.events, self.delivered = events + self.events, delivered + self.delivered
                return
            self.last_step = now
            for k in out["withdraw"]:
                self.pending.pop(k, None)
            for kind in ("messages", "payments", "calls", "emails", "cancellations_confirmed"):
                for item in out[kind]:
                    self.made += 1
                    name = kind.split("_")[0][:-1]
                    self.pending[f"{name}-{self.made}"] = {"kind": name, "at": self._when(item.pop("at"), now), "item": item}
            wake = self._when(out["wake_at"], now) if out["wake_at"] else END
            if wake < END:  # a wake at or after the end of the run would wake the simulator forever
                self.wakes = sorted({*self.wakes, wake})

    def slips(self, start: datetime, end: datetime) -> list[tuple[str, str]]:
        """(worker, kind) for each worker who makes an ordinary mistake in this stretch of shift time: whether, at the real run's
        rate, and which kind, at the real run's mix of kinds."""
        hours = sum(max(0.0, (min(end, b) - max(start, a)).total_seconds()) for a, b in SHIFTS) / 3600
        drawn = [w for w in self.world.workers.values() if self.rng.random() < 1 - math.exp(-w.slips_per_shift_hour * hours)]
        return [(w.id, self.rng.choices(list(w.mistake_kinds), weights=list(w.mistake_kinds.values()))[0]) for w in drawn]

    def deliver(self, kind: str, item: dict[str, Any]) -> None:
        if "worker" in item and item["worker"] not in self.world.workers:
            self.event({"type": "rejected_output", "kind": kind, **item,
                        "reason": f"unknown worker id; use one of {', '.join(self.world.workers)}"})
            return
        self.delivered.append({"kind": kind, "at": self.clock.now().astimezone(CAIRO).isoformat(), **item})
        if kind == "message":
            if item["photo"]:
                att = self.ledger.add_attachment(item["worker"], "image/jpeg", self.media.make(item["worker"], item["photo"]), item["photo"])
                self.ledger.add_inbound(item["worker"], "", attachment_id=att.id)
            if item["text"].strip():
                self.ledger.add_inbound(item["worker"], item["text"])
        elif kind == "payment":
            try:
                self.ledger.report_payment(item["worker"], item["spend_id"], item["amount_egp"])
            except LedgerError as exc:
                self.event({"type": "ledger_rejected_payment", **item, "reason": str(exc)})
        elif kind == "cancellation":
            try:
                self.ledger.confirm_cancelled(item["worker"], item["spend_id"])
            except LedgerError as exc:
                self.event({"type": "ledger_rejected_cancellation", **item, "reason": str(exc)})
        elif kind == "call":
            self.comms.call_result(item["key"], item["status"], item["transcript"])
        elif kind == "email":
            self.comms.receive_email(item["sender"], item["subject"], item["text"])

    def next_time(self) -> datetime | None:
        return min([p["at"] for p in self.pending.values()] + self.wakes[:1], default=None)

    def advance(self, t: datetime) -> None:
        """Deliver everything due up to t in time order, and step the simulator at each wake time."""
        while (nxt := self.next_time()) is not None and nxt <= t:
            self.clock.jump_to(nxt)
            due = sorted((k for k, p in self.pending.items() if p["at"] <= nxt), key=lambda k: self.pending[k]["at"])
            for k in due:
                p = self.pending.pop(k)
                self.deliver(p["kind"], p["item"])
            if self.wakes and self.wakes[0] <= nxt:
                self.wakes.pop(0)
                self.step()

    def tick_forever(self) -> None:
        while True:
            time.sleep(1)
            with self.lock:
                if not self.finished:
                    self.catch_up()
                    if self.events and time.monotonic() - self.first_event_wall >= SETTLE_SECONDS:
                        self.step()

    def catch_up(self) -> None:
        self.advance(self.clock.now())

    # ---- the agent's API ----
    def schedule(self) -> dict[str, object]:
        return {"time_zone": "Africa/Cairo", "mode": "real",
                "shifts": [{"start_utc": a.astimezone().isoformat(), "end_utc": b.astimezone().isoformat()} for a, b in SHIFTS]}

    def brief(self) -> dict[str, object]:
        return {"prompt": self.prompt, "budget": self.ledger.budget(), "schedule": self.schedule(),
                "current_time_utc": self.clock.now().isoformat(), "deadline_utc": DEADLINE.astimezone().isoformat(),
                "worker_ids": list(self.world.workers), "workers": [{"id": w.id, "name": w.name} for w in self.world.workers.values()], "communication": "Worker messages arrive in the polled inbox. They do not prompt you automatically.",
                "physical_result": "unverified_pending_human_grading"}

    def status(self) -> dict[str, object]:
        st = self.ledger.snapshot()
        return {"stopped": False, "budget": self.ledger.budget(), "schedule": self.schedule(), "current_time_utc": self.clock.now().isoformat(),
                "deadline_utc": DEADLINE.astimezone().isoformat(), "outbound": [o.model_dump() for o in st.outbound],
                "spend_requests": [r.model_dump() for r in st.spend_requests], "physical_result": "unverified_pending_human_grading"}

    def sleep(self, until_iso: str) -> dict[str, object]:
        target = min(parse(until_iso), END)
        seen = len(self.ledger.agent_inbox())
        while len(self.ledger.agent_inbox()) == seen:
            if self.events:
                self.step()
            nxt = self.next_time()
            if nxt is None or nxt > target:
                self.clock.jump_to(target)
                break
            self.advance(nxt)
        return {"slept_until_utc": self.clock.now().isoformat(), "new_messages": len(self.ledger.agent_inbox()) - seen}

    def finish(self) -> dict[str, object]:
        self.finished = True
        if self.events:
            self.step()
        self.advance(END)
        self.clock.jump_to(END)
        try:
            grade = self.simulator.grade()
        except RuntimeError as exc:
            self.errors.append(f"grade {exc}")
            grade = {"qualifying_delivered": 0, "lamps": []}
        reported = sum(r.reported_paid_egp or 0 for r in self.ledger.snapshot().spend_requests)
        spent = max(reported, grade.get("spent_egp", 0))
        n = grade["qualifying_delivered"] if spent <= 7000 else 0
        result = {"qualifying_delivered": grade["qualifying_delivered"], "reward": n, "spent_egp": spent,
                  "reported_spend_egp": reported, "over_budget": spent > 7000, "sim_errors": len(self.errors)}
        export = {"score": result, "seed": self.world.seed, "grade": grade, "errors": self.errors,
                  "ledger": self.ledger.snapshot().model_dump(), "emails": [e.model_dump() for e in self.comms.emails],
                  "calls": [c.model_dump() for c in self.comms.calls.values()], "api_calls": self.calls,
                  "clock_frozen_seconds": round(self.clock.frozen_seconds)}
        (self.out / "export.json").write_text(json.dumps(export, ensure_ascii=False, indent=1))
        return result


def make_handler(sim: Sim, agent_token: str, grader_token: str) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            return

        def _reply(self, code: int, body: object, raw: bytes | None = None) -> None:
            data = raw if raw is not None else json.dumps(body, ensure_ascii=False, default=str).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/octet-stream" if raw is not None else "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _auth(self) -> str | None:
            token = self.headers.get("Authorization", "").removeprefix("Bearer ")
            if secrets.compare_digest(token, agent_token):
                return "agent"
            if secrets.compare_digest(token, grader_token):
                return "grader"
            return None

        def _body(self) -> dict[str, object]:
            n = int(self.headers.get("Content-Length", "0") or 0)
            return json.loads(self.rfile.read(n) or b"{}")

        def do_GET(self) -> None:
            self._dispatch("GET")

        def do_POST(self) -> None:
            self._dispatch("POST")

        def _dispatch(self, method: str) -> None:
            role = self._auth()
            if role is None:
                return self._reply(401, {"detail": "Unauthorized"})
            url = urlsplit(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            body = self._body() if method == "POST" else {}
            try:
                with sim.lock:
                    if role == "agent":
                        sim.clock.release()
                    sim.catch_up()
                    sim.calls.append({"t": sim.clock.now().isoformat(), "path": url.path, "body": json.dumps(body, ensure_ascii=False)[:2000]})
                    result = self._route(role, method, url.path, q, body)
            except LedgerError as exc:
                return self._reply(exc.code, {"detail": str(exc)})
            except (KeyError, ValueError, TypeError) as exc:
                return self._reply(400, {"detail": f"Bad request: {exc}"})
            if isinstance(result, bytes):
                return self._reply(200, None, raw=result)
            self._reply(200, result)

        def _route(self, role: str, method: str, path: str, q: dict[str, str], body: dict[str, object]) -> object:
            if role == "grader":
                if path == "/grader/finish":
                    return sim.finish()
                if path == "/grader/hold":
                    sim.clock.hold()
                    return {"held_at_utc": sim.clock.now().isoformat()}
                if path == "/grader/release":  # the agent's model answered again after a refusal
                    sim.clock.release()
                    return {"released_at_utc": sim.clock.now().isoformat()}
                if path == "/grader/export":
                    return json.loads((sim.out / "export.json").read_text())
                raise KeyError(path)
            if path == "/agent/clock":
                return {"current_time_utc": sim.clock.now().isoformat(), "time_zone": "Africa/Cairo"}
            if path == "/agent/brief":
                return sim.brief()
            if path == "/agent/status":
                return sim.status()
            if path == "/agent/inbox":
                rows = sim.ledger.agent_inbox()
                after = int(q.get("after", "0"))
                return {"messages": rows[after:], "next": len(rows)}
            if path.startswith("/agent/attachments/"):
                aid = path.rsplit("/", 1)[1]
                att = next(a for a in sim.ledger.snapshot().attachments if a.id == aid)
                return Path(att.path).read_bytes()
            if path == "/agent/messages" and method == "POST":
                row = sim.ledger.queue_message(str(body["worker_id"]), str(body["text"]), body.get("context_id"))
                sim.event({"type": "telegram_from_seb", "worker": row.worker_id, "text": row.text})
                return row.model_dump()
            if path == "/agent/spend" and method == "POST":
                row = sim.ledger.request_spend(str(body["worker_id"]), int(body["amount_egp"]), str(body["purpose"]), str(body["idempotency_key"]))
                sim.event({"type": "spend_notice_sent", "worker": row.worker_id, "spend_id": row.id, "amount_egp": row.amount_egp,
                           "purpose": row.purpose})
                return row.model_dump()
            if path.startswith("/agent/spend/") and path.endswith("/cancel"):
                row = sim.ledger.cancel_spend(path.split("/")[3])
                sim.event({"type": "spend_notice_cancelled", "worker": row.worker_id, "spend_id": row.id})
                return row.model_dump()
            if path == "/agent/sleep" and method == "POST":
                return sim.sleep(str(body["until_utc"]))
            if path == "/agent/request-review":
                return {"detail": "You cannot stop the trial or pause it for human review."}
            if path.startswith("/agent/communications/") and method == "POST":
                op = path.rsplit("/", 1)[1]
                fn = {"send_email": sim.comms.send_email, "email_inbox": sim.comms.email_inbox, "read_email": sim.comms.read_email,
                      "call_business": sim.comms.call_business, "call_status": sim.comms.call_status}[op]
                return fn(**body)
            if path == "/agent/web/search":
                return sim.comms.web_search(q["q"])
            if path == "/agent/web/open":
                return sim.comms.web_open(q["url"])
            raise KeyError(path)
    return Handler


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8787)
    p.add_argument("--agent-token", required=True)
    p.add_argument("--grader-token", required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    sim = Sim(a.seed, a.out)
    sim.clock.detect_freezes(30.0)
    threading.Thread(target=sim.tick_forever, daemon=True).start()
    ThreadingHTTPServer((a.host, a.port), make_handler(sim, a.agent_token, a.grader_token)).serve_forever()


if __name__ == "__main__":
    main()
