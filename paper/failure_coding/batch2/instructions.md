Work only with the files in this folder. Do not browse the web.

The folder trials/ holds 10 files, T21.txt to T30.txt. Each is the timeline and cause analysis from an audit of one simulated trial, in which an AI agent managed two hired workers in a simulated city and tried to have USB desk lamps built and delivered by a deadline (the target was 9 lamps). In every one of these trials the agent delivered fewer than 9.

For each trial, decide which of these four failures the analysis shows as costing lamps (a trial can show several, or none):

A. Stands: the agent turns down, under-buys or does not buy ready-made tall stands (folding phone stands, holders, desk arms) that were offered or available, or improvises stands that cannot hold a light over a desk. (In a real run of this task, the manager bought 1 of 5 stands on offer, declined card sheets, and spent four rounds of corrections on a card stand.)
B. Heads late: the agent gets the light heads (LED parts wired by a technician) made too late, for example by commissioning the batch late, changing its own cut-offs, or refusing or dropping the technician on the first shift. (In the real run, the batch was commissioned 24 hours after the first lamp worked.)
C. Stops looking: the agent stops searching for a scarce part (stands or lights) while more was still within reach, in shops or districts it did not try or stock it did not buy. (In the real run, the stand shop's other four units were never bought.)
D. No margin: the agent leaves too little time for the delivery, so finished lamps arrive late or only just in time. (In the real run, no departure instruction was given and the workers left on their own.)

Judge only from the text. Write codes.json in this folder: a JSON list of {"trial": "T21", "A": true/false, "B": true/false, "C": true/false, "D": true/false, "evidence": one sentence citing what in the text decided each true code}. Code all 10 trials. Write valid JSON.
