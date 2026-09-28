import unittest
import subprocess
import os

class TestRSS(unittest.TestCase):
    def test_rss_script_exists(self):
        self.assertTrue(os.path.exists("scripts/generate_feed.py"))

    def test_rss_output_valid(self):
        # Run the script and check if it produces valid XML
        result = subprocess.run(["python3", "scripts/generate_feed.py"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("<rss version=\"2.0\">", result.stdout)
        self.assertIn("<channel>", result.stdout)

if __name__ == "__main__":
    unittest.main()
