#!/usr/bin/env bash
# install.sh — install humanize globally into Claude Code config.
# Idempotent. Re-run to update.

set -e

CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[install] CLAUDE_HOME = $CLAUDE_HOME"
echo "[install] REPO_DIR    = $REPO_DIR"

# 1. Skill
mkdir -p "$CLAUDE_HOME/skills/humanize"
cp -r "$REPO_DIR"/SKILL.md "$CLAUDE_HOME/skills/humanize/"
mkdir -p "$CLAUDE_HOME/skills/humanize/scripts"
cp "$REPO_DIR/scripts/humanize_score.py" "$CLAUDE_HOME/skills/humanize/scripts/"
chmod +x "$CLAUDE_HOME/skills/humanize/scripts/humanize_score.py"
echo "[install] skill installed at $CLAUDE_HOME/skills/humanize/"

# 2. Subagent
mkdir -p "$CLAUDE_HOME/agents"
cp "$REPO_DIR/agents/humanizer-reviewer.md" "$CLAUDE_HOME/agents/"
echo "[install] agent installed at $CLAUDE_HOME/agents/humanizer-reviewer.md"

# 3. Always-on rule
mkdir -p "$CLAUDE_HOME/rules"
cat > "$CLAUDE_HOME/rules/10-anti-slop.md" <<'EOF'
# Rule 10 — Anti-slop discipline

**Always on.** Every prose token I write passes through this filter.

## The 15 things I do not do

1. No "delve", "tapestry", "landscape", "testament", "underscore", "intricate", "interplay", "pivotal", "foster", "enduring".
2. No "stands as", "serves as", "marking a pivotal moment in the evolution of".
3. No "Studies show" / "research suggests" without an inline citation.
4. No em-dashes outside academic contexts (≤1 per paragraph there).
5. No rule-of-three constructions when two or four items would do.
6. No "It's not just X, it's Y" parallelisms.
7. No emojis as bullets or headings.
8. No "Great question!", "I hope this helps", "Let me know if".
9. No knowledge-cutoff disclaimers ("As of my last training update").
10. No "It can be argued that" when a stance is required.
11. No "in order to", "due to the fact that", "at this point in time".
12. No filler conclusions ("The future looks bright").
13. No methodology pseudo-precision ("careful evaluation", "rigorous analysis").
14. No commit verbs that say nothing ("improves", "enhances", "refines").
15. No fragmented headers (heading + 1-line restatement).

## When in doubt

Run `~/.claude/skills/humanize/scripts/humanize_score.py FILE.md`. If score >40, edit before shipping. If score >60, the PostToolUse hook will warn me. The `humanizer-reviewer` agent does the deep pass.

## Profile-aware exceptions

The /humanize skill at `~/.claude/skills/humanize/SKILL.md` contains the full 38-pattern catalogue with profile carve-outs (academic / docs / blog / commit).

## Why

AI slop compounds across sessions. Future Claude reads my output and learns "this is how we write here." Every untreated pattern strengthens the next session's tendency to repeat it. Catch it at write-time or it becomes the house style.
EOF
echo "[install] rule installed at $CLAUDE_HOME/rules/10-anti-slop.md"

# 4. Hook (the user must register this in settings.json manually; we just place the script)
mkdir -p "$CLAUDE_HOME/hooks"
cp "$REPO_DIR/hooks/humanize-post-write.sh" "$CLAUDE_HOME/hooks/"
chmod +x "$CLAUDE_HOME/hooks/humanize-post-write.sh"
echo "[install] hook script at $CLAUDE_HOME/hooks/humanize-post-write.sh"
echo "[install] (manual step) wire it into ~/.claude/settings.json under hooks.PostToolUse"

# 5. Smoke-test the scorer
echo ""
echo "[install] smoke-test the scorer..."
echo "Studies show that this delves into the intricate landscape." > /tmp/humanize_smoke.md
python "$CLAUDE_HOME/skills/humanize/scripts/humanize_score.py" /tmp/humanize_smoke.md || true
rm /tmp/humanize_smoke.md

echo ""
echo "[install] done. Next steps:"
echo "  1. Append a §'Anti-slop discipline' section to ~/.claude/CLAUDE.md pointing to ~/.claude/rules/10-anti-slop.md"
echo "  2. Wire the hook into ~/.claude/settings.json (see hooks/humanize-post-write.sh comment)"
echo "  3. Try: /humanize [paste some AI text]"
