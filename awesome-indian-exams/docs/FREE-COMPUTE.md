# Free compute for the hive: the jugaad list

How this project keeps running 24/7 with no budget. Every entry is something the hive can use today or that the
owner can apply for. Free tiers change often, so the Hermes lane re-checks this page against each provider's
official page every month (backlog task `T-016`, re-added monthly by JEVX).

> **Status:** first written 2026-09-27 from the maintainer's knowledge and web search, not yet re-checked entry
> by entry against official pages. Treat the limits as indicative.

## Already wired in (no setup)

| What | What is free | How the hive uses it | Caveat |
|---|---|---|---|
| **GitHub Actions** | Standard runners are free for public repositories | Validates every push and pull request; runs the cloud hive by hand when the Mac is off (`.github/workflows/hive-cloud.yml`) | Never schedule the hive: frequent automated pushes look like spam. Scheduled checks pause after 60 days without repository activity |
| **GitHub Models** | Free, rate-limited inference with the workflow's `GITHUB_TOKEN` (`permissions: models: read`) | Default provider of the free agent and the judge | Per-request limits (about 8k tokens in, 4k out) and daily request caps, so expect **roughly 5–15 tasks a day** from this alone. The agent keeps its context small to fit |

## One-time owner steps that add free capacity (repository secrets)

Add any of these under *Settings → Secrets and variables → Actions*. The free agent tries providers in order and
skips any that is missing or rate-limited, so each extra key adds capacity.

| Secret | Where to get it | Notes |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio | Free tier with daily limits. Free-tier prompts may be used by Google to improve its products, which is fine for this public content |
| `OPENROUTER_API_KEY` | OpenRouter | Models whose id ends in `:free` cost nothing, within daily limits |
| `GROQ_API_KEY` | Groq | Free tier, fast inference, rate-limited |

## Paid by the owner (already bought)

| What | How the hive uses it |
|---|---|
| **OpenCode Go** plan | Secret `OPENCODE_API_KEY`. The cloud OpenCode lane runs the real OpenCode CLI on DeepSeek V4.1 Flash, and the judge prefers it. Content work uses free tiers first to save the plan's limits. Known issue: the Go gateway sometimes rejects requests, so every lane has a free fallback |
| **Google AI Pro / Workspace accounts** | Gemini CLI signed in with one of them is a Mac worker in the Hermes lane; Drive for desktop mounts their files for the harvest; NotebookLM (through its MCP on the Mac) is a source of leads for Hermes-lane workers |

## Free on the owner's Mac

| What | Why |
|---|---|
| **Gemini CLI** signed in with a Google account | Free tier of about 1,000 requests a day (more with AI Pro); runs as an extra Hermes-lane worker (`gemini --yolo -p`) |
| **Ollama** + a small instruct model | Unlimited local inference. Set `HIVE_CMD_HERMES=free-agent` in cron and the agent uses `http://localhost:11434/v1` when cloud providers are exhausted |
| The owner's own **JEVX / Hermes / OpenCode** | Extra lanes through `ops/crontab.example`. Their claims never collide with the cloud's |

## Worth applying for

| Programme | What it can give | Fit |
|---|---|---|
| **GitHub Student Developer Pack** | Free GitHub Copilot Pro for verified students, which raises GitHub Models limits | Needs current student verification |
| **Oracle Cloud Always Free** | Always-free Arm VM capacity, enough to host Ollama with a small model 24/7 | Needs a card for identity verification; no charge on the always-free tier |
| **Google Cloud free trial / free tier** | Trial credits for new accounts plus always-free products | Needs a card |
| **Google for Startups, Microsoft for Startups, AWS Activate** | Cloud credits for early-stage startups | Apply once AIR1 has a website and a public product. This repository is that product |
| **Kaggle / Google Colab** | Free notebook GPUs with weekly quotas | Good for training and evaluating the future JEV+LLM model, not for 24/7 serving |

## Rules for adding an entry

Only free or free-credit offers, each with the provider's official page, what exactly is free, and the catch
(card needed, data use, limits). Remove offers that have ended.
