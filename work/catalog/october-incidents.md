# October 2026 Memphis run: friction and incident reference

Purpose: give the world simulator realistic friction at realistic rates. Every claim cites chat ids (`in-`/`out-`), photos (`file-`), spend requests (`spend-`) or manager-transcript timestamps (`tx Sun04 16:38`). All times are Cairo time (UTC+3). `~` marks an estimate. `[?]` marks something the record does not settle.
Sources: worker-chats.txt + english-translations.json (798 messages: 440 from Seb or the bot, 358 from workers), agent-transcript.txt, spend_requests.json (33 requests), workers.json.

## 0. Headline numbers
- 2 workers, 19 shift-hours each. Mostafa (worker-a) is based in New Maadi and sometimes in Ashgar City, Giza (in-000007, in-000444). Abdelrahman (worker-b) lives in Ashgar City, 6th of October (in-000442, in-001089).
- Result: 2 lamps. B001 is a 180 EGP phone stand with a technician-made head, tested Oct 5 (in-000508). A001 is a hand-folded card body with a Panatek head, lit Oct 7 at 15:45 (file-001157, file-001174). Delivery itself is not in the chat. The last worker lines are "shall we go to the delivery place?" (in-001200) and "let's go now to the address" at 16:25 (in-001211). The count of 2 comes from the brief.
- Money: 33 spend requests reserved 8,880 EGP against the 7,000 budget. The bot recorded 3,045 EGP as paid. 14 requests were still "committed" and never reported (spend_requests.json).
- Documented real spend (paid or quoted) is about 5,370 EGP [~]:
  - transport, including a 95 EGP courier: about 3,940 (73%)
  - electrical parts: 430
  - technician labour: 650
  - lamp bodies: 350
  - Several of Abdelrahman's outbound fares and Mostafa's Oct 5 return were never reported, so true transport is higher.

## 1. Outcome timeline (lamps = built and worker-tested; delivery could only happen Oct 7)
| Shift | Parts and purchases | Technician work and heads | Bodies and lamps | Lamps at end |
|---|---|---|---|---|
| Thu 1 Oct 14-17 | Mostafa phoned 2 shops in 15 min (in-000022) and travelled to Lampatronics (290 EGP, in-001018). The "5V Type-C 6-LED board" turned out to be unrated with no connector (in-000108, in-000123). He bought it anyway for 20 EGP (in-000132); it was never used. Abdelrahman: pipe and fittings failed (in-000019, in-000048); a 500 EGP metal stand was rejected (in-000060). | None. Seb cancelled the planned meeting of the two workers (out-000144). | Bought a 180 EGP folding phone stand, the future B001 body (in-000074, file-000095). The shop had only 5 in stock (in-000128). | 0 |
| Sun 4 Oct 13-17 | Phone round: Metanoia: technician in 3 days (in-000203). PCBZone: technician on leave (in-000220). Electrolik: no answer (in-000230). Nori: did not understand (in-000207). Most: "see the website" (in-000335). Abdelrahman bought module + DC jack + USB 5→12V cable for 58.50 EGP using exact part codes (out-000332, file-000372). | Fares PCB visit: 21-day design, not their service (in-000301, in-000317). Lampatronics said it could install in under an hour (in-000348), then refused (in-000375). Harby Tech next door joined and insulated the parts in about 12 min for 50 EGP (in-000390, file-000400). Mostafa's PCBZone visit produced only a "Wednesday night or Thursday" offer (in-000435). | Head #1 prepared, not yet powered. | 0 |
| Mon 5 Oct 13-17 | Lampatronics had the parts but no technician (in-000470). Seb authorised up to 25 sets (out-000537). Mostafa bought 6 sets for 351 EGP; the invoice came at 18:49, after the shift (file-000625). Why 6 was never stated (out-000628). | No technician work. Seb told Mostafa not to wait for one (out-000569, out-000588). | Head lit at 13:20 (file-000432). Mounted with factory adhesive at 13:37 (file-000453). Ran over 20 min (in-000490). Stable and readable at 14:27 (in-000508): **B001**. Abdelrahman's stationery search for a card body found nothing (in-000606, in-000648). | 1 |
| Tue 6 Oct 13-17 | 300 g 100×70 ribbed sheet + 19 mm clips + ruler for 170 EGP (in-000672, in-000811). A3 300 g not available (in-000839). | Mostafa rode New Maadi → Panatek (6th of October): 865 EGP round trip (in-000922, in-000929). Price 100 EGP per head (in-000732); 600 EGP paid that day (in-000915, in-000977). Handover estimate 16:45 (in-000813). He left without the heads (in-000871, in-000899). | Folded body stood at 28 cm by 16:24 after 4 photo corrections (in-000824, in-000832). | 1 |
| Wed 7 Oct 13-17 | No money left for more bodies: Seb said available was 0 at 15:38 (out-001148). No free boxes nearby (in-001134), no hard covers (in-001185). | Technician finished overnight. A courier brought the heads to Mostafa's home for 90-95 EGP at 14:53 (in-001023, in-001063, in-001082). The photo shows 3 modules; the head count was never given (file-001085, out-001094). | Workers met at Courtyard Maadi about 15:17-15:40 (in-001119, in-001140). **A001** lit at 15:45 (file-001161), stood alone over a page at 15:49 (file-001170), and was lit beside B001 at 15:52 (in-001180). Seb's run halted at 16:07 (out-001198). Workers left for delivery at 16:25 (in-001211). | 2 |

