# Start here

A map of the project for anyone joining it: what each folder holds, where the data that is not in git lives, and what is still
open. Last updated 5 November 2026.

## What this is

GPT-6.1 Sol (called Seb in that role) managed two hired workers in Cairo over chat for five shifts in October 2026, with 7,000
EGP, to build USB desk lamps from components. It finished two. Memphis is a Harbor task built from that real-world evaluation:
one language model (the world model) simulates the workers, shops and city from the real chats, shops, prices and incident
counts, and the agent being tested takes Seb's place. The paper (`paper/`) is a case study of the method, written for TMLR.

## Where things are

| What | Where |
|---|---|
| The paper | `paper/main.tex` and `paper/main.pdf`. Build with `tectonic main.tex` in `paper/`. `\anonymoustrue` in the preamble gives the review build; `\anonymousfalse` the named one. The main text must stay within 12 pages before the references (TMLR's shorter review period). |
| The real-world evaluation | `context/consent.md` (the workers' written consent, item by item), `context/real-run/`: Seb's full transcript, all 798 worker messages, the 33 spending requests, calls, emails and photos. `context/README.md` explains each file. `work/catalog/october-incidents.md` is the friction table counted from the chats, with message ids. |
| The task and simulator | `build_task.py`, `hsim/` (server, clock, ledger), `world/` (facts, instructions, photos, the hint `world/hint_note_v3.md`), `harbor_ext/` (Codex and Claude Code agent wrappers), `run.sh`. The measured version is the tag `v12.0-rc17`. `docs/DESIGN.md` and `docs/AUDIT.md` describe the design and the audit. `docs/HISTORY.md` is the development log. |
| Results | `RESULTS.md` (every round, with audit verdicts and causes). `report/site/index.html` is a browsable report with every trial's transcript and audit. |
| Final round r18 (GPT), raw trials | GitHub release **v12.1**, asset `memphis-eval-r18.zip`: the ten built tasks and the ten trial folders. Each trial's world-model folder is `trials/<trial>/artifacts/out/world/`, with `state.md` (the world model's notes on the current state) and `log.md` (the timed account of everything that happened). |
| Claude rounds c1, c2, c3, raw trials | GitHub release **claude-trials**, asset `memphis-eval-claude.tgz`: the 30 valid trials (one per seed and condition in each round), their audits and friction codes, and the scripts that ran the rounds. Each trial has `state.md` and `log.md` under `artifacts/out/world/`. The older release **c1-trials** holds round c1 alone. |
| Earlier rounds | r13: release v12.0 or v12.0-rc10 (`memphis-r13-trials.tgz`). r12: release v12.0-rc9. r16: its raw trial folders were not kept, but each trial's transcript and audit are in `report/site/trials/r16-*.html`. |
| Audits | `audits/` (rounds r12, r13, r18 and c1 to c3, one file per trial). |
| Analysis behind the paper's numbers | `paper/*.py`: coverage (`coverage.py`), friction counts (`friction_check.py` with `friction_coded/` and `friction_coded_claude/`), round statistics (`rounds_stats.py`, and `claude_rounds.py` for the three Claude rounds pooled), agent cost and tokens (`agent_round.py`), blind failure coding (`failure_coding.py` and `failure_coding/`). `paper/technician_sensitivity.md` is the estimate of the technician-delay error. |
| Human check of four audits | `paper/audit_review/` builds a review page, holds the reviewer's answers (`answers/`) and scores them against the audits (`score_review.py`). |
| Writing checks | `paper/writing_checks/`: what readers with no context flagged in the paper, before and after each rewrite, and a blind comparison of old and new paragraphs. The writing rules are in `.claude/skills/human-writer-claude/` (`author_rules.md`, `prose_check.py`). |
| Review supplement | Built by `scripts/anon_release.py` (pseudonyms for the workers, client name and building number removed). It is not in git because of its size. |

## Running a trial

The task needs Docker, Python 3.12, Harbor 0.23 and a Codex sign-in (`~/.codex/auth.json`) for the world model; a Claude agent
also needs a Claude Code token. `README.md` shows a run. Trials run on a cloud VM in Google Cloud project `memphis-513601`, with
results copied to the bucket `gs://memphis-513601-results`; `scripts/claude_round.sh` and `scripts/claude_replicates.sh` are
the unattended runners, and both delete the VM when they finish.

## Open work

- **Claude replicates (done 5 November):** rounds c2 and c3 (20 trials, `scripts/claude_replicates.sh`) gave Claude three
  trials per seed and condition. The paper's Claude section, Tables 3 and 4 and RESULTS.md cover all 30 trials.
- **Worker details (redacted 5 November):** worker A's first message gives his surname and home street, and worker B once sent
  his phone number; every trial's copy of the chats repeats them, and the world model and agents wrote the street in English
  too. They are removed from every tracked file (`scripts/redact_repo.py`), from the files of every GitHub release, and from
  the four r18 trial pages of the published report. `scripts/package.py`, `scripts/package_claude.py` and
  `scripts/anon_release.py` apply the same rules, which are kept outside git in `private/worker_redactions.json`. The commits
  before 5 November and the tags still hold them, by decision (the repository is private; v12.0-rc17 builds the tasks as
  measured), as do the private Drive copies of the October record.
- **Client details (removed 6 November):** the client, at whose home the lamps were delivered, is named in the trials and
  his address (street, building number, map link) is in the task. Every copy that leaves the repository drops them
  (`CLIENT` in `scripts/anon_release.py`): the published report, `report/site/`, the Drive copy of `memphis-eval-r18.zip`
  (built by `scripts/package.py`) and the review copy. The task's own files, the trials and the GitHub releases keep them.
- **Consent (done 4 November):** both workers agreed in writing to all five uses asked of them; the request and their answers
  are summarised in `context/consent.md`, and the paper's ethics statement says so.
- **Human audit check (done 7 November):** a collaborator reviewed four audits of the final round; the answers are in
  `paper/audit_review/answers/`, `paper/audit_review/score_review.py` compares them with the audits, and the paper reports the
  result in Section 6 and the audit appendix.
- **Submission:** upload the review supplement with the anonymous PDF.
