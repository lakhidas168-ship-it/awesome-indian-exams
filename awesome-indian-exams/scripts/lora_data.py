#!/usr/bin/env python3
"""Data preparation for the exam-AI LoRA notebook (`notebooks/lora/exam-ai-lora.ipynb`).

Stdlib only, CPU only, so every rule the notebook depends on can be unit-tested here. The notebook imports this
module from the cloned repository; the training loop itself (torch) stays in the notebook.

The one invariant worth repeating: files named `*-eval-*` (the T-122 evaluation sets) are held out for scoring
and are never built into training examples. `split_train_eval` is the only place that decides this.
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate import parse_frontmatter, section  # noqa: E402

EVAL_SUFFIX_RE = re.compile(r"-eval-\d+$")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

SYSTEM_PROMPT = (
    "You are the Awesome Indian Exams tutor. Answer only from the list's own pages and questions. "
    "Always end with the source URL you checked. If a fact is not in the list, answer "
    "'Not sure - check the official notification' with the official link instead of guessing."
)


def load_questions(directory: Path | str) -> dict[str, dict]:
    """Every `questions/*.json` object, keyed by id. Raises ValueError on a malformed file."""
    out: dict[str, dict] = {}
    for path in sorted(Path(directory).glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSON: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("id"), str):
            raise ValueError(f"{path}: a question file must be a JSON object with an 'id'")
        if data["id"] in out:
            raise ValueError(f"{path}: duplicate question id '{data['id']}'")
        out[data["id"]] = data
    return out


def is_eval_question(question_id: str) -> bool:
    return bool(EVAL_SUFFIX_RE.search(question_id))


def split_train_eval(questions: dict[str, dict]) -> tuple[dict[str, dict], dict[str, dict]]:
    """Hold out every `*-eval-*` file. Training never sees these ids."""
    train, held_out = {}, {}
    for qid, question in questions.items():
        (held_out if is_eval_question(qid) else train)[qid] = question
    return train, held_out


def load_exam_families(registry_path: Path | str) -> dict[str, str]:
    data = tomllib.loads(Path(registry_path).read_text(encoding="utf-8"))
    return {exam["id"]: exam["family"] for exam in data.get("exam", [])}


def question_families(question: dict, exam_family: dict[str, str]) -> list[str]:
    return sorted({exam_family[e] for e in question.get("exams", []) if e in exam_family})


def answer_index(question: dict) -> int | None:
    """The index of the correct option, for a verbatim option or a single letter."""
    options = question.get("options") or []
    answer = question.get("answer") or ""
    if answer in options:
        return options.index(answer)
    if len(answer) == 1 and answer.upper() in LETTERS[: len(options)]:
        return LETTERS.index(answer.upper())
    return None


def score_prediction(text: str, options: list[str]) -> int | None:
    """Read an option index out of a model answer. `ANSWER: C` first, then the option text."""
    if not isinstance(text, str) or not options:
        return None
    found = re.findall(r"ANSWER\s*[:=]\s*\(?([A-Za-z])\)?", text, flags=re.IGNORECASE)
    if found:
        letter = found[-1].upper()
        if letter in LETTERS[: len(options)]:
            return LETTERS.index(letter)
    lowered = text.lower()
    for index, option in sorted(enumerate(options), key=lambda pair: -len(pair[1])):
        option = option.strip()
        if option and option.lower() in lowered:
            return index
    return None


def summarise(questions: dict[str, dict], predictions: dict[str, int | None]) -> dict:
    """Score predictions against the answer key. A missing prediction counts as wrong."""
    total = correct = unparsed = 0
    probe_total = probe_correct = 0
    wrong: list[str] = []
    for qid, question in sorted(questions.items()):
        total += 1
        predicted = predictions.get(qid)
        if predicted is None:
            unparsed += 1
        ok = predicted is not None and predicted == answer_index(question)
        correct += int(ok)
        if str(question.get("answer", "")).lower().startswith("not sure"):
            probe_total += 1
            probe_correct += int(ok)
        if not ok:
            wrong.append(qid)
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total else 0.0,
        "unparsed": unparsed,
        "probe_total": probe_total,
        "probe_correct": probe_correct,
        "probe_accuracy": round(probe_correct / probe_total, 4) if probe_total else 0.0,
        "wrong": wrong,
    }


def chat(user: str, assistant: str) -> dict:
    return {"messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]}


def _one_line(text: str, limit: int = 700) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def exam_page_examples(exams_dir: Path | str, family: str) -> list[dict]:
    """Evidence-gated Q/A built from one family's exam pages (this list's own content)."""
    examples: list[dict] = []
    folder = Path(exams_dir) / family
    for page in sorted(folder.glob("*.md")):
        meta, body = parse_frontmatter(page.read_text(encoding="utf-8"))
        if not meta or not meta.get("title"):
            continue
        title = meta["title"]
        site = meta.get("official_site", "")
        verified = meta.get("verification", "unverified")
        facts = (f"{title} is conducted by {meta.get('conducting_body', '')}. Official website: {site}. "
                 f"The page covers cycle {meta.get('cycle', '')} and its evidence status is '{verified}' "
                 f"(last checked {meta.get('last_verified', '')}). Source: {site}")
        examples.append(chat(f"Who conducts {title}, and what is the official website?", facts))
        pattern = section(body, "## Exam pattern")
        if pattern:
            examples.append(chat(f"What exam pattern does the list record for {title}?",
                                 f"{_one_line(pattern)} Source: {site}"))
        syllabus = section(body, "## Syllabus")
        if syllabus:
            examples.append(chat(f"What syllabus does the list record for {title}?",
                                 f"{_one_line(syllabus)} Source: {site}"))
        examples.append(chat(f"Tell me the exact dates for {title}.",
                             f"Not sure - this list does not track the exact dates for {title}. "
                             f"Check the official notification at {site}."))
    return examples


def practice_examples(questions: dict[str, dict]) -> list[dict]:
    """The list's original questions, answered in the evidence-gated format."""
    examples: list[dict] = []
    for qid in sorted(questions):
        question = questions[qid]
        options = question.get("options") or []
        letters = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(options))
        index = answer_index(question)
        letter = LETTERS[index] if index is not None else "?"
        source = question.get("source_url") or "the official notification"
        examples.append(chat(
            f"Question: {question.get('question', '')}\nOptions:\n{letters}\nAnswer with the letter of one option.",
            f"ANSWER: {letter}\nREASON: {question.get('solution', '')}\nSOURCE: {source}"))
    return examples


def build_family_examples(root: Path | str, family: str, train_questions: dict[str, dict],
                          exam_family: dict[str, str]) -> list[dict]:
    """All training examples for one exam family, de-duplicated, eval sets excluded by construction."""
    root = Path(root)
    examples = exam_page_examples(root / "exams", family)
    examples += [ex for qid, q in sorted(train_questions.items())
                 if family in question_families(q, exam_family)
                 for ex in practice_examples({qid: q})]
    seen: set[str] = set()
    unique: list[dict] = []
    for example in examples:
        key = example["messages"][1]["content"]
        if key not in seen:
            seen.add(key)
            unique.append(example)
    return unique


def build_all_family_examples(root: Path | str, train_questions: dict[str, dict],
                              exam_family: dict[str, str]) -> dict[str, list[dict]]:
    families = sorted(set(exam_family.values()))
    return {family: build_family_examples(root, family, train_questions, exam_family)
            for family in families}
