#!/usr/bin/env bash
# humanize-post-write.sh
# PostToolUse hook for Claude Code. Fires after Write/Edit. Runs the humanize scorer
# on prose files (.md, .tex, .rst, .txt) outside .claude/ and prints a warning if
# the score exceeds the threshold.
#
# Wire into ~/.claude/settings.json:
#   "hooks": {
#     "PostToolUse": [
#       {
#         "matcher": "Edit|Write",
#         "hooks": [
#           {"type": "command", "command": "bash ~/.claude/hooks/humanize-post-write.sh \"${TOOL_FILE_PATH}\""}
#         ]
#       }
#     ]
#   }
#
# Threshold defaults to 60. Override via HUMANIZE_THRESHOLD env var.

set -u

FILE_PATH="${1:-}"
THRESHOLD="${HUMANIZE_THRESHOLD:-60}"
SCORER="${HUMANIZE_SCORER:-$HOME/.claude/skills/humanize/scripts/humanize_score.py}"

# Bail conditions: empty path, doesn't exist, in .claude/ infra, not prose.
[[ -z "$FILE_PATH" ]] && exit 0
[[ ! -f "$FILE_PATH" ]] && exit 0
[[ "$FILE_PATH" == *".claude/"* ]] && exit 0
[[ "$FILE_PATH" == *"/node_modules/"* ]] && exit 0
[[ "$FILE_PATH" == *"/.git/"* ]] && exit 0

case "$FILE_PATH" in
    *.md|*.tex|*.rst|*.txt) : ;;
    *) exit 0 ;;
esac

# Bail if scorer not installed
[[ ! -f "$SCORER" ]] && exit 0

# Run scorer; capture exit + score
RESULT=$(python "$SCORER" --json --threshold="$THRESHOLD" "$FILE_PATH" 2>/dev/null)
EXIT=$?

if [[ -z "$RESULT" ]]; then
    exit 0
fi

SCORE=$(echo "$RESULT" | python -c "import sys, json; print(json.load(sys.stdin)['score'])" 2>/dev/null)
VERDICT=$(echo "$RESULT" | python -c "import sys, json; print(json.load(sys.stdin)['verdict'])" 2>/dev/null)

if [[ "$EXIT" -eq 1 ]]; then
    TOP=$(echo "$RESULT" | python -c "
import sys, json
d = json.load(sys.stdin)
for off in d['top_offenders'][:3]:
    print(f\"   - {off['pattern']} (weighted={off['weighted']})\")
" 2>/dev/null)
    echo ""
    echo "[humanize-warn] $FILE_PATH"
    echo "[humanize-warn] score=$SCORE/100 ($VERDICT) — exceeds threshold $THRESHOLD"
    echo "[humanize-warn] top offenders:"
    echo "$TOP"
    echo "[humanize-warn] consider: /humanize $FILE_PATH"
fi

exit 0
