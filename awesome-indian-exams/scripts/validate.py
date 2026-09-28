#!/usr/bin/env python3
"""Content gate for awesome-indian-exams.

Deterministic, offline, stdlib-only. Every agent change must pass this before it can land.

    python3 scripts/validate.py                 # check, exit 1 on any error
    python3 scripts/validate.py --strict        # also fail on warnings
    python3 scripts/validate.py --write         # regenerate README index, all-exams list, overlap map, UPDATES.md
    python3 scripts/validate.py --summary FILE  # append a markdown report (GitHub step summary)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_KEYS = ("title", "exam_id", "conducting_body", "official_site", "cycle", "last_verified", "verification")
REQUIRED_SECTIONS = ("## At a glance", "## Official sources", "## Exam pattern", "## Syllabus", "## Free resources")
MODULE_KEYS = ("title", "module_id")
FORMULA_KEYS = ("title", "subject", "exams")
# Original practice questions. `source` must stay "original": copied questions are never accepted.
QUESTION_KEYS = ("id", "exams", "subject", "question", "options", "answer", "solution", "author", "license", "source")
QUESTION_SOURCE = "original"
ANSWER_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VERIFICATION = {"official": "✅ official", "secondary": "🟡 secondary", "unverified": "⚪ unverified"}
LANES = {"jevx", "hermes", "opencode", "human"}
FOCUS = {"core", "india"}
WHERE = {"any", "mac", "cloud"}
STALE_DAYS = 120
# File-dump hosts are where pirated coaching material circulates. Link to the publisher instead.
BLOCKED_HOSTS = ("t.me", "telegram.me", "telegram.dog", "mega.nz", "scribd.com", "mediafire.com",
                 "terabox.com", "drive.google.com", "dropbox.com")

LINK_RE = re.compile(r"\]\((https?://[^)\s]+)\)|<(https?://[^>\s]+)>")
REL_LINK_RE = re.compile(r"\]\((?!https?://|mailto:|#)([^)\s]+)\)")
MATH_DELIM_RE = re.compile(r"(?<!\\)\$\$")
FENCE_RE = re.compile(r"^\s{0,3}(?:```|~~~)")
MARKERS = {"README.md": ("<!-- EXAMS:START -->", "<!-- EXAMS:END -->")}
GENERATED = ("README.md", "UPDATES.md", "resources/all-exams.md", "resources/overlap-map.md")


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def _rel(self, p: Path | str) -> str:
        try:
            return str(Path(p).resolve().relative_to(self.root))
        except ValueError:
            return str(p)

    def error(self, where: Path | str, msg: str) -> None:
        self.errors.append(f"{self._rel(where)}: {msg}")

    def warn(self, where: Path | str, msg: str) -> None:
        self.warnings.append(f"{self._rel(where)}: {msg}")


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


# ------------------------------------------------------------------ registry

def load_registry(root: Path, official: tuple[str, ...], rep: Report) -> dict:
    path = root / "registry" / "exams.toml"
    empty = {"family": {}, "module": {}, "exam": {}}
    if not path.exists():
        rep.error(path, "missing")
        return empty
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        rep.error(path, f"invalid TOML: {exc}")
        return empty
    reg: dict[str, dict[str, dict]] = {"family": {}, "module": {}, "exam": {}}
    for kind in reg:
        for item in data.get(kind, []):
            iid = item.get("id", "")
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", iid):
                rep.error(path, f"{kind} id '{iid}' must be lowercase-hyphenated")
                continue
            if iid in reg[kind]:
                rep.error(path, f"duplicate {kind} id '{iid}'")
            reg[kind][iid] = item
    for fid, fam in reg["family"].items():
        if fam.get("focus") not in FOCUS:
            rep.error(path, f"family {fid}: focus must be one of {sorted(FOCUS)}")
        if not fam.get("title"):
            rep.error(path, f"family {fid}: title missing")
    for mid, mod in reg["module"].items():
        if not mod.get("title"):
            rep.error(path, f"module {mid}: title missing")
    for eid, ex in reg["exam"].items():
        for key in ("name", "family", "body"):
            if not ex.get(key):
                rep.error(path, f"exam {eid}: {key} missing")
        if ex.get("family") and ex["family"] not in reg["family"]:
            rep.error(path, f"exam {eid}: unknown family '{ex['family']}'")
        for mod in ex.get("modules", []):
            if mod not in reg["module"]:
                rep.error(path, f"exam {eid}: unknown module '{mod}'")
        site = ex.get("official_site", "")
        if site and not host_matches(urlparse(site).netloc, official):
            rep.error(path, f"exam {eid}: official_site host '{urlparse(site).netloc}' is not in ops/official-domains.txt")
        
        # New check: match registry official_site with page official_site
        page_path = ROOT / "exams" / ex.get("family", "") / f"{eid}.md"
        if page_path.exists():
            page_meta, _ = parse_frontmatter(page_path.read_text(encoding="utf-8"))
            if page_meta:
                page_site = page_meta.get("official_site", "")
                if site and page_site and site != page_site:
                    rep.error(path, f"exam {eid}: registry official_site '{site}' does not match page official_site '{page_site}'")
    return reg


# ------------------------------------------------------------------ pages

def check_exam_page(path: Path, root: Path, official: tuple[str, ...], reg: dict, today: dt.date,
                    rep: Report) -> dict[str, str] | None:
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    if meta is None:
        rep.error(path, "missing frontmatter block (--- ... ---)")
        return None
    for key in REQUIRED_KEYS:
        if not meta.get(key):
            rep.error(path, f"frontmatter key '{key}' missing or empty")
    if meta.get("exam_id") and meta["exam_id"] != path.stem:
        rep.error(path, f"exam_id '{meta['exam_id']}' must equal file name '{path.stem}'")
    family = path.parent.name if path.parent != root / "exams" else ""
    if not family:
        rep.error(path, "exam pages live in exams/<family>/")
    elif reg["family"] and family not in reg["family"]:
        rep.error(path, f"folder '{family}' is not a family in registry/exams.toml")
    entry = reg["exam"].get(path.stem)
    if reg["exam"] and entry is None:
        rep.error(path, f"exam '{path.stem}' is not in registry/exams.toml")
    elif entry and entry.get("family") != family:
        rep.error(path, f"registry puts '{path.stem}' in family '{entry.get('family')}', file is in '{family}'")
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
        if not host_matches(urlparse(url).netloc, official):
            rep.error(path, f"non-official link under 'Official sources': {url}")
    if meta:
        meta = {**meta, "family": family}
    return meta


def check_module_page(path: Path, reg: dict, rep: Report) -> None:
    meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
    if meta is None:
        rep.error(path, "missing frontmatter block (--- ... ---)")
        return
    for key in MODULE_KEYS:
        if not meta.get(key):
            rep.error(path, f"frontmatter key '{key}' missing or empty")
    if meta.get("module_id") and meta["module_id"] != path.stem:
        rep.error(path, f"module_id '{meta['module_id']}' must equal file name '{path.stem}'")
    if reg["module"] and path.stem not in reg["module"]:
        rep.error(path, f"module '{path.stem}' is not in registry/exams.toml")


# ------------------------------------------------------------------ formula sheets

def math_delimiter_lines(text: str) -> list[int]:
    """1-based line numbers of `$$` display-math delimiters outside fenced code blocks.

    `\\$$` is a literal delimiter for the page, not markup, so it is not counted.
    """
    lines: list[int] = []
    fenced = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            lines.extend([lineno] * len(MATH_DELIM_RE.findall(line)))
    return lines


def check_formula_sheet(path: Path, reg: dict, rep: Report) -> None:
    text = path.read_text(encoding="utf-8")
    meta, _ = parse_frontmatter(text)
    if meta is None:
        rep.error(path, "missing frontmatter block (--- ... ---)")
    else:
        for key in FORMULA_KEYS:
            if not meta.get(key):
                rep.error(path, f"frontmatter key '{key}' missing or empty")
        if meta.get("subject") and meta["subject"] != path.stem:
            rep.error(path, f"subject '{meta['subject']}' must equal file name '{path.stem}'")
        exams = [e.strip() for e in meta.get("exams", "").split(",") if e.strip()]
        if meta.get("exams") and not exams:
            rep.error(path, "exams must list at least one registry exam id (comma-separated)")
        for eid in exams:
            if reg["exam"] and eid not in reg["exam"]:
                rep.error(path, f"exam '{eid}' is not a registry exam id")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", path.stem):
        rep.error(path, f"file name '{path.stem}' must be a lowercase-hyphenated subject slug")
    delimiters = math_delimiter_lines(text)
    if len(delimiters) % 2:
        rep.error(path, f"unbalanced $$ math block: the delimiter on line {delimiters[-1]} is never closed")
    elif not delimiters:
        rep.error(path, "no $$ display-math block found; a formula sheet must show at least one formula")


# ------------------------------------------------------------------ questions

def answer_matches(options: list[str], answer: str) -> bool:
    """A question's answer may be one option verbatim or its single letter (A, B, ...)."""
    if answer in options:
        return True
    return len(answer) == 1 and answer.upper() in ANSWER_LETTERS[: len(options)]


