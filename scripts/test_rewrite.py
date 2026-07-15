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


class ComprehensionFalsePositives(unittest.TestCase):
    def test_imperative_openers_not_named_entities(self):
        # Sentence-initial capitals (imperatives, greetings, sign-offs) must NOT
        # count as named entities — the bug that flagged readable marketing copy.
        text = ("Hi team. Get more done today. Reach your goals faster. "
                "Connect the tools you already use. See the difference. Best, the crew.")
        ents = dict(scan.find_named_entities(text, scan.split_sentences(text))["entities"])
        for w in ("Get", "Reach", "Connect", "See", "Hi", "Best"):
            self.assertNotIn(w, ents, f"{w} wrongly counted as a named entity")

    def test_single_brand_email_no_entity_bombing(self):
        text = ("With Acme, you can connect the tools you already use. "
                "Get insights that flag what needs attention. Reach a real support team any time. "
                "See it for yourself. Acme already runs the day-to-day for thousands of teams. "
                "Whether you work solo or lead a team, Acme takes the busywork off your plate. "
                "Book a free demo today and we will walk you through how it fits your work.")
        self.assertFalse(scan.named_entity_window_compound(text, scan.split_sentences(text)),
                         "one-brand readable email wrongly triggered entity-bombing")

    def test_readable_prose_not_high_comprehension(self):
        # Grade ~5, Flesch ~80 marketing prose must not escalate to HIGH/CRITICAL.
        text = ("Most owners track more moving parts than one person can handle. That costs time. "
                "Acme gives some of it back. Whether you work solo or lead a team, the platform "
                "takes the repetitive work off your plate. You spend less time on busywork and more "
                "on the decisions that grow the business. Book a demo and we will show you how it fits.")
        v = scan.analyze(text, audience="marketing")["comprehension"]["verdict"]
        self.assertIn(v, ("PASS", "LOW", "MEDIUM"), f"readable prose scored {v}")


class FingerprintTells(unittest.TestCase):
    def test_placeholders_caught(self):
        self.assertTrue(scan.find_placeholders("Hi [First Name], welcome to [Your Company]."))
        self.assertTrue(scan.find_placeholders("Draft dated 2025-XX-XX."))

    def test_placeholders_no_false_positives(self):
        # markdown checkbox, [sic], numeric citation, normal aside must NOT flag
        self.assertEqual(scan.find_placeholders("- [x] done\n- [ ] todo"), [])
        self.assertEqual(scan.find_placeholders("He wrote 'recieve' [sic] in the note."), [])
        self.assertEqual(scan.find_placeholders("As shown in [1] and [2]."), [])

    def test_citation_markup_caught(self):
        self.assertTrue(scan.find_citation_markup("great point oai_citation turn0search1 here"))
        self.assertEqual(scan.find_citation_markup("A normal sentence with a citation of sorts."), [])

    def test_ai_utm_caught(self):
        self.assertTrue(scan.find_ai_utm("see https://x.com/a?utm_source=chatgpt.com"))
        self.assertEqual(scan.find_ai_utm("see https://x.com/a?utm_source=newsletter"), [])

    def test_hashtag_stuffing(self):
        self.assertTrue(scan.find_hashtag_stuffing("post #AI #Tech #Innovation #Future #Growth #Web3")[0])
        self.assertFalse(scan.find_hashtag_stuffing("a normal post with #one tag")[0])

    def test_placeholder_raises_ai_slop_score(self):
        base = "We help teams move faster and keep everything in one place for the week ahead."
        with_ph = "Hi [First Name], " + base
        self.assertGreater(scan.analyze(with_ph)["density"], scan.analyze(base)["density"])

    def test_clean_human_text_still_passes(self):
        # a normal human sentence with brackets/hashtag must not get fingerprint-flagged
        r = scan.analyze("The report [see appendix] covers Q3. Follow #teamwork if curious.")
        self.assertEqual(r["high"]["unfilled_placeholders"], [])
        self.assertEqual(r["high"]["citation_markup"], [])


class UniformRhythm(unittest.TestCase):
    def test_flags_uniform_ai_rhythm(self):
        # Short, uniform-length sentences (low std) = AI tell.
        t = ("We help teams move faster. We build tools that just work. We ship new "
             "features weekly. We answer support quickly. We care about your success. "
             "We keep your data safe.")
        r = scan.analyze(t)
        self.assertTrue(r["high"]["uniform_rhythm"])
        self.assertIsNotNone(r["stats"]["sentence_length_std"])

    def test_does_not_flag_varied_human_rhythm(self):
        # Real human rhythm: a short beat next to long, winding sentences.
        t = ("The cat sat. Then, after a while, having weighed its options with the "
             "unhurried patience that only a well-fed animal can afford on a warm "
             "afternoon, it rose, stretched to twice its length, and padded off toward "
             "the door without a backward glance. Nobody minded. It was that kind of day.")
        r = scan.analyze(t)
        self.assertFalse(r["high"]["uniform_rhythm"])

    def test_needs_enough_sentences(self):
        r = scan.analyze("Short. Also short. Third one.")
        self.assertFalse(r["high"]["uniform_rhythm"])  # < 5 sentences → not scored


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
