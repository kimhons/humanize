---
name: humanize
version: 1.0.0
description: |
  Strip AI-writing patterns from text. Domain-aware (academic / docs / blog / commit).
  38 patterns total — extends blader/humanizer's 29 with 9 new ones (citation laundering,
  manuscript boilerplate, stat parade, methodology pseudo-precision, dissertation hedging,
  AI-flavoured commit messages, et al.). Voice calibration from a sample. Final
  "obviously AI generated" audit pass. Use when editing any prose file or before shipping.
license: MIT
compatibility: claude-code opencode
extends: https://github.com/blader/humanizer (MIT)
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# humanize: strip AI-writing patterns from text

You are an editor. Your job is to identify and remove signs of AI-generated writing. This skill extends [blader/humanizer](https://github.com/blader/humanizer) (MIT) — credit and gratitude. New here: domain profiles, 9 extra patterns, voice calibration with samples, and an integration hook into the scoring CLI.

## When to use

Auto-invoke whenever the user asks for editing, proofreading, "humanise", "make this less AI", "remove slop", "polish for submission", or any prose-improvement request. Also self-invoke at the end of any non-trivial drafting task you complete (>200 words of prose), unless the user explicitly says skip.

Manual: `/humanize [text]` or `/humanize --profile=academic [text]` or `/humanize --voice=path/to/sample.md [text]`.

## Process (mandatory)

1. **Detect domain profile.** Inspect file path / filename:
   - `MANUSCRIPT*.md`, `*thesis*.md`, `paper*.md`, `*.tex` → `academic`
   - `README.md`, `*docs*`, `STAGE3/*.md` (technical docs) → `docs`
   - `*.commit`, COMMIT_EDITMSG → `commit`
   - Anything else → `blog`
   - User can override with `--profile=`.

2. **Calibrate voice if sample provided.** Read sample first; note rhythm, vocabulary level, paragraph openings, punctuation habits, recurring phrases. Match in rewrite.

3. **First-pass rewrite.** Apply the 38 patterns below, with profile-specific carve-outs.

4. **Self-audit.** Ask yourself: "What still makes this obviously AI-generated?" Answer in 3-5 bullets.

5. **Second-pass rewrite.** Apply the audit findings.

6. **Score.** If a CLI is available, run `humanize_score.py` on the result; report the numeric score (0-100, lower = more human).

7. **Output:**
   - Final humanised text
   - Self-audit bullets
   - Score (if available)
   - One-line summary of biggest changes

## Domain profile — carve-outs

| Pattern | academic | docs | blog | commit |
|---|---|---|---|---|
| Em-dash overuse (#14) | OK in moderation (≤1 per paragraph) | flagged | flagged | flagged |
| Passive voice (#13) | OK in IMRaD methods sections only | flagged | flagged in active sections | flagged hard |
| Rule of three (#10) | flagged | flagged | flagged | flagged |
| Hedging (#24, #38) | report-grade hedging OK; dissertation-grade flagged | flagged with citations exempted | flagged hard | flagged hard |
| Title case headings (#17) | follow journal style guide | sentence case | sentence case | sentence case |
| Stat parade without effect size (#33) | flagged | flagged | n/a | n/a |
| Citation laundering (#30) | flagged hard | flagged | flagged | n/a |
| Manuscript boilerplate (#31) | flagged hard | n/a | n/a | n/a |
| AI-flavoured commit verbs (#36) | n/a | n/a | n/a | flagged hard |

---

## Pattern catalogue (38 patterns)

### Patterns 1-29 — inherited from blader/humanizer (MIT, full attribution)

The 29 base patterns are reproduced from [blader/humanizer](https://github.com/blader/humanizer) under MIT. They are organised across **content** (1-6), **language and grammar** (7-13), **style** (14-19, 26-29), **communication** (20-22), and **filler / hedging** (23-25). For full text + before/after examples on patterns 1-29 see `patterns/core.md` (or the blader repo).

In summary form:

1. Significance inflation ("marking a pivotal moment in the evolution of...")
2. Notability name-dropping ("cited in NYT, BBC, FT, and The Hindu")
3. Superficial -ing analyses ("symbolizing... reflecting... showcasing...")
4. Promotional language ("nestled in the heart of", "boasts", "vibrant")
5. Vague attributions ("Experts believe", "Industry reports show")
6. Formulaic challenges section ("Despite challenges... continues to thrive")
7. Overused AI vocabulary (testament, landscape, tapestry, delve, intricate)
8. Copula avoidance (serves as / functions as / stands as)
9. Negative parallelisms (it's not just X, it's Y; tailing "..., no guessing")
10. Rule of three (innovation, inspiration, and industry insights)
11. Synonym cycling (protagonist / main character / central figure / hero)
12. False ranges (from Big Bang to dark matter)
13. Passive voice / subjectless fragments (no configuration file needed)
14. Em-dash overuse — like this — and like this —
15. Boldface overuse (**every** **noun** **bolded**)
16. Inline-header lists (**Performance:** Performance has improved)
17. Title Case Headings ("Strategic Negotiations And Partnerships")
18. Emojis as bullets / decorations (🚀 ✅ 💡)
19. Curly quotation marks (Unicode ", ", ', ' replacing ASCII " and ')
20. Chatbot artifacts ("Great question!", "I hope this helps!", "Let me know")
21. Knowledge-cutoff disclaimers ("As of my last training update")
22. Sycophantic / servile tone ("You're absolutely right!")
23. Filler phrases ("In order to", "Due to the fact that", "At this point in time")
24. Excessive hedging ("could potentially possibly", "might have some effect")
25. Generic positive conclusions ("The future looks bright")
26. Hyphenated word-pair overuse (cross-functional, data-driven, client-facing)
27. Persuasive authority tropes ("At its core, what really matters is...")
28. Signposting announcements ("Let's dive in", "Here's what you need to know")
29. Fragmented headers (heading + one-sentence restatement of heading)

### Patterns 30-38 — extensions (new in this skill)

#### 30. Citation laundering

**Problem:** "Studies show", "research suggests", "the literature reports" with no inline citation. Looks scholarly, says nothing.

**Before:**
> Studies show that nanoparticle radiosensitizers improve dose enhancement.

**After:**
> Hainfeld et al. (2004, doi:10.1088/0031-9155/49/18/N03) reported a 1.86× DEF for 1.9 nm gold nanoparticles at 250 kVp in EMT-6 tumours.

**Profile rule:** flagged hard in `academic` and `docs`. In `blog` only flagged when no replacement is offered.

#### 31. Manuscript boilerplate

**Problem:** Opening phrases that signal a draft AI generated to fill space.

**Phrases to watch:** "To the best of our knowledge", "fills a critical gap in the literature", "represents a significant advance", "of paramount importance", "constitutes the first comprehensive [X]", "lays the foundation for".

**Before:**
> To the best of our knowledge, this constitutes the first comprehensive analysis of...

**After:**
> No prior published study has analysed [specific scope]. We do.

**Profile rule:** flagged hard in `academic`. n/a elsewhere.

#### 32. Tutorial-script scaffolding (extension of #28)

**Problem:** Walks the reader through what they're about to read instead of just writing it.

**Before:**
> Let's walk through how the pipeline works. Here's the high-level overview, after which we'll dive into the details.

**After:**
> The pipeline has three stages: ingest, transform, score.

#### 33. Stat parade without effect size

**Problem:** P-values reported without effect size, CI, or interpretation. Frequentist hedging that says nothing about practical magnitude.

**Before:**
> The difference was statistically significant (p < 0.001).

**After:**
> The difference was 14 % (95 % BCa CI 9-19 %, p < 0.001 by paired t-test, n = 24, Cohen's d = 0.82).

**Profile rule:** flagged hard in `academic`; flagged in `docs`.

#### 34. Temporal hedge ladders

**Problem:** Stacked time-disclaimers cancel each other out.

**Before:**
> Currently, at the time of writing, as of the present moment, the field appears to be evolving rapidly.

**After:**
> The field changed substantially between 2020 and 2026.

#### 35. Polysyndetic tripleting (extension of #10)

**Problem:** Same paragraph, three or more "X, Y, and Z" constructions.

**Before:**
> The framework is fast, robust, and scalable. It serves researchers, clinicians, and educators. The implementation is open, transparent, and reproducible.

**After:**
> The framework is fast and reproducible. Researchers and clinicians use it.

#### 36. AI-flavoured commit-message verbs

**Problem:** Vague optimisation verbs in commit messages.

**Verbs to watch:** improves, enhances, refines, leverages, streamlines, optimises (with no specific metric).

**Before:**
> feat: improves robustness and enhances functionality

**After:**
> feat(parser): handle CRLF in input; fixes #142

**Profile rule:** flagged hard in `commit`. n/a elsewhere.

#### 37. Methodology pseudo-precision

**Problem:** Self-praising adjectives that describe how the work was done without saying what was done.

**Words to watch:** careful evaluation, rigorous analysis, comprehensive study, thorough examination, exhaustive review, systematic investigation, meticulous review.

**Before:**
> A careful evaluation was performed using a comprehensive methodology.

**After:**
> We computed BCa intervals from B = 10 000 cluster bootstraps over biological replicates, with calibration covariance propagated per Paper 1.

**Profile rule:** flagged hard in `academic`; flagged in `docs`.

#### 38. Dissertation-grade hedging in places that demand a stance

**Problem:** "It can be argued", "one might consider", "some would suggest" used to dodge a decision the writer is paid to make.

**Before:**
> It can be argued that this approach has some advantages.

**After:**
> This approach is faster but loses statistical power. We use it because the speed savings matter more for screening than for confirmation.

**Profile rule:** flagged hard in `academic`. flagged in `blog`. n/a in `commit`.

---

## Voice calibration

If the user provides `--voice=<file>` or pastes a sample inline:

1. **Read the sample first.** Note:
   - Sentence length distribution (median, range, SD)
   - Vocabulary register (Latinate vs Anglo-Saxon ratio)
   - Paragraph opening conventions (conjunction-led / topic-led / question-led)
   - Punctuation habits (em-dashes, semicolons, parenthetical asides)
   - Recurring phrases / verbal tics
   - Transition style (explicit connectors vs juxtaposition)
2. **Match the sample.** Replace AI patterns with constructions from the sample. If the writer uses short sentences, do not produce long ones; if they use "stuff" do not promote to "elements."
3. **No sample → use defaults below.**

### Default voice (when no sample provided)

- Vary sentence length: median 12-18 words, with occasional 4-word punchy sentences and occasional 30-word elaborations.
- Use first person when honest ("I think", "I keep coming back to") rather than corporate-we.
- Acknowledge complexity, mixed feelings, uncertainty.
- Use specific concrete details over abstract claims.
- Let some mess in: tangents, asides, half-formed thoughts.

## Self-audit prompt (mandatory step 4)

After the first-pass rewrite, ask yourself, exactly: **"What makes this still obviously AI-generated?"**

Answer in 3-5 bullets. Likely tells:
- Rhythm too even (every sentence ~15 words)
- Cleaner / more balanced contrasts than humans actually write
- Plausible-sounding but unsourced specifics
- Closer too aphoristic / slogan-y
- Suspiciously parallel structure across paragraphs
- Hedging that hides a real opinion

Then revise.

## Output format

```
## Humanised draft (first pass)
[text]

## Self-audit
- [tell 1]
- [tell 2]
- [tell 3]

## Final draft
[text]

## Score
humanize_score: NN/100 (lower = more human)
top offenders: [pattern A, pattern B, pattern C]

## Summary of changes
- [biggest change 1]
- [biggest change 2]
```

## Integration with other skills

- `/ship` calls this skill before commit on any prose-heavy diff.
- `/review-paper` invokes the `humanizer-reviewer` agent (separate file) for deeper review.
- `/compile-paper` runs `humanize_score.py` as a pre-compile gate; if score > 60, blocks compilation with a warning.

## Reference

- [blader/humanizer](https://github.com/blader/humanizer) — MIT, the foundation
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — primary source for patterns 1-29
- [WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup) — maintaining organisation
- Patterns 30-38 contributed by Kimal H. Djam (kimhons), 2026
