"""Tests for ops/free_agent.py against a scripted local LLM (no network, no keys)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from mock_llm import MockLLM, tool_call, tools_used

CONTENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONTENT / "ops"))
import free_agent  # noqa: E402

KEY_ENVS = ("GITHUB_TOKEN", "GITHUB_MODELS_TOKEN", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "GROQ_API_KEY",
            "HIVE_LLM_BASE_URL", "OLLAMA_BASE_URL", "FREELLMAPI_KEY", "FREELLMAPI_BASE_URL", "OPENCODE_API_KEY",
            "BASH_ENV", "HIVE_IN_JUDGE")


def clean_env(**extra: str) -> dict:
    env = {k: v for k, v in os.environ.items() if k not in KEY_ENVS}
    return {**env, "HIVE_429_WAIT": "0", **extra}


class Page(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        body = b"<html><body><h1>Notice</h1><p>Exam pattern: 100 questions.</p><script>x()</script></body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class FreeAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.content = self.tmp / CONTENT.name
        shutil.copytree(CONTENT, self.content, ignore=shutil.ignore_patterns("__pycache__", "tests_main"))
        self.fetch_log = self.tmp / "fetch.jsonl"
        self.notes = self.tmp / "notes.md"
        self.web = ThreadingHTTPServer(("127.0.0.1", 0), Page)
        threading.Thread(target=self.web.serve_forever, daemon=True).start()
        self.page_url = f"http://127.0.0.1:{self.web.server_address[1]}/notice"
        self.mocks: list[MockLLM] = []

    def tearDown(self) -> None:
        for m in self.mocks:
            m.close()
        self.web.shutdown()
        self.web.server_close()
        shutil.rmtree(self.tmp)

    def mock(self, script) -> MockLLM:
        m = MockLLM(script)
        self.mocks.append(m)
        return m

    def run_agent(self, env: dict, lane: str = "hermes") -> subprocess.CompletedProcess:
        env = {**env, "HIVE_TASK_ID": "T-201", "HIVE_FETCH_LOG": str(self.fetch_log), "HIVE_NOTES": str(self.notes)}
        return subprocess.run([sys.executable, str(self.content / "ops" / "free_agent.py"), "--lane", lane,
                               "do the task"], env=env, text=True, capture_output=True, timeout=120)

    def test_edits_page_records_fetch_and_finishes(self) -> None:
        page = "exams/ssc/ssc-cgl.md"
        steps = [("read_file", {"path": page, "limit": 400}),
                 ("fetch_url", {"url": self.page_url}),
                 ("replace_in_file", {"path": page, "old": "## Free resources\n",
                                      "new": "## Free resources\n\n- Added by the test.\n"}),
                 ("run_gate", {}),
                 ("finish", {"notes": "## Sources opened\n- test page"})]
        m = self.mock(lambda body: tool_call(*steps[tools_used(body)], tools_used(body)))
        res = self.run_agent(clean_env(HIVE_LLM_BASE_URL=m.url))
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Added by the test.", (self.content / page).read_text(encoding="utf-8"))
        self.assertIn("Sources opened", self.notes.read_text(encoding="utf-8"))
        record = json.loads(self.fetch_log.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(record["status"], 200)
        self.assertFalse(record["official"])  # 127.0.0.1 is not an official domain
        self.assertEqual(len(record["sha256"]), 64)
        fetched_text = [msg for msg in m.requests[2]["messages"] if msg["role"] == "tool"][-1]["content"]
        self.assertIn("100 questions", fetched_text)
        self.assertNotIn("x()", fetched_text)  # scripts are stripped

    def test_refuses_guardrails_other_lanes_and_escapes(self) -> None:
        attempts = ["ops/judge.py", "scripts/validate.py", "../outside.txt", "ops/done/T-201.md",
                    "README.md", ".agents/skills/exam-page/SKILL.md"]
        steps = [("write_file", {"path": p, "content": "pwned"}) for p in attempts] + [("finish", {"notes": "x"})]
        m = self.mock(lambda body: tool_call(*steps[tools_used(body)], tools_used(body)))
        before = {p: (self.content / p).read_text(encoding="utf-8") for p in attempts if (self.content / p).exists()}
        res = self.run_agent(clean_env(HIVE_LLM_BASE_URL=m.url))
        self.assertEqual(res.returncode, 0, res.stderr)
        results = [msg["content"] for msg in m.requests[-1]["messages"] if msg["role"] == "tool"]
        self.assertEqual(len([r for r in results if r.startswith("refused")]), len(attempts), results)
        for p, text in before.items():
            self.assertEqual((self.content / p).read_text(encoding="utf-8"), text, p)
        self.assertFalse((self.tmp / "outside.txt").exists())

    def test_falls_back_when_first_provider_is_rate_limited(self) -> None:
        limited = self.mock(lambda body: {})
        limited.fail_with = 429
        backup = self.mock(lambda body: tool_call("finish", {"notes": "from backup"}, 0))
        env = clean_env(HIVE_LLM_BASE_URL=limited.url, OLLAMA_BASE_URL=backup.url)
        res = self.run_agent(env)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue(limited.requests)
        self.assertTrue(backup.requests)
        self.assertIn("from backup", self.notes.read_text(encoding="utf-8"))

    def test_no_provider_exits_75_so_the_task_is_requeued(self) -> None:
        limited = self.mock(lambda body: {})
        limited.fail_with = 429
        env = clean_env(HIVE_LLM_BASE_URL=limited.url, OLLAMA_BASE_URL="http://127.0.0.1:9/v1")
        self.assertEqual(self.run_agent(env).returncode, free_agent.EX_TEMPFAIL)

    def test_freellmapi_router_is_a_fallback_only_when_its_key_is_set(self) -> None:
        limited = self.mock(lambda body: {})
        limited.fail_with = 429
        router = self.mock(lambda body: tool_call("finish", {"notes": "from freellmapi"}, 0))
        dead_ollama = "http://127.0.0.1:9/v1"
        env = clean_env(HIVE_LLM_BASE_URL=limited.url, FREELLMAPI_BASE_URL=router.url, OLLAMA_BASE_URL=dead_ollama)
        self.assertEqual(self.run_agent(env).returncode, free_agent.EX_TEMPFAIL)  # no key: router skipped
        self.assertFalse(router.requests)
        res = self.run_agent({**env, "FREELLMAPI_KEY": "test-key"})
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(router.requests[0]["model"], "auto")
        self.assertIn("from freellmapi", self.notes.read_text(encoding="utf-8"))

    def test_trim_keeps_requests_under_budget(self) -> None:
        messages = [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}]
        for i in range(10):
            messages += [{"role": "assistant", "content": "", "tool_calls": []},
                         {"role": "tool", "tool_call_id": str(i), "content": "x" * 5000}]
        free_agent.trim(messages, 20000)
        self.assertLessEqual(sum(len(json.dumps(m)) for m in messages), 20000)
        self.assertEqual(messages[-1]["content"], "x" * 5000)  # the newest output is kept


if __name__ == "__main__":
    unittest.main()
