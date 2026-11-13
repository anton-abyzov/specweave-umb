#!/bin/bash
# T-05 check: origin/main of anton-abyzov/specwithcode states MIT everywhere, the brand audit
# passes on it, and the published npm package says MIT. Runs on an exported tree with a
# temporary index, so the shared specwithcode-dev checkout (one slot, owned by the queue holder)
# is read but never changed.
set -euo pipefail
UMB="$(cd "$(dirname "$0")/../../.." && pwd)"
REPO="$UMB/repositories/anton-abyzov/specwithcode-dev"
git -C "$REPO" fetch -q origin main
REF="$(git -C "$REPO" rev-parse origin/main)"
X="$(mktemp -d /tmp/t05-mit.XXXXXX)"
trap 'rm -rf "$X" "$X.index"' EXIT
git -C "$REPO" archive "$REF" | tar -x -C "$X"
git -C "$REPO" ls-tree -r "$REF" | awk '$1=="160000"{print $4}' | while read -r p; do mkdir -p "$X/$p"; done
echo "origin/main $REF"
cd "$X"
node --test scripts/studio-fleet/npm-package.test.mjs scripts/studio-fleet/runtime-package.test.mjs 2>&1 | grep -E '^# (pass|fail)'
GIT_DIR="$REPO/.git" GIT_WORK_TREE="$X" GIT_INDEX_FILE="$X.index" git read-tree "$REF"
GIT_DIR="$REPO/.git" GIT_WORK_TREE="$X" GIT_INDEX_FILE="$X.index" node scripts/studio-brand-audit.mjs 2>&1 | grep -E '"checks(Passed|Failed)"'
GIT_DIR="$REPO/.git" GIT_WORK_TREE="$X" GIT_INDEX_FILE="$X.index" node scripts/studio-brand-audit.mjs >/dev/null 2>&1
! grep -rn -E 'UNLICENSED|LicenseRef-proprietary' apps/desktop/resources/linux apps/mobile/modules/*/*.podspec scripts/build-desktop-artifact.ts scripts/studio-fleet/npm-package.mjs scripts/studio-fleet/runtime-package.mjs
LICENSE_ON_NPM="$(npm view specwithcode license)"
echo "npm view specwithcode license: $LICENSE_ON_NPM (latest $(npm view specwithcode version))"
test "$LICENSE_ON_NPM" = "MIT"
