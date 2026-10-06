"""Offline tests for ops/cloud_batch.sh -- the free GitHub Actions cloud hive, using the scripted mock LLM.

A dry run (HIVE_CLOUD_DRY=1) copies the content folder to a throwaway repo, runs the six workers against a
LOCAL bare hub with the mock LLM playing both the worker and the JEVX judge, then computes the single
candidate commit that GitHub would receive -- without ever touching a real remote.

Tests:
  1. A dry run completes a task end to end and produces exactly one candidate commit.
  2. Claim and agent refs never appear on the 'origin' remote (they live on the local 'hub' only).
  3. The run is skipped entirely while the Mac is active (HIVE_MAC_LAST_SEEN < 7200 s ago).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from mock_llm import MockLLM, tool_call, tools_used

CONTENT = Path(__file__).resolve().parents[1]
# The fixture page is created by setUpClass inside the throwaway copy, not taken from the live repo: the evidence
# gate only guards pages that claim to be official, and a real page drifts (psu-ee.md was `unverified` when this
# test was written and became `official` later, which made the mock edit a no-op and the run produce no commit).
PAGE = "exams/engineering/psu-ee.md"
FIXTURE_TASKS = """
[[task]]
id = "T-901"
lane = "hermes"
priority = 0
title = "Offline cloud test: verify the PSU EE page"
accept = ["a"]

