# Original practice questions

Short, worked practice questions written from scratch for this list. They are **not** previous-year questions
and not copied from any coaching material, book or lecture. Each file states its author, so the source is clear.

## Format

One question per file: `questions/<id>.json`, where the file name equals the `id`. The gate
(`python3 scripts/validate.py`) rejects a question that is missing its `answer`, `solution` or `author`, that
has no `options`, whose `answer` is not one of the options, that points at an exam id not in
[the registry](../registry/exams.toml), or that lies about its `source`.

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Unique id; must equal the file name (lowercase-hyphenated). |
| `exams` | list of strings | Registry exam ids the question is useful for, e.g. `gate-ee`. |
| `subject` | string | Subject, e.g. `Electric Circuits`. |
| `question` | string | The question text. |
| `options` | list of strings | At least two options. |
| `answer` | string | One of the options, or its single letter (`A`, `B`, ...). |
| `solution` | string | Short worked solution with the formula used. |
| `author` | string | Who wrote it. Required, so credit is always clear. |
| `license` | string | `CC BY-SA 4.0` (matches the rest of the written content). |
| `source` | string | Must be `original`. Copied questions are refused. |
| `source_url` | string | Official URL the answer was checked against (T-122 eval sets). Optional for older files, required for `*-eval-*`. |

## Evaluation sets (T-122)

Files named `<family>-eval-<NN>.json` (for example `ee-eval-01.json`) form the per-exam-family AI
evaluation sets: 50 original questions per family. Each set mixes three kinds:

1. **Technical questions** whose answers follow from a worked computation; the `source_url` is the
   official syllabus or notice that lists the topic.
2. **Exam-fact questions** whose answers are stated verbatim in the official document at `source_url`.
3. **Not-sure probes**: questions the list cannot answer (exact session dates, cutoffs, vacancy
   counts). Their `answer` is the "Not sure" option and the `solution` explains what is missing and
   links the official page to check. A model that guesses on these fails the item.

Every `solution` ends with `Source checked: <URL>` naming the exact URL fetched. No question is
copied from an exam paper or coaching material.

## Example

```json
{
  "id": "ee-circuits-voltage-divider-01",
  "exams": ["gate-ee", "upsc-ese-ee", "ssc-je-ee"],
  "subject": "Electric Circuits",
  "question": "Two resistors of 4 ohm and 6 ohm are in series across 20 V DC. What is the voltage across the 6 ohm resistor?",
  "options": ["6 V", "8 V", "10 V", "12 V"],
  "answer": "12 V",
  "solution": "Series R = 10 ohm, I = 2 A, V = 2 x 6 = 12 V.",
  "author": "Rajon Das",
  "license": "CC BY-SA 4.0",
  "source": "original"
}
```
