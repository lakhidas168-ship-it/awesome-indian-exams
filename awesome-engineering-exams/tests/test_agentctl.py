"""Integration test for ops/agentctl.py against a throwaway local git remote."""
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


class AgentCtl(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        remote = self.tmp / "remote.git"
        sh("git", "init", "-q", "--bare", "-b", "main", str(remote), cwd=self.tmp)
        self.repos = []
        seed = self.tmp / "seed"
        sh("git", "init", "-q", "-b", "main", str(seed), cwd=self.tmp)
        shutil.copytree(CONTENT, seed / CONTENT.name, ignore=shutil.ignore_patterns("__pycache__"))
        sh("git", "add", "-A", cwd=seed)
        sh("git", "commit", "-qm", "seed", cwd=seed)
        sh("git", "remote", "add", "origin", str(remote), cwd=seed)
        sh("git", "push", "-q", "origin", "main", cwd=seed)
        for name in ("a", "b"):
            sh("git", "clone", "-q", "-b", "main", str(remote), name, cwd=self.tmp)
            self.repos.append(self.tmp / name)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def ctl(self, repo: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["python3", str(repo / CONTENT.name / "ops" / "agentctl.py"), *args],
                              cwd=repo, env=ENV, text=True, capture_output=True)

    def test_two_agents_never_share_a_task(self) -> None:
        a, b = self.repos
        procs = [subprocess.Popen(["python3", str(r / CONTENT.name / "ops" / "agentctl.py"), "next", "hermes",
                                   "--claim", "--agent", r.name], cwd=r, env=ENV, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for r in (a, b)]
        ids = [json.loads(p.communicate()[0])["id"] for p in procs]
        self.assertEqual(len(set(ids)), 2, ids)
        self.assertNotEqual(self.ctl(a, "claim", ids[1], "--agent", "a").returncode, 0)

    def test_human_tasks_are_never_handed_to_workers(self) -> None:
        a = self.repos[0]
        seen = set()
        while (res := self.ctl(a, "next", "hermes", "--claim", "--agent", "a")).returncode == 0:
            seen.add(json.loads(res.stdout)["id"])
        self.assertEqual(res.returncode, 3)
        self.assertTrue(seen)
        self.assertFalse(any(t.startswith("H-") for t in seen))

    def test_merged_receipt_marks_done_and_reap_frees_claim(self) -> None:
        a = self.repos[0]
        task = json.loads(self.ctl(a, "next", "hermes", "--claim", "--agent", "a").stdout)["id"]
        (a / CONTENT.name / "ops" / "done").mkdir(parents=True, exist_ok=True)
        (a / CONTENT.name / "ops" / "done" / f"{task}.md").write_text("receipt\n", encoding="utf-8")
        sh("git", "add", "-A", cwd=a)
        sh("git", "commit", "-qm", "merge", cwd=a)
        sh("git", "push", "-q", "origin", "main", cwd=a)
        self.assertRegex(self.ctl(a, "status").stdout, rf"{task}\s+hermes\s+p\d+\s+done")
        self.assertIn(f"reaped {task} (done)", self.ctl(a, "reap").stdout)
        self.assertNotEqual(json.loads(self.ctl(a, "next", "hermes").stdout)["id"], task)


if __name__ == "__main__":
    unittest.main()
