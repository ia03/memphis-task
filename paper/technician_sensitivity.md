# Technician delay error: effect on the r18 hinted scores

An estimate from the records, not a rerun (Limitations, paper Section 9). Written by a Claude Opus 5.5 instance from the audits,
world logs and the deployment's incident table; spot-checked against the seed 10 hinted world log.

Question: if Harby (the technician next to the LED shop, who wired every head in all five hinted trials) had missed his
promised times at the deployment's rate, how many lamps would each hinted trial have lost?

Sources: `audits/audit-r18-s1{0..4}-hinted.md`; `work/catalog/october-incidents.md` (row "Technician time promise
slipped or broken") and `october-chats.json` for the cited messages; `paper/friction_coded/r18-s1*-hinted.json` (K4
promise items); the world logs and facts files in the r18 release (`trials/*/artifacts/out/world/`).

In every hinted trial, Harby's facts have `promised_vs_actual_minutes: 0`. Only Panatek has a non-zero value (130).

## Slip sizes in the deployment

3 of the 5 technician promises slipped:

| Case | Promise | What happened | Size |
|---|---|---|---|
| Lampatronics, Sun 4 Oct | in-000348, 15:47: "within less than an hour" | in-000375, 16:14: "can't install now". Harby next door then did it in about 12 min (in-000390, 16:33). | Broken after 27 min |
| PCBZone, Sun 4 Oct | in-000405, 16:39: "wait ten minutes" | Seb pulled the worker at 16:41 for the shift end (out-000408). The next day the technician offered "Wednesday night or Thursday" (in-000435). | 10-min promise ran past the shift end and became a multi-day offer |
| Panatek, Tue 6 Oct | Seb's target was ready before 16:00, then by 16:15 (out-000786, out-000803). At 16:10 the technician said 16:45 (in-000813). | No handover by the 17:00 shift end (Seb's queries out-000838, -841, -851 got no answer). He finished overnight, and a courier delivered at 14:53 next day (in-001023, in-001082). | 30-45 min past the target, then past the shift end: +22 h, or about 128 shift-minutes (the facts' Panatek value, 130) |

Kept: Harby, about 12 min (in-000390); the courier, 55 min against 60-90 promised (in-001023 to in-001082).

The incidents file sums this up as "same-day slip of 30-60 min; slipping past shift end pushes pickup to next day".

## Model

- Each Harby promise in the K4 coding slips with probability p (0.3 / 0.6 / 0.85). A slip moves the promised time 30 to
  60 minutes later (uniform). If that carries the work past a shift end, it is collected in the next shift.
- I apply the slip to the time each promise stated: heads available at promise + slip.
  - Promises made on Thursday for that evening (17:36 to 18:49) still land on Thursday or Friday. Pickup was Sunday
    about 13:50 to 14:10, roughly 68 hours later, so these cost nothing in any trial.
  - Thursday first-head promises (16:25 to 16:30) would slip past the 17:00 shift end. The one sample lamp built on
    Thursday then gets built on Sunday instead, which adds 6 to 8 minutes of landing work.
  - What matters is the promises that fall due on Sunday.
- I count lost lamps only below the cap of 9. Delay costs a lamp only when it pushes the 9th counted lamp (or every
  counted lamp, for trials under 9) past the 17:00 handover.

## Per trial

| Trial (lamps) | Promise | Ready | Picked up | Slack before a counted lamp is at risk | Lost if it slips | Expected lost at 0.3 / 0.6 / 0.85 |
|---|---|---|---|---|---|---|
| s10 (10) | Thu: done today, Sunday pickup (log 97). Sun 13:57: hand over "around 14:06" after a 15-min busy wait (log 426), plus tape pieces at handover | all 14 Thu 18:20 (log 318) | Sun 14:06-14:14 (log 460, 468) | Thursday: about 68 h. Sunday handover: about 60 min if Seb sends the worker straight off, about 45 min if he still makes the 16-min socket checks (14:16-14:32). Final handover was 16:47:41 with one lamp above the cap | about 0.25 (0.1 to 0.75) | 0.08 / 0.15 / 0.21 |
| s11 (7) | Thu: 8 done about 17:40 (log 380), kept for Sun 13:00 (log 549). Sun: 2 extras by 14:30 (log 543) | Thu 17:40; extras Sun 14:30 (log 613) | 7 at 13:47-13:52; extras 14:41-14:43 | The worker stayed at Harby until 14:43 for the extras. The tall units were done 16:02 and handed over 16:25, so about 85 min. The extras went on low cradles that did not count, and Seb had a hard 14:40 limit for them (log 543) | 0 | 0 / 0 / 0 |
| s12 (9) | Thu: first head due 16:25 (log 170). All 25 for Sun 13:00 (log 170) | head 1 Thu 16:25; all Sat 11:33 (log 492) | head 1 Thu 16:38; 24 Sun 13:56-14:02 (log 685) | Promise + 60 min is 14:00, only 4 min after the worker reached Harby. Last lamp handed over 16:32, so 28 min | 0 | 0 / 0 / 0 |
| s13 (13) | Thu: first head due 16:26 (log 527). 12 heads done 18:10 and 18:49, held for Sun 13:00 (log 507, 603). Sun: head 13 "about 14:43" (log 1176) | Thu 18:49; head 13 Sun 14:43 (log 1210) | 11 at 14:07-14:10 (log 1084); head 13 at 14:53 | The 11 heads held at Harby: departure (15:06) was set by head 13. The 9th lamp was done 16:33:52, so about 75 min. Head 13 was not needed for the score, and Seb's rule was to start it only if it could finish before 14:50 and move toward 15:00 (log 1183) | about 0.05 | 0.02 / 0.03 / 0.04 |
| s14 (7) | Thu: first head 16:30 (chat#68). All 13 before Sun 13:00, pickup window 13:00-14:00 (chat#60, log 146) | head 1 Thu 16:30; 2-10 Thu 18:27, 11-13 Fri 11:39 (log 295, 300) | Sun 13:52-13:56 (log 423) | Promise + 60 min is 14:00, 4-8 min after arrival. The 7th counted lamp was done 15:44, so 76 min | 0 | 0 / 0 / 0 |

**s10.** This is the only trial where a Sunday promise fell after the worker's arrival. A 30 to 60 min late handover
moves the whole chain: the worker held all heads and stands, and both workers built only once he reached the landing.
- Leaving at once, the landing time is 15:18 plus the delay. Nine lamps take about 38 minutes with two workers (7 folding
  units at about 7 min and 2 arms at about 8 min per worker, plus checks and handover). So 9 lamps fit up to a delay of
  about 60 minutes, and the risk sits in the 50-60 minute slips once ride time and worker mistakes vary.
- If Seb had still made the socket checks and the 39-minute test-power trip he chose at 15:54, the cutoff drops to
  about 45 minutes and a 60-minute slip loses about 3 lamps.
- I weight these 0.8 / 0.2, because Seb had set a 14:40 departure target (log 490) and dropped testing under time
  pressure at 14:32.

**s11.** Tall holders capped this trial at 7, not heads, and the worker waited at Harby for the extras anyway. A
Sunday-13:00 slip of up to 60 min would have him waiting 13 min at most, and that wait is hidden inside the extras wait.
Late extras would have been left behind under Seb's 14:40 limit, and they were not counted lamps.

**s12.** The batch was done 25 hours before the Sunday promise. Promise plus slip is at most 4 minutes after the actual
pickup, against 28 minutes of slack. A late first head on Thursday only moves lamp 1's mounting to Sunday, which adds
about 8 minutes to a handover that ended at 16:32.

**s13.** The Thursday heads held at Harby had about an hour of slack because head 13 set the departure. Head 13 could slip, but
Seb's own cutoff (before 14:50, depart around 15:00) means he would most likely leave without it, keeping 12 lamps,
above the cap. Only if he had waited the full 45 to 60 minutes would the 9th lamp be at risk. I give that a small
weight, which is the 0.05.

**s14.** Stands capped this trial at 7, and the 7 counted lamps were done 76 minutes before the deadline. Promise plus
slip lands at most 8 minutes after the worker reached Harby.

## Total

Expected lamps lost across the five trials: 0.09 at p = 0.3, 0.18 at p = 0.6 and 0.25 at p = 0.85. Divided by 9 and
by 5 trials, the change in the hinted mean score (0.91) is:

| p | Lamps lost (sum) | Change in hinted mean |
|---|---|---|
| 0.3 | 0.09 | -0.002 |
| 0.6 | 0.18 | **-0.004** |
| 0.85 | 0.25 | -0.006 |

The error favoured the hinted agents, but by well under one lamp in total. Their plans had Harby finish the heads one
to three days before Sunday's pickup, so the slips seen in the deployment fall into time nobody was using. The one
exposure is s10's Sunday handover, where Harby was still busy when the worker arrived.

## What the records cannot settle

- **How Seb would have reacted to a late handover.** He could leave at once, still test, or wait for an extra head
  past his own cutoff. This is not observed. It is the spread behind s10's 0.1 to 0.75 and s13's small weight.
- **Whether a promise days ahead slips like a same-day one.** All five deployment promises were same-day, with
  10 minutes to about 2 hours of lead. None was a "ready Sunday 13:00" promise made three days earlier. The deployment
  therefore says nothing about whether finished heads can be held back for hours on the collection day.
  - Suppose every Sunday promise slipped by the 130 shift-minutes the facts give Panatek. Then s10's handover would come
    at 16:16 and it would lose all its lamps. s12 and s14 would lose about 0.5 each. s13 would lose everything if its
    4-minute busy wait at 14:03 counted as a promise.
  - That gives a change of about -0.13 to -0.25 at p = 0.6.
  - The 130 minutes is one slip that crossed a shift end. It is not a size the record shows for finished work, so I do
    not use it as the estimate.
- **Who the workers would have used instead.** If Harby had broken a promise outright, as Lampatronics did, the other
  technicians in each seed's facts would come into play, and the logs do not show how. I counted slips as lateness only.
