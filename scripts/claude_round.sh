#!/usr/bin/env bash
# The Claude Code round on the frozen v12.0-rc17 tasks, unattended on a cloud VM: a test trial, a usage check, the ten trials
# (void ones run again once), an audit and a friction count of each, then the VM deletes itself. Every stage is copied to the
# results bucket, so nothing depends on the laptop and nothing is lost when the VM goes.
#
#   BUCKET=gs://... sudo systemd-run --unit memphis-round --uid "$USER" --setenv HOME="$HOME" --setenv BUCKET="$BUCKET" \
#     --working-directory "$PWD" bash scripts/claude_round.sh
#
# Needs ~/.codex/auth.json (world model, `codex login --device-auth`) and ~/.claude-token (agent and auditors,
# `claude setup-token`). Progress: `gcloud storage cat $BUCKET/status.txt`.
set -uo pipefail
cd "$(dirname "$0")/.."
: "${BUCKET:?set BUCKET to the results bucket}"
TAG=v12.0-rc17
export PATH="$PWD/.venv/bin:/usr/local/bin:/usr/bin:/bin:/snap/bin"
export CODEX_AUTH_JSON="$HOME/.codex/auth.json"
export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.claude-token")"
export CLAUDE_FORCE_OAUTH=1
NOTE="In this trial the agent is Claude Opus 5.5 run through Claude Code (harbor_ext/memphis_claude.py), not Codex: its transcript is agent/claude-code-part*.txt then agent/claude-code.txt (stream-json events)."

status() { echo "$(date -u +%FT%TZ) $*" | tee -a status.txt; gcloud storage cp -q status.txt "$BUCKET/status.txt"; }
upload() { gcloud storage rsync -q -r jobs "$BUCKET/jobs"; [ -d audits-claude ] && gcloud storage rsync -q -r audits-claude "$BUCKET/audits"; [ -d friction-claude ] && gcloud storage rsync -q -r friction-claude "$BUCKET/friction"; true; }
finish() { status "$1"; upload; status "deleting this VM"; gcloud compute instances delete "$(hostname -s)" --zone us-central1-a --quiet; exit 0; }
wait_for_help() { status "STOPPED, needs a person: $1 (the VM stays up until its 96-hour timer)"; upload; exit 1; }
usage() { python3 scripts/codex_usage.py 2>/dev/null || echo '{}'; }

( while sleep 600; do upload; done ) & SYNC=$!
trap 'kill $SYNC 2>/dev/null' EXIT

status "checking sign-ins"
# The sign-in must outlast the whole round: once its token expires, parallel copies renewing it get it revoked.
python3 scripts/check_signin.py "$CODEX_AUTH_JSON" --hours 72 || wait_for_help "the Codex sign-in for the world model failed or expires within 72 hours"
claude -p "Reply with the single word OK." --model claude-opus-5-5 | grep -q OK || wait_for_help "the Claude sign-in failed"

BEFORE=$(usage)
status "Codex usage before the test trial: $BEFORE"
python3 scripts/claude_tasks.py "$HOME/tasks-c0" --job c0-test --seeds 10 --conds unhinted
status "test trial started (seed 10 unhinted)"
./run.sh "$HOME/tasks-c0/c0-test.yaml" > jobs-c0-test.log 2>&1
[ "$(python3 scripts/round_trials.py count jobs/c0-test)" = 1 ] || wait_for_help "the test trial did not run; read jobs-c0-test.log"
python3 scripts/check_trials.py jobs/c0-test | tee -a status.txt || wait_for_help "the test trial is void; read jobs/c0-test"
AFTER=$(usage)
status "Codex usage after the test trial: $AFTER"
read -r N WHY < <(python3 scripts/round_trials.py gate "$BEFORE" "$AFTER" jobs/c0-test)
[ "${N:-0}" -gt 0 ] || wait_for_help "$WHY; upgrade a plan or wait for its reset"
status "usage allows the round, $N trials at a time: $WHY"

python3 scripts/claude_tasks.py "$HOME/tasks-c1" --job c1
sed -i "s/^n_concurrent_trials: .*/n_concurrent_trials: $N/" "$HOME/tasks-c1/c1.yaml"
status "round c1 started: 10 trials, $N at a time"
./run.sh "$HOME/tasks-c1/c1.yaml" > jobs-c1.log 2>&1
[ "$(python3 scripts/round_trials.py count jobs/c1)" = 10 ] || wait_for_help "round c1 did not run all ten trials; read jobs-c1.log"
python3 scripts/check_trials.py jobs/c1 >> status.txt
RERUNS=(jobs/c1)
while read -r seed cond; do
  [ -n "$seed" ] || continue
  status "running void trial again: seed $seed $cond"
  python3 scripts/claude_tasks.py "$HOME/tasks-c1b-$seed-$cond" --job "c1b-$seed-$cond" --seeds "$seed" --conds "$cond"
  ./run.sh "$HOME/tasks-c1b-$seed-$cond/c1b-$seed-$cond.yaml" >> jobs-c1b.log 2>&1
  RERUNS+=("jobs/c1b-$seed-$cond")
done < <(python3 scripts/round_trials.py void jobs/c1)
upload
status "trials done; auditing"

# The audits use the measured version's own audit prompt, whose paths (the hint the agent saw) point into that version.
rm -rf /tmp/rc17 && git worktree prune && git worktree add -f /tmp/rc17 "$TAG" > /dev/null 2>&1
mkdir -p audits-claude friction-claude
python3 scripts/round_trials.py valid "${RERUNS[@]}" > valid-trials.txt
[ -s valid-trials.txt ] || wait_for_help "no valid trial to audit"
audit() {
  local dir=$1 slug=$2 hinted=""
  [[ $slug == *-hinted ]] && hinted="--hinted"
  python3 /tmp/rc17/scripts/audit_prompt.py "$dir" "audits-claude/audit-$slug.md" $hinted --note "$NOTE" > "/tmp/prompt-$slug.txt"
  claude -p "$(cat /tmp/prompt-$slug.txt)" --model claude-opus-5-5 --permission-mode bypassPermissions \
    --disallowedTools WebSearch,WebFetch > "audits-claude/audit-$slug.log" 2>&1
  python3 paper/friction_inputs.py "$dir" "friction-claude/in/$slug"
  claude -p "$(cat paper/friction_guide.md)

Your trial's folder: $PWD/friction-claude/in/$slug. Trial slug: $slug. Output path: $PWD/friction-claude/$slug.json." \
    --model claude-opus-5-5 --permission-mode bypassPermissions --disallowedTools WebSearch,WebFetch \
    > "friction-claude/$slug.log" 2>&1
}
export -f audit; export NOTE
xargs -P 5 -L 1 bash -c 'audit "$0" "$1"' < valid-trials.txt
upload
finish "round done: $(wc -l < valid-trials.txt) valid trials audited and coded"
