"""Build the audit-review page's data: one JSON file per final-round trial plus the index embedded in the page."""
import glob, json, random, re, sys
from pathlib import Path

REPO, TRIALS, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
HIDE = re.compile(r"^(verdict\b|.*counterfactual|.*fair range)", re.I)
index = []
for d in sorted(TRIALS.glob("r18-s*-*__*")):
    slug = d.name.split("__")[0]
    m = re.match(r"r18-s(\d+)-(hinted|unhinted)", slug)
    seed, cond = int(m.group(1)), m.group(2)
    audit = (REPO / "audits" / f"audit-{slug}.md").read_text(encoding="utf-8")
    verdict = [json.loads(b) for b in re.findall(r"`{3}json\s*(\{.*?\})\s*`{3}", audit, flags=re.S)][-1]
    body = re.sub(r"`{3}json\s*\{.*?\}\s*`{3}", "", audit, flags=re.S)
    parts = re.split(r"(?m)^## ", body)
    sections = [{"title": "Overview", "md": re.sub(r"(?m)^# .*\n", "", parts[0]).strip(), "hidden": False}]
    for p in parts[1:]:
        title, _, rest = p.partition("\n")
        sections.append({"title": title.strip(), "md": rest.strip(), "hidden": bool(HIDE.match(title.strip()))})
    raw = [(f, effect) for key, effect in [("count_changing_defects", "changed the count"), ("plausible_count_changing", "may have changed the count"),
                                           ("new_defects", "new in this round"), ("known_defects_seen", "known kind")] for f in verdict.get(key) or []]
    plain_path = OUT.parent / "plain" / "out" / f"{slug}.json"
    plain_ids = [q["id"] for q in json.loads(plain_path.read_text())["findings"]] if plain_path.exists() else []
    if any(not f.get("id") for f, _ in raw):  # this audit's JSON gives no ids: the plain rewrite took them from its table, in order
        assert len(raw) == len(plain_ids), (slug, len(raw), plain_ids)
        raw = [(dict(f, id=i), e) for (f, e), i in zip(raw, plain_ids)]
    findings, seen = [], set()
    for f, effect in raw:
        if f["id"] in seen: continue
        seen.add(f["id"])
        findings.append({"id": f["id"], "cls": f.get("class") or f["id"][0], "sev": f.get("severity"), "effect": effect, "summary": f.get("summary") or f.get("what") or ""})
    export = json.loads((d / "verifier" / "export.json").read_text())
    led = export.get("ledger", {})
    chat = [{"t": o["queued_at_utc"], "who": "Seb", "to": o.get("worker_id"), "text": o.get("text", "")} for o in led.get("outbound", [])]
    chat += [{"t": i["received_at_utc"], "who": i.get("worker_id"), "text": i.get("text", "") or ("[photo]" if i.get("attachment_id") else "")} for i in led.get("inbound", [])]
    chat.sort(key=lambda x: x["t"])
    facts = json.loads((d / "artifacts" / "out" / "world" / "facts.json").read_text())
    flat = []
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items(): walk(v, f"{path}.{k}" if path else str(k))
        elif isinstance(o, list) and o and all(isinstance(x, (dict, list)) for x in o):
            for i, v in enumerate(o): walk(v, f"{path}[{i}]")
        else:
            flat.append([path, o if isinstance(o, (int, float, bool)) or o is None else (o if isinstance(o, str) else json.dumps(o, ensure_ascii=False))])
    walk(facts, "")
    log = (d / "artifacts" / "out" / "world" / "log.md").read_text(encoding="utf-8").splitlines()
    score = json.loads((d / "verifier" / "score.json").read_text())
    data = {"slug": slug, "sections": sections, "log": log, "facts": flat, "chat": chat,
            "grade": export.get("grade", {}).get("lamps", [])}
    (OUT / "data" / f"{slug}.json").write_text(json.dumps(data, ensure_ascii=False))
    index.append({"slug": slug, "seed": seed, "cond": cond, "lamps": score["qualifying_delivered"], "score": round(score["reward"], 2),
                  "spent": score["spent_egp"], "findings": findings,
                  "claude": {"fair": verdict.get("fair"), "range": verdict.get("fair_lamp_range"), "expected": verdict.get("expected_fair_lamps")}})
order = [t["slug"] for t in index]
random.Random(20261102).shuffle(order)
for t in index: t["order"] = order.index(t["slug"]) + 1
index.sort(key=lambda t: t["order"])
(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False))
for t in index:
    f = OUT / "data" / f"{t['slug']}.json"
    print(t["order"], t["slug"], t["claude"]["fair"], len(t["findings"]), "findings", f"{f.stat().st_size // 1024} KB")
