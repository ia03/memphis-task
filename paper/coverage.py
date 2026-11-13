"""Share of world-log entries that involve observed vs sampled businesses, per trial."""
# Usage, from paper/: python3 coverage.py .. TRIAL_DIR...   (the repo root, then Harbor trial folders, e.g. a release's trials/*)
import re, sys, json, collections
from pathlib import Path
repo, trials = Path(sys.argv[1]), [Path(p) for p in sys.argv[2:]]
# Observed businesses: key, English name and aliases from world/suppliers.yaml (parsed without PyYAML).
obs, cur = {}, None
for line in (repo / "world/suppliers.yaml").read_text().splitlines():
    if m := re.match(r'- key: (\S+)', line): cur = m.group(1); obs[cur] = {cur}
    elif cur and (m := re.match(r'  name: "(.*)"', line)):
        name = m.group(1); obs[cur].add(re.sub(r'\s*\(.*?\)', '', name).strip())
        obs[cur].update(re.findall(r'\(([^)]*)\)', name))
    elif cur and (m := re.match(r'  aliases: \[(.*)\]', line)):
        obs[cur].update(a.strip().strip('"') for a in m.group(1).split('",'))
def pat(names):
    alts = sorted({n.strip().strip('"').lower() for n in names if len(n.strip().strip('"')) >= 3}, key=len, reverse=True)
    return re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(a) for a in alts) + r')(?!\w)')
OBS = {k: pat(v) for k, v in obs.items()}
SAMPLED = re.compile(r'walkin-[a-z_]+-[a-z_]+-\d+|\(\d\)|shop \d on the main market street|walk-in|sampled shop', re.I)
GENERIC = re.compile(r'(?<!\w)(shop|shops|store|stall|kiosk|stationer\w*|grocer\w*|bookshop|vendor|seller|electrician|technician)(?!\w)', re.I)
rows = []
for d in sorted(trials):
    text = (d / "artifacts/out/world/log.md").read_text()
    # An entry starts at a timestamped heading or a bare timestamp line; the lines under it belong to it. A log written
    # as timestamped bullets instead ("- 2026-10-01T13:27:41: ...") has an entry per bullet.
    START = re.compile(r'^(#{1,4} .*)?20\d\d-\d\d-\d\d[T ]\d\d:\d\d')
    if not any(START.match(line) for line in text.split('\n')):
        START = re.compile(r'^[-*] 20\d\d-\d\d-\d\d[T ]\d\d:\d\d')
    entries = []
    for line in text.split('\n'):
        if START.match(line) or not entries: entries.append(line)
        else: entries[-1] += '\n' + line
    c = collections.Counter(); hit = collections.Counter()
    for e in entries:
        low = e.lower()
        o = [k for k, p in OBS.items() if p.search(low)]
        sm = bool(SAMPLED.search(e))
        for k in o: hit[k] += 1
        if o and not sm: c['observed_only'] += 1
        elif sm and not o: c['sampled_only'] += 1
        elif o and sm: c['both'] += 1
        elif GENERIC.search(e): c['generic_only'] += 1
        else: c['no_business'] += 1
    rows.append(dict(trial=d.name.split('__')[0], entries=len(entries), **c, top=hit.most_common(4)))
for r in rows: print(json.dumps(r, ensure_ascii=False))
# Per condition: of the entries that name a specific business, the share that name only observed ones (Section 4).
for cond in ("hinted", "unhinted"):
    rs = [r for r in rows if r["trial"].endswith("-" + cond)]
    named = sum(r.get("observed_only", 0) + r.get("sampled_only", 0) + r.get("both", 0) for r in rs)
    if named:
        share = sum(r.get("observed_only", 0) for r in rs) / named
        each = [r.get("observed_only", 0) / max(1, r.get("observed_only", 0) + r.get("sampled_only", 0) + r.get("both", 0)) for r in rs]
        generic = sum(r.get("generic_only", 0) for r in rs) / sum(r["entries"] for r in rs)
        print(f"{cond}: {share:.1%} of {named} entries naming a business name only observed ones "
              f"(per trial {min(each):.0%} to {max(each):.0%}); {generic:.0%} of entries mention shops generically")
