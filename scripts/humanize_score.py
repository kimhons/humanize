#!/usr/bin/env python3
"""humanize_score — quantify AI-writing patterns in a text file.

Returns JSON: {"score": 0-100, "breakdown": {pattern_id: count}, "top_offenders": [...], "profile": "..."}.
Lower score = more human. Threshold convention:
   0-20   clean / human
   20-40  some AI residue, acceptable
   40-60  obvious patterns, needs editing
   60-100 heavy slop, rewrite

Pure Python, zero dependencies. Compatible with Python 3.9+.

Usage:
   python humanize_score.py FILE.md
   python humanize_score.py --profile=academic FILE.md
   python humanize_score.py --json FILE.md > result.json

Profile detection (auto unless --profile= is given):
   MANUSCRIPT*.md, *thesis*.md, *.tex     -> academic
   README.md, docs/*, STAGE3/*.md         -> docs
   .git/COMMIT_EDITMSG, *.commit          -> commit
   else                                   -> blog
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ---- Pattern definitions (38 patterns) ----------------------------------------

# Each pattern: (id, name, regex, weight, profile_carveouts).
# profile_carveouts maps profile -> multiplier (1.0 default; 0.0 disables; 0.5 reduces).


@dataclass
class Pattern:
    pid: int
    name: str
    regex: re.Pattern[str]
    weight: float = 1.0
    profile_carveouts: dict[str, float] = field(default_factory=dict)

    def adjusted_weight(self, profile: str) -> float:
        return self.weight * self.profile_carveouts.get(profile, 1.0)


def _re(p: str, flags: int = re.IGNORECASE) -> re.Pattern[str]:
    return re.compile(p, flags)


PATTERNS: list[Pattern] = [
    # 1 Significance inflation
    Pattern(
        1,
        "significance_inflation",
        _re(
            r"\b(stands? as|serves? as|is a testament|marking a pivotal moment|"
            r"underscoring (its )?(importance|significance)|reflects? (a )?broader|"
            r"setting the stage for|indelible mark|deeply rooted|evolving landscape|"
            r"focal point|key turning point|represents? a shift)\b"
        ),
        weight=1.5,
    ),
    # 2 Notability name-dropping
    Pattern(
        2,
        "notability_name_dropping",
        _re(
            r"\b(cited in|featured in|covered by|written by a leading expert|active social media presence)\b"
        ),
        weight=1.0,
    ),
    # 3 Superficial -ing analyses
    Pattern(
        3,
        "superficial_ing",
        _re(
            r"\b(highlighting|underscoring|emphasizing|symbolizing|reflecting|"
            r"contributing to|cultivating|fostering|encompassing|showcasing) \b"
        ),
        weight=1.2,
    ),
    # 4 Promotional language
    Pattern(
        4,
        "promotional",
        _re(
            r"\b(nestled|breathtaking|stunning|vibrant|boasts?|in the heart of|"
            r"renowned for|must[- ]visit|profound|groundbreaking|exemplifies|"
            r"a commitment to)\b"
        ),
        weight=1.5,
    ),
    # 5 Vague attribution
    Pattern(
        5,
        "vague_attribution",
        _re(
            r"\b(experts? (argue|believe|say|note)|industry (reports|observers)|"
            r"observers (have )?(noted|cited)|some (critics|sources|publications))\b"
        ),
        weight=1.5,
        profile_carveouts={"commit": 0.0},
    ),
    # 6 Formulaic challenges section
    Pattern(
        6,
        "formulaic_challenges",
        _re(
            r"\b(despite (its|these) (challenges|drawbacks|limitations)|"
            r"continues to thrive|future (outlook|prospects)|challenges? and legacy)\b"
        ),
        weight=1.5,
    ),
    # 7 AI vocabulary
    Pattern(
        7,
        "ai_vocabulary",
        _re(
            r"\b(delve|delves|delving|tapestry|landscape|testament|underscore[sd]?|"
            r"intricate|intricacies|interplay|garner[sed]*|pivotal|aligns? with|"
            r"foster(s|ed|ing)?|enduring|enhanc(e|ed|ing|es|ement)|valuable insights?)\b"
        ),
        weight=1.0,
    ),
    # 8 Copula avoidance
    Pattern(
        8,
        "copula_avoidance",
        _re(r"\b(serves? as|stands? as|functions? as|represents? a|marks? a)\s+\w+"),
        weight=0.8,
    ),
    # 9 Negative parallelisms
    Pattern(
        9,
        "negative_parallelism",
        _re(
            r"\b(it[''']s not (just|only|merely) about|not (just|only|merely) X[, ]+but|, no \w+\.)"
        ),
        weight=1.2,
    ),
    # 10 Rule of three (any "A, B, and C" — coarse; we count occurrences per paragraph in scoring)
    Pattern(10, "rule_of_three", _re(r"\b\w+,\s*\w+,?\s*and\s+\w+\b"), weight=0.5),
    # 11 Synonym cycling — heuristic, not regex; flagged if same noun has 3+ synonym variants in one paragraph
    Pattern(11, "synonym_cycling", _re(r"$^"), weight=0.0),  # placeholder; computed separately
    # 12 False ranges
    Pattern(
        12,
        "false_ranges",
        _re(
            r"\bfrom\s+(?:the\s+)?\w+\s+to\s+(?:the\s+)?\w+(?:\s*,\s*from\s+(?:the\s+)?\w+\s+to\s+(?:the\s+)?\w+)+"
        ),
        weight=1.5,
    ),
    # 13 Passive voice / subjectless fragments — heuristic
    Pattern(
        13,
        "passive_voice",
        _re(r"\b(is|are|was|were|been|being)\s+\w+ed\b"),
        weight=0.3,
        profile_carveouts={"academic": 0.4},
    ),
    # 14 Em-dash overuse
    Pattern(14, "em_dash_overuse", _re(r"—"), weight=0.4, profile_carveouts={"academic": 0.2}),
    # 15 Boldface overuse — count **bold** phrases per paragraph
    Pattern(15, "boldface_overuse", _re(r"\*\*[^*]{1,40}\*\*"), weight=0.3),
    # 16 Inline-header lists
    Pattern(
        16,
        "inline_header_lists",
        _re(r"^\s*[-*]\s*\*\*[A-Z][^*]+\*\*[: ]", re.MULTILINE),
        weight=1.0,
    ),
    # 17 Title Case Headings (heuristic: heading line where >50% of words start uppercase)
    Pattern(17, "title_case_headings", _re(r"$^"), weight=0.0),  # placeholder
    # 18 Emojis as bullets / decorations
    Pattern(18, "emojis", _re("[\U0001f300-\U0001faff☀-➿]"), weight=1.5),
    # 19 Curly quotes
    Pattern(19, "curly_quotes", _re(r"[‘’“”]"), weight=0.5),
    # 20 Chatbot artifacts
    Pattern(
        20,
        "chatbot_artifacts",
        _re(
            r"\b(I hope this helps|let me know if|here is (a|an|the)|of course!|"
            r"certainly!|you[''']re absolutely right|would you like (me to)?|happy to help)\b"
        ),
        weight=2.0,
    ),
    # 21 Knowledge-cutoff disclaimers
    Pattern(
        21,
        "cutoff_disclaimer",
        _re(
            r"\b(as of my (last )?(training|knowledge)|while specific details (are|appear) (limited|scarce)|"
            r"based on (the )?(available|publicly available) information|"
            r"up to my (last )?training update)\b"
        ),
        weight=2.0,
    ),
    # 22 Sycophantic / servile tone
    Pattern(
        22,
        "sycophantic",
        _re(
            r"\b(great question!|excellent point|that[''']s a (great|fantastic|wonderful)|brilliant observation)\b"
        ),
        weight=2.0,
    ),
    # 23 Filler phrases
    Pattern(
        23,
        "filler_phrases",
        _re(
            r"\b(in order to|due to the fact that|at this point in time|"
            r"in the event that|has the ability to|it is important to note that|"
            r"with regards to|in light of the fact that)\b"
        ),
        weight=1.0,
    ),
    # 24 Excessive hedging
    Pattern(
        24,
        "excessive_hedging",
        _re(
            r"\b(could potentially possibly|might (potentially )?have some|"
            r"may possibly|it could be argued that|one might suggest that)\b"
        ),
        weight=1.5,
    ),
    # 25 Generic positive conclusions
    Pattern(
        25,
        "generic_conclusion",
        _re(
            r"\b(the future looks bright|exciting times (lie ahead|await)|"
            r"a step in the right direction|continues to evolve)\b"
        ),
        weight=1.5,
    ),
    # 26 Hyphenated word-pair overuse
    Pattern(
        26,
        "hyphenated_pairs",
        _re(
            r"\b(cross-functional|data-driven|client-facing|decision-making|"
            r"end-to-end|real-time|long-term|high-quality|well-known)\b"
        ),
        weight=0.4,
        profile_carveouts={"academic": 0.6},
    ),
    # 27 Persuasive authority tropes
    Pattern(
        27,
        "persuasive_authority",
        _re(
            r"\b(at its core|in reality|what really matters|fundamentally|"
            r"the deeper issue|the heart of the matter|the real question)\b"
        ),
        weight=1.2,
    ),
    # 28 Signposting announcements
    Pattern(
        28,
        "signposting",
        _re(
            r"\b(let[''']s (dive in|explore|break this down|walk through|take a look)|"
            r"here[''']s what you need to know|now let[''']s look at|"
            r"without further ado)\b"
        ),
        weight=1.5,
    ),
    # 29 Fragmented headers — heuristic, computed separately
    Pattern(29, "fragmented_headers", _re(r"$^"), weight=0.0),  # placeholder
    # ---- Extensions 30-38 (new) ----
    # 30 Citation laundering
    Pattern(
        30,
        "citation_laundering",
        _re(
            r"\b(studies (have )?(shown|suggest|reported|indicate)|"
            r"research (suggests|indicates|has shown)|the literature (reports|suggests))\b(?![^.]*\d{4})"
        ),
        weight=2.0,
        profile_carveouts={"academic": 2.5, "commit": 0.0},
    ),
    # 31 Manuscript boilerplate
    Pattern(
        31,
        "manuscript_boilerplate",
        _re(
            r"\b(to the best of our knowledge|fills a critical gap|"
            r"represents a significant advance|of paramount importance|"
            r"constitutes the first comprehensive|lays the foundation for)\b"
        ),
        weight=2.5,
        profile_carveouts={"academic": 3.0, "blog": 1.5, "docs": 1.0, "commit": 0.0},
    ),
    # 32 Tutorial-script scaffolding
    Pattern(
        32,
        "tutorial_scaffolding",
        _re(
            r"\b(let[''']s walk through|let[''']s start with|here[''']s the high-level|"
            r"after which we[''']ll|in this section[, ]+we will)\b"
        ),
        weight=1.2,
    ),
    # 33 Stat parade without effect size
    Pattern(
        33,
        "stat_parade",
        _re(r"\bp\s*[<>=]\s*0?\.\d+(?![^.]{0,80}(95\s*%|CI|Cohen|effect size|d\s*=))"),
        weight=1.5,
        profile_carveouts={"academic": 2.0, "blog": 0.5},
    ),
    # 34 Temporal hedge ladders
    Pattern(
        34,
        "temporal_hedges",
        _re(r"\b(currently|at present|at the time of writing|as of (now|today))\b"),
        weight=0.6,
    ),
    # 35 Polysyndetic tripleting — count "X, Y, and Z" patterns per paragraph
    Pattern(35, "polysyndetic_tripleting", _re(r"$^"), weight=0.0),  # computed separately
    # 36 AI-flavoured commit verbs
    Pattern(
        36,
        "ai_commit_verbs",
        _re(
            r"^(feat|fix|chore|refactor|perf|docs|style|test)(\([^)]+\))?:\s+"
            r"(improves?|enhances?|refines?|leverages?|streamlines?|optimises?)\b",
            re.MULTILINE | re.IGNORECASE,
        ),
        weight=2.0,
        profile_carveouts={"commit": 3.0, "academic": 0.0, "docs": 0.0, "blog": 0.0},
    ),
    # 37 Methodology pseudo-precision
    Pattern(
        37,
        "methodology_pseudo",
        _re(
            r"\b(careful evaluation|rigorous analysis|comprehensive (study|review|analysis)|"
            r"thorough examination|exhaustive review|systematic investigation|"
            r"meticulous (review|analysis))\b"
        ),
        weight=2.0,
        profile_carveouts={"academic": 2.5, "commit": 0.0},
    ),
    # 38 Dissertation-grade hedging
    Pattern(
        38,
        "dissertation_hedging",
        _re(
            r"\b(it can be argued that|one might (consider|suggest|argue)|"
            r"some (would|might) (suggest|argue)|it could be (said|argued))\b"
        ),
        weight=1.8,
        profile_carveouts={"academic": 2.5, "commit": 0.0},
    ),
]


# ---- Heuristic computations for placeholder patterns --------------------------

# Synonym groups for synonym-cycling detection.
SYNONYM_GROUPS: list[set[str]] = [
    {"hero", "protagonist", "main character", "central figure", "individual"},
    {"company", "organization", "organisation", "firm", "enterprise", "business"},
    {"author", "writer", "scribe", "novelist"},
    {"event", "occurrence", "incident", "happening"},
    {"problem", "issue", "challenge", "difficulty", "obstacle"},
]


def count_synonym_cycling(text: str) -> int:
    """#11. Heuristic — for each paragraph, count repeated noun-meaning across 3+ variants.

    Coarse: detects when 3+ candidate synonyms (e.g. hero / protagonist / main character)
    co-occur in the same paragraph. Reports paragraphs that match.
    """
    count = 0
    for para in re.split(r"\n\s*\n", text):
        for group in SYNONYM_GROUPS:
            hits = sum(1 for term in group if re.search(rf"\b{re.escape(term)}\b", para, re.I))
            if hits >= 3:
                count += 1
    return count


def count_title_case_headings(text: str) -> int:
    """#17. Lines starting with #/##/###/etc where >50% of content words are capitalised."""
    count = 0
    for line in text.splitlines():
        m = re.match(r"^\s*#{1,6}\s+(.+)$", line)
        if not m:
            continue
        content = m.group(1).strip()
        words = [w for w in re.findall(r"[A-Za-z]+", content) if len(w) > 2]
        if len(words) < 2:
            continue
        capitalised = sum(1 for w in words if w[0].isupper())
        if capitalised / len(words) > 0.5:
            count += 1
    return count


