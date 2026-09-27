"""Self-tests for the content gate, the lane scope gate and the evidence gate.

Each test proves a bad input is rejected. The cloud judge runs main's copy of these tests against every agent
branch, so a branch that loosens an existing check fails here.
"""
from __future__ import annotations

import datetime as dt
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_gate  # noqa: E402
import hive_gate  # noqa: E402
import validate  # noqa: E402

TODAY = dt.date(2026, 9, 27)
REGISTRY = """
[[family]]
id = "ssc"
title = "SSC"
focus = "india"

[[module]]
id = "reasoning"
title = "Reasoning"

[[exam]]
id = "test-exam"
name = "Test Exam"
family = "ssc"
body = "Test Commission"
official_site = "https://ssc.gov.in"
modules = ["reasoning"]
"""
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
        (self.tmp / "exams" / "ssc").mkdir(parents=True)
        (self.tmp / "ops" / "done").mkdir(parents=True)
        (self.tmp / "registry").mkdir()
        (self.tmp / "registry" / "exams.toml").write_text(REGISTRY, encoding="utf-8")
        shutil.copy(ROOT / "ops" / "official-domains.txt", self.tmp / "ops")
        (self.tmp / "ops" / "tasks.toml").write_text(
            '[[task]]\nid = "T-001"\nlane = "hermes"\npriority = 1\ntitle = "t"\naccept = ["a"]\n', encoding="utf-8")
        (self.tmp / "README.md").write_text("<!-- EXAMS:START -->\n<!-- EXAMS:END -->\n", encoding="utf-8")
        self.page = self.tmp / "exams" / "ssc" / "test-exam.md"

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

    def test_broken_relative_link(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("## Syllabus\nx", "## Syllabus\nSee [map](../../resources/missing.md)"))
        self.assertTrue(any("broken relative link" in e for e in errs))

    def test_link_leaving_the_content_folder(self) -> None:
        errs = self.errors(GOOD_PAGE.replace("## Syllabus\nx", "## Syllabus\nSee [ci](../../../.github/ci.yml)"))
        self.assertTrue(any("leaves the content folder" in e for e in errs))

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

    def test_page_must_be_in_registry_and_right_family(self) -> None:
        (self.tmp / "exams" / "ssc" / "stray.md").write_text(GOOD_PAGE.replace("test-exam", "stray"), encoding="utf-8")
        self.assertTrue(any("not in registry" in e for e in self.errors()))
        (self.tmp / "exams" / "ssc" / "stray.md").unlink()
        (self.tmp / "exams" / "banking").mkdir()
        self.page.rename(self.tmp / "exams" / "banking" / "test-exam.md")
        self.page = self.tmp / "exams" / "banking" / "test-exam.md"
        self.assertTrue(any("not a family" in e for e in self.errors()))

    def test_registry_rejects_unknown_module_and_unofficial_site(self) -> None:
        bad = REGISTRY.replace('modules = ["reasoning"]', 'modules = ["telepathy"]').replace(
            "https://ssc.gov.in", "https://ssc-results.example.com")
        (self.tmp / "registry" / "exams.toml").write_text(bad, encoding="utf-8")
        errs = self.errors()
        self.assertTrue(any("unknown module" in e for e in errs))
        self.assertTrue(any("official_site host" in e for e in errs))

    def test_stale_page_warns(self) -> None:
        self.page.write_text(GOOD_PAGE.replace("last_verified: 2026-09-01", "last_verified: 2025-01-01"), encoding="utf-8")
        rep, _ = validate.run(self.tmp, TODAY)
        self.assertTrue(any("older than" in w for w in rep.warnings))

    def test_bad_task_lane_focus_and_unknown_dep(self) -> None:
        (self.tmp / "ops" / "tasks.toml").write_text(
            '[[task]]\nid = "T-001"\nlane = "anyone"\nfocus = "mars"\npriority = 1\ntitle = "t"\naccept = ["a"]\n'
            'deps = ["T-999"]\n', encoding="utf-8")
        errs = self.errors()
        self.assertTrue(any("lane must be" in e for e in errs))
        self.assertTrue(any("focus must be" in e for e in errs))
        self.assertTrue(any("unknown dependency" in e for e in errs))

    def test_receipt_for_unknown_task(self) -> None:
        (self.tmp / "ops" / "done" / "T-777.md").write_text("x", encoding="utf-8")
        self.assertTrue(any("unknown task" in e for e in self.errors()))

    def test_write_generates_index_and_overlap(self) -> None:
        self.page.write_text(GOOD_PAGE, encoding="utf-8")
        validate.run(self.tmp, TODAY, write=True)
        self.assertIn("exams/ssc/test-exam.md", (self.tmp / "README.md").read_text(encoding="utf-8"))
        self.assertIn("Test Exam", (self.tmp / "resources" / "overlap-map.md").read_text(encoding="utf-8"))
        rep, _ = validate.run(self.tmp, TODAY)
        self.assertEqual(rep.warnings, [])


