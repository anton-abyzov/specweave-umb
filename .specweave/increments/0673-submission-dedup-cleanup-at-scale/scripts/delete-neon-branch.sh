#!/usr/bin/env bash
# delete-neon-branch.sh — Delete a Neon branch created by create-neon-branch.sh.
#
# Primary path: `neonctl branches delete` by name.
# Fallback:     Neon REST API via curl — look up branch id by name, then DELETE.
#
# Required env:
#   NEON_PROJECT_ID           — Neon project UUID
#   NEON_API_KEY              — required only if neonctl is absent
#
# Usage:
#   NEON_PROJECT_ID=xxx bash delete-neon-branch.sh <branch-name>
#
# Example:
#   bash delete-neon-branch.sh 0673-dryrun-20260422-180000
#
# Exit codes:
#   0 — branch deleted (prints "deleted <name>" to stdout)
#   non-zero — deletion failed; see stderr

set -euo pipefail

log_err() { printf '%s\n' "delete-neon-branch: $*" >&2; }
fatal()   { log_err "$*"; exit 1; }

require_var() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    fatal "required env var \$$name is not set"
  fi
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fatal "required command not found: $1"
}

usage() {
  cat >&2 <<EOF
Usage: NEON_PROJECT_ID=xxx bash delete-neon-branch.sh <branch-name>
EOF
  exit 2
}

delete_via_neonctl() {
  local name="$1"
  neonctl branches delete "$name" \
    --project-id "$NEON_PROJECT_ID" \
    >/dev/null \
    || fatal "neonctl branches delete failed for $name"
}

delete_via_api() {
  local name="$1"
  require_var NEON_API_KEY
  require_cmd curl
  require_cmd python3

  local api="https://console.neon.tech/api/v2"

  # Step 1: list branches, find the id by name.
  local list_resp
  list_resp=$(curl -fsS \
    -H "Authorization: Bearer $NEON_API_KEY" \
    "$api/projects/$NEON_PROJECT_ID/branches") \
    || fatal "Neon REST API branch-list failed (curl non-zero)"

  local branch_id
  branch_id=$(python3 - "$list_resp" "$name" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
target = sys.argv[2]
for b in data.get("branches", []) or []:
    if b.get("name") == target:
        print(b.get("id", ""))
        break
PY
)

  [[ -n "$branch_id" ]] || fatal "branch not found: $name"

  # Step 2: DELETE by id.
  curl -fsS \
    -X DELETE \
    -H "Authorization: Bearer $NEON_API_KEY" \
    "$api/projects/$NEON_PROJECT_ID/branches/$branch_id" \
    >/dev/null \
    || fatal "Neon REST API branch-delete failed for $branch_id ($name)"
}

main() {
  [[ $# -eq 1 && -n "${1:-}" ]] || usage
  local name="$1"

  require_var NEON_PROJECT_ID

  if command -v neonctl >/dev/null 2>&1; then
    delete_via_neonctl "$name"
  else
    log_err "neonctl not found; falling back to Neon REST API"
    delete_via_api "$name"
  fi

  printf 'deleted %s\n' "$name"
}

main "$@"
