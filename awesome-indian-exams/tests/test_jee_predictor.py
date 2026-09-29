import unittest
import subprocess
import os
import shutil
from tools.jee_predictor import predict

class TestJEEPredictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs("data/josaa", exist_ok=True)
        with open("data/josaa/2023.csv", "w") as f:
            f.write("Institute,Program,Category,ClosingRank\nIIT Bombay,CSE,OPEN,500\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree("data/josaa")

    def test_missing_data(self):
        self.assertEqual(predict(1000, "2000"), "Data for 2000 not found.")

    def test_safe_rank(self):
        result = predict(400, "2023")
        self.assertIn("Safe", result)

    def test_possible_rank(self):
        result = predict(450, "2023")
        self.assertIn("Possible", result)

    def test_reach_rank(self):
        result = predict(550, "2023")
        self.assertIn("Reach", result)

    def test_cli_output(self):
        result = subprocess.run(['python3', 'tools/jee_predictor.py', '400', '2023'], capture_output=True, text=True)
        self.assertIn("Safe", result.stdout)

    def test_invalid_rank(self):
        result = subprocess.run(['python3', 'tools/jee_predictor.py', 'abc', '2023'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()
