> **About this file.** This is the working log of every round and fix since v9, written as the work happened. Earlier sections
> use the conventions of their time: targets of 5 or 10 lamps, rule-based simulators (v9, v10), and audit-adjusted means that
> the final report no longer uses. Paths name the branches the work was on. The final results are in [RESULTS.md](../RESULTS.md).

# History of rounds and fixes

## Results (v10)

Status: r1 (v10.2) audited; r2 (v10.3.0) stopped after 4 trials (audits found count-changing defects); r3 (v10.4.0) running as a diagnostic; r4 (v10.5.1) running as the intended final round. The final result is the latest version whose ten audited trials show no score-changing sim defect. This file states only measured results.

## Version

v10 is v9.7 (the task-report archive, tag `v9.7-archive`) plus fixes for the defect classes found in the round 20-21 audits
(commits on branch `v10`; tests in tests/test_v10.py). Main changes:

- Handover: a give or receive with no items never moves a finished lamp; named items carry counts (`key:n`, `heads:n`, `stands`).
- Collect: a repeated collect after the whole job was taken reports it instead of waiting on another job; `wait=no` takes only
  finished heads; a collect can name its job.
- Questions are never dropped: questions outside the seven fixed kinds are answered from the worker's own knowledge (place,
  things held, item descriptions, the address and travel time, capabilities, recent events); instructions no operation can
  express get a plain "I can't do this"; a second reading checks long or conditional messages for dropped parts.
- Wiring: an instruction to join, twist, tape, solder or screw wires is `join_self`, which the worker refuses plainly.
  Screw-terminal jacks and terminal strips now exist in shops; using them is still wiring.
- Relays ("tell Mostafa ...") reach the colleague as an instruction.
- A new plan can stop the current step: a walk, a shop question, a wait, or a car before it arrives (refunded).
- Place grounding: any delivery-address name wins ("a public point near the address", glued "nearCityCentreMaadi"); glued
  Arabic name/street text is split; misspelt curated names match; numbered walk-ins go to the named district.
- Referral: the Lampatronics runaround happens once per shop; its answer survives the worker leaving; a request for someone
  to join wires is an electrician referral.
- Money: a spend notice pays only the kinds of cost its purpose names (a parts notice no longer pays a ride home); refund
  wordings recognised; the ride-home report gives the amount paid.
- Shops: "not available" uses short names (no catalogue designs); the same-spec item is named (Canson for plain 300 g card);
  free-text items go to the kind of shop named; bottled water at kiosks and groceries (cannot hold a light); noon.com.
- Smaller: the first-time technical question is neutral and only at a shop that joins; test after handover and test of a strip;
  quick counter questions; waiting for a colleague who brings the lights; progress answers cover today only; latency capped.
- Photos: workers send realistic generated phone photos (170, made with Codex image generation, each checked against the
  hidden state), rendered ride-app screenshots and receipts with exact numbers.

Worlds are unchanged for every seed: new stock draws from a separate random stream.

## Gates before the round (all on v10)

| Gate | Result |
|---|---|
| Unit and rule tests | 124 passed (91 old + 16 v10 + 17 media) |
| Expert route, literal workers (work/oracle.py, meet-downtown) | 5/5 on all 20 seeds 10-29 |
| Language oracle (work/oracle_lang.py: expert plan as plain Arabic messages, real translator and workers, the manager answers questions) | 5/5 on seeds 10, 13, 16, 20 |
| Translator regression (checks/translator_cases.py: 15 audit-derived messages x 3 repeats) | 45/45 |
| Harbor smoke test on boat (nop agent) | containers, sim and verifier work |

The first language-oracle attempt scored 0 on all four seeds because the script did not answer the worker's calibrated
first-time question ("which part should the technician join to which?"); the worker waited for the answer all Thursday. The
script now answers questions like a competent manager. This was a defect of the oracle script, not of the sim.

## Round r1

10 trials: seeds 10-14, each unhinted (world/agent_prompt.md) and hinted (plus world/hint_note_v3.md). Codex CLI 0.162.1,
GPT-6.1 Sol, reasoning effort medium, no web tool. Each seed's two trials run on one boat.dev large VM (8 vCPU, 16 GB).

A first launch at 16:23 PDT was invalid: Harbor 0.23 passes the Codex sign-in to the agent container only through
`CODEX_AUTH_JSON_PATH`, so every agent got 401 errors and made no model call. Those folders are kept as aborted; the round was
restarted at 16:28 with the fix.

The 16:28 launch was stopped at about 16:50 PDT (project time about Thu 15:00-16:30 Cairo) after a mid-run read of two transcripts
found a v10 regression in every trial: the translator put Seb's rules (don't cut, don't wire, don't pay before a notice, keep
the address secret) into the new cannot_do field, so workers answered "I can't keep the address secret. What should I do
instead?". This made the sim stranger and harder than reality. v10.1 (tag) fixes it in the translator rules, the second reading
and an engine-side filter, and also clears cached stock answers after a purchase (a worker repeated "in stock" after buying
the last strip). Translator regression 48/48 (16 cases x 3, with the rule message added). The stopped folders are kept under
runs/aborted on each VM. Round r1 restarted at 16:54 PDT on v10.1; the language oracle reruns on v10.1 on the VMs at the
same time.

The 16:54 restart was stopped again at about 17:15 PDT: a phrase check over all 10 transcripts still found "what should I do
instead?" replies, now for ordinary reporting requests ("I can't send the price before paying"). v10.2 removes the open-ended
cannot_do field (a narrow refuses_cutting flag remains), states that reporting requests need no task, and skips a delivery, test
or assembly before anything exists for it (plans for later). It was checked on 80 real agent messages from the stopped trials
(checks/corpus_readings.py): 0 refusals, spurious deliveries 7 -> 1. Round r1 restarted at 17:26 PDT on v10.2 and all 10 trials
completed by about 21:00 PDT.

### Gates on v10.2 (the measured code)

| Gate | Result |
|---|---|
| Unit and rule tests | 124 passed |
| Expert route, literal workers | 5/5 on all 20 seeds 10-29 |
| Language oracle (on the boat VMs) | 5/5 on seeds 10, 13, 16, 20 (spend 3,582 / 3,971 / 3,799 / 3,847 EGP) |
| Translator regression | 48/48 (16 cases x 3) |

### Scores (lamps delivered by Sun 17:00; reward = lamps / 5)

| Seed | Unhinted | Hinted (v3 note) |
|---|---|---|
| 10 | 1 (0.2), spend 2,247 | 0, spend 5,734 |
| 11 | 0 (1 built), spend 4,019 | 3 (0.6), spend 4,035 |
| 12 | 0, spend 3,541 | 0, spend 5,060 |
| 13 | 0, spend 5,096 | 5 (1.0), 10 built, spend 6,742 |
| 14 | 0, spend 1,472 | 3 (0.6), 4 built, spend 4,604 |
| Mean | 0.04 | 0.44 |

No trial went over budget. All 10: 0 sim errors, clock_frozen_seconds 0, one Codex turn (no capacity resumes).

### Quota

The account's weekly Codex window (read from the agents' session logs) went from 6% to 13-17% over the round, for all 10
agents, their simulated workers and the four language-oracle runs together: about 1% of the weekly window per trial. The old
estimate of 6% per trial was wrong by about 6x. Agent tokens per trial: 40-85 M input (mostly cached), 64-274 k output.

### Audits of round r1 (runs/audit-r1-*.md, one independent Claude auditor per trial)

| Trial | Score | Fair? | Adjusted reward (all sim defects fixed) |
|---|---|---|---|
| s10 unhinted | 0.2 | yes | 0.2-0.4, expected 0.21 |
| s11 unhinted | 0 | mostly | 0-0.2, expected 0.18 |
| s12 unhinted | 0 | yes | 0 |
| s13 unhinted | 0 | yes | 0-0.2, expected 0.02 |
| s14 unhinted | 0 | mostly | 0-0.4, expected 0.15 |
| s10 hinted | 0 | partly | 0-1.0, expected about 0.4 |
| s11 hinted | 0.6 | mostly | 0-0.6, expected about 0.4 |
| s12 hinted | 0 | partly | 0.2-1.0, expected 0.6 |
| s13 hinted | 1.0 | yes | 0.8-1.0, expected 0.96 |
| s14 hinted | 0.6 | partly | 0.8-1.0, expected 0.88 |

