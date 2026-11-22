# Hand check of the setback coding

Section 5 of the paper reports that we checked 14 of the Opus coders' decisions on the final-round trials by hand, covering
all eight setback kinds of Figure 4, and agreed with 13.

- `cards.json`: what the reviewer saw for each decision: the kind's definition, the situation, a yes-or-no question, the
  cited evidence from the trial (Arabic messages with an English gloss), and notes on the evidence. The coders' decision was
  not shown.
- `coder_decisions.json`: the coders' decision for each occasion (`happened`), with the trial, the occasion's index in the
  coded file under `friction_coded/`, and the cited log line, chat or call.
- `answers.json`: the reviewer's answer to each card's question.
- `handcheck.py`: prints the agreement and the one disagreement (h09, a phone call in which a shop agreed to prepare lamp
  heads but would give no price or time; the coders counted it as a usable answer, the reviewer did not).

The keys skip h10 and h12, which were dropped from the sample before the check.