Left unused: at least 2 and up to 5 prepared Panatek heads (6 paid, 3 modules in file-001085), plus the 20 EGP board.

## 2. Incident table: world and worker friction
Rates are counted from the record. Small samples: treat them as a centre value with wide error bars.

### 2a. Suppliers and technicians
| Kind | n | Typical cost | Example ids | Simulator rate |
|---|---|---|---|---|
| Supplier misinformation: a phone or counter claim about spec or capability proved wrong when acted on | 4 clear + 1 doubtful, of ~9 checkable claims | 30 min to 2.5 h of one worker; 0-380 EGP in trips; once 20 EGP of dead stock | in-000022→in-000123 (Oct 1 board: 2.5 h, 290 EGP); in-000282→in-000435 (PCBZone "come in": ~1h45, 379 EGP); in-000348→in-000375; in-000259→in-000317; [?] in-000721 "no shipping" vs courier in-001063 | About 1 in 2 capability or spec claims made by phone or at the counter are wrong. Prices are reliable (2d). |
| Request not understood without a picture or part codes | 4 of ~6 first contacts about the custom head | 10-40 min each | in-000149, in-000207, in-000282, in-000335. Fixed by a diagram (out-000226) or part codes (out-000332 → right parts first time, file-000372) | About 2 in 3 first contacts fail on a vague spec. Exact part codes or a link fix it about 1 in 1. |
| Out of stock, wrong spec, too dear, or limited quantity at the first shop | ~12 misses vs ~7 hits | 5-30 min per miss; one detour cost 75 min + 420 EGP (in-000562, in-000616) | in-000019, in-000028, in-000048, in-000060, in-000128 (5 units only), in-000566, in-000606, in-000678, in-000839, in-001134, in-001185; [?] 6 of 25 sets (in-000626) | About 2 in 3 first asks for a specific item fail. A substitute usually turns up at the 2nd or 3rd shop within 15-60 min. Bulk stock of a given item is often single digits. |
| Defective or unusable part | 2 | 15 min; 20 EGP | in-000076 (last stand broken, not bought); in-000123 (board unrated) | About 1 in 10 items inspected or bought. 0 of 7 coded electrical sets showed a fault (only 2 were ever powered). |
| Technician lead time beyond the 4-day horizon, or "not our service" | 6 of 8 shops approached for head prep | 15-60 min per shop | in-000203 (3 days), in-000301 (21 days), in-000435 (Wed/Thu), in-000196, in-000317, in-000470, in-000230 (no answer) | Only about 1 in 4 shops will do small custom electrical work within 1-2 days. Successes: Harby Tech (in-000390), Panatek (in-000698). |
| Technician time promise slipped or broken | 3 of 5 promises | Same-day slip of 30-60 min; slipping past shift end pushes pickup to next day (+22 h here) | in-000348→in-000375 (broken after 27 min); in-000405 ("10 min" → after shift, in-000435); Panatek 16:00 target → 16:45 (in-000813) → handed over 14:53 next day (in-001082). Kept: in-000390 (~12 min), courier in-001023→in-001082 (55 min vs 60-90 promised) | About 1 in 2 technician time promises slip. |
| Technician work defects: failed joins, wrong polarity | 0 observed | none | Both heads that were powered lit first time (file-000432, file-001157). The other Panatek heads were never powered, and their count was never confirmed (out-001094). | Record shows 0 of 2. There is no basis for a high rate. |
| Supplier remote channels dead: Seb's own calls, emails and forms, Oct 1-3 | ~9 calls with 0 quotes; ≥5 email bounces; 4 forms blocked or erroring; 1 supplier had closed | Off-shift only; 3 days with no usable quote | tx Thu01 14:03, 14:49, 16:17, 16:33, 20:36; Fri02 10:10, 11:13; Sat03 18:09; Mon05 08:31; Fri02 15:12 (Cupindy closed) | About 0 usable quotes from ~30 remote attempts. Every actionable fact came from workers' calls and visits (e.g., in-000022). Part of this is harness friction (see 3b). |

