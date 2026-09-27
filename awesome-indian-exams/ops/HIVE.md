# The hive: how JEVX, Hermes and OpenCode run this repo without the owner

Three agent roles work **in parallel**, stay in sync through git alone, and publish every hour. The owner only
logs in and pays for anything that isn't free. By default nothing needs paying for: see
[`docs/FREE-COMPUTE.md`](../docs/FREE-COMPUTE.md).

| Role | Lane | Does |
|---|---|---|
| **Hermes** | research + content | writes and verifies exam pages, modules, registry entries from official documents |
| **OpenCode** | tooling | extends the content gate, formats, tests |
| **JEVX** | planner + judge | reviews every change, publishes what passes, keeps the backlog fed |
| owner | human | `H-` tasks only: login, payment, repository settings |

## Two ways to run, same rules

**Cloud (free, 24/7):** `.github/workflows/hive-cloud.yml` (repository root) runs
every hour on GitHub Actions. The Hermes and OpenCode lanes run in parallel on the built-in zero-cost agent
([`free_agent.py`](free_agent.py)) using GitHub Models through the workflow's own token (no key, no card). Then
the JEVX judge ([`judge.py`](judge.py)) runs every code gate and an LLM review, and publishes approved work
straight to `main`. Kill switch: set the repository variable `HIVE_ENABLED` to `false`.

