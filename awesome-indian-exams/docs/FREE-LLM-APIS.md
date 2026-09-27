# Free LLM API keys for the hive (checked 2026-09-27)

Free tiers let the hive's `free-agent` workers run without paying. Each provider limits requests or tokens per
day. Keys from **different providers** add up, because each provider counts its own limits.

## Where the keys go

- **24/7 work runs on the owner's Mac.** Put the keys in `~/.hive/agents.env` there, one `NAME=value` per line.
  The Mac's `hive-loop.sh` picks them up on its next start.
- **GitHub Actions is only for occasional manual runs** (for example `hive-cloud.yml` while the Mac is off, or
  `ai-accounts.yml`). Never schedule the hive on GitHub:
  - frequent automated pushes got the owner's previous account flagged as spam;
  - GitHub's terms forbid using hosted runners for anything unrelated to the repository's own project;
  - the free tiers' daily caps would run out anyway.
- **Never commit a key.** Keys go only in `agents.env` on the Mac, or in repository secrets.

## The providers, best value first

Limits change often. The numbers below are those listed by the sources at the end on 2026-09-27; the provider's own
console shows the live numbers.

| # | Provider | Get the key | Free limits (as listed) | Env var | OpenAI-compatible base URL |
|---|---|---|---|---|---|
| 1 | Cerebras | <https://cloud.cerebras.ai> | Reported 1M tokens/day, 10–30 RPM | `CEREBRAS_API_KEY` | `https://api.cerebras.ai/v1` |
| 2 | Google AI Studio (Gemini) | <https://aistudio.google.com/app/apikey> | Flash models: about 15 RPM and up to about 1,500 requests/day, by model. Pro left the free tier in April 2026 | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com/v1beta/openai` |
| 3 | Groq | <https://console.groq.com/keys> | 30 RPM, 250–1,000 requests/day by model | `GROQ_API_KEY` | `https://api.groq.com/openai/v1` |
| 4 | NVIDIA NIM | <https://build.nvidia.com> | 40 RPM (NVIDIA Developer Program sign-up) | `NVIDIA_API_KEY` | `https://integrate.api.nvidia.com/v1` |
| 5 | Mistral | <https://console.mistral.ai/api-keys> | Free monthly credits, no card | `MISTRAL_API_KEY` | `https://api.mistral.ai/v1` |
| 6 | OpenRouter | <https://openrouter.ai/keys> | Free models: 20 RPM, 50 requests/day, or 1,000/day after a one-time $10 credit purchase | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` |
| 7 | GitHub Models | <https://github.com/marketplace/models> | 150 requests/day (small models), 50/day (large). Uses the workflow's own `GITHUB_TOKEN` | `GITHUB_TOKEN` | `https://models.github.ai/inference` |
| 8 | Cloudflare Workers AI | <https://dash.cloudflare.com/profile/api-tokens> | 10,000 "neurons"/day | `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` | `https://api.cloudflare.com/client/v4/accounts/<account id>/ai/v1` |
| 9 | Ollama Cloud | <https://ollama.com/settings/keys> | Free session and weekly limits (not published) | `OLLAMA_API_KEY` | `https://ollama.com/v1` |
| 10 | SambaNova Cloud | <https://cloud.sambanova.ai> | Small daily limits (sources differ: about 20 RPM, 200K tokens/day) | `SAMBANOVA_API_KEY` | `https://api.sambanova.ai/v1` |
| 11 | Cohere | <https://dashboard.cohere.com/api-keys> | Trial key: 1,000 calls/month | `COHERE_API_KEY` | see Cohere's "Compatibility API" docs |
| 12 | Hugging Face Inference Providers | <https://huggingface.co/settings/tokens> | Small monthly credit | `HF_TOKEN` | `https://router.huggingface.co/v1` |
| 13 | LLM7.io | <https://token.llm7.io> | About 60 requests/hour without a key; more with a free token | `LLM7_API_KEY` | `https://api.llm7.io/v1` |
| 14 | Kilo Code gateway | <https://app.kilo.ai/profile> | About 200 requests/hour | `KILO_API_KEY` | `https://api.kilo.ai/api/gateway` |
| 15 | Aion Labs | <https://www.aionlabs.ai/app/api-keys/> | 15 RPM, 20K tokens/day | `AION_API_KEY` | `https://api.aionlabs.ai/v1` |
| 16 | OVHcloud AI Endpoints | <https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/> | 2 RPM without sign-up | none | `https://oai.endpoints.kepler.ai.cloud.ovh.net/v1` |
| 17 | Z AI (Zhipu GLM) | <https://open.bigmodel.cn/usercenter/apikeys> | Permanent free Flash models; sign-up may need a Chinese phone number | `ZAI_API_KEY` | `https://open.bigmodel.cn/api/paas/v4` |
| 18 | ModelScope | <https://modelscope.cn/my/myaccesstoken> | About 2,000 requests/day; needs Chinese phone verification | `MODELSCOPE_API_KEY` | `https://api-inference.modelscope.cn/v1` |

**Command-line agents on the Mac (use the owner's own login, no API key):**

- **Gemini CLI:** 1,000 requests/day and 60 requests/minute with a personal Google account.
- **Qwen Code:** its free OAuth tier closed on 15 April 2026, so don't rely on it.

## Tips from the lists and forums

1. **Spread the load across providers.** Each counts its own limits. `free_agent.py` already moves to the next
   provider on a 429 or a missing key.
2. **One account per provider.** Opening several accounts at the same provider to multiply the free quota breaks
   almost every provider's terms, and the keys get banned. Different providers are fine.
3. **Small, fast models for bulk work, big ones for judging.** Flash, 8B and 20B models are enough for drafting
   and checking links; keep the large models for the JEVX judge.
4. **OpenRouter's one-time $10** raises its free-model limit from 50 to 1,000 requests a day. It is the cheapest
   upgrade if one is ever wanted.
5. **Free tiers may use prompts for training.** Never send personal data. The hive only sends public exam
   content.
6. **Model names retire often.** When a provider answers 404 for a model, update the model list rather than the
   code.

## Sources

- [awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis): provider list, key URLs, base URLs.
- OpenRouter: [FAQ](https://openrouter.ai/docs/faq) and [free tiers compared](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/).
- Cerebras free tier: [1M tokens/day](https://yangmao.ai/en/deals/cerebras-free-inference/).
- [Groq rate limits](https://console.groq.com/docs/rate-limits).
- [Gemini free tier 2026](https://tokenmix.ai/blog/gemini-api-free-tier-limits) and [Gemini CLI quotas](https://geminicli.com/docs/resources/quota-and-pricing/).
- [GitHub Models free tier](https://getaitools.dev/service/github-models).
- [SambaNova rate limits](https://docs.sambanova.ai/docs/en/models/rate-limits).
- [Qwen Code free tier ending](https://inventivehq.com/blog/qwen-code-still-free-2026-shutdown).
- [GitHub terms for Actions](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features).
