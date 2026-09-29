import unittest
from pathlib import Path
from scripts.validate import Report, check_eligibility_entry

class TestEligibility(unittest.TestCase):
    def test_eligibility_missing_source(self):
        rep = Report(Path("."))
        entry = {"age_limit": "21-30"}
        check_eligibility_entry(entry, rep, Path("registry/exams.toml"))
        self.assertTrue(any("missing official_source_url" in err for err in rep.errors))

    def test_eligibility_with_source(self):
        rep = Report(Path("."))
        entry = {"age_limit": "21-30", "official_source_url": "https://example.com"}
        check_eligibility_entry(entry, rep, Path("registry/exams.toml"))
        self.assertFalse(any("missing official_source_url" in err for err in rep.errors))

if __name__ == '__main__':
    unittest.main()
