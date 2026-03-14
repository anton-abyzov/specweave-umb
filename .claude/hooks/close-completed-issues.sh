#!/bin/bash
# close-completed-issues.sh — PostToolUse hook
# Fires on any Edit/Write to metadata.json.
# 1. Closes GitHub issues when increment status → completed
# 2. Triggers living docs sync (once per increment, guarded by marker file)
set +e

command -v jq >/dev/null 2>&1 || exit 0

FILE_PATH=$(jq -r '.tool_input.file_path // .file_path // ""')
[[ "$FILE_PATH" != */.specweave/increments/*/metadata.json ]] && exit 0

PROJECT_ROOT="${FILE_PATH%%/.specweave/*}"
CONFIG="$PROJECT_ROOT/.specweave/config.json"
[[ ! -f "$CONFIG" ]] && exit 0

INC_STATUS=$(jq -r '.status // ""' "$FILE_PATH" 2>/dev/null)
[[ "$INC_STATUS" != "completed" && "$INC_STATUS" != "done" ]] && exit 0

INC_DIR=$(dirname "$FILE_PATH")
INC_NAME=$(basename "$INC_DIR")
INC_ID="${INC_NAME%%-*}"   # e.g. "0523" from "0523-living-docs-sync-cleanup"

# === Section 1: Close GitHub issues ===
command -v gh >/dev/null 2>&1 && {
  read -r OWNER REPO GH_ENABLED < <(jq -r '[.sync.github.owner, .sync.github.repo, (.sync.github.enabled | tostring)] | @tsv' "$CONFIG" 2>/dev/null)
  if [[ "$GH_ENABLED" == "true" && -n "$OWNER" && -n "$REPO" ]]; then
    ISSUES=$(jq -r '
      .externalLinks.github.issues // {} | to_entries[] |
      select(.value.status != "closed" and .value.issueNumber != null) |
      [.key, (.value.issueNumber | tostring)] | @tsv
    ' "$FILE_PATH" 2>/dev/null)

    CLOSED=()
    while IFS=$'\t' read -r US_ID NUM; do
      [[ -z "$NUM" ]] && continue
      gh issue close "$NUM" --repo "$OWNER/$REPO" --comment "Increment $INC_NAME completed." 2>/dev/null && CLOSED+=("$US_ID")
    done < <(printf '%s\n' "$ISSUES")

    if [[ ${#CLOSED[@]} -gt 0 ]]; then
      CLOSED_JSON=$(printf '%s\n' "${CLOSED[@]}" | jq -R -s 'split("\n") | map(select(. != ""))')
      jq --argjson ids "$CLOSED_JSON" 'reduce $ids[] as $id (.; .externalLinks.github.issues[$id].status = "closed")' \
        "$FILE_PATH" > "${FILE_PATH}.tmp" && mv "${FILE_PATH}.tmp" "$FILE_PATH"
    fi
  fi
}

# === Section 2: Living docs sync (once per increment) ===
mkdir -p "$INC_DIR/reports"
SYNC_MARKER="$INC_DIR/reports/.living-docs-synced"
LOCK_FILE="$PROJECT_ROOT/.specweave/state/.sync-${INC_ID}.lock"

if [[ ! -f "$SYNC_MARKER" && ! -f "$LOCK_FILE" ]]; then
  command -v specweave >/dev/null 2>&1 && {
    mkdir -p "$PROJECT_ROOT/.specweave/state"
    touch "$LOCK_FILE"
    LOG="$INC_DIR/reports/living-docs-sync.log"
    # Run in background — sync calls GitHub/JIRA/ADO and can take 30-120s
    (
      cd "$PROJECT_ROOT" && \
      specweave sync-living-docs "$INC_ID" >> "$LOG" 2>&1
      touch "$SYNC_MARKER"
      rm -f "$LOCK_FILE"
    ) &
    disown
  }
fi

exit 0
