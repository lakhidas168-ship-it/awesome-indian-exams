"""Self-tests for the original practice-question format.

Each test proves a bad question file is rejected by the content gate. The cloud judge runs main's copy of the
gate against these files, so a question that loses its answer, solution or author must never pass.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
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
GOOD_QUESTION = {
    "id": "sample-question-01",
    "exams": ["gate-ee"],
    "subject": "Electric Circuits",
    "question": "Two 1 ohm resistors in series across 2 V: what is the current?",
    "options": ["0.5 A", "1 A", "2 A", "4 A"],
    "answer": "1 A",
    "solution": "Series R = 2 ohm, I = V/R = 2/2 = 1 A.",
    "author": "Test Author",
    "license": "CC BY-SA 4.0",
    "source": "original",
}


class Questions(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "exams").mkdir()
        (self.tmp / "ops" / "done").mkdir(parents=True)
        (self.tmp / "registry").mkdir()
        shutil.copy(ROOT / "ops" / "official-domains.txt", self.tmp / "ops")
        (self.tmp / "registry" / "exams.toml").write_text(REGISTRY, encoding="utf-8")
        (self.tmp / "ops" / "tasks.toml").write_text(
            '[[task]]\nid = "T-101"\nlane = "opencode"\npriority = 2\ntitle = "t"\naccept = ["a"]\n', encoding="utf-8")
        (self.tmp / "README.md").write_text("<!-- EXAMS:START -->\n<!-- EXAMS:END -->\n", encoding="utf-8")
        (self.tmp / "questions").mkdir()
        self.question = self.tmp / "questions" / "sample-question-01.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def errors(self, question: dict, name: str = "sample-question-01.json") -> list[str]:
        path = self.tmp / "questions" / name
        path.write_text(json.dumps(question), encoding="utf-8")
        rep, _ = validate.run(self.tmp, TODAY)
        return rep.errors

    def test_good_question_passes(self) -> None:
        self.assertEqual(self.errors(GOOD_QUESTION), [])

    def test_missing_answer_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        del bad["answer"]
        self.assertTrue(any("answer" in e for e in self.errors(bad)))

    def test_missing_solution_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        del bad["solution"]
        self.assertTrue(any("solution" in e for e in self.errors(bad)))

    def test_missing_author_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        del bad["author"]
        self.assertTrue(any("author" in e for e in self.errors(bad)))

    def test_empty_answer_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        bad["answer"] = "   "
        self.assertTrue(any("answer" in e for e in self.errors(bad)))

    def test_answer_must_be_an_option(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        bad["answer"] = "3 A"
        self.assertTrue(any("does not match any option" in e for e in self.errors(bad)))

    def test_letter_answer_is_accepted(self) -> None:
        good = copy.deepcopy(GOOD_QUESTION)
        good["answer"] = "B"
        self.assertEqual(self.errors(good), [])

    def test_copied_source_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        bad["source"] = "coaching-material"
        self.assertTrue(any("source must be 'original'" in e for e in self.errors(bad)))

    def test_unknown_exam_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        bad["exams"] = ["not-a-real-exam"]
        self.assertTrue(any("not a registry exam id" in e for e in self.errors(bad)))

    def test_missing_options_rejected(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        del bad["options"]
        self.assertTrue(any("options" in e for e in self.errors(bad)))

    def test_id_must_match_file_name(self) -> None:
        bad = copy.deepcopy(GOOD_QUESTION)
        bad["id"] = "other-id"
        self.assertTrue(any("must equal the file name" in e for e in self.errors(bad)))

    def test_invalid_json_rejected(self) -> None:
        (self.tmp / "questions" / "sample-question-01.json").write_text("{not json", encoding="utf-8")
        rep, _ = validate.run(self.tmp, TODAY)
        self.assertTrue(any("invalid JSON" in e for e in rep.errors))

    def test_repo_questions_pass(self) -> None:
        rep, _ = validate.run(ROOT, dt.date.today())
        self.assertEqual(rep.errors, [])


if __name__ == "__main__":
    unittest.main()
