# Exam AI: a free, evidence-gated model for every exam family

Plan for the JEVX planner and the owner. The goal is an AI tutor that is free for every aspirant, hosted at no
cost, and that **never states an exam fact it cannot show a source for**: JEVX's evidence gate, applied to a
language model.

## What others offer (survey, 2026-09-27)

| Who | Model | License | What it means for us |
|---|---|---|---|
| Physics Wallah | Aryabhata 1.0, a 7B maths model for JEE, on Hugging Face (`PhysicsWallahAI/Aryabhata-1.0`); reports 86–90% on JEE Main 2025 maths | CC BY-NC 4.0 | Good for non-commercial use with credit. Do not build the core on it: NC blocks any later commercial use by the owner |
| Tech Mahindra with NVIDIA | Hindi-first education LLM, 8B (Project Indus, 2026) | check before use | Watch; Hindi explanations |
| Sarvam AI | Sarvam 30B and 105B (MoE), 22 Indian languages, on Hugging Face | Apache 2.0 | Commercial use allowed. Too large for free hosting, but fine as a teacher model for generating and checking training data |
| AI4Bharat (IIT Madras) | IndicTrans2 translation, 22 scheduled languages | MIT (models) | Hindi and regional versions of this list (`T-125`) |
| AI-tutor startups (SuperKalam, Lytmus, YoLearn, Sortmyprep, ProLearn) | Closed products on top of general models | closed | Their value is grounding and feedback, which we give free and open |

## Principles

1. **Facts come from retrieval, not from weights.** Notifications change every cycle, so exam facts (dates,
   patterns, fees, eligibility) are always retrieved from this list's pages, with their evidence status and
   official links. Fine-tuning teaches format, reasoning and the rules, never the facts.
2. **Evidence gate on every answer.** Every factual sentence must cite a retrieved page section. A small verifier
   (code, like `scripts/evidence_gate.py`) checks that each citation exists in what was retrieved and that quoted
   numbers appear in it. Anything that fails becomes "not sure: check the official notification", with the link.
3. **Free end to end.**
   - Hosting: static files on GitHub Pages and Hugging Face.
   - Inference: on the student's own device (browser or phone), so there is no server bill.
   - Training: free notebook GPUs.
4. **Clean data only:**
   - this list's own content (CC BY-SA);
   - original questions written by the hive;
   - datasets whose license allows it (checked one by one).

   Exam bodies' papers are for evaluation only, never redistributed. Coaching material is never used.
5. **One base model, small adapters per exam family,** instead of 118 separate models. The base is shared and
   each family's adapter is a small download.

## Phases

**Phase 0: "Ask the list", no training (`T-120`, `T-121`).**
- **Corpus:** the export gains `data/corpus.jsonl`: every page split by section, with its URL, evidence status and
  official links.
- **Tool:** a website tool that retrieves the best sections in the browser and answers with a small open model
  running in the browser (WebLLM on WebGPU, which ships enabled in current Chrome, Edge, Firefox and Safari),
  quoting and linking its sources.
- **Fallback:** when the student's device cannot run a model, the tool shows the retrieved sections with links.
  The answer is still useful and still honest.

**Phase 1: evaluation first (`T-122`).**
- **Question set:** 50 original questions per exam family, whose answers are verified against official sources.
- **Metrics:**
  - accuracy;
  - citation correctness;
  - the "not sure" rate on questions the list cannot answer, which should be high.

  Every model change must beat the last on this set before release.

**Phase 2: per-family adapters (`T-123`).**
- **Method:** LoRA or QLoRA fine-tuning on Kaggle's free GPUs (about 30 hours a week on T4 or P100).
- **Base:** a small open model under a permissive license. A 1.5B-parameter model fits a phone and a browser;
  a 7B model fits a laptop.
- **What it learns:** answering in the evidence-gated format, step-by-step solutions to original questions,
  explanations in Hindi (with IndicTrans2 for data), and refusing to invent facts.
- **License check:** confirm each base model's license in the task. Some sizes in the same family carry
  different licenses.

**Phase 3: publish free (`T-124`, owner login `H-006`).**
- **Hugging Face Hub:** model repos are free. We publish the adapters, merged weights, a GGUF build for Ollama,
  LM Studio and phone apps, and a WebLLM build for the browser.
- **Model card:** evaluations, limits, license and data sources.
- **Demo:** a Hugging Face Space on the free CPU tier, running the small GGUF, plus the in-browser tool on the
  website.
- **Alternatives if Hugging Face is down:**
  - GitHub Releases (files under 2 GB);
  - Kaggle Models;
  - the Ollama registry.

  ModelScope is also free, but it needs phone verification that is hard to get from India.

## What the owner provides (logins only)

- `H-006`: a Hugging Face account and a write token, saved as the repository secret `HF_TOKEN`. Also a Kaggle
  account for the free GPUs.

## How this fits the rest of the list

This is feature 59 in [feature-catalogue.md](feature-catalogue.md). It feeds chain 9 there: the evidence status
of every page becomes the AI's citations. It reuses the study tools, the offline copy and the open data, so the
AI works offline once it is downloaded.
