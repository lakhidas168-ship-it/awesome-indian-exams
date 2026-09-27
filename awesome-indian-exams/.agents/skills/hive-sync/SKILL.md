---
name: hive-sync
description: How JEVX, Hermes and OpenCode stay in sync in the awesome-indian-exams hive (lanes, task claims, receipts, MCP tools). Use when starting any hive work.
---

# Hive sync

- **One task per run.** The runner claims it for you and gives it in the prompt. Don't pick another.
- **Don't run git.** The runner commits, writes the receipt, pushes, and opens the PR or hands the branch to the
  cloud judge.
- **Lanes:** Hermes writes content (`exams/`, `modules/`, `resources/`, `registry/`, `docs/`). OpenCode builds
  tooling (`scripts/`, `tests/`, formats). JEVX plans (`ops/tasks.toml`, `ops/plan/`) and judges.
- **80/20 focus:** about 80% of runs go to the engineering track and 20% to all other exams (`ops/hive.toml`).
  The runner picks the task, so you just do the one you're given.
- **MCP tools** (server `ops/mcp_server.py`): `hive_status`, `next_task`, `validate_content`,
  `check_lane_scope`, `list_exams`, `exam_info`, `fetch_url` (records evidence), `read_skill`.
- **Evidence:** fetch official documents with the `fetch_url` tool, never another way, so the fetch is recorded.
  An `official` status without a recorded fetch is rejected by code.
- **Finish with notes:** sources opened and what each confirmed, what you couldn't confirm, what you changed.
