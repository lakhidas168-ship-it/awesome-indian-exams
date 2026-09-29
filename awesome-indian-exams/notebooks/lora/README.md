# Exam AI: LoRA fine-tuning on Kaggle's free GPUs

One permissively licensed small base model, one QLoRA adapter per exam family, trained only on material this
project has the right to use. This is phase 2 of `ops/plan/exam-llm.md` (task
[T-123](https://github.com/lakhidas168-ship-it/awesome-indian-exams/blob/main/awesome-indian-exams/ops/tasks.toml));
phase 3 (`T-124`) publishes the winning adapter by hand.

| File | What it is |
|---|---|
| [`exam-ai-lora.ipynb`](exam-ai-lora.ipynb) | The Kaggle notebook: license check, data build, training, evaluation, release gate. |
| [`licenses.json`](licenses.json) | Every base model and dataset with its license, the URL verified against, and the date. |

## Run it (free)

1. Kaggle -> New Notebook -> File -> Import Notebook -> upload `exam-ai-lora.ipynb`.
2. Accelerator: **GPU T4 x2** (or P100). Internet: **on**. ~45–90 minutes of the ~30 free GPU hours a week.
3. Attach this repository as a Kaggle dataset (upload the folder whole) or let the notebook clone the public
   GitHub repository. No API keys, no paid calls.

## The release rule (enforced, not promised)

- The `*-eval-*` files (`questions/ee-eval-*.json`, 50 questions, `T-122`) are **held out**: the notebook scores
  the base model and each adapter on them and never trains on them (`scripts/lora_data.py:split_train_eval`).
- An adapter is copied to `/kaggle/working/release/<family>/` **only if it beats the base model** on those
  questions; otherwise the notebook raises after writing `results.json` and releases nothing.
- `scripts/lora_release_gate.py` recomputes every recorded score from the predictions and the answer key, so a
  hand-edited results file cannot claim a win. Run it locally:

      python3 scripts/lora_release_gate.py --registry notebooks/lora/licenses.json --results results.json

- A family without a T-122 evaluation slice gets no release (its adapter stays a candidate). Exact dates,
  cutoffs and vacancy counts are never learned as facts: the format taught is
  "Not sure - check the official notification" with the official link.

## Licenses (verified 2026-09-28 against the pages linked in `licenses.json`)

| Used | Model / dataset | License |
|---|---|---|
| base | `Qwen/Qwen2.5-1.5B-Instruct` | Apache-2.0 |
| alternative | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | Apache-2.0 |
| rejected | `PhysicsWallahAI/Aryabhata-1.0` | CC BY-NC 4.0 (blocks commercial use) |
| data | this list's pages, modules, formula sheets | CC BY-SA 4.0 |
| data | this list's original questions | CC BY-SA 4.0 |
| replay | `HuggingFaceH4/ultrachat_200k` (capped sample) | MIT |

The adapters are released under CC BY-SA 4.0, matching the content they learn from; attribution
"Awesome Indian Exams by Rajon Das and contributors".

## Outputs

`/kaggle/working/results.json` (scores, per-question predictions), `/kaggle/working/adapters/<family>/`
(candidates), `/kaggle/working/release/<family>/` (adapter + `MODEL_CARD.md`, only when the gate passes).
