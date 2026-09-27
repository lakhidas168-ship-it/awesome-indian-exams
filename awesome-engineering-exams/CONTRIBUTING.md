# Contributing

Students, teachers and toppers are all welcome. The one rule: **anything a student might act on must be
traceable to an official source.**

## Fixing or adding exam facts

1. Find the official document (notification, information brochure, syllabus PDF) on an official domain.
   The accepted domains are listed in [`ops/official-domains.txt`](ops/official-domains.txt). To add a domain,
   say in your PR why it is official.
2. Edit the exam page in `exams/`. Put the document's URL under `## Official sources`.
3. Set `verification: official` and `last_verified: <today>` only if the official document supports every
   number on the page. Otherwise leave it as `secondary` or `unverified`.
4. Run the gate: `python3 scripts/validate.py` (Python 3.11+, no dependencies).

## Adding an exam page

Copy the structure of an existing page. Frontmatter keys: `title`, `exam_id` (the file name),
`conducting_body`, `official_site`, `cycle`, `last_verified`, `verification`. Required sections:
`At a glance`, `Official sources`, `Exam pattern`, `Syllabus`, `Free resources`. You don't need to edit the
README index; it is regenerated automatically.

## Adding resources

- Free and legal only, linked to the publisher. No links to Telegram, Google Drive, Mega, Scribd or other file
  dumps (the gate rejects them).
- No copied text from coaching material, paid courses, books or lecture transcripts. Write in your own words.
- Paid resources are out of scope for this list.

## Licensing of contributions

By contributing, you agree that your content is published under CC BY-SA 4.0 and your code under MIT.
