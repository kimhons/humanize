# humanize — A Comprehensive Anti-Slop Framework for Claude Code

**Author:** Kimal H. Djam (kimhons) — public-domain repo
**Inspired by:** [blader/humanizer](https://github.com/blader/humanizer) (MIT, 2.4k stars) — credit + extends
**License:** MIT
**Status:** Plan v1.0 (2026-04-27)

---

## 1. Why a new framework

The blader/humanizer skill is the strongest open-source reference but stops at the slash-command pattern. It is **passive** — Claude only humanises when you explicitly type `/humanizer`. Every other write Claude does in the session goes through unfiltered, gets indexed by future sessions as "this is how we write here," and the AI slop compounds.

Three additional gaps:
1. **No domain calibration.** Em-dashes are fine in scientific prose; passive voice is correct in IMRaD methods sections. The reference treats all text the same.
2. **No scoring or feedback loop.** You can't quickly tell whether a draft is at AI-slop 12 % or 78 %.
3. **No always-on enforcement.** No hook, no subagent, no standing rule baked into CLAUDE.md, no commit-time gate.

---

## 2. The 6-layer architecture

Layered defence so AI slop has no clear path to merge.

```
Layer 1  Standing order in CLAUDE.md             (always loaded; tells every session "don't slop")
Layer 2  Always-on rule file (.claude/rules/)    (referenced by global config; specific anti-slop directives)
Layer 3  /humanize skill                          (explicit invocation for batch cleanup, with voice calibration)
Layer 4  PostToolUse hook on Write/Edit           (auto-flags slop in prose files at commit time)
Layer 5  humanizer-reviewer subagent              (deeper review; called by /ship and /review-paper)
Layer 6  humanize-score CLI                       (returns 0-100 AI-slop probability for any text file)
```

Plus four **domain profiles** (academic, blog, docs, commit) each with its own pattern carve-outs.

---

## 3. Pattern catalogue — extends blader/humanizer's 29

Inherits all 29 from blader (with attribution). Adds:

| # | New pattern | Why |
|---|---|---|
| 30 | **Citation laundering** ("studies show", "research suggests") with no inline citation | Academic-specific tell |
| 31 | **Manuscript boilerplate** ("To the best of our knowledge", "fills a critical gap in the literature") | Academic-paper opener slop |
| 32 | **Excess scaffolding language in code-adjacent docs** ("Let's walk through", "Here's the high-level overview") | Tutorial-script feel |
| 33 | **Stat parade without effect size** ("p < 0.05", no Cohen's d / 95 % CI / effect interpretation) | Frequentist hedging |
| 34 | **Temporal hedge ladders** ("currently ... at present ... at the time of writing") | Multiple cutoff disclaimers |
| 35 | **List of three with rule of polysyndeton** ("X, Y, and Z" repeated >2× per paragraph) | Stronger version of rule of three |
| 36 | **AI-flavoured commit messages** ("Improves robustness", "Enhances functionality") | Commit-specific |
| 37 | **Methodology pseudo-precision** ("careful evaluation", "rigorous analysis", "comprehensive study") | Self-praise without specifics |
| 38 | **Dissertation-grade hedging** ("It can be argued", "One might consider") in places that demand a stance | Academic-only |

Total: **38 patterns** across 5 + 1 (academic) categories.

---

## 4. Domain profiles

Each profile selects a **subset** of the 38 patterns + adds domain-specific overrides.

| Profile | Use case | Em-dash | Passive | Rule of three | Hedging |
|---|---|---|---|---|---|
| `academic` | Papers, theses, abstracts | OK in moderation | OK in IMRaD methods | flagged | dissertation-grade flagged; report-grade OK |
| `docs` | README, technical docs | flagged | flagged | flagged | OK with citations |
| `blog` | Blog posts, essays | flagged | flagged in active sections | flagged | flagged hard |
| `commit` | Commit messages | flagged | flagged | flagged | flagged hard |

Profile detection is automatic from path/filename heuristics (e.g., `MANUSCRIPT*.md` → academic; `README.md` → docs; `*.commit` → commit; otherwise → blog). User can override with `/humanize --profile=academic`.

---

## 5. The 6 deliverables

### Layer 1 — Global CLAUDE.md insertion
File: `C:\Users\Owner\.claude\CLAUDE.md` — append a §"Anti-slop discipline" section pointing to the rule + skill + hook. Always-loaded, so every session sees it.

### Layer 2 — Always-on rule file
File: `C:\Users\Owner\.claude\rules\10-anti-slop.md` — concise standing order with the top-15 forbidden patterns inline. Loaded into every session as part of the global rules ensemble.

### Layer 3 — /humanize skill
File: `C:\Users\Owner\.claude\skills\humanize\SKILL.md` — extends blader's 29 patterns to 38, adds 4 domain profiles, voice calibration, audit pass. Single self-contained file plus optional `references/` and `scripts/`.

### Layer 4 — PostToolUse hook
File: `C:\Users\Owner\.claude\hooks\humanize-post-write.sh` — fires on Write/Edit of `.md` / `.tex` files outside `.claude/`. Runs the scorer; if score > threshold (configurable, default 60 %), prints a warning with top-3 offending patterns.

### Layer 5 — humanizer-reviewer subagent
File: `C:\Users\Owner\.claude\agents\humanizer-reviewer.md` — sonnet model, 12 turns, tools: Read, Grep, Edit. Used by `/ship`, `/review-paper`, and on demand. Returns severity-tagged findings + corrected text.

### Layer 6 — humanize-score CLI
File: `D:\dev\projects\humanize\scripts\humanize_score.py` — pure-Python; reads a text file, applies regex + heuristic checks for the 38 patterns, returns JSON: `{score: 0-100, breakdown: {pattern: count}, top_offenders: [...]}`. Zero dependencies.

---

## 6. The public repo

Path: `D:\dev\projects\humanize\` — git-init, MIT-licensed, pushed to `github.com/kimhons/humanize` (user-confirmed name).

```
humanize/
├── README.md                 # Public docs + install instructions for both Claude Code AND OpenCode
├── LICENSE                   # MIT
├── PLAN.md                   # This file
├── CHANGELOG.md
├── SKILL.md                  # The Claude Code skill (drop-in compatible with blader/humanizer install path)
├── patterns/
│   ├── core.md               # 29 patterns inherited from blader (with attribution)
│   └── extensions.md         # 9 new patterns (30-38)
├── profiles/
│   ├── academic.md
│   ├── docs.md
│   ├── blog.md
│   └── commit.md
├── scripts/
│   ├── humanize_score.py     # CLI scorer
│   ├── install.sh            # bash installer (POSIX)
│   └── install.ps1           # PowerShell installer (Windows)
├── hooks/
│   └── humanize-post-write.sh
├── agents/
│   └── humanizer-reviewer.md
├── examples/
│   ├── academic_before_after.md
│   ├── blog_before_after.md
│   └── commit_before_after.md
└── tests/
    └── test_scoring.py       # pytest of the scorer against fixtures
```

---

## 7. Build sequence (today)

1. Write `humanize/PLAN.md` (this file).
2. Write `humanize/SKILL.md` (extending blader, domain profiles, voice calibration, audit pass).
3. Write `humanize/patterns/core.md` + `patterns/extensions.md`.
4. Write `humanize/profiles/{academic,docs,blog,commit}.md`.
5. Write `humanize/scripts/humanize_score.py` (pure Python, 38-pattern regex catalogue, deterministic scoring).
6. Write `humanize/hooks/humanize-post-write.sh`.
7. Write `humanize/agents/humanizer-reviewer.md`.
8. Write `humanize/README.md` + `LICENSE`.
9. Write installation scripts.
10. Install globally: copy/symlink to `C:\Users\Owner\.claude\{skills,rules,hooks,agents}\`.
11. Append §"Anti-slop discipline" to `C:\Users\Owner\.claude\CLAUDE.md`.
12. Smoke test: run scorer on 5 fixtures (one per domain + a known-bad sample); verify scores land in expected ranges.
13. Stage all files, `git init`, first commit. Tag `v1.0.0`.
14. Hand off to user: `gh repo create kimhons/humanize --public --source=. --push`. (User presses send.)

---

## 8. Attribution + relationship to blader/humanizer

- The 29 core patterns and the audit-pass concept come from blader. Credit prominent in README, LICENSE preserves MIT.
- The 9 extensions, the 4 domain profiles, the scorer, the hook, the agent, the always-on rule, the global CLAUDE.md insertion — these are net-new contributions.
- Drop-in install path compatibility (`~/.claude/skills/humanize/`) so users coming from blader's repo only have to swap one git remote.

---

## 9. Open decisions before pushing public

| | Question | Default |
|---|---|---|
| A | Repo name | `humanize` (short, clean, kimhons/humanize) |
| B | Repo description | "Anti-slop framework for Claude Code: skill + hook + agent + scorer. Strips 38 AI-writing patterns. Domain-aware (academic / docs / blog / commit). Extends @blader/humanizer." |
| C | Topics / tags | `claude-code`, `claude-skill`, `humanizer`, `ai-slop`, `writing-quality`, `academic-writing` |
| D | Public on push? | Yes (per user instruction) |
| E | License | MIT (matches blader; lets blader users copy back) |
| F | Acknowledge blader in README? | Yes, prominent — top-of-page block |

End of plan.
