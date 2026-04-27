# Detection Robustness — research synthesis and extended design

**Date:** 2026-04-27
**Purpose:** Extend the `humanize` framework so academic writing passes AI-detection checks at submission.
**Frame:** This is **not** a guide to disguising AI work. It is a guide to producing genuinely human-authored writing that passes detection because the human is doing the authorship work, with AI as an editing assistant.

---

## 1. State of the AI-detector landscape (2026)

| Detector | Approach | Stated FPR | Real-world FPR (native EN) | Real-world FPR (ESL) | Survival after 3× humanizer |
|---|---|---|---|---|---|
| GPTZero | Perplexity + burstiness + ML classifier | 0.24 % | 3 % | **18 %** | 18 % detection |
| Originality.ai | Multi-model classifier; academic-tuned | <1 % | 5-7 % | 12-15 % | ~30 % detection |
| **Pangram** | Trained on 200 M+ samples; multi-feature ML | ~0 % | <1 % | <2 % | ~75 % detection (the strongest) |
| Copyleaks | Used by academic institutions | ~1 % | 4 % | 10 % | ~40 % detection |
| Turnitin AI | Proprietary academic model; min 300 words | 1 % | 4-6 % | **15-20 %** | ~50 % detection |
| ZeroGPT | Free, perplexity-only | 5 % | 8 % | 25 % | ~10 % detection |

**Implications:**
1. **Pangram is the strongest** — perplexity + burstiness tricks do not survive.
2. **Turnitin is a real risk for academic submission**, especially for ESL writers.
3. **ESL false-positive rate is ~3-6× higher** than native — francophone-English writers (like Kimal) are over-represented in false flags.
4. **No detector is reliable on text <50 words.** Short-form is naturally harder to classify.
5. **Watermarking is rare in production** — OpenAI tested but rolled back; some Google models embed it.

