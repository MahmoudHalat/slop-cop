# slop-cop Voice Profiles

The rewrite step needs a voice to write toward. This file holds seven of them. Each profile strips the AI tells a scan flags and replaces them with one consistent human register, so the output reads like a person chose the words on purpose.

## How the rewrite uses this

The workflow picks one profile per job. The user can name it, or the rewrite infers it from the `--audience` / `--genre` flags (see the map below). It then rewrites only the flagged spans in that voice and leaves clean prose alone.

Voice changes how something is said, never what it claims. Meaning, facts, numbers, quotes, and citations survive the rewrite unchanged. If a span carries a statistic or a source, the rewrite keeps both and restyles the words around them.

**Anti-sterilization rule:** subtracting tells without adding a voice creates new, equally detectable slop. Always rewrite toward a voice, never toward a vacuum.

## Picking a profile from the flags

| scan.py `--audience` | Default profile |
|---|---|
| casual | casual (or plain) |
| marketing | professional |
| academic | academic |
| encyclopedic | plain |
| technical | technical |
| fiction | match the manuscript's own voice; warm or casual if none is set |
| healthcare | warm |

A named `--genre` overrides the inference. When nothing is set, use **plain**.

## The shared source sentence

Every profile below rewrites the same sloppy line, so you can read the voices side by side:

> Our platform serves as a robust, seamless solution that leverages cutting-edge AI to revolutionize how teams navigate their workflows.

It carries no facts, numbers, or citations, so each rewrite is free to restyle it fully. When a real span does carry those, they stay fixed and only the wording moves.

---

## 1. plain (default)

- **Essence.** Neutral and clear, with no persona; the safe default when no voice is named.
- **Rhythm.** Mostly 10 to 18 words. Vary on purpose. Paragraphs of two to four sentences.
- **Vocabulary.** Reach for plain verbs: use, run, show, build, cut. Avoid leverage, robust, seamless, elevate, unlock.
- **Pairs with.** `--audience casual`, `encyclopedic`.
- **Rewrite.** Our platform uses AI to help teams manage their work.

---

## 2. professional

- **Essence.** Business-credible and crisp. Warm enough to trust, never stiff.
- **Rhythm.** 12 to 20 words, steady. One idea per sentence. Paragraphs under four sentences.
- **Vocabulary.** Reach for concrete outcome words: handle, support, speed up, reduce. Avoid synergy, best-in-class, empower, holistic.
- **Pairs with.** `--audience marketing`.
- **Rewrite.** Our platform brings AI into your team's workflow, so everyday work moves more smoothly.

---

## 3. casual

- **Essence.** Conversational, like explaining it to a colleague at their desk.
- **Rhythm.** Short. Often 6 to 14 words. Contractions throughout. Fragments are fine.
- **Vocabulary.** Reach for everyday words: get, make, run, easy, handy. Avoid utilize, facilitate, myriad, plethora.
- **Pairs with.** `--audience casual`, `fiction`.
- **Rewrite.** Our platform's got AI built in, so your team's workflow just runs easier.

---

## 4. technical

- **Essence.** Precise and active, with terms defined and no hand-waving.
- **Rhythm.** 14 to 24 words. Longer where precision needs it. One claim per sentence.
- **Vocabulary.** Reach for exact verbs: parse, route, validate, apply. Avoid seamless, powerful, robust, cutting-edge.
- **Pairs with.** `--audience technical`.
- **Rewrite.** The platform applies AI at each step of a team's workflow.

---

## 5. warm

- **Essence.** Human and first-person, a little self-aware about its own claims.
- **Rhythm.** Mixed. A short line lands next to a longer one. Asides are welcome.
- **Vocabulary.** Reach for people words: we, you, help, honestly, care. Avoid solution, ecosystem, journey, revolutionize.
- **Pairs with.** `--audience healthcare`, `fiction`. For healthcare, keep the warmth and drop the jokey asides.
- **Rewrite.** We built AI into the platform to make your team's workflow easier. Honestly, that's the whole goal.

---

## 6. blunt

- **Essence.** Direct and short, with the hedging stripped out.
- **Rhythm.** Clipped. Many sentences under 10 words. Declaratives, few qualifiers.
- **Vocabulary.** Reach for flat verbs: runs, does, cuts, saves. Avoid arguably, somewhat, in order to, it should be noted.
- **Pairs with.** `--audience marketing`, `casual`.
- **Rewrite.** Our platform runs your team's workflow on AI. Nothing fancy.

---

## 7. academic

- **Essence.** Formal register that hedges where the evidence is genuinely uncertain, and stays structured.
- **Rhythm.** 18 to 28 words. Subordinate clauses allowed. Each paragraph opens with its claim.
- **Vocabulary.** Reach for measured verbs: suggests, indicates, may, appears. Avoid game-changing, supercharge, unleash, dive in.
- **Pairs with.** `--audience academic`, `encyclopedic`.
- **Rewrite.** The platform employs AI methods that may streamline how teams carry out their workflows.
