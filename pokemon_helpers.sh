#!/bin/bash
# Pokemon Agent Helper - Stuck Detection & Smart Navigation

SERVER="http://localhost:8765"
SCREENSHOT_PATH="/Users/conanssam-m4/.openclaw/workspace-blogbot/pkm_helper.png"

# Get current map info
get_state() {
  curl -s "$SERVER/state"
}

# Compare two states - returns 0 if identical (stuck), 1 if changed
state_changed() {
  local before="$1"
  local after="$2"
  local bp=$(echo "$before" | python3 -c "import sys,json;s=json.load(sys.stdin);print(s['player']['position']['y'],s['player']['position']['x'],s['map']['map_name'],s['dialog']['active'])" 2>/dev/null)
  local ap=$(echo "$after" | python3 -c "import sys,json;s=json.load(sys.stdin);print(s['player']['position']['y'],s['player']['position']['x'],s['map']['map_name'],s['dialog']['active'])" 2>/dev/null)
  [[ "$bp" != "$ap" ]] && return 1 || return 0
}

# Screenshot hash - detect if screen actually changed (pixel-level)
screenshot_hash() {
  curl -s "$SERVER/screenshot" -o "$SCREENSHOT_PATH" 2>/dev/null
  md5 -q "$SCREENSHOT_PATH" 2>/dev/null
}

# Smart action - sends action, checks if state changed, retries if stuck
smart_action() {
  local actions="$1"
  local max_retries="${2:-3}"
  
  local hash_before=$(screenshot_hash)
  local state_before=$(get_state)
  
  # Send action
  curl -s -X POST "$SERVER/action" -H "Content-Type: application/json" -d "{\"actions\":[$actions]}" > /dev/null 2>&1
  
  local hash_after=$(screenshot_hash)
  
  # Check screenshot change (most reliable)
  if [[ "$hash_before" != "$hash_after" ]]; then
    echo "MOVED (screenshot changed)"
    return 0
  fi
  
  echo "STUCK (screenshot identical)"
  return 1
}

# Get full game info
game_info() {
  curl -s "$SERVER/state" | python3 -c "
import sys,json
s=json.load(sys.stdin)
p=s['player']
print(f'Map: {s[\"map\"][\"map_name\"]} ({s[\"map\"][\"map_id\"]})')
print(f'Pos: {p[\"position\"]}, Facing: {p[\"facing\"]}')
print(f'Dialog: {s[\"dialog\"][\"active\"]}, Battle: {s[\"battle\"][\"in_battle\"]}')
print(f'Party: {len(s[\"party\"])} Pokemon, Money: {p[\"money\"]}')
for m in s.get('party',[]):
    print(f'  {m.get(\"species\",\"?\")} HP:{m.get(\"hp\",\"?\")}/{m.get(\"max_hp\",\"?\")} Lv:{m.get(\"level\",\"?\")}')
"
}

case "${1:-info}" in
  info) game_info ;;
  hash) screenshot_hash ;;
  stuck) 
    H1=$(screenshot_hash)
    sleep 1
    H2=$(screenshot_hash)
    if [[ "$H1" == "$H2" ]]; then echo "STUCK"; else echo "MOVING"; fi
    ;;
esac