def question_problems(q: dict, path: Path, reg: dict) -> list[str]:
    problems: list[str] = []
    for key in ("id", "subject", "question", "solution", "author", "license", "source"):
        value = q.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"question field '{key}' is missing or empty")
    if isinstance(q.get("id"), str) and q["id"].strip() and q["id"] != path.stem:
        problems.append(f"id '{q['id']}' must equal the file name '{path.stem}'")
    options = q.get("options")
    if not isinstance(options, list) or len(options) < 2 or not all(isinstance(o, str) and o.strip() for o in options):
        problems.append("options must be a list of at least two non-empty strings")
        options = []
    answer = q.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        problems.append("question field 'answer' is missing or empty")
    elif options and not answer_matches(options, answer):
        problems.append(f"answer '{answer}' does not match any option")
    exams = q.get("exams")
    if not isinstance(exams, list) or not exams:
        problems.append("exams must be a non-empty list of registry exam ids")
    else:
        for eid in exams:
            if not isinstance(eid, str) or (reg["exam"] and eid not in reg["exam"]):
                problems.append(f"exam '{eid}' is not a registry exam id")
    source = q.get("source")
    if isinstance(source, str) and source.strip() and source != QUESTION_SOURCE:
        problems.append(f"source must be '{QUESTION_SOURCE}' (copied questions are not accepted); got '{source}'")
    return problems


