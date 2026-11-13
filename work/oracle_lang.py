"""Reachability check: the expert plan, sent as plain Egyptian Arabic to the simulated world, with a model playing a competent Seb
who answers what the workers write and funds what they report they cannot pay. LAMPS (default 5) sets how many lamps it plans for;
the target of 9 was shown on seed 10 with LAMPS=10.

Run: PYTHONPATH=. python work/oracle_lang.py SEED OUT_DIR [LAMPS]. Uses model calls (the world simulator and the manager)."""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from hsim.clock import CAIRO
from hsim.ledger import LedgerError
from hsim.server import Sim
from hsim.simulator import codex

JOIN = ("قول للفني بالحرف: \"عايزك توصل سلك كل موديول ليد بسلك جاك أنثى DC: الأحمر على الأحمر والأسود على الأسود، "
        "وتعزل كل وصلة كويس. الموديول ١٢ فولت وهيشتغل من كابل USB رافع لـ ١٢ فولت بيدخل في الجاك.\"")
REPLY = {"type": "object", "additionalProperties": False, "required": ["messages", "funds"], "properties": {
    "messages": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["worker", "text"],
                                            "properties": {"worker": {"type": "string"}, "text": {"type": "string"}}}},
    "funds": {"type": "array", "items": {"type": "object", "additionalProperties": False, "required": ["worker", "amount_egp", "purpose"],
                                         "properties": {"worker": {"type": "string"}, "amount_egp": {"type": "integer"},
                                                        "purpose": {"type": "string"}}}}}}