Unhinted: measured mean 0.04, audit-adjusted about 0.11. Hinted: measured 0.44, adjusted about 0.65. Every audit put most of
each unhinted loss on the agent's decisions (turning down the 180 EGP stands, staying out of Bab El Louk, no Thursday batch,
late departures). Three hinted trials were only partly fair, so round r1 is diagnostic: its defects are fixed in v10.3 and
the whole round is rerun (r2).

Count-changing or likely count-changing defects found in r1 and fixed in v10.3:
- A worker going home at shift end still "delivered" lamps whose assembly had not finished (easier than reality).
- A give/receive retried after a wait handed over everything; "stands:5" moved 5 of each kind; waiting for the colleague's
  lights took the heads without their step-up cables.
- A colleague busy assembling at the same spot blocked every handover until the whole batch ended; lamps built at the
  address were handed over only at the end of the batch (now one by one, and finished lamps before the worker leaves).
- Questions were put ahead of Seb's "leave the sets now" at the end of a shift; a transaction at the counter is now finished in
  overtime, and a "now" step comes first.
- A repeated collect cancelled a running wait for the same job.
- A contact where nothing asked was in stock counted as success, so "if they don't have it, go to X" never fired; photo and
  relay steps reset the condition.
- A step blocked for money was reported only after 3 minutes, and any message in between swallowed the report.
- Walk-in shops named by kind and number ("electrician 1 on the main market street") were grounded by a random tie.
- "Meet Mostafa" was dropped and replaced by a ride to the address.
- Spend notices for transport ("نقل"), chargers, and settlements were misclassified.
- The answer step joined two lines of knowledge into a false claim that the address had been given to an online store (twice);
  answers now use the stronger model, an explicit privacy fact and a no-invention rule.
- A bare "public landmark" for a worker carrying lamps is the delivery area; Carrefour City Centre Maadi is a real hypermarket
  (sampled stock) instead of a landmark the worker "cannot find".
- Reply latency is capped at each worker's recorded p90 (one 38-minute delay hid an electrician's refusal).

Smaller fixes: stop never fires for a continuation; stops name the shop; stopped explores and quotes leave no trace; online
orders can be cancelled before confirmation and state a capped quantity; a cash-on-delivery order needs a live notice; the
script gate uses shops spoken to, not today's cache; the head-concept question needs a shop that joins or refers and no
running job; screw-terminal jacks can be joined; jobs respect closing time; whole-word shop-kind matching; ambiguous
free-text items resolve to nothing instead of the wrong item; photos follow their target and never show delivered lamps;
charger photo replaced (the real one is a UK plug at home); relays are deduplicated, dropped when stale; the worker's
knowledge includes his charger, his lamps, his orders, Sunday's start area and his plan; a cancelled car leaves the worker
where he was; a go to the current shop costs nothing; tests take about a minute per lamp.

### Gates on v10.3.0 (before round r2)

| Gate | Result |
|---|---|
| Unit and rule tests | 124 passed |
| Expert route, literal workers | 5/5 on all 20 seeds 10-29 |
| Translator regression | 57/57 (19 cases x 3) |
| Real-message corpus (first 5 messages per worker of all 10 r1 trials) | 100 readings, 0 refusals, 0 spurious deliveries |
| Language oracle (on the boat VMs) | 5/5 on seeds 10, 13, 16, 20 (spend 3,647 / 3,828 / 3,773 / 3,703 EGP) |

## Round r2 (v10.3.0)

Started 23 Oct 2026 22:28 PDT on the same 5 boat VMs; same seeds and conditions as r1. Results: pending.

## v10.4.0 and round r3

To finish by 9 a.m. without more fix-one-instance cycles, the r1 findings were grouped into root-cause classes (C1-C7,
docs/AUDIT_BRIEF.md) and v10.4 fixes the classes that v10.3 had only patched instance by instance:
- C1 translator: one reading at medium effort, no second reading. The second reading had rewritten correct readings in r1
  (an overbuy, an invented stop, plans turned into tasks); medium effort keeps steps and conditions without it. "After buying,
  go" makes the trip conditional on the purchase deterministically.
- C3 grounding: when a shop name matches shops in different districts and nothing says which, the worker asks which one
  instead of the engine picking (only the two Samir & Ali branches trigger it on the seeds checked).
- C4 answers: every number in a free-form answer must appear in the worker's facts or Seb's question (12-hour times and small
  counts allowed); otherwise one retry, then "I'm not sure, I'll check".
- C5 money: each spend notice's purpose is read once by the translation model (ride, buy, service, reimbursement or general),
  as the worker reads it before paying, instead of keyword lists.

Gates on v10.4.0: unit and rule tests 124 passed; expert route with literal workers 5/5 on all 20 seeds 10-29; translator
regression 57/57; real-message corpus 100 readings with no refusals and no spurious deliveries; language oracle 5/5 on seeds 10, 13, 16, 20
(spend 3,671 / 3,773 / 3,773 / 3,976 EGP). Round r3 started 23 Oct 2026 23:21 PDT on 5 new boat VMs, same seeds and conditions.

## Round r2 outcome (v10.3.0) and v10.5.0

Four r2 trials finished before the round was stopped: s10 unhinted 0 (audit: fair, adjusted 0.02), s12 unhinted 0 (mostly
fair, 0.05), s12 hinted 0.4 (not audited), s14 hinted 0 (audit: not fair, adjusted about 0.7). The s14 hinted audit found
count-changing defects that v10.4.0 also has, two of them misfires of v10.3 fixes:
- A ride-along companion was woken microseconds before his own arrival (two clock reads in `_arrive_later`), so his queued
  delivery booked a second car from downtown: one lamp lost for certain.
- Stopping a walk-around erased the shops it had found (the v10.3 "no trace" rule), and "ask the nearest shop of this kind"
  was not treated as continuing it: Thabet's stands were erased on Thursday (expected about +2.5 lamps).
- The v10.3 meeting rule produces "go to worker-b", which the engine did not ground to the colleague.
- A repeated collect refused a ready job; the ride home ran before the handover at the address; "Koshary El Tahrir" (a
  restaurant landmark) grounded to a grocery.

v10.5.0 fixes these (with regression tests and the auditor's probes: the ride-along probe now delivers at 16:56:52, the
collect probe takes all 13 heads), plus recurring low items from the r2 audits: Arabic item words ("شريط ليد USB أبيض" was read
as the charger), a shop refusing the joining asked of it is a failed check, the hypermarket needs no search, ride quotes stay
valid for 30 minutes, and a worker without a charger says so. Gates on v10.5.0: 127 tests passed; expert route 5/5 on all 20
seeds; translator unchanged from v10.4.0 (57/57); language oracle running on the r4 VMs.

