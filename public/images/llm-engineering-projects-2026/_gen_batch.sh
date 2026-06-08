#!/bin/zsh
# Batch-generate the 15 part images for the LLM engineering projects post via codex exec.
set -u
CODEX=/Users/conanssam-m4/.npm-global/bin/codex
DIR=/Users/conanssam-m4/.openclaw/workspace-blogbot/content/images/llm-engineering-projects-2026
PROMPTS="$DIR/_prompts.txt"
STYLE='Hand-drawn technical sketch on off-white drawing paper, casual engineering notebook brainstorming aesthetic. Black ballpoint ink with warm yellow highlighter accents, neat legible handwritten English labels, minimal, clean, no photorealism, no clutter, no smooth gradients. Wide LANDSCAPE 3:2 composition (clearly wider than tall). SUBJECT:'

ok=0; fail=0
# read only lines containing the || delimiter
grep '||' "$PROMPTS" | while IFS= read -r line; do
  name="${line%%||*}"
  subj="${line#*||}"
  name="${name## }"; name="${name%% }"
  target="$DIR/${name}.png"
  if [[ -f "$target" ]] && [[ $(stat -f%z "$target" 2>/dev/null) -gt 100000 ]]; then
    echo "SKIP ${name}.png (already exists)"
    ok=$((ok+1))
    continue
  fi
  full="$STYLE $subj Save the resulting PNG as exactly ${name}.png in the current working directory, overwriting if it already exists, then run 'ls -l ${name}.png' to confirm."
  echo "===== GENERATING ${name} ====="
  "$CODEX" exec --full-auto -C "$DIR" "$full" </dev/null >/dev/null 2>&1
  if [[ -f "$target" ]]; then
    sz=$(stat -f%z "$target" 2>/dev/null)
    echo "OK  ${name}.png  (${sz} bytes)"
    ok=$((ok+1))
  else
    echo "FAIL ${name}.png  (not created)"
    fail=$((fail+1))
  fi
done
echo "===== BATCH DONE ====="
ls -l "$DIR"/part*.png 2>/dev/null
echo "part files present: $(ls "$DIR"/part*.png 2>/dev/null | wc -l | tr -d ' ') / 15"
