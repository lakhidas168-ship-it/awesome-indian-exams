"""Self-tests for the formula-sheet format.

Each test proves a bad sheet is rejected by the content gate. The cloud judge runs main's copy of the gate
against these files, so a sheet whose `$$` display-math blocks do not balance must never pass.
"""
from __future__ import annotations

import datetime as dt
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402

TODAY = dt.date(2026, 9, 27)
REGISTRY = """
[[family]]
id = "engineering"
title = "Engineering"
focus = "core"

[[module]]
id = "ee-core"
title = "Electrical engineering core"

[[exam]]
id = "gate-ee"
name = "GATE EE"
family = "engineering"
body = "IITs"
modules = ["ee-core"]
"""
GOOD_SHEET = """---
title: Sample sheet
subject: sample-sheet
exams: gate-ee
---

# Sample sheet

## DC basics

$$ V = IR $$

$$ P = VI = I^2 R $$
"""


class FormulaSheets(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "exams").mkdir()
        (self.tmp / "ops" / "done").mkdir(parents=True)
        (self.tmp / "registry").mkdir()
        shutil.copy(ROOT / "ops" / "official-domains.txt", self.tmp / "ops")
        (self.tmp / "registry" / "exams.toml").write_text(REGISTRY, encoding="utf-8")
        (self.tmp / "ops" / "tasks.toml").write_text(
            '[[task]]\nid = "T-103"\nlane = "opencode"\npriority = 3\ntitle = "t"\naccept = ["a"]\n', encoding="utf-8")
        (self.tmp / "README.md").write_text("<!-- EXAMS:START -->\n<!-- EXAMS:END -->\n", encoding="utf-8")
        (self.tmp / "formula-sheets").mkdir()
        self.sheet = self.tmp / "formula-sheets" / "sample-sheet.md"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def errors(self, text: str, name: str = "sample-sheet.md") -> list[str]:
        path = self.tmp / "formula-sheets" / name
        path.write_text(text, encoding="utf-8")
        rep, _ = validate.run(self.tmp, TODAY)
        return rep.errors

    def test_good_sheet_passes(self) -> None:
        self.assertEqual(self.errors(GOOD_SHEET), [])

    def test_unbalanced_block_rejected(self) -> None:
        bad = GOOD_SHEET.replace("$$ P = VI = I^2 R $$", "$$ P = VI = I^2 R")
        errs = self.errors(bad)
        self.assertTrue(any("unbalanced $$ math block" in e for e in errs), errs)

    def test_stray_closing_delimiter_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET + "\n$$\n")
        self.assertTrue(any("unbalanced $$ math block" in e for e in errs), errs)

    def test_escaped_delimiter_is_literal(self) -> None:
        self.assertEqual(self.errors(GOOD_SHEET + "\nWrite \\$$ for a literal delimiter.\n"), [])

    def test_fenced_code_is_ignored(self) -> None:
        text = GOOD_SHEET + "\n```text\n$$ not a formula\n```\n"
        self.assertEqual(self.errors(text), [])

    def test_missing_frontmatter_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.split("---\n", 2)[2])
        self.assertTrue(any("frontmatter" in e for e in errs), errs)

    def test_missing_title_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("title: Sample sheet\n", ""))
        self.assertTrue(any("'title'" in e for e in errs), errs)

    def test_missing_subject_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("subject: sample-sheet\n", ""))
        self.assertTrue(any("'subject'" in e for e in errs), errs)

    def test_subject_must_match_file_name(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("subject: sample-sheet", "subject: other-subject"))
        self.assertTrue(any("must equal file name" in e for e in errs), errs)

    def test_bad_file_name_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("subject: sample-sheet", "subject: Bad_Name"), name="Bad_Name.md")
        self.assertTrue(any("lowercase-hyphenated" in e for e in errs), errs)

    def test_missing_exams_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("exams: gate-ee\n", ""))
        self.assertTrue(any("'exams'" in e for e in errs), errs)

    def test_unknown_exam_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("exams: gate-ee", "exams: not-a-real-exam"))
        self.assertTrue(any("not a registry exam id" in e for e in errs), errs)

    def test_no_math_block_rejected(self) -> None:
        errs = self.errors(GOOD_SHEET.replace("$$ V = IR $$", "V = IR").replace("$$ P = VI = I^2 R $$", "P = VI"))
        self.assertTrue(any("no $$ display-math block" in e for e in errs), errs)

    def test_repo_sheets_pass(self) -> None:
        rep, _ = validate.run(ROOT, dt.date.today())
        self.assertEqual(rep.errors, [])


if __name__ == "__main__":
    unittest.main()
