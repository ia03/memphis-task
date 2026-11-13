"""Harbor Codex agent that survives model capacity and transport failures without costing project time."""

from __future__ import annotations

import asyncio
import os
import shlex

from harbor.agents.installed.base import NonZeroAgentExitCodeError
from harbor.agents.installed.codex import Codex
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

TRANSIENT = ("Selected model is at capacity", "stream disconnected", "connection reset", "service unavailable",
             "request timed out", "Reconnecting", "rate limit reached", "429", "Too Many Requests")
SIGNIN_REFUSED = ("401 Unauthorized",)  # a missing or rejected sign-in never recovers by waiting
WATCH_SECONDS = 5
CONTINUE = "Continue working on the task."


class MemphisCodex(Codex):
    MAX_RESUMES = 60
    CLOSED_FEATURES = ("apps", "browser_use", "browser_use_external", "computer_use")

    def build_cli_flags(self) -> str:
        closed = " ".join(f"--disable {f}" for f in self.CLOSED_FEATURES)
        base = super().build_cli_flags()
        return f"{base} {closed}".strip()

    async def _tail(self, environment: BaseEnvironment) -> str:
        result = await environment.exec(command="tail -c 4000 /logs/agent/codex.txt 2>/dev/null || true")
        return result.stdout or ""

    async def _grader(self, environment: BaseEnvironment, path: str) -> None:
        token = os.environ.get("SIM_GRADER_TOKEN", "")
        await environment.exec(command="curl -s -X POST -H " + shlex.quote(f"Authorization: Bearer {token}") +
                               f" -H 'Content-Type: application/json' -d '{{}}' http://sim:8787/grader/{path}")

    async def _watch_refusals(self, environment: BaseEnvironment, stop: asyncio.Event) -> None:
        """While Codex retries a refused model request ("Reconnecting ..." in its log), hold the project clock; release it when
        the next event shows the model answered. Rate limits then cost wall time, never the agent's project time."""
        held = False
        while not stop.is_set():
            try:
                last = (await environment.exec(command="tail -n 1 /logs/agent/codex.txt 2>/dev/null || true")).stdout or ""
                refused = '"type":"error"' in last and any(t in last for t in TRANSIENT)
                if refused and not held:
                    await self._grader(environment, "hold")
                    held = True
                elif held and last.strip() and not refused:
                    await self._grader(environment, "release")
                    held = False
            except Exception:  # noqa: BLE001 - the watcher must never stop the agent
                pass
            try:
                await asyncio.wait_for(stop.wait(), WATCH_SECONDS)
            except asyncio.TimeoutError:
                pass

    async def run(self, instruction: str, environment: BaseEnvironment, context: AgentContext) -> None:
        delay = 30.0
        for part in range(self.MAX_RESUMES + 1):
            stop = asyncio.Event()
            watcher = asyncio.create_task(self._watch_refusals(environment, stop))
            try:
                await super().run(instruction if part == 0 else CONTINUE, environment, context)
                failed = False
            except NonZeroAgentExitCodeError:
                failed = True
            finally:
                stop.set()
                await watcher
            tail = await self._tail(environment)
            transient = (any(t in tail for t in TRANSIENT) and '"turn.failed"' in tail
                         and not any(t in tail for t in SIGNIN_REFUSED))
            await environment.exec(command=f"cp /logs/agent/codex.txt /logs/agent/codex-part{part}.txt 2>/dev/null || true")
            if not transient:
                if failed:
                    raise NonZeroAgentExitCodeError("Codex exited with a non-transient error")
                return
            await self._grader(environment, "hold")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 600.0)
            self._resume = True
        raise NonZeroAgentExitCodeError("Codex kept failing on model capacity; trial is unscored")
