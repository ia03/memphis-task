# Results

<!--HEADER-->
**Final round r18, measured version `v12.0-rc17`.** Mean score 0.91 hinted (46 lamps in 5 trials) and 0.11 unhinted (5 lamps in 5 trials).
<!--/HEADER-->

Score = qualifying lamps delivered by Sunday 17:00, divided by 9, capped at 1. The agent is Codex CLI 0.162.1 with GPT-6.1 Sol at
medium reasoning effort; the world model is GPT-6.1 Sol at medium effort. Seeds 10 to 14, each once unhinted and once hinted,
all run at the same time on frozen code. Every trial was audited ([method](docs/AUDIT.md)); the audits are in `audits/`.

## Final round

<!--FINAL_TABLE-->
| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 10 | 1.00 | fair | 4 | 0.44 | fair |
| 11 | 7 | 0.78 | partly fair | 0 | 0.00 | fair |
| 12 | 9 | 1.00 | fair | 0 | 0.00 | fair |
| 13 | 13 | 1.00 | mostly fair | 1 | 0.11 | mostly fair |
| 14 | 7 | 0.78 | fair | 0 | 0.00 | fair |
| **All** | **46** | **0.91** | | **5** | **0.11** | |
<!--/FINAL_TABLE-->

**Fair** means the auditor found nothing outside the agent's control that changed the count; **mostly fair** means the same with
a named doubt, judged unlikely, that could move the count; **partly fair** means a finding outside the agent's control plausibly
changed the count. Each audit gives its probabilities. Trial names read round, seed, condition: r18-s11-hinted is round 18, seed
11, hinted.

### What decided each trial

<!--FINAL_CAUSES-->
- **Seed 10 hinted** (10): Ten lamps: all 10 stands bought on Thursday, 14 heads joined that afternoon, and the arms taped with bought tape; built on the landing and handed over 13 minutes before the deadline.
- **Seed 11 hinted** (7): Seven lamps from 7 tall holders. Abdelrahman started both shifts in districts with holders for sale and Seb sent him on without a look; after the technician refused, three times, to commit to a further batch of heads, which his facts allowed, Seb also dropped a planned holder search (partly fair).
- **Seed 12 hinted** (9): Nine lamps: every tall stand downtown and in New Maadi bought, with 25 heads joined; Seb never looked in Dokki or Hadayek October, where more stands were.
- **Seed 13 hinted** (13): Thirteen lamps: nine folding stands and four arms taped with bought tape; the ninth lamp was done 26 minutes before the deadline.
- **Seed 14 hinted** (7): Seven lamps on the seven folding stands found. Three metal arms got no lamp: told they needed tape or clips, on sale where both workers stood, Seb tried packaging, paper and rubber bands instead, then built five low cradles.
- **Seed 10 unhinted** (4): Four lamps from the only four USB strips Seb found; he never had a worker walk the downtown streets that held more, and his 12V route ended when the parts were bought 20 seconds before his own Thursday cutoff.
- **Seed 11 unhinted** (0): No lamp: two finished lamps were 2 minutes from the door at 17:00. Seb routed them through a worker's home and a mall with almost no margin, and ordered no batch of heads until Sunday afternoon.
- **Seed 12 unhinted** (0): No lamp: Seb turned down the folding stands and clamp arms on Thursday, then strapped six joined heads to the sides of water bottles, which cannot hold a light over a page.
- **Seed 13 unhinted** (1): One lamp from the only light found, a mall's single USB strip. Seb never looked in Manial, where two shops had strips and stands; the LED shop's referral to the technician next door never came, which may have cost one to three lamps (mostly fair).
- **Seed 14 unhinted** (0): No lamp: Seb designed a USB strip wrapped round a sealed water bottle, which cannot light a page from above, kept it after his worker said the light went round the bottle, and turned down the folding holder.
<!--/FINAL_CAUSES-->

### Acceptance check

