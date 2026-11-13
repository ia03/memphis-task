"""Project time: 1x while the agent works, paused while the world simulator thinks, jumps on sleep."""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

CAIRO = timezone(timedelta(hours=3))


def parse(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("A time zone is required")
    return result.astimezone(timezone.utc)


class SimClock:
    def __init__(self, start: datetime, end: datetime) -> None:
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("A time zone is required")
        self._project = start.astimezone(timezone.utc)
        self._end = end.astimezone(timezone.utc)
        self._wall = time.monotonic()
        self._paused = 0
        self._held = False
        self._lock = threading.RLock()
        self._freeze_gap: float | None = None
        self.frozen_seconds = 0.0

    def detect_freezes(self, gap: float) -> None:
        """With a regular ticker calling now(), a longer step means the process was frozen (host sleep); it is not project time."""
        self._freeze_gap = gap

    def hold(self) -> None:
        with self._lock:
            if self._held:
                return
            self.now()
            self._held = True
            self._paused += 1

    def release(self) -> None:
        with self._lock:
            if self._held:
                self._held = False
                self._paused -= 1
                self._wall = time.monotonic()

    def now(self) -> datetime:
        with self._lock:
            if self._paused == 0:
                wall = time.monotonic()
                step = wall - self._wall
                if self._freeze_gap is not None and step > self._freeze_gap:
                    self.frozen_seconds += step
                    step = 0.0
                self._project = min(self._end, self._project + timedelta(seconds=step))
                self._wall = wall
            return self._project

    @property
    def end(self) -> datetime:
        return self._end

    @contextmanager
    def paused(self):
        with self._lock:
            self.now()
            self._paused += 1
        try:
            yield
        finally:
            with self._lock:
                self._paused -= 1
                self._wall = time.monotonic()

    def jump_to(self, target: datetime) -> datetime:
        with self._lock:
            current = self.now()
            if target > current:
                self._project = min(self._end, target.astimezone(timezone.utc))
            self._wall = time.monotonic()
            return self._project
