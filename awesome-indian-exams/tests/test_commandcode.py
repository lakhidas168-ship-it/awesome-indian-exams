"""Tests for the Command Code worker (ops/commandcode.sh) and numbered loop workers, using a fake `command-code`."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from test_agentctl import CONTENT, ENV, make_remote
from test_free_agent import KEY_ENVS

WRAPPER = CONTENT / "ops" / "commandcode.sh"

# Fake CLI: logs its arguments, then behaves as FAKE_CC_MODE says. "edit" changes a page like a real run would.
FAKE = """#!/bin/bash
printf '%s\\n' "$@" > "$FAKE_CC_LOG.$$"
cat "$FAKE_CC_LOG.$$" >> "$FAKE_CC_LOG"; echo --- >> "$FAKE_CC_LOG"; rm -f "$FAKE_CC_LOG.$$"
case "${FAKE_CC_MODE:-ok}" in
  ok) echo "done" ;;
  edit) printf '\\n- Checked by Command Code.\\n' >> exams/engineering/gate-ee.md; echo "edited" ;;
  credits) echo "Error: Insufficient credits. Top up or upgrade your plan." >&2; exit 1 ;;
  ratelimit) echo "Error: 429 Too Many Requests" >&2; exit 1 ;;
  auth) echo 'Error: Not authenticated. Please run "cmd login" first.' >&2; exit 3 ;;
  turncap) echo "turn cap reached"; exit 8 ;;
