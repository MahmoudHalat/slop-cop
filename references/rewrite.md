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

## Anti-sterilization: the concreteness rule

Subtracting tells without adding anything creates new slop. Strip every flagged
word from a paragraph and you usually get flat, sanded, characterless prose that a
different classifier flags just as fast. The scanner has a signature for it:
`sanded_prose` (few vocabulary tells, many structural ones, low burstiness). If
your rewrite trips it, or its burstiness sits below about 0.5, you subtracted
without adding, and you are not done.

The fix that matters most is concreteness. When you cut an abstraction, do not
replace it with a warmer abstraction. Replace it with a specific: a number, a name,
a scene, one small true detail. This is the single biggest difference between a
rewrite that reads human and one that reads like clean corporate filler.

- "takes the repetitive work off your plate" → "copies the numbers between your
  tools so you don't have to"
- "empowers teams to succeed" → "when something breaks at 2am, you reach a person,
  not a ticket queue"
- "drives meaningful results" → name the actual task it does: "flags the one number
  in the report that moved"

Concreteness comes from scenes, specific nouns, and plain description of what the
thing actually does. It does NOT come from inventing data. Evidence-safe still
holds: if you don't have a real number, don't manufacture one to sound specific. A
true scene beats a fake statistic. Generic praise is abstraction in a nicer coat.
If a sentence would be true of any product in the category, it is not a rewrite yet.
Make it true of this one, honestly.

**Concrete AND complete.** Concreteness changes HOW each point is said. It never
lets you drop a point or add one. Before you finish, check the rewrite against the
original: is every claim, feature, audience, and offer still there, and did you
invent nothing that wasn't? Getting vivid by quietly dropping the "works for solo
or team" line, or by inventing a capability to make a scene land, trades one kind
of slop for another. The strongest rewrites in the wild keep every element of the
brief and still read human. Match that: full coverage, zero invention, concrete
throughout.

The rest, in order of leverage:

- **Vary the rhythm on purpose.** A short sentence after two long ones. A fragment
  where it lands. Uniform sentence length is the loudest structural tell.
- **Open with something real** — a question, a concrete scene — not a mission
  statement.
- **Break the parallel-clause reflex.** "You connect. You get. You reach." is
  corporate. Turn at least one item into a sentence with texture.
- **Pick the warmest voice that fits.** Default to warm or conversational. Reach for
  "professional" only when the context truly needs distance. Stiffness is a failure
  mode, not a safe default.

## Rewrite versus patch

- **Patch** (spot-fix the listed items) when the draft scans LOW or MEDIUM and the
  findings are scattered: a few vocabulary swaps, one long sentence, a weak opener.
- **Full rewrite** (rebuild the passage) when the draft scans HIGH or CRITICAL, or
  when five or more vocabulary flags stack with three or more structural patterns
  and uniform rhythm. At that density you are not editing sentences, you are
  replacing a template. Patching a template just moves the tells around.

The combined recommendation from the scan tells you which. Follow it.
