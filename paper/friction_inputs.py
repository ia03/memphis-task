"""Write the three files a friction coder reads (friction_guide.md) for one trial: log.md, chat.md and comms.md.

    python3 friction_inputs.py TRIAL_DIR OUT_DIR

log.md is the world model's log as it is. chat.md lists every message between Seb and the workers (`chat#N`, Cairo time, photos as
`[photo <id>: <caption>]`); comms.md lists Seb's calls (`call#N`) and emails (`email#N`), from the trial's verifier/export.json.
"""

import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CAIRO = timezone(timedelta(hours=3))


def cairo(utc: str) -> str:
    return datetime.fromisoformat(utc).astimezone(CAIRO).strftime("%a %H:%M:%S")


def main(trial: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(trial / "artifacts" / "out" / "world" / "log.md", out / "log.md")
    export = json.loads((trial / "verifier" / "export.json").read_text())
    ledger = export["ledger"]
    photos = {a["id"]: a for a in ledger["attachments"]}
    rows = [(o["queued_at_utc"], f"Seb -> {o['worker_id']}: {o['text']}") for o in ledger["outbound"] if o.get("text")]
    for i in ledger["inbound"]:
        text = i.get("text") or ""
        if i.get("attachment_id") in photos:
            text += f" [photo {i['attachment_id']}: {photos[i['attachment_id']]['caption']}]"
        rows.append((i["received_at_utc"], f"{i['worker_id']} -> Seb: {text.strip()}"))
    rows.sort(key=lambda r: r[0])
    (out / "chat.md").write_text("".join(f"chat#{n} {cairo(t)} {x}\n" for n, (t, x) in enumerate(rows, 1)))
    lines = [f"call#{n} {cairo(c['time_utc'])} to {c['key']} ({c.get('number', '')}) status={c.get('status', '')}: "
             f"{c.get('transcript', '')}" for n, c in enumerate(export["calls"], 1)]
    for n, e in enumerate(export["emails"], 1):
        when = cairo(e["time_utc"]) if e.get("time_utc") else ""
        lines.append(f"email#{n} {when} {e.get('direction', '')} {e.get('address', '')} subject={e.get('subject', '')!r}: "
                     f"{e.get('text', '')}")
    (out / "comms.md").write_text("".join(line.replace("\n", " ") + "\n" for line in lines))


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
