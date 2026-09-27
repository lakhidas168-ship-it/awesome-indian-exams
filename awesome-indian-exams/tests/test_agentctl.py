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


def make_remote(tmp: Path, clones: tuple[str, ...], tasks_toml: str | None = None) -> list[Path]:
    """Bare remote seeded with this content folder (optionally a custom backlog) plus working clones."""
    remote = tmp / "remote.git"
    sh("git", "init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp)
    seed = tmp / "seed"
    sh("git", "init", "-q", "-b", "main", str(seed), cwd=tmp)
    shutil.copytree(CONTENT, seed / CONTENT.name, ignore=shutil.ignore_patterns("__pycache__", "tests_main"))
    if tasks_toml is not None:
        (seed / CONTENT.name / "ops" / "tasks.toml").write_text(tasks_toml, encoding="utf-8")
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

    def test_focus_rotation_picks_india_one_hour_in_five(self) -> None:
        a = self.repos[0]
        core = json.loads(ctl(a, "next", "hermes", env={**ENV, "HIVE_SLOT": "0"}).stdout)
        india = json.loads(ctl(a, "next", "hermes", env={**ENV, "HIVE_SLOT": "4"}).stdout)
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


if __name__ == "__main__":
    unittest.main()
