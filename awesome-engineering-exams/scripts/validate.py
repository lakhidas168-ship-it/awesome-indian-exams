#!/usr/bin/env python3
"""Content gate for awesome-engineering-exams.

Deterministic, offline, stdlib-only. Every agent PR must pass this before it can merge.

    python3 scripts/validate.py                 # check, exit 1 on any error
    python3 scripts/validate.py --strict        # also fail on warnings
    python3 scripts/validate.py --write         # regenerate README index + UPDATES.md, then check
    python3 scripts/validate.py --summary FILE  # append a markdown report (GitHub step summary)
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_KEYS = ("title", "exam_id", "conducting_body", "official_site", "cycle", "last_verified", "verification")
REQUIRED_SECTIONS = ("## At a glance", "## Official sources", "## Exam pattern", "## Syllabus", "## Free resources")
VERIFICATION = {"official": "✅ official", "secondary": "🟡 secondary", "unverified": "⚪ unverified"}
LANES = {"jevx", "hermes", "opencode", "human"}
STALE_DAYS = 120
# File-dump hosts are where pirated coaching material circulates. Link to the publisher instead.
BLOCKED_HOSTS = ("t.me", "telegram.me", "telegram.dog", "mega.nz", "scribd.com", "mediafire.com",
                 "terabox.com", "drive.google.com", "dropbox.com")

LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)|<(https?://[^>\s]+)>")
INDEX_START, INDEX_END = "<!-- EXAMS:START -->", "<!-- EXAMS:END -->"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: Path | str, msg: str) -> None:
        self.errors.append(f"{_rel(where)}: {msg}")

    def warn(self, where: Path | str, msg: str) -> None:
        self.warnings.append(f"{_rel(where)}: {msg}")


def _rel(p: Path | str) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    """Flat `key: value` frontmatter only; no YAML dependency."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    meta: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip()
    return meta, text[end + 5:]


def load_official_hosts(root: Path) -> tuple[str, ...]:
    path = root / "ops" / "official-domains.txt"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    return tuple(l.strip().lower() for l in lines if l.strip() and not l.lstrip().startswith("#"))


def host_matches(host: str, entries: tuple[str, ...]) -> bool:
    host = host.lower().split(":")[0]
    return any(host == e or host.endswith("." + e) for e in entries)


def section(body: str, heading: str) -> str:
    start = body.find(heading + "\n")
    if start == -1:
        return ""
    nxt = body.find("\n## ", start + len(heading))
    return body[start: nxt if nxt != -1 else len(body)]


def links(text: str) -> list[str]:
    return [a or b for a, b in LINK_RE.findall(text)]


def parse_date(value: str) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def check_exam_page(path: Path, official: tuple[str, ...], today: dt.date, rep: Report) -> dict[str, str] | None:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    if meta is None:
        rep.error(path, "missing frontmatter block (--- ... ---)")
        return None
    for key in REQUIRED_KEYS:
        if not meta.get(key):
            rep.error(path, f"frontmatter key '{key}' missing or empty")
    if meta.get("exam_id") and meta["exam_id"] != path.stem:
        rep.error(path, f"exam_id '{meta['exam_id']}' must equal file name '{path.stem}'")
    if meta.get("verification") and meta["verification"] not in VERIFICATION:
        rep.error(path, f"verification must be one of {sorted(VERIFICATION)}")
    if meta.get("last_verified"):
        day = parse_date(meta["last_verified"])
        if day is None:
            rep.error(path, "last_verified must be YYYY-MM-DD")
        elif day > today:
            rep.error(path, f"last_verified {day} is in the future")
        elif (today - day).days > STALE_DAYS:
            rep.warn(path, f"last_verified {day} is older than {STALE_DAYS} days; re-verify against the official source")
    site = meta.get("official_site", "")
    if site and not host_matches(urlparse(site).netloc, official):
        rep.error(path, f"official_site host '{urlparse(site).netloc}' is not in ops/official-domains.txt")
    for heading in REQUIRED_SECTIONS:
        if heading + "\n" not in body:
            rep.error(path, f"missing section '{heading}'")
    for url in links(section(body, "## Official sources")):
        host = urlparse(url).netloc
        if not host_matches(host, official):
            rep.error(path, f"non-official link under 'Official sources': {url}")
    return meta


def check_links(path: Path, rep: Report) -> None:
    for url in links(path.read_text(encoding="utf-8")):
        host = urlparse(url).netloc.lower()
        if host_matches(host, BLOCKED_HOSTS):
            rep.error(path, f"blocked file-dump host (link the publisher instead): {url}")
        if url.startswith("http://"):
            rep.warn(path, f"plain http link: {url}")


