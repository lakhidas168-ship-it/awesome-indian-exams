"""Dry run of the whole cloud hive, offline: runner (Hermes on the free agent) → branch → judge → main.

A scripted local LLM plays both the worker and the JEVX judge. Skipped inside the judge itself (HIVE_IN_JUDGE).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from mock_llm import MockLLM, tool_call, tools_used
from test_agentctl import CONTENT, ENV, make_remote, sh
from test_free_agent import KEY_ENVS

PAGE = "exams/engineering/gate-ee.md"


def worker_script(edits: list[tuple[str, str]], page: str = PAGE):
    steps = [("read_file", {"path": page, "limit": 300})]
    steps += [("replace_in_file", {"path": page, "old": old, "new": new}) for old, new in edits]
    steps += [("run_gate", {}), ("finish", {"notes": "## Changed\n- dry run"})]

    def script(body: dict) -> dict:
        if "You are JEVX" in body["messages"][0]["content"]:
            return {"role": "assistant", "content": '{"approve": true, "reason": "dry run looks right"}'}
        n = tools_used(body)
        return tool_call(*steps[min(n, len(steps) - 1)], n)
    return script


@unittest.skipIf(os.environ.get("HIVE_IN_JUDGE"), "the dry run is not repeated inside the judge")
class CloudDryRun(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = make_remote(self.tmp, ("repo",))[0]
        self.mock: MockLLM | None = None

    def tearDown(self) -> None:
        if self.mock:
            self.mock.close()
        shutil.rmtree(self.tmp)

    def env(self) -> dict:
        base = {k: v for k, v in ENV.items() if k not in KEY_ENVS}
        return {**base, "HIVE_LLM_BASE_URL": self.mock.url, "HIVE_CMD_HERMES": "free-agent", "HIVE_OPEN_PR": "0",
                "HIVE_HOME": str(self.tmp / "hive"), "HIVE_SLOT": "1", "OLLAMA_BASE_URL": "http://127.0.0.1:9/v1"}

    def sh(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(args, cwd=self.repo, env=self.env(), text=True, capture_output=True, timeout=600)

    def pin(self, page: str, field: str, value: str) -> None:
        """Pin one front-matter field on the remote, so the test keeps passing as the hive verifies the live page."""
        path = self.repo / CONTENT.name / page
        text = path.read_text(encoding="utf-8")
        pinned = re.sub(rf"^{field}: .*$", f"{field}: {value}", text, count=1, flags=re.M)
        if pinned != text:
            path.write_text(pinned, encoding="utf-8")
            sh("git", "commit", "-qam", f"fixture: {field} {value}", cwd=self.repo)
            sh("git", "push", "-q", "origin", "main", cwd=self.repo)

    def remote_file(self, path: str) -> str:
        self.sh("git", "fetch", "-q", "origin", "main")
        return self.sh("git", "show", f"origin/main:{CONTENT.name}/{path}").stdout

    def test_task_flows_from_claim_to_published_main(self) -> None:
        self.mock = MockLLM(worker_script([("## Free resources\n", "## Free resources\n\n- Dry-run marker.\n")]))
        run = self.sh("bash", f"{CONTENT.name}/ops/run-hourly.sh", "hermes")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("agent/hermes/T-001", self.sh("git", "ls-remote", "origin").stdout)

        judge = self.sh("python3", f"{CONTENT.name}/ops/judge.py", "--publish")
        self.assertEqual(judge.returncode, 0, judge.stdout + judge.stderr)
        self.assertIn("published", judge.stdout, judge.stdout)
        self.assertIn("Dry-run marker.", self.remote_file(PAGE))
        receipt = self.remote_file("ops/done/T-001.md")
        self.assertIn("## Content gate output (code)", receipt)
        self.assertIn("PASS", receipt)
        self.assertIn("T-001", self.remote_file("UPDATES.md"))
        refs = self.sh("git", "ls-remote", "origin").stdout
        self.assertNotIn("agent/hermes/T-001", refs)
        self.assertNotIn("claim/T-001", refs)

    def test_official_claim_without_fetched_evidence_is_stopped(self) -> None:
        # An exam page that is still unverified may not become "official" without a code-recorded official fetch.
        self.pin(PAGE, "verification", "unverified")
        self.mock = MockLLM(worker_script([("verification: unverified", "verification: official")]))
        run = self.sh("bash", f"{CONTENT.name}/ops/run-hourly.sh", "hermes")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("evidence", run.stdout + run.stderr)
        refs = self.sh("git", "ls-remote", "origin").stdout
        self.assertNotIn("agent/hermes/T-001", refs)  # nothing published
        self.assertNotIn("claim/T-001", refs)  # and the task went back to the queue


if __name__ == "__main__":
    unittest.main()
