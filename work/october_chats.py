"""Copy the real run's worker chats (export readable/worker-chats.txt) into work/catalog/october-chats.json, one readable line
per message and worker, in Cairo time. The world simulator reads it as its reference for how the workers and shops behaved.
Run once: python work/october_chats.py EXPORT/readable/worker-chats.txt"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CAIRO = timezone(timedelta(hours=3))
rows = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
out: dict[str, list[tuple[str, str]]] = {}
for r in rows:
    when = datetime.fromisoformat(r.get("received_at_utc") or r.get("settled_at_utc") or r["queued_at_utc"]).astimezone(CAIRO)
    who = "WORKER" if r["direction"] == "inbound" else "SEB"
    text = " ".join((r.get("text") or "").split()) + (f" [photo {r['attachment_id']}]" if r.get("attachment_id") else "")
    out.setdefault(r["worker_id"], []).append((when.isoformat(), f"[{when:%a %d %b %H:%M}] {r['id']} {who}: {text}"))
path = Path(__file__).resolve().parent / "catalog" / "october-chats.json"
path.write_text(json.dumps({w: [line for _, line in sorted(v)] for w, v in sorted(out.items())}, ensure_ascii=False, indent=1))
print({w: len(v) for w, v in out.items()}, path)
