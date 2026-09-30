import unittest
import datetime as dt
from pathlib import Path
import sys

# Mocking the environment for the test
class MockReport:
    def __init__(self):
        self.errors = []
    def error(self, path, msg):
        self.errors.append(msg)

# We need to import the function to test.
# Since validate.py is a script, we can import it if we add the directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))
from validate import check_eligibility_entry

class TestEligibilityCheck(unittest.TestCase):
    def test_missing_source_url(self):
        rep = MockReport()
        # The function now checks for both next_notification_source_url and exam_window_source_url
        entry = {"next_notification": "2026-01-01", "exam_window": "2026-06-01"}
        check_eligibility_entry(entry, rep, Path("test.toml"), "test-exam")
        self.assertIn("exam test-exam: eligibility next_notification missing next_notification_source_url", rep.errors)
        self.assertIn("exam test-exam: eligibility exam_window missing exam_window_source_url", rep.errors)

    def test_valid_entry(self):
        rep = MockReport()
        entry = {
            "next_notification": "2026-01-01", 
            "next_notification_source_url": "https://example.com",
            "exam_window": "2026-06-01",
            "exam_window_source_url": "https://example.com"
        }
        check_eligibility_entry(entry, rep, Path("test.toml"), "test-exam")
        self.assertEqual(len(rep.errors), 0)

if __name__ == "__main__":
    unittest.main()
