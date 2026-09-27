---
name: exam-page
description: Write or verify an exam page in awesome-indian-exams (exams/<family>/<id>.md) from the exam's official notification, with honest evidence status. Use for any task that creates or verifies an exam page.
---

# Exam page

**Where:** `exams/<family>/<id>.md`. The `<id>` and `<family>` come from `registry/exams.toml`. Copy the
structure of an existing page (for example `exams/ssc/ssc-cgl.md`).

**Frontmatter (all required):** `title`, `exam_id` (= file name), `conducting_body`, `official_site`, `cycle`,
`last_verified` (YYYY-MM-DD), `verification` (`official` | `secondary` | `unverified`).

**Sections (all required, in this order):** `## At a glance` · `## Official sources` · `## Exam pattern` ·
`## Syllabus` · `## Free resources`. Add a `## How to prepare (free, in order)` section when you can.

## Steps

1. Read the registry entry: `official_site` is the starting point. If it is blank, find the official site and
   check that its domain is in `ops/official-domains.txt`. If it is not, say so in your notes and keep the page
   `unverified`.
2. Fetch the current official notification or information bulletin with `fetch_url`. PDFs are fine.
3. Take every number (stages, questions, marks, time, negative marking, age, qualification) from that document
   only. If the document does not state something, leave it out or write "see the notification".
4. Under `## Official sources`, list **exactly the URLs you fetched**, as `<https://...>` links. Only official
   domains are allowed there.
5. Link the shared modules the exam uses (`../../modules/<id>.md` if the page exists, otherwise the overlap map
   at `../../resources/overlap-map.md`).
6. Set `verification: official` and `last_verified: <today>` **only** if the official document was fetched
   successfully this run and supports every number on the page. Otherwise use `secondary` or `unverified`, and put
   a one-line evidence-status note at the top of the page.
7. Run the content gate. Fix every error before you finish.

## Never

Invent facts · cite coaching sites as sources · copy text from coaching notes, books or transcripts · link to
Telegram/Drive/Mega/Scribd · edit generated files (README index, `resources/all-exams.md`,
`resources/overlap-map.md`, `UPDATES.md`).
