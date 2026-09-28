"""Growth features: installable app, link previews, SEO descriptions, the daily question and the Hindi start page."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

import export_json  # noqa: E402

NODE = shutil.which("node")
# The website files live at the repository root; a copy of the content folder alone skips those checks.
HAS_SITE = (REPO / "overrides" / "main.html").exists() and (REPO / "hooks" / "seo.py").exists()


class AppAndPreviewTest(unittest.TestCase):
    def test_manifest_and_icons(self):
        m = json.loads((ROOT / "manifest.webmanifest").read_text())
        for key in ("name", "short_name", "start_url", "display", "icons"):
            self.assertIn(key, m)
        sizes = {i["sizes"] for i in m["icons"]}
        self.assertTrue({"192x192", "512x512"} <= sizes)
        for icon in m["icons"]:
            self.assertTrue((ROOT / icon["src"]).exists(), icon["src"])
        self.assertTrue((ROOT / "assets" / "social-card.png").exists())
        self.assertTrue((ROOT / "assets" / "qr-site.svg").exists())

    @unittest.skipUnless(HAS_SITE, "website files not in this checkout")
    def test_service_worker_has_build_stamp(self):
        sw = (ROOT / "sw.js").read_text()
        self.assertIn('"__BUILD__"', sw)   # replaced by the commit in pages.yml
        self.assertIn("__BUILD__", (REPO / ".github" / "workflows" / "pages.yml").read_text())

    @unittest.skipUnless(HAS_SITE, "website files not in this checkout")
    def test_head_template_links_manifest_and_previews(self):
        html = (REPO / "overrides" / "main.html").read_text()
        for needle in ("manifest.webmanifest", 'property="og:title"', 'property="og:description"',
                       'property="og:image"', "social-card.png"):
            self.assertIn(needle, html)

    @unittest.skipUnless(HAS_SITE, "website files not in this checkout")
    def test_seo_descriptions(self):
        spec = importlib.util.spec_from_file_location("seo", REPO / "hooks" / "seo.py")
        seo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(seo)
        text = seo.describe("SSC CGL", {"exam_id": "ssc-cgl", "cycle": "CGL 2026",
                                        "conducting_body": "Staff Selection Commission", "verification": "secondary"})
        self.assertIn("SSC CGL", text)
        self.assertIn("CGL 2026", text)
        self.assertIn("Staff Selection Commission", text)
        self.assertIn("confirm on the official site", text)
        self.assertIn("Prepare once", seo.describe("Reasoning", {"module_id": "reasoning"}))
        self.assertEqual(seo.describe("About", {}), "")

    def test_pages_exist(self):
        self.assertIn('id="aie-daily"', (ROOT / "tools" / "daily.md").read_text())
        self.assertIn("qr-site.svg", (ROOT / "tools" / "poster.md").read_text())
        hi = (ROOT / "hi" / "index.md").read_text()
        self.assertIn("शुरू करें", hi)
        self.assertIn("../tools/daily.md", hi)


@unittest.skipUnless(NODE, "node is not installed")
class DailyQuestionTest(unittest.TestCase):
    PROBE = r"""
global.window = {}; global.navigator = {};
global.location = { protocol: "file:", href: "file:///x/index.html", pathname: "/x/index.html" };
global.document = { currentScript: null, readyState: "complete", querySelector: () => null, getElementById: () => null };
require(process.argv[1]);   // data.js
require(process.argv[2]);   // tools.js
const t = window.AIE_TOOLS, data = window.AIE_DATA;
const n = data.questions.length + Object.values(data.decks).reduce((a, d) => a + d.cards.length, 0);
const seen = new Set(); let ok = true;
for (let day = 1; day <= n; day++) {
  const a = t.dailyItem(data, day), b = t.dailyItem(data, day);
  if (JSON.stringify(a) !== JSON.stringify(b)) ok = false;           // same question for everyone on a day
  if (!a.options.includes(a.answer)) ok = false;                      // the answer is always an option
  seen.add(a.question);
}
console.log(JSON.stringify({ ok, n, unique: seen.size }));
"""

    def test_daily_question_is_stable_and_cycles_without_repeats(self):
        with tempfile.TemporaryDirectory() as d:
            data_js = Path(d) / "data.js"
            self.assertEqual(export_json.main(["--js", str(data_js)]), 0)
            res = subprocess.run([NODE, "-e", self.PROBE, str(data_js), str(ROOT / "tools" / "tools.js")],
                                 check=True, capture_output=True, text=True)
            out = json.loads(res.stdout.strip().splitlines()[-1])
            self.assertTrue(out["ok"])
            self.assertEqual(out["unique"], out["n"])   # every question gets its day before any repeats


if __name__ == "__main__":
    unittest.main()