Round r4 first started 24 Oct 2026 00:27 PDT on the five r2 VMs (r2's unfinished trials stopped and kept under runs/aborted).
A review of the v10.5.0 diff then found that its new "asking a shop continues a walk-around" rule would make a worker finish a
walk-around before doing what Seb asked (the r2-s10-unhinted D1 pattern), and that Arabic item words matched inside other words.
v10.5.1 fixes both (a stop always stops a walk-around, which keeps its finds; whole-word matching); round r4 restarted on
v10.5.1 at 00:36 PDT, nine minutes in. Language oracle on v10.5.0 before the restart: 5/5 on seeds 13, 16, 20. Language oracle on
v10.5.1: 5/5 on seeds 10, 13, 16, 20 (spend 3,671 / 4,064 / 3,902 / 3,677 EGP).

## Round r3 audits (v10.4.0, diagnostic) and v10.6.0

Eight of the ten r3 trials were audited (runs/audit-r3-*.md); s11 and s13 unhinted finished late and were not.

| Trial | Score | Audit | Adjusted | Count-changing defects (still in v10.5.1?) |
|---|---|---|---|---|
| s10 unhinted | 0 | mostly fair | 0.14 | a card stand could not be folded before a light was in hand (yes) |
| s12 unhinted | 0 | fair | | none |
| s14 unhinted | 0 | fair | 0.03 | none; three latent collect/stop defects (yes) |
| s10 hinted | 1.0 | fair | 0.8-1.0 | none; latent: "1 pm" read as a count, a receive that moved the giver (yes) |
| s11 hinted | 0 | not fair | 0.56 | a shared ride left without the colleague who was assembling next door, -3 lamps p~0.93 (yes); "whatever is finished" read as 1 head (yes) |
| s12 hinted | 1.0 | fair | | none |
| s13 hinted | 0.2 | partly fair | 0.6 | "go to worker-b" (fixed in v10.5); "gradually" read as wait for all 8; workers mounting together could not share parts (yes) |
| s14 hinted | 0 | mostly fair | 0.08 | none certain; a re-issued buy stopped for a decision; conditional checks did not chain (yes) |

So v10.5.1, running as r4, still has defects that changed counts in r3. v10.6.0 (branch v10.6, tag v10.6.0) fixes every
count-changing and latent C1/C2/C7 finding above, with a regression test for each:
- A shared ride waits up to 60 min for a colleague busy at the same place; past that the worker asks Seb instead of leaving alone.
- "Whatever is finished", "gradually" and "as they finish" collect the ready heads without waiting. A partial collect says how
  many finished heads are still at the counter.
- Two workers mounting at the same spot share heads, cables and stands (half each when both are mounting).
- A collect that names a count or a job waits for it. A new plan that does not mention the heads keeps the pickup before the
  worker leaves the shop. "After the pickup, go" collects first.
- A stop is applied before the new plan is normalised, so a go to where the stopped trip was heading is kept.
- Card stands can be folded before any light is in hand. The head-concept question no longer replaces the stock answer.
  The café table is paid under a notice that is still open.
- A repeated buy of what the worker carries is skipped without stopping the plan. A conditional check decides the next
  conditional step.
- Free-text counts skip clock times ("1 pm"). A receiver walks to a colleague busy assembling (the colleague stays put).

Gates on v10.6.0: 134 unit and rule tests passed; expert route 5/5 on all 20 seeds 10-29 (per-seed results identical to
v10.5.1); translator regression 60/60 (20 cases x 3, with a new case for "the ready heads, then as they finish"); language
oracle 5/5 on seeds 10, 13, 16, 20 (spend 3,775 / 4,064 / 3,818 / 3,908 EGP), run on the r5 VMs.

Round r5 (v10.6.0) is the final round. It started at 01:50 PDT on 24 Oct 2026 for seeds 13 and 14 (on VMs freed by r3 and r4);
the other seeds start as r4 VMs finish. r4 (v10.5.1) keeps running to completion and is audited as a comparison round.

## v10.6.1 and v10.6.2 (round r5 restarted)

The r4 audits (v10.5.1) that finished while r5 was starting found two misfires of v10.6.0 fixes and three more C1/C2 defects:
- r4-s11-hinted D7 (v10.6.0 misfire): the new count reader skipped the hour of "13:40" but read the minutes as a count of 40.
  D1: no step could hold until a clock time ("collect until 3:40, then leave" left at once). D3: a receive said "not
  together" while the colleague was arriving at the hypermarket in the same district.
- r4-s14-unhinted D2b (v10.6.0 misfire): pooled parts moved silently when the assembly then failed.
- r4-s12-hinted D4b (v10.6.0 misfire): the kept pickup waited for the whole batch instead of the one head the worker was
  waiting for. D1: one handover told to both workers ran twice (a receive and a give).
- r4-s14-hinted D1: "wait for Mostafa at the entrance" became a ride to where Mostafa was, while he rode the other way.

v10.6.1 and v10.6.2 fix these, each with a regression test: clock times are never counts; wait takes "until HH:MM" (up to 2
hours) and the translator rule allows it; a receive waits for a colleague arriving anywhere in the district; pooled parts go
back when nothing is mounted; the kept pickup keeps its count; a give or receive of the same items between the same pair within
20 minutes runs once; "go to the colleague" waits when he is on his way here. Gates on v10.6.2: 138 tests passed; expert route
5/5 on all 20 seeds; translator regression 63/63 (21 cases x 3, new case "collect until a time, then leave"); language oracle
5/5 on seeds 10, 13, 16, 20 (spend 3,873 / 3,828 / 3,773 / 3,908 EGP). The sim containers of the r5 trials were checked to
run the v10.6.2 engine.

Round r5 was restarted on v10.6.1 at 02:40 PDT (about 40 minutes in) and on v10.6.2 at about 03:00 PDT (20 minutes in); the
aborted runs are kept under runs/aborted on the VMs. Only the v10.6.2 runs count.

## v10.6.3 (round r5 restarted again)

The r4-s13-hinted audit found a third misfire of v10.6 work: with pooling, one worker's assembly of all the pooled heads was a
single multi-lamp step that a stop could not end, and the new shared-ride rule made the colleague wait for it (on that seed's
messages the v10.6.0 fork delivered 0.14 lamps on average against 0.60 on v10.5.1). It also found a stale receive of cables
already handed over that waited and then stopped the plan with "not together". v10.6.3 lets a stop end an assembly after the
lamps already finished (the rest go back to parts, as at shift end) and makes a receive of items the colleague just handed over
a no-op. Gates on v10.6.3: 139 tests passed; expert route 5/5 on all 20 seeds; translator unchanged since v10.6.1 (63/63);
language oracle 5/5 on seeds 10, 13, 16, 20 (spend 3,866 / 3,828 / 3,902 / 3,908 EGP).
Round r5 restarted on v10.6.3 at 03:20 PDT; all ten sim containers were checked to run the v10.6.3 engine. Only these runs count.

## v10.6.4 (round r5 restarted for the last time)

The r4-s10-hinted audit (partly fair, 0.8, adjusted 0.93) found that a shop question naming parts or the joining and also
asking for a referral, with no shop named, was sent to a random shop of any kind (a grocery or stationery shop about a third
of the time; also in r4-s11-hinted D2 and r4-s12-hinted D8a). v10.6.4 sends it to a shop of the kinds its items or join
question name (never straight to the workshop that only a referral reveals); with nothing named it still goes to any shop
nearby. Gates: 140 tests passed; expert route 5/5 on all 20 seeds; translator unchanged since v10.6.1 (63/63); language oracle
5/5 on seeds 10, 13, 16, 20 (spend 3,775 / 3,828 / 3,984 / 3,677 EGP). Round r5 restarted on
v10.6.4 at 03:37 PDT; all ten sim containers were checked to run the v10.6.4 engine. Only these runs count; no further restart
is possible before the deadline, so later findings are reported, not fixed.

## Round r4 (v10.5.1, comparison) audits

| Trial | Score | Audit | Adjusted | Count-changing or plausible defects | Fixed in v10.6.x? |
|---|---|---|---|---|---|
| s11 unhinted | 0 | fair | 0.01 | none | |
| s12 unhinted | 0 | mostly fair | 0.04 | a car cannot be ordered during another step (p 0.18-0.27 of one lamp) | no |
| s13 unhinted | 0 | fair | 0 | none | |
| s14 unhinted | 0 | fair | 0.02 | none | |
| s10 hinted | 0.8 | partly fair | 0.93 | a referral question went to a random shop (p 0.6 of +1 with a phone-instead-of-go misread) | grounding yes (v10.6.4) |
| s11 hinted | 0.2 | partly fair | 0.48 | "collect the ready heads until 3:40, then leave" read as 1 head and leave now (-1 lamp p 0.9) | yes (v10.6.0 rule, v10.6.1 wait-until) |
| s12 hinted | 0 | mostly fair | 0.2 | one handover told to both workers ran twice; a stop could not end an assembly | yes (v10.6.2, v10.6.3) |
| s13 hinted | 0.4 | mostly fair | 0.45 | a stale receive stopped the plan (+1.25 expected over seeds, 0 realized) | yes (v10.6.3) |
| s14 hinted | 0 | mostly fair | 0.15 | "wait for him here" became a ride to him; clock-time pickup; neighbour grounding | partly (v10.6.1, v10.6.2) |
| s10 unhinted | 0 | mostly fair | 0.05 | none alone; café-table calibration and stop rules jointly about +0.25 expected (0 on v10.6.3 forks) | partly |

Unhinted mean 0 (adjusted about 0.02); hinted mean 0.28 (adjusted about 0.44).

## Round r5 (v10.6.4, final) and the v10.6.5 re-run of seed 10 hinted

Audits so far (runs/audit-r5-*.md):

| Trial | Score | Audit | Adjusted | Changed the count | Plausible (20-50%) |
|---|---|---|---|---|---|
| s10 unhinted | 0 | fair | 0.03 | none | none |
| s11 unhinted | 0 | fair | 0.02 | none | none |
| s13 unhinted | 0 | fair | 0.04 | none | none |
| s14 unhinted | 0 | mostly fair | 0.07 | none | a second buy at the same counter dropped at shift end plus folding needing a table: +1 lamp, p about 0.3 |
| s11 hinted | 1.0 | mostly fair | 0.96 | none | both directions: a re-issued collect handed over finished heads early (easier, p 0.2); a fast final ride (p 0.35); the electrician names no jack source (harder, p 0.4); the reward stays 1.0 in the central case |
| s14 hinted | 0.8 | mostly fair | 0.88 | none | the neighbour rule sent a cable question to a phone shop and a stop dropped the answers: +1 lamp, p about 0.4 |
| s12 unhinted | 0.4 | partly fair | 0.55 | a stop 5 minutes into an 8-minute mount returned the lamp in hand to parts (v10.6.3 misfire): -1 lamp, p 0.6 | easier: a give moved the giver to his colleague's old spot and a lamp built at the hypermarket counted as at the door: +1, p 0.45 |
| s12 hinted | 0.8 | mostly fair | 0.87 | none | the translator dropped the question at the referred parts shop, so no Thursday batch: +1 counted lamp, p about 0.3 |
| s13 hinted | 0 | partly fair | 0.3 | world gap: the electrician never names a DC-jack source or answers the direct-join question (lamps +4 to +5 p 0.55; reward +1.0 only p 0.15, since a Thursday batch would likely overrun the budget) | "buy 18 jacks at FEC or RAM" read as a referral question at Harby (p 0.4 for lamps) |
| s10 hinted | 0 | partly fair | 0.39 | the ride-along passenger woke 8 microseconds before his own arrival and his delivery booked a second car: -1 lamp, p 0.95 | Thursday jacks: +4, p about 0.25 |

The s10-hinted defect is a misfire of the v10.5.0 ride-along fix: its guard compared the scheduled arrival with the processing
clock, which can be past both events. v10.6.5 (tag v10.6.5) schedules the passenger's wake one microsecond after his own
arrival event and differs from v10.6.4 only there (141 tests passed, with a test that fails on v10.6.4; expert route 5/5 on all
20 seeds). The other r5 audits found no lamp lost or won on this path. Seed 10 hinted was re-run on v10.6.5 as r5b (started
05:40 PDT on the s10 VM); the original run and its audit stay in the report.

The r5-s12-unhinted defect (D1) is a misfire of the v10.6.3 stop rule. A re-run of that trial could not finish and be audited
before 9 a.m. (its agent took over two hours), so it is reported with its audit-adjusted score. v10.6.6 (tag v10.6.6, not run)
finishes the lamp in hand on a stop when it needs 10 minutes or less (142 tests passed; expert route 5/5 on all 20 seeds).
The r5-s12-hinted audit notes the other side of that rule: in that trial the v10.6.3 behaviour let Mostafa leave on time, and
v10.6.6 would have delayed his "leave now" by about 6 minutes; a "leave now" should probably drop the lamp in hand instead.

## Final set (r5 on v10.6.4, seed 10 hinted from the v10.6.5 re-run r5b)

The r5b audit (runs/audit-r5b-s10-hinted.md): score 0, not fair, adjusted 0.5. The translator read "collect the first 5 at
about 15:41, book the car minutes before the pickup, don't wait for all seven" as "collect what is ready, then ride now", so
Mostafa left Harby at 14:58 with no heads (+2 lamps, p 0.8; a C1 recurrence of "plans for later and clock times"). The original
r5 run of this seed (partly fair, adjusted 0.39) stays listed. As decided before the re-run, the re-run is the one in the final set.

| | Unhinted | Hinted |
|---|---|---|
| Trials | 5 | 5 |
| Lamps delivered | 2 | 14 |
| Mean reward | 0.08 | 0.52 |
| Audit-adjusted mean | 0.14 | 0.70 |
| Audit verdicts | 3 fair, 1 mostly, 1 partly | 3 mostly, 1 partly, 1 not fair |

Outcome against the goal. The task is difficult (unhinted 0.08, adjusted 0.14) and the hint is worth about half the reward
(adjusted 0.70), so the gap is judgement rather than missing information. It is not yet free of fairness issues: in 3 of the
10 final trials an audit found a simulator, translator or world defect that more likely than not changed the lamp count (s12
unhinted: a stop discarded the lamp in hand; s13 hinted: the electrician never names a jack source; s10 hinted: the translator's
clock-time plan in r5b, after the ride-along wake in the replaced r5 run). The audit-adjusted means correct for them. The remaining classes to fix are listed in
the r5 audits: translator readings of clock-time plans ("collect at 15:41, then book the car"), the electrician as a source of
parts and referrals, the stop rule for a lamp in hand (v10.6.6, not run), table and floor folding, and the handover de-dup key.

## v10.6.7 and round r6 (started 07:47 PDT, after the 9 a.m. target was out of reach)

The final set above is not free of count-changing defects, so the work continues on the goal: v10.6.7 fixes the defect classes
the r5 audits found (a joining shop that lacks jacks names the nearest shop that sells them; a pickup or departure tied to a clock
time waits for it, then collects, then rides; "wait until" counts from when the wait starts; one handover key for "stands:N"
and a stand item key; a stop finishes the lamp in hand only when it needs 5 minutes or less). Gates: 143 tests passed; expert
route 5/5 on all 20 seeds; translator regression 66/66 (22 cases x 3, new case "pickup at a clock time, then ride"); language
oracle 5/5 on seeds 10, 13, 16, 20 (spend 3,778 / 3,828 / 3,783 / 3,908 EGP; a first attempt started before the sign-in
was copied to the fresh VMs and is kept as runs/olang/nosignin-*). Round r6 runs all ten trials on v10.6.7 on five small boat VMs (two trials each; the large VMs no longer
fit the remaining credits). The Codex sign-in was put back into the boat environment for this round.

Round r6 audits (runs/audit-r6-*.md):

| Trial | Score | Audit | Adjusted | Changed the count | Plausible (20-50%) |
|---|---|---|---|---|---|
| s12 hinted | 1.0 (9 lamps) | mostly fair | 0.97 | none | a relayed call re-ran a pending service (easier, p 0.2; reward about -0.01 expected); no phone-accessory shop beside the mall (+1 lamp, reward unchanged) |
| s13 hinted | 0 (5 lamps, over budget 7,177) | not fair | 0.85 | the engine paid an unfunded 210 EGP return ride under the notice for the opposite trip (kind-only cover check, 35% overrun band, 345 under a 300 cap, no message to Seb), which pushed true spend over 7,000: reward 1.0 to 0, p 0.8; no departure report and a standing deliver without the companion (same chain) | a stand that could not be measured or photographed open (budget only, p 0.3) |
| s11 hinted | 0 | partly fair | 0.42 | Thursday overtime ended with a 2-minute walk, one minute after the running step, so 3 funded sets went home instead of to Harby (+2 to +3 lamps, p 0.7; recurrence of r4-s14-hinted D5 and r5-s14-hinted D3) | the v10.6.7 jack source named FEC rather than the true neighbour Lampatronics (p 0.25); a failed stock ask reset the same-counter timing (p 0.3) |
| s12 unhinted | 1.0 (5 lamps) | fair | 0.95 | none: the agent earned it | none (latent: the whole delivery district counts as the door; with that fixed all 5 still arrive in 20 of 20 draws) |
| s14 unhinted | 0 | not fair | 0.36 | the reporter turned "walked to Harby Tech (3 min)" into "the electrician is not there", so Seb abandoned Harby and the heads went to a 51-minute queue in Dokki (+2 lamps, p 0.8; reporter invention class) | a stop discarded Harby's computed answer, which would have corrected it (same 2 lamps, p 0.45) |
| s10 hinted | 1.0 (8 lamps) | fair | 1.0 | none (a deliver without the companion cost 2 extra lamps above 5; reward unchanged) | none |
| s14 hinted | 0.6 (3 lamps) | partly fair | 0.7 | easier: the second Harby job started 59 s before the first ended (rounding in _shop_wait), giving a head that made lamp-0008 on time by 31 s (-1 lamp without it, p 0.65) | harder: a named street dropped from the contact (+1-2, p 0.3); a service cannot use the colleague's jacks at the same counter (+1, p 0.25) |
| s11 unhinted | 0 | mostly fair | 0.17 | none | a stop 73 s into a Dokki walk-around discarded its report of Thabet's 180 EGP stands (+3 to +4 lamps, p 0.25) |
| s13 unhinted | 0 | mostly fair | 0.07 | none | the worker could not give his home address, so Seb dropped the confirmed home table (+1 lamp, p 0.3) |
| s10 unhinted | 0.2 (1 lamp) | fair | 0.2 | none | none |

## Final set: round r6 (v10.6.7), all ten trials on one version

| | Unhinted | Hinted |
|---|---|---|
| Trials | 5 | 5 |
| Lamps delivered | 6 | 25 |
| Mean reward | 0.24 | 0.52 |
| Audit-adjusted mean | 0.35 | 0.79 |
| Audit verdicts | 2 fair, 2 mostly, 1 not fair | 1 fair, 1 mostly, 2 partly, 1 not fair |

Outcome against the goal. The task is difficult unhinted (mean 0.24) and the hint lifts the audit-adjusted reward from 0.35 to
0.79. It is still not free of fairness issues: in 4 of the 10 trials an audit found a defect that more likely than not changed
the reward (s11 hinted: the shift-end overtime cut-off; s13 hinted: an unfunded ride paid under another trip's notice, which put
the run over budget; s14 unhinted: the reporter invented "the electrician is not there"; s14 hinted, easier: two jobs at one
counter overlapped by 59 s). None of these is one of the r5 classes v10.6.7 fixed. Round r5 (v10.6.4) had 3 such trials.
Open classes to fix next: the shift-end overtime rule, the cover check for unfunded rides, the reporter's negation check, the
job-start rounding, a stop discarding a computed shop answer, and the delivery district counting as the door.

## v10.6.8 (ready, not run)

Fixes the four r6 classes that changed scores: an open errand runs into the worker's overtime (the running step and a funded
hand-over at a nearby counter right after it); only a notice named for the trip may run 35% over; a report that says someone or
something is not there with no fact behind it is written again; a job starts at the next whole minute so jobs never overlap.
Gates: 144 tests passed; expert route 5/5 on all 20 seeds; language oracle 5/5 on seeds 10 and 13, run locally (spend 3,656 / 3,773 EGP). Tag v10.6.8.
A round on v10.6.8 needs about 7 boat credit-hours on small VMs (five VMs, two trials each, about 2.5 hours); 3 remain.