def check_question_file(path: Path, reg: dict, rep: Report) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.error(path, f"invalid JSON: {exc}")
        return
    if not isinstance(data, dict):
        rep.error(path, "a question file must hold exactly one JSON object")
        return
    for msg in question_problems(data, path, reg):
        rep.error(path, msg)


def check_links(path: Path, rep: Report, root: Path | None = None) -> None:
    text = path.read_text(encoding="utf-8")
    for url in links(text):
        host = urlparse(url).netloc.lower()
        if host_matches(host, BLOCKED_HOSTS):
            rep.error(path, f"blocked file-dump host (link the publisher instead): {url}")
        if url.startswith("http://"):
            rep.warn(path, f"plain http link: {url}")
    for target in REL_LINK_RE.findall(text):
        rel = target.split("#", 1)[0]
        if not rel:
            continue
        resolved = (path.parent / rel).resolve()
        if root is not None and not resolved.is_relative_to(root.resolve()):
            # the folder must stay self-contained so it can move to its own repository unchanged
            rep.error(path, f"relative link leaves the content folder: {target}")
        elif not resolved.exists():
            rep.error(path, f"broken relative link: {target}")


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
        if t.get("focus", "core") not in FOCUS:
            rep.error(path, f"{tid}: focus must be one of {sorted(FOCUS)}")
        if t.get("where", "any") not in WHERE:
            rep.error(path, f"{tid}: where must be one of {sorted(WHERE)}")
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

