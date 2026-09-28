import unittest
import datetime as dt
import sys
from pathlib import Path
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate

class TestOverlapMap(unittest.TestCase):
    def test_overlap_map_generation(self):
        # Setup minimal registry
        reg = {
            "family": {
                "f1": {"title": "Family 1"},
                "f2": {"title": "Family 2"}
            },
            "module": {
                "m1": {"title": "Module 1"},
                "m2": {"title": "Module 2"}
            },
            "exam": {
                "e1": {"name": "Exam 1", "family": "f1", "modules": ["m1", "m2"]},
                "e2": {"name": "Exam 2", "family": "f1", "modules": ["m1"]},
                "e3": {"name": "Exam 3", "family": "f2", "modules": ["m2"]}
            }
        }
        
        # Mock root
        tmp = Path(tempfile.mkdtemp())
        (tmp / "modules").mkdir()
        (tmp / "modules" / "m1.md").write_text("---", encoding="utf-8")
        (tmp / "modules" / "m2.md").write_text("---", encoding="utf-8")
        
        output = validate.render_overlap(tmp, reg)
        
        # Verify 'Start here' sections
        self.assertIn("## Start here: Family 1", output)
        self.assertIn("- **Module 1** (2 exams)", output)
        self.assertIn("- **Module 2** (1 exams)", output)
        
        self.assertIn("## Start here: Family 2", output)
        self.assertIn("- **Module 2** (1 exams)", output)
        
        shutil.rmtree(tmp)

if __name__ == "__main__":
    unittest.main()