The bar was fixed before the final rounds ([docs/AUDIT.md](docs/AUDIT.md#acceptance-bar)).

<!--FINAL_BAR-->
- Findings an audit lists as having changed a count: none. The bar allows findings that only plausibly changed a count, reported with their probability, so a partly fair trial can pass it.
- Counts outside their audited fair range by more than one lamp: none.
- Hinted: the auditors' best estimates of a fair count differ from the actual counts by +0.30 lamps per trial on average (bar: within half a lamp).
- Unhinted: the auditors' best estimates of a fair count differ from the actual counts by +0.19 lamps per trial on average (bar: within half a lamp).
<!--/FINAL_BAR-->

## Claude Opus 5.5 on the frozen version

Rounds c1, c2 and c3 ran Claude Opus 5.5 as the agent, through Claude Code 2.1.311 at medium effort with its web tools turned
off, on the frozen version `v12.0-rc17`: one trial per seed and condition in each round, 30 trials in all. Only the agent side
changed: the agent image installs Claude Code, and the proxy lets it reach api.anthropic.com. The world is the one round r18 ran
(the simulator folder is byte-identical to the r18 release), with GPT-6.1 Sol at medium effort as the world model, the same seeds
10 to 14 and the same hint. Every trial was audited with the r18 audit prompt, by Claude Opus 5.5, and coded for friction with
the r18 guide. The audits are `audits/audit-c1-*.md` to `audits/audit-c3-*.md`.

Round c1 ran on one cloud machine, all ten trials at once; the rerun ran after them. Seed 10 hinted was void (one simulator call
took 20 minutes) and was run again once (†). Before the round, one test trial on seed 10 unhinted measured how much of each plan
a trial uses; it delivered no lamp, was not audited and is not counted. Rounds c2 and c3 ran later on another machine
(`scripts/claude_replicates.sh`, 4 and 5 November): round c2's seed 10 unhinted ran first, alone, to measure usage, and counts as
that round's trial; the other 19 ran ten at a time. None of the 20 was void.

### Round c1

| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 0 † | 0.00 | fair | 0 | 0.00 | fair |
| 11 | 0 | 0.00 | mostly fair | 0 | 0.00 | fair |
| 12 | 8 | 0.89 | not fair * | 0 | 0.00 | fair |
| 13 | 0 | 0.00 | fair | 8 | 0.89 | fair |
| 14 | 0 | 0.00 | mostly fair | 0 | 0.00 | mostly fair |
| **All** | **8** | **0.18** | | **8** | **0.18** | |

\* The auditor labelled this trial mostly fair. By the verdict scale, its finding (about a 60% chance that it cost the ninth lamp) makes it not fair.

### Round c2

| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 0 | 0.00 | fair | 0 | 0.00 | mostly fair |
| 11 | 7 | 0.78 | fair | 2 | 0.22 | fair |
| 12 | 6 | 0.67 | fair | 2 | 0.22 | partly fair |
| 13 | 12 | 1.00 | fair | 0 | 0.00 | fair |
| 14 | 5 | 0.56 | fair | 3 | 0.33 | fair |
| **All** | **30** | **0.60** | | **7** | **0.16** | |

### Round c3

| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 0 | 0.00 | fair | 2 | 0.22 | fair |
| 11 | 7 | 0.78 | fair | 3 | 0.33 | fair |
| 12 | 9 | 1.00 | fair | 8 | 0.89 | fair |
| 13 | 12 | 1.00 | fair | 0 | 0.00 | fair |
| 14 | 3 | 0.33 | fair | 5 | 0.56 | fair |
| **All** | **31** | **0.62** | | **18** | **0.40** | |

### All three rounds

Claude delivered 69 lamps in the 15 hinted trials and 33 in the 15 unhinted ones. The mean of the seed means is 0.47 with the
hint (95% bootstrap over seeds, keeping each seed's three trials together, 0.19 to 0.71) and 0.24 without it (0.14 to 0.33). The
hint gap is +0.22 (+0.03 to +0.41): the hint was ahead on seeds 11, 12 and 13, behind on seed 10 and level on seed 14. Round c1
alone gave a gap of 0.00; rounds c2 and c3 gave +0.44 and +0.22. Repeats of the same task vary a lot:
49% of the variance in hinted scores and 88% of that in unhinted scores lies between the three trials of a seed. Three hinted
trials reached the target (12, 9 and 12 lamps), none in c1; no unhinted trial did. On the same version and seeds GPT-6.1 Sol
scored 0.91 hinted and 0.11 unhinted (the final round above). `paper/claude_rounds.py` and `paper/rounds_stats.py` compute these.

### What decided each Claude trial

Round c1:

- **Seed 10 hinted** (0): Twenty good heads were made at the technician on time, but no stand was tall enough. Seb never had a worker search Dokki, Manial or Maadi Degla, which had tall holders, and at 15:06 Sunday approved the five low cradles it had turned down at 13:41.
- **Seed 11 hinted** (0): Seven units on tall holders, each head held on with rubber bands, so the head slid when a unit was carried. Seb asked for cable ties and foam tape, which no shop in this world sells, named electrical tape late and in a district without it, and never used the modules' own adhesive backs.
- **Seed 12 hinted** (8): Eight lamps on every tall holder in Bab El Louk, plus six units on low cradles that could not count. Seb never tried Dokki. On Sunday a worker stood in a New Maadi shop that had one more tall holder and left at Seb's 13:30 cutoff without being shown it (not fair by the verdict scale, although the auditor labelled it mostly fair; the audit puts the chance that this cost the ninth lamp at about 60%).
- **Seed 13 hinted** (0): Thirteen units on folding stands, every one built on a round LED board whose voltage the facts leave unknown. Seb decided from the board's layout that it was 12V and dropped its own rule that a sample must light before the batch was bought, so the grader counted none. The shop also sold 12V modules, but the worker's first ask failed and Seb's follow-up asked only about the board. In October the same unrated board cost one of the real manager's workers 2.5 hours.
- **Seed 14 hinted** (0): Three metal arms bought, and no district searched beyond downtown, the mall and one Maadi street. No worker sent for tape until 16:11 Sunday, and heads and stands apart until 16:03, so assembly began at 16:55 (mostly fair; about a 20% chance that a faster finish would have added a lamp).
- **Seed 10 unhinted** (0): Two USB strips wound on low cradles, which Seb knew were low. Tall stands were sold in Dokki and Manial, where one worker started each shift; Seb sent him elsewhere both times.
- **Seed 11 unhinted** (0): The world's only USB strip that needed no wiring, mounted on a low cradle. Seb had turned down the tall stands a worker found in New Maadi, and never found the 12V route.
- **Seed 12 unhinted** (0): Eight strips on low cradles. The workers reported tall folding holders three times on Thursday, and Seb declined them.
- **Seed 13 unhinted** (8): Twenty strips ordered online on Thursday and every tall holder in two Maadi Degla shops bought on Sunday. More tall stands were in districts never searched, among them the district where each worker started a shift.
- **Seed 14 unhinted** (0): Six strips round low cradles after a 548 EGP metal arm was turned down as too dear. A worker reported that the light sat as low as the cradle, and Seb had the rest built the same way (mostly fair; a district missing from the facts stalled one worker, judged very unlikely to matter).

Round c2:

- **Seed 10 hinted** (0): All 14 heads were made and tested by 14:16 Sunday, but no tall stand was bought. Seb searched downtown, the delivery area, Carrefour and the City Centre mall, which have none, and at 15:39 fell back on New Maadi's five low cradles. Tall stands were in Manial (one worker's Sunday start), Maadi Degla and Dokki (his Thursday start).
- **Seed 11 hinted** (7): Seven tall stands, all that downtown and New Maadi held, each made a lamp. Dokki and Manial, the workers' start areas, held 11 more and were never searched. Eight more units went on low cradles that Seb itself had called too low.
- **Seed 12 hinted** (6): Six metal arms with technician-joined heads, all the arms in the shops visited. Seb turned down 13 tall folding holders in three shops as "low" without asking their height, the mistake the hint warns against; six heads and about 1,000 EGP went unused.
- **Seed 13 hinted** (12): All four metal arms at El Tamimi and all eight folding stands in New Maadi, with technician-joined heads.
- **Seed 14 hinted** (5): Five tall structures, every one in New Maadi, Bab El Louk and the delivery area, and five more units on low cradles that Seb had rejected on Thursday as "much too low". Dokki, Hadayek October and Abbasiya were never searched.
- **Seed 10 unhinted** (0): No structure bought. Seb searched downtown, Ataba and Carrefour, which have none, and bought only two strips (mostly fair; about a 15% chance that the worker who started Sunday in Manial, where two counters sold folding stands, would have found two had the simulator played the shop check Seb asked for).
- **Seed 11 unhinted** (2): One ready USB strip in reach (Carrefour, its only one) and one step-up cable at RAM. Seb never had the worker ask the other Bab El Louk shops that stock the cable.
- **Seed 12 unhinted** (2): Only two strips found in shops; eight folding stands bought and eight strips ordered online, cash on delivery, due Sunday. The world model never chose an arrival time and ruled about 20 times that the parcel had not yet arrived, until Seb cancelled at 16:25 (partly fair; the audit puts the chance that this cost lamps at 0.40). The district the workers walked on Thursday also had a shop with six strips that the simulator did not route them to and Seb never asked for (0.15).
- **Seed 13 unhinted** (0): Five units on Carrefour's low cradle, bought after Seb itself had called it too short, and after it had turned down 500 EGP metal arms on Thursday as too pricey. Only five heads were funded before a cutoff Seb set itself.
- **Seed 14 unhinted** (3): All three metal arms of the one downtown shop that had them; four strips went unused. Tall stands in Dokki and New Maadi, the workers' start districts, were never searched. Seb also misread the time zone on Thursday and sent the workers home an hour before the shift ended.

Round c3:

- **Seed 10 hinted** (0): Five units on low cradles that Seb knew were low. Seb never searched Dokki or Manial, where the workers started, and at 13:03 Sunday turned down a worker's offer to search Manial, where two shops sold tall stands.
- **Seed 11 hinted** (7): Seven tall stands, all that downtown and New Maadi held. Dokki and Manial, the start areas, held 11 more; 17 tested heads were left over.
- **Seed 12 hinted** (9): Nine folding stands with technician-joined heads.
- **Seed 13 hinted** (12): All four metal arms and all eight folding holders in the shops visited.
- **Seed 14 hinted** (3): Three stands. Seb turned down two folding stands at 14:21 and never searched Dokki, Abbasiya or Hadayek October; 15 heads were delivered as spares.
- **Seed 10 unhinted** (2): Four strips but two stands. The searches went to Bab El Louk, Ataba and Carrefour, which have none, and one Maadi Degla counter had two folding holders. Seb stopped buying lights once stands could not be found.
- **Seed 11 unhinted** (3): Three lamps on the three telescopic stands downtown and five more units on low cradles that a worker had reported as under 15 cm. New Maadi and Manial, the workers' start places, held more tall stands.
- **Seed 12 unhinted** (8): All eight strips and all eight holders in Bab El Louk. The ninth lamp needed one more of each, sold in Abbasiya, New Maadi and Dokki; on Sunday a worker re-checked shops already known to be empty.
- **Seed 13 unhinted** (0): Eighteen modules and jacks bought with no technician lined up. The LED shop referred assembly to the technician next door, and a worker stood in that shop with all the parts, but Seb asked only about stock. On Sunday Seb relied first on the workers wiring, which they refuse, then on finding a technician in Maadi, where the facts list none that will do it.
- **Seed 14 unhinted** (5): Six strips and five tall stands. Seb never searched Dokki, Abbasiya or the other Bab El Louk shops that had more, and redirected Thursday's light search to Ataba, which the facts do not model, and to stationery.

Stands set the count in 22 of the 27 trials that fell short of nine lamps: too low, too few, or, in c1 seed 11 hinted, not
fastened. Of the other five, two ran out of lights (c2 seeds 11 and 12 unhinted), one lacked a ninth light and a ninth stand (c3
seed 12 unhinted), one never had its heads joined (c3 seed 13 unhinted), and one built every unit on a board of unknown voltage
(c1 seed 13 hinted). Most often Seb searched two or three districts, bought every tall stand they held, and never sent a worker
to the districts with more, often the ones where a worker started the shift. The hint warns that each shop stocks only a few
stands and that nearby shops may have none, but does not say where else to look.

### Acceptance check

Round c1:

- Findings that probably changed a count: one, so this round does not meet the bar's first condition. The seed 12 hinted audit
  lists a finding at about 0.6; the verdict scale calls a finding that probably changed the count "not fair", and we report the
  trial as not fair, although the auditor labelled it mostly fair. The log
  confirms the finding: the shop had one tall holder at 181 EGP, and after a drawn worker mistake and five minutes of a
  seven-minute inquiry the worker left without learning of it.
- Counts outside their audited fair range by more than one lamp: none.
- Hinted: the auditors' best estimates of a fair count differ from the actual counts by +0.42 lamps per trial (bar: within half
  a lamp).
- Unhinted: -0.01 lamps per trial.

Rounds c2 and c3 meet all three conditions:

- Findings that probably changed a count: none. The largest is the c2 seed 12 unhinted parcel (0.40, so partly fair). The log
  confirms it: from Sunday 12:45 the world model's notes say again and again that the courier time remains unselected.
- Counts outside their audited fair range by more than one lamp: none.
- Best estimates minus actual counts, per trial: c2 hinted -0.06, unhinted +0.42; c3 hinted -0.10, unhinted -0.02.

### Coverage, friction and cost

All 30 trials:

- **Coverage** (`paper/coverage.py`): of the world-log entries that name a specific business, 90.5% in the hinted trials (50%
  to 98% per trial) and 85.1% in the unhinted ones (50% to 100%) name only businesses from October, against 93.7% and 90.1% for
  GPT in r18. Round c1 alone: 88.2% and 85.3%.
- **Friction** (`paper/friction_check.py paper/friction_coded_claude`): the kinds the world decides came out close to GPT's
  round. A wrong counter claim 12 of 44, a failed first ask 925 of 1060, custom electrical work 21 of 66, a slipped technician
  promise 11 of 43 (mostly the LED shop's within-the-hour offer, as in r18), long rides late 140 of 141 (median 1.60 times the
  quote), and no failed join in 71. Two kinds depend on the agent and differ: remote calls and emails gave a usable quote 2 times
  in 217 (GPT: 14 of 251), and Seb asked for a new photo or a follow-up on 34 of 873 photos (GPT: 47 of 330; October 9 of 53).
- **Agent cost** (`paper/agent_round.py`): Claude Code's own API-equivalent totals were $2.88 to $12.46 per trial, a mean of
  $3.90 with the hint and $6.34 without it. Cached input ran to 7 to 42 million tokens and output, thinking included, to 29 to
  92 thousand, against 77 to 109 million and 109 to 623 thousand for GPT. A trial took 1.0 to 2.6 hours of wall time. Between
  shifts the agents waited on a background timer. Both the agent and the world model ran on subscription plans, so these are not
  amounts paid.

## The target is reachable on every seed

A target is fair only if it can be reached on every seed. The highest count reached in a trial audited fair or mostly fair in
rounds r13 to r18, all under the one-object lamp rules. The fastener rule was tightened in rc16 so that a stand's own clamp no
longer counts; the lamps in these trials stood on folding holders with the module's adhesive or on arms with tape, so they meet
it too. The target of 9 was fixed after round r12 and is now conservative:

<!--REACH_TABLE-->
| Seed | Highest count shown | How |
|---|---|---|
| 10 | 10 | r18-s10-hinted (hinted, audit: fair) |
| 11 | 14 | r16-s11-hinted (hinted, audit: fair) |
| 12 | 13 | r16-s12-hinted (hinted, audit: fair) |
| 13 | 13 | r18-s13-hinted (hinted, audit: mostly fair) |
| 14 | 10 | r13-s14-hinted (hinted, audit: fair) |
<!--/REACH_TABLE-->

## Earlier rounds on the same design

<!--EARLIER-->
### Round r16 (v12.0-rc15)

Version rc15, fully audited. Its audits found four general issues, all fixed for the final round: a stand's own clamp counted as the clips that hold a part (seed 13 hinted, partly fair); workers hosted each other at home though the real worker refused; drawn worker mistakes were sometimes merged or skipped; and they were played as the cheapest kind.

| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 7 | 0.78 | fair | 0 | 0.00 | fair |
| 11 | 14 | 1.00 | fair | 1 | 0.11 | fair |
| 12 | 13 | 1.00 | fair | 0 | 0.00 | fair |
| 13 | 12 | 1.00 | partly fair | 8 | 0.89 | mostly fair |
| 14 | 10 | 1.00 | mostly fair | 3 | 0.33 | fair |
| **All** | **56** | **0.96** | | **12** | **0.27** | |

Mean score 0.96 hinted and 0.27 unhinted.

<details><summary>What decided each trial</summary>

- **Seed 10 hinted** (7): Seven lamps from the seven stands found in Dokki on Thursday; Seb never looked for more. Three metal arms bought for 1,500 EGP got no lamp: Seb bought nothing to hold the module on them.
- **Seed 11 hinted** (14): Fourteen lamps: 14 stands from four shops and 19 heads joined by the technician over three days; the last lamp was done 32 minutes before the deadline.
- **Seed 12 hinted** (13): Thirteen lamps: every folding holder in Dokki and Bab El Louk bought and 18 heads joined; the holders set the count.
- **Seed 13 hinted** (12): Twelve lamps, seven of them on arms whose own clamps held the module with nothing applied, which the facts did not allow (partly fair; fixed in rc16). The five folding-stand lamps are solid.
- **Seed 14 hinted** (10): Ten lamps: seven on folding stands and three on arms held with rubber bands, the last finished 70 seconds before the deadline.
- **Seed 10 unhinted** (0): Seb designed a card tent with its ridge at 16-17 cm and no room to write under it, kept it after a worker said it was tight for a hand, and turned down the 180 EGP folding holder.
- **Seed 11 unhinted** (1): One lamp. Seb approved seven low fixed phone stands that cannot light a page from above; three of four heads went on them, and his changing cutoffs at the technician limited the heads.
- **Seed 12 unhinted** (0): No lamp: Seb bought bare-lead 12V modules that need a technician, refused the one technician offered on Thursday, and on Sunday searched only where there is none.
- **Seed 13 unhinted** (8): Eight lamps: bought one shop's whole stock of 8 modules, had them joined, and matched 8 stands; Seb told the worker not to look for more.
- **Seed 14 unhinted** (3): Three lamps on the only three tall arms Seb bought; he turned down the other arms and folding stands on Thursday and tried a low cradle and a bottle on Sunday, which cannot hold a light over a page.

</details>

### Round r13 (v12.0-rc10)

Version rc10, fully audited. Four unhinted trials were re-run after a sign-in outage (marked †). Two trials are partly fair: a grading threshold the agent could not see, and an unusually short last walk to the door; both were fixed in rc11 and rc12.

| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 7 | 0.78 | mostly fair | 1 † | 0.11 | mostly fair |
| 11 | 14 | 1.00 | mostly fair | 4 † | 0.44 | partly fair |
| 12 | 11 | 1.00 | mostly fair | 0 † | 0.00 | partly fair |
| 13 | 9 | 1.00 | fair | 0 | 0.00 | mostly fair |
| 14 | 10 | 1.00 | fair | 4 † | 0.44 | fair |
| **All** | **51** | **0.96** | | **9** | **0.20** | |

Mean score 0.96 hinted and 0.20 unhinted.

<details><summary>What decided each trial</summary>

- **Seed 10 hinted** (7): Stands set the count: all 7 folding stands in Dokki carried 7 of 18 heads. The shop's clamp arms, which Seb asked about, were never reported to him.
- **Seed 11 hinted** (14): Fourteen lamps: heads joined on Thursday, every stand in Dokki bought, and Sunday's assembly run to the last minutes.
- **Seed 12 hinted** (11): Eleven lamps, assembled on the landing. The budget was spent by Thursday afternoon, so the clamp arms, which need tape or clips, mostly stayed unused.
- **Seed 13 hinted** (9): Nine lamps from folding stands and heads joined on Thursday; a rubber-band mount on a clamp arm failed, and Seb stopped the arm work.
- **Seed 14 hinted** (10): Ten lamps: every tall stand the workers found carried a head joined on Thursday, assembled on the landing with time to spare.
- **Seed 10 unhinted** (1): Seb called the 180 EGP stands too expensive and bought one, as a prototype. With four light strips and one tall stand, one lamp, finished at 16:54; boxes, bottles and low cradles failed as the facts say.
- **Seed 11 unhinted** (4): Four strip lamps handed over at 16:59:32, after a walk from the mall the simulator set at 5 minutes where other runs took 8 to 15 (partly fair, on the easy side).
- **Seed 12 unhinted** (0): Eight working lamps rejected: the light sat at 18 cm and the grading standard, which the agent could not see, said about 20 cm (partly fair; fixed in v12.0-rc11).
- **Seed 13 unhinted** (0): Rejected the folding stand twice; its one unit was a closed A3 card box barely wider than an A4 sheet, lit from an 18 cm roof, with little room for a hand (not counted; 1 lamp in doubt); never returned to the LED shop it had found on Thursday.
- **Seed 14 unhinted** (4): Four lamps from USB strips on folded card panels. Seb bought only four card sheets and cancelled the stop that had more, and looked for no strips beyond the six he found on Thursday.

</details>

### Round r12 (v12.0-rc9)

The same design one version earlier, also fully audited. Version rc10 added: a unit must be one object; parts are held only by listed attach methods or bought fasteners; shops next to each other are 1-2 minutes apart; each shift starts at the facts' start place; outputs naming an unknown worker go back to the simulator; workers may finish assembly outside the client's door.

| Seed | Hinted lamps | Score | Audit | Unhinted lamps | Score | Audit |
|---|---|---|---|---|---|---|
| 10 | 7 | 0.78 | fair | 0 | 0.00 | fair |
| 11 | 1 | 0.11 | fair | 0 | 0.00 | fair |
| 12 | 11 | 1.00 | fair | 5 | 0.56 | mostly fair |
| 13 | 10 | 1.00 | mostly fair | 1 | 0.11 | mostly fair |
| 14 | 5 | 0.56 | fair | 3 | 0.33 | mostly fair |
| **All** | **34** | **0.69** | | **9** | **0.20** | |

Mean score 0.69 hinted and 0.20 unhinted.

<details><summary>What decided each trial</summary>

- **Seed 10 hinted** (7): Bought all 7 folding stands in Dokki, plus 3 tablet arms that never got a head: Seb forbade tearing tape and never looked for clips.
- **Seed 11 hinted** (1): Spent 6,361 EGP by Thursday evening, 2,000 of it on clamp arms never used. Too little was left on Sunday for a car to bring the 13 finished heads from the technician.
- **Seed 12 hinted** (11): Ordered 18 heads on Thursday, bought all 14 stands in reach, carried everything to one place on Sunday and finished six lamps at the door.
- **Seed 13 hinted** (10): Ordered 14 heads on Thursday and at 16:14 Sunday sent every part in one car to finish by hand at the door. The tenth lamp was accepted two seconds before the deadline.
- **Seed 14 hinted** (5): 13 heads joined but only 5 stands bought: Seb cancelled the Dokki stand search and sent nobody to other districts.
- **Seed 10 unhinted** (0): One lamp built at Mostafa's home, 30 minutes from the address. Seb's plan had the workers meet only at 16:33, and the lamp was still on the way at 17:00.
- **Seed 11 unhinted** (0): Seb ruled out the 12V module route on Thursday and turned down every tall stand as too dear. No unit was ever assembled.
- **Seed 12 unhinted** (5): Found the joining route without the hint; on Sunday a walk found the technician next door. Five module lamps, the fifth received 15 seconds before the deadline.
- **Seed 13 unhinted** (1): Chose Abbasiya over the downtown electronics street and bought 1,682 EGP of parts before any technician agreed. One strip lamp, accepted 57 seconds before the deadline.
- **Seed 14 unhinted** (3): Bought 3 USB strips on Thursday and never looked for more. Three lamps, each one strip bridged between two folding stands.

</details>
<!--/EARLIER-->

## How the final version came about

Round r16 ran v12.0-rc15, which carried every fix from r13's audits (grading judges the lit area, not an exact height; the
simulator never uses the grading standard to decide what happens; a fixed walk from the mall to the door; outages and rate limits
pause a trial instead of changing it; void trials are run again). All ten r16 trials were audited: 7 fair, 2 mostly fair, 1
partly fair. The audits found four general issues, fixed in rc16 and rc17 before the final round:

- A stand's own clamp counted as the clips that hold a part (r16-s13-hinted, partly fair). A stand's attach value now names a
  fastener someone must apply; its own holder or clamp is never one.
- Workers hosted each other at home for assembly, though the real Mostafa refused exactly that. A worker may now work alone at
  his own table but does not host the other.
- The simulator sometimes merged a newly drawn worker mistake into one already running, or skipped it.
- Left to choose, the simulator played drawn mistakes as the cheapest kind, late reports. The server now draws the kind too, at
  the record's mix of misreads, wrong turns and unannounced route changes.

Round r18 ran rc17. During it, the host computer slept for 26 minutes (18:59-19:25 PDT on 26 October). The project clock treats
such a pause as frozen, so no agent lost project time; two simulator steps that failed during the pause (one in each seed 13 trial) were retried afterwards,
and some agents reconnected to the model on their own. Each audit of the final round checked whether anything the agent saw from
the pause changed a decision.

## Limits

<!--LIMITS-->
- **The technician sometimes balks at a multi-day batch his facts allow.** His facts let him join up to a set number of heads
  a day on any open day, keep finished work for pickup, and keep his promises. In seed 11 hinted he refused three times to commit
  to a further batch for Friday and Saturday, and the agent then dropped a planned stand search (partly fair; fair count 7 to 11,
  about a 45% chance it cost lamps); in seed 10
  unhinted he hedged the same way, with no effect. The same seed in r16 got the work.
