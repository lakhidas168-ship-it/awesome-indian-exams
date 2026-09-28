import unittest
import sys
import os

# Add the root directory to sys.path to import scripts
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.normalization import calculate_ssc_normalized_score

class TestNormalization(unittest.TestCase):
    def test_ssc_formula(self):
        # Example values
        m_ij = 80
        m_ti = 100
        m_iq = 60
        m_gm = 70
        m_ga = 90
        m_qa = 70
        
        # M_ij = (70 - 90) / (100 - 60) * (80 - 60) + 70
        # M_ij = (-20) / (40) * (20) + 70
        # M_ij = -0.5 * 20 + 70
        # M_ij = -10 + 70 = 60
        
        result = calculate_ssc_normalized_score(m_ij, m_ti, m_iq, m_gm, m_ga, m_qa)
        self.assertEqual(result, 60.0)

if __name__ == '__main__':
    unittest.main()
