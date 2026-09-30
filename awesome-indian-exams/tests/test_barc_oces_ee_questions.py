import unittest
import json
import os
from pathlib import Path
import sys

# Add the root directory to sys.path so we can import scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.validate import question_problems

class TestBARCOCESEEQuestionValidation(unittest.TestCase):
    def setUp(self):
        self.reg = {"exam": {"barc-oces-ee": {"id": "barc-oces-ee"}}}
        self.path = Path("exams/engineering/barc-oces-ee.json")

    def test_valid_question(self):
        q = {
            "id": "barc-oces-ee",
            "exams": ["barc-oces-ee"],
            "subject": "Electrical Engineering",
            "question": "What is the unit of resistance?",
            "options": ["Volts", "Amperes", "Ohms", "Watts"],
            "answer": "Ohms",
            "solution": "Resistance is measured in Ohms.",
            "author": "Hive",
            "license": "CC-BY-4.0",
            "source": "original"
        }
        problems = question_problems(q, self.path, self.reg)
        self.assertEqual(problems, [])

    def test_invalid_source(self):
        q = {
            "id": "barc-oces-ee",
            "exams": ["barc-oces-ee"],
            "subject": "Electrical Engineering",
            "question": "What is the unit of resistance?",
            "options": ["Volts", "Amperes", "Ohms", "Watts"],
            "answer": "Ohms",
            "solution": "Resistance is measured in Ohms.",
            "author": "Hive",
            "license": "CC-BY-4.0",
            "source": "copied"
        }
        problems = question_problems(q, self.path, self.reg)
        self.assertIn("source must be 'original' (copied questions are not accepted); got 'copied'", problems)

    def test_missing_field(self):
        q = {
            "id": "barc-oces-ee",
            "exams": ["barc-oces-ee"],
            "subject": "Electrical Engineering",
            "question": "What is the unit of resistance?",
            "options": ["Volts", "Amperes", "Ohms", "Watts"],
            "answer": "Ohms",
            "solution": "Resistance is measured in Ohms.",
            "author": "Hive",
            "license": "CC-BY-4.0"
            # Missing source
        }
        problems = question_problems(q, self.path, self.reg)
        self.assertTrue(any("missing or empty" in p for p in problems))

if __name__ == '__main__':
    unittest.main()
