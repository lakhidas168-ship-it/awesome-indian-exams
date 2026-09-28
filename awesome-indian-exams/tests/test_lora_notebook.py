"""Checks the shipped notebook and license registry are real, not placeholders.

Every code cell must compile as Python, the notebook must actually call the gate before releasing, and the
license registry must record a license for every model and dataset it trains on.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lora_data  # noqa: E402
import lora_release_gate as gate  # noqa: E402

NOTEBOOK = ROOT / "notebooks" / "lora" / "exam-ai-lora.ipynb"
REGISTRY_PATH = ROOT / "notebooks" / "lora" / "licenses.json"
README = ROOT / "notebooks" / "lora" / "README.md"


def notebook_code() -> str:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return "\n".join("".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code")


def notebook_text() -> str:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return "\n".join("".join(cell["source"]) for cell in notebook["cells"])


class Notebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cls.code = notebook_code()
        cls.text = notebook_text()

    def test_valid_nbformat_with_code_cells(self) -> None:
        self.assertEqual(self.notebook["nbformat"], 4)
        code_cells = [c for c in self.notebook["cells"] if c["cell_type"] == "code"]
        markdown_cells = [c for c in self.notebook["cells"] if c["cell_type"] == "markdown"]
        self.assertGreaterEqual(len(code_cells), 6)
        self.assertGreaterEqual(len(markdown_cells), 2)

    def test_every_code_cell_compiles(self) -> None:
        for index, cell in enumerate(self.notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            with self.subTest(cell=index):
                compile(source, f"cell-{index}", "exec")

    def test_trains_and_evaluates_with_the_repo_tooling(self) -> None:
        for marker in ("lora_data.load_questions", "lora_data.split_train_eval",
                       "lora_data.build_all_family_examples", "get_peft_model", "LoraConfig",
                       "PeftModel", "gate.registry_problems", "gate.results_problems",
                       "gate.release_allowed", "gate.render_model_card", "SystemExit"):
            self.assertIn(marker, self.code)

    def test_refuses_to_release_when_the_gate_fails(self) -> None:
        self.assertIn("release blocked", self.code)
        self.assertIn("shutil.copytree", self.code)
        blocked = self.code.index("release blocked")
        released = self.code.index("shutil.copytree")
        self.assertLess(blocked, released, "the release copy must come after the blocked check")

    def test_records_licenses_in_the_notebook_itself(self) -> None:
        for marker in ("Qwen/Qwen2.5-1.5B-Instruct", "HuggingFaceTB/SmolLM2-1.7B-Instruct",
                       "PhysicsWallahAI/Aryabhata-1.0", "ultrachat_200k", "Apache-2.0", "CC BY-NC 4.0",
                       "CC BY-SA 4.0", "MIT", "licenses.json", "T-122", "2026-09-28"):
            self.assertIn(marker, self.text)

    def test_eval_files_are_the_held_out_set(self) -> None:
        questions = lora_data.load_questions(ROOT / "questions")
        train, held_out = lora_data.split_train_eval(questions)
        self.assertEqual(len(held_out), 50)
        self.assertTrue(all(not lora_data.is_eval_question(qid) for qid in train))


class Registry(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_passes_the_shipped_gate(self) -> None:
        self.assertEqual(gate.registry_problems(self.registry), [])

    def test_every_used_entry_records_license_source_and_date(self) -> None:
        entries = [m for m in self.registry["base_models"] if m.get("used")] + \
                  [d for d in self.registry["datasets"] if d.get("used")]
        self.assertGreaterEqual(len(entries), 3)
        for entry in entries:
            for key in ("license", "license_url", "source_url", "verified"):
                self.assertTrue(entry.get(key), f"{entry.get('id')}: {key} missing")

    def test_only_one_used_base_model(self) -> None:
        self.assertEqual(sum(1 for m in self.registry["base_models"] if m.get("used")), 1)

    def test_question_dataset_keeps_eval_files_held_out(self) -> None:
        question_datasets = [d for d in self.registry["datasets"] if "questions/" in d.get("paths", [])]
        self.assertTrue(question_datasets)
        self.assertIn("never trained on", question_datasets[0].get("note", ""))

    def test_readme_records_the_release_rule_and_licenses(self) -> None:
        text = README.read_text(encoding="utf-8")
        for marker in ("T-122", "beats the base model", "Apache-2.0", "CC BY-NC 4.0", "CC BY-SA 4.0", "MIT"):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
