"""Integration tests for ops/agentctl.py against a throwaway local git remote."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def sh(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, env=ENV, text=True, capture_output=True, check=True)


# Tests never depend on the live backlog: it shrinks as the hive works, and main's tests run on every branch.
FIXED_BACKLOG = """
[[task]]
id = "H-001"
lane = "human"
priority = 1
title = "owner step"
accept = ["a"]

[[task]]
id = "T-001"
lane = "hermes"
priority = 1
title = "Verify the GATE EE page against the official GATE 2027 information brochure"
accept = ["a"]

[[task]]
id = "T-002"
lane = "hermes"
priority = 2
title = "core task two"
accept = ["a"]

[[task]]
id = "T-201"
lane = "hermes"
focus = "india"
priority = 1
title = "india task one"
accept = ["a"]

[[task]]
id = "T-202"
lane = "hermes"
focus = "india"
priority = 2
title = "india task two"
accept = ["a"]

[[task]]
id = "T-101"
lane = "opencode"
priority = 1
title = "tooling task"
accept = ["a"]
"""


def make_remote(tmp: Path, clones: tuple[str, ...], tasks_toml: str = FIXED_BACKLOG) -> list[Path]:
    """Bare remote seeded with this content folder, a fixed backlog and no receipts, plus working clones."""
    remote = tmp / "remote.git"
    sh("git", "init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp)
    seed = tmp / "seed"
    sh("git", "init", "-q", "-b", "main", str(seed), cwd=tmp)
    shutil.copytree(CONTENT, seed / CONTENT.name, ignore=shutil.ignore_patterns("__pycache__", "tests_main"))
    (seed / CONTENT.name / "ops" / "tasks.toml").write_text(tasks_toml, encoding="utf-8")
    for receipt in (seed / CONTENT.name / "ops" / "done").glob("*.md"):
        receipt.unlink()
    for plan in (seed / CONTENT.name / "ops" / "plan").glob("*.md"):
        plan.unlink()
    # Generated files (UPDATES.md, README index) link the receipts removed above: regenerate them, or the seed's
    # content gate fails as soon as the live repo has published its first task.
    sh("python3", str(seed / CONTENT.name / "scripts" / "validate.py"), "--write", cwd=seed / CONTENT.name)
    sh("git", "add", "-A", cwd=seed)
    sh("git", "commit", "-qm", "seed", cwd=seed)
    sh("git", "remote", "add", "origin", str(remote), cwd=seed)
    sh("git", "push", "-q", "origin", "main", cwd=seed)
    out = []
    for name in clones:
        sh("git", "clone", "-q", "-b", "main", str(remote), name, cwd=tmp)
        out.append(tmp / name)
    return out


def ctl(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["python3", str(repo / CONTENT.name / "ops" / "agentctl.py"), *args],
                          cwd=repo, env=env or ENV, text=True, capture_output=True)


class AgentCtl(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repos = make_remote(self.tmp, ("a", "b"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_two_agents_never_share_a_task(self) -> None:
        a, b = self.repos
        procs = [subprocess.Popen(["python3", str(r / CONTENT.name / "ops" / "agentctl.py"), "next", "hermes",
                                   "--claim", "--agent", r.name], cwd=r, env=ENV, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for r in (a, b)]
        ids = [json.loads(p.communicate()[0])["id"] for p in procs]
        self.assertEqual(len(set(ids)), 2, ids)
        self.assertNotEqual(ctl(a, "claim", ids[1], "--agent", "a").returncode, 0)

    def test_human_tasks_are_never_handed_to_workers(self) -> None:
        a = self.repos[0]
        seen = []
        for _ in range(12):
            res = ctl(a, "next", "hermes", "--claim", "--agent", "a")
            if res.returncode != 0:
                break
            seen.append(json.loads(res.stdout)["id"])
        self.assertTrue(seen)
        self.assertFalse(any(t.startswith("H-") for t in seen), seen)

    def test_focus_rotation_picks_india_about_one_hour_in_five(self) -> None:
        import sys
        sys.path.insert(0, str(CONTENT / "ops"))
        import agentctl
        import tomllib
        config = tomllib.loads((CONTENT / "ops" / "hive.toml").read_text(encoding="utf-8"))
        slots = {f: next(s for s in range(50) if agentctl.preferred_focus("hermes", config, s, 0.2) == f)
                 for f in ("core", "india")}
        a = self.repos[0]
        core = json.loads(ctl(a, "next", "hermes", env={**ENV, "HIVE_SLOT": str(slots["core"])}).stdout)
        india = json.loads(ctl(a, "next", "hermes", env={**ENV, "HIVE_SLOT": str(slots["india"])}).stdout)
        self.assertEqual(core.get("focus", "core"), "core")
        self.assertEqual(india.get("focus"), "india")

    def test_merged_receipt_marks_done_and_reap_frees_claim(self) -> None:
        a = self.repos[0]
        task = json.loads(ctl(a, "next", "hermes", "--claim", "--agent", "a").stdout)["id"]
        (a / CONTENT.name / "ops" / "done").mkdir(parents=True, exist_ok=True)
        (a / CONTENT.name / "ops" / "done" / f"{task}.md").write_text("receipt\n", encoding="utf-8")
        sh("git", "add", "-A", cwd=a)
        sh("git", "commit", "-qm", "merge", cwd=a)
        sh("git", "push", "-q", "origin", "main", cwd=a)
        self.assertRegex(ctl(a, "status").stdout, rf"{task}\s+hermes\s+\w+\s+p\d+\s+done")
        self.assertIn(f"reaped {task} (done)", ctl(a, "reap").stdout)
        self.assertNotEqual(json.loads(ctl(a, "next", "hermes").stdout)["id"], task)

    def test_receipt_criteria_are_not_rendered_as_review_checkboxes(self) -> None:
        repo = self.repos[0]
        validator_log = repo / "validator.log"
        validator_log.write_text("PASS: sample validation\n", encoding="utf-8")
        result = ctl(repo, "receipt", "T-001", "--lane", "hermes", "--agent-cmd", "sample-agent",
                     "--started", "2026-09-28T00:00:00Z", "--validator-log", str(validator_log))
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = (repo / CONTENT.name / "ops" / "done" / "T-001.md").read_text(encoding="utf-8")
        self.assertIn("Acceptance criteria (task requirements)", receipt)
        self.assertIn("not individual review checkboxes", receipt)
        self.assertIn("Historical receipts", receipt)
        self.assertIn("ops/plan/<date>.md", receipt)
        self.assertIn("- a", receipt)
        self.assertNotIn("- [ ]", receipt)


if __name__ == "__main__":
    unittest.main()
