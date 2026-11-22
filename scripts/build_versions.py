"""Build the TMLR (anonymous) and arXiv (named) versions of the paper from paper/main.tex.

Usage: uv run --no-project --python 3.12 python scripts/build_versions.py

Writes to dist/paper/ (git-ignored):
  tmlr.pdf, tmlr/      anonymous PDF and the source it was built from
  arxiv.pdf, arxiv/    named PDF and the source to upload: comments removed, main.bbl instead of refs.bib,
                       only the figures the paper uses
  arxiv.zip            arxiv/ zipped for upload

The two versions differ only in the \\anonymoustrue switch at the top of main.tex; the text is the same.
Builds with tectonic when it is installed, otherwise latexmk (MiKTeX or TeX Live). If pdflatex is installed,
the arXiv folder is also compiled again on its own, the way arXiv will, to check it is complete.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPER = ROOT / "paper"
OUT = ROOT / "dist" / "paper"
SWITCH = "\\anonymoustrue"
SUPPORT = ["tmlr.sty", "tmlr.bst", "fancyhdr.sty"]


def fail(msg):
    sys.exit(f"build_versions: {msg}")


def strip_comments(tex):
    """Drop LaTeX comments. A line that was only a comment goes; otherwise the % stays, so line joins are kept."""
    out = []
    for line in tex.splitlines():
        m = re.search(r"(?<!\\)%", line)
        if m is None:
            out.append(line)
        elif line[: m.start()].strip():
            out.append(line[: m.start() + 1])
    return "\n".join(out) + "\n"


def figures(tex):
    files = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex)
    for f in files:
        if not (PAPER / f).is_file():
            fail(f"figure not found: paper/{f}")
    return files


def compile_pdf(d, use_bib=True):
    """Compile main.tex in d. Returns the main.log text."""
    if not use_bib:
        for _ in range(3):
            run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], d)
    elif shutil.which("tectonic"):
        run(["tectonic", "-k", "--keep-logs", "main.tex"], d)
    elif shutil.which("latexmk"):
        run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], d)
    else:
        fail("needs tectonic or latexmk on PATH")
    log = (d / "main.log").read_text(errors="replace")
    problems = [l for l in log.splitlines() if l.startswith("! ") or re.search(r"undefined (on|references)", l)]
    if problems or not (d / "main.pdf").is_file():
        fail(f"build in {d} has problems:\n  " + "\n  ".join(problems[:10]))
    return log


def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        fail(f"{' '.join(cmd)} failed in {cwd}:\n{(r.stdout + r.stderr)[-3000:]}")


def pages(log):
    m = re.findall(r"\((\d+) pages?", log)
    return m[-1] if m else "?"


def build(name, tex, figs, work):
    d = work / name
    (d / "figs").mkdir(parents=True)
    (d / "main.tex").write_text(tex)
    for f in SUPPORT + ["refs.bib"]:
        shutil.copy2(PAPER / f, d / f)
    for f in figs:
        (d / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PAPER / f, d / f)
    log = compile_pdf(d)
    shutil.copy2(d / "main.pdf", OUT / f"{name}.pdf")
    keep = ["main.tex", "main.bbl"] + SUPPORT + figs
    if name == "tmlr":
        keep.append("refs.bib")
    src = OUT / name
    for f in keep:
        (src / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(d / f, src / f)
    return pages(log)


def main():
    tex = (PAPER / "main.tex").read_text()
    if len(re.findall(rf"^{re.escape(SWITCH)}\s*$", tex, re.M)) != 1:
        fail(f"expected one line '{SWITCH}' in paper/main.tex")
    figs = figures(tex)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="bv") as w:
        work = Path(w)
        tmlr_tex = re.sub(rf"^{re.escape(SWITCH)}\s*$", lambda _: SWITCH, tex, flags=re.M)
        arxiv_tex = strip_comments(re.sub(rf"^{re.escape(SWITCH)}\s*$", lambda _: "\\anonymousfalse", tex, flags=re.M))
        n_tmlr = build("tmlr", tmlr_tex, figs, work)
        n_arxiv = build("arxiv", arxiv_tex, figs, work)

        left = [l for l in (OUT / "arxiv" / "main.tex").read_text().splitlines() if re.search(r"(?<!\\)%.", l)]
        if left:
            fail("comment text left in arxiv/main.tex:\n  " + "\n  ".join(left[:5]))

        if shutil.which("pdflatex"):
            check = work / "arxiv-check"
            shutil.copytree(OUT / "arxiv", check)
            compile_pdf(check, use_bib=False)
            standalone = "compiles on its own with pdflatex"
        else:
            standalone = "not checked on its own (pdflatex not installed)"

    with zipfile.ZipFile(OUT / "arxiv.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted((OUT / "arxiv").rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(OUT / "arxiv").as_posix())

    print(f"tmlr.pdf   {n_tmlr} pages, anonymous")
    print(f"arxiv.pdf  {n_arxiv} pages, named")
    print(f"arxiv.zip  {len(zipfile.ZipFile(OUT / 'arxiv.zip').namelist())} files; source {standalone}")
    print(f"output in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
