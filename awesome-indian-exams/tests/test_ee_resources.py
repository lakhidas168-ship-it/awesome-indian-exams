import unittest
import os

class TestEEResources(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(os.path.exists('resources/ee-free-resources.md'))

    def test_content_contains_nptel(self):
        with open('resources/ee-free-resources.md', 'r') as f:
            content = f.read()
            self.assertIn('NPTEL Courses mapped to GATE EE syllabus', content)
            self.assertIn('nptel.ac.in', content)

if __name__ == '__main__':
    unittest.main()
