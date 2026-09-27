"""Protocol test for the hive MCP server over stdio."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1]


def session(*requests: dict) -> list[dict]:
    lines = "\n".join(json.dumps(r) for r in requests) + "\n"
    res = subprocess.run([sys.executable, str(CONTENT / "ops" / "mcp_server.py")], input=lines, text=True,
                         capture_output=True, timeout=60)
    return [json.loads(line) for line in res.stdout.splitlines() if line.strip()]


class McpServer(unittest.TestCase):
    def test_handshake_list_and_calls(self) -> None:
        replies = session(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "list_exams", "arguments": {"family": "medical"}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "check_lane_scope", "arguments": {
                 "branch": "agent/hermes/T-001", "paths": [f"{CONTENT.name}/ops/judge.py"]}}},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "read_skill", "arguments": {"name": "exam-page"}}},
            {"jsonrpc": "2.0", "id": 6, "method": "does/not/exist"},
        )
        by_id = {r["id"]: r for r in replies}
        self.assertEqual(len(replies), 6)  # the notification gets no reply
        self.assertEqual(by_id[1]["result"]["protocolVersion"], "2025-06-18")
        names = {t["name"] for t in by_id[2]["result"]["tools"]}
        self.assertTrue({"hive_status", "next_task", "validate_content", "fetch_url", "exam_info"} <= names)
        self.assertIn("neet-ug", by_id[3]["result"]["content"][0]["text"])
        self.assertIn("may not change", by_id[4]["result"]["content"][0]["text"])
        self.assertIn("Exam page", by_id[5]["result"]["content"][0]["text"])
        self.assertEqual(by_id[6]["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