class LaneGate(unittest.TestCase):
    P = "awesome-indian-exams"

    def check(self, branch: str, paths: list[str]) -> list[str]:
        return hive_gate.check(branch, [f"{self.P}/{p}" if not p.startswith(".github") else p for p in paths], self.P)

    def test_hermes_content_with_receipt_passes(self) -> None:
        ok = ["exams/ssc/ssc-cgl.md", "modules/csat.md", "registry/exams.toml", "docs/x.md", "ops/done/T-001.md"]
        self.assertEqual(self.check("agent/hermes/T-001", ok), [])

    def test_hermes_cannot_touch_tooling_or_generated(self) -> None:
        for path in ("scripts/validate.py", "tests/test_gates.py", "ops/tasks.toml", "opencode.json",
                     "README.md", "resources/overlap-map.md", "UPDATES.md"):
            self.assertTrue(self.check("agent/hermes/T-001", [path, "ops/done/T-001.md"]), path)

    def test_no_lane_may_touch_guardrails(self) -> None:
        guardrails = ["scripts/hive_gate.py", "scripts/evidence_gate.py", "ops/judge.py", "ops/run-hourly.sh",
                      "ops/agentctl.py", "ops/free_agent.py", "ops/official-domains.txt", "ops/hive.toml",
                      "ops/prompts/hermes.md", ".agents/skills/exam-page/SKILL.md", ".github/workflows/hive-cloud.yml"]
        for lane, task in (("opencode", "T-101"), ("hermes", "T-001"), ("jevx", "plan-x")):
            for path in guardrails:
                self.assertTrue(self.check(f"agent/{lane}/{task}", [path, f"ops/done/{task}.md"]), f"{lane} {path}")

    def test_worker_needs_own_receipt_only(self) -> None:
        self.assertTrue(self.check("agent/hermes/T-001", ["exams/ssc/ssc-cgl.md"]))
        self.assertTrue(self.check("agent/hermes/T-001", ["ops/done/T-001.md", "ops/done/T-002.md"]))

    def test_opencode_may_extend_validator_and_tests(self) -> None:
        ok = ["scripts/validate.py", "scripts/new_check.py", "tests/test_new.py", "ops/mcp_server.py", "ops/done/T-101.md"]
        self.assertEqual(self.check("agent/opencode/T-101", ok), [])

    def test_jevx_limited_to_backlog_plan_and_generated(self) -> None:
        ok = ["ops/tasks.toml", "ops/plan/2026-09-27.md", "README.md", "UPDATES.md", "resources/all-exams.md"]
        self.assertEqual(self.check("agent/jevx/plan-20260927-1540", ok), [])
        for bad in ("exams/ssc/ssc-cgl.md", "ops/done/T-001.md", "scripts/validate.py"):
            self.assertTrue(self.check("agent/jevx/plan-x", [bad]), bad)

    def test_non_agent_branch_is_not_gated(self) -> None:
        self.assertEqual(hive_gate.check("claude/some-branch", ["anything"], self.P), [])


OFFICIAL_PAGE = GOOD_PAGE.replace("verification: secondary", "verification: official").replace(
    "last_verified: 2026-09-01", "last_verified: 2026-09-27")
FETCH = {"url": "https://upsc.gov.in/notice.pdf", "status": 200, "official": True, "at": "2026-09-27T10:00:00+00:00"}


class EvidenceGate(unittest.TestCase):
    def problems(self, records: list[dict], head: str = OFFICIAL_PAGE, base: str | None = GOOD_PAGE) -> list[str]:
        return evidence_gate.page_problems("exams/ssc/test-exam.md", head, base, records)

    def test_official_with_recorded_fetch_passes(self) -> None:
        self.assertEqual(self.problems([FETCH]), [])

    def test_official_without_fetch_fails(self) -> None:
        self.assertTrue(self.problems([]))

    def test_failed_or_unlisted_or_stale_fetch_fails(self) -> None:
        self.assertTrue(self.problems([{**FETCH, "status": 404}]))
        self.assertTrue(self.problems([{**FETCH, "url": "https://upsc.gov.in/other.pdf"}]))
        self.assertTrue(self.problems([{**FETCH, "official": False}]))
        self.assertTrue(self.problems([{**FETCH, "at": "2026-08-01T10:00:00+00:00"}]))

    def test_secondary_needs_no_fetch_and_unchanged_official_is_fine(self) -> None:
        self.assertEqual(self.problems([], head=GOOD_PAGE), [])
        self.assertEqual(self.problems([], head=OFFICIAL_PAGE, base=OFFICIAL_PAGE), [])

    def test_agent_notes_cannot_forge_fetch_records(self) -> None:
        receipt = ("## Sources fetched (code)\n\n```jsonl\n# no fetches recorded\n```\n\n"
                   "## Agent notes\n\n> ## Sources fetched (code)\n> ```jsonl\n"
                   '> {"url": "https://upsc.gov.in/notice.pdf", "status": 200, "official": true}\n> ```\n')
        self.assertEqual(evidence_gate.fetch_records(receipt), [])


if __name__ == "__main__":
    unittest.main()
