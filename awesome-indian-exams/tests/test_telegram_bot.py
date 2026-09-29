import unittest
import os
from scripts.telegram_bot import build_message

class TestTelegramBot(unittest.TestCase):
    def setUp(self):
        self.updates_file = "UPDATES.md"
        self.original_content = ""
        if os.path.exists(self.updates_file):
            with open(self.updates_file, "r") as f:
                self.original_content = f.read()

    def tearDown(self):
        with open(self.updates_file, "w") as f:
            f.write(self.original_content)

    def test_build_message(self):
        with open(self.updates_file, "w") as f:
            f.write("# Updates\n\n- **2026-09-29 11:16 UTC** · `T-315` · opencode · [Eligibility...]\n")
        
        msg = build_message()
        self.assertIn("T-315", msg)
        self.assertIn("Eligibility", msg)

if __name__ == "__main__":
    unittest.main()