### 2b. Movement and place
| Kind | n | Typical cost | Example ids | Simulator rate |
|---|---|---|---|---|
| Car ride slower than the app ETA | 4 of 6 timed trips | +30 to +45 min (1.5-2x the app estimate) | Oct 1: ETA 15:11 (out-000047) → about 15:45 (in-000084, in-000103). Oct 5: 47 min quoted (out-000488) → about 85 min (in-000572, in-000586). Oct 6: 15:21 ETA (out-000723) → about 15:55 (in-000783). Oct 7: 39 min quoted (out-000938) → about 83 min with a reroute (in-000999→in-001119). On time: in-000279→in-000289 (14 min). | Long cross-Cairo legs: x1.5-2. Short hops: on time. |
| Ride-app failure | 1 of ~16 rides | 35 min late departure | in-000513 | About 1 in 15 rides. |
| Navigation or location trouble | ~5 | 3-40 min | in-000309→in-000353 (PCBZone location, ~38 min); in-000292→in-000295 (entrance, 3 min); in-000658 blank pin (out-000664); in-001080/in-001089 vs in-001099 (meeting confusion); PCBZone address only "Giza" (out-000344) | About 1 per worker-day of travel, usually under 10 min. |
| No usable workspace | 3 | ~40 min search; once blocked home assembly | out-000691 → in-000748 → in-000773 (table found 15:33); in-001032 (home unusable); in-000462 (compound, no stationery shop) | A worker away from home lacks a table about 1 in 2 times. A free public venue was found once (in-001054). |
| No mobile signal inside a shop | 2 of 2 Lampatronics visits | Silences of up to ~2 h; a purchase made after cancellation | in-000132, in-000532 → in-000626 | Per shop. Make it sticky for that venue. |

