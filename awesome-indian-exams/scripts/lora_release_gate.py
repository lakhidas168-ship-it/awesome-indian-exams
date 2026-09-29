#!/usr/bin/env python3
"""Release gate for the exam-AI LoRA adapters (`notebooks/lora/`).

Two checks, both offline and stdlib-only:

1. **Licenses** (`registry_problems`): every base model and every dataset the notebook trains on must record its
   license, the URL it was verified against and the date. Training on a non-commercial or share-alike base model,
   or on any entry with no license, blocks everything.
2. **Evaluation** (`results_problems`): a family adapter may only be marked `released` when it *beats* the base
   model on the held-out T-122 questions, and the recorded scores must be recomputable from the predictions and
   the answer key, so a hand-written results file cannot claim a win.

    python3 scripts/lora_release_gate.py --registry notebooks/lora/licenses.json
    python3 scripts/lora_release_gate.py --registry notebooks/lora/licenses.json --results results.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lora_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "awesome-indian-exams/lora-licenses/1"
RESULTS_SCHEMA = "awesome-indian-exams/lora-eval/1"

# A base model must be permissive enough for the adapter and its weights to stay free to use and share.
MODEL_LICENSES = ("apache-2.0", "mit", "bsd-2-clause", "bsd-3-clause", "cc0-1.0", "unlicense", "isc")
# Training data may additionally be attribution/share-alike, plus this list's own content (CC BY-NC-SA 4.0 since
# 29 Sep 2026); adapters trained on it are released under CC BY-NC-SA 4.0 too: free for study, no commercial use.
DATA_LICENSES = MODEL_LICENSES + ("cc-by-4.0", "cc-by-sa-4.0", "cc-by-sa-3.0",
                                  "odc-by-1.0", "odc-odbl-1.0", "gfdl-1.3", "cc-by-nc-sa-4.0")
# Rejected candidates still record a real license name, so a typo can never pass as "not used".
KNOWN_LICENSES = DATA_LICENSES + ("cc-by-nc-4.0", "cc-by-nc-sa-4.0", "cc-by-nc-nd-4.0", "cc-by-nd-4.0",
                                  "gemma", "llama3.1", "llama3.2", "proprietary", "unknown")
SUMMARY_KEYS = ("total", "correct", "accuracy", "unparsed", "probe_total", "probe_correct", "probe_accuracy")


def parse_day(value: object) -> dt.date | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _entry_problems(entry: object, where: str, allowed: tuple[str, ...], today: dt.date) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{where}: must be an object"]
    problems: list[str] = []
    if not entry.get("id"):
        problems.append(f"{where}: 'id' missing")
    used = entry.get("used")
    if used not in (True, False):
        problems.append(f"{where}: 'used' must be true or false")
    for key in ("license", "license_url", "source_url", "verified"):
        if not entry.get(key):
            problems.append(f"{where}: '{key}' missing")
    checked = parse_day(entry.get("verified"))
    if entry.get("verified") and checked is None:
        problems.append(f"{where}: 'verified' must be YYYY-MM-DD")
    elif checked and checked > today:
        problems.append(f"{where}: 'verified' {checked} is in the future")
    license_name = str(entry.get("license", "")).strip().lower()
    if used is True:
        if license_name not in allowed:
            problems.append(f"{where}: training on license '{license_name or '(none)'}' is not allowed "
                            f"(allowed: {', '.join(allowed)})")
    else:
        if license_name and license_name not in KNOWN_LICENSES:
            problems.append(f"{where}: unknown license '{license_name}' (record a real one even when unused)")
        if not entry.get("reason"):
            problems.append(f"{where}: an unused entry needs a 'reason' saying why it is not used")
    return problems


def registry_problems(reg: object, today: dt.date | None = None) -> list[str]:
    """Every problem that stops training/release, from `notebooks/lora/licenses.json`."""
    today = today or dt.date.today()
    if not isinstance(reg, dict):
        return ["licenses.json: must hold a JSON object"]
    problems: list[str] = []
    if reg.get("schema") != SCHEMA:
        problems.append(f"licenses.json: schema must be '{SCHEMA}'")
    checked_at = parse_day(reg.get("checked_at"))
    if checked_at is None:
        problems.append("licenses.json: 'checked_at' must be YYYY-MM-DD")
    elif checked_at > today:
        problems.append(f"licenses.json: 'checked_at' {checked_at} is in the future")
    output = reg.get("output_license")
    if not isinstance(output, dict) or not output.get("name") or not output.get("url"):
        problems.append("licenses.json: 'output_license' needs a name and a url")
    models = reg.get("base_models")
    if not isinstance(models, list) or not models:
        problems.append("licenses.json: 'base_models' must be a non-empty list")
        models = []
    datasets = reg.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        problems.append("licenses.json: 'datasets' must be a non-empty list")
        datasets = []
    used_models = []
    for index, model in enumerate(models):
        entry_problems = _entry_problems(model, f"base_models[{index}]", MODEL_LICENSES, today)
        problems += entry_problems
        if isinstance(model, dict) and model.get("used") is True and not entry_problems:
            used_models.append(model.get("id"))
    if len(used_models) != 1:
        problems.append(f"base_models: exactly one model must be marked used (found {len(used_models)})")
    used_datasets = [d for d in datasets if isinstance(d, dict) and d.get("used") is True]
    if not used_datasets:
        problems.append("datasets: at least one dataset must be marked used")
    for index, dataset in enumerate(datasets):
        problems += _entry_problems(dataset, f"datasets[{index}]", DATA_LICENSES, today)
    return problems


def used_base_model(reg: dict) -> str:
    return next(m["id"] for m in reg.get("base_models", []) if m.get("used") is True)


def _predictions_problems(predictions: object, expected_ids: set[str], questions: dict, where: str) -> list[str]:
    problems: list[str] = []
    if not isinstance(predictions, dict):
        return [f"{where}: 'predictions' must be an object of question id -> option index"]
    missing = sorted(expected_ids - set(predictions))
    extra = sorted(set(predictions) - expected_ids)
    if missing:
        problems.append(f"{where}: {len(missing)} evaluation questions have no prediction, e.g. {missing[0]}")
    if extra:
        problems.append(f"{where}: predictions for unknown questions, e.g. {extra[0]}")
    for qid in sorted(expected_ids & set(predictions)):
        value = predictions[qid]
        if value is None:
            continue
        options = questions[qid].get("options") or []
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < len(options):
            problems.append(f"{where}: prediction for {qid} must be an option index or null, got {value!r}")
    return problems


def _block_problems(block: object, expected_ids: set[str], questions: dict, where: str) -> tuple[list[str], int | None]:
    """Recompute a base/adapter summary from its predictions; return problems and the win count."""
    if not isinstance(block, dict):
        return [f"{where}: must be an object"], None
    problems = _predictions_problems(block.get("predictions"), expected_ids, questions, where)
    summary = lora_data.summarise({qid: questions[qid] for qid in expected_ids}, block.get("predictions") or {})
    for key in SUMMARY_KEYS:
        if key not in block:
            problems.append(f"{where}: '{key}' missing")
        elif block[key] != summary[key]:
            problems.append(f"{where}: '{key}' is {block[key]!r} but the predictions recompute to {summary[key]!r}")
    return problems, summary["correct"]


def results_problems(results: object, questions: dict[str, dict], registry: dict | None = None,
                     today: dt.date | None = None) -> list[str]:
    """Every problem in a notebook results file, with the scores recomputed from the predictions."""
    today = today or dt.date.today()
    if not isinstance(results, dict):
        return ["results: must hold a JSON object"]
    problems: list[str] = []
    if results.get("schema") != RESULTS_SCHEMA:
        problems.append(f"results: schema must be '{RESULTS_SCHEMA}'")
    if not results.get("base_model"):
        problems.append("results: 'base_model' missing")
    elif registry is not None and results["base_model"] != used_base_model(registry):
        problems.append(f"results: base_model '{results['base_model']}' is not the used model in licenses.json")
    created = parse_day(str(results.get("created", ""))[:10])
    if not created:
        problems.append("results: 'created' must start with YYYY-MM-DD")
    elif created > today:
        problems.append(f"results: 'created' {created} is in the future")
    expected_ids = set(questions)
    if not expected_ids:
        problems.append("results: no evaluation questions were given to the gate")
        return problems
    base_problems, base_correct = _block_problems(results.get("base"), expected_ids, questions, "base")
    problems += base_problems
    adapters = results.get("adapters")
    if not isinstance(adapters, dict) or not adapters:
        problems.append("results: 'adapters' must be a non-empty object keyed by exam family")
        adapters = {}
    release = results.get("release")
    if not isinstance(release, dict):
        problems.append("results: 'release' block missing")
        release = {}
    primary = release.get("primary")
    if primary not in adapters:
        problems.append(f"results: release.primary '{primary}' is not one of the evaluated adapters")
    primary_correct = None
    for family, block in sorted(adapters.items()):
        block_problems, correct = _block_problems(block, expected_ids, questions, f"adapters.{family}")
        problems += block_problems
        released = block.get("released") if isinstance(block, dict) else None
        if released not in (True, False):
            problems.append(f"adapters.{family}: 'released' must be true or false")
            continue
        beats = (correct is not None and base_correct is not None and correct > base_correct)
        if released and not beats:
            problems.append(f"adapters.{family}: marked released but it does not beat the base model "
                            f"({correct} vs {base_correct} correct)")
        if not released and not block.get("reason"):
            problems.append(f"adapters.{family}: a held-back adapter needs a 'reason'")
        if family == primary:
            primary_correct = correct
            if beats and released is not True:
                problems.append(f"adapters.{primary}: beats the base model but is not marked released")
    expected_allowed = (primary_correct is not None and base_correct is not None
                        and primary_correct > base_correct)
    if release.get("allowed") is not expected_allowed:
        problems.append(f"results: release.allowed is {release.get('allowed')!r} but the T-122 scores say "
                        f"{expected_allowed!r}")
    return problems


def release_allowed(results: dict, questions: dict[str, dict]) -> tuple[bool, list[str]]:
    problems = results_problems(results, questions)
    allowed = not problems and bool(results.get("release", {}).get("allowed"))
    return allowed, problems


def render_model_card(reg: dict, results: dict, family: str) -> str:
    """The model-card section T-124 publishes: license, data sources, evaluation, evidence-gate behaviour."""
    base = next(m for m in reg.get("base_models", []) if m.get("used") is True)
    datasets = [d for d in reg.get("datasets", []) if d.get("used") is True]
    adapter = results.get("adapters", {}).get(family, {})
    lines = [
        f"# Awesome Indian Exams AI - {family} adapter",
        "",
        f"Base model: `{base['id']}` ({base['license']}) - license verified {base['verified']} at {base['license_url']}.",
        f"Adapter license: {reg['output_license']['name']} ({reg['output_license']['url']}).",
        "",
        "## Data sources (each with its license)",
        "",
        "| Dataset | License | Source |",
        "|---|---|---|",
    ]
    for dataset in datasets:
        lines.append(f"| {dataset['id']} | {dataset['license']} | {dataset['source_url']} |")
    lines += [
        "",
        "## Evaluation - held-out T-122 questions",
        "",
        "| Model | Correct | Total | Accuracy | Not-sure probes |",
        "|---|---:|---:|---:|---:|",
        f"| Base ({base['id']}) | {results['base']['correct']} | {results['base']['total']} | "
        f"{results['base']['accuracy']:.2f} | {results['base']['probe_correct']}/{results['base']['probe_total']} |",
        f"| {family} adapter | {adapter.get('correct')} | {adapter.get('total')} | "
        f"{adapter.get('accuracy', 0):.2f} | {adapter.get('probe_correct')}/{adapter.get('probe_total')} |",
        "",
        f"Release: {'allowed' if results['release']['allowed'] else 'blocked'} - "
        f"{results['release'].get('reason', '')}",
        "",
        "## Evidence-gate behaviour",
        "",
        "The adapter is trained to answer in the list's evidence-gated format: answer, reason, source URL. When a",
        "fact is not in the list (exact dates, cutoffs, vacancies) it answers 'Not sure - check the official",
        "notification' with the official link instead of guessing, and the website's citation verifier checks every",
        "cited section before an answer is shown.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", type=Path, default=ROOT / "notebooks" / "lora" / "licenses.json")
    ap.add_argument("--results", type=Path)
    ap.add_argument("--questions", type=Path, default=ROOT / "questions")
    ap.add_argument("--family", help="family for --card (default: release.primary)")
    ap.add_argument("--card", type=Path, help="write the model card here when the gate passes")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today(), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    problems: list[str] = []
    reg = json.loads(args.registry.read_text(encoding="utf-8")) if args.registry.exists() else None
    if reg is None:
        problems.append(f"{args.registry}: missing")
    else:
        problems += registry_problems(reg, args.today)
    if args.results:
        results = json.loads(args.results.read_text(encoding="utf-8")) if args.results.exists() else None
        if results is None:
            problems.append(f"{args.results}: missing")
        else:
            if reg is not None:
                used = reg.get("base_models") or []
                if not any(isinstance(m, dict) and m.get("used") is True for m in used):
                    problems.append("licenses.json: no used base model, refusing to check results")
            all_questions = lora_data.load_questions(args.questions)
            _, held_out = lora_data.split_train_eval(all_questions)
            problems += results_problems(results, held_out, reg, args.today)
            if args.card and not problems:
                family = args.family or results.get("release", {}).get("primary", "")
                args.card.write_text(render_model_card(reg, results, family), encoding="utf-8")
                print(f"card written: {args.card}")
    for line in problems:
        print(f"ERROR   {line}")
    print(f"{'FAIL' if problems else 'PASS'}: lora release gate ({args.registry.name}), {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
