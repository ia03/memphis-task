"""Print the prompt for an independent auditor (a capable model with file access, read-only) to audit one finished trial.

Usage: python scripts/audit_prompt.py TRIAL_DIR OUT_MD [--hinted]
TRIAL_DIR is a Harbor trial folder (verifier/, artifacts/out/, agent/). The auditor writes its audit to OUT_MD and ends with a
JSON verdict. The method is the one used for every published audit (docs/AUDIT.md)."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_NOTE = """Version v12.0-rc18, frozen (no mid-round patches). Rules that are intended in this version (check they were applied, not
whether they should exist): a unit must be one object that can be moved as a whole; a structure's attach value names the
fastener someone must apply (adhesive, tape or clips they bought or have), and a structure's own holder, clamp or jaws are not
one; a worker may work alone at his own home table but does not host the other worker there (hosts_other_worker_at_home); shops next to each other are 1-2 minutes apart; each shift starts at the
facts' start_location; outputs naming an unknown worker go back to the simulator; workers may finish assembly on the landing or
street outside the client's door (the home is not a workspace); the server draws which worker makes a mistake and its kind (misread,
wrong turn, unannounced change) at the record's rates and mix, each a new one (never merged into an earlier one or skipped); the grader judges whether the A4 area is lit and usable, not an exact height; the simulator
may never use grading.md to decide what happens (only to judge and describe results); the walk from the mall to the door
takes 8-12 minutes (delivery_address in facts.json); simulator calls are retried with the clock paused; while the agent's own
model refuses requests the clock is held too; the agent's tools wait for the world without a time limit; trials in which one
simulator call took over 10 minutes were voided and run again before audit (scripts/check_trials.py); the simulator must look
up every entity a step involves in facts.json and quote the facts it applied in log.md, keep a '## Facts in play' section in
state.md copied from facts.json, and treat an entity's own facts as overriding the record's general friction rates; facts state
each shop's open days, whether a technician takes work for later days, and when a shop's in-person claim plays; each
simulator.jsonl row lists the commands the simulator ran (what it read)."""


def prompt(trial: Path, out: Path, hinted: bool, note: str = "", target: int = 9) -> str:
    hint = (f"Hinted: the agent also saw {ROOT / 'world/hint_note_v3.md'}." if hinted
            else "Unhinted: the agent saw only the task rules.")
    return f"""Audit one finished trial of the Memphis task. Read-only: edit nothing except your output file.

The evaluated agent ("Seb") manages two hired workers in Cairo over chat to get desk lamps built from components and delivered
(7,000 EGP; shifts Thu 1 Oct 14:00-17:00 and Sun 4 Oct 13:00-17:00 Cairo). Score = qualifying lamps delivered by Sun 17:00,
divided by {target}. One model simulates the whole world: both workers, every shop, the city and time. The code only keeps the
clock, the money ledger and the agent's API. A separate model call grades the run at the end.

Trial folder: {trial}
- artifacts/out/world/: the simulator's folder exactly as it ran: BRIEF.md (its instructions), task_rules.md, grading.md,
  facts.json (this seed's world truth), october/ (the real record it used as behaviour reference: chats, worker profiles,
  incident rates), state.md and log.md (its memory and narrative).
- artifacts/out/simulator.jsonl: every simulator step (prompt with Seb's events, answer with timed outputs) and the grade call.
  The step prompts say when the server drew a worker mistake (a "slip" there; rates in world/workers.yaml, from
  october/incidents.md). Write "worker mistake", not "slip".
- verifier/score.json and verifier/export.json: score, grade with per-lamp evidence, ledger, emails, calls, API calls.
- agent/codex-part*.txt then agent/codex.txt: the agent's transcript (what Seb saw and decided).
{hint}

{VERSION_NOTE}{(' ' + note) if note else ''}

Question: is the score a fair measurement of the agent? Find every place where the simulator or grader, rather than the agent,
changed what happened, in both directions. Classify each finding:
- E (easier than reality): anything beyond facts.json (item, price, stock, service, favour, referral, timing, capacity), a worker
  knowing or doing what he was not told or could not know, initiative beyond the real workers (compare october/), lucky timing,
  a drawn worker mistake played at no cost where it should have cost something.
- H (harder than reality): a shop omitting or refusing what its facts allow, a worker failing a clear instruction a real one
  would follow, invented obstacles or delays beyond the facts, worker mistakes stacked or made decisive more often than the record implies.
- I (inconsistency or plumbing): state.md vs log.md contradictions, double or lost deliveries, money not matching the ledger.
- V (visibility): something decisive that Seb could not see.
- G (grading): a lamp counted or not counted against the evidence and grading.md.
Check numbers against facts.json. Do not report the agent's own decisions as simulator problems; variation a real person would
also show is not a defect.

Method: 1) timeline of decisive decisions and events (Thursday, Sunday) with log times; 2) for each lamp short of {target} (or each
counted lamp), its cause; 3) judge each counted unit against grading.md yourself; 4) the range of lamp counts a fair world could
have given, with every E/H/G finding removed, using Seb's own later messages, and your best single estimate; 5) findings list (class, log time and quote, facts
field or record id, lamp effect, probability it changed the count).

Write the audit to {out} in plain English with short sentences: a header with the score and spend, a "Verdict" section first,
then the sections above. End the file with a JSON block, and make your final message only that block:
{{"trial", "lamps", "fair": "yes|mostly|partly|no", "fair_lamp_range": [lo, hi], "expected_fair_lamps", "count_changing_defects": [...],
"plausible_count_changing": [...], "new_defects": [...]}}, each defect with "class", "summary" and "severity".
"fair" is "yes" when nothing outside the agent's control changed the count, "mostly" when a named doubt could move one lamp."""


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("trial", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--hinted", action="store_true")
    p.add_argument("--note", default="", help="one trial-specific sentence for the auditor")
    a = p.parse_args()
    print(prompt(a.trial.resolve(), a.out.resolve(), a.hinted, a.note))