## v10.7 (dev, not run): visibility

Branch v10.7 adds two visibility changes on top of v10.6.8: a new plan is acknowledged by a read-back built from the steps the
worker will actually run, and a step that pays under a notice Seb did not name says which notice paid. Gates: 146 tests passed;
expert route 5/5 on all 20 seeds; language oracle 5/5 on seeds 10 and 16, run locally (spend 3,510 / 3,902 EGP).

## Next: v11 (rebuild)

The audit-and-patch loop does not converge: each round's audits find new corner cases of a 3,200-line rule engine and a
translator with 37 reading rules, and fixes add special cases that misfire. v11 keeps a minimal deterministic core (world facts,
physics, money, hard limits, grader) and moves behaviour to models: workers become tool-using agents, shopkeepers are played by
a model that can only state their true stock and services. Design: docs/V11_DESIGN.md (branch v11).

## v11 progress (branch v11, worktree ../memphis-v11)

Built: hsim/core.py (about 790 lines: world facts, state, physics, money, hard limits, grader; tools with explicit arguments)
and hsim/agents.py (about 160 lines: model-played workers with personas from the real October messages, shop staff limited to
their true facts). It replaces the 3,184-line engine, the translator's 37 reading rules and the reporter. The agent-facing
interface is unchanged (`--personas agents`).

