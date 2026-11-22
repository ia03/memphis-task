"""Compare the hand answers with the Opus coders' decisions for the 14 checked setback occasions (Section 5).

    uv run --no-project --python 3.12 python -I paper/friction_handcheck/handcheck.py
"""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
coded = {d["key"]: d for d in json.loads((HERE / "coder_decisions.json").read_text())}
answers = json.loads((HERE / "answers.json").read_text())

agree = 0
for key, d in coded.items():
    ours = answers[key] == "yes"
    same = ours == d["happened"]
    agree += same
    if not same:
        print(f"disagree {key} {d['trial']} {d['kind']} {d['cite']}: coders {d['happened']}, hand {ours} ({d['what']})")
print(f"agree on {agree} of {len(coded)}; kinds covered: {len({d['kind'] for d in coded.values()})}")
