#!/bin/bash
# Exercise the real CLI with the umbrella's configured owner commands and an isolated product fixture.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="${SPECWEAVE_CLI:-$(command -v specweave)}"
FIXTURE="$(mktemp -d)"
trap 'rm -rf "$FIXTURE"' EXIT
export SPECWEAVE_WORKSPACE="$FIXTURE"
cd "$FIXTURE"
mkdir -p .specweave
jq '.testing | {testing: {strictClose, ownerCommands, commands: ["true"]}}' \
  "$ROOT/.specweave/config.json" > .specweave/config.json
jq -e '.testing.commands == [
  "python3 scripts/fleet-project-sync.py --self-test",
  "python3 -m unittest discover -s tests -p test_handoff_evidence.py",
  "python3 scripts/release/timing.py --self-test"
]' "$ROOT/.specweave/config.json" >/dev/null

reject() {
  local text="$1"
  shift
  if "$CLI" "$@" > result.log 2>&1; then
    echo "Unexpected success: $*" >&2
    exit 1
  fi
  if ! grep -Fq "$text" result.log; then
    cat result.log >&2
    exit 1
  fi
}

number=0
for repo in specwithcode-dev specweave-studio; do
  number=$((number + 1))
  owner="repositories/anton-abyzov/$repo"
  id="$(printf '%04d' "$number")-$repo"
  inc=".specweave/increments/$id"
  mkdir -p "$owner"
  printf '%s\n' '{"scripts":{"verify:pr":"bash verify.sh","test:server:sharded":"bash server.sh"}}' > "$owner/package.json"
  printf '%s\n' 'test -f ready || exit 99' > "$owner/verify.sh"
  printf '%s\n' 'test -f server-ready || exit 98' > "$owner/server.sh"
  "$CLI" create-increment Fixture --id "$id" --no-commit >/dev/null
  cat > "$inc/spec.md" <<SPEC
# Fixture

## Acceptance Criteria
- [x] AC-01: Run owner check.

## Tasks

### T-01 Verify owner
- AC: AC-01 | Files: $owner/src/example.ts | Test: true
SPEC
  reject 'exit 99' verify "$id" --cmd true
  touch "$owner/ready"
  reject 'exit 98' verify "$id" --cmd true
  touch "$owner/server-ready"
  "$CLI" verify "$id" >/dev/null
  jq -e --arg cwd "$owner" '.commands | map(select(.cwd == $cwd and .exit == 0 and .source == "config testing.ownerCommands")) | length == 2' \
    "$inc/reports/verify.json" >/dev/null
  reject T-01 complete "$id" --yes
  "$CLI" task done T-01 "$id" --run true --no-commit >/dev/null
  "$CLI" verify "$id" >/dev/null
  reject 'no reports/review.md' complete "$id" --yes
  printf '%s\n' 'Verdict: ship' > "$inc/reports/review.md"
  "$CLI" complete "$id" --yes >/dev/null
  jq -e '.status == "completed"' "$inc/metadata.json" >/dev/null
  echo "$repo: owner failure, working directory, task and review gates passed"
done
