"""Harbor Claude Code agent for Memphis, run the way MemphisCodex runs the measured agent: no web tools beyond the task's own,
the project clock held while the model API refuses requests, and the session resumed after transient failures."""

from __future__ import annotations

import asyncio
import json
import os
import shlex

from harbor.agents.installed.base import NonZeroAgentExitCodeError
from harbor.agents.installed.claude_code import ClaudeCode
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

# Claude Code's built-in web tools; the task's web.py is the agent's only web, as for Codex (web_search disabled).
CLOSED_TOOLS = "WebSearch,WebFetch"
TRANSIENT = ("api_retry", "overloaded", "Overloaded", "529", "429", "rate_limit", "rate limit", "usage limit",
             "hit your limit", "Connection error", "ECONNRESET", "socket hang up", "fetch failed", "timed out",
             "API Error: 5")
SIGNIN_REFUSED = ("401", "Invalid API key", "authentication_error", "OAuth token has expired", "Please run /login")
WATCH_SECONDS = 5
CONTINUE = "Continue working on the task."


class MemphisClaude(ClaudeCode):
    MAX_RESUMES = 60

    @property
    def _log(self) -> str:
        return (self.environment_logs_dir / "claude-code.txt").as_posix()

    def build_cli_flags(self) -> str:
        base = super().build_cli_flags()
        if "--disallowedTools" in base:
            return base
        return f"{base} --disallowedTools {CLOSED_TOOLS}".strip()

    async def _grader(self, environment: BaseEnvironment, path: str) -> None:
        token = os.environ.get("SIM_GRADER_TOKEN", "")
        await environment.exec(command="curl -s -X POST -H " + shlex.quote(f"Authorization: Bearer {token}") +
                               f" -H 'Content-Type: application/json' -d '{{}}' http://sim:8787/grader/{path}")

    async def _lines(self, environment: BaseEnvironment, n: int) -> list[str]:
        result = await environment.exec(command=f"tail -n {n} {self._log} 2>/dev/null || true")
        return [line for line in (result.stdout or "").splitlines() if line.strip()]

    async def _result(self, environment: BaseEnvironment) -> tuple[dict | None, str]:
        """The session's closing stream-json result event, if any, and the log's tail."""
        lines = await self._lines(environment, 40)
        for line in reversed(lines):
            if '"type":"result"' in line.replace(" ", ""):
                try:
                    return json.loads(line), "\n".join(lines)
                except json.JSONDecodeError:
                    break
        return None, "\n".join(lines)

    @staticmethod
    def _refused(line: str) -> bool:
        """Whether a stream-json line shows a model request being refused. Claude Code also reports plan usage in
        rate_limit_event lines; only one whose status is "rejected" is a refusal."""
        if '"type":"result"' in line.replace(" ", ""):
            return False
        if '"rate_limit_event"' in line:
            try:
                return json.loads(line)["rate_limit_info"]["status"] == "rejected"
            except (json.JSONDecodeError, KeyError, TypeError):
                return False
        return any(t in line for t in TRANSIENT)

    async def _watch_refusals(self, environment: BaseEnvironment, stop: asyncio.Event) -> None:
        """While Claude Code retries a refused model request, hold the project clock; release it when the next event shows
        the model answered. Rate limits then cost wall time, never the agent's project time."""
        held = False
        while not stop.is_set():
            try:
                last = (await self._lines(environment, 1) or [""])[-1]
                refused = self._refused(last)
                if refused and not held:
                    await self._grader(environment, "hold")
                    held = True
                elif held and last and not refused:
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
            finally:
                stop.set()
                await watcher
            result, tail = await self._result(environment)
            await environment.exec(command=f"cp {self._log} {self._log[:-4]}-part{part}.txt 2>/dev/null || true")
            if result is not None and not result.get("is_error"):
                return
            text = json.dumps(result) if result is not None else tail
            if any(s in text for s in SIGNIN_REFUSED) or not any(t in text for t in TRANSIENT):
                raise NonZeroAgentExitCodeError(f"Claude Code ended with a non-transient error: {text[-500:]}")
            await self._grader(environment, "hold")
            await asyncio.sleep(delay)
            delay = min(delay * 2, 600.0)
            self._resume = True
        raise NonZeroAgentExitCodeError("Claude Code kept failing on model capacity; trial is unscored")
