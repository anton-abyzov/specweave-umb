# Tasks

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | codex@antons-macbook-m4max | cd repositories/anton-abyzov/0882-codex && npx vitest run t… |  |
| T-02 | done | codex@antons-macbook-m4max | node .specweave/increments/0882-finish-bounded-cli-filesyst… |  |

2/2 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 Guard LSP and dashboard and skip LSP symlinks
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/0882-codex/bin/specweave.js, repositories/anton-abyzov/0882-codex/src/cli/commands/lsp.ts, repositories/anton-abyzov/0882-codex/src/cli/commands/dashboard.ts, repositories/anton-abyzov/0882-codex/src/core/lsp/lsp-client.ts, repositories/anton-abyzov/0882-codex/tests/unit/cli/commands/scan-root-guards.test.ts, repositories/anton-abyzov/0882-codex/tests/unit/core/lsp/lsp-symlinks.test.ts, repositories/anton-abyzov/0882-codex/tests/unit/cli/commands/lsp-setup.test.ts, repositories/anton-abyzov/0882-codex/CHANGELOG.md | Test: cd repositories/anton-abyzov/0882-codex && npx vitest run tests/unit/cli/commands/scan-root-guards.test.ts tests/unit/cli/commands/lsp-setup.test.ts tests/unit/core/lsp/lsp-symlinks.test.ts --config vitest.unit.config.ts --maxWorkers=1
- [x] done by codex@antons-macbook-m4max 2026-09-22T03:27:10.978Z — cd repositories/anton-abyzov/0882-codex && npx vitest run tests/unit/cli/commands/scan-root-guards.test.ts tests/unit/c…

### T-02 Verify original PR and complete delivery
- AC: AC-04 | Files: repositories/anton-abyzov/0882-codex/scripts/e2e/bounded-scans.mjs, .specweave/increments/0882-finish-bounded-cli-filesystem-scans/reports/verification.md, .specweave/increments/0882-finish-bounded-cli-filesystem-scans/scripts/blackbox.mjs | Test: node .specweave/increments/0882-finish-bounded-cli-filesystem-scans/scripts/blackbox.mjs
- [x] done by codex@antons-macbook-m4max 2026-09-22T03:38:18.773Z — node .specweave/increments/0882-finish-bounded-cli-filesystem-scans/scripts/blackbox.mjs → exit 0 log: .specweave/incre…
