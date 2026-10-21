#!/bin/bash
# 0982 headless routines checks at the released source (fictional fixtures only).
# Starts both fixture servers, runs the three checks, stops only the PIDs it started.
set -euo pipefail
WT=/Users/antonabyzov/.specwithcode/m4/worktrees/routines-layout-verify
OUT=${1:-/Users/antonabyzov/.specwithcode/m4/evidence/routines-layout/verify-1.0.66}
export PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH
export PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never
export PLAYWRIGHT_MODULE=$WT/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core/index.mjs
export PLAYWRIGHT_EXECUTABLE_PATH=/Users/antonabyzov/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell
mkdir -p "$OUT"
for port in 5788 5796; do
  if lsof -t -iTCP:$port -sTCP:LISTEN >/dev/null; then echo "port $port busy" >&2; exit 2; fi
done
CHECKS=${CHECKS:-$WT/apps/web/tests}
cd "$WT"
(cd apps/web && PROJECT_UI_PORT=5788 exec node tests/project-workspace/serve.mjs >"$OUT/serve-pane.log" 2>&1) & PANE=$!
PROJECT_UI_PORT=5796 node apps/web/tests/settings-presentation/serve.mjs >"$OUT/serve-settings.log" 2>&1 & SETTINGS=$!
trap 'kill $PANE $SETTINGS 2>/dev/null || true' EXIT
for i in $(seq 1 90); do
  curl -s -o /dev/null http://127.0.0.1:5788/ && curl -s -o /dev/null http://127.0.0.1:5796/ && break
  sleep 2
done
UI_EVIDENCE_DIR=$OUT ROUTINES_PREFIX=verify PROJECT_UI_PORT=5788 node "$CHECKS/project-workspace/routines-layout-check.mjs"
UI_EVIDENCE_DIR=$OUT ROUTINES_PREFIX=verify PROJECT_UI_PORT=5796 node "$CHECKS/settings-presentation/routines-check.mjs"
UI_EVIDENCE_DIR=$OUT/0980 PROJECT_UI_OUTPUT=$OUT/0980 PROJECT_UI_PORT=5788 node "$CHECKS/project-workspace/routines-check.mjs"