def count_fragmented_headers(text: str) -> int:
    """#29. Heading followed by a one-sentence paragraph that restates the heading."""
    count = 0
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^\s*#{1,6}\s+\w", line):
            continue
        # Find the next non-empty line
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            continue
        next_line = lines[j].strip()
        if (
            next_line
            and not next_line.startswith("#")
            and len(next_line.split()) <= 8
            and j + 1 < len(lines)
            and lines[j + 1].strip()
        ):
            # next-next line is also content -> next_line is a fragment intro
            count += 1
    return count


def count_polysyndetic_tripleting(text: str) -> int:
    """#35. Count paragraphs with 3+ 'X, Y, and Z' patterns."""
    count = 0
    for para in re.split(r"\n\s*\n", text):
        triplets = re.findall(r"\b\w+,\s*\w+,?\s*and\s+\w+\b", para)
        if len(triplets) >= 3:
            count += 1
    return count


# ---- Profile detection --------------------------------------------------------


def detect_profile(path: Path) -> str:
    name = path.name.lower()
    full = str(path).lower().replace("\\", "/")
    if name == "commit_editmsg" or name.endswith(".commit"):
        return "commit"
    if any(x in name for x in ("manuscript", "thesis", "paper")) or name.endswith(".tex"):
        return "academic"
    if name == "readme.md" or "/docs/" in full or "/stage3/" in full:
        return "docs"
    return "blog"