### 2c. Worker behaviour
| Kind | n | Typical cost | Example ids | Simulator rate |
|---|---|---|---|---|
| Misunderstanding an instruction or concept | a: 5, b: ~10 | 2-15 min, fixed by one explanation or diagram; worst case ~75 min | a: in-000209, in-000321, in-000022 (Type-C), in-000543, in-000754. b: in-000019 (~15 min), in-000492, in-000556, file-000791 (4 rounds, ~37 min of folding), in-000963, in-001101 | a: 0-2 misreads per new concept. b: needs a verbatim script per new supplier type, and 33 of 216 messages ask "what now / should I go" (in-000189, in-000501). |
| Overstay past 17:00 on an open errand | a: 3 of 5 shifts | +35 min (in-000435); about +110 min (in-000610, in-000629); on the road at 17:01 (in-000871) | despite out-000408, out-000588, out-000604 | a: 0-110 min on any errand still open near shift end. b's rides home end after 17:00 because home is far (file-000614). |
| Paying over cap, without a reservation, or after cancellation | 4 (+1 pricier ride choice) | 10-79 EGP each | in-000132 (20, after cancel); in-000435 (379 vs 300 cap); in-001128 (260 vs 250); in-001183 (45, unreserved); in-000725 (Wasalny +71 vs Flex, within cap) | About 1 in 5 paid events; always small. |
| Unannounced route or destination change | b: 2 of 5 days; a: 1 | 240-420 EGP + up to 75 min | in-000562/in-000608 (far shop, no reservation); in-000852/in-000854 (one-way, then home: 390 vs ~150); in-000735 (a left without Panatek's finish confirmation, so heads stayed overnight) | b: about 1 in 3 days. |
| Privacy slip with the delivery address | 1 full + 1 partial | Address exposed to a ride app | file-000517 (in-000518, in-000524); street name in quotes file-000939, file-001192 | b: 1 of 2 days on which he priced delivery routes. |
| Reporting gaps: counts, whereabouts, costs not volunteered | ~17 omissions | Seb chases for up to 6 messages; forces decisions made blind | in-000626 (6 vs 25 never explained); in-000871 (heads location: 6 asks, out-000815…out-000888); in-001086 (head count: 4 asks); in-000405 (PCBZone outcome only next day); in-000004 (tools never stated) | a: about 3 of 4 multi-item errands end without a count. b: omits costs or route changes until asked, 3 of 3 times. |
| Start lateness and reply latency (calibration) | a late on 3 of 5 shifts | 9-20 min late | in-000007, in-000201, in-000429 | Median reply 3-4 min. Silences of 50-60 min while riding or in no-signal shops (in-000572, in-001068). |

### 2d. Money, evidence, build
| Kind | n | Typical cost | Example ids | Simulator rate |
|---|---|---|---|---|
| Payment and ledger friction (bot /paid, cancel buttons) | a: 9 malformed of ~20 attempts; b: 4 failed, only 2 of 19 requests ever reported | Funds locked; on Oct 7, 21 of 78 Seb messages (13:00-16:00) were /paid instructions; available budget showed 0 at 15:38 (out-001148) | in-000741, in-001004, in-001039, in-001101, in-001104; cancel button not found (in-000761, so 400 EGP stayed held, spend-000730); successes only after a copyable line (out-000716→in-000717, out-001153→in-001154) | /paid works only when the exact line is supplied. b reported 2 of 19 requests, both only after a copyable line. Payments get batched to the last day. |
| Photo or evidence problems | ~9 of 53 photo messages; 36 photos had no caption | 2-10 min follow-up each; one unresolved head count | in-000048 (photos refused); in-000403 (no invoice); out-000145 (board photo shows no voltage); out-001094 (3 modules, no count); file-000498 (food receipt as reading page); file-000432 (test on a car seat); file-000808 (padded chair); out-001148 (fare screen is not a receipt) | About 1 in 6 photos needs a redo or a question. No technician receipt appears in the record (Harby: in-000403; none for Panatek). |
| Assembly or stability failure | 0 lamp failures; 1 folding geometry error | 4 photo-correction rounds, ~37 min (in-000781 15:47 → in-000832 16:24) | B001 mounted in ~4 min (out-000451→file-000453) and passed 20 min (in-000508). A001 lit and stood alone within ~4 min (file-001157 15:45 → file-001170 15:49) | With a head and a body in hand, assembly takes 5-10 min per lamp. Novel folds take 1-4 correction rounds. |
| Price accuracy (calibration, not friction) | ~10 quotes | Paid amount within 0-12% of the quote | Stand 180 (in-000074→in-000098). Parts 58.50 (out-000379). Panatek 100/head → 600 (in-000732, in-000983). Paper ~170 (in-000676→in-000811). Rides 143 (in-000040→in-001001), 417 (in-000721→in-000929), 387→390 (file-000856→in-001095), 232→260 with a reroute (in-001128) | Price quotes hold. Car legs cost 110-450 EGP. Ashgar City ↔ downtown is 390-420 per leg (in-000413, in-000616). |

## 3. What not to simulate
### 3a. The real manager's own decision errors (exclude; the agent under test supplies its own)
- **M1 Slow scale-up.**
  - Seb ran one sample then one batch at every layer.
  - B001 passed at 14:27 Oct 5 (in-000508). The batch heads were commissioned only at 14:38 Oct 6 (out-000739), from a technician about 75 min away (in-000735→in-000783).
  - Bodies were never batch-bought. The stand shop's other 4 units at 180 were not bought (in-000128). Seb declined 5 sheets for 550 to protect delivery money (out-000834). Only 1 card body was ever made.
- **M2 Transport-heavy routing.**
  - Car round trips with 800 and 900 EGP caps (out-000488, out-000729). Six part sets were taken from New Maadi to Panatek in 6th of October: 865 EGP travel for 600 EGP of labour, and then a courier anyway (in-001063).
  - Every trip home for Abdelrahman cost 309-420 EGP (file-000152, in-000413, in-000616, in-001095). Seb first asked where he ends shifts only on Oct 6 (out-000842).
  - Of the ~3,940 EGP transport, the fares are world prices; the number and length of trips are Seb's choices.
- **M3 Ledger process.** 33 fine-grained reservations (8,880 EGP against a 7,000 budget). Seb refused new spending until /paid was reconciled, so the last shift was spent on bookkeeping (21 of 78 messages) with "available 0" (out-001148). Worker non-reporting (2d) is world friction; blocking work on it was Seb's choice.
- **M4 No delivery dispatch.** At 16:02, with B001 and A001 both lit, Seb was still asking for paper or covers for more bodies (out-001190). It had sent no departure instruction before its run halted at 16:07 (out-001198). The workers asked twice (in-001200, in-001201) and left on their own at 16:25 (in-001211).
- **M5 Early disclosure of the address.** Seb sent the address as a "planning note" on Oct 5 (out-000427), which Abdelrahman then typed into Uber (file-000517). The slip itself is worker friction (2c).
- **M6 Shift-time planning.** A 47-min-each-way collection trip was authorised at 14:05 in a shift ending at 17:00 (out-000489), and a stationery errand at 15:13 (out-000550). Some of the overstays and the late, unexplained "6 sets" followed from this.

### 3b. Harness or platform friction (not world; simulate only if the sim models the platform)
- Evaluation stops: 16:07 on Oct 7 (out-001198), with a resume and stop flicker at 16:45-16:46 (out-001212…out-001217). The cause is not in the record. An earlier stop at 05:38 Oct 7 was off-shift (out-000890).
- Seb's email tool showed only sender and subject for 4 supplier replies (tx Sat03 09:46, Sun04 13:14, Sun04 19:01, Fri02 12:17).
- Calling allowance stuck at $1.02 from Oct 2 (tx Fri02 16:02).
- About 8 timeouts on the worker channel or project API (tx Mon05 14:59, Tue06 16:46, Wed07 13:01, Wed07 15:43). Attachment downloads timed out twice (tx Sun04 16:38, Wed07 13:20). The guide server was down once (tx Wed07 13:13).
- Bot UI: the cancel button was missing (in-000761).

## 4. Why only 2 lamps (ranked)
1. **Heads arrived only 2 hours before the deadline.** No off-the-shelf 5V USB head existed. About 6 of 8 shops could not do the join in time, and the one batch technician slipped past shift end. The batch heads reached a worker at 14:53 on the last day (in-001082). This is world friction, made worse by M1's 24-hour gap before commissioning.
2. **Only 2 bodies ever existed.** These were the 180 EGP stand and one folded sheet. Body scale-up was deferred (M1), shops held small stock (in-000128, in-000839), and on the last day there were no free boxes or covers (in-001134, in-001185). Mostly the manager's doing.
3. **Money ran dry and was locked.** About 73% of documented spend went on car travel (M2, priced by the world). The rest of the shortfall was budget the ledger showed as committed: 2c/2d reporting gaps, combined with Seb's choice to block spending until /paid was reconciled (M3). Seb saw 0 EGP available on the last afternoon (out-001148), so it could buy nothing more.
4. **Time lost to movement and worker deviations.** Trips ran +30-45 min, there were overstays and detours (2b, 2c), and the final assembly window was only 15:40-16:07 before the halt (M4, 3b).

Uncertain: whether the 2 lamps were delivered before 17:00 is outside the chat record (the brief says 2 qualified). How many Panatek heads were delivered is unconfirmed (file-001085 shows 3 modules).
