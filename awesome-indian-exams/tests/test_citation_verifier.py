import unittest
from scripts.citation_verifier import verify_citation

class TestCitationVerification(unittest.TestCase):
    def test_valid_citations(self):
        corpus = ["sec1", "sec2", "sec3"]
        self.assertTrue(verify_citation("According to [sec1], the answer is X.", corpus))
        
    def test_invalid_citations(self):
        corpus = ["sec1", "sec2"]
        self.assertFalse(verify_citation("According to [sec3], the answer is X.", corpus))

if __name__ == '__main__':
    unittest.main()
