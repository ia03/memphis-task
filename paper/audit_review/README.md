# Audit review page

The page at [private report link removed] lets a person check Claude's audits of the ten final-round trials.
It saves answers in the page's own store (`reviews/<user id>`).

- `plain/`: each audit rewritten in plain English (Simplified Technical English rules) by one Claude instance per audit,
  with `plain_guide.md`. `check_plain.py` checks each against its audit: finding ids, log citations, verdict and range.
- `build_review_data.py`: builds the page's data files from the audits and the raw r18 trials (GitHub release v12.1).
  Usage: `python3 build_review_data.py <repo> <trials dir> <out dir>`, with `plain/out/` beside `<out dir>`.
- `page_template.html`: the page; the trial index replaces `__INDEX__`.
- `answers/reviewer_1.json`: the answers of a collaborator on the project who reviewed four trials (copied from the page's "Copy answers" button,
  7 November 2026). `score_review.py` compares them with the audits:
  `python3 paper/audit_review/score_review.py paper/audit_review/answers/reviewer_1.json`.