**Mac (the owner's own agents, extra capacity):** one command, [`mac-bootstrap.sh`](mac-bootstrap.sh), detects
the agents and installs the schedule; [`run-hourly.sh`](run-hourly.sh) runs the real JEVX, Hermes, OpenCode,
Gemini CLI and Antigravity from cron. Each works in its own git worktree, opens a PR, and
JEVX approves with a label; [`merge_ready.sh`](merge_ready.sh) merges approved, green PRs. Any lane can also
run on the free agent: `HIVE_CMD_HERMES=free-agent`, with Ollama for fully local and free models.

Both modes claim from the same backlog on the remote, so cloud and Mac agents never take the same task.

```
 every hour ┌────────────── Hermes (content) ───┐   ┌── OpenCode (tooling) ──┐
            │ claim → agent edits → content gate │   │ same steps, own lane   │   (parallel, own worktrees)
            │ → receipt (code) → lane + evidence │   │                        │
            │ gates → push agent/<lane>/<task>   │   │                        │
            └──────────────────┬─────────────────┘   └───────────┬────────────┘
                               ▼                                 ▼
            JEVX judge: main's own gates + main's self-tests on the branch + evidence + LLM verdict
                               ▼
               approved → squash onto main → index, overlap map and UPDATES.md regenerated
```

## Focus: starts at 20%, grows as it matures

[`hive.toml`](hive.toml) `[focus.ramp]`: the "india" focus (every exam family except the engineering track)
starts at **20%** of runs and gains **1 point for every 5 india tasks published**, as long as at least 80% of
judged india work was approved. If quality drops, it falls back to 20% until it recovers. It is capped at 60%, so
the engineering track always keeps at least 40%. The share is computed from receipts and judge logs on `main`, so
the cloud and the Mac always agree. Hours are assigned with a golden-ratio sequence, so any stretch of hours
matches the share. If the preferred focus has no ready task, the lane takes one from the other focus rather than
idling. `agentctl.py status` prints the current share.

## Workers: many agents per lane

`run-hourly.sh <lane> [worker]`: several agents can serve one lane in parallel, each with its own worktree, lock
and log. On the Mac the Hermes lane has three workers (Hermes `hermes -z`, Gemini CLI `gemini --yolo -p`,
Antigravity `agy -p` behind a pseudo-terminal), and the OpenCode lane runs `opencode run` on the OpenCode Go plan
(DeepSeek V4.1 Flash). A worker that fails without changing anything retries once on the free agent
(`HIVE_FALLBACK`), so one logged-out tool never stalls a lane. Tasks marked `where = "mac"` (they need local files)
run only on the Mac.

## Sandbox (cloud)

In the cloud, agents that have a shell (the real OpenCode CLI) work on a copy of the content folder with no
`.git` and no GitHub token. The runner copies their file changes back, and every gate still applies, so an agent
can never push or publish by itself.

## Harvest: the owner's earlier work

[`harvest.py`](harvest.py) scans the Mac (Documents, Desktop, Downloads, code folders), every Google Drive for
desktop account, iCloud and `~/Hive-Inbox` (Google Takeout exports). It builds a **private** inventory in
`~/.hive/harvest/`, drops duplicates, and flags transcripts, coaching material and personal data. Only the
owner's own, non-personal work becomes tasks (`T-5xx`, `where = "mac"`), which name nothing but an opaque
`inv:` id. Hermes-lane workers read items through the MCP tools `harvest_search` / `harvest_item`, keep the
structure and advice, and re-verify every fact officially (skill `harvest-import`).

## Self-healing

[`doctor.py`](doctor.py) checks the content gate, the backlog per lane and focus, quality, stale claims and, on
the Mac, every tool, login, the schedule, each worker's last run and errors, and the harvest. JEVX reads it every
hour: a tooling problem becomes an OpenCode task; a login, payment or settings click becomes an `H-` task that
links the exact page in [`docs/OWNER-CLICKS.md`](../docs/OWNER-CLICKS.md).

## Sync protocol (all state is on the remote)

| State | Where | Written by |
|---|---|---|
| backlog | `ops/tasks.toml` on `main` | JEVX only |
| claimed | `refs/heads/claim/<id>` or branch `agent/<lane>/<id>` | `agentctl.py next --claim` (atomic create-only push) |
| done | `ops/done/<id>.md` on `main` | the runner writes it; it counts once published |
| plan / judge log | `ops/plan/<date>.md` | JEVX |

- Two agents can never hold the same task: a claim is a push that only succeeds if the ref doesn't exist yet
  (stress-tested with 12 parallel agents and 80 tasks, each taken exactly once).
- A claim with no work branch for 6 hours is freed, so a crashed agent never blocks a task. A run that finds no
  free LLM capacity frees its task immediately.
- Workers never touch generated files, so parallel changes don't conflict.

## Trust model: what stops a bad change

1. **Receipts are written by code.** The runner records the diff, the real content-gate output and every URL the
   agent fetched (status, size, SHA-256). Agent notes are quoted separately, labelled as claims, and can't pose
   as code sections.
2. **Evidence gate.** A page becomes `official` only with a recorded HTTP 200 fetch, from an allowlisted
   official domain, of a URL listed on the page, within a day of `last_verified`.
3. **Lane scope.** Each lane may only change its own files ([`scripts/hive_gate.py`](../scripts/hive_gate.py)).
4. **Guardrails are protected.** No agent may change the gates, judge, runner, claim tool, free agent,
   prompts, skills, domain allowlist, `hive.toml` or `.github/`. Only the owner can.
5. **The judge uses main's gates, not the branch's**, and runs main's self-tests against the branch's code. A
   change that loosens an existing check fails a test main already has.
6. **LLM review** on top, for what code can't judge: usefulness, honesty, copied text.
7. **Content gate** everywhere: official sources only, no file-dump links, no broken links, required sections.

## Agent tooling

- **MCP server** ([`mcp_server.py`](mcp_server.py), stdio): `hive_status`, `next_task`, `validate_content`,
  `check_lane_scope`, `list_exams`, `exam_info`, `fetch_url` (records evidence to `$HIVE_FETCH_LOG`),
  `read_skill`. OpenCode picks it up from [`opencode.json`](../opencode.json). For Hermes, JEVX or any other
  MCP client, register the stdio command `python3 <repo>/awesome-indian-exams/ops/mcp_server.py`.
- **Skills** ([`.agents/skills/`](../.agents/skills/)): `exam-page`, `module-page`, `hive-tooling`,
  `review-agent-work`, `hive-sync`, in the standard `SKILL.md` format. OpenCode loads `.agents/skills`
  natively, and the runner also puts the lane's skill into every prompt.

## Tested

`python3 -m unittest discover -s tests` includes:
- an offline **dry run** of the whole cloud loop (claim → free agent edits → gates → receipt → branch → judge →
  published on `main`), with a scripted local LLM;
- a **negative dry run**: an agent marking a page official without evidence is stopped before publishing;
- a **stress test** of parallel claims (`HIVE_STRESS_WORKERS=12 HIVE_STRESS_TASKS=80` for a heavier run);
- an MCP protocol test, provider fallback on HTTP 429, and scope refusal for every guardrail.

## Commands

```bash
python3 ops/agentctl.py status               # backlog, claims, this hour's focus per lane
python3 ops/agentctl.py next hermes          # what Hermes would pick next (no claim)
python3 scripts/validate.py --write          # regenerate index, all-exams, overlap map, UPDATES.md
python3 -m unittest discover -s tests        # all self-tests, dry run and stress test
ops/run-hourly.sh hermes                     # one hive run by hand (Mac)
python3 ops/judge.py --no-llm                # dry-judge pending cloud branches without publishing
```
