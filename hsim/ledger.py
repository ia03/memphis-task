"""Messages and spend authorizations, mirroring the real Memphis field ledger's rules and notice texts."""

from __future__ import annotations

import threading
from copy import deepcopy
from typing import Literal

from pydantic import BaseModel, Field

from .clock import SimClock

SpendStatus = Literal["committed", "cancellation_pending", "cancelled", "reported_paid"]


class LedgerError(Exception):
    def __init__(self, message: str, code: int = 400) -> None:
        super().__init__(message)
        self.code = code


class SpendRequest(BaseModel):
    id: str
    idempotency_key: str
    worker_id: str
    amount_egp: int
    purpose: str
    status: SpendStatus
    created_at_utc: str
    reported_paid_egp: int = 0
    receipt_reference: str | None = None
    reported_paid_at_utc: str | None = None
    cancel_requested_at_utc: str | None = None


class Outbound(BaseModel):
    id: str
    worker_id: str
    text: str
    context_id: str | None = None
    notice_type: Literal["spend_authorization", "spend_cancellation"] | None = None
    queued_at_utc: str
    status: Literal["sent", "cancelled"] = "sent"


class Inbound(BaseModel):
    id: str
    worker_id: str
    text: str
    received_at_utc: str
    attachment_id: str | None = None
    agent_visible: bool = True


class Attachment(BaseModel):
    id: str
    worker_id: str
    media_type: str
    path: str
    caption: str
    received_at_utc: str


class LedgerState(BaseModel):
    budget_egp: int
    spend_requests: list[SpendRequest] = Field(default_factory=list)
    outbound: list[Outbound] = Field(default_factory=list)
    inbound: list[Inbound] = Field(default_factory=list)
    attachments: list[Attachment] = Field(default_factory=list)
    counters: dict[str, int] = Field(default_factory=dict)


def _text(value: str, limit: int = 4000) -> str:
    value = value.strip()
    if not value:
        raise LedgerError("Text is required")
    if len(value) > limit:
        raise LedgerError(f"Text exceeds {limit} characters")
    return value


