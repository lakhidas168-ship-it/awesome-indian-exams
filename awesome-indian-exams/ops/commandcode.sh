#!/usr/bin/env bash
# Command Code (GOAT plan) as a hive worker: one headless run per task; backs off when credits or rate limits run out.
#
#   HIVE_CMD_COMMANDCODE="bash ops/commandcode.sh"      (in ~/.hive/agents.env; mac-bootstrap.sh writes it)
#
# run-hourly.sh starts agents in the content folder and appends the prompt as the last argument.
# Exit codes the runner understands:
#   0   the agent ran (the content gate decides whether its work is good)
#   75  no capacity: daily cap reached, credits used up or rate limited. The task goes back to the queue and the
#       loop backs off (HIVE_LOOP_IDLE) instead of burning a worker every few seconds.
#   *   anything else (not logged in, crash): the runner retries once on HIVE_FALLBACK (free-agent).
#
# ~/.hive/agents.env settings (defaults in brackets):
#   HIVE_COMMANDCODE_BIN [command-code]       the CLI (npm i -g command-code; `cmd` is the same binary)
#   HIVE_COMMANDCODE_MODEL []                 model id for -m; empty = the account's default (`command-code --list-models`)
#   HIVE_COMMANDCODE_MAX_RUNS_PER_DAY [0]     optional cap on runs per UTC day across all Command Code workers;
#                                             0 = no cap (the hive runs at 1B+ tokens/day; when credits run out
#                                             the lane backs off by itself and the other lanes keep going)
#   HIVE_COMMANDCODE_MAX_TURNS [60]           turn cap per run (Command Code exits 8 when it hits it)
# Compatible with macOS bash 3.2.
set -u

PROMPT="${!#:?usage: commandcode.sh <prompt>}"
BIN="${HIVE_COMMANDCODE_BIN:-command-code}"
HIVE_HOME="${HIVE_HOME:-$HOME/.hive}"
CAP="${HIVE_COMMANDCODE_MAX_RUNS_PER_DAY:-0}"
mkdir -p "$HIVE_HOME"

if ! command -v "$BIN" >/dev/null 2>&1; then
  echo "commandcode: $BIN not found; install it with  npm i -g command-code  then  command-code login" >&2
  exit 127
fi

# Optional spend guard, for when GOAT credits must last the month.
# One line per run in a per-day file; mkdir is the lock so parallel workers never over-count.
if [ "$CAP" != 0 ]; then
  COUNT_FILE="$HIVE_HOME/commandcode.runs.$(date -u +%Y-%m-%d)"
  LOCK="$HIVE_HOME/commandcode.count.lock"
  i=0; until mkdir "$LOCK" 2>/dev/null; do i=$((i + 1)); [ "$i" -ge 50 ] && rmdir "$LOCK" 2>/dev/null; sleep 0.2; done
  used=0; [ -f "$COUNT_FILE" ] && used="$(wc -l < "$COUNT_FILE" | tr -d ' ')"
  if [ "$used" -ge "$CAP" ]; then
    rmdir "$LOCK"
    echo "commandcode: daily cap reached ($used/$CAP runs today, HIVE_COMMANDCODE_MAX_RUNS_PER_DAY)" >&2
    exit 75
  fi
  echo "${HIVE_TASK_ID:-run} $(date -u +%H:%M:%S)" >> "$COUNT_FILE"
  rmdir "$LOCK"
  find "$HIVE_HOME" -maxdepth 1 -name 'commandcode.runs.*' -mtime +7 -delete 2>/dev/null || true
fi

set -- --yolo --trust --skip-onboarding --no-auto-update --max-turns "${HIVE_COMMANDCODE_MAX_TURNS:-60}"
[ -n "${HIVE_COMMANDCODE_MODEL:-}" ] && set -- "$@" -m "$HIVE_COMMANDCODE_MODEL"

OUT="$(mktemp "${TMPDIR:-/tmp}/commandcode.XXXXXX")"
"$BIN" "$@" -p "$PROMPT" > "$OUT" 2>&1
rc=$?
cat "$OUT"
if [ "$rc" != 0 ] && grep -qiE 'insufficient credits|CREDITS_EXHAUSTED|spend cap|rate.?limit|too many requests|HTTP 429' "$OUT"; then
  rm -f "$OUT"
  echo "commandcode: no capacity right now (exit $rc); backing off" >&2
  exit 75
fi
rm -f "$OUT"
if [ "$rc" = 8 ]; then
  echo "commandcode: hit the turn cap (HIVE_COMMANDCODE_MAX_TURNS); keeping the partial work for the gate" >&2
  exit 0
fi
exit "$rc"
