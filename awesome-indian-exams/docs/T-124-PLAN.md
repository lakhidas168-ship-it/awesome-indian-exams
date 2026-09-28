# T-124: Publish Exam AI to Hugging Face

This task involves setting up a manual workflow to publish the Exam AI model to the Hugging Face Hub.

## Plan

1. Create a GitHub Actions workflow file `.github/workflows/publish-to-hf.yml` that runs only manually (`workflow_dispatch`).
2. The workflow will use the `HF_TOKEN` secret to push the model artifacts (adapter, merged weights, GGUF, WebLLM build) to the Hugging Face Hub.
3. The model card will be generated/updated to include:
    - License (Apache 2.0 or similar permissive).
    - Data sources (this list's content, original questions).
    - Evaluation results (from Phase 1).
    - Evidence-gate behavior (the model's tendency to cite sources or admit ignorance).
4. Verify the workflow configuration.

## Notes

- The workflow must be manual only (no schedule).
- The model card must be comprehensive as per the requirements.
- I will document the process in `ops/.notes.md`.
