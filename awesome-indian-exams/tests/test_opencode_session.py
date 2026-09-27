"""OpenCode Go needs an x-opencode-session header; 429 from a pooled endpoint is retried once (2026-09-28)."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ops"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import free_agent  # noqa: E402
from mock_llm import MockLLM  # noqa: E402


class OpenCodeSessionTest(unittest.TestCase):
    def _llm(self, server: MockLLM, provider: str) -> free_agent.LLM:
        env = {"OPENCODE_API_KEY": "test-key", "HIVE_429_WAIT": "0"}
        with mock.patch.dict(os.environ, env, clear=False), \
             mock.patch.dict(free_agent.PROVIDERS, {provider: (server.url, ("OPENCODE_API_KEY",))}):
            os.environ.pop("HIVE_LLM_BASE_URL", None)
            return free_agent.LLM({"lane_providers": {"opencode": [provider]}, "models": {provider: ["m"]}}, "opencode")

    def test_opencode_go_sends_session_header(self):
        server = MockLLM(lambda body: {"role": "assistant", "content": "ok"})
        self.addCleanup(server.close)
        self._llm(server, "opencode-go").chat([{"role": "user", "content": "hi"}])
        self.assertTrue(server.headers[0].get("x-opencode-session", "").startswith("ses_hive_"))

    def test_other_providers_send_no_session_header(self):
        server = MockLLM(lambda body: {"role": "assistant", "content": "ok"})
        self.addCleanup(server.close)
        self._llm(server, "openrouter").chat([{"role": "user", "content": "hi"}])
        self.assertNotIn("x-opencode-session", server.headers[0])

    def test_429_is_retried_once_then_provider_is_dropped(self):
        server = MockLLM(lambda body: {"role": "assistant", "content": "ok"})
        server.fail_with = 429
        self.addCleanup(server.close)
        with mock.patch.dict(os.environ, {"HIVE_429_WAIT": "0"}):
            llm = self._llm(server, "opencode-go")
            with self.assertRaises(free_agent.NoProvider):
                llm.chat([{"role": "user", "content": "hi"}])
        self.assertEqual(len(server.requests), 2)


if __name__ == "__main__":
    unittest.main()