- **A referral sometimes does not come.** The LED shop's facts end its answer with a referral to the technician next door. In
  seed 13 unhinted it never came, and a worker's walk down the same street did not find him (mostly fair; about a 25% chance it
  cost one to three lamps). Every other recent run on this seed that asked there got it.
- **Small liberties with the facts.** A client brought delivered lamps back out for a re-check (seed 12 hinted) and accepted
  loose stock after the deadline (seed 12 unhinted); a technician's 8-minute busy wait was skipped once (seed 14 hinted); the LED
  shop's 25-minute runaround was cut to 4 minutes once (seed 10 hinted); and a worker was sent back to an empty shop once (seed
  12 unhinted). Whether a technician cutting tape strips (seed 13 hinted) is a favour, two audits disagree. None changed a count.
- **Some worker mistakes still cost little.** The server now draws each mistake and its kind at the record's rates and mix, and
  most cost real time. Some land where nothing depends on them, for example a misread that a message already on its way
  corrects. The auditors put this well under one lamp per trial.
- **Mistake counts vary.** The draws use the seed's random stream, but different plans change when the draws fall, so this round
  drew between 5 and 9 mistakes per trial against about 8 expected, including 5 and 9 on the two trials of seed 14.
- **Travel times at the edges of their ranges.** Rides sometimes ran at the slow end of the facts' ranges, and one loaded walk to
  the door took 15 minutes against the facts' 8-12. None changed a count.
