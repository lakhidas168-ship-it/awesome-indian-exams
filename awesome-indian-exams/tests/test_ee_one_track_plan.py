import unittest
from pathlib import Path
import sys

# Mocking the environment for testing
class TestEEOneTrackPlan(unittest.TestCase):
    def test_file_exists(self):
        path = Path("resources/ee-one-track-plan.md")
        self.assertTrue(path.exists(), "resources/ee-one-track-plan.md should exist")

    def test_content_contains_table(self):
        path = Path("resources/ee-one-track-plan.md")
        content = path.read_text()
        self.assertIn("| Subject | GATE EE |", content)
        self.assertIn("| Exam | Extra Topics Added |", content)

if __name__ == "__main__":
    unittest.main()
