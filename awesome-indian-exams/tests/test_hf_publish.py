"""The Hugging Face dataset folder is built correctly without any network or token."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import hf_publish  # noqa: E402


class DatasetFolderTest(unittest.TestCase):
    def test_build_folder(self):
        with tempfile.TemporaryDirectory() as d:
            files = hf_publish.build_folder(Path(d))
            self.assertIn("exams.json", files)
            self.assertIn("README.md", files)
            self.assertTrue(any(f.startswith("decks/") for f in files))
            card = (Path(d) / "README.md").read_text()
            self.assertTrue(card.startswith("---\nlicense: cc-by-sa-4.0"))
            self.assertIn(hf_publish.REPO, card)
            self.assertGreaterEqual(len(json.loads((Path(d) / "exams.json").read_text())["exams"]), 100)

    def test_check_without_token_fails_clearly(self):
        import os
        old = os.environ.pop("HF_TOKEN", None)
        try:
            with self.assertRaises(SystemExit) as cm:
                hf_publish.main(["--check"])
            self.assertIn("HF_TOKEN", str(cm.exception))
        finally:
            if old is not None:
                os.environ["HF_TOKEN"] = old


if __name__ == "__main__":
    unittest.main()
