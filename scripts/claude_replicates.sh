#!/usr/bin/env bash
# Two more Claude Code trials per seed and condition on the frozen v12.0-rc17 tasks (rounds c2 and c3, set up exactly as
# round c1), unattended on a cloud VM. The first trial (c2, seed 10 unhinted) also measures Codex and Claude usage; it counts
# like the others. Then the other 19 trials (void ones run again once), an audit and a friction count of each, and the VM
# deletes itself. Any failure after the sign-in check uploads what there is and deletes the VM too, so it never sits idle.
#
#   BUCKET=gs://... sudo systemd-run --unit memphis-replicates --uid "$USER" --setenv HOME="$HOME" --setenv BUCKET="$BUCKET" \
#     --working-directory "$PWD" bash scripts/claude_replicates.sh
#
# Needs ~/.codex/auth.json (world model, `codex login --device-auth`) and ~/.claude-token (agent and auditors,
# `claude setup-token`). Progress: `gcloud storage cat $BUCKET/replicates/status.txt`.
set -uo pipefail
cd "$(dirname "$0")/.."
: "${BUCKET:?set BUCKET to the results bucket}"
OUT="$BUCKET/replicates"
TAG=v12.0-rc17
export PATH="$PWD/.venv/bin:/usr/local/bin:/usr/bin:/bin:/snap/bin"
export CODEX_AUTH_JSON="$HOME/.codex/auth.json"
export CLAUDE_CODE_OAUTH_TOKEN="$(cat "$HOME/.claude-token")"
export CLAUDE_FORCE_OAUTH=1
NOTE="In this trial the agent is Claude Opus 5.5 run through Claude Code (harbor_ext/memphis_claude.py), not Codex: its transcript is agent/claude-code-part*.txt then agent/claude-code.txt (stream-json events)."

status() { echo "$(date -u +%FT%TZ) $*" | tee -a status.txt; gcloud storage cp -q status.txt "$OUT/status.txt"; }
upload() {
  gcloud storage rsync -q -r jobs "$OUT/jobs"
  [ -d audits-claude ] && gcloud storage rsync -q -r audits-claude "$OUT/audits"
  [ -d friction-claude ] && gcloud storage rsync -q -r friction-claude "$OUT/friction"
  for f in jobs-*.log valid-trials.txt; do [ -f "$f" ] && gcloud storage cp -q "$f" "$OUT/logs/$f"; done
  true
}
delete_vm() { status "deleting this VM"; gcloud compute instances delete "$(hostname -s)" --zone us-central1-a --quiet; }
finish() { status "$1"; upload; delete_vm; exit 0; }
give_up() { status "STOPPED: $1"; upload; delete_vm; exit 1; }
usage() { python3 scripts/codex_usage.py 2>/dev/null || echo '{}'; }
run_job() {  # JOB [SKIP_TASK]: build the ten tasks (less SKIP_TASK), run them N at a time, then run each void trial again once
  local job=$1 skip=${2:-}
  python3 scripts/claude_tasks.py "$HOME/tasks-$job" --job "$job"
  if [ -n "$skip" ]; then rm -rf "$HOME/tasks-$job/$skip"; sed -i "\#/$skip\$#d" "$HOME/tasks-$job/$job.yaml"; fi
  sed -i "s/^n_concurrent_trials: .*/n_concurrent_trials: $N/" "$HOME/tasks-$job/$job.yaml"
  ./run.sh "$HOME/tasks-$job/$job.yaml" > "jobs-$job.log" 2>&1
  python3 scripts/check_trials.py "jobs/$job" >> status.txt
  while read -r seed cond; do
    [ -n "$seed" ] || continue
    status "running void trial again: $job seed $seed $cond"
    python3 scripts/claude_tasks.py "$HOME/tasks-${job}b-$seed-$cond" --job "${job}b-$seed-$cond" --seeds "$seed" --conds "$cond"
    ./run.sh "$HOME/tasks-${job}b-$seed-$cond/${job}b-$seed-$cond.yaml" >> "jobs-${job}b.log" 2>&1
  done < <(python3 scripts/round_trials.py void "jobs/$job")
  upload
}

( while sleep 600; do upload; done ) & SYNC=$!
trap 'kill $SYNC 2>/dev/null' EXIT

status "checking sign-ins"
# The sign-in must outlast the whole run: once its token expires, parallel copies renewing it get it revoked.
python3 scripts/check_signin.py "$CODEX_AUTH_JSON" --hours 20 || { status "STOPPED, needs a person: the Codex sign-in failed or expires within 20 hours"; exit 1; }
claude -p "Reply with the single word OK." --model claude-opus-5-5 | grep -q OK || { status "STOPPED, needs a person: the Claude sign-in failed"; exit 1; }

BEFORE=$(usage)
status "Codex usage before the first trial: $BEFORE"
N=1
python3 scripts/claude_tasks.py "$HOME/tasks-c2a" --job c2a --seeds 10 --conds unhinted
status "first trial started (c2, seed 10 unhinted)"
./run.sh "$HOME/tasks-c2a/c2a.yaml" > jobs-c2a.log 2>&1
[ "$(python3 scripts/round_trials.py count jobs/c2a)" = 1 ] || give_up "the first trial did not run; read logs/jobs-c2a.log"
SKIP=memphis-seed10-unhinted; LEFT=19
python3 scripts/check_trials.py jobs/c2a | tee -a status.txt || { SKIP=""; LEFT=20; status "the first trial is void; round c2 runs seed 10 unhinted again"; }
AFTER=$(usage)
status "Codex usage after the first trial: $AFTER"
read -r N WHY < <(python3 scripts/round_trials.py gate "$BEFORE" "$AFTER" jobs/c2a "$LEFT")
[ "${N:-0}" -gt 0 ] || give_up "$WHY"
status "usage allows the other $LEFT trials, $N at a time: $WHY"

status "round c2 started: $((LEFT - 10)) trials"
run_job c2 $SKIP
status "round c3 started: 10 trials"
run_job c3
status "trials done; auditing"

# The audits use the measured version's own audit prompt, whose paths (the hint the agent saw) point into that version.
rm -rf /tmp/rc17 && git worktree prune && git worktree add -f /tmp/rc17 "$TAG" > /dev/null 2>&1
mkdir -p audits-claude friction-claude
{ python3 scripts/round_trials.py valid --round c2 jobs/c2a jobs/c2 jobs/c2b-*
  python3 scripts/round_trials.py valid --round c3 jobs/c3 jobs/c3b-*; } > valid-trials.txt
[ -s valid-trials.txt ] || give_up "no valid trial to audit"
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
finish "replicates done: $(wc -l < valid-trials.txt) valid trials audited and coded"
