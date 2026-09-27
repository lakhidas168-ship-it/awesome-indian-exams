# The hive: how JEVX, Hermes and OpenCode run this repo without the owner

Three agents work **in parallel** on the owner's Mac, each in its own git worktree, and stay in sync through git
alone: no shared memory, no chat between agents, no central server. The owner only logs in once and pays for
the agents; everything else is automatic.

```
               ┌───────────── every hour (cron) ─────────────┐
               ▼                        ▼                     ▼
      Hermes (research)         OpenCode (tooling)       JEVX (planner + judge)
   claims 1 content task     claims 1 tooling task    reviews PRs, labels hive:approved,
   edits exams/, resources/   edits scripts/, tests/   writes ops/tasks.toml + ops/plan/
               │                        │                     │
               └── runner: content gate → receipt → PR ──┐    └── runner: merge_ready.sh
                                                          ▼             (approved + CI green → merge)
                                      GitHub Actions: content gate + lane scope gate
                                                          ▼
                                     main → public list; UPDATES.md shows every change
```

## Lanes

| Lane | Agent | Owns | May change |
|---|---|---|---|
| research + content | **Hermes** | verifying exam facts against official documents, writing pages, PYQ analysis | `exams/`, `resources/`, new content folders, its own receipt |
| tooling | **OpenCode** | validator rules, tests, formats, site build, CI | everything in the content folder except `ops/tasks.toml` and `UPDATES.md`, plus `.github/workflows/awesome-exams*.yml` |
| planner + judge | **JEVX** | backlog, PR review and approval, plan, README index, `UPDATES.md` | `ops/tasks.toml`, `ops/plan/`, `README.md`, `UPDATES.md` |
| owner | **human** | login, payment, repository settings | `H-` tasks in the backlog only |

`scripts/hive_gate.py` enforces these scopes in CI, so a lane that strays turns its own PR red.

## Sync protocol (all state is on the remote)

| State | Where | Written by |
|---|---|---|
| backlog | `ops/tasks.toml` on `main` | JEVX only |
| claimed | `refs/heads/claim/<id>` or branch `agent/<lane>/<id>` | `agentctl.py next --claim` (atomic create-only push) |
| done | `ops/done/<id>.md` on `main` | runner writes it, it counts once the PR merges |
| plan | `ops/plan/<date>.md` | JEVX |

- Two agents can never hold the same task: a claim is a push that only succeeds if the ref does not exist yet.
- A claim with no work branch for 6 hours is freed (`agentctl.py reap`), so a crashed agent never blocks a task.
- A rejected PR is closed with `--delete-branch`; its task becomes available again.
- Workers never touch shared generated files (README index, `UPDATES.md`), so parallel PRs don't conflict.

## Evidence rules

1. **Receipts are written by code.** The runner, not the agent, records the diff and the real content gate
   output. Agent notes are kept in a separate section labelled as claims.
2. **Official sources only for exam facts.** `ops/official-domains.txt` is the allowlist; the gate rejects
   anything else under `## Official sources`.
3. **Honest status.** Every exam page says `official`, `secondary` or `unverified`, and the README shows it.
4. **No piracy.** No coaching material, book scans, or lecture transcripts; no file-dump links.
5. **Never weaken the gate.** JEVX rejects any PR that removes a check or relaxes a test.

## Commands

```bash
python3 ops/agentctl.py status               # who holds what
python3 ops/agentctl.py next hermes          # what Hermes would pick next (no claim)
python3 scripts/validate.py                  # content gate
python3 -m unittest discover -s tests        # gate self-tests
ops/run-hourly.sh hermes                     # one hive run by hand
```

Setup on the Mac: see [`crontab.example`](crontab.example).
