#!/bin/bash
# close-completed-issues.sh — PostToolUse hook
# Fires on any Edit/Write to metadata.json.
# Closes GitHub issues when increment status → completed.
# Living docs sync is handled by specweave complete → onIncrementDone().
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

# Cleanup: remove stale sync lock files from previous architecture (>60 min old)
find "$PROJECT_ROOT/.specweave/state/" -name ".sync-*.lock" -mmin +60 -delete 2>/dev/null

# Source GITHUB_TOKEN from .env (gh auth keyring may be invalid)
ENV_FILE="$PROJECT_ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
  GH_TOKEN_VAL=$(grep -E '^(GH_TOKEN|GITHUB_TOKEN)=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'")
  [[ -n "$GH_TOKEN_VAL" ]] && export GH_TOKEN="$GH_TOKEN_VAL"
fi

# Close GitHub issues for completed increment
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

exit 0
