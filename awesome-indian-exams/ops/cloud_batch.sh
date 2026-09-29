#!/bin/bash
# Cloud batch runner for the hive. Used by .github/workflows/hive-cloud.yml, and dry-runnable on the Mac.
#
# ONE job: 6 workers (3 hermes-lane + 3 opencode-lane) run in parallel, each looping until 40 minutes are used
# or there is no ready task. Everything runs against a LOCAL bare hub (/tmp/hub.git) so claims and agent/*
# branches NEVER reach GitHub. Then the judge publishes approved work onto the hub's main, and at most ONE
# commit is pushed to origin/main.
#
#   HIVE_CLOUD_DRY=1 bash ops/cloud_batch.sh     # temp copy of the content folder + the tests' mock LLM; never pushes
#   bash ops/cloud_batch.sh                       # real run (GitHub Actions); pushes at most one commit
#
# Env:
#   HIVE_MAC_LAST_SEEN   unix seconds the Mac's publisher last ran; skip if now - it < 7200
#   HIVE_CLOUD_DIR       scratch dir (default /tmp/hive-cloud-$$); the test sets it to inspect hub/origin
#   HIVE_CLOUD_MAX_TASKS tasks per worker (default 1 in dry mode, 0 = unlimited = until the 40-minute budget)
# bash 3.2 compatible (macOS default): no arrays, no [[ ]], no ${var,,}.
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTENT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$CONTENT/.." && pwd)"
PREFIX="$(basename "$CONTENT")"
CLOUD_DIR="${HIVE_CLOUD_DIR:-/tmp/hive-cloud-$$}"
HUB_DIR="$CLOUD_DIR/hub.git"
HIVE_HOME="$CLOUD_DIR/home"
MAX_WORKERS=6
WORKER_TIMEOUT=2400   # 40 minutes in seconds
START_TIME="$(date +%s)"
DRY_RUN="${HIVE_CLOUD_DRY:-0}"
if [ "$DRY_RUN" = "1" ]; then
  MAX_TASKS="${HIVE_CLOUD_MAX_TASKS:-1}"
else
  MAX_TASKS="${HIVE_CLOUD_MAX_TASKS:-0}"
fi

log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }

# --- Step 1: Skip unless the Mac is away (HIVE_MAC_LAST_SEEN unix seconds, set hourly by the Mac's publisher) ---
MAC_LAST_SEEN="${HIVE_MAC_LAST_SEEN:-0}"
case "$MAC_LAST_SEEN" in ''|*[!0-9]*) MAC_LAST_SEEN=0 ;; esac
NOW="$(date +%s)"
if [ "$MAC_LAST_SEEN" -gt 0 ] && [ $((NOW - MAC_LAST_SEEN)) -lt 7200 ]; then
  log "Mac was seen $((NOW - MAC_LAST_SEEN)) seconds ago (< 7200); skipping cloud run"
  exit 0
fi
log "Mac last seen ${MAC_LAST_SEEN} seconds ago (0 = never); proceeding with cloud run"

# --- Steps 2-3: a working repo + a LOCAL bare hub. Agent/branch/claim refs go to 'hub' (HIVE_REMOTE), never 'origin' ---
rm -rf "$CLOUD_DIR"
mkdir -p "$CLOUD_DIR" "$HIVE_HOME"

if [ "$DRY_RUN" = "1" ]; then
  REPO="$CLOUD_DIR/repo"
  log "DRY RUN: copying the content folder to $REPO/$PREFIX"
  mkdir -p "$REPO/$PREFIX"
  rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='*.bak-*' "$CONTENT/" "$REPO/$PREFIX/"
  cd "$REPO"
  git init -q
  git symbolic-ref HEAD refs/heads/main
  git add -A
  git commit -q -m "dry-run seed"
else
  REPO="$REPO_ROOT"
  cd "$REPO"
  log "Real run: using the Actions checkout at $REPO"
fi
git config user.name "hive-bot"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
BASE_SHA="$(git rev-parse HEAD)"
log "Base commit $BASE_SHA"

git clone --bare "$REPO" "$HUB_DIR" >/dev/null 2>&1 || { log "could not clone the local hub"; exit 1; }
git remote add hub "$HUB_DIR" 2>/dev/null || git remote set-url hub "$HUB_DIR"
git push --quiet hub "HEAD:refs/heads/main"

if [ "$DRY_RUN" = "1" ]; then
  git clone --bare "$REPO" "$CLOUD_DIR/origin.git" >/dev/null 2>&1
  git remote add origin "$CLOUD_DIR/origin.git"
  log "ORIGIN_REPO=$CLOUD_DIR/origin.git"
fi

# Worker environment: agents are the built-in free-agent, they push only agent/* branches to the hub.
export HIVE_REMOTE=hub
export HIVE_BASE=main
export HIVE_HOME
export HIVE_WHERE=cloud
export HIVE_OPEN_PR=0
export HIVE_SANDBOX=1
export HIVE_CMD_HERMES=free-agent
export HIVE_CMD_OPENCODE=free-agent
export HIVE_FALLBACK=free-agent
export HIVE_NO_TASK_EXIT=3
export HIVE_TIMEOUT="${HIVE_TIMEOUT:-$WORKER_TIMEOUT}"

