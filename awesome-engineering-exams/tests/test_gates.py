"""Self-tests for the content gate and the lane scope gate. Each test proves a bad input is rejected."""
from __future__ import annotations

import datetime as dt
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import hive_gate  # noqa: E402
import validate  # noqa: E402

TODAY = dt.date(2026, 9, 27)
GOOD_PAGE = """---
title: Test Exam
exam_id: test-exam
conducting_body: Test Commission
official_site: https://upsc.gov.in
cycle: 2027
last_verified: 2026-09-01
verification: secondary
---

# Test Exam

## At a glance
x

## Official sources
- <https://upsc.gov.in/notice.pdf>

## Exam pattern
x

## Syllabus
x

## Free resources
- <https://ocw.mit.edu/>
"""


class ContentGate(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "exams").mkdir()
        (self.tmp / "ops" / "done").mkdir(parents=True)
        shutil.copy(ROOT / "ops" / "official-domains.txt", self.tmp / "ops")
        (self.tmp / "ops" / "tasks.toml").write_text(
            '[[task]]\nid = "T-001"\nlane = "hermes"\npriority = 1\ntitle = "t"\naccept = ["a"]\n', encoding="utf-8")
        (self.tmp / "README.md").write_text(f"{validate.INDEX_START}\n{validate.INDEX_END}\n", encoding="utf-8")
        self.page = self.tmp / "exams" / "test-exam.md"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def errors(self, page_text: str = GOOD_PAGE) -> list[str]:
        self.page.write_text(page_text, encoding="utf-8")
        rep, _ = validate.run(self.tmp, TODAY)
        return rep.errors

    def test_good_page_passes(self) -> None:
        self.assertEqual(self.errors(), [])

    def test_repo_content_passes(self) -> None:
        rep, pages = validate.run(ROOT, dt.date.today())
        self.assertEqual(rep.errors, [])
        self.assertGreater(len(pages), 0)

    def test_missing_frontmatter(self) -> None:
        self.assertTrue(any("frontmatter" in e for e in self.errors(GOOD_PAGE.split("---\n", 2)[2])))

    def test_non_official_site(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("official_site: https://upsc.gov.in", "official_site: https://coaching.example.com"))
        self.assertTrue(any("official_site host" in e for e in errs))

    def test_lookalike_domain_is_not_official(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("https://upsc.gov.in/notice.pdf", "https://upsc-gov.in.example.com/notice.pdf"))
        self.assertTrue(any("non-official link" in e for e in errs))

    def test_non_official_link_under_official_sources(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("https://upsc.gov.in/notice.pdf", "https://blog.example.com/pattern"))
        self.assertTrue(any("non-official link" in e for e in errs))

    def test_file_dump_link_blocked_anywhere(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("https://ocw.mit.edu/", "https://t.me/freenotes"))
        self.assertTrue(any("blocked file-dump host" in e for e in errs))

    def test_future_date(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("last_verified: 2026-09-01", "last_verified: 2027-01-01"))
        self.assertTrue(any("future" in e for e in errs))

    def test_unknown_verification(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("verification: secondary", "verification: trust-me"))
        self.assertTrue(any("verification must be" in e for e in errs))

    def test_missing_section(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("## Syllabus\n", "## Topics\n"))
        self.assertTrue(any("missing section '## Syllabus'" in e for e in errs))

    def test_exam_id_must_match_file(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("exam_id: test-exam", "exam_id: other"))
        self.assertTrue(any("exam_id" in e for e in errs))

    def test_stale_page_warns(self) -> None:
        self.page.write_text(GOOD_PAGE.replace("last_verified: 2026-09-01", "last_verified: 2025-01-01"), encoding="utf-8")
        rep, _ = validate.run(self.tmp, TODAY)
        self.assertTrue(any("older than" in w for w in rep.warnings))

    def test_bad_task_lane_and_unknown_dep(self) -> None:
        (self.tmp / "ops" / "tasks.toml").write_text(
            '[[task]]\nid = "T-001"\nlane = "anyone"\npriority = 1\ntitle = "t"\naccept = ["a"]\ndeps = ["T-999"]\n',
            encoding="utf-8")
        errs = self.errors()
        self.assertTrue(any("lane must be" in e for e in errs))
        self.assertTrue(any("unknown dependency" in e for e in errs))

    def test_receipt_for_unknown_task(self) -> None:
        (self.tmp / "ops" / "done" / "T-777.md").write_text("x", encoding="utf-8")
        self.assertTrue(any("unknown task" in e for e in self.errors()))

    def test_write_fills_index(self) -> None:
        self.page.write_text(GOOD_PAGE, encoding="utf-8")
        validate.run(self.tmp, TODAY, write=True)
        self.assertIn("exams/test-exam.md", (self.tmp / "README.md").read_text(encoding="utf-8"))
        rep, _ = validate.run(self.tmp, TODAY)
        self.assertEqual(rep.warnings, [])


class LaneGate(unittest.TestCase):
    P = "awesome-engineering-exams"

    def check(self, branch: str, paths: list[str]) -> list[str]:
        return hive_gate.check(branch, paths, self.P)

    def test_hermes_content_with_receipt_passes(self) -> None:
        self.assertEqual(self.check("agent/hermes/T-001", [f"{self.P}/exams/gate-ee.md", f"{self.P}/ops/done/T-001.md"]), [])

    def test_hermes_cannot_touch_gate(self) -> None:
        errs = self.check("agent/hermes/T-001", [f"{self.P}/scripts/validate.py", f"{self.P}/ops/done/T-001.md"])
        self.assertTrue(errs)

    def test_hermes_cannot_edit_allowlist_or_backlog(self) -> None:
        for path in ("ops/official-domains.txt", "ops/tasks.toml"):
            self.assertTrue(self.check("agent/hermes/T-001", [f"{self.P}/{path}", f"{self.P}/ops/done/T-001.md"]))

    def test_worker_needs_own_receipt_only(self) -> None:
        self.assertTrue(self.check("agent/hermes/T-001", [f"{self.P}/exams/gate-ee.md"]))
        self.assertTrue(self.check("agent/hermes/T-001", [f"{self.P}/ops/done/T-001.md", f"{self.P}/ops/done/T-002.md"]))

    def test_opencode_may_touch_scripts_and_own_workflow_only(self) -> None:
        ok = [f"{self.P}/scripts/validate.py", ".github/workflows/awesome-exams.yml", f"{self.P}/ops/done/T-101.md"]
        self.assertEqual(self.check("agent/opencode/T-101", ok), [])
        self.assertTrue(self.check("agent/opencode/T-101", [".github/workflows/other.yml", f"{self.P}/ops/done/T-101.md"]))
        self.assertTrue(self.check("agent/opencode/T-101", ["README.md", f"{self.P}/ops/done/T-101.md"]))

    def test_jevx_limited_to_backlog_plan_and_generated(self) -> None:
        ok = [f"{self.P}/ops/tasks.toml", f"{self.P}/ops/plan/2026-09-27.md", f"{self.P}/README.md", f"{self.P}/UPDATES.md"]
        self.assertEqual(self.check("agent/jevx/plan-20260927-1540", ok), [])
        for bad in ("exams/gate-ee.md", "ops/prompts/jevx.md", "ops/done/T-001.md", "scripts/validate.py"):
            self.assertTrue(self.check("agent/jevx/plan-x", [f"{self.P}/{bad}"]), bad)

    def test_non_agent_branch_is_not_gated(self) -> None:
        self.assertEqual(self.check("claude/some-branch", ["anything"]), [])


if __name__ == "__main__":
    unittest.main()
