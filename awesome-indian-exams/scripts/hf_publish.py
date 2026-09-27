#!/usr/bin/env python3
"""Publish the list's open data as a free Hugging Face dataset, and check the Hugging Face login.

    python3 scripts/hf_publish.py --build DIR   # write the dataset folder only (no network, no token)
    python3 scripts/hf_publish.py --check       # confirm HF_TOKEN works; prints the account name, never the token
    python3 scripts/hf_publish.py --publish     # create <account>/awesome-indian-exams (dataset) and upload

Run by .github/workflows/ai-accounts.yml, by hand only (never on a schedule). The token comes from the HF_TOKEN
environment variable (a repository secret). The dataset holds the same open data as the website: every exam with
its modules, official site and page status, plus the flashcard decks. Needs `huggingface_hub` only for --check and
--publish.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from export_json import REPO, build, load_decks  # noqa: E402

DATASET = "awesome-indian-exams"

CARD = """---
license: cc-by-sa-4.0
language:
- en
pretty_name: Awesome Indian Exams (open data)
tags:
- education
- india
- competitive-exams
- exam-preparation
size_categories:
- n<1K
---

# Awesome Indian Exams: open data

The open data behind [Awesome Indian Exams]({repo}), a free, evidence-gated preparation map for India's
competitive exams.

| File | What it holds |
|---|---|
| `exams.json` | {n_exams} exams: name, family, conducting body, official website, the shared syllabus modules each needs, and the exam page's cycle, evidence status and last-verified date |
| `decks/*.json` | Flashcard decks ({n_decks}); every deck names its official source |

**Evidence status matters.** A page is `official` only when it was checked against the official notification.
`secondary` and `unverified` pages must be confirmed on the official website before anyone relies on them. Always
check the current notification before applying or paying a fee.

Built from the repository by `scripts/hf_publish.py`; the same data is on the website at `/data/exams.json`.
License: CC BY-SA 4.0 (attribution: "Awesome Indian Exams by Rajon Das and contributors"). Links to third-party
websites are not covered; their content belongs to its publishers.
"""


def build_folder(out: Path) -> list[str]:
    """Write the dataset files into `out` and return their relative paths."""
    data, decks = build(ROOT), load_decks(ROOT)
    out.mkdir(parents=True, exist_ok=True)
    (out / "exams.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (out / "decks").mkdir(exist_ok=True)
    for deck_id, deck in decks.items():
        (out / "decks" / f"{deck_id}.json").write_text(json.dumps(deck, ensure_ascii=False, indent=1) + "\n",
                                                        encoding="utf-8")
    (out / "README.md").write_text(CARD.format(repo=REPO, n_exams=len(data["exams"]), n_decks=len(decks)),
                                   encoding="utf-8")
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())


def api():
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        raise SystemExit("HF_TOKEN is not set: add it as a repository secret (see docs/OWNER-CLICKS.md).")
    from huggingface_hub import HfApi   # imported here so --build and the tests need no extra package
    return HfApi(token=token)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", type=Path, metavar="DIR", help="write the dataset folder only")
    mode.add_argument("--check", action="store_true", help="confirm the Hugging Face login")
    mode.add_argument("--publish", action="store_true", help="create the dataset if needed and upload")
    args = ap.parse_args(argv)

    if args.build:
        for f in build_folder(args.build):
            print(f)
        return 0

    hf = api()
    who = hf.whoami()
    name = who.get("name", "")
    print(f"Hugging Face login works: account '{name}'")
    if args.check:
        return 0
    repo_id = f"{name}/{DATASET}"
    hf.create_repo(repo_id, repo_type="dataset", exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        files = build_folder(Path(d))
        hf.upload_folder(folder_path=d, repo_id=repo_id, repo_type="dataset",
                         commit_message="Update open data from the Awesome Indian Exams repository")
    print(f"Published {len(files)} files to https://huggingface.co/datasets/{repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
