#!/usr/bin/env bash
# Hourly hive runner: one lane, one task, one PR (or one judged branch in the cloud).
# The agent only edits files. This script does the git work and writes the receipt,
# so every claim about "what changed", "what was fetched" and "checks passed" comes from code, not from the agent.
#
#   ops/run-hourly.sh hermes|opencode|jevx
#
# Env:
#   HIVE_CMD_HERMES / HIVE_CMD_OPENCODE / HIVE_CMD_JEVX   agent command; the prompt is appended as the last argument.
#                 "free-agent" = the built-in zero-cost agent (ops/free_agent.py). HIVE_CMD_OPENCODE defaults to
#                 "opencode run".
#   HIVE_OPEN_PR  1 (default): open a PR, JEVX reviews it. 0 (cloud): push the branch for ops/judge.py instead.
#   HIVE_HOME     per-lane worktrees and logs (default ~/.hive)
#   HIVE_TIMEOUT  seconds per agent run (default 2700)
#   HIVE_REMOTE / HIVE_BASE   default origin / main
# Compatible with macOS bash 3.2.
set -euo pipefail

LANE="${1:?usage: run-hourly.sh hermes|opencode|jevx}"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
PREFIX="$(python3 -c 'import os,sys;print(os.path.relpath(sys.argv[1],sys.argv[2]))' "$(dirname "$HERE")" "$REPO")"
REMOTE="${HIVE_REMOTE:-origin}"
BASE="${HIVE_BASE:-main}"
HIVE_HOME="${HIVE_HOME:-$HOME/.hive}"
TIMEOUT="${HIVE_TIMEOUT:-2700}"
OPEN_PR="${HIVE_OPEN_PR:-1}"

case "$LANE" in
  hermes)   CMD="${HIVE_CMD_HERMES:-}" ;;
  opencode) CMD="${HIVE_CMD_OPENCODE:-opencode run}" ;;
  jevx)     CMD="${HIVE_CMD_JEVX:-}" ;;
  *) echo "unknown lane: $LANE" >&2; exit 2 ;;
esac
if [ -z "$CMD" ]; then
  echo "set HIVE_CMD_$(echo "$LANE" | tr a-z A-Z) to the command that runs $LANE with a prompt argument" >&2
  exit 2
fi

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $LANE: $*"; }

# One run per lane at a time; a lock older than 3h is from a crashed run.
mkdir -p "$HIVE_HOME"
LOCK="$HIVE_HOME/$LANE.lock"
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +180 2>/dev/null)" ]; then rmdir "$LOCK"; fi
if ! mkdir "$LOCK" 2>/dev/null; then log "previous run still active, skipping"; exit 0; fi
TASK_ID=""
PR_OPENED=0
cleanup() {
  # A run that dies after claiming must not keep the task locked for 6 hours.
  if [ -n "$TASK_ID" ] && [ "$PR_OPENED" = 0 ]; then
    python3 "$C/ops/agentctl.py" release "$TASK_ID" >/dev/null 2>&1 || true
  fi
  rmdir "$LOCK" 2>/dev/null || true
}
trap cleanup EXIT

# Each lane works in its own worktree, so lanes run in parallel without touching each other's files.
WT="$HIVE_HOME/worktrees/$LANE"
git -C "$REPO" fetch --quiet "$REMOTE" "$BASE"
if [ ! -d "$WT" ]; then
  git -C "$REPO" worktree add --quiet --detach "$WT" "$REMOTE/$BASE"
fi
sync_to_base() {
  git fetch --quiet "$REMOTE" "$BASE"
  git checkout --quiet --detach -f "$REMOTE/$BASE"
  git clean -fdq
}
cd "$WT"
sync_to_base
C="$WT/$PREFIX"
NOTES="$C/ops/.notes.md"   # gitignored scratch file the agent writes; copied into the receipt
FETCH_LOG="$HIVE_HOME/$LANE.fetch.jsonl"   # written by code (free_agent / MCP fetch tool), outside the worktree
rm -f "$NOTES" "$FETCH_LOG"
if [ "$CMD" = "free-agent" ]; then CMD="python3 $C/ops/free_agent.py --lane $LANE"; fi
export HIVE_NOTES="$NOTES" HIVE_FETCH_LOG="$FETCH_LOG"

