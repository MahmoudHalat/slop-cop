#!/usr/bin/env python3
"""
Tests for slop-cop's deterministic rewrite layer (safe fixes + suggestions).

Run:  python3 scripts/test_rewrite.py         (from repo root)
      python3 test_rewrite.py                 (from scripts/)

Zero dependencies (stdlib unittest). These lock the meaning-preserving
guarantees of the safe-fix engine so the rewrite workflow can trust it.
"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.join(HERE, "scan.py")
sys.path.insert(0, HERE)
import scan  # noqa: E402


class SafeFixEngine(unittest.TestCase):
    def test_em_dash_becomes_comma(self):
        out, _ = scan.apply_safe_fixes("It was fast—very fast.")
        self.assertNotIn("—", out)
        self.assertEqual(out, "It was fast, very fast.")

    def test_utilize_family_case_preserving(self):
        out, _ = scan.apply_safe_fixes("We utilize this. Utilize that. UTILIZE it.")
        self.assertIn("use this", out)
        self.assertIn("Use that", out)
        self.assertIn("USE it", out)

    def test_wordy_connectives(self):
        # Only unarguable swaps are "safe". Quantifier phrases like "a number of"
        # are deliberately NOT here: "a number of us" → "several of us" (keep "of"),
        # "a number of people" → "several people" (drop "of"). That pronoun edge
        # would change grammar, so it belongs to the judgment layer, not safe fixes.
        out, _ = scan.apply_safe_fixes(
            "In order to win, and due to the fact that we tried, we left."
        )
        self.assertIn("To win", out)
        self.assertIn("because we tried", out)

    def test_quotes_are_protected(self):
        # The "delve" case: a flagged word quoted as an EXAMPLE must survive.
        text = 'The tool flags "utilize" and "in order to" as tells.'
        out, fixes = scan.apply_safe_fixes(text)
        self.assertEqual(out, text)
        self.assertEqual(fixes, [])

    def test_curly_quotes_protected(self):
        text = "It flags “utilize” as a tell."
        out, _ = scan.apply_safe_fixes(text)
        self.assertIn("“utilize”", out)

    def test_code_spans_protected(self):
        out, _ = scan.apply_safe_fixes("Call `utilize()` and see in order to debug.")
        self.assertIn("`utilize()`", out)
        self.assertIn("to debug", out)  # outside code still fixed

    def test_idempotent(self):
        once, _ = scan.apply_safe_fixes("We utilize it in order to win—now.")
        twice, f2 = scan.apply_safe_fixes(once)
        self.assertEqual(once, twice)
        self.assertEqual(f2, [])

    def test_never_raises_density(self):
        text = ("We utilize a robust solution in order to deliver value, and due to "
                "the fact that synergy matters—we win.")
        before = scan.analyze(text)["density"]
        fixed, _ = scan.apply_safe_fixes(text)
        after = scan.analyze(fixed)["density"]
        self.assertLessEqual(after, before)

    def test_plain_text_untouched(self):
        text = "The cat sat on the mat. It was a warm afternoon."
        out, fixes = scan.apply_safe_fixes(text)
        self.assertEqual(out, text)
        self.assertEqual(fixes, [])

    def test_fix_records_have_offsets(self):
        text = "We utilize it."
        fixes = scan.find_safe_fixes(text)
        self.assertTrue(fixes)
        f = fixes[0]
        for k in ("start", "end", "original", "replacement", "reason"):
            self.assertIn(k, f)
        self.assertEqual(text[f["start"]:f["end"]], f["original"])


class Suggestions(unittest.TestCase):
    def test_schema(self):
        text = "We utilize this—really. Experts believe it is a game changer."
        sug = scan.build_suggestions(text, scan.analyze(text))
        self.assertIn("scores", sug)
        self.assertIn("safe_fixes", sug)
        self.assertIn("judgment", sug)
        self.assertIn("ai_slop", sug["scores"])
        self.assertIn("comprehension", sug["scores"])

    def test_judgment_items_carry_guidance(self):
        text = "Experts believe this is a testament to our robust, seamless synergy."
        sug = scan.build_suggestions(text, scan.analyze(text))
        for item in sug["judgment"]:
            self.assertIn("guidance", item)
            self.assertIn("axis", item)
            self.assertTrue(item["guidance"])


class CLI(unittest.TestCase):
    def _run(self, args, stdin):
        return subprocess.run([sys.executable, SCAN, *args], input=stdin,
                              capture_output=True, text=True)

    def test_apply_safe_stdout(self):
        r = self._run(["--apply-safe"], "We utilize it in order to win.")
        self.assertIn("use it to win", r.stdout)
        self.assertEqual(r.returncode, 0)

    def test_suggest_emits_json(self):
        r = self._run(["--suggest"], "We utilize this—really.")
        data = json.loads(r.stdout)
        self.assertIn("safe_fixes", data)
        self.assertIn("scores", data)

    def test_audit_mode_unchanged(self):
        # Default audit output still renders the dual-axis header (no regression).
        r = self._run([], "This is a perfectly ordinary sentence about cats.")
        self.assertIn("SLOP-COP DUAL-AXIS SCAN", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