- **Chains have only the branches the record shows.** IKEA exists only at its 6th of October branch. In round r16, two
  agents that sent a worker to the Cairo Festival City branch lost 20-40 minutes and no lamp, since IKEA had no suitable light in
  stock.
- **Small timing margins.** Some results turned on minutes: in seed 11 unhinted two finished lamps were 2 minutes from the door
  at 17:00, and in seed 13 unhinted the only lamp arrived with 3 minutes to spare. A slightly different pace could change them.
- **Photos.** The photo library often shows a different scene than the worker's text (every audit noted it), for example a lit
  lamp that was never powered. The agents usually asked and the workers corrected it, but in seed 10 hinted a worker vouched for
  a wrong photo, which helped send the agent on a 40-minute detour. No count changed.
- **Saved world logs end when the agent stops.** The world folder saved with each trial is a snapshot from the end of the agent's
  run. The world's last steps (rides home after 17:00) and the grade call are only in the grading export file
  (`verifier/export.json`), which holds the grade with its evidence for each lamp.
- **Ledger edge cases.** A spend notice closes on its first payment report, so a second payment against it is refused (the agent
  then sends a new notice). Open notices can reserve more than the budget in total (once 7,656 EGP against 7,000), though no
  payment ever exceeded it. Rides home after 18:00 are recorded at 18:00, or left out of the spend figure if still unpaid when the
  run closes (in five trials; seed 12 unhinted spent about 3,350 EGP, not the 3,051 shown).
- **The host computer slept for 26 minutes during the round.** The project clock treated the pause as frozen; two simulator steps
  (one in each seed 13 trial) were retried after it, and some agents reconnected to the model. Every audit checked whether the pause changed a decision; none
  did.
- **One world-model family.** GPT-6.1 Sol plays the world and is the main agent under test. One round with Claude Opus 5.5 as
  the agent (above) found the kinds of friction the simulator decides at rates close to GPT's, but one round cannot rule out a
  smaller family effect, and in that round Claude Opus 5.5 also wrote the audits.
<!--/LIMITS-->

## History

Every earlier round and every fix, with the trial that showed the problem, is in [docs/HISTORY.md](docs/HISTORY.md).
