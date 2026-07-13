# Rewrite doctrine

slop-cop rewrites by measuring, not by vibe. Every rewrite is a loop: scan the
draft, apply the fixes that are safe to automate, rewrite the rest by hand with a
target voice, then scan again to prove the result improved on both axes. The
scanner is the referee. If the second scan is not better than the first, the
rewrite is not done.

This file is the doctrine. The mechanics live in `scripts/scan.py`
(`--suggest`, `--apply-safe`); the voices live in `voice-profiles.md`.

## The three modes

slop-cop's default is **audit**: it scores and reports, and it does not touch the
text. The two rewrite modes are opt-in.

| Mode | What it does | When |
|---|---|---|
| **audit** (default) | Score both axes, list findings, change nothing. | Proactive QA before anything ships. |
| **rewrite** | Return a cleaned version plus a before/after score. Original is left intact. | "Clean this up", "rewrite this", "de-slop this". |
| **edit-in-place** | Apply targeted edits to a file with the Edit tool, preserving passages that are already human. | "Fix this file", "edit this in place". |

Audit stays the default because catching slop before it ships is the job. Rewrite
is a service you ask for.

## The rewrite pipeline

1. **Scan.** Run `python3 scripts/scan.py --suggest <file>` (or pipe text). You
   get before-scores for both axes, a list of deterministic `safe_fixes` (with
   character offsets), and a `judgment` worklist where each item carries an axis,
   a category, examples, and a specific instruction.

2. **Apply the safe fixes.** Run `python3 scripts/scan.py --apply-safe <file>`
   (add `--in-place` to write the file). These are meaning-preserving 1:1 swaps
   only: em dash to comma, "utilize" to "use", "in order to" to "to". They never
   touch text inside quotes or code, so a word being quoted as an example survives.
   You do not rewrite these by hand; the engine owns them.

3. **Rewrite the judgment items.** Read the worklist. For each item, apply its
   instruction in the target voice (see `voice-profiles.md`). This is where the
   real work is: splitting a 50-word sentence, naming a vague authority, killing a
   copula-avoidance ("serves as" to "is"), un-burying a claim, defining an acronym.
   Rewrite for BOTH axes at once. A sentence can read less like a bot and still be
   unreadable; fix both.

4. **Re-scan.** Run the plain scan on your rewrite. Report before and after for
   AI-Slop and Comprehension. If either axis did not improve, or either is still
   above LOW, do one more pass on what is still flagged. Two passes is the norm;
   a third means the draft needed a rethink, not a polish.

5. **Report.** Show the before/after verdicts and densities on both axes, and a
   short list of what changed. The re-scan is the proof. Do not claim a rewrite
   worked without it.

## Evidence-safe: what a rewrite must never change

Voice changes HOW something is said. It never changes WHAT is claimed.

- **Never alter facts, numbers, dates, names, or units.** "$40M Series B" stays
  "$40M Series B". If the draft says a thing happened in 2019, the rewrite says 2019.
- **Never touch quotations or citations.** Text inside quote marks is the source's
  words, not yours. Leave `(WO2025147762A1)` and `[Link]` exactly as they are.
- **Never invent a source to satisfy a "name the authority" instruction.** If the
  draft says "experts believe" and there is no source, cut the claim or flag it.
  Do not manufacture a citation.
- **Preserve meaning.** If you cannot rewrite a sentence without changing what it
  asserts, leave it and note why. A wrong sentence that reads clean is worse than
  a clunky sentence that is true.
- **Keep passages that are already human.** Do not rewrite text that scanned clean.
  Churn is not improvement.

## Anti-sterilization

Subtracting tells without adding voice creates new slop. Strip every flagged word
from a paragraph and you often get flat, sanded, characterless prose that a
different classifier flags just as fast. The scanner has a signature for exactly
this failure: `sanded_prose` (few vocabulary tells, many structural ones, low
burstiness). If your rewrite trips it, you subtracted without adding.

So always rewrite toward a voice, not toward a vacuum. Pick a profile before you
start. Fold specifics back in where you cut abstraction. Vary sentence length on
purpose. The goal is prose a person would want to read, not prose that merely
avoids the banned words.

## Rewrite versus patch

- **Patch** (spot-fix the listed items) when the draft scans LOW or MEDIUM and the
  findings are scattered: a few vocabulary swaps, one long sentence, a weak opener.
- **Full rewrite** (rebuild the passage) when the draft scans HIGH or CRITICAL, or
  when five or more vocabulary flags stack with three or more structural patterns
  and uniform rhythm. At that density you are not editing sentences, you are
  replacing a template. Patching a template just moves the tells around.

The combined recommendation from the scan tells you which. Follow it.
