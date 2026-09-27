---
name: harvest-import
description: Turn one item of the owner's earlier local exam work (inventory id inv:xxxxxxxx) into verified public content in awesome-indian-exams. Use for tasks titled "Harvest inv:...". Mac only.
---

# Harvest import

The owner spent nine months building exam material that is now scattered across the Mac and several Google
accounts. `ops/harvest.py` indexed it privately in `~/.hive/harvest/`. Your job is to turn one item into public
content that meets the hub's standards.

1. Read the item: MCP tool `harvest_item` with the task's `inv:` id, or `python3 ops/harvest.py show <id>`.
   Related items: `harvest_search`.
2. Use it for what the owner is uniquely good at: **structure, study order, advice and leads.** Treat every exam
   fact in it (patterns, marks, dates, syllabus) as unverified until you fetch the official notification with
   `fetch_url` and confirm it.
3. Write the target page (`exams/<family>/<exam>.md`, or a module) in your own words, following the `exam-page`
   or `module-page` skill.
4. **Never** put in the repository: local paths or file names, personal data (names, phone numbers, emails, ID
   numbers), or text from coaching material, books or lecture transcripts. Items flagged `transcript` or
   `third-party` are refused by the tool for this reason.
5. If the NotebookLM MCP is available on this Mac, you may query the owner's notebooks the same way, as leads
   that need official verification.
6. In your notes, say which parts came from the owner's item (by id only) and which official URLs confirmed
   the facts.