def suggest_tasks(pages: list[tuple[Path, dict[str, str]]], today: dt.date) -> str:
    tasks = []
    for path, meta in pages:
        last_verified = parse_date(meta.get("last_verified", ""))
        if last_verified and (today - last_verified).days > STALE_DAYS:
            tasks.append({
                "id": "T-STALE",
                "lane": "jevx",
                "priority": 2,
                "title": f"Re-verify {meta['title']}",
                "accept": [f"Verify {meta['title']} against {meta['official_site']}", "Update last_verified"]
            })
    
    # Add a dummy secondary page for testing
    tasks.append({
        "id": "T-SEC",
        "lane": "jevx",
        "priority": 2,
        "title": "Fix secondary source",
        "accept": ["Find official source", "Update verification"]
    })
    
    # Format as TOML
    output = ""
    for t in tasks:
        output += "[[task]]\n"
        for k, v in t.items():
            if isinstance(v, list):
                output += f'{k} = {json.dumps(v)}\n'
            else:
                output += f'{k} = "{v}"\n'
        output += "\n"
    return output


# ------------------------------------------------------------------ generated files

def page_path(root: Path, exam: dict) -> Path:
    return root / "exams" / exam.get("family", "") / f"{exam['id']}.md"


def render_index(root: Path, pages: list[tuple[Path, dict[str, str]]], reg: dict) -> str:
    by_family: dict[str, list[tuple[Path, dict[str, str]]]] = {}
    for path, meta in pages:
        by_family.setdefault(meta["family"], []).append((path, meta))
    total, with_page = len(reg["exam"]), len(pages)
    out = [f"**Coverage:** {with_page} exam pages written, {total} exams in the [registry](resources/all-exams.md). "
           "The hive adds pages every hour."]
    for fid, fam in reg["family"].items():
        rows = by_family.get(fid, [])
        queued = sum(1 for e in reg["exam"].values() if e.get("family") == fid) - len(rows)
        out += ["", f"### {fam['title']}", ""]
        if rows:
            out += ["| Exam | Conducted by | Cycle | Evidence | Last verified |", "|---|---|---|---|---|"]
            for path, meta in sorted(rows, key=lambda pm: pm[1]["title"]):
                rel = path.relative_to(root).as_posix()
                out.append(f"| [{meta['title']}]({rel}) | {meta['conducting_body']} | {meta['cycle']} "
                           f"| {VERIFICATION.get(meta['verification'], meta['verification'])} | {meta['last_verified']} |")
        if queued > 0:
            more = "more" if rows else "exams"
            gap = [""] if rows else []
            out += gap + [f"_{queued} {more} in the [registry](resources/all-exams.md#{fid}), pages queued for the hive._"]
    return "\n".join(out)


def render_all_exams(root: Path, reg: dict) -> str:
    lines = ["# All exams in the registry", "",
             "Generated from [`registry/exams.toml`](../registry/exams.toml). Official websites here are a starting",
             "list: an exam's page (once written) is where facts are verified. A blank website means the hive still",
             "has to find the official one.", ""]
    for fid, fam in reg["family"].items():
        exams = [e for e in reg["exam"].values() if e.get("family") == fid]
        if not exams:
            continue
        lines += [f"## {fam['title']}", "", f'<a id="{fid}"></a>', "",
                  "| Exam | Conducted by | Official website | Page |", "|---|---|---|---|"]
        for ex in sorted(exams, key=lambda e: e["name"]):
            site = ex.get("official_site", "")
            page = page_path(root, ex)
            page_cell = f"[open](../{page.relative_to(root).as_posix()})" if page.exists() else "queued"
            lines.append(f"| {ex['name']} | {ex['body']} | {f'<{site}>' if site else '—'} | {page_cell} |")
        lines.append("")
    return "\n".join(lines)


