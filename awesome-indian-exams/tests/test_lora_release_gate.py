"""Self-tests for the LoRA release gate (`scripts/lora_release_gate.py`).

Each test proves a bad input is rejected: an unlicensed model or dataset, a non-commercial base, or an adapter
that does not beat the base model on the held-out T-122 questions.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import lora_data  # noqa: E402
import lora_release_gate as gate  # noqa: E402

TODAY = dt.date(2026, 9, 28)
REGISTRY = json.loads((ROOT / "notebooks" / "lora" / "licenses.json").read_text(encoding="utf-8"))


def good_results(questions: dict) -> dict:
    base = {qid: None for qid in questions}
    adapter = {qid: lora_data.answer_index(q) for qid, q in questions.items()}
    return {
        "schema": gate.RESULTS_SCHEMA,
        "base_model": gate.used_base_model(REGISTRY),
        "eval_set": "questions/*-eval-*.json",
        "created": "2026-09-28T00:00:00Z",
        "base": {"predictions": base, **lora_data.summarise(questions, base)},
        "adapters": {
            "engineering": {"predictions": adapter, **lora_data.summarise(questions, adapter),
                            "released": True, "reason": ""},
        },
        "release": {"allowed": True, "primary": "engineering", "reason": "engineering beats base"},
    }


class Registry(unittest.TestCase):
    def problems(self, mutate) -> list[str]:
        registry = copy.deepcopy(REGISTRY)
        mutate(registry)
        return gate.registry_problems(registry, TODAY)

    def test_shipped_registry_passes(self) -> None:
        self.assertEqual(gate.registry_problems(REGISTRY, TODAY), [])

    def test_used_base_model_license_required(self) -> None:
        problems = self.problems(lambda r: r["base_models"][0].pop("license"))
        self.assertTrue(any("license" in p for p in problems))

    def test_non_commercial_base_model_rejected(self) -> None:
        def mutate(registry):
            registry["base_models"][0]["license"] = "cc-by-nc-4.0"
        self.assertTrue(any("not allowed" in p for p in self.problems(mutate)))

    def test_share_alike_base_model_rejected(self) -> None:
        def mutate(registry):
            registry["base_models"][1]["used"] = True
            registry["base_models"][1]["license"] = "cc-by-sa-4.0"
            registry["base_models"][0]["used"] = False
            registry["base_models"][0]["reason"] = "other"
        problems = self.problems(mutate)
        self.assertTrue(any("not allowed" in p for p in problems))

    def test_two_used_base_models_rejected(self) -> None:
        def mutate(registry):
            registry["base_models"][1]["used"] = True
            registry["base_models"][1]["reason"] = ""
        self.assertTrue(any("exactly one model" in p for p in self.problems(mutate)))

    def test_unused_entry_needs_a_reason(self) -> None:
        def mutate(registry):
            registry["base_models"][1]["reason"] = ""
        self.assertTrue(any("reason" in p for p in self.problems(mutate)))

    def test_unused_entry_license_typo_rejected(self) -> None:
        def mutate(registry):
            registry["base_models"][1]["license"] = "apache2"
        self.assertTrue(any("unknown license" in p for p in self.problems(mutate)))

    def test_used_dataset_missing_source_url_rejected(self) -> None:
        def mutate(registry):
            registry["datasets"][0].pop("source_url")
        self.assertTrue(any("source_url" in p for p in self.problems(mutate)))

    def test_no_used_dataset_rejected(self) -> None:
        def mutate(registry):
            for dataset in registry["datasets"]:
                dataset["used"] = False
                dataset["reason"] = "not used"
        self.assertTrue(any("at least one dataset" in p for p in self.problems(mutate)))

    def test_future_verified_date_rejected(self) -> None:
        def mutate(registry):
            registry["datasets"][0]["verified"] = "2027-01-01"
        self.assertTrue(any("future" in p for p in self.problems(mutate)))

    def test_bad_schema_rejected(self) -> None:
        def mutate(registry):
            registry["schema"] = "something-else"
        self.assertTrue(any("schema" in p for p in self.problems(mutate)))

    def test_missing_checked_at_rejected(self) -> None:
        def mutate(registry):
            registry.pop("checked_at")
        self.assertTrue(any("checked_at" in p for p in self.problems(mutate)))


class Results(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.questions = lora_data.split_train_eval(lora_data.load_questions(ROOT / "questions"))[1]

    def problems(self, mutate, registry=None) -> list[str]:
        results = good_results(self.questions)
        mutate(results)
        return gate.results_problems(results, self.questions, registry, TODAY)

    def test_good_results_pass(self) -> None:
        self.assertEqual(self.problems(lambda r: None, REGISTRY), [])

    def test_adapter_tie_rejected(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["predictions"] = dict(results["base"]["predictions"])
            summary = lora_data.summarise(self.questions, results["adapters"]["engineering"]["predictions"])
            results["adapters"]["engineering"].update(summary)
        problems = self.problems(mutate)
        self.assertTrue(any("does not beat" in p for p in problems))

    def test_adapter_worse_than_base_rejected(self) -> None:
        def mutate(results):
            base = {qid: lora_data.answer_index(q) for qid, q in self.questions.items()}
            results["base"] = {"predictions": base, **lora_data.summarise(self.questions, base)}
            results["adapters"]["engineering"] = {"predictions": {qid: None for qid in self.questions},
                                                  **lora_data.summarise(self.questions, {}),
                                                  "released": True, "reason": ""}
            results["release"] = {"allowed": True, "primary": "engineering", "reason": "lie"}
        problems = self.problems(mutate)
        self.assertTrue(any("does not beat" in p for p in problems))
        self.assertTrue(any("release.allowed" in p for p in problems))

    def test_missing_prediction_rejected(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["predictions"].pop("ee-eval-01")
        self.assertTrue(any("no prediction" in p for p in self.problems(mutate)))

    def test_unknown_prediction_rejected(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["predictions"]["ee-eval-99"] = 0
        self.assertTrue(any("unknown questions" in p for p in self.problems(mutate)))

    def test_hand_written_score_rejected(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["correct"] = 49
            results["adapters"]["engineering"]["accuracy"] = 0.98
        problems = self.problems(mutate)
        self.assertTrue(any("recompute" in p for p in problems))

    def test_out_of_range_prediction_rejected(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["predictions"]["ee-eval-01"] = 99
        self.assertTrue(any("option index" in p for p in self.problems(mutate)))

    def test_primary_beating_everything_but_held_back_rejected(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["released"] = False
            results["release"]["allowed"] = False
            results["release"]["reason"] = "held back"
        problems = self.problems(mutate)
        self.assertTrue(any("not marked released" in p for p in problems))

    def test_held_back_adapter_needs_reason(self) -> None:
        def mutate(results):
            results["adapters"]["engineering"]["released"] = False
            results["adapters"]["engineering"]["reason"] = ""
            results["release"]["allowed"] = False
            results["release"]["reason"] = "held back"
        problems = self.problems(mutate)
        self.assertTrue(any("reason" in p for p in problems))

    def test_primary_must_be_evaluated(self) -> None:
        def mutate(results):
            results["release"]["primary"] = "medical"
        self.assertTrue(any("release.primary" in p for p in self.problems(mutate)))

    def test_base_model_must_match_registry(self) -> None:
        def mutate(results):
            results["base_model"] = "someone/other-model"
        self.assertTrue(any("base_model" in p for p in self.problems(mutate, REGISTRY)))

    def test_future_created_date_rejected(self) -> None:
        def mutate(results):
            results["created"] = "2027-01-01T00:00:00Z"
        self.assertTrue(any("future" in p for p in self.problems(mutate)))

    def test_release_allowed_reports_block(self) -> None:
        results = good_results(self.questions)
        results["release"]["allowed"] = False
        allowed, reasons = gate.release_allowed(results, self.questions)
        self.assertFalse(allowed)
        self.assertTrue(any("release.allowed" in r for r in reasons))

    def test_release_allowed_reports_pass(self) -> None:
        allowed, reasons = gate.release_allowed(good_results(self.questions), self.questions)
        self.assertTrue(allowed)
        self.assertEqual(reasons, [])


class ModelCard(unittest.TestCase):
    def test_card_records_licenses_and_scores(self) -> None:
        questions = lora_data.split_train_eval(lora_data.load_questions(ROOT / "questions"))[1]
        card = gate.render_model_card(REGISTRY, good_results(questions), "engineering")
        self.assertIn("Qwen/Qwen2.5-1.5B-Instruct", card)
        self.assertIn("apache-2.0", card)
        self.assertIn("cc-by-sa-4.0", card)
        self.assertIn("mit", card)
        self.assertIn("CC BY-SA 4.0", card)
        self.assertIn("not sure", card.lower())


if __name__ == "__main__":
    unittest.main()
