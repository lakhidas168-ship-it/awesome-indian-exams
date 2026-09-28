"""MkDocs hook: give every page a search and link-preview description.

Exam pages get one built from their own frontmatter (exam, cycle, conducting body, evidence status), so a search
result or a WhatsApp preview says exactly what the page is. Pages that set `description:` keep their own.
"""
from __future__ import annotations

EVIDENCE = {"official": "checked against the official notification", "secondary": "cross-checked, confirm on the official site",
            "unverified": "structure and official links; confirm numbers on the official site"}


def describe(title: str, meta: dict) -> str:
    if meta.get("exam_id"):
        parts = [f"{title}: exam pattern, syllabus, official links, previous papers and free resources"]
        if meta.get("cycle"):
            parts.append(f"for {meta['cycle']}")
        if meta.get("conducting_body"):
            parts.append(f"(conducted by {meta['conducting_body']})")
        text = " ".join(parts) + "."
        if meta.get("verification") in EVIDENCE:
            text += f" Evidence: {EVIDENCE[meta['verification']]}."
        return text + " Free, no login."
    if meta.get("module_id"):
        return f"{title}: what it covers, which exams it counts for, and free official resources. Prepare once, use for many exams."
    return ""


def on_page_context(context, page, config, nav):
    meta = page.meta if isinstance(page.meta, dict) else {}
    if not meta.get("description") and page.title:
        text = describe(page.title, meta)
        if text:
            page.meta["description"] = text
    return context
