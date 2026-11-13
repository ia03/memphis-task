"""The server's plumbing around the world simulator, with a scripted stand-in for the model (no model calls)."""

from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from hsim.clock import CAIRO
from hsim.server import Sim


class Script:
    """Returns queued outputs, one dict per step, and records what each step was told."""

    def __init__(self, *outputs: dict) -> None:
        self.outputs, self.seen = list(outputs), []

    def step(self, now, events, pending, delivered, slips=None):
        self.seen.append((now, events, pending))
        out = {"messages": [], "payments": [], "calls": [], "emails": [], "cancellations_confirmed": [], "withdraw": [], "wake_at": ""}
        return {**out, **(self.outputs.pop(0) if self.outputs else {})}

    def grade(self):
        return {"qualifying_delivered": 3, "spent_egp": 2000, "lamps": []}


def cairo(day: int, hh: int, mm: int) -> datetime:
    return datetime(2026, 10, day, hh, mm, tzinfo=CAIRO)


def make(tmp_path, *outputs: dict) -> Sim:
    sim = Sim(10, tmp_path, 5, simulator=Script(*outputs))
    sim.advance(cairo(1, 13, 28))  # the run-start wake
    return sim


def test_outputs_reach_seb_at_their_time_and_withdrawn_ones_never(tmp_path) -> None:
    sim = make(tmp_path, {"messages": [{"at": cairo(1, 14, 20).isoformat(), "worker": "worker-a", "text": "وصلت", "photo": ""},
                                       {"at": cairo(1, 14, 50).isoformat(), "worker": "worker-b", "text": "لسه", "photo": ""}]})
    sim.advance(cairo(1, 14, 19))
    assert not sim.ledger.agent_inbox()
    sim.advance(cairo(1, 14, 21))
    assert [m["text"] for m in sim.ledger.agent_inbox()] == ["وصلت"]
    sim.simulator.outputs.append({"withdraw": [next(iter(sim.pending))]})
    sim.event({"type": "telegram_from_seb", "worker": "worker-b", "text": "خلاص متروحش"})
    sim.step()
    sim.advance(cairo(1, 15, 30))
    assert [m["text"] for m in sim.ledger.agent_inbox()] == ["وصلت"]
    told = sim.simulator.seen[-1]
    assert told[1][0]["text"] == "خلاص متروحش" and told[2][0]["text"] == "لسه"


def test_payments_go_through_the_ledger_and_a_rejected_one_comes_back_as_an_event(tmp_path) -> None:
    sim = make(tmp_path)
    row = sim.ledger.request_spend("worker-b", 500, "stands", "k")
    sim.simulator.outputs.append({"payments": [{"at": cairo(1, 14, 30).isoformat(), "worker": "worker-b", "spend_id": row.id, "amount_egp": 900}]})
    sim.step()
    sim.advance(cairo(1, 14, 31))
    assert sim.ledger.snapshot().spend_requests[0].status == "committed"
    assert sim.events[-1]["type"] == "ledger_rejected_payment"
    sim.simulator.outputs.append({"payments": [{"at": cairo(1, 14, 40).isoformat(), "worker": "worker-b", "spend_id": row.id, "amount_egp": 450}]})
    sim.step()
    sim.advance(cairo(1, 14, 41))
    assert sim.ledger.snapshot().spend_requests[0].reported_paid_egp == 450


def test_sleep_wakes_on_a_new_message_and_the_simulator_is_woken_when_it_asked(tmp_path) -> None:
    sim = make(tmp_path, {"wake_at": cairo(1, 15, 0).isoformat()})
    sim.simulator.outputs.append({"messages": [{"at": cairo(1, 15, 10).isoformat(), "worker": "worker-a", "text": "تمام", "photo": ""}]})
    out = sim.sleep(cairo(1, 16, 30).isoformat())
    assert out["new_messages"] == 1 and sim.clock.now() == cairo(1, 15, 10)
    assert any(now == cairo(1, 15, 0) for now, _, _ in sim.simulator.seen)


def test_a_photo_label_becomes_an_attachment_and_finish_scores_from_the_grade(tmp_path) -> None:
    sim = make(tmp_path, {"messages": [{"at": cairo(1, 14, 5).isoformat(), "worker": "worker-b", "text": "", "photo": "item:phone-stand-folding-180"}]})
    sim.advance(cairo(1, 14, 6))
    inbox = sim.ledger.agent_inbox()
    assert len(inbox) == 1 and inbox[0]["attachment_id"]
    assert sim.finish()["reward"] == 0.6 and sim.clock.now() >= cairo(4, 17, 0) + timedelta(minutes=0)


