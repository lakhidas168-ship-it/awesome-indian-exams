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

**Mac (the owner's own agents, extra capacity):** [`run-hourly.sh`](run-hourly.sh) runs the real JEVX, Hermes and
OpenCode from cron ([`crontab.example`](crontab.example)). Each works in its own git worktree, opens a PR, and
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

## 80 / 20 focus

[`hive.toml`](hive.toml) sets `core = 4, india = 1`. Each lane spends 4 runs in 5 on the engineering track
(`focus = "core"` tasks) and 1 in 5 on every other exam family (`focus = "india"`). Lanes are offset so they
switch in different hours. If the preferred focus has no ready task, the lane takes one from the other focus
rather than idling. `agentctl.py status` prints this hour's focus per lane.

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