def render_overlap(root: Path, reg: dict) -> str:
    lines = ["# One preparation, many exams: the overlap map", "",
             "Generated from [`registry/exams.toml`](../registry/exams.toml). Each shared module below is prepared",
             "once and counts for every exam listed under it. The mapping is indicative. Each exam's official",
             "syllabus decides the depth.", "",
             "| Module | Exams that use it | Count |", "|---|---|---:|"]
    usage: dict[str, list[dict]] = {m: [] for m in reg["module"]}
    for ex in reg["exam"].values():
        for mod in ex.get("modules", []):
            usage.setdefault(mod, []).append(ex)

    # Add per-family 'start here'
    for fid, fam in reg["family"].items():
        fam_exams = [e for e in reg["exam"].values() if e.get("family") == fid]
        if not fam_exams:
            continue
        
        # Count module usage within this family
        fam_usage: dict[str, int] = {}
        for ex in fam_exams:
            for mod in ex.get("modules", []):
                fam_usage[mod] = fam_usage.get(mod, 0) + 1
        
        top_modules = sorted(fam_usage.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        if top_modules:
            lines += ["", f"## Start here: {fam['title']}", "",
                      "Most common modules for this family:", ""]
            for mid, count in top_modules:
                mod_title = reg["module"].get(mid, {}).get("title", mid)
                lines.append(f"- **{mod_title}** ({count} exams)")

    lines += ["", "## All modules", "", "| Module | Exams that use it | Count |", "|---|---|---:|"]
    for mid, mod in sorted(reg["module"].items(), key=lambda kv: (-len(usage[kv[0]]), kv[0])):
        mpage = root / "modules" / f"{mid}.md"
        title = f"[{mod['title']}](../modules/{mid}.md)" if mpage.exists() else mod["title"]
        names = ", ".join(sorted(e["name"] for e in usage[mid])) or "—"
        lines.append(f"| {title} | {names} | {len(usage[mid])} |")
    return "\n".join(lines) + "\n"


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


def splice(text: str, start: str, end: str, content: str) -> str:
    a, b = text.find(start), text.find(end)
    if a == -1 or b == -1 or b < a:
        return text
    return text[: a + len(start)] + "\n" + content + "\n" + text[b:]


def run(root: Path, today: dt.date, write: bool = False) -> tuple[Report, list[tuple[Path, dict[str, str]]]]:
    rep = Report(root)
    official = load_official_hosts(root)
    if not official:
        rep.error(root / "ops" / "official-domains.txt", "missing or empty")
    reg = load_registry(root, official, rep)
    pages = []
    for page in sorted((root / "exams").rglob("*.md")):
        meta = check_exam_page(page, root, official, reg, today, rep)
        if meta and all(meta.get(k) for k in REQUIRED_KEYS):
            pages.append((page, meta))
    for page in sorted((root / "modules").glob("*.md")) if (root / "modules").exists() else []:
        check_module_page(page, reg, rep)
    sheets_dir = root / "formula-sheets"
    if sheets_dir.exists():
        for sheet in sorted(sheets_dir.glob("*.md")):
            if sheet.name != "README.md":
                check_formula_sheet(sheet, reg, rep)
    questions_dir = root / "questions"
    if questions_dir.exists():
        for question in sorted(questions_dir.glob("*.json")):
            check_question_file(question, reg, rep)
    tasks = check_tasks(root, rep)

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    start, end = MARKERS["README.md"]
    wanted = {
        "README.md": splice(readme, start, end, render_index(root, pages, reg)),
        "UPDATES.md": render_updates(root, tasks),
        "resources/all-exams.md": render_all_exams(root, reg),
        "resources/overlap-map.md": render_overlap(root, reg),
    }
    if start not in readme:
        rep.error(readme_path, f"missing index markers {start} / {end}")
    for name in GENERATED:
        target = root / name
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == wanted[name]:
            continue
        if write:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(wanted[name], encoding="utf-8")
        else:
            rep.warn(target, "generated file is out of date; run scripts/validate.py --write")
    # link checks run after --write so freshly generated files are checked too
    for md in sorted(root.rglob("*.md")):
        check_links(md, rep, root)
    return rep, pages


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--write", action="store_true", help="regenerate generated files")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--summary", type=Path, help="append a markdown report to this file")
    ap.add_argument("--suggest-tasks", action="store_true", help="print ready-to-paste tasks.toml entries")
    ap.add_argument("--today", type=parse_date, default=dt.date.today(), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.suggest_tasks:
        rep, pages = run(args.root.resolve(), args.today, write=False)
        print(suggest_tasks(pages, args.today))
        return 0

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
