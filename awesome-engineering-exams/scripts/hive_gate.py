#!/usr/bin/env python3
"""Lane scope gate for agent PRs: each lane may only touch its own files.

    git diff --name-only origin/main...HEAD | python3 scripts/hive_gate.py --branch agent/hermes/T-001

Exit 0 when every changed path is inside the lane's scope, 1 otherwise. Non-agent branches pass.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PREFIX = Path(__file__).resolve().parents[1].name  # awesome-engineering-exams
WORKFLOW = re.compile(r"^\.github/workflows/awesome-exams[\w.-]*\.ya?ml$")


def allowed(lane: str, task: str, path: str, prefix: str = PREFIX) -> bool:
    if lane == "jevx":
        return path in (f"{prefix}/README.md", f"{prefix}/UPDATES.md", f"{prefix}/ops/tasks.toml") or (
            path.startswith(f"{prefix}/ops/plan/"))
    if not path.startswith(f"{prefix}/"):
        return lane == "opencode" and bool(WORKFLOW.match(path))
    inner = path[len(prefix) + 1:]
    if inner.startswith("ops/done/"):
        return inner == f"ops/done/{task}.md"
    if inner in ("ops/tasks.toml", "UPDATES.md"):
        return False
    if lane == "hermes":
        return not inner.startswith(("scripts/", "tests/", "ops/"))
    if lane == "opencode":
        return True
    return False


def check(branch: str, paths: list[str], prefix: str = PREFIX) -> list[str]:
    parts = branch.split("/")
    if len(parts) < 3 or parts[0] != "agent":
        return []
    lane, task = parts[1], parts[2]
    problems = [f"{lane} may not change {p}" for p in paths if not allowed(lane, task, p, prefix)]
    if lane in ("hermes", "opencode") and f"{prefix}/ops/done/{task}.md" not in paths:
        problems.append(f"missing receipt {prefix}/ops/done/{task}.md")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--branch", required=True)
    args = ap.parse_args(argv)
    paths = [line.strip() for line in sys.stdin if line.strip()]
    problems = check(args.branch, paths)
    for p in problems:
        print(f"ERROR {p}")
    print(f"{'FAIL' if problems else 'PASS'}: {args.branch}, {len(paths)} changed paths")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