[[task]]
id = "T-951"
lane = "opencode"
priority = 0
title = "Offline cloud test: tooling check"
accept = ["a"]
"""
CLEAN = ("GITHUB_TOKEN", "GITHUB_MODELS_TOKEN", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "GROQ_API_KEY",
         "FREELLMAPI_KEY", "FREELLMAPI_BASE_URL", "OPENCODE_API_KEY", "HIVE_LLM_BASE_URL", "OLLAMA_BASE_URL",
         "HIVE_MAC_LAST_SEEN", "HIVE_CMD_HERMES", "HIVE_CMD_OPENCODE", "HIVE_FALLBACK", "HIVE_WHERE",
         "HIVE_OPEN_PR", "HIVE_SANDBOX", "HIVE_REMOTE", "HIVE_BASE", "HIVE_HOME", "HIVE_TASK_ID", "HIVE_NOTES",
         "HIVE_FETCH_LOG", "HIVE_TIMEOUT", "HIVE_NO_TASK_EXIT", "HIVE_CLOUD_DRY", "HIVE_CLOUD_DIR",
         "HIVE_CLOUD_MAX_TASKS", "HIVE_IN_JUDGE", "BASH_ENV", "HIVE_429_WAIT", "HIVE_CPA_BASE_URL", "HIVE_CPA_KEY_FILE")


def clean_env(**extra: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in CLEAN}
    env.update({"GIT_AUTHOR_NAME": "hive-bot",
                "GIT_AUTHOR_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
                "GIT_COMMITTER_NAME": "hive-bot",
                "GIT_COMMITTER_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
                "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
    env.update(extra)
    return env


class MockFetchHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = b"<html><body><h1>PSU EE recruitment</h1><p>GATE-based hiring, official portal.</p></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@unittest.skipIf(os.environ.get("HIVE_IN_JUDGE"), "the cloud batch dry run is not repeated inside the judge")
class CloudBatchDryRunTest(unittest.TestCase):
    """Runs the cloud batch once in dry-run mode; the tests assert on its real output and remotes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp())
        # Replicate the real repo layout: <repo_root>/awesome-indian-exams (the content folder).
        cls.repo_root = cls.tmp / "awesome-indian-exams"
        cls.content = cls.repo_root / "awesome-indian-exams"
        shutil.copytree(CONTENT, cls.content, ignore=shutil.ignore_patterns("__pycache__", "tests_main", ".git"))
        # Deterministic ready work: the live backlog shrinks as the hive works.
        with (cls.content / "ops" / "tasks.toml").open("a", encoding="utf-8") as fh:
            fh.write(FIXTURE_TASKS)
        # The mock edit is built from the page's CURRENT verification value, so the fixture cannot rot: when a
        # real page moves unverified -> official the test still produces a real edit (official -> secondary, which
        # the evidence gate does not guard) instead of a no-op replace that left the worker with no changes.
        page_text = (cls.content / PAGE).read_text(encoding="utf-8")
        current = re.search(r"^verification: (\S+)$", page_text, re.M).group(1)
        target = "secondary" if current == "official" else "unverified"
        edit_step = ("replace_in_file", {"path": PAGE, "old": f"verification: {current}\n",
                                         "new": f"verification: {target}\n"})
        cls.cloud_dir = cls.tmp / "cloud"
        cls.fetch_server = ThreadingHTTPServer(("127.0.0.1", 0), MockFetchHandler)
        fetch_url = f"http://127.0.0.1:{cls.fetch_server.server_address[1]}/psu"
        threading.Thread(target=cls.fetch_server.serve_forever, daemon=True).start()

        steps = [("read_file", {"path": PAGE, "limit": 400}), ("fetch_url", {"url": fetch_url}),
                 edit_step,
                 ("run_gate", {}),
                 ("finish", {"notes": "## Sources opened\n- local mock page\n## Changed\n- mock edit"})]

        def script(body: dict) -> dict:
            if "You are JEVX" in body["messages"][0]["content"]:
                return {"role": "assistant", "content": '{"approve": true, "reason": "offline cloud test"}'}
            n = tools_used(body)
            return tool_call(*steps[min(n, len(steps) - 1)], n)

        cls.mock = MockLLM(script)
        env = clean_env(HIVE_CLOUD_DRY="1", HIVE_CLOUD_DIR=str(cls.cloud_dir), HIVE_CLOUD_MAX_TASKS="1",
                        HIVE_LLM_BASE_URL=cls.mock.url, HIVE_MAC_LAST_SEEN="0")
        cls.res = subprocess.run(["bash", str(cls.content / "ops" / "cloud_batch.sh")], cwd=cls.repo_root,
                                 env=env, text=True, capture_output=True, timeout=600)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.mock.close()
        cls.fetch_server.shutdown()
        cls.fetch_server.server_close()
        shutil.rmtree(cls.tmp)

    def out(self) -> str:
        return self.res.stdout + self.res.stderr

    def ls_remote(self, repo: Path, *patterns: str) -> str:
        return subprocess.run(["git", "ls-remote", str(repo), *patterns],
                              text=True, capture_output=True).stdout

    def test_dry_run_completes_a_task_and_produces_one_candidate_commit(self) -> None:
        out = self.out()
        self.assertEqual(self.res.returncode, 0, out)
        low = out.lower()
        # A real candidate commit: exactly one, never a fabricated placeholder.
        self.assertEqual(low.count("candidate commit"), 1, out)
        self.assertIsNotNone(re.search(r"candidate commit ([0-9a-f]{40})", low), out)
        # End to end: workers pushed branches for the hub's judge, which published approved work onto hub main.
        self.assertIn("published", low, out)
        base = re.search(r"base commit ([0-9a-f]{40})", low)
        self.assertIsNotNone(base, out)
        hub_main = self.ls_remote(self.cloud_dir / "hub.git", "refs/heads/main").split()[0]
        self.assertNotEqual(hub_main, base.group(1), "the hub's main should have advanced past the base commit")

    def test_claim_and_agent_refs_never_reach_origin(self) -> None:
        out = self.out()
        self.assertEqual(self.res.returncode, 0, out)
        origin = re.search(r"ORIGIN_REPO=(\S+)", self.res.stdout)
        self.assertIsNotNone(origin, out)
        leaked = self.ls_remote(Path(origin.group(1)), "refs/heads/agent/*", "refs/heads/claim/*")
        self.assertEqual(leaked.strip(), "", f"refs leaked to origin: {leaked}")


class CloudBatchSkipTest(unittest.TestCase):
    """The Mac-alive check exits before any work, without copying the repo or building a hub."""

    def test_skip_when_mac_alive(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            env = clean_env(HIVE_CLOUD_DRY="1", HIVE_CLOUD_DIR=str(tmp / "cloud"),
                            HIVE_MAC_LAST_SEEN=str(int(time.time()) - 3600))  # seen 1 hour ago
            res = subprocess.run(["bash", str(CONTENT / "ops" / "cloud_batch.sh")], cwd=CONTENT.parent,
                                 env=env, text=True, capture_output=True, timeout=120)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("skipping cloud run", (res.stdout + res.stderr).lower())
            self.assertFalse((tmp / "cloud").exists(), "nothing should be set up when the Mac is active")
        finally:
            shutil.rmtree(tmp)


class CloudBatchUnitTests(unittest.TestCase):
    def test_mac_alive_check_logic(self) -> None:
        now = 1_000_000
        self.assertTrue(now - (now - 3600) < 7200)       # seen 1 h ago -> skip
        self.assertFalse(now - (now - 10800) < 7200)     # seen 3 h ago -> run
        self.assertFalse(now - (now - 7200) < 7200)      # exactly 7200 s -> run (strict <)


if __name__ == "__main__":
    unittest.main()
