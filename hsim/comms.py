"""Seb's email, AI-call and web tools. Calls and emails go to the world simulator as events; web search reads the real
October search results (work/catalog/web-corpus.json) and the shops' web pages from the seed's facts."""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from pydantic import BaseModel
from rank_bm25 import BM25Okapi

from .world import ROOT, World

CORPUS = ROOT / "work" / "catalog" / "web-corpus.json"


class Email(BaseModel):
    id: str
    direction: str
    address: str
    subject: str
    text: str
    time_utc: str


class Call(BaseModel):
    key: str
    number: str
    status: str
    transcript: str = ""
    time_utc: str


class Comms:
    def __init__(self, world: World, now: Callable[[], str], event: Callable[[dict[str, Any]], None]) -> None:
        self.world, self.now, self.event = world, now, event
        self.emails: list[Email] = []
        self.calls: dict[str, Call] = {}
        self.sent_keys: dict[str, str] = {}
        self.pages = json.loads(CORPUS.read_text())["results"]
        self.bm25 = BM25Okapi([self._tokens(f"{p['title']} {p['snippet']} {p['url']}") for p in self.pages])

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[\w؀-ۿ]+", text.lower())

    def send_email(self, to: str, subject: str, text: str, key: str) -> dict[str, str]:
        if key in self.sent_keys:
            return {"status": "duplicate_key", "message_id": self.sent_keys[key]}
        mid = f"email-{len(self.emails) + 1:04d}"
        self.sent_keys[key] = mid
        self.emails.append(Email(id=mid, direction="outbound", address=to, subject=subject[:200], text=text[:12000], time_utc=self.now()))
        self.event({"type": "email_from_seb", "to": to, "subject": subject[:200], "text": text[:12000]})
        return {"status": "sent", "message_id": mid}

    def receive_email(self, sender: str, subject: str, text: str) -> None:
        self.emails.append(Email(id=f"email-{len(self.emails) + 1:04d}", direction="inbound", address=sender, subject=subject,
                                 text=text, time_utc=self.now()))

    def email_inbox(self) -> dict[str, list[dict[str, str]]]:
        return {"messages": [{"id": e.id, "from": e.address, "subject": e.subject, "time_utc": e.time_utc, "preview": e.text[:160]}
                             for e in self.emails if e.direction == "inbound"]}

    def read_email(self, message_id: str) -> dict[str, str]:
        e = next((x for x in self.emails if x.id == message_id), None)
        return e.model_dump() if e else {"error": "unknown message"}

    def call_business(self, number: str, instructions: str, key: str, language: str = "ar-EG", max_seconds: int = 600) -> dict[str, str]:
        if key not in self.calls:
            self.calls[key] = Call(key=key, number=number, status="in_progress", time_utc=self.now())
            self.event({"type": "ai_phone_call_from_seb", "key": key, "number": number, "language": language, "instructions": instructions})
        return self.calls[key].model_dump()

    def call_result(self, key: str, status: str, transcript: str) -> None:
        if key in self.calls:
            self.calls[key] = self.calls[key].model_copy(update={"status": status, "transcript": transcript, "time_utc": self.now()})

    def call_status(self, key: str) -> dict[str, str]:
        c = self.calls.get(key)
        return c.model_dump() if c else {"error": "unknown call"}

    def web_search(self, query: str) -> dict[str, list[dict[str, str]]]:
        scores = self.bm25.get_scores(self._tokens(query))
        best = sorted(range(len(self.pages)), key=lambda i: -scores[i])[:8]
        return {"results": [{k: self.pages[i][k] for k in ("title", "url", "snippet")} for i in best if scores[i] > 0]}

    def web_open(self, url: str) -> dict[str, str]:
        domain = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
        s = next((x for x in self.world.suppliers.values() if x.web_domain and domain.endswith(x.web_domain.replace("www.", ""))), None)
        page = next((p for p in self.pages if p["url"] == url), None)
        if s is None:
            if page is None:
                return {"url": url, "error": "page not available"}
            return {"url": url, "title": page["title"], "text": page["snippet"] or "(page text not available)"}
        lines = [s.name.split(" (")[0], f"Address: {s.address or 'not stated'}", f"Phone: {s.phone or 'not stated'}", f"Email: {s.email or 'not stated'}"]
        for o in s.offers:
            if o.web_price_egp is not None:
                extra = f" Delivery {o.delivery_days} days." if o.delivery_days else ""
                lines.append(f"Listed: {self.world.items[o.item].name} — {o.web_price_egp:g} EGP.{extra}")
        lines += [f"Listed: {c.says}" for c in s.web_claims]
        if page is not None:
            lines.insert(0, page["title"])
        return {"url": url, "text": "\n".join(lines)}