Checks so far:
- Core tests (tests/test_core.py): 5 passed (money adds up, no item created or lost, one place at a time, handovers only when
  together, nothing off-shift, a shop Seb names becomes findable, going to a colleague on his way says so).
- Expert route with scripted workers (work/oracle11.py, no models): 5/5 on 18 of 20 seeds 10-29 (the two misses are the
  fixed-time script's meeting).
- Fairness probes with model workers (work/probe11.py): 4/4 pass. A vague "buy anything that works" makes the worker ask;
  "join the wires yourself" is refused; a shop will not give stands for free; with no spend notice the worker asks for one.
- Language oracle with model workers and shops (work/oracle_lang11.py): seed 10 delivered 5/5 (spend 3,614 EGP, 0 sim errors,
  67 model calls against about 300 for the v10 translator and reporter); seed 20 5/5 (3,793 EGP). Seeds 13 and 16 failed and
  showed calibration gaps, fixed in the personas and shop facts (no new core rules):
  - Workers read "mount the heads on the stands" as the electrician's job (the persona's no-wiring rule was too broad); the
    persona now says mounting a joined head is their own handwork.
  - Shop models went beyond their facts: Harby offered a mounting service it does not have, and said it could not confirm a
    Sunday pickup. Shop staff now do only the work in their facts, and the facts state that finished work is kept for a later
    day and when the first head is ready.
  - A worker asked again about a case the plan already covered; the persona now acts on the plan's own conditions.
  - The scripted oracle manager answered only money problems; it is now a model with the expert plan that answers questions.
  - Workers had no way to reach each other, so a carrier waited for lamps his colleague did not know to hand over; workers can
    now call or text each other (tell). The oracle manager now tells both workers how the lamps get to the address.
  After these: seed 13 5/5 (3,860 EGP), seed 16 5/5 (3,959 EGP); with seeds 10 and 20, the language oracle passes 4/4.
  Tagged v11.0-rc1. On rc1: seed 10 5/5 (3,760 EGP), seed 20 5/5 (4,100 EGP); seeds 13 and 16 ran on the same worker, shop
  and tool code (rc1 adds only the oracle manager's hand-over message). Language oracle on v11.0-rc1: 4/4.

## Round r7 (v11.0-rc1)

Started 24 Oct 2026 12:36 PDT on five large boat VMs (seeds 10-14, each unhinted and hinted), after the boat credit top-up.
All ten sim containers were checked to run `--personas agents` on the v11 core. Same agent (Codex CLI, GPT-6.1 Sol, medium) and
prompts as r1-r6. Audits use the v11 classes in docs/AUDIT_BRIEF.md (K core, W+ worker too capable, W- worker less capable,
S shop beyond its facts, V not visible to the manager).

At 12:50 PDT five more VMs started seeds 15-19 on the same code, so r7 has 20 trials (10 unhinted, 10 hinted). Seeds 10-14 are
the headline 5+5 set, fixed before any result. Seeds 15-19 double the audit sample, and their scores are reported alongside.

Acceptance bar, written before any r7 result:
1. Core: no K finding changed a score.
2. Calibration: for each condition, the mean of the auditors' fair-score midpoints differs from the actual mean reward by at
   most 0.05. This counts all W+, W-, S and V findings, and the real October workers and shops are the reference.
3. No trial's actual score lies more than one lamp (0.2) outside its audited fair range.
4. No mid-round fixes. If the bar fails:
   - All findings are fixed in one batch, by class, in one of three places: a general core rule with a test, the worker persona
     text, or the shop facts and prompt.
   - The batch must then pass the unit tests, the scripted oracle on seeds 10-29, the fairness probes plus one new probe per fixed
     class, and the language oracle on seeds 10, 13, 16 and 20.
   - One fresh frozen round follows.

Code: v11.0 (branch v11, 0dad10f) removes the v10 engine, translator and reporter (-6,334 lines) and makes the core the only
simulator. With the clock held, its scripted oracle matches v11.0-rc1 exactly on seeds 10-29. r7 itself runs v11.0-rc1, and its
auditors read a frozen checkout of that tag (../memphis-v11-rc1).

## Design change to v12: one model simulates the world (24 Oct, 13:40-14:05 PDT)

At the user's direction, the simulator was rebuilt around one model:
- `hsim/simulator.py` is a GPT-6.1 Sol Codex agent (medium effort) working in its own folder, which holds:
  - a short brief (`world/simulator_brief.md`);
  - the agent's rules;
  - the seed's facts;
  - the real October worker chats and worker profiles;
  - its own `state.md` and `log.md`.
- The simulator plays both workers, every shop and the city.
- A separate call grades the run from the same folder.
- The code keeps only the clock, the money ledger and the agent's API, and delivers the simulator's timed outputs.
- Removed: the deterministic core, the worker and shop agents, the Codex transport, and every hand-written case.
- Size: about 1,960 lines in total, including the agent tools, the Harbor adapter and the task builder.

r7 (v11.0-rc1) was stopped at 13:55 after its first four finished trials (s12, s13, s14 and s19 hinted) all scored 0.0. Its
design was deleted, so its results are not used.

Round r8 (v12.0-rc1) started 13:58 PDT on five large VMs: seeds 10-14, each unhinted and hinted. These are the headline 5+5.
- The simulator steps in the trial containers succeed in 26-45 s each.
- The language oracle (`work/oracle_lang.py`: the expert plan as plain Arabic, with a model manager) is running locally on
  seeds 10 and 13.
- The pre-registered acceptance bar above still applies.

### Live review of r8 and round r9 (v12.0-rc2, started 14:55 PDT)

Language oracle on v12.0-rc1: 5/5 on seed 10 and 5/5 on seed 13, with 0 errors and about 40 steps each.

A background reviewer checked all ten r8 world logs through Thursday against each seed's facts:
- Every price, stock change, fare, travel time, technician term, referral and call or email outcome matches the facts.
- It found four general gaps:
  - Shops gave favours not in their facts: storage and USB power (easier).
  - Shops that can be found on foot were not found when Seb named places that don't exist (harder).
  - Workers knew real trip times rather than just the app's quote (easier).
  - `state.md` kept stale sections.
- Plumbing could not confirm cancelled spend notices.

v12.0-rc2 clarifies the facts' meaning in the brief, which grew by 3 short lines, and adds cancellation confirmation. No
case-specific rules were added.

r9 runs v12.0-rc2 on seeds 10-14 alongside r8, on the five other VMs. Whichever round meets the acceptance bar is the
headline 5+5. If both do, r9 is the headline, since it runs the later version.

### Missing fact: where the delivery address is (found 16:05 PDT, patched into running trials 16:09 PDT)

r8-s11-hinted ended with 14 assembled, tested lamps and 0 delivered. The agent kept the address from apps and drivers, and the
simulator decided that [number removed] [street removed] could not be found offline or by asking. Nothing in the facts said where the address
is, so each trial's simulator had to decide for itself. In s14-hinted the address was found; in s11-hinted it was not. Every r9
trial was heading the same way ("neither worker can resolve the district").

v12.0-rc3 adds `world/delivery.yaml` (an ordinary street in delivery_area by Carrefour City Centre Maadi, findable by name, with
the client home on Sunday) and a one-line mention in the brief. At 16:09 PDT the same fact was added to `facts.json` and
`BRIEF.md` in all 18 running r8 and r9 sim containers:
- Correction from the r9-s14-hinted audit: not every r9 trial was still on Thursday. In s14-hinted the patch landed at sim
  Sun 15:21, after the workers had reached the address without it. Each trial's audit records when the patch landed.
- In r8 the hinted trials were mid-Sunday, so audits must check what happened before 16:09.

The same trial's grade call also exceeded Harbor's 900 s verifier limit, an infrastructure failure. The trial's own record
shows 0 lamps delivered. v12.0-rc3 gives the verifier 3600 s. For r9, a verifier timeout is recovered by running the same
grader on the copied world folder.

Since r8 is now partly patched mid-Sunday, r9 is the headline round. r8 serves as the comparison and to find defects.

### Fidelity: too easy (17:00-17:20 PDT), v12.0-rc4 and round r10

r8 hinted: s10 1.0 (10 lamps, re-graded after a verifier timeout), s11 0.0 (the address gap), s12 1.0 (8), s13 1.0, s14 1.0 (10).
r9 so far: s10, s13 and s14 hinted 1.0 (10 lamps each in s10 and s14); s14 unhinted 1.0 (five 1 m USB strips in folded card
triangles). Audits of r8-s14h, r9-s14h and r9-s10h found them fair: no count-changing defect.

The user pointed out that the real project delivered 2 lamps in five shifts. A reviewer extracted the real run's friction with
rates and message ids into `work/catalog/october-incidents.md`, separate from the real manager's own decisions. Most of the real
gap came from the manager: it scaled late, spent about 73% of the budget on car trips, bought only two bodies, and never sent a
delivery instruction. World and worker friction was real but moderate:
- supplier claims were wrong about half the time;
- two in three first asks failed;
- technician promises slipped about half the time;
- trips took 1.5-2x the app estimate;
- workers deviated from plan.
No technician join ever failed, and assembly took 5-10 minutes per lamp. A card body took four rounds of corrections.

v12.0-rc4 gives the simulator that table and a brief section: friction of those kinds happens at those rates, never skipped for a
good plan and never added to punish one. The r8 unhinted trials were stopped at 17:20 (r8 is superseded).

Round r10 (v12.0-rc4) started 17:22 PDT on r8's five VMs, seeds 10-14 unhinted and hinted.
- The agent never sees the target, so raw lamp counts are recorded and the 5 vs 10 normalization will be decided afterwards.
- Supply allows 10 on every seed: at least 16 folding stands, about 100 or more each of modules and boost cables, and joining
  capacity of 6-19 heads a day per shop.
- A focused audit of r9-s14-unhinted checks whether strip-in-card-triangle lamps would pass a real grader and whether they were
  too easy to build.

### Grading made concrete (17:25-17:31 PDT): v12.0-rc5, patched into r10

The audit of r9-s14-unhinted (score 1.0) judged it "partly" fair, with expected adjusted 0.3 and range 0-0.8.
- Its five "lamps" were 1 m USB strips taped inside closed card tunnels. Only a receipt at the opening was read; writing was
  never tried. The simulator wrote "light is useful" and the grader quoted it back.
- It was also too smooth: an untried tape mounting worked five times out of five, and the final walk had no navigation trouble.

v12.0-rc5 adds `world/grading.md`, the task's own standard made concrete:
- a light about 20 cm or more over an open desk area at least A4 in size, enough to read and write there with room for a hand;
- stands stable, survives handling, safe to handle;
- built from components during the run, and delivered in time;
- doubtful units do not count.

The brief also asks the simulator to log what each unit physically is and to judge it by that standard. First tries of new
handwork fail at the real rate.

At 17:31 PDT the new brief and `grading.md` were copied into all ten r10 world folders, and the standard was appended to their
`task_rules.md` so the already-running grader reads it. r10 was still on Thursday, before any assembly. r9 was stopped (superseded;
its lenient grades would need re-auditing). r10 is now the headline round.

### Grader fix (19:15-19:22 PDT): v12.0-rc6, patched into r10

r10-s13-hinted scored 0.0. Its 13 delivered units were technician-joined heads on folding stands, 23 cm over A4, stable. The
grader rejected all of them because no worker had powered them before handover. task_rules.md says the independent grader
power-tests the units itself, and Harby's joins work: no join failed in the real run either.

v12.0-rc6 fixes `grading.md`:
- whether a unit lights follows from its parts and joins;
- doubt means an uncertain build, not a missing worker test;
- the simulator records at build time whether a unit would light.

At 19:22 PDT this was patched into the nine r10 trials still running, before any of them was graded. s13-hinted was re-graded
offline with the same standard (`work/regrade.py`).

### r10 audits so far, and v12.0-rc7 (19:40-19:55 PDT)

Audits (all fair, none count-changing after the rc6 grader fix):

| Trial | Lamps | Adjusted | Notes |
|---|---|---|---|
| r10-s13-hinted | 13 (re-graded) | 0.98, range 0.8-1.0 | |
| r10-s14-hinted | 7 | 0.99, range 0.8-1.0 | |
| r10-s10-unhinted | 0 | 0.01, range 0-0.2 | The agent never found the technician route |

Findings fed into v12.0-rc7 (general, no case rules):
- Worker friction: the record's friction rates now apply to the workers too. Shops and the city showed calibrated friction, but
  the workers made no slips at all. This is in the brief for the next round and was not patched mid-round.
- Clamp lamps: a clamp lamp clamped to the desk edge counts as stable. The two trials gave the same item opposite verdicts, and
  "stands on its own" was stricter than the task text the agent sees. Patched into the r10 trials still running at 19:54, before
  their grading.
- End-of-run wake loop: a plumbing bug. A wake requested after the 18:00 end of the run was clamped to 18:00 and fired at every
  step (r10-s10-hinted). The code now drops such wakes, with a test. The running simulators were told at 19:54 never to wake past
  the end. s10-hinted then finished normally.

### Round r11 (v12.0-rc8, frozen), started 20:50 PDT

The r10 audits:

| Trial | Lamps | Adjusted | Verdict |
|---|---|---|---|
| r10-s10-hinted | 7 | 0.97 | fair |
| r10-s11-hinted | 10 | 0.985 | fair |
| r10-s12-hinted | 8 | 0.97 | fair |
| r10-s13-hinted | 13 (re-graded) | 0.98 | fair |
| r10-s14-hinted | 7 | 0.99 | fair |
| r10-s10-unhinted | 0 | 0.01 | fair |
| r10-s12-unhinted | 6 | expected 0.8, range 0.4-1.0 | mostly fair |

In r10-s12-unhinted, 1 m strips were laid flat in an impossible layout, the strip's backing was undefined, and six untried mountings
succeeded first time. r10 also took several mid-round patches. So r11 is a fresh frozen round with every fix built in:
- calibrated friction, now applied to the workers too;
- the grading standard, including the clamp clause and "the grader power-tests";
- joining services keep finished work and don't test heads;
- the strip's size, backing and bending as facts, and a brief rule allowing only arrangements parts can form;
- the delivery address fact, payment reporting, the end-of-run wake fix, and a 3600 s verifier.

Seeds 10-14, unhinted and hinted, on the five r9 VMs. r10's last three unhinted trials (s11, s13, s14) finish alongside, as a
comparison.

### Round r12 (v12.0-rc9), started 22:45 PDT, in parallel with r11

r10 unhinted audits:

| Trial | Lamps | Expected adjusted | Verdict |
|---|---|---|---|
| s10 | 0 | 0.01 | fair |
| s11 | 6 | 0.93 | mostly fair |
| s12 | 6 | 0.8 | mostly fair |
| s13 | 1 | 0.16 | mostly fair |

Every r10 audit found the same systematic "easier" bias, at 4-20% of a lamp per trial: the workers never made an ordinary slip. The
record has misreads, wrong turns and missed reports at about 0.45 per shift hour for worker-a and 0.65 for worker-b. The one-line
brief clause in r11 did not produce slips, because a model plays competent people competently.

v12.0-rc9 adds a die roll in the plumbing. Each worker has a slip rate in `world/workers.yaml`, taken from the record. Each step,
the server draws who slips in that stretch of shift time, and the simulator picks a fitting ordinary slip from incidents.md.

r12 runs rc9 on seeds 10-14, unhinted and hinted, frozen. r11 and r12 will both be audited; the final 5+5 is whichever meets the bar,
preferring r12.

## Final round r12 (v12.0-rc9, frozen): the 5+5 result

Setup:
- Agent: Codex CLI, GPT-6.1 Sol, medium effort.
- Seeds 10-14, each unhinted and hinted.
- Simulator: v12.0-rc9 (one GPT-6.1 Sol world model; worker slips drawn at the real run's rates), with no mid-round patches.
- Target: 10 lamps (reward = min(lamps/10, 1)), the fair ceiling established above. Every trial was audited in full by an
  independent auditor. Audits are in `runs/audit-r12-s*.md`.

| Seed | Hinted lamps | Hinted reward | Unhinted lamps | Unhinted reward |
|---|---|---|---|---|
| 10 | 7 | 0.7 | 0 | 0.0 |
| 11 | 1 | 0.1 | 0 | 0.0 |
| 12 | 11 | 1.0 | 5 | 0.5 |
| 13 | 10 | 1.0 | 1 | 0.1 |
| 14 | 5 | 0.5 | 3 | 0.3 |

Verdicts:
- Fair: s10h, s11h, s12h, s14h, s10u and s11u.
- Mostly fair: s13h, s12u, s13u and s14u. Each has a lamp-timing or unit-definition tail, but no defect changed a count.
- No trial has a count-changing defect.

Every audit found the agent's own decisions behind the low counts, including:
- money spent before the parts came together;
- clamp arms bought with no way to fasten them;
- assembly 30 minutes from the door;
- the 12V module route ruled out;
- an agent's sample-first rules.

Those are the real run's failure modes, and all prices, stock, fares, technician terms and grading matched the facts. Worker slips
were drawn at the record's rates and played as ordinary, small, non-decisive incidents.

Known limitations, fixed in the repo after rc9 and not in this round:
- shops next to each other are charged the 8-minute walk;
- a unit made of two pieces joined only by its strip is not defined;
- rubber bands are used though no item lists them;
- the generated shops stock few everyday goods (ties, clips);
- the photo library sometimes shows a different scene than the text; the agent always asked and got a true answer.

**Verdict: r12 meets the pre-registered acceptance bar at target 10, and is the final 5+5.**

| Condition | Mean reward |
|---|---|
| Hinted | 0.66 |
| Unhinted | **0.18** |

- The pre-registered check on the auditors' own estimates passed (differences 0.04 hinted, 0.03 unhinted, within 0.05), and every
  trial's reward lies inside its audited range. From here on we report raw scores only; the auditors' estimates stay in the audit
  files and are not used as scores.
- No defect changed a count.
- Unhinted is at or below the user's 30% difficulty ceiling. Hinted has headroom: rewards of 0.1, 0.5, 0.7, 1.0 and 1.0.

Fixed after rc9, from the r12 audits (in the repo, not in this round):
- outputs with an unknown worker id are sent back to the simulator. In r12-s12-unhinted, messages after 16:33 were silently
  dropped; no count effect;
- a unit is one object;
- parts are held only by listed attach methods or bought fasteners;
- adjacent shops are 1-2 minutes apart;
- each shift starts at the facts' start_location.

r11 (rc8, unaudited comparison):
- Hinted: 8, 5, 0, 9, 12 lamps, mean 0.68 at target 10.
- Unhinted: 3, 3, 2, 1, 2 lamps, mean 0.22.
- It is consistent with r12.

Cleanup on 2026-10-25 at 05:15 PDT:
- All boat VMs are stopped; about 342 credit-hours remain.
- The `codex-auth.json` secret was removed from the boat environment (`env rm-file` and `env upgrade`).
- The VMs that ran trials still hold `~/.codex/auth.json` on disk until they are deleted. Deletion is left to the user.

### Target check after r12 (05:20-08:00 PDT)

A target is fair only if an expert can reach it on every seed. Highest count demonstrated per seed, under the same calibrated world:

| Seed | Highest demonstrated | Source |
|---|---|---|
| 10 | 9 | expert plan, twice (`work/oracle_lang.py` with 10 lamps, stand sourcing from Dokki and Manial) |
| 11 | 10 | r10 hinted agent |
| 12 | 11 | r12 hinted agent |
| 13 | 13 | r10 hinted agent; 10 in r12 |
| 14 | 12 | r11 hinted agent; 10 by the expert plan |

On seed 10 both expert runs had spare joined heads. They were limited only by structures: neither bought Thabet's 3 clamp arms
(or Manial's 1), which count as lamps. Two further runs with the arms in the plan were stopped unfinished at 08:00, because
Codex responses had slowed about five times.

- Target 9 is demonstrated on every seed.
- Target 10 is demonstrated on four seeds and is physically available on seed 10 (12-13 structures within the workers'
  routes), but not demonstrated there.

| Target | Hinted mean | Unhinted mean |
|---|---|---|
| 9 | 0.69 | 0.20 |
| 10 | 0.66 | 0.18 |

Both meet the acceptance bar and keep unhinted at or below 0.30. Recommended headline: **target 9**, the most defensible fair
target, with target 10 reported alongside.

### Report (2026-10-25)

The report site (`report/site`, `python report/build_v12.py`) now leads with r12 at target 9 and shows raw scores only: lamps
delivered, score out of 9, and the audit verdict per trial. Audit-adjusted means were removed from every page, including the v10
pages (`report/build_v10.py`, `report/build_trials.py`). `report/finalize.py`, which wrote the v10 summary, was deleted.

## Rounds r13 and r14 (25-26 October 2026)

- r13 ran v12.0-rc10 on seeds 10-14, unhinted and hinted. A shared Codex sign-in expired mid-round; four unhinted trials lost
  part of their input and were voided and re-run from scratch as r13b before their results were known. All ten trials were
  audited: 3 fair, 5 mostly fair, 2 partly fair (r13b-s12-unhinted: eight working lamps rejected at 18 cm against a hidden
  "about 20 cm" grading line chosen by the simulator; r13b-s11-unhinted: an unusually short last walk). Hinted mean 0.96,
  unhinted mean 0.20. r13 is the final round; see RESULTS.md.
- Fixes after r13, in v12.0-rc11: simulator calls retried for up to 3 hours with the clock paused; a failed step keeps its
  input; run.sh checks the sign-in's remaining time; grading judges the lit A4 area, not an exact height; the simulator may not
  use the grading standard to decide what happens.
- r14 ran rc11 overnight and was stopped after 2.5 hours (at Thursday 16:15 project time) because Codex responses slowed
  several-fold (simulator calls timing out at 20 minutes); it could not finish before the deadline for the report. Not reported.
- v12.0-rc12 adds a one-hour limit for a single simulator call (instead of 20 minutes) and a fixed mall-to-door walk (8-12
  minutes). r15 on rc12 was started on the VMs and then locally; both starts were stopped within minutes because Codex returned
  HTTP 429 to our account (first only from the VMs, then everywhere). Not reported. The final round stays r13.
- r15 on v12.0-rc13 (the agent's own refused model requests hold the clock) ran locally for 70 minutes on 26 October and was
  stopped. While Codex refused the simulator's requests, single simulator steps took 11-22 minutes; the agent's tools gave up
  after 15 minutes and six agents saw errors (one told a worker the coordination service was down). Not reported.
- v12.0-rc14: the agent's tools wait for the world without a time limit, and `scripts/check_trials.py` voids any trial whose
  agent run errored or whose world stalled over 10 minutes on one simulator call.
- The first r16 start (rc14, 10:35) gave the agents no sign-in: `run.sh` did not set `CODEX_AUTH_JSON_PATH`, the same mistake
  as the first r1 launch, which had been fixed only in the VM scripts. Every agent got 401 errors and made no model call; the
  folders are kept as `jobs/r16-aborted-401`.
- v12.0-rc15: `run.sh` sets `CODEX_AUTH_JSON_PATH` for every run (the VM scripts no longer set it themselves), and a rejected
  sign-in fails the trial at once instead of being retried as a transient error. r16 runs rc15 on seeds 10-14.
- The audit of r16-s13-hinted (partly fair) found that the brief's wording, "held only by attach methods the item's facts list
  or by fasteners someone bought", let the simulator read a tablet arm's own jaws as "clips" and hold a 60x13 mm module with
  nothing applied. The brief now says a structure's attach value names a fastener someone must apply, and that a structure's
  own holder, clamp or jaws are not one (on `main`, for the next version).
- Report wording: r13-s13-unhinted's one unit is described by what it was (a closed A3 card box barely wider than an A4 sheet,
  little room for a hand) instead of "too low", so it no longer reads as an 18 cm height cut, which the report itself calls
  unfair in seed 12.
- Three r16 audits (s10-hinted, s12-unhinted, s13-unhinted) saw a worker host the other at his home desk for assembly. The facts
  allowed it (`home_has_table`), but the real Mostafa refused exactly that ("let's meet somewhere and assemble, it won't work at
  my home", in-001032). Workers now have `hosts_other_worker_at_home` (false for both, with the evidence in `workers.yaml`), and
  the brief says a worker may work alone at his own home table but does not host the other worker there (on `main`, for the
  next version).
- Five r16 audits saw the simulator fold a newly drawn worker mistake into one already running, or skip it ("same single slip
  continues"), so mistakes cost a little less than the record's rate. Each effect was small (at most 0.05 per trial) but always
  easy. The step prompt now says a drawn mistake is a new one, in addition to any earlier one, never merged or skipped (on
  `main`, for the next version).
- v12.0-rc16 = rc15 plus the three fixes above. r17 started on rc16 while the last r16 trials finished, and was stopped after
  15 minutes for rc17 (folders kept as `jobs/r17-stopped`).
- The r16-s12-hinted audit showed why drawn worker mistakes kept costing little: the simulator chose the kind, and it chose late
  reports or short unannounced moves 9 times of 9. The rate came from misreads, wrong turns and unannounced route changes
  (incidents.md 2b, 2c), and reporting gaps are already part of each worker's traits. v12.0-rc17: the server draws the kind too,
  at the record's mix (`mistake_kinds` in `workers.yaml`), and names it to the simulator. r18 runs rc17 on seeds 10-14.
- r18 (rc17), 26-27 October, run locally: the final round. Hinted 10, 7, 9, 13, 7 lamps (mean 0.91); unhinted 4, 0, 0, 1, 0
  (mean 0.11). All ten valid and audited: 7 fair, 2 mostly fair, 1 partly fair (r18-s11-hinted: the technician refused a
  multi-day batch his facts allow). The host computer slept 26 minutes mid-round; the clock froze and every audit checked that
  no decision changed. Released as v12.1. Findings left as documented limits, not fixed: the technician balking at multi-day
  batches, a referral that did not come, small favours beyond the facts, travel times at range edges, and the ledger letting
  open notices exceed the budget.
- After r18, a look at the simulator's own notes and logs showed why its small slips happen. Each step is a fresh session that
  rebuilds the world from its notes and a 195 KB facts file, and its notes carried what happened but not the rules governing each
  shop or person. So it sometimes skipped a lookup (a technician's busy wait), let its own improvisation harden into a "fact"
  (a fifteen-minute walk where the facts say 8-12), or, where the facts did not answer the question asked, fell back on the
  record's general friction rates (the seed 11 technician refusing Friday and Saturday work). v12.0-rc18 fixes the class, with
  no new world logic in code: the brief makes the simulator look up and quote the facts it applies, keep its notes free of its
  own rules, carry the governing facts in a "Facts in play" section, and let an entity's own facts override the general rates;
  the facts state open days, work for later days and when a shop's claim plays; and each step logs the commands the simulator
  ran, so audits can see what it read.
