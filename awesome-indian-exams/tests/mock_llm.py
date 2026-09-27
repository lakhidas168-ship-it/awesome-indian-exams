"""A scripted OpenAI-compatible chat server for offline hive tests (no network, no keys)."""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable


def tool_call(name: str, args: dict, n: int) -> dict:
    return {"role": "assistant", "content": "",
            "tool_calls": [{"id": f"call_{n}", "type": "function",
                            "function": {"name": name, "arguments": json.dumps(args)}}]}


class MockLLM:
    """`script(request_body) -> message` decides each reply. `fail_with` forces an HTTP error status."""

    def __init__(self, script: Callable[[dict], dict]) -> None:
        self.script = script
        self.fail_with: int | None = None
        self.requests: list[dict] = []
        self.headers: list[dict] = []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                owner.requests.append(body)
                owner.headers.append({k.lower(): v for k, v in self.headers.items()})
                if owner.fail_with:
                    self.send_response(owner.fail_with)
                    self.end_headers()
                    return
                payload = json.dumps({"choices": [{"message": owner.script(body)}]}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/v1"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def tools_used(body: dict) -> int:
    return sum(1 for m in body["messages"] if m.get("role") == "tool")