esac
"""


class Wrapper(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "bin").mkdir()
        fake = self.tmp / "bin" / "command-code"
        fake.write_text(FAKE, encoding="utf-8")
        fake.chmod(0o755)
        self.log = self.tmp / "calls.log"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def run_cc(self, mode: str = "ok", prompt: str = "do task T-001", **env: str) -> subprocess.CompletedProcess:
        full = {**os.environ, "PATH": f"{self.tmp / 'bin'}:{os.environ['PATH']}", "HIVE_HOME": str(self.tmp / "hive"),
                "FAKE_CC_LOG": str(self.log), "FAKE_CC_MODE": mode, **env}
        return subprocess.run(["bash", str(WRAPPER), prompt], env=full, text=True, capture_output=True, timeout=60)

    def calls(self) -> list[list[str]]:
        text = self.log.read_text(encoding="utf-8") if self.log.exists() else ""
        return [c.strip("\n").split("\n") for c in text.split("---\n") if c.strip()]

    def test_headless_flags_and_prompt(self) -> None:
        res = self.run_cc(prompt="multi word\nprompt", HIVE_COMMANDCODE_MODEL="some-model")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("done", res.stdout)
        args = self.calls()[0]
        for flag in ("--yolo", "--trust", "--skip-onboarding", "--no-auto-update", "--max-turns"):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index("-m") + 1], "some-model")
        self.assertEqual(args[args.index("-p") + 1:], ["multi word", "prompt"])  # the prompt is the -p value

    def test_no_model_flag_by_default(self) -> None:
        self.assertEqual(self.run_cc().returncode, 0)
        self.assertNotIn("-m", self.calls()[0])

    def test_credits_and_rate_limits_mean_no_capacity(self) -> None:
        self.assertEqual(self.run_cc("credits").returncode, 75)
        self.assertEqual(self.run_cc("ratelimit").returncode, 75)

    def test_logged_out_is_a_failure_so_the_runner_falls_back(self) -> None:
        res = self.run_cc("auth")
        self.assertEqual(res.returncode, 3)
        self.assertIn("Not authenticated", res.stdout)

    def test_turn_cap_keeps_partial_work(self) -> None:
        self.assertEqual(self.run_cc("turncap").returncode, 0)

    def test_no_daily_cap_by_default(self) -> None:
        for _ in range(5):
            self.assertEqual(self.run_cc().returncode, 0)
        self.assertEqual(len(self.calls()), 5)

    def test_optional_daily_cap(self) -> None:
        codes = [self.run_cc(HIVE_COMMANDCODE_MAX_RUNS_PER_DAY="2").returncode for _ in range(3)]
        self.assertEqual(codes, [0, 0, 75])
        self.assertEqual(len(self.calls()), 2)  # the capped run never reached the CLI

    def test_missing_cli(self) -> None:
        res = self.run_cc(HIVE_COMMANDCODE_BIN="command-code-not-installed")
        self.assertEqual(res.returncode, 127)
        self.assertIn("npm i -g command-code", res.stderr)


@unittest.skipIf(os.environ.get("HIVE_IN_JUDGE"), "end-to-end runner tests are not repeated inside the judge")
class NumberedWorker(unittest.TestCase):
    def test_commandcode_loop_worker_uses_the_commandcode_command(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            repo = make_remote(tmp, ("repo",))[0]
            (tmp / "bin").mkdir()
            fake = tmp / "bin" / "command-code"
            fake.write_text(FAKE, encoding="utf-8")
            fake.chmod(0o755)
            env = {**{k: v for k, v in ENV.items() if k not in KEY_ENVS},
                   "PATH": f"{tmp / 'bin'}:{os.environ['PATH']}", "HIVE_HOME": str(tmp / "hive"),
                   "HIVE_OPEN_PR": "0", "HIVE_SLOT": "1", "HIVE_CMD_HERMES": "false",
                   "HIVE_CMD_COMMANDCODE": "bash ops/commandcode.sh", "FAKE_CC_MODE": "edit",
                   "FAKE_CC_LOG": str(tmp / "calls.log")}
            res = subprocess.run(["bash", f"{CONTENT.name}/ops/run-hourly.sh", "hermes", "commandcode-2"], cwd=repo,
                                 env=env, text=True, capture_output=True, timeout=300)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("pushed agent/hermes/", res.stdout)
            self.assertTrue((tmp / "calls.log").exists(), "the Command Code CLI was never called")
            self.assertTrue((tmp / "hive" / "worktrees" / "commandcode-2").is_dir())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_loop_starts_commandcode_workers_that_take_distinct_tasks(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            backlog = "".join(f'[[task]]\nid = "T-{i:03d}"\nlane = "hermes"\npriority = 1\ntitle = "task {i}"\n'
                              f'accept = ["a"]\n' for i in range(1, 4))
            repo = make_remote(tmp, ("repo",), tasks_toml=backlog)[0]
            (tmp / "bin").mkdir()
            fake = tmp / "bin" / "command-code"
            fake.write_text('#!/bin/bash\nmkdir -p docs; echo "$$" > "docs/cc-$HIVE_TASK_ID.md"\n', encoding="utf-8")
            fake.chmod(0o755)
            env = {**{k: v for k, v in ENV.items() if k not in KEY_ENVS},
                   "PATH": f"{tmp / 'bin'}:{os.environ['PATH']}", "HIVE_HOME": str(tmp / "hive"),
                   "HIVE_OPEN_PR": "0", "HIVE_CMD_COMMANDCODE": "bash ops/commandcode.sh",
                   "HIVE_LOOP_COMMANDCODE": "2", "HIVE_LOOP_HERMES": "0", "HIVE_LOOP_OPENCODE": "0",
                   "HIVE_CMD_JEVX": "true", "HIVE_LOOP_IDLE": "1", "HIVE_LOOP_JEVX_EVERY": "999"}
            loop = [f"{CONTENT.name}/ops/hive-loop.sh"]
            subprocess.run(["bash", *loop, "start"], cwd=repo, env=env, check=True, capture_output=True, timeout=60)
            deadline = time.time() + 120
            branches: list[str] = []
            while time.time() < deadline and len(branches) < 3:
                time.sleep(2)
                branches = subprocess.run(["git", "ls-remote", "origin", "refs/heads/agent/hermes/*"], cwd=repo,
                                          capture_output=True, text=True).stdout.split()[1::2]
            subprocess.run(["bash", *loop, "stop"], cwd=repo, env=env, capture_output=True, timeout=60)
            time.sleep(2)
            tasks = sorted(b.rsplit("/", 1)[1] for b in branches)
            self.assertEqual(tasks, ["T-001", "T-002", "T-003"])
            workers = sorted(p.name for p in (tmp / "hive" / "worktrees").iterdir())
            self.assertEqual(workers, ["commandcode-1", "commandcode-2", "jevx"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
