#!/bin/sh
# Where the paper's main text ends, and where each section starts.
# Usage: scripts/page_probe.sh [paper-dir]   (default: paper)
# Target: the main text ends on page 12. Needs tectonic and uv.
SRC=${1:-paper}
D=$(mktemp -d "${TMPDIR:-/tmp}/probe.XXXX")
cp -R "$SRC"/. "$D"/
uv run --no-project --python 3.12 python - "$D/main.tex" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]); t = p.read_text()
keys = [r"\section{The real-world evaluation}", r"\section{From the real-world evaluation to a simulated task}",
        r"\section{Simulator error and coverage}", r"\section{Auditing the simulator and the grader}",
        r"\section{Experiments}", r"\section{Related work}", r"\section{Limitations}",
        "retrieved the bibliography metadata from arXiv."]
for i, k in enumerate(keys):
    if t.count(k) != 1:
        sys.exit(f"probe key not found once: {k}")
    t = t.replace(k, k + r"\pdfsavepos\write\probefile{" + k.replace("\\", "").replace("{", " ").replace("}", "")[:40] + r" | p\thepage\space\the\pdflastypos}", 1)
t = t.replace(r"\begin{document}", r"\newwrite\probefile\immediate\openout\probefile=probe.txt" + "\n" + r"\begin{document}", 1)
p.write_text(t)
PY
(cd "$D" && tectonic -k main.tex >/dev/null 2>&1)
awk -F' [|] ' '{split($2,a," "); printf "%-42s %s at %d pt from bottom\n", $1, a[1], a[2]/65536}' "$D/probe.txt"
rm -rf "$D"
