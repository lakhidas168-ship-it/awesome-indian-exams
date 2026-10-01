# Verification Standards for Exam Pages

This document codifies the evidence standards that every exam page in `awesome-indian-exams` must meet. These standards are enforced by the content gate (`scripts/validate.py`) and the evidence gate (`scripts/evidence_gate.py`).

## Frontmatter `last_verified` Date Integrity

### Rule 1: Official Fetch Required for Updates
The `last_verified` date in frontmatter **must only be updated** if official documents were successfully opened and verified during the current run with **HTTP 200 status**.

- A page's `last_verified` date represents the date the official source was last fetched and confirmed.
- Updating `last_verified` without a successful HTTP 200 fetch from an official domain is prohibited.
- The fetch must be recorded in the task receipt (`ops/done/T-XXX.md`) via the `fetch_url` tool.

### Rule 2: Evidence Text Date Must Match Frontmatter
The evidence status line in the page body **must contain a date that exactly matches** the `last_verified` frontmatter date.

**Required format** (example):
```markdown
---
last_verified: 2026-09-27
verification: official
---

> **Evidence status: 🟢 official.** Every number below is from the SSC Combined Graduate Level
> Examination, 2026 notice (F. No. HQ-C11018/1/2026-C-1), fetched from ssc.gov.in on 2026-09-27.
```

- The date in "fetched from ... on YYYY-MM-DD" or "checked on YYYY-MM-DD" or "verified on YYYY-MM-DD" **must equal** `last_verified`.
- Any contradiction (evidence text date ≠ frontmatter `last_verified`) automatically rejects the page from `verification: official` status.
- The evidence gate (`scripts/evidence_gate.py`) cross-checks the receipt's fetch records against both dates.

### Rule 3: Failed Fetches Preserve Existing Content
If official sources fail to fetch (HTTP 403, 404, 5xx, URLError, timeout, DNS failure):

1. **Do not change** the existing `last_verified` date.
2. **Downgrade** `verification` to `secondary` or `unverified`.
3. **Retain** all existing verified content — do not remove numbers, patterns, or syllabus entries.
4. Add a disclaimer at the top of the page noting the fetch failure and current status.

**Example disclaimer:**
```markdown
> **Evidence status: 🟡 secondary.** The official portal `example.gov.in` returned HTTP 403 on 2026-10-01.
> Content retains the last verified facts from 2026-09-15. Re-verify when the portal is accessible.
```

### Rule 4: Verification Status Definitions

| Status | Meaning | Requirements |
|--------|---------|--------------|
| `official` | Every fact traced to official document fetched this run | HTTP 200 fetch recorded in receipt; evidence text date = `last_verified`; all numbers sourced from fetched doc |
| `secondary` | Facts from official sources but not re-verified this run | Previous `official` content retained; fetch failed or not attempted this run |
| `unverified` | No official source confirmed; content may be incomplete | Placeholder or harvested content awaiting verification |

## Official Sources Section

Under `## Official sources`, **only** list URLs that:
1. Are on domains listed in `ops/official-domains.txt`
2. Were fetched with HTTP 200 during the current or a previous verified run
3. Directly support the numbers in `## At a glance` and `## Exam pattern`

Coaching sites, blogs, news aggregators, Telegram, Drive, Mega, Scribd, and file-dump hosts are **never** allowed under `## Official sources`.

## Content Gate Checks

The content gate (`scripts/validate.py --strict`) enforces:

1. All required frontmatter keys present (`title`, `exam_id`, `conducting_body`, `official_site`, `cycle`, `last_verified`, `verification`)
2. `last_verified` is valid YYYY-MM-DD, not in the future
3. `verification` is one of `official`, `secondary`, `unverified`
4. All required sections present (`## At a glance`, `## Official sources`, `## Exam pattern`, `## Syllabus`, `## Free resources`)
5. All links under `## Official sources` point to allowed official domains
6. No blocked hosts (Telegram, Drive, Mega, etc.) anywhere in the page
7. Relative links resolve within the content folder
8. Generated files (`README.md`, `UPDATES.md`, `resources/all-exams.md`, `resources/overlap-map.md`) are in sync

## Evidence Gate Checks

The evidence gate (`scripts/evidence_gate.py`) runs on agent branches and enforces:

For any exam page newly marked `verification: official` or with a changed `last_verified`:
- The task receipt must contain a `## Sources fetched (code)` block with JSONL fetch records
- At least one record must have: `status: 200`, `official: true`, URL matching one under `## Official sources`, fetch date within ±1 day of `last_verified`
- If no such record exists, the gate fails with: "marked official, but no code-recorded fetch backs it"

## Agent Workflow for Verification

When assigned a verification task (e.g., "Verify exams/xxx/yyy.md against official notification"):

1. **Fetch** the official notification/bulletin using the `fetch_url` tool (records evidence automatically).
2. **Extract** every number (stages, questions, marks, time, negative marking, age, qualification, dates) from the fetched document only.
3. **Update** the page with only confirmed facts. If a fact is not in the document, write "see the notification" or omit it.
4. **Set** `last_verified` to today's date (YYYY-MM-DD) **only if** the fetch succeeded (HTTP 200).
5. **Write** the evidence status line with the matching date: "fetched from <domain> on YYYY-MM-DD".
6. **Set** `verification: official` **only if** the fetch succeeded and all numbers match.
7. **If fetch fails**: keep existing `last_verified`, set `verification: secondary` or `unverified`, add disclaimer, retain all content.
8. **Run** `scripts/validate.py --strict` and fix all errors before finishing.

## Common Violations and Fixes

| Violation | Fix |
|-----------|-----|
| `last_verified` updated but no fetch in receipt | Re-fetch with `fetch_url`, update receipt, ensure HTTP 200 |
| Evidence text date ≠ `last_verified` | Align both dates to the actual fetch date |
| `verification: official` but fetch failed (403/URLError) | Downgrade to `secondary`/`unverified`, add disclaimer, revert `last_verified` |
| Non-official link under `## Official sources` | Remove or replace with official domain link |
| Missing evidence status line | Add `> **Evidence status: ...**` block with fetch date |
| Stale `last_verified` (>120 days) | Re-verify against current official notification |

## References

- `scripts/validate.py` — content gate implementation
- `scripts/evidence_gate.py` — evidence gate implementation
- `ops/official-domains.txt` — allowlisted official domains
- `ops/tasks.toml` — task definitions with acceptance criteria

---

*This standard is binding for all agent lanes. Changes require a reviewed pull request by the owner.*