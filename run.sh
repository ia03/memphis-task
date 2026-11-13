#!/usr/bin/env bash
# Run one Harbor job config. Needs Docker, Harbor and a Codex sign-in file (CODEX_AUTH_JSON).
set -euo pipefail
cd "$(dirname "$0")"
: "${CODEX_AUTH_JSON:?set CODEX_AUTH_JSON to your Codex auth.json path}"
python3 scripts/check_signin.py "$CODEX_AUTH_JSON" --hours 12
# Harbor 0.23 gives the agent container the sign-in only through CODEX_AUTH_JSON_PATH; without it Codex sends an empty API key.
export CODEX_AUTH_JSON_PATH="$CODEX_AUTH_JSON"
mkdir -p private
[ -s private/agent-token ] || openssl rand -hex 16 > private/agent-token
[ -s private/grader-token ] || openssl rand -hex 16 > private/grader-token
export PYTHONPATH="$PWD"
export SIM_AGENT_TOKEN="$(cat private/agent-token)"
export SIM_GRADER_TOKEN="$(cat private/grader-token)"
exec harbor run -y -c "$1"
