# Rewrite one audit in plain English (Simplified Technical English)

A person will use your text to check an audit of one simulated trial. They did not write the audit. They know the project but
not the auditor's shorthand. Your job is to say what the audit says, in plain words, so they can check it against the evidence.

## The trial, in one paragraph

An AI manager called Seb directs two simulated workers in Cairo. The workers are Mostafa and Abdelrahman (the audit may call
them worker-a / worker-b, or a / b). They have two shifts: Thursday 14:00-17:00 and Sunday 13:00-17:00. The goal is to build
USB desk lamps from parts and deliver them to a client's address by Sunday 17:00. Each lamp that passes the grading standard
counts. The target is 9 lamps. A language model (the "world model") plays the city, the shops and the workers. It must follow a
file of facts for this seed. An auditor (Claude) checked the trial for anything outside Seb's control that changed the lamp count.

Words to use, always the same way:
- "head": one LED module joined to a DC jack, used with a USB step-up cable. It is the light of a lamp.
- "stand": the thing that holds the light over the desk (folding phone stand, metal arm, clamp arm, cradle).
- "Harby": the technician next door to the LED shop (Lampatronics) downtown. He joins heads.
- "the facts": the seed's file of true facts about shops, prices, stock and people.
- "the world log": the world model's record of events. Cite it as "log N".
- "worker mistake": a mistake the server makes a worker do at random (the audit may say "drawn mistake").
- "the grader": the model that decides which delivered units count as lamps.

## Writing rules (from ASD-STE100)

1. Write short sentences. A sentence has 20 words or fewer. Never more than 25.
2. Put one idea in each sentence.
3. Use the active voice. Say who did the action: "Harby refused the batch", not "the batch was refused".
4. Use simple past for events and simple present for facts and rules.
5. Use common words. Do not use codes, field names or abbreviations from the audit. Say what they mean:
   - "promised_vs_actual 0" becomes "the facts say his promises are never late".
   - "E1", "H1", "I3" are finding ids. You may keep the id once, in the `id` field only.
   - "sim step 36" becomes "the world model's step at 15:56" (use the time if the audit gives it).
6. Use the same word for the same thing every time (see the list above). Do not use synonyms for variety.
7. Do not use noun stacks of more than three words.
8. Use "Seb", "Mostafa", "Abdelrahman", "Harby", shop names and times exactly as the audit gives them.
9. Keep every number exact: times, prices, counts, probabilities. Do not round.
10. Keep the evidence. Where the audit cites a log line, write "log N" (or "log N-M") in the sentence it supports.
    Use only log numbers that appear in the audit. Never add a new one.
11. Do not add facts, reasons or opinions that are not in the audit. If the audit is unclear, say "The audit does not say".
12. Do not use em dashes, semicolons, or "not X but Y" sentences.

## What to write

Read the whole audit file. Then write JSON to your output path, in exactly this shape:

{
  "slug": "<trial slug>",
  "what_happened": ["3 to 6 sentences: what Seb did, what was delivered, how many lamps counted"],
  "cause": ["2 to 8 sentences: why the trial got fewer than 9 lamps, or why it reached the target, from the audit's section 2"],
  "findings": [
    {"id": "H1",
     "title": "one plain line of 12 words or fewer",
     "what": ["1 to 4 sentences: what happened in the simulation"],
     "why": ["1 to 3 sentences: why the audit says the simulator was wrong, and which fact or rule it broke"],
     "effect": "one sentence: the effect on the lamp count",
     "chance": "the audit's chance that it changed the count, for example \"about 45%\", or null if the audit gives none"}
  ],
  "verdict": {"label": "Fair | Mostly fair | Partly fair | Not fair",
              "range": "the fair range, for example \"7 to 11 lamps\"",
              "best": "the best estimate, for example \"8.8 lamps\"",
              "reason": ["1 to 4 sentences: why the auditor gave this verdict"]}
}

Write one entry in "findings" for each finding id in the audit's JSON block (count_changing_defects, plausible_count_changing,
new_defects, known_defects_seen). Use each id once, in the order they first appear there. Then reply with one line: the slug,
the number of findings, and any sentence you could not make plain.