def check_tasks(root: Path, rep: Report) -> dict[str, dict]:
    path = root / "ops" / "tasks.toml"
    if not path.exists():
        rep.error(path, "missing")
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        rep.error(path, f"invalid TOML: {exc}")
        return {}
    tasks: dict[str, dict] = {}
    for t in data.get("task", []):
        tid = t.get("id", "")
        if not re.fullmatch(r"[A-Z]-\d{3}", tid):
            rep.error(path, f"task id '{tid}' must look like T-001")
            continue
        if tid in tasks:
            rep.error(path, f"duplicate task id {tid}")
        if t.get("lane") not in LANES:
            rep.error(path, f"{tid}: lane must be one of {sorted(LANES)}")
        if not isinstance(t.get("priority"), int):
            rep.error(path, f"{tid}: priority must be an integer (1 = most urgent)")
        if not t.get("title"):
            rep.error(path, f"{tid}: title missing")
        if not t.get("accept"):
            rep.error(path, f"{tid}: accept (acceptance criteria) missing")
        tasks[tid] = t
    for tid, t in tasks.items():
        for dep in t.get("deps", []):
            if dep not in tasks:
                rep.error(path, f"{tid}: unknown dependency {dep}")
    for receipt in sorted((root / "ops" / "done").glob("*.md")):
        if receipt.stem not in tasks:
            rep.error(receipt, f"receipt for unknown task {receipt.stem}")
    return tasks


def render_index(pages: list[tuple[Path, dict[str, str]]]) -> str:
    rows = ["| Exam | Conducted by | Cycle | Evidence | Last verified |", "|---|---|---|---|---|"]
    for path, meta in sorted(pages, key=lambda pm: pm[1].get("title", "")):
        rows.append(f"| [{meta['title']}](exams/{path.name}) | {meta['conducting_body']} | {meta['cycle']} "
                    f"| {VERIFICATION.get(meta['verification'], meta['verification'])} | {meta['last_verified']} |")
    return "\n".join(rows)


def render_updates(root: Path, tasks: dict[str, dict]) -> str:
    entries = []
    for receipt in (root / "ops" / "done").glob("*.md"):
        meta, _ = parse_frontmatter(receipt.read_text(encoding="utf-8"))
        meta = meta or {}
        entries.append((meta.get("finished_at", ""), receipt.stem, meta.get("lane", "?"),
                        tasks.get(receipt.stem, {}).get("title", meta.get("title", ""))))
    lines = ["# Updates", "",
             "Generated from merged task receipts in [`ops/done/`](ops/done/). Newest first. "
             "Each receipt records what changed and the validator output at merge time.", ""]
    if not entries:
        lines.append("_No merged agent updates yet. The hive's first receipts will appear here._")
    for finished, tid, lane, title in sorted(entries, reverse=True):
        lines.append(f"- **{finished[:16].replace('T', ' ')} UTC** · `{tid}` · {lane} · "
                     f"[{title}](ops/done/{tid}.md)")
    return "\n".join(lines) + "\n"


def splice_index(readme: str, index: str) -> str:
    a, b = readme.find(INDEX_START), readme.find(INDEX_END)
    if a == -1 or b == -1 or b < a:
        return readme
    return readme[: a + len(INDEX_START)] + "\n" + index + "\n" + readme[b:]


def run(root: Path, today: dt.date, write: bool = False) -> tuple[Report, list[tuple[Path, dict[str, str]]]]:
    rep = Report()
    official = load_official_hosts(root)
    if not official:
        rep.error(root / "ops" / "official-domains.txt", "missing or empty")
    pages = []
    for page in sorted((root / "exams").glob("*.md")):
        meta = check_exam_page(page, official, today, rep)
        if meta and all(meta.get(k) for k in REQUIRED_KEYS):
            pages.append((page, meta))
    for md in sorted(root.rglob("*.md")):
        check_links(md, rep)
    tasks = check_tasks(root, rep)

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    wanted_readme = splice_index(readme, render_index(pages))
    updates_path = root / "UPDATES.md"
    wanted_updates = render_updates(root, tasks)
    if write:
        if wanted_readme != readme:
            readme_path.write_text(wanted_readme, encoding="utf-8")
        if not updates_path.exists() or updates_path.read_text(encoding="utf-8") != wanted_updates:
            updates_path.write_text(wanted_updates, encoding="utf-8")
    else:
        if INDEX_START not in readme:
            rep.error(readme_path, f"missing index markers {INDEX_START} / {INDEX_END}")
        elif wanted_readme != readme:
            rep.warn(readme_path, "exam index is out of date; run scripts/validate.py --write")
        if not updates_path.exists() or updates_path.read_text(encoding="utf-8") != wanted_updates:
            rep.warn(updates_path, "UPDATES.md is out of date; run scripts/validate.py --write")
    return rep, pages


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--write", action="store_true", help="regenerate README index and UPDATES.md")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--summary", type=Path, help="append a markdown report to this file")
    ap.add_argument("--today", type=parse_date, default=dt.date.today(), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    rep, pages = run(args.root.resolve(), args.today, write=args.write)
    counts = {k: sum(1 for _, m in pages if m["verification"] == k) for k in VERIFICATION}
    status = ", ".join(f"{VERIFICATION[k]}: {n}" for k, n in counts.items())
    for line in rep.errors:
        print(f"ERROR   {line}")
    for line in rep.warnings:
        print(f"WARNING {line}")
    failed = bool(rep.errors) or (args.strict and bool(rep.warnings))
    print(f"{'FAIL' if failed else 'PASS'}: {len(pages)} exam pages ({status}); "
          f"{len(rep.errors)} errors, {len(rep.warnings)} warnings")
    if args.summary:
        with args.summary.open("a", encoding="utf-8") as fh:
            fh.write(f"### Content gate: {'❌ FAIL' if failed else '✅ PASS'}\n\n{status}\n\n")
            for line in rep.errors:
                fh.write(f"- ❌ {line}\n")
            for line in rep.warnings:
                fh.write(f"- ⚠️ {line}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
