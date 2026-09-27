"""The open-data export: shape, page metadata, and that it covers the real registry."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_json  # noqa: E402

REGISTRY = """
[[family]]
id = "ssc"
title = "SSC"

[[module]]
id = "reasoning"
title = "Reasoning"

[[module]]
id = "unused"
title = "Unused"

[[exam]]
id = "ssc-cgl"
name = "SSC CGL"
family = "ssc"
body = "Staff Selection Commission"
official_site = "https://ssc.gov.in"
modules = ["reasoning"]

[[exam]]
id = "ssc-chsl"
name = "SSC CHSL"
family = "ssc"
body = "Staff Selection Commission"
official_site = "https://ssc.gov.in"
modules = ["reasoning"]
"""

PAGE = """---
title: SSC CGL
exam_id: ssc-cgl
conducting_body: Staff Selection Commission
official_site: https://ssc.gov.in
cycle: CGL 2026
last_verified: 2026-09-27
verification: secondary
---

# SSC CGL
"""


class ExportTest(unittest.TestCase):
    def test_shape_and_page_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "registry").mkdir()
            (root / "registry" / "exams.toml").write_text(REGISTRY)
            (root / "exams" / "ssc").mkdir(parents=True)
            (root / "exams" / "ssc" / "ssc-cgl.md").write_text(PAGE)
            (root / "modules").mkdir()
            (root / "modules" / "reasoning.md").write_text("# Reasoning\n")
            data = export_json.build(root)
        by_id = {e["id"]: e for e in data["exams"]}
        self.assertEqual(set(by_id), {"ssc-cgl", "ssc-chsl"})
        cgl = by_id["ssc-cgl"]
        self.assertEqual(cgl["page"]["path"], "exams/ssc/ssc-cgl.md")
        self.assertEqual(cgl["page"]["verification"], "secondary")
        self.assertEqual(cgl["page"]["cycle"], "CGL 2026")
        self.assertIsNone(by_id["ssc-chsl"]["page"])
        mods = {m["id"]: m for m in data["modules"]}
        self.assertEqual(mods["reasoning"]["exams"], ["ssc-cgl", "ssc-chsl"])
        self.assertEqual(mods["reasoning"]["page"], "modules/reasoning.md")
        self.assertNotIn("unused", mods)   # neither used by an exam nor written as a page
        json.dumps(data)                    # serialisable

    def test_real_registry(self):
        data = export_json.build(ROOT)
        ids = [e["id"] for e in data["exams"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 100)
        for e in data["exams"]:
            if e["page"]:
                self.assertTrue((ROOT / e["page"]["path"]).exists(), e["id"])
                self.assertIn(e["page"].get("verification"), ("official", "secondary", "unverified"), e["id"])

    def test_cli_writes_file(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "data" / "exams.json"
            self.assertEqual(export_json.main(["--out", str(out)]), 0)
            self.assertIn("exams", json.loads(out.read_text()))


if __name__ == "__main__":
    unittest.main()