**Sources:**
- [GPTZero: How AI Detectors Work](https://gptzero.me/news/how-ai-detectors-work/)
- [Pangram: Why Perplexity and Burstiness Fail](https://www.pangram.com/blog/why-perplexity-and-burstiness-fail-to-detect-ai)
- [Pangram Labs: 30 AI Detectors Tested 2026](https://www.pangram.com/blog/best-ai-detector-tools)
- [PMC: Academic AI detection accuracy and limitations](https://pmc.ncbi.nlm.nih.gov/articles/PMC12331776/)
- [Walter Writes: Are AI Detectors Accurate (2026)](https://walterwrites.ai/are-ai-detectors-accurate/)
- [Chicago Booth Review: Do AI Detectors Work Well Enough](https://www.chicagobooth.edu/review/2025/december/do-ai-detectors-work-well-enough-trust)
- [Becker Friedman Institute: Artificial Writing and Automated Detection](https://bfi.uchicago.edu/insights/artificial-writing-and-automated-detection/)

---

## 2. What detectors actually look for

### 2.1 Perplexity (predictability)

**Definition.** Average negative log-likelihood of each token under a language model. Low perplexity = highly predictable = AI-flavoured.

**Human signature.** Perplexity in the 40-90 range (depending on the LM used as scorer). AI typically 10-25.

**How to raise it (legitimately).**
- Rare collocations: "irreparable epistemic gap" instead of "significant gap"
- Domain-specific jargon used non-formulaically: "the impedance trace plateaus before normalization" instead of "the data shows a plateau"
- Idioms and colloquialisms: "the calibration was a wash" instead of "the calibration was unsuccessful"
- Personal-experience specifics: "I ran this on a 2019 Dell rather than the cluster" instead of "computed locally"

### 2.2 Burstiness (variance)

**Definition.** Variation in sentence length and sentence-perplexity across the document. Humans vary; AI is uniform.

**Metric.** Coefficient of variation (CV) of sentence-token-counts. Human academic writing has CV ≈ 0.55-0.85. AI typically 0.20-0.45.

**How to raise it.**
- Mix 4-word sentences with 30-word sentences in the same paragraph.
- Use occasional fragments. Like this. Or — when the rhythm calls for it — long sweeping sentences that take their time getting where they're going, with parenthetical asides and the occasional dash.
- Vary paragraph length: 30-word paragraphs alongside 200-word paragraphs.

### 2.3 N-gram and feature classifiers

**Definition.** Modern detectors (Pangram, Originality, Turnitin) train ML classifiers on dozens of features: bigram frequencies, syntactic tree depth, function-word density, punctuation patterns, lexical density, stop-word ratios, etc.

**Why perplexity+burstiness alone fail.** A classifier that learned "Claude tends to put 'underscoring' after a noun phrase 42 % of the time" will flag your text even if perplexity and burstiness are tuned.

**How to defeat (legitimately).**
- Match a corpus of YOUR human writing rather than synthesising "average human" prose.
- Inject domain-specific vocabulary at frequencies that match your actual usage in pre-AI-era writing.
- Restructure sentence-tree shapes (use dependency-grammar variety: subject-verb-object, but also fronted adverbials, cleft sentences, parenthetical insertions).

### 2.4 Watermarks

**Definition.** Cryptographic bias in token-selection embedded by the model provider. Detectable only by the issuer with the secret key.

**Status (2026).** Mostly experimental. OpenAI demonstrated; not deployed in production. Google has experimented with SynthID for text but rollout is partial.

**Implication.** Watermarks are NOT a current threat for Claude-generated text in production.

### 2.5 Hidden Unicode tricks

**Definition.** Some humanizers insert zero-width chars (U+200B, U+200C, U+FEFF) to confuse detectors.

**Status.** Pangram and Copyleaks normalise Unicode before detection — this trick fails. Worse, some detectors flag normalised-Unicode anomalies as AI-evasion attempts.

**Recommendation.** **Do NOT** use Unicode tricks. They reduce credibility and can be reverse-detected.

---

## 3. What works (techniques validated by research)

| Technique | Evidence | Effort | Risk |
|---|---|---|---|
| Burstiness injection (sentence-length variance) | Strongest single signal | Low | Low |
| Voice anchoring to author's pre-AI corpus | Matches Pangram's training intuition | Medium | Low |
| Personal-experience specifics | Adds irreproducible detail | Medium | Low — must be true |
| Domain-jargon used non-formulaically | Lowers AI-pattern match | Medium | Low |
| Imperfection (controlled) | Real human edits leave marks | Low | Medium — overdo it and trip flag for "trying too hard" |
| Citation specificity (exact DOIs, dates, page nums) | Verifiable specifics LLMs avoid | High | Low |
| Substantive human revision (not just paraphrase) | Best practice; ethical | High | None |

## 4. What does NOT work

| Anti-pattern | Why it fails |
|---|---|
| Single-pass paraphrasing | Detectors trained against this; Pangram still catches |
| Synonym thesaurus attack | Modern classifiers use n-grams, not just words |
| Random typos injection | Pangram flags too-perfect-with-typos |
| Unicode hidden chars | Detectors normalise; some flag the attempt |
| Removing em-dashes only | One feature out of dozens |
| Adding "I think" everywhere | Detectors learned this hack |
| ChatGPT humanizer tools (single-pass) | 18-30 % detection still after 3 passes |

---

## 5. Ethical frame

This system is **only legitimate** when:

- The person submitting is the actual author (made the decisions, holds responsibility for accuracy).
- AI was a drafting/editing aid (not the author of the ideas).
- The work reflects human expertise, judgement, and original analysis.
- The human reviews and approves every claim.

It is **NOT legitimate** for:

- Submitting AI-only work as human-authored in academic contexts that prohibit AI assistance.
- Misrepresenting authorship to bypass legitimate detection.
- Bypassing AI-disclosure requirements where they exist.

For Kimal's PhD slate, the work IS his — Creighton-acquired primary data, his statistical analyses, his interpretations, his patent (US 63 270 375). AI assists with drafting + editing; Kimal owns and verifies every claim. **AI declarations** in the manuscripts disclose this honestly per AAPM/Wiley/Elsevier 2024 policies. The risk we're managing is false-positive detection of a **substantively human** paper, not concealment of authorship.

---

## 6. Extended architecture — adding 5 more layers

The original 6-layer humanize design (rule, skill, hook, agent, scorer, profiles) handles **style** patterns. Detection robustness needs 5 more layers focused on **statistical signatures**.

```
Original layers (style):
  L1 Standing rule in CLAUDE.md
  L2 .claude/rules/10-anti-slop.md
  L3 /humanize skill
  L4 PostToolUse hook
  L5 humanizer-reviewer subagent
  L6 humanize_score.py CLI

NEW layers (signature):
  L7 burstiness_check.py            — CV of sentence lengths; flag below 0.55
  L8 author-corpus voice anchor     — match against Kimal's pre-AI writing
  L9 detector-panel.py              — multi-detector validation; aggregate score
  L10 attestation marks              — verifiable specifics (dates, DOIs, equipment IDs, named people)
  L11 ESL-aware profile              — francophone-English transfer-pattern allowances
```

### Layer 7 — burstiness check

Computes:
- Sentence-token-count distribution (mean, std, CV)
- Paragraph-length distribution
- Function-word ratio (the, and, of, to, in)
- Lexical diversity (TTR — type-token ratio)
- Subordinate clause depth (proxy via comma/semicolon density)

Flags if:
- Sentence CV < 0.55
- Sentence count below 6 in a 300-word block (uniform pacing)
- Lexical diversity outside human range (0.40-0.65)

Output: same JSON shape as humanize_score, with key `signature_score` 0-100.

### Layer 8 — author-corpus voice anchor

Maintains a manifest of the author's verified pre-AI human writing:

For Kimal:
- Master's thesis V2 (2020) — 200+ pages, pre-LLM-era
- Djam et al. 2020 Springer chapter — co-authored 2018-2020
- Master's coursework essays
- His 9-volume textbook series (independent authorship)

Computes the author's signature: vocabulary frequency curve, punctuation patterns, paragraph rhythms. The skill matches new drafts against this signature, not generic "human."

### Layer 9 — multi-detector validation panel

Wraps free + API detectors:
- ZeroGPT (free API)
- GPTZero (free tier API)
- Originality.ai (paid; user provides API key)
- Copyleaks (paid; user provides API key)
- Pangram (paid; user provides API key — the strongest, worth it for academic submissions)

Output: matrix of (detector × text-block) probabilities. Aggregate verdict: PASS / NEEDS WORK / HEAVY SLOP. The skill iterates rewrites until ≥3 of 5 detectors clear at threshold.

### Layer 10 — attestation marks

Verifiable specifics that LLMs cannot hallucinate consistently:

- **Exact dates** of experiments (2020-03-09; not "in early 2020")
- **Equipment serial numbers** (Faxitron CellRad #XYZ; not "a kV X-ray cell irradiator")
- **DOI / PMID** for every claim (full DOI, not paraphrased)
- **Named collaborators** with affiliations (Andrew E. Ekpenyong, Creighton; not "the senior author")
- **Lab logbook references** ("logbook entry 2020-03-09 14:23"; not "during the experiment")
- **Quantitative specifics** (NRRI 0.847 ± 0.012; not "a high NRRI")

These are not aesthetic — they are evidence. They distinguish substantively human academic work from plausible AI output. Reviewers and detectors both lean on them.

### Layer 11 — ESL-aware profile

Calibrated for francophone-English writers:

- **Allowed**: Latinate vocabulary preference (academic French → English transfer is heavy on Latinate cognates).
- **Allowed**: Slightly longer sentences (French academic style).
- **Flagged**: Article omission errors (typical ESL tell, but also AI-generated text doesn't make these).
- **Allowed**: Occasional French syntactic transfer ("for to do X" structures, sparingly).
- **Custom threshold**: Burstiness CV target 0.50 (vs 0.55 for native EN), since francophone-English academic writing tends to be more uniform.

This layer prevents over-correction toward "native EN slang" that Kimal would not naturally produce.

---

## 7. Detection-pass workflow

For any prose deliverable headed to a journal / Middlesex submission / public release:

```
draft.md
   │
   ▼
[L3 /humanize]  ── style cleanup, 38 patterns, voice calibration
   │
   ▼
[L6 humanize_score]  ── numeric style score; iterate to <40
   │
   ▼
[L7 burstiness_check]  ── CV ≥0.55 (or ≥0.50 for ESL profile)
   │
   ▼
[L8 voice anchor]  ── matches Kimal's pre-AI corpus signature
   │
   ▼
[L10 attestation marks audit]  ── every claim has: date, DOI, person, number, citation
   │
   ▼
[L9 detector panel]  ── ≥3 of 5 detectors clear
   │
   ▼
[L5 humanizer-reviewer subagent]  ── final critical pass
   │
   ▼
SUBMIT
```

Targets at submission:
- humanize_score ≤ 30 / 100
- Sentence-CV ≥ 0.55 (or ≥ 0.50 ESL)
- Detector panel: ≥ 3 of 5 say "human" at default thresholds
- Attestation marks density: ≥ 1 verifiable specific per 200 words

---

## 8. Honest limits

1. **No system is 100 % reliable** against all detectors, especially Pangram on long-form academic English.
2. **False positives on ESL writers** are real and not always fixable by humanization — they reflect detector bias against non-native English styles. If a paper triggers Turnitin, the answer is **disclosure + appeal**, not deeper humanization.
3. **The strongest defence is genuine human authorship.** Substantive human revision, original analysis, and verifiable attestation marks defeat detectors better than any post-hoc humanizer.
4. **Detector landscape changes.** Targets that pass today may flag in 6 months. The framework needs continuous calibration; the multi-detector panel + author corpus is the maintenance hook.
5. **Disclose AI assistance** when journal policies require. The AI-declaration skill in the slate's `.claude/skills/ai-declaration/` already handles this.

End of detection-robustness research.
