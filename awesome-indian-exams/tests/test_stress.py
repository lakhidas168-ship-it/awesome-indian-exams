"""Stress test: many agents claiming from one backlog at once. Every task must be taken exactly once.

Skipped inside the cloud judge (HIVE_IN_JUDGE=1) to keep judging fast; CI and local runs execute it.
Scale it up with HIVE_STRESS_WORKERS / HIVE_STRESS_TASKS.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_agentctl import CONTENT, ENV, make_remote

WORKERS = int(os.environ.get("HIVE_STRESS_WORKERS", "6"))
TASKS = int(os.environ.get("HIVE_STRESS_TASKS", "30"))
WORKER = """
import json, subprocess, sys
got = []
while True:
    res = subprocess.run([sys.executable, sys.argv[1], "next", "hermes", "--claim", "--agent", sys.argv[2]],
                         capture_output=True, text=True)
    if res.returncode == 3:
        break
    if res.returncode != 0:
        print("ERR", res.stderr, file=sys.stderr)
        break
    got.append(json.loads(res.stdout)["id"])
print(json.dumps(got))
"""


@unittest.skipIf(os.environ.get("HIVE_IN_JUDGE"), "heavy test skipped inside the judge")
class ClaimStress(unittest.TestCase):
    def test_parallel_workers_take_each_task_exactly_once(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            backlog = "".join(f'[[task]]\nid = "T-{i:03d}"\nlane = "hermes"\npriority = {1 + i % 3}\n'
                              f'title = "task {i}"\naccept = ["a"]\n' for i in range(1, TASKS + 1))
            clones = make_remote(tmp, tuple(f"w{i}" for i in range(WORKERS)), tasks_toml=backlog)
            procs = [subprocess.Popen(["python3", "-c", WORKER, str(c / CONTENT.name / "ops" / "agentctl.py"), c.name],
                                      cwd=c, env=ENV, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for c in clones]
            import json
            results = [json.loads(p.communicate(timeout=300)[0] or "[]") for p in procs]
            claimed = [t for r in results for t in r]
            self.assertEqual(len(claimed), TASKS, f"claimed {len(claimed)} of {TASKS}")
            self.assertEqual(len(set(claimed)), TASKS, "a task was claimed twice")
            self.assertGreater(sum(1 for r in results if r), 1, "work was not spread across workers")
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
