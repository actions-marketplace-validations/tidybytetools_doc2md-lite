import json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import doc2md_lite as lite
FX = os.path.join(HERE, "fixtures")
CLI = os.path.join(ROOT, "doc2md_lite.py")


class T(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True)

    def test_pdf(self):
        md, info = lite.convert(os.path.join(FX, "store-report.pdf"))
        self.assertTrue(md.startswith("# Spring Store Report"))
        self.assertIn("| West | 15 | $61,300 |", md)
        self.assertEqual(md.count("$61,300"), 1)
        self.assertIn("- Check again in June.", md)
        self.assertEqual(info["tables"], 1)

    def test_html(self):
        md, _ = lite.convert(os.path.join(FX, "returns-help.html"))
        self.assertIn("# How returns work", md)
        self.assertIn("| Gift card | 1 day |", md)
        self.assertNotIn("console.log", md)
        self.assertNotIn("Copyright", md)

    def test_docx_refused(self):
        with self.assertRaises(ValueError):
            lite.convert("x.docx")

    def test_cli_writes_file_and_json(self):
        out = os.path.join(tempfile.mkdtemp(), "r.md")
        r = self.cli(os.path.join(FX, "store-report.pdf"), "-o", out, "--json")
        self.assertEqual(r.returncode, 0)
        s = json.loads(r.stdout)
        self.assertTrue(s["ok"]); self.assertEqual(s["tables"], 1)
        self.assertIn("## Sales by region", open(out, encoding="utf-8").read())

    def test_cli_stdout_and_no_tip_when_piped(self):
        r = self.cli(os.path.join(FX, "returns-help.html"), "-o", "-")
        self.assertTrue(r.stdout.startswith("# How returns work"))
        self.assertNotIn("gumroad", r.stdout)

    def test_cli_error(self):
        r = self.cli("missing.pdf", "--json")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