# ---- Scoring ------------------------------------------------------------------


def score_text(text: str, profile: str = "blog") -> dict:
    """Compute the AI-slop score and breakdown."""
    breakdown: dict[str, int] = {}
    weighted: dict[str, float] = {}
    total_words = max(len(text.split()), 1)

    for p in PATTERNS:
        if p.weight == 0:
            continue
        hits = len(p.regex.findall(text))
        if hits:
            breakdown[p.name] = hits
            weighted[p.name] = hits * p.adjusted_weight(profile)

    # Heuristic computations
    sc = count_synonym_cycling(text)
    if sc:
        breakdown["synonym_cycling"] = sc
        weighted["synonym_cycling"] = sc * 1.0

    th = count_title_case_headings(text)
    if th:
        breakdown["title_case_headings"] = th
        weighted["title_case_headings"] = th * 0.7

    fh = count_fragmented_headers(text)
    if fh:
        breakdown["fragmented_headers"] = fh
        weighted["fragmented_headers"] = fh * 1.0

    pt = count_polysyndetic_tripleting(text)
    if pt:
        breakdown["polysyndetic_tripleting"] = pt
        weighted["polysyndetic_tripleting"] = pt * 1.5

    # Normalise: weighted score per 100 words, capped at 100
    raw = sum(weighted.values()) / total_words * 100
    score = min(100.0, raw * 5.0)  # 5× scaling so 20 weighted hits / 100 words = 100

    top_offenders = sorted(weighted.items(), key=lambda kv: -kv[1])[:5]

    return {
        "score": round(score, 1),
        "profile": profile,
        "word_count": total_words,
        "breakdown": breakdown,
        "weighted": {k: round(v, 2) for k, v in weighted.items()},
        "top_offenders": [{"pattern": k, "weighted": round(v, 2)} for k, v in top_offenders],
        "verdict": (
            "clean"
            if score < 20
            else "minor_residue"
            if score < 40
            else "needs_editing"
            if score < 60
            else "heavy_slop"
        ),
    }


# ---- CLI ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score a text file on AI-writing patterns. Lower score = more human."
    )
    parser.add_argument("path", help="Path to text file (.md, .tex, .txt, ...)")
    parser.add_argument(
        "--profile",
        choices=["academic", "docs", "blog", "commit", "auto"],
        default="auto",
        help="Domain profile (default: auto-detect from filename).",
    )
    parser.add_argument("--json", action="store_true", help="Emit raw JSON.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=60.0,
        help="Exit non-zero if score exceeds threshold (default 60).",
    )
    args = parser.parse_args(argv)

    path = Path(args.path)
    if not path.is_file():
        print(f"error: {path} is not a file", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    profile = args.profile if args.profile != "auto" else detect_profile(path)
    result = score_text(text, profile=profile)
    result["path"] = str(path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"humanize_score: {result['score']}/100  ({result['verdict']})")
        print(f"profile:        {profile}  ({result['word_count']} words)")
        print("top offenders:")
        for off in result["top_offenders"]:
            print(f"  - {off['pattern']:32s} weighted={off['weighted']}")

    return 1 if result["score"] > args.threshold else 0


if __name__ == "__main__":
    sys.exit(main())
