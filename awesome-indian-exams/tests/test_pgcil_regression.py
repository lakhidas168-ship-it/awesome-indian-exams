import unittest
from pathlib import Path
from scripts.validate import Report, check_exam_page

class TestPGCILValidation(unittest.TestCase):
    def test_pgcil_validation_regression(self):
        # This test ensures that the validation logic for PGCIL Diploma Trainee EE
        # (or similar exams) is correctly enforced by the content gate.
        # We simulate a scenario where the exam page is missing a required section.
        
        rep = Report(Path("."))
        # Mocking a path that doesn't exist, but we will provide the content
        # Actually, check_exam_page reads the file. Let's create a temporary file.
        
        path = Path("exams/engineering/pgcil-dt-ee.md")
        content = """---
title: PGCIL Diploma Trainee (Electrical)
exam_id: pgcil-dt-ee
conducting_body: Power Grid Corporation of India Limited
official_site: https://www.powergrid.in
cycle: Annual
last_verified: 2026-09-28
verification: official
---

# PGCIL Diploma Trainee (Electrical)

## At a glance

## Official sources

## Exam pattern

## Syllabus

# Missing Free resources section
"""
        # We need to make sure the file exists for the test
        with open(path, "w") as f:
            f.write(content)
            
        try:
            # We need to mock the registry and official hosts
            reg = {"family": {"engineering": {}}, "exam": {"pgcil-dt-ee": {"family": "engineering"}}}
            official = ("powergrid.in",)
            import datetime as dt
            
            check_exam_page(path, Path("."), official, reg, dt.date(2026, 9, 29), rep)
            
            # Check if the error for missing section was caught
            self.assertTrue(any("missing section '## Free resources'" in err for err in rep.errors), 
                            f"Errors found: {rep.errors}")
        finally:
            if path.exists():
                path.unlink()

if __name__ == '__main__':
    unittest.main()
