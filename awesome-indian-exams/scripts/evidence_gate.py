#!/usr/bin/env python3
"""Evidence gate: a page may only become `verification: official` with a code-recorded fetch of an official source.

For every exam page an agent change marks official (newly, or with a new last_verified date), the task receipt in
the same change must contain a fetch record, written by code (free_agent.py or the hive MCP server), that shows:
  * HTTP 200 from a host on ops/official-domains.txt,
  * a URL that is listed under the page's "## Official sources",
  * fetched within one day of the page's last_verified date.

    python3 scripts/evidence_gate.py --base origin/main --branch agent/hermes/T-201

Branches that are not agent branches pass (human contributions get human review).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

CONTENT = Path(__file__).resolve().parents[1]
# Only the first, unquoted, line-anchored section counts: agent notes are quoted and come after it.
FETCH_BLOCK = re.compile(r"^## Sources fetched \(code\)\n+```(?:jsonl)?\n(.*?)^```", re.S | re.M)


def git(*args: str, root: Path = CONTENT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=check)


def norm(url: str) -> str:
    url = url.split("#", 1)[0].strip()
    scheme, _, rest = url.partition("://")
    host, _, path = rest.partition("/")
    return f"{scheme.lower()}://{host.lower()}/{path}".rstrip("/")


def fetch_records(receipt_text: str) -> list[dict]:
    records = []
    match = FETCH_BLOCK.search(receipt_text)
    for block in [match.group(1)] if match else []:
        for line in block.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def page_problems(path: str, head_text: str, base_text: str | None, records: list[dict]) -> list[str]:
    head, body = validate.parse_frontmatter(head_text)
    if not head or head.get("verification") != "official":
        return []
    base = validate.parse_frontmatter(base_text)[0] if base_text else None
    if base and base.get("verification") == "official" and base.get("last_verified") == head.get("last_verified"):
        return []  # already official, not re-dated: nothing new is claimed
    listed = {norm(u) for u in validate.links(validate.section(body, "## Official sources"))}
    day = validate.parse_date(head.get("last_verified", ""))
    for rec in records:
        urls = {norm(rec.get("url", "")), norm(rec.get("final_url", "") or rec.get("url", ""))}
        at = validate.parse_date(str(rec.get("at", ""))[:10])
        if (rec.get("status") == 200 and rec.get("official") and urls & listed
                and day and at and abs((day - at).days) <= 1):
            return []
    return [f"{path}: marked official, but no code-recorded fetch (HTTP 200, official domain, listed under "
            f"'Official sources', within a day of last_verified) backs it"]


def check(base: str, branch: str, worktree: Path | None = None) -> list[str]:
    """`worktree`: judge a checkout other than the one this script lives in (the judge runs main's copy)."""
    if not branch.startswith("agent/"):
        return []
    top = Path(git("rev-parse", "--show-toplevel", root=worktree or CONTENT).stdout.strip())
    prefix = CONTENT.name
    changed = git("diff", "--name-only", f"{base}...HEAD", root=top).stdout.split()
    records: list[dict] = []
    for path in changed:
        if path.startswith(f"{prefix}/ops/done/") and path.endswith(".md"):
            records += fetch_records((top / path).read_text(encoding="utf-8"))
    problems: list[str] = []
    for path in changed:
        if not (path.startswith(f"{prefix}/exams/") and path.endswith(".md")) or not (top / path).exists():
            continue
        prior = git("show", f"{base}:{path}", root=top, check=False)
        problems += page_problems(path, (top / path).read_text(encoding="utf-8"),
                                  prior.stdout if prior.returncode == 0 else None, records)
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--worktree", type=Path, help="checkout to judge (default: this script's own)")
    args = ap.parse_args(argv)
    problems = check(args.base, args.branch, args.worktree)
    for p in problems:
        print(f"ERROR {p}")
    print(f"{'FAIL' if problems else 'PASS'}: evidence gate for {args.branch}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
