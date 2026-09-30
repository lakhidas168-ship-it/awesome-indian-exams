import unittest
import sys
from pathlib import Path

# Add the scripts directory to the start of path to import local validate
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate

class TestStateAEJERegistry(unittest.TestCase):
    def test_state_ae_je_registry_validation(self):
        # Mock registry data for state-ae-je
        registry_exam = {
            "id": "state-ae-je",
            "name": "State AE / JE (Electrical)",
            "family": "engineering",
            "body": "State PSCs and state power utilities",
            "official_site": "https://apsc.nic.in",
            "modules": ["ee-core", "engineering-mathematics", "general-awareness"]
        }
        
        # Mock official domains
        official_domains = ("apsc.nic.in", "ssc.gov.in")
        
        # Simulate the check
        site = registry_exam.get("official_site", "")
        is_valid = not site or validate.host_matches(validate.urlparse(site).netloc, official_domains)
        
        self.assertTrue(is_valid, "State AE/JE official site should be valid")

    def test_state_ae_je_invalid_site(self):
        # Mock registry data for state-ae-je with invalid site
        registry_exam = {
            "id": "state-ae-je",
            "official_site": "https://fake-site.com"
        }
        
        # Mock official domains
        official_domains = ("apsc.nic.in", "ssc.gov.in")
        
        # Simulate the check
        site = registry_exam.get("official_site", "")
        is_valid = not site or validate.host_matches(validate.urlparse(site).netloc, official_domains)
        
        self.assertFalse(is_valid, "State AE/JE invalid site should be rejected")

if __name__ == "__main__":
    unittest.main()
