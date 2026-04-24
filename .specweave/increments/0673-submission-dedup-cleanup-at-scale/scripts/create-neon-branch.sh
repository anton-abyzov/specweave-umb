#!/usr/bin/env bash
# create-neon-branch.sh — Create a zero-copy Neon branch from main for the 0673 dry-run.
#
# Purpose: produce a throw-away branch of production so the 0673 cleanup script can run
# against real data without touching prod. Prints only the pooled and non-pooled connection
# strings on stdout so callers can `eval` / capture them.
#
# Primary path: `neonctl branches create` (requires authenticated neonctl).
# Fallback:     Neon REST API via curl using $NEON_API_KEY (per AC-US2-01).
#
# Required env:
#   NEON_PROJECT_ID           — Neon project UUID (always required)
#   NEON_API_KEY              — required only if neonctl is absent or unauthenticated
#
# Usage:
#   NEON_PROJECT_ID=xxx bash create-neon-branch.sh
#
# Output (stdout, exactly three lines):
#   pooled=<postgres://...-pooler...>
#   direct=<postgres://...>
#   name=<branch-name>
#
# The `name=` line is the authoritative identifier for the branch we just
# created. Callers MUST use it (not `neonctl branches list | tail -1`) to
# derive the rollback/delete target — otherwise a concurrent branch
# creation between steps can cause the wrong branch to be captured.
#
# Exit codes:
#   0 — branch created, connection strings printed
#   non-zero — creation failed; see stderr for diagnostics

set -euo pipefail

log_err() { printf '%s\n' "create-neon-branch: $*" >&2; }
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

branch_name() {
  printf '0673-dryrun-%s' "$(date -u +%Y%m%d-%H%M%S)"
}

create_via_neonctl() {
  local name="$1"
  # `neonctl branches create` returns metadata; we don't use its stdout here.
  # --output json makes the output stable for future extension but we silence it.
  neonctl branches create \
    --project-id "$NEON_PROJECT_ID" \
    --parent main \
    --name "$name" \
    --output json \
    >/dev/null

  # Fetch pooled (the --pooled flag yields a pgbouncer pooler hostname).
  local pooled direct
  pooled=$(neonctl connection-string "$name" \
    --project-id "$NEON_PROJECT_ID" \
    --pooled) || fatal "neonctl connection-string --pooled failed"
  direct=$(neonctl connection-string "$name" \
    --project-id "$NEON_PROJECT_ID") || fatal "neonctl connection-string failed"

  printf 'pooled=%s\n' "$pooled"
  printf 'direct=%s\n' "$direct"
  printf 'name=%s\n' "$name"
}

create_via_api() {
  local name="$1"
  require_var NEON_API_KEY
  require_cmd curl
  require_cmd python3

  local api="https://console.neon.tech/api/v2"
  local body
  body=$(printf '{"branch":{"name":"%s","parent_id":null}}' "$name")

  # Parent not specified → Neon defaults to the project's primary branch (main).
  local resp
  resp=$(curl -fsS \
    -X POST \
    -H "Authorization: Bearer $NEON_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$body" \
    "$api/projects/$NEON_PROJECT_ID/branches") \
    || fatal "Neon REST API branch-create failed (curl non-zero)"

  # Extract the two connection_uris entries (pooled + direct) from the response.
  # Neon returns `connection_uris: [{connection_uri, connection_parameters}]`; the
  # pooled one has `.connection_parameters.pooler_host` set. We use python3 for
  # robust JSON parsing (jq is not guaranteed on operator machines).
  local pooled direct
  read -r pooled direct < <(python3 - "$resp" <<'PY'
import json, sys
data = json.loads(sys.argv[1])
uris = data.get("connection_uris", []) or []
pooled = ""
direct = ""
for u in uris:
    params = u.get("connection_parameters", {}) or {}
    host = params.get("host", "") or ""
    uri = u.get("connection_uri", "") or ""
    if "pooler" in host or "-pooler" in uri:
        pooled = uri
    else:
        direct = uri
# Fallback: if Neon returned only one URI, use it for both and let caller see.
if not direct and uris:
    direct = uris[0].get("connection_uri", "") or ""
if not pooled and uris:
    pooled = uris[-1].get("connection_uri", "") or ""
print(pooled or "", direct or "")
PY
)

  [[ -n "$pooled" && -n "$direct" ]] \
    || fatal "Neon API returned unexpected response (missing connection_uris)"

  printf 'pooled=%s\n' "$pooled"
  printf 'direct=%s\n' "$direct"
  printf 'name=%s\n' "$name"
}

main() {
  require_var NEON_PROJECT_ID

  local name
  name=$(branch_name)

  if command -v neonctl >/dev/null 2>&1; then
    create_via_neonctl "$name"
  else
    log_err "neonctl not found; falling back to Neon REST API"
    create_via_api "$name"
  fi
}

main "$@"
