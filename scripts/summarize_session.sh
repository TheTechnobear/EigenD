#!/usr/bin/env zsh
# scripts/summarize_session.sh
# Create a compact session summary from a session transcript and append a resume line.
# Usage: ./scripts/summarize_session.sh [path/to/session.log]

set -euo pipefail

SESSION_FILE="${1:-.github/current_session.log}"
OUT_DIR=".github/session_summaries"
RESUME_FILE=".github/copilot-session_resume.md"

# thresholds (tweak as needed)
MAX_MESSAGES=${MAX_MESSAGES:-30}
MAX_TOKENS=${MAX_TOKENS:-8000}
KEEP_LAST=${KEEP_LAST:-5}

mkdir -p "$OUT_DIR"

if [ ! -f "$SESSION_FILE" ]; then
  echo "No session file found at '$SESSION_FILE'. Create one or pass path as first arg."
  exit 0
fi

# Detect message count using common transcript formats
MSG_COUNT=0
if grep -qE '^(User:|Assistant:)' "$SESSION_FILE"; then
  MSG_COUNT=$(grep -cE '^(User:|Assistant:)' "$SESSION_FILE" || echo 0)
elif grep -q '"role": "user"' "$SESSION_FILE" 2>/dev/null; then
  MSG_COUNT=$(grep -c '"role": "' "$SESSION_FILE" || echo 0)
else
  # fallback: non-empty lines roughly correspond to messages
  MSG_COUNT=$(awk 'NF{c++}END{print c+0}' "$SESSION_FILE")
fi

# Estimate tokens: prefer tiktoken if available, otherwise fall back to words*0.75 heuristic
EST_TOKENS=$(python3 - <<'PY'
import sys, json
path = sys.argv[1]
text = open(path, 'rb').read().decode('utf-8', errors='ignore')
try:
    import tiktoken
    enc = tiktoken.get_encoding('cl100k_base')
    toks = len(enc.encode(text))
    print(toks)
except Exception:
    wc = len(text.split())
    print(int(wc * 0.75))
PY
"$SESSION_FILE")

if [ "$MSG_COUNT" -le "$MAX_MESSAGES" ] && [ "$EST_TOKENS" -le "$MAX_TOKENS" ]; then
  echo "Session under thresholds (messages=$MSG_COUNT tokens≈$EST_TOKENS). No summarisation required."
  exit 0
fi

TIMESTAMP=$(date +%F_%H%M%S)
OUT_FILE="$OUT_DIR/${TIMESTAMP}_session_summary.md"

{
  echo "Date: $(date +%F)"
  echo "SessionID: ${TIMESTAMP}"
  echo ""
  echo "Summary (auto-generated):"
  echo ""
  echo "- Messages: $MSG_COUNT"
  echo "- Estimated tokens: $EST_TOKENS"
  echo "- Kept last $KEEP_LAST messages verbatim below."
  echo ""
  echo "Key decisions / TODOs (auto-extracted heuristics):"
  grep -iE 'todo|decid|fix|refactor|follow up|action item|next step' "$SESSION_FILE" | sed 's/^/  - /' | head -n 20 || echo "  - (no obvious TODO/decision lines found)"
  echo ""
  echo "Files mentioned (heuristic):"
  grep -oE '([./~]?[A-Za-z0-9_./-]+\.[A-Za-z0-9_-]{1,8})' "$SESSION_FILE" | sort -u | sed 's/^/  - /' | head -n 40 || echo "  - (none found)"
  echo ""
  echo "Last $KEEP_LAST messages:" 
  echo '```'
  # Print last KEEP_LAST messages simply: find lines beginning with User: or Assistant: and print last N entries and their following lines until next speaker marker (crude but practical)
  awk -v keep=$KEEP_LAST 'BEGIN{RS=""; FS="\n"} {for(i=1;i<=NF;i++) if($i~/^(User:|Assistant:)/) print $i"\n"} ' "$SESSION_FILE" | tail -n $KEEP_LAST
  echo '```'
  echo ""
  echo "Notes: manually review and refine this summary. If ready, append a one-line entry to $RESUME_FILE."
} > "$OUT_FILE"

echo "Wrote summary to $OUT_FILE"

# Append a one-line resume entry
RESUME_LINE="$(date +%F): summarised session ${TIMESTAMP} (messages=${MSG_COUNT}, tokens≈${EST_TOKENS})"
echo "$RESUME_LINE" >> "$RESUME_FILE"
echo "Appended resume line to $RESUME_FILE"

exit 0
