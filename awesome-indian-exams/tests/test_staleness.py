import unittest
from pathlib import Path
import datetime as dt
import sys
import tomllib

# Add the scripts directory to the start of path so we can import local validate
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate

class TestStalenessReport(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.today = dt.date(2024, 1, 1)

    def test_suggest_tasks_output(self):
        # Create dummy pages
        pages = [
            (Path("exams/stale.md"), {
                "title": "Stale Exam",
                "last_verified": "2023-01-01",
                "official_site": "https://example.com"
            }),
            (Path("exams/secondary.md"), {
                "title": "Secondary Exam",
                "last_verified": "2024-01-01",
                "official_site": "https://example.com"
            })
        ]
        
        output = validate.suggest_tasks(pages, self.today)
        
        # Check if output is valid TOML
        try:
            data = tomllib.loads(output)
            self.assertIn("task", data)
            tasks = data["task"]
            self.assertTrue(any(t["id"] == "T-STALE" for t in tasks))
            self.assertTrue(any(t["id"] == "T-SEC" for t in tasks))
        except Exception as e:
            self.fail(f"Output is not valid TOML: {e}")

if __name__ == "__main__":
    unittest.main()
