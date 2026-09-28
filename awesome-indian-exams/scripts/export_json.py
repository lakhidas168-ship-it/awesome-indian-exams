#!/usr/bin/env python3
"""Export the list as open data: one JSON file that apps, planners and other lists can build on.

    python3 scripts/export_json.py [--out PATH] [--js PATH]   # default: print the JSON to stdout

The website build (.github/workflows/pages.yml) publishes it at /data/exams.json. `--js` also writes data/data.js
(`window.AIE_DATA` with the exams, the flashcard decks in data/flashcards/ and the original questions in
questions/), which the study tools read, so they
work even in the offline copy opened from disk. Nothing here is committed, so the files can never go stale or
conflict with the hive: they are rebuilt from the registry, the pages and the decks on every deploy. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate import page_path, parse_frontmatter  # noqa: E402

REPO = "https://github.com/lakhidas168-ship-it/awesome-indian-exams"
PAGE_KEYS = ("cycle", "verification", "last_verified", "conducting_body", "official_site")


def build(root: Path = ROOT) -> dict:
    reg = tomllib.loads((root / "registry" / "exams.toml").read_text(encoding="utf-8"))
    modules = {m["id"]: m for m in reg.get("module", [])}
    exams = []
    for ex in reg.get("exam", []):
        item = {
            "id": ex["id"],
            "name": ex.get("name", ""),
            "family": ex.get("family", ""),
            "conducting_body": ex.get("body", ""),
            "official_site": ex.get("official_site", ""),
            "modules": list(ex.get("modules", [])),
            "page": None,
        }
        path = page_path(root, ex)
        if path.exists():
            meta, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
            meta = meta or {}
            rel = path.relative_to(root).as_posix()
            item["page"] = {"path": rel, "url": f"{REPO}/blob/main/awesome-indian-exams/{rel}"}
            item["page"].update({k: meta[k] for k in PAGE_KEYS if meta.get(k)})
        exams.append(item)
    used = {m for ex in exams for m in ex["modules"]}
    return {
        "source": REPO,
        "license": "see LICENSE.md in the repository",
        "note": "verification is 'official' only when the page was checked against the official notification; "
                "always confirm numbers and dates on the official site before applying or paying a fee",
        "families": [{"id": f["id"], "title": f.get("title", "")} for f in reg.get("family", [])],
        "modules": [
            {"id": mid, "title": m.get("title", ""), "exams": sorted(ex["id"] for ex in exams if mid in ex["modules"]),
             "page": f"modules/{mid}.md" if (root / "modules" / f"{mid}.md").exists() else None}
            for mid, m in modules.items() if mid in used or (root / "modules" / f"{mid}.md").exists()
        ],
        "exams": exams,
    }


def load_decks(root: Path = ROOT) -> dict:
    decks = {}
    for path in sorted((root / "data" / "flashcards").glob("*.json")):
        deck = json.loads(path.read_text(encoding="utf-8"))
        decks[deck["id"]] = deck
    return decks


def load_questions(root: Path = ROOT) -> list:
    """Original practice questions (questions/*.json, format in questions/README.md)."""
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted((root / "questions").glob("*.json"))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, help="write the JSON here instead of stdout")
    ap.add_argument("--js", type=Path, help="also write the tools' data file (window.AIE_DATA) here")
    args = ap.parse_args(argv)
    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    elif not args.js:
        sys.stdout.write(text)
    if args.js:
        payload = json.dumps({"exams": data, "decks": load_decks(), "questions": load_questions()},
                             ensure_ascii=False, separators=(",", ":"))
        args.js.parent.mkdir(parents=True, exist_ok=True)
        # "</" is escaped so the data can never close a script element early.
        args.js.write_text("window.AIE_DATA = " + payload.replace("</", "<\\/") + ";\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
