"""Study tools: flashcard decks are well formed and officially sourced, the tools' script parses, and the data
file the tools read (data.js) loads."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_json  # noqa: E402
import validate  # noqa: E402

NODE = shutil.which("node")


class DeckTest(unittest.TestCase):
    def test_decks_are_well_formed_and_sourced(self):
        official = validate.load_official_hosts(ROOT)
        decks = sorted((ROOT / "data" / "flashcards").glob("*.json"))
        self.assertTrue(decks, "at least one deck")
        seen_decks = set()
        for path in decks:
            deck = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(deck["id"], path.stem, path.name)
            self.assertNotIn(deck["id"], seen_decks)
            seen_decks.add(deck["id"])
            self.assertTrue(deck.get("title"), path.name)
            host = urlparse(deck["source"]["url"]).netloc
            self.assertTrue(validate.host_matches(host, official), f"{path.name}: source host {host} is not official")
            ids = [c["id"] for c in deck["cards"]]
            self.assertEqual(len(ids), len(set(ids)), f"{path.name}: duplicate card ids")
            for c in deck["cards"]:
                self.assertTrue(c["front"].strip() and c["back"].strip(), f"{path.name}: empty card {c['id']}")

    def test_tool_pages_have_their_mount_points(self):
        for page, mount in (("study-planner.md", "aie-planner"), ("flashcards.md", "aie-flashcards"),
                            ("score-calculator.md", "aie-calculator")):
            self.assertIn(f'id="{mount}"', (ROOT / "tools" / page).read_text(encoding="utf-8"), page)


@unittest.skipUnless(NODE, "node is not installed")
class ScriptTest(unittest.TestCase):
    def test_tools_js_parses(self):
        subprocess.run([NODE, "--check", str(ROOT / "tools" / "tools.js")], check=True)

    def test_data_js_loads_with_exams_and_decks(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "data.js"
            self.assertEqual(export_json.main(["--js", str(out)]), 0)
            probe = ("global.window = {}; require(process.argv[1]);"
                     "const d = window.AIE_DATA; console.log(JSON.stringify("
                     "{exams: d.exams.exams.length, decks: Object.keys(d.decks).length}));")
            res = subprocess.run([NODE, "-e", probe, str(out)], check=True, capture_output=True, text=True)
            counts = json.loads(res.stdout)
            self.assertGreaterEqual(counts["exams"], 100)
            self.assertGreaterEqual(counts["decks"], 1)


if __name__ == "__main__":
    unittest.main()
