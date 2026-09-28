import unittest
import subprocess
import sys
import tomllib
import os

class TestStalenessCLI(unittest.TestCase):
    def test_cli_output_is_toml(self):
        # Run the script with --suggest-tasks
        # Ensure we are in the root directory
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        result = subprocess.run(
            [sys.executable, "scripts/validate.py", "--suggest-tasks"],
            capture_output=True,
            text=True,
            env=env
        )
        # Check if it actually ran
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        self.assertEqual(result.returncode, 0)
        
        # Verify it parses as TOML
        try:
            data = tomllib.loads(result.stdout)
            self.assertIn("task", data)
        except Exception as e:
            self.fail(f"Output is not valid TOML: {e}\nOutput was:\n{result.stdout}")

if __name__ == "__main__":
    unittest.main()
