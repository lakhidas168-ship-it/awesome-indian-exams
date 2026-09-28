import unittest
from scripts.translate_page import verify_integrity

class TestTranslation(unittest.TestCase):
    def test_integrity_pass(self):
        original = "The exam is on 2023-12-01. Visit https://example.com for details."
        translated = "परीक्षा 2023-12-01 को है। विवरण के लिए https://example.com पर जाएं।"
        self.assertTrue(verify_integrity(original, translated))

    def test_integrity_fail(self):
        original = "The exam is on 2023-12-01."
        translated = "परीक्षा 2024-01-01 को है।"
        self.assertFalse(verify_integrity(original, translated))

if __name__ == '__main__':
    unittest.main()
