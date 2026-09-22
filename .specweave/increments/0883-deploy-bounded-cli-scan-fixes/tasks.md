# Tasks

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/0883-release && npm run build … |  |
| T-02 | claimed | codex@antons-macbook-m4max |  |  |

1/2 done · 0 skipped · 1 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 Prepare and verify combined stable patch
- AC: AC-02 | Files: repositories/anton-abyzov/0883-release | Test: cd repositories/anton-abyzov/0883-release && npm run build && npm run lint:skills && npm run lint:docs-refs && node scripts/e2e/bounded-scans.mjs
- [x] done by codex@antons-macbook-m4max 2026-09-22T04:49:40.582Z — cd repositories/anton-abyzov/0883-release && npm run build && npm run lint:skills && npm run lint:docs-refs && node scr…

### T-02 Merge, publish, and verify registry artifact
- AC: AC-01, AC-03, AC-04 | Files: .specweave/increments/0883-deploy-bounded-cli-scan-fixes/reports | Test: npm view specweave@2.3.0 version
- [ ] claimed by codex@antons-macbook-m4max since 2026-09-22T04:53:32.385Z
