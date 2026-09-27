---
name: module-page
description: Write a shared syllabus module page (modules/<id>.md) for awesome-indian-exams, covering what the module contains, how deep each exam family goes, and free official resources. Use for tasks that create modules/ pages.
---

# Module page

A module is a block of syllabus shared by many exams (for example quantitative aptitude, Indian polity, NCERT
physics). Students prepare it once and it counts for every exam that lists it in `registry/exams.toml`.

**Where:** `modules/<id>.md`, with `<id>` from the `[[module]]` entries in the registry.
**Frontmatter:** `title`, `module_id` (= file name).
**Model page:** `modules/quant-aptitude.md`.

## Sections

1. One line on which exam families use it, linking `../resources/overlap-map.md`.
2. `## What it covers`: the topics, grouped.
3. `## Depth by exam family`: a short table of how deep each family goes.
4. `## Free resources`: only free, legal material linked to its publisher (NCERT `ncert.nic.in`, NIOS
   `nios.ac.in`, official bodies, Khan Academy, MIT OCW, NPTEL). Never file dumps or coaching PDFs.
5. `## How to practise`: concrete, short.

Keep it under about 60 lines. Run the content gate before you finish.
