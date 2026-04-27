# humanize

> Anti-slop framework for Claude Code. Skill + scorer + agent + hook + always-on rule. Strips 38 AI-writing patterns. Domain-aware (academic / docs / blog / commit). Extends [blader/humanizer](https://github.com/blader/humanizer).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Compatible: Claude Code](https://img.shields.io/badge/Compatible-Claude%20Code-blue)](https://claude.ai/claude-code)
[![Compatible: OpenCode](https://img.shields.io/badge/Compatible-OpenCode-green)](https://opencode.ai)

## What this is

`humanize` is six tools that work together so AI slop has no clear path into your prose:

| Layer | Component | Triggered by |
|---|---|---|
| 1 | Standing rule in `~/.claude/CLAUDE.md` | Loaded into every session |
| 2 | Always-on rule file at `~/.claude/rules/10-anti-slop.md` | Same |
| 3 | `/humanize` slash command | Manual invocation |
| 4 | PostToolUse hook on Write/Edit | Fires automatically when Claude writes prose |
| 5 | `humanizer-reviewer` subagent | Called by `/ship`, `/review-paper`, on demand |
| 6 | `humanize_score.py` CLI | Fast scoring; exits non-zero above threshold |

Plus four **domain profiles** (academic, docs, blog, commit) with their own carve-outs. Em-dashes are fine in scientific prose. Passive voice is correct in IMRaD methods. Vague attributions are flagged hard in academic but allowed (with citation) in docs. The framework adapts.

## What it detects (38 patterns)

Inherits 29 from [blader/humanizer](https://github.com/blader/humanizer) (significance inflation, promotional language, em-dash overuse, rule of three, AI vocabulary, copula avoidance, sycophancy, filler phrases, hedging, generic conclusions, …) — full list with before/after in [SKILL.md](SKILL.md).

New extensions (#30-38):

| # | Pattern | Why it matters |
|---|---|---|
| 30 | Citation laundering ("studies show" with no citation) | Academic-killer |
| 31 | Manuscript boilerplate ("To the best of our knowledge…") | Generic paper opener |
| 32 | Tutorial-script scaffolding ("Let's walk through…") | Doc tutorial-script feel |
| 33 | Stat parade without effect size | Frequentist hedging |
| 34 | Temporal hedge ladders | Stacked time-disclaimers |
| 35 | Polysyndetic tripleting | Stronger rule-of-three |
| 36 | AI-flavoured commit verbs ("improves", "enhances") | Commit-specific |
| 37 | Methodology pseudo-precision ("careful", "rigorous", "comprehensive") | Self-praise without specifics |
| 38 | Dissertation-grade hedging where stance is required | Academic-only |

## Install (Claude Code, global)

```bash
# Clone
git clone https://github.com/kimhons/humanize.git ~/.claude/skills/humanize
# Activate the agent
cp ~/.claude/skills/humanize/agents/humanizer-reviewer.md ~/.claude/agents/
# Wire the hook (one-line append to settings.json — see scripts/install.sh)
bash ~/.claude/skills/humanize/scripts/install.sh
```

For OpenCode users:

```bash
git clone https://github.com/kimhons/humanize.git ~/.config/opencode/skills/humanize
```

## Install (manual, single-file)

```bash
mkdir -p ~/.claude/skills/humanize
curl -L https://raw.githubusercontent.com/kimhons/humanize/main/SKILL.md \
     -o ~/.claude/skills/humanize/SKILL.md
```

## Usage

### Manual invocation

```
/humanize [paste your text]
```

```
/humanize --profile=academic [paste]
```

```
/humanize --voice=path/to/sample-of-my-writing.md [paste]
```

### CLI scoring

```bash
$ python ~/.claude/skills/humanize/scripts/humanize_score.py STAGE3/MANUSCRIPT.md
humanize_score: 38.4/100  (minor_residue)
profile:        academic  (3,420 words)
top offenders:
  - methodology_pseudo                weighted=12.50
  - significance_inflation            weighted=7.50
  - citation_laundering               weighted=5.00
  - hyphenated_pairs                  weighted=2.40
  - excessive_hedging                 weighted=1.50
```

```bash
# JSON output for CI / pipelines
python humanize_score.py --json --profile=docs README.md
```

### Hooked into commit time

The hook auto-fires after any `.md` / `.tex` Edit/Write, prints a warning when score > 60. Threshold tunable via `HUMANIZE_THRESHOLD=70` in your shell.

### Subagent for deep review

```
> Have the humanizer-reviewer audit this manuscript
```

The agent loads the file, runs the scorer, identifies top-5 offenders by line, rewrites them, self-audits, and reports back.

## Voice calibration

Drop a sample of your own writing and the skill will match your rhythm, vocabulary, and quirks rather than producing a generic "clean" rewrite:

```
/humanize --voice=blog-archive/2024-09-thoughts.md
[paste AI-generated draft]
```

## Domain profiles — at a glance

| Pattern | academic | docs | blog | commit |
|---|---|---|---|---|
| Em-dash overuse | OK in moderation | flag | flag | flag |
| Passive voice | OK in IMRaD methods | flag | flag in active voice | flag |
| Hedging | report-grade OK | flag | flag hard | flag hard |
| Stat parade | flag hard | flag | n/a | n/a |
| Citation laundering | flag hard | flag | flag | n/a |
| Manuscript boilerplate | flag hard | n/a | n/a | n/a |
| AI commit verbs | n/a | n/a | n/a | flag hard |

## Why six layers?

The blader/humanizer skill is excellent but **passive only** — Claude only humanises when you type `/humanizer`. Every other write goes through unfiltered. AI slop compounds across sessions because future sessions index "this is how we write here."

`humanize` closes the loop:

- The **rule** in `~/.claude/CLAUDE.md` puts the directive into every session prompt.
- The **hook** catches AI patterns at write-time, before they're committed.
- The **scorer** gives a number you can grep in CI and pre-commit.
- The **subagent** does the heavy review on demand.
- The **skill** does the manual cleanup with voice calibration.
- The **profiles** stop us from "fixing" passive voice in a methods section or em-dashes in an academic paper.

## Acknowledgments

This work would not exist without:

- [blader/humanizer](https://github.com/blader/humanizer) — MIT, the foundation
- [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — pattern catalog
- [WikiProject AI Cleanup](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_AI_Cleanup) — maintains the source

## License

MIT — see [LICENSE](LICENSE).

## Author

Kimal Honour Djam ([@kimhons](https://github.com/kimhons))
