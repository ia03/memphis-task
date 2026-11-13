import json
import os
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def request(path, body=None, raw=False, query=None):
    # No timeout: the world answers when the simulator has finished its step, and the project clock is stopped meanwhile.
    base = os.environ["TASK5_FIELD_URL"].rstrip("/")
    token = os.environ["TASK5_FIELD_AGENT_TOKEN"]
    url = base + path + ("?" + urlencode(query) if query else "")
    payload = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": "Bearer " + token, "Content-Type": "application/json"}
    try:
        with urlopen(Request(url, data=payload, headers=headers, method="POST" if body is not None else "GET")) as r:
            return r.read() if raw else json.load(r)
    except HTTPError as exc:
        try:
            detail = json.load(exc).get("detail", exc.reason)
        except Exception:
            detail = exc.reason
        raise SystemExit(f"HTTP {exc.code}: {detail}")
