# SBI recruitment now lives on `sbi.bank.in` (proposal for `ops/official-domains.txt`)

**Problem (found while verifying T-264 SBI Clerk and T-263 SBI PO, 2026-09-28).** `ops/official-domains.txt`
lists `sbi.co.in`, but SBI's careers portal and all recruitment documents have moved: every URL fetched this
week returns HTTP 200 and its `final_url` after redirects is on `sbi.bank.in`. `ops/free_agent.py:fetch` marks `official` from
the **final** URL host, so every SBI fetch is recorded `official: false` and no SBI page can satisfy the
evidence gate for `verification: official` — even though the fetched document is SBI's own advertisement.

SBI's own caution notice on the careers page says recruitment details are published only on
`https://sbi.co.in/careers` and `https://bank.sbi/careers`, and the advertisements themselves instruct
candidates to use `https://sbi.bank.in/web/careers/current-openings`. These are SBI's official domains, not
third-party mirrors.

## Measured, same machine, 2026-09-27/28 (UTC), from `~/.hive/opencode-2.fetch.jsonl`

| URL fetched | status | final_url host | official |
|---|---|---|---|
| `https://sbi.co.in/web/careers/current-openings` | 200 | `sbi.bank.in` | false |
| `https://sbi.co.in/webfiles/uploads/files_2627/08/JA_2026_Detailed_Advt_Eng.pdf` | 200 | `sbi.bank.in` | false |
| `https://sbi.bank.in/webfiles/uploads/files_2627/08/JA_2026_Detailed_Advt_Eng.pdf` | 200 | `sbi.bank.in` | false |
| `https://sbi.co.in` (T-263) | 200 | `sbi.co.in/redirect/` | **true** |

## Proposed change (protected file — JEVX lane decides)

Add to `ops/official-domains.txt`, under the "Exam bodies that publish on their own domains" block:

```
sbi.bank.in
bank.sbi
```

`validate.host_matches` matches an entry itself and any subdomain, so both lines are safe (neither is a public
suffix). No gate is weakened: the evidence gate still requires a code-recorded HTTP 200 fetch of a URL listed
under the page's Official sources, within a day of `last_verified`; this only stops the redirect from
disqualifying SBI's own host.

## Impact

- Unblocks `verification: official` for SBI Clerk, SBI PO and the other SBI pages once re-fetched.
- Until then, T-263/T-264 keep `secondary` with the reason stated on the page.
