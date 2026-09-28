import unittest
import sys
from pathlib import Path

# Add the scripts directory to the path to import validate
sys.path.append(str(Path(__file__).resolve().parents[1] / "scripts"))
import validate

class TestRegistryValidation(unittest.TestCase):
    def test_official_site_mismatch(self):
        # Mock registry data
        registry_exam = {
            "id": "test-exam",
            "official_site": "https://wrong.com"
        }
        official_domains = ("correct.com",)
        
        # Simulate the check
        site = registry_exam.get("official_site", "")
        is_valid = not site or validate.host_matches(validate.urlparse(site).netloc, official_domains)
        
        self.assertFalse(is_valid, "Mismatch should be rejected")

    def test_official_site_match(self):
        registry_exam = {
            "id": "test-exam",
            "official_site": "https://correct.com"
        }
        official_domains = ("correct.com",)
        
        site = registry_exam.get("official_site", "")
        is_valid = not site or validate.host_matches(validate.urlparse(site).netloc, official_domains)
        
        self.assertTrue(is_valid, "Match should be accepted")

    def test_official_site_blank(self):
        registry_exam = {
            "id": "test-exam",
            "official_site": ""
        }
        official_domains = ("correct.com",)
        
        site = registry_exam.get("official_site", "")
        is_valid = not site or validate.host_matches(validate.urlparse(site).netloc, official_domains)
        
        self.assertTrue(is_valid, "Blank site should be accepted")

if __name__ == "__main__":
    unittest.main()