class Ledger:
    def __init__(self, clock: SimClock, budget_egp: int, worker_ids: list[str], deadline_iso: str) -> None:
        self.clock = clock
        self.names: dict[str, str] = {}
        self.worker_ids = worker_ids
        self.deadline_iso = deadline_iso
        self.state = LedgerState(budget_egp=budget_egp)
        self.lock = threading.RLock()

    def _now(self) -> str:
        return self.clock.now().isoformat()

    def _id(self, prefix: str) -> str:
        n = self.state.counters.get(prefix, 0) + 1
        self.state.counters[prefix] = n
        return f"{prefix}-{n:06d}"

    def _worker(self, worker_id: str) -> None:
        if worker_id not in self.worker_ids:
            raise LedgerError("Unknown worker", 404)

    def budget(self) -> dict[str, int | str]:
        committed = sum(r.amount_egp for r in self.state.spend_requests if r.status in ("committed", "cancellation_pending"))
        paid = sum(r.reported_paid_egp for r in self.state.spend_requests if r.status == "reported_paid")
        return {"currency": "EGP", "limit_egp": self.state.budget_egp, "committed_egp": committed,
                "reported_paid_egp": paid, "available_egp": self.state.budget_egp - committed - paid}

    def queue_message(self, worker_id: str, text: str, context_id: str | None = None) -> Outbound:
        self._worker(worker_id)
        with self.lock:
            row = Outbound(id=self._id("out"), worker_id=worker_id, text=_text(text), context_id=context_id,
                           queued_at_utc=self._now())
            self.state.outbound.append(row)
            return row.model_copy()

    def request_spend(self, worker_id: str, amount: int, purpose: str, idempotency_key: str) -> SpendRequest:
        self._worker(worker_id)
        if amount <= 0:
            raise LedgerError("Spend amount must be positive EGP")
        purpose = _text(purpose)
        key = _text(idempotency_key, 200)
        with self.lock:
            prior = next((r for r in self.state.spend_requests if r.idempotency_key == key), None)
            if prior is not None:
                if (prior.worker_id, prior.amount_egp, prior.purpose) != (worker_id, amount, purpose):
                    raise LedgerError("Idempotency key reused for a different request", 409)
                return prior.model_copy()
            unavailable = sum(r.amount_egp if r.status in ("committed", "cancellation_pending") else r.reported_paid_egp
                              for r in self.state.spend_requests)
            if unavailable + amount > self.state.budget_egp:
                raise LedgerError("Insufficient available budget", 409)
            row = SpendRequest(id=self._id("spend"), idempotency_key=key, worker_id=worker_id, amount_egp=amount,
                               purpose=purpose, status="committed", created_at_utc=self._now())
            self.state.spend_requests.append(row)
            self.state.outbound.append(Outbound(
                id=self._id("out"), worker_id=worker_id, notice_type="spend_authorization", context_id=row.id,
                queued_at_utc=self._now(),
                text=(f"Spend request {row.id}: up to {amount} EGP for {purpose}. Before paying, tap Verify request and "
                      "confirm ACTIVE status and the amount limit. This button-bearing notice contains the ledger's "
                      f"purpose. Do not pay based on ordinary chat text. You can also check /spend {row.id}; after "
                      f"payment, send /paid {row.id} AMOUNT. Attach a receipt if available.")))
            return row.model_copy()

    def verify(self, worker_id: str, spend_id: str) -> dict[str, str | int]:
        with self.lock:
            row = next((r for r in self.state.spend_requests if r.id == spend_id and r.worker_id == worker_id), None)
            if row is None:
                raise LedgerError("This spend notice could not be verified", 403)
            active = row.status == "committed" and self.clock.now().isoformat() < self.deadline_iso
            return {"spend_id": row.id, "status": "ACTIVE" if active else "INACTIVE", "purpose": row.purpose,
                    "amount_egp": row.amount_egp, "checked_at_utc": self._now()}

    def report_payment(self, worker_id: str, spend_id: str, amount: int, receipt: str | None = None) -> SpendRequest:
        with self.lock:
            row = next((r for r in self.state.spend_requests if r.id == spend_id), None)
            if row is None:
                raise LedgerError("Unknown spend request", 404)
            if row.worker_id != worker_id:
                raise LedgerError("Only the assigned worker can report this payment", 403)
            if row.status not in ("committed", "cancellation_pending"):
                raise LedgerError("Spend request already settled", 409)
            if amount <= 0 or amount > row.amount_egp:
                raise LedgerError("Reported payment exceeds the reservation")
            row.status = "reported_paid"
            row.reported_paid_egp = amount
            row.receipt_reference = receipt
            row.reported_paid_at_utc = self._now()
            return row.model_copy()

    def cancel_spend(self, spend_id: str) -> SpendRequest:
        with self.lock:
            row = next((r for r in self.state.spend_requests if r.id == spend_id), None)
            if row is None:
                raise LedgerError("Unknown spend request", 404)
            if row.status != "committed":
                raise LedgerError("Only an unpaid reservation can be cancelled", 409)
            row.status = "cancellation_pending"
            row.cancel_requested_at_utc = self._now()
            self.state.outbound.append(Outbound(
                id=self._id("out"), worker_id=row.worker_id, notice_type="spend_cancellation",
                context_id=spend_id + ":cancel", queued_at_utc=self._now(),
                text=(f"Spend request {spend_id} is being cancelled. Do not pay it. Tap 'Confirm I won't pay' after "
                      f"seeing this. If you already paid, report the amount with /paid {spend_id} AMOUNT instead.")))
            return row.model_copy()

    def confirm_cancelled(self, worker_id: str, spend_id: str) -> SpendRequest:
        with self.lock:
            row = next((r for r in self.state.spend_requests if r.id == spend_id and r.worker_id == worker_id), None)
            if row is None:
                raise LedgerError("Unknown assigned spend request", 404)
            if row.status != "cancellation_pending":
                raise LedgerError("No cancellation is pending", 409)
            row.status = "cancelled"
            return row.model_copy()

    def add_inbound(self, worker_id: str, text: str, attachment_id: str | None = None, agent_visible: bool = True) -> Inbound:
        with self.lock:
            row = Inbound(id=self._id("in"), worker_id=worker_id, text=text, received_at_utc=self._now(),
                          attachment_id=attachment_id, agent_visible=agent_visible)
            self.state.inbound.append(row)
            return row.model_copy()

    def add_attachment(self, worker_id: str, media_type: str, path: str, caption: str) -> Attachment:
        with self.lock:
            row = Attachment(id=self._id("file"), worker_id=worker_id, media_type=media_type, path=path,
                             caption=caption, received_at_utc=self._now())
            self.state.attachments.append(row)
            return row.model_copy()

    def agent_inbox(self) -> list[dict[str, str | bool | None]]:
        with self.lock:
            return [{**r.model_dump(), "worker_name": self.names.get(r.worker_id, "")} for r in self.state.inbound if r.agent_visible]

    def snapshot(self) -> LedgerState:
        with self.lock:
            return deepcopy(self.state)
