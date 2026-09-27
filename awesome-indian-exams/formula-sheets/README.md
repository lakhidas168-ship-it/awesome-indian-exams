# Formula sheets

One page of standard results per subject, written from scratch for this list. A sheet is a study aid, not a
source of exam facts: marks, dates and syllabus claims stay on the exam pages, which carry the evidence.

## Format

One subject per file: `formula-sheets/<subject>.md`, where `<subject>` is a lowercase-hyphenated slug and the
file name equals the frontmatter `subject`. The gate (`python3 scripts/validate.py`) rejects a sheet with no
frontmatter, missing `title`, `subject` or `exams`, an exam id that is not in
[the registry](../registry/exams.toml), no `$$` display-math block, or a `$$` block left unclosed.

| Frontmatter key | Meaning |
|---|---|
| `title` | Sheet title, e.g. `Electric Circuits — formula sheet`. |
| `subject` | Lowercase-hyphenated slug; must equal the file name. |
| `exams` | Comma-separated registry exam ids the sheet serves, e.g. `gate-ee, upsc-ese-ee`. |

Display math goes between `$$` delimiters. Every opening `$$` needs a closing `$$`; the gate pairs them up
outside fenced code blocks, so an unclosed block fails with the line number. A `\$$` is a literal delimiter for
the page and is ignored by the check.

```markdown
---
title: Electric Circuits — formula sheet
subject: electric-circuits
exams: gate-ee, upsc-ese-ee
---

# Electric Circuits — formula sheet

$$ V = IR, \qquad P = VI $$
```

## Sheets

- [Electric Circuits](electric-circuits.md) — DC, network theorems, transients, RLC, AC power, resonance,
  three-phase and two-port results.