run_agent() {  # $1 = prompt file
  local prompt rc
  prompt="$(cat "$1")"
  # Agents start in the content folder, so OpenCode finds opencode.json (MCP) and .agents/skills there.
  # perl alarm = portable timeout (macOS has no coreutils timeout by default)
  # shellcheck disable=SC2086  # CMD is intentionally word-split into command + args
  (cd "$C" && perl -e 'alarm shift; exec @ARGV' "$TIMEOUT" $CMD "$prompt") && rc=0 || rc=$?
  if [ "$rc" = 75 ]; then log "no free LLM capacity right now (exit 75); task goes back to the queue"; exit 0; fi
  [ "$rc" = 0 ] || log "agent exited with $rc"
}

skill_for() {  # lane skill injected into the prompt (agents that load .agents/skills natively see it anyway)
  case "$LANE:$1" in
    hermes:*modules/*) echo module-page ;;
    hermes:*) echo exam-page ;;
    opencode:*) echo hive-tooling ;;
    *) echo review-agent-work ;;
  esac
}

open_pr() {  # $1 = branch, $2 = title, $3 = body file
  git push --quiet -u "$REMOTE" "HEAD:refs/heads/$1"
  gh pr create --base "$BASE" --head "$1" --title "$2" --body-file "$3"
}

if [ "$LANE" = "jevx" ]; then
  # Planner + judge. First land what was approved last hour (CI has finished by now), then review and plan
  # on the fresh main, then merge anything already approved and green.
  "$C/ops/merge_ready.sh" || log "merge_ready failed"
  sync_to_base
  python3 "$C/ops/agentctl.py" reap --hours 6 || true
  P="$HIVE_HOME/$LANE.prompt.md"
  {
    cat "$C/ops/prompts/jevx.md"
    printf '\n## Context gathered by the runner (code)\n\n### Backlog status\n```\n'
    python3 "$C/ops/agentctl.py" status || true
    printf '```\n\n### Content gate on %s\n```\n' "$BASE"
    python3 "$C/scripts/validate.py" || true
    printf '```\n\n### Open agent PRs\n```\n'
    gh pr list --state open --json number,title,headRefName,url \
      --jq '.[] | select(.headRefName | startswith("agent/")) | "#\(.number) \(.headRefName) \(.title) \(.url)"' || true
    printf '```\n'
  } > "$P"
  run_agent "$P"
  python3 "$C/scripts/validate.py" --write > /dev/null || true
  if [ -n "$(git status --porcelain)" ]; then
    BR="agent/jevx/plan-$(date -u +%Y%m%d-%H%M)"
    git add -A
    git commit --quiet -m "hive(jevx): plan and backlog update $(date -u +%Y-%m-%dT%H:%MZ)"
    printf 'Planner update from the JEVX lane. Touches only ops/tasks.toml, ops/plan/, README index and UPDATES.md.\n' > "$HIVE_HOME/jevx.body.md"
    # An older planner PR still open (CI red or slow) would conflict with this one; this run supersedes it.
    gh pr list --state open --json number,headRefName \
      --jq '.[] | select(.headRefName | startswith("agent/jevx/")) | .number' | while read -r n; do
      gh pr close "$n" --delete-branch --comment "Superseded by the next JEVX run." || true
    done
    open_pr "$BR" "hive(jevx): plan $(date -u +%Y-%m-%d\ %H:%M) UTC" "$HIVE_HOME/jevx.body.md" || log "PR creation failed"
  fi
  "$C/ops/merge_ready.sh" || log "merge_ready failed"
  exit 0
fi

# Worker lanes: claim one task, let the agent edit files, gate, receipt, PR.
python3 "$C/ops/agentctl.py" reap --hours 6 || true
set +e
TASK_JSON="$(python3 "$C/ops/agentctl.py" next "$LANE" --claim --agent "$LANE")"
rc=$?
set -e
if [ $rc -eq 3 ]; then log "no ready task"; exit 0; fi
if [ $rc -ne 0 ]; then log "agentctl failed ($rc)"; exit $rc; fi
TASK_ID="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys;print(json.load(sys.stdin)["id"])')"
TITLE="$(printf '%s' "$TASK_JSON" | python3 -c 'import json,sys;print(json.load(sys.stdin)["title"])')"
BRANCH="agent/$LANE/$TASK_ID"
STARTED="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
export HIVE_TASK_ID="$TASK_ID"
log "claimed $TASK_ID: $TITLE"
git checkout --quiet -B "$BRANCH"   # -B: a retried task may have a stale local branch

P="$HIVE_HOME/$LANE.prompt.md"
{
  cat "$C/ops/prompts/$LANE.md"
  printf '\n## Skill\n\n'
  cat "$C/.agents/skills/$(skill_for "$TITLE")/SKILL.md"
  printf '\n## Your task (from ops/tasks.toml)\n\n```json\n%s\n```\n' "$TASK_JSON"
  printf '\nWork only inside %s. Write your notes (sources opened, what you confirmed, what you could not) to %s.\n' "$C" "$NOTES"
} > "$P"
run_agent "$P"

# Workers never regenerate README index / UPDATES.md (the JEVX lane does), so parallel PRs don't conflict.
GATE_LOG="$HIVE_HOME/$LANE.gate.log"
if ! python3 "$C/scripts/validate.py" > "$GATE_LOG" 2>&1; then
  log "content gate failed, giving the agent one repair pass"
  { cat "$P"; printf '\n## The content gate failed. Fix these errors and change nothing else:\n```\n'; cat "$GATE_LOG"; printf '```\n'; } > "$P.fix"
  run_agent "$P.fix"
  if ! python3 "$C/scripts/validate.py" > "$GATE_LOG" 2>&1; then
    log "content gate still failing; releasing $TASK_ID"
    cat "$GATE_LOG"
    python3 "$C/ops/agentctl.py" release "$TASK_ID" || true
    exit 1
  fi
fi

if [ -z "$(git status --porcelain)" ] && [ "$(git rev-list --count "$REMOTE/$BASE"..HEAD)" = "0" ]; then
  log "agent made no changes; releasing $TASK_ID"
  python3 "$C/ops/agentctl.py" release "$TASK_ID" || true
  exit 0
fi

git add -A
python3 "$C/ops/agentctl.py" receipt "$TASK_ID" --lane "$LANE" --agent-cmd "$CMD" \
  --started "$STARTED" --validator-log "$GATE_LOG" --notes "$NOTES" --fetch-log "$FETCH_LOG" > /dev/null
rm -f "$NOTES"
git add -A
if [ "$OPEN_PR" = 0 ]; then
  git commit --quiet -m "[$TASK_ID] $TITLE (lane: $LANE)" -m "Hive-Publish: judge"
else
  git commit --quiet -m "[$TASK_ID] $TITLE (lane: $LANE)"
fi
# Fail early on claims the judge would reject anyway: scope, and "official" without fetched evidence.
if ! git diff --name-only "$REMOTE/$BASE"...HEAD | python3 "$C/scripts/hive_gate.py" --branch "$BRANCH" \
   || ! python3 "$C/scripts/evidence_gate.py" --base "$REMOTE/$BASE" --branch "$BRANCH"; then
  log "lane scope or evidence gate failed; releasing $TASK_ID"
  exit 1
fi
git push --quiet -u "$REMOTE" "HEAD:refs/heads/$BRANCH"
PR_OPENED=1   # the work branch now holds the task; closing/rejecting it with branch deletion frees it
if [ "$OPEN_PR" = 0 ]; then
  log "pushed $BRANCH for the cloud judge"
  exit 0
fi
gh pr create --base "$BASE" --head "$BRANCH" --title "[$TASK_ID] $TITLE" --body-file "$C/ops/done/$TASK_ID.md" \
  || { log "PR creation failed; branch $BRANCH is pushed, open the PR by hand or delete the branch"; exit 1; }
log "opened PR for $TASK_ID"