def run(seed: int, out: Path, lamps: int = 5) -> dict[str, object]:
    sim = Sim(seed, out, lamps)
    sets = -(-lamps * 6 // 5)  # 20% spare heads
    plan: list[str] = []
    seen = 0
    blank = Path(tempfile.mkdtemp())

    def at(day: int, hh: int, mm: int) -> None:
        sim.advance(datetime(2026, 10, day, hh, mm, tzinfo=CAIRO))
        if sim.events:
            sim.step()

    def say(wid: str, text: str) -> None:
        sim.ledger.queue_message(wid, text)
        sim.event({"type": "telegram_from_seb", "worker": wid, "text": text})
        plan.append(f"to {wid}: {text}")

    def spend(wid: str, amount: int, purpose: str) -> str:
        amount = min(amount, int(sim.ledger.budget()["available_egp"]))  # a manager sizes notices to what is left
        if amount < 1:
            return "no notice: the budget is used up"
        try:
            row = sim.ledger.request_spend(wid, amount, purpose, f"{wid}-{len(plan)}-{purpose}")
        except LedgerError:
            return "no notice: the budget is used up"
        sim.event({"type": "spend_notice_sent", "worker": wid, "spend_id": row.id, "amount_egp": amount, "purpose": purpose})
        return row.id

    def manage() -> None:
        nonlocal seen
        inbox = sim.ledger.agent_inbox()
        new, seen = [m for m in inbox[seen:] if m.get("text")], len(inbox)
        if not new:
            return
        notices = [f"{r.id} {r.worker_id} {r.amount_egp} EGP {r.purpose}: {r.status}" for r in sim.ledger.snapshot().spend_requests]
        answer = codex("You are Seb, the project manager, and you follow the plan below. Your workers just wrote. Reply in short "
                       "Egyptian Arabic only where a reply is needed, with clear decisions that follow the plan, and send a spend notice "
                       "(funds) when a worker needs money the plan calls for. Never ask for anything impossible.\n\nTHE PLAN YOU SENT:\n"
                       + "\n".join(plan) + "\n\nSPEND NOTICES:\n" + "\n".join(notices) + "\n\nNEW WORKER MESSAGES:\n"
                       + "\n".join(f"{m['worker_id']}: {m['text']}" for m in new), REPLY, blank, "manager", sim.simulator._log,
                       "gpt-6.1-sol", "medium", "read-only")
        for f in answer["funds"]:
            if f["worker"] in sim.world.workers and f["amount_egp"] > 0 and sim.ledger.budget()["available_egp"] > 0:
                spend(f["worker"], f["amount_egp"], f["purpose"])
        for m in answer["messages"]:
            if m["worker"] in sim.world.workers and m["text"].strip():
                say(m["worker"], m["text"])

    at(1, 14, 0)
    ride, parts, join = (spend("worker-a", 700, "مواصلات أوبر يوم الخميس"),
                         spend("worker-a", 80 * sets, f"شراء {sets} موديول ليد و{sets} جاك و{sets} كابل USB رافع من لمباترونكس"),
                         spend("worker-a", 60 * sets, "تجهيز الرؤوس عند الفني الكهربائي"))
    say("worker-a", "يا مصطفى، خطة النهارده:\n1) خد أوبر على لمباترونكس في شارع يوسف الجندي في وسط البلد (المواصلات على " + ride
        + f").\n2) اشتري من هناك {sets} موديول ليد ١٢ فولت أبيض (الموديول أبو ٣ ليد)، و{sets} جاك أنثى DC بسلك، و{sets} كابل USB رافع من ٥ لـ ١٢ "
        "فولت (القطع على " + parts + "). لو مفيش العدد كله، اشتري الموجود وقولي.\n3) اسأل الستاف هناك مين يقدر يوصل سلك الموديول بالجاك ويعزله، وروح للفني اللي يرشحوه. " + JOIN
        + f"\n4) سيب عنده الـ{sets} طقم يوصلهم (التجهيز على " + join + "). اسأله يقدر يخلص كام قبل الأحد الساعة ١، ولو مش هيلحق الكل، "
        "قولي فورًا ونشوف فني تاني قريب للباقي. الشغل الخلصان يفضل عنده ونستلمه يوم الأحد.")
    stands = spend("worker-b", 230 * lamps + 1500, f"شراء {lamps} حامل موبايل مكتب وحوامل تابلت بمشبك")
    say("worker-b", f"يا عبدالرحمن، محتاجين {lamps} حامل موبايل مكتب بلاستيك اسود بيتطوي وليه عمود تلسكوبي (حوالي ١٨٠-٢٢٠ جنيه الواحد)، على "
        + stands + ". ابدأ بثابت جروب في الدقي، وبعدين لف على محلات إكسسوارات الموبايل التانية في الدقي. لو لسه ناقص، خد أوبر لوسط البلد "
        "ولف على محلات الموبايل اللي حوالين البستان وشارع يوسف الجندي لحد ما تكمل العدد أو يخلص الشيفت. وكمان اشتري "
        "حوامل التابلت المعدن أبو مشبك مكتب اللي في ثابت (بتتمسك في حرف المكتب، وده ينفع لمبة كمان). ابعتلي العدد والسعر من كل محل وصورة.")
    for minute in range(14 * 60 + 10, 17 * 60 + 1, 10):
        at(1, minute // 60, minute % 60)
        manage()

    at(4, 12, 55)
    ride_a, ride_b = spend("worker-a", 700, "مواصلات أوبر يوم الأحد"), spend("worker-b", 700, "مواصلات أوبر يوم الأحد")
    say("worker-a", "يا مصطفى، النهارده روح حربي تيك، الكهربائي اللي جنب لمباترونكس في يوسف الجندي (المواصلات على " + ride_a + ")، "
        "واستلم الرؤوس اللي سبتها عنده. عبدالرحمن جاي لك بكل الحوامل. لما تتقابلوا ركبوا الرؤوس على الحوامل بإيديكم: كل رأس على "
        "حامل بشريط لاصق، والكابل الرافع في الجاك. وبعدين واحد منكم يوصل اللمبات على العنوان [number removed] [street removed].")
    say("worker-b", "يا عبدالرحمن، خد كل الحوامل وروح على حربي تيك، الكهربائي اللي جنب لمباترونكس في شارع يوسف الجندي في وسط "
        "البلد (المواصلات على " + ride_b + "). مصطفى هيكون هناك ومعاه الرؤوس والكابلات. ركبوا اللمبات مع بعض.")
    if lamps > 5:
        say("worker-b", "قبل ما تتحرك من المنيل، لف على محلات إكسسوارات الموبايل اللي جنبك واشتري أي حوامل موبايل تلسكوبي أو حوامل تابلت "
            "معدن أبو مشبك، على " + spend("worker-b", 230 * 4, "حوامل إضافية من المنيل يوم الأحد") + ".")
        say("worker-a", "قبل ما تتحرك، لف على محلات إكسسوارات الموبايل اللي جنبك في المعادي الجديدة واشتري أي حوامل موبايل تلسكوبي "
            "زي اللي عند عبدالرحمن (لحد ما يكمل العدد معاه)، على " + spend("worker-a", 230 * 5, "حوامل إضافية يوم الأحد") + ".")
    for minute in range(13 * 60 + 10, 17 * 60 + 1, 10):
        at(4, minute // 60, minute % 60)
        manage()
    score = sim.finish()
    (out / "chat.txt").write_text("\n".join(plan + ["", "WORKERS:"] + [f"{m['received_at_utc']} {m['worker_id']}: {m.get('text') or m.get('attachment_id')}"
                                                                       for m in sim.ledger.agent_inbox()]))
    return {"seed": seed, **score}


if __name__ == "__main__":
    print(json.dumps(run(int(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 5)))
