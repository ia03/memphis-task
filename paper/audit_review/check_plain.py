"""Check each plain rewrite against its audit, then merge it into the review page's data files."""
import json, re, sys
from pathlib import Path
REPO, S = Path(sys.argv[1]), Path(sys.argv[2])
index = {t["slug"]: t for t in json.loads((S / "review/index.json").read_text())}
LOG = re.compile(r"\blogs?\s+((?:\d+(?:\s*[-–]\s*\d+)?)(?:\s*(?:,|and|&)\s*\d+(?:\s*[-–]\s*\d+)?)*)", re.I)
def lognums(text):
    out = set()
    for m in LOG.finditer(text):
        for a, b in re.findall(r"(\d+)(?:\s*[-–]\s*(\d+))?", m.group(1)):
            out.add(int(a));  out.add(int(b)) if b else None
    return out
BAD = {"em dash": "—", "semicolon": ";", "code": re.compile(r"\b[a-z]+_[a-z_]+\b|\b[EHIVG]\d+\b|\bsim step\b|\bfacts\.json\b")}
VL = {"yes": "fair", "mostly": "mostly fair", "partly": "partly fair", "no": "not fair"}
ok_all = True
for slug, t in index.items():
    f = S / "plain/out" / f"{slug}.json"
    if not f.exists(): print(slug, "MISSING"); ok_all = False; continue
    P = json.loads(f.read_text()); audit = (REPO / "audits" / f"audit-{slug}.md").read_text()
    problems = []
    texts = list(P.get("what_happened", [])) + list(P.get("cause", []))
    for q in P.get("findings", []):
        texts += [q.get("title", ""), q.get("effect", "")] + list(q.get("what", [])) + list(q.get("why", []))
    texts += list((P.get("verdict") or {}).get("reason", []))
    ids_plain = [q.get("id") for q in P.get("findings", [])]; ids_index = [x["id"] for x in t["findings"]]
    if sorted(ids_plain) != sorted(ids_index): problems.append(f"finding ids {ids_plain} vs audit {ids_index}")
    extra = lognums(" ".join(texts)) - lognums(audit)
    if extra: problems.append(f"log numbers not in the audit: {sorted(extra)}")
    long = [x for x in texts if len(x.split()) > 25]
    if long: problems.append(f"{len(long)} sentences over 25 words, e.g. {long[0][:90]!r}")
    for name, pat in BAD.items():
        hits = [x for x in texts if (pat in x if isinstance(pat, str) else pat.search(x))]
        if hits: problems.append(f"{name} in {len(hits)}: {hits[0][:90]!r}")
    v = P.get("verdict") or {}
    if (v.get("label") or "").strip().lower() != VL.get(t["claude"]["fair"]): problems.append(f"verdict {v.get('label')!r} vs audit {t['claude']['fair']}")
    rng = t["claude"]["range"]
    if rng and not all(str(n) in (v.get("range") or "") for n in rng): problems.append(f"range {v.get('range')!r} vs audit {rng}")
    exp = t["claude"]["expected"]
    if exp is not None and str(exp).rstrip("0").rstrip(".") not in (v.get("best") or ""): problems.append(f"best {v.get('best')!r} vs audit {exp}")
    print(slug, "OK" if not problems else "CHECK:"); [print("   -", p) for p in problems]
    ok_all &= not problems
    d = json.loads((S / "review/data" / f"{slug}.json").read_text()); d["plain"] = P
    (S / "review/data" / f"{slug}.json").write_text(json.dumps(d, ensure_ascii=False))
print("all clean" if ok_all else "some need a look")
