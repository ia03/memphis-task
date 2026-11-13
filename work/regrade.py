"""Grade a finished trial again from its copied world folder, for trials whose Harbor verifier timed out before the grade
call returned. Same grader prompt as the run; read-only. Run: PYTHONPATH=. python work/regrade.py TRIAL_DIR"""

import json
import sys
from pathlib import Path

from hsim.simulator import Simulator

out = Path(sys.argv[1]) / "artifacts" / "out"
sim = Simulator.__new__(Simulator)
sim.folder, sim.model, sim.effort, sim.sandbox = out / "world", "gpt-6.1-sol", "medium", "read-only"
grade = sim.grade()
(out / "regrade.json").write_text(json.dumps(grade, ensure_ascii=False, indent=1))
print(json.dumps({"qualifying_delivered": grade["qualifying_delivered"], "spent_egp": grade["spent_egp"],
                  "reward": min(grade["qualifying_delivered"] / 5, 1.0) if grade["spent_egp"] <= 7000 else 0.0}))