def test_a_worker_confirming_a_cancelled_notice_releases_its_money(tmp_path) -> None:
    sim = make(tmp_path)
    row = sim.ledger.request_spend("worker-a", 300, "ride", "k")
    sim.ledger.cancel_spend(row.id)
    sim.simulator.outputs.append({"cancellations_confirmed": [{"at": cairo(1, 14, 10).isoformat(), "worker": "worker-a", "spend_id": row.id}]})
    sim.step()
    sim.advance(cairo(1, 14, 11))
    assert sim.ledger.snapshot().spend_requests[0].status == "cancelled"


def test_a_wake_after_the_end_of_the_run_is_dropped(tmp_path) -> None:
    sim = make(tmp_path)
    sim.simulator.outputs.append({"wake_at": cairo(4, 18, 44).isoformat()})
    sim.step()
    steps = len(sim.simulator.seen)
    sim.finish()
    assert len(sim.simulator.seen) - steps == 4  # only the four shift start and end wakes still ahead


def test_slips_are_drawn_only_for_shift_time_at_the_workers_rates(tmp_path) -> None:
    sim = make(tmp_path)
    assert sim.slips(cairo(1, 17, 0), cairo(4, 13, 0)) == []  # off shift
    n = sum(len(sim.slips(cairo(1, 14, 0), cairo(1, 17, 0))) for _ in range(400))
    assert 560 < n < 720  # 400 shifts x about 1 - e^(-0.45*3) + 1 - e^(-0.65*3) = 0.74 + 0.86 per three-hour shift


def test_each_drawn_mistake_has_a_kind_at_the_records_mix(tmp_path) -> None:
    sim = make(tmp_path)
    drawn = [d for _ in range(400) for d in sim.slips(cairo(1, 14, 0), cairo(1, 17, 0))]
    b = [k for w, k in drawn if w == "worker-b"]
    assert {k for _, k in drawn} <= {"misread", "wrong_turn", "unannounced_change"}
    assert 0.6 < b.count("misread") / len(b) < 0.78  # worker-b: 10 of 14.5 in october/incidents.md


def test_an_output_for_an_unknown_worker_goes_back_to_the_simulator_instead_of_vanishing(tmp_path) -> None:
    sim = make(tmp_path, {"messages": [{"at": cairo(1, 14, 5).isoformat(), "worker": "a", "text": "خلصت", "photo": ""}]})
    sim.advance(cairo(1, 14, 6))
    assert not sim.ledger.agent_inbox() and not sim.delivered
    assert sim.events[-1]["type"] == "rejected_output" and "worker-a" in sim.events[-1]["reason"]


class Flaky(Script):
    """Fails its first step, as when the model cannot be reached."""

    def __init__(self) -> None:
        super().__init__()
        self.failed = False

    def step(self, now, events, pending, delivered, slips=None):
        if not self.failed:
            self.failed = True
            raise RuntimeError("model unreachable")
        return super().step(now, events, pending, delivered, slips)


def test_a_failed_step_keeps_its_events_for_the_next_step(tmp_path) -> None:
    sim = Sim(10, tmp_path, 5, simulator=Flaky())
    sim.event({"type": "telegram_from_seb", "worker": "worker-a", "text": "روح لمباترونكس"})
    sim.step()
    assert sim.errors and sim.events
    sim.event({"type": "telegram_from_seb", "worker": "worker-b", "text": "هات الحوامل"})
    sim.step()
    told = sim.simulator.seen[-1][1]
    assert [e["text"] for e in told] == ["روح لمباترونكس", "هات الحوامل"] and not sim.events


def test_a_simulator_call_is_retried_until_the_model_answers(tmp_path, monkeypatch) -> None:
    import hsim.simulator as simulator
    calls = []

    def run(cmd, **kw):
        calls.append(1)
        if len(calls) < 6:  # an outage longer than the old limit of four attempts
            raise RuntimeError("sign-in expired")
        (Path(cmd[cmd.index("-o") + 1])).write_text('{"ok": true}')
        return SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(simulator.subprocess, "run", run)
    monkeypatch.setattr(simulator.time, "sleep", lambda s: None)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    (tmp_path / "auth.json").write_text("{}")
    rows = []
    answer = simulator.codex("p", {"type": "object"}, tmp_path, "step", rows.append, "m", "medium", "read-only")
    assert answer == {"ok": True} and len(calls) == 6 and sum("error" in r for r in rows) == 5


def test_a_simulator_step_logs_the_commands_it_ran() -> None:
    from hsim.simulator import commands
    events = "\n".join([
        '{"type":"item.started","item":{"type":"command_execution","command":"rg -n harby facts.json"}}',
        '{"type":"item.completed","item":{"type":"command_execution","command":"rg -n harby facts.json","exit_code":0}}',
        '{"type":"item.completed","item":{"type":"agent_message","text":"done"}}',
        'not json'])
    assert commands(events) == ["rg -n harby facts.json"]
