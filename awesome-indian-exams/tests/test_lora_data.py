"""Self-tests for the LoRA data preparation (`scripts/lora_data.py`).

The important one is `test_eval_sets_never_leak_into_training`: the T-122 files must stay held out, or every
adapter score in the notebook would be a lie.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lora_data  # noqa: E402


def question(qid: str, answer: str = "10 V", options: list[str] | None = None) -> dict:
    return {
        "id": qid,
        "exams": ["gate-ee"],
        "subject": "Electric Circuits",
        "question": f"Sample {qid}?",
        "options": options or ["5 V", "10 V", "15 V"],
        "answer": answer,
        "solution": "V = IR.",
        "author": "Test",
        "license": "CC BY-NC-SA 4.0",
        "source": "original",
    }


class Questions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.questions = lora_data.load_questions(ROOT / "questions")
        cls.train, cls.held_out = lora_data.split_train_eval(cls.questions)

    def test_split_is_disjoint_and_complete(self) -> None:
        self.assertEqual(set(self.train) & set(self.held_out), set())
        self.assertEqual(set(self.train) | set(self.held_out), set(self.questions))

    def test_t122_set_is_held_out(self) -> None:
        self.assertEqual(len(self.held_out), 50)
        self.assertTrue(all(lora_data.is_eval_question(qid) for qid in self.held_out))
        self.assertTrue(any(qid.startswith("ee-eval-") for qid in self.held_out))

    def test_train_never_contains_an_eval_id(self) -> None:
        self.assertFalse(any(lora_data.is_eval_question(qid) for qid in self.train))

    def test_eval_sets_never_leak_into_training(self) -> None:
        exam_family = lora_data.load_exam_families(ROOT / "registry" / "exams.toml")
        examples = lora_data.build_all_family_examples(ROOT, self.train, exam_family)
        blob = json.dumps(examples)
        for qid, q in self.held_out.items():
            self.assertNotIn(q["question"], blob, f"evaluation question {qid} leaked into training")

    def test_load_questions_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "bad.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                lora_data.load_questions(folder)

    def test_load_questions_rejects_missing_id(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "no-id.json"
            path.write_text(json.dumps({"question": "x"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                lora_data.load_questions(folder)


class Scoring(unittest.TestCase):
    OPTIONS = ["5 V", "10 V", "15 V"]

    def test_answer_index_verbatim_and_letter(self) -> None:
        self.assertEqual(lora_data.answer_index(question("q", "10 V")), 1)
        self.assertEqual(lora_data.answer_index(question("q", "B")), 1)
        self.assertIsNone(lora_data.answer_index(question("q", "99 V")))

    def test_score_prediction_reads_answer_letter(self) -> None:
        self.assertEqual(lora_data.score_prediction("ANSWER: C\nREASON: nothing", self.OPTIONS), 2)
        self.assertEqual(lora_data.score_prediction("answer = b", self.OPTIONS), 1)

    def test_score_prediction_falls_back_to_option_text(self) -> None:
        self.assertEqual(lora_data.score_prediction("I think 10 V is right.", self.OPTIONS), 1)

    def test_score_prediction_rejects_out_of_range_letter(self) -> None:
        self.assertIsNone(lora_data.score_prediction("ANSWER: E", self.OPTIONS))

    def test_summarise_counts_and_probes(self) -> None:
        not_sure = "Not sure - check the official notification"
        questions = {
            "a": question("a", "10 V"),
            "b": question("b", "5 V"),
            "c": question("c", not_sure, ["1 V", "2 V", not_sure]),
        }
        summary = lora_data.summarise(questions, {"a": 1, "b": 2, "c": 2})
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["correct"], 2)
        self.assertEqual(summary["unparsed"], 0)
        self.assertEqual(summary["probe_total"], 1)
        self.assertEqual(summary["probe_correct"], 1)
        self.assertEqual(summary["wrong"], ["b"])

    def test_summarise_counts_missing_prediction_as_wrong(self) -> None:
        summary = lora_data.summarise({"a": question("a")}, {})
        self.assertEqual(summary["correct"], 0)
        self.assertEqual(summary["unparsed"], 1)


class Examples(unittest.TestCase):
    def test_question_families_uses_registry_map(self) -> None:
        q = {"exams": ["gate-ee", "ssc-cgl", "not-an-exam"]}
        mapping = {"gate-ee": "engineering", "ssc-cgl": "ssc"}
        self.assertEqual(lora_data.question_families(q, mapping), ["engineering", "ssc"])

    def test_page_examples_carry_the_source_and_a_not_sure_answer(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            page = Path(folder) / "exams" / "engineering" / "gate-ee.md"
            page.parent.mkdir(parents=True)
            page.write_text(
                "---\n"
                "title: GATE EE\n"
                "exam_id: gate-ee\n"
                "conducting_body: IITs\n"
                "official_site: https://gate2027.iitm.ac.in/\n"
                "cycle: 2027\n"
                "last_verified: 2026-09-01\n"
                "verification: official\n"
                "---\n\n"
                "## Exam pattern\n\nThree-hour CBT, 65 questions.\n\n"
                "## Official sources\n\n<https://gate2027.iitm.ac.in/>\n",
                encoding="utf-8")
            examples = lora_data.exam_page_examples(Path(folder) / "exams", "engineering")
        self.assertGreaterEqual(len(examples), 3)
        sources = " ".join(e["messages"][2]["content"] for e in examples)
        self.assertIn("https://gate2027.iitm.ac.in/", sources)
        self.assertIn("Not sure", sources)
        for example in examples:
            self.assertEqual([m["role"] for m in example["messages"]], ["system", "user", "assistant"])


if __name__ == "__main__":
    unittest.main()
