---
name: hive-tooling
description: Rules for changing awesome-indian-exams tooling (scripts/validate.py, new scripts, tests, content formats). Use for any OpenCode-lane task.
---

# Hive tooling

- **Stdlib-only Python 3.11.** No new dependencies. Shell must run on macOS bash 3.2.
- **Every new check gets a test** in `tests/` showing it rejects bad input. Run
  `python3 -m unittest discover -s tests` and `python3 scripts/validate.py` before you finish.
- **Protected files cannot be changed by any agent** (the lane gate rejects them): `scripts/hive_gate.py`,
  `scripts/evidence_gate.py`, `ops/judge.py`, `ops/run-hourly.sh`, `ops/merge_ready.sh`, `ops/agentctl.py`,
  `ops/free_agent.py`, `ops/official-domains.txt`, `ops/hive.toml`, `ops/prompts/`, `.agents/`, and everything in
  `.github/`. If a task needs one of them, write the proposal to `docs/` and say so in your notes.
- **Never weaken a check.** The judge runs main's self-tests against your code, so removing or loosening an
  existing rule fails there.
- Generated files (`README.md` index, `resources/all-exams.md`, `resources/overlap-map.md`, `UPDATES.md`) are
  written only by `validate.py --write` in the JEVX lane. Don't edit them by hand.
- Keep changes to what the task asks.