# --- Step 4: workers loop over the existing runner ops/run-hourly.sh until the budget is used or no task ---
run_worker() {
  LANE="$1"
  WORKER="$2"
  DONE_TASKS=0
  log "Worker $WORKER ($LANE) starting"
  while :; do
    if [ "$MAX_TASKS" -gt 0 ] && [ "$DONE_TASKS" -ge "$MAX_TASKS" ]; then
      log "Worker $WORKER: per-worker task cap ($MAX_TASKS) reached"
      break
    fi
    NOW="$(date +%s)"
    if [ $((NOW - START_TIME)) -ge "$WORKER_TIMEOUT" ]; then
      log "Worker $WORKER: 40-minute budget used"
      break
    fi
    set +e
    bash "$REPO/$PREFIX/ops/run-hourly.sh" "$LANE" "$WORKER" > "$HIVE_HOME/$WORKER.log" 2>&1
    RC=$?
    set -e
    tail -n 4 "$HIVE_HOME/$WORKER.log" | sed "s/^/[$WORKER] /" || true
    if [ "$RC" -eq 3 ]; then
      log "Worker $WORKER: no ready task"
      break
    fi
    [ "$RC" -eq 0 ] || log "Worker $WORKER: run-hourly exited $RC"
    DONE_TASKS=$((DONE_TASKS + 1))
  done
  log "Worker $WORKER finished ($DONE_TASKS task(s))"
}

log "Starting $MAX_WORKERS workers (3 hermes + 3 opencode)"
PIDS=""
for i in 1 2 3; do
  run_worker hermes "hermes-$i" &
  PIDS="$PIDS $!"
done
for i in 1 2 3; do
  run_worker opencode "opencode-$i" &
  PIDS="$PIDS $!"
done
for PID in $PIDS; do
  wait "$PID" || true
done

# --- Step 5: judge the hub's agent branches and publish the approved ones onto the hub's main ---
log "All workers finished. Running the judge (--publish --limit 30) against the hub"
cd "$REPO"
set +e
python3 "$REPO/$PREFIX/ops/judge.py" --publish --limit 30 2>&1 | while IFS= read -r line; do
  log "JUDGE: $line"
done
JUDGE_RC=${PIPESTATUS[0]}
set -e
[ "$JUDGE_RC" -eq 0 ] || log "Judge exited with $JUDGE_RC"

# --- Step 6: at most ONE commit to origin/main ---
git fetch --quiet hub main
HUB_TREE="$(git rev-parse "hub/main^{tree}" 2>/dev/null || echo "")"
BASE_TREE="$(git rev-parse "$BASE_SHA^{tree}")"
if [ -z "$HUB_TREE" ] || [ "$HUB_TREE" = "$BASE_TREE" ]; then
  log "No hive changes; nothing to push"
  exit 0
fi
STAT="$(git diff --shortstat "$BASE_SHA" "hub/main" | sed 's/^ //')"
MSG="Cloud hive update $(date -u '+%Y-%m-%d %H:%M') UTC: $STAT"

if [ "$DRY_RUN" = "1" ]; then
  COMMIT="$(git commit-tree "$HUB_TREE" -p "$BASE_SHA" -m "$MSG")"
  COUNT="$(git rev-list --count "$BASE_SHA".."hub/main")"
  log "DRY RUN: hub/main is $COUNT commit(s) ahead of the base; GitHub would receive ONE commit"
  log "DRY RUN: candidate commit $COMMIT"
  log "DRY RUN complete; nothing was pushed"
  exit 0
fi

# Real run. If origin/main moved meanwhile (Mac publish, a merged PR), re-apply the hive's diff on top of it
# instead of overwriting it; retry once on a non-fast-forward rejection.
ATTEMPT=1
while [ "$ATTEMPT" -le 2 ]; do
  git fetch --quiet origin main
  if [ "$(git rev-parse origin/main)" = "$BASE_SHA" ]; then
    COMMIT="$(git commit-tree "$HUB_TREE" -p "$BASE_SHA" -m "$MSG")"
  else
    log "origin/main moved during the run; re-applying the hive's changes on top of it"
    git checkout --quiet -f --detach origin/main
    if ! git diff --binary "$BASE_SHA" "hub/main" | git apply --3way --index; then
      log "hive changes conflict with the new origin/main; nothing pushed (the next run retries)"
      exit 0
    fi
    COMMIT="$(git commit-tree "$(git write-tree)" -p origin/main -m "$MSG")"
  fi
  if git push --quiet origin "$COMMIT:refs/heads/main"; then
    log "Pushed $COMMIT to origin/main"
    break
  fi
  log "push rejected (non-fast-forward); retrying ($ATTEMPT/2)"
  ATTEMPT=$((ATTEMPT + 1))
  if [ "$ATTEMPT" -gt 2 ]; then
    log "nothing pushed; the next run retries"
  fi
done

log "Cloud batch run complete"
