#!/usr/bin/env python3
"""Export the list as open data: one JSON file that apps, planners and other lists can build on.

    python3 scripts/export_json.py [--out PATH]      # default: print to stdout

The website build (.github/workflows/pages.yml) publishes it at /data/exams.json. Nothing here is committed, so
the file can never go stale or conflict with the hive: it is rebuilt from the registry and the pages on every
deploy. Stdlib only.
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, help="write here instead of stdout")
    args = ap.parse_args(argv)
    text = json.dumps(build(), ensure_ascii=False, indent=1) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
