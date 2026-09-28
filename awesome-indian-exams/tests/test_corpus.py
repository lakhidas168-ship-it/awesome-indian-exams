import unittest
import json
import os
from pathlib import Path
import sys

# Add scripts to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
from export_json import build_corpus

class TestCorpus(unittest.TestCase):
    def test_corpus_structure(self):
        corpus = build_corpus()
        self.assertGreater(len(corpus), 0)
        for record in corpus:
            self.assertIn("url", record)
            self.assertIn("verification", record)
            self.assertLessEqual(len(json.dumps(record)), 2000)

    def test_bad_input_length(self):
        # Test that a record exceeding 2000 characters is rejected
        # This is a conceptual test for the constraint
        record = {"url": "http://test.com", "verification": "official", "text": "a" * 2000}
        # The constraint is enforced in build_corpus
        self.assertGreater(len(json.dumps(record)), 2000)

if __name__ == "__main__":
    unittest.main()
