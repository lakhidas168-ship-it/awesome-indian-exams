"""Focused bounds for the local judge's nested test execution."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from test_agentctl import CONTENT

sys.path.insert(0, str(CONTENT / "ops"))
import judge  # noqa: E402


class JudgeSafety(unittest.TestCase):
    def test_nested_judge_refuses_before_accessing_a_git_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(CONTENT / "ops" / "judge.py"), "--publish", "--no-llm"],
                cwd=tmp, env={**os.environ, "HIVE_IN_JUDGE": "1"},
                text=True, capture_output=True, timeout=5,
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("refusing nested judge invocation", result.stdout)

    def test_nested_cloud_batch_refuses_when_in_judge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["bash", str(CONTENT / "ops" / "cloud_batch.sh")],
                cwd=tmp, env={**os.environ, "HIVE_IN_JUDGE": "1"},
                text=True, capture_output=True, timeout=5,
            )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("refusing nested cloud_batch invocation", result.stdout)

    def test_gate_command_has_a_deadline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(subprocess.TimeoutExpired):
                judge.run_gate_command(
                    [sys.executable, "-c", "import time; time.sleep(30)"],
                    Path(tmp), None, os.environ.copy(), timeout=0.1,
                )

    def test_gate_timeout_kills_descendant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ready, marker = Path(tmp) / "ready", Path(tmp) / "descendant-survived"
            child = f"import pathlib,time; time.sleep(2); pathlib.Path({str(marker)!r}).touch()"
            parent = ("import pathlib,subprocess,sys,time; "
                      f"subprocess.Popen([sys.executable, '-c', {child!r}]); "
                      f"pathlib.Path({str(ready)!r}).touch(); time.sleep(5)")
            with self.assertRaises(subprocess.TimeoutExpired):
                judge.run_gate_command([sys.executable, "-c", parent], Path(tmp), None,
                                       os.environ.copy(), timeout=1)
            self.assertTrue(ready.exists(), "the descendant was not started before timeout")
            time.sleep(2.2)
            self.assertFalse(marker.exists(), "the gate left a descendant running")

    def test_both_tests_main_and_tests_discover_without_import_collision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for suite in ("tests_main", "tests"):
                sd = p / suite
                sd.mkdir()
                (sd / "test_agentctl.py").write_text("SUITE = " + repr(suite) + "\n", encoding="utf-8")
                (sd / "test_sample.py").write_text(
                    "import unittest, test_agentctl\n"
                    "class T(unittest.TestCase):\n"
                    "    def test_ok(self):\n"
                    f"        self.assertEqual(test_agentctl.SUITE, {suite!r})\n",
                    encoding="utf-8",
                )
            base_env = {k: v for k, v in os.environ.items() if k != "BASH_ENV"}
            env = {**base_env, "HIVE_IN_JUDGE": "1", "HIVE_JUDGE_FULL_TESTS": "0", "PYTHONPATH": "."}
            for suite in ("tests_main", "tests"):
                res = judge.run_gate_command(
                    [sys.executable, "-m", "unittest", "discover", "-s", suite],
                    p, None, env, timeout=10,
                )
                self.assertEqual(res.returncode, 0, f"{suite} failed: {res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main()

