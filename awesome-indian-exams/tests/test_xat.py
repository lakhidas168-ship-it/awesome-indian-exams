import unittest
import os

class TestXATValidation(unittest.TestCase):
    def test_xat_file_exists(self):
        self.assertTrue(os.path.exists('exams/management/xat.md'))

if __name__ == '__main__':
    unittest.main()
