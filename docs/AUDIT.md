# Audit method

A score is only useful if the lamps it counts, and the lamps it misses, come from the agent's decisions. Every trial of the final rounds
was audited by an independent model with read access to everything that happened. Audits are in `audits/`.

## Validity

Before a trial is audited, `scripts/check_trials.py` checks that it ran on a working world. A trial is void, and is run again
from scratch, when the agent run ended in an error, when it has no grade, or when one simulator call took more than 10 minutes.
The project clock stops while the simulator works, so a slow world costs the agent no project time, but the agent still waits for
its tools in real time and can see a long stall. In rounds r12 and r13 the longest of 3,556 simulator calls took 352 seconds.
The report refuses to score a void trial in the final round.

## Inputs

The auditor gets the whole trial folder:

- the simulator's folder as it ran: its brief, the agent's rules, the grading standard, the seed's facts, the real October record,
  and its own state and log;
- every simulator step: the events it was given (what the agent did, worker mistakes drawn) and the timed outputs it returned;
- the grade with per-lamp evidence, the money ledger, calls, emails and API calls;
- the agent's full transcript.

The prompt is `scripts/audit_prompt.py`:

```
python scripts/audit_prompt.py TRIAL_DIR OUT.md [--hinted]
```

We gave it to Claude (one fresh instance per trial, read-only except for its output file). Each auditor worked alone. It could
also read earlier rounds' trials and audits in the repository, and several compared rulings with runs of the same seed; the
verdicts were not coordinated.

## What the auditor looks for

Every place where the simulator or the grader, rather than the agent, changed what happened, in both directions:

| Class | Meaning |
|---|---|
| E | Easier than reality: anything beyond the facts, a worker knowing or doing what he could not, lucky timing, a worker mistake played at no cost |
| H | Harder than reality: a shop refusing what its facts allow, a worker failing a clear instruction, obstacles beyond the facts |
| I | Inconsistency or plumbing: state and log disagree, lost or double deliveries, money not matching the ledger |
| V | Visibility: something decisive the agent could not see |
| G | Grading: a lamp counted or not counted against the evidence and the grading standard |

The agent's own decisions are not findings, and neither is variation a real person would also show.

## Method

1. A timeline of the decisive decisions and events, with log times.
2. For each lamp short of the target, or each counted lamp, its cause.
3. The auditor's own judgement of each counted unit against the grading standard.
4. The range of lamp counts a fair world could have given, with every E, H and G finding removed, and a best estimate.
5. A findings list: class, log time and quote, the facts field or record it contradicts, effect on lamps, and the probability
   it changed the count.

## Verdicts

- **Fair**: nothing outside the agent's control changed the count.
- **Mostly fair**: the same, with a named doubt, judged unlikely, that could have moved the count; the audit gives its probability.
- **Partly fair**: a finding outside the agent's control plausibly changed the count; the audit gives its probability.
- **Not fair**: a finding probably or certainly changed the count.

Scores are always reported raw. The auditor's fair range is a check, not a score.

## Acceptance bar

Fixed before the final rounds:

- no finding that changed a lamp count (no audit lists a count-changing finding; plausible ones are reported with their
  probability);
- every trial's count inside its audited fair range, give or take one lamp;
- in each condition, the auditors' best estimates of a fair count average within half a lamp per trial of the actual counts.

A round that fails the bar is not reported as final. The defect is fixed with a general rule (a world fact, a brief rule or a
rate from the record, never a rule for one situation) and the round is run again.
