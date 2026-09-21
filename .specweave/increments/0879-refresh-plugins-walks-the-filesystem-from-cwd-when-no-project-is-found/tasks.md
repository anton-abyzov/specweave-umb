# Tasks: refresh-plugins walks the filesystem from cwd when no project is found

<!-- SW:BOARD -->
| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-02 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-03 | done | claude@antons-macbook-m4max | cd repositories/anton-abyzov/specweave && npx vitest run te… |  |
| T-04 | done | claude@antons-macbook-m4max | bash .specweave/increments/0879-refresh-plugins-walks-the-f… |  |

4/4 done · 0 skipped · 0 claimed · 0 blocked · 0 stale · 0 open
<!-- /SW:BOARD -->

### T-01 Bound the legacy-lockfile walk: no symlinks, max depth
- AC: AC-02 | Files: repositories/anton-abyzov/specweave/src/utils/cleanup-stale-plugins.ts, repositories/anton-abyzov/specweave/tests/unit/utils/cleanup-stale-lockfiles.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/utils/cleanup-stale-lockfiles.test.ts --config vitest.unit.config.ts
- [x] done by claude@antons-macbook-m4max 2026-09-21T20:33:41.916Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/utils/cleanup-stale-lockfiles.test.ts --config vite…

### T-02 refresh-plugins bails out with a clear message when no project is found
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specweave/src/cli/commands/refresh-plugins.ts, repositories/anton-abyzov/specweave/src/utils/find-project-root.ts, repositories/anton-abyzov/specweave/tests/unit/cli/commands/refresh-plugins.test.ts, repositories/anton-abyzov/specweave/tests/unit/commands/refresh-plugins.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/cli/commands/refresh-plugins.test.ts tests/unit/commands/refresh-plugins.test.ts tests/unit/refresh-plugins-adapter.test.ts --config vitest.unit.config.ts
- [x] done by claude@antons-macbook-m4max 2026-09-21T20:33:42.851Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/cli/commands/refresh-plugins.test.ts tests/unit/com…

### T-03 Guard the doctor/update stale-lockfile scan outside a project
- AC: AC-04 | Files: repositories/anton-abyzov/specweave/src/core/doctor/checkers/installation-health-checker.ts, repositories/anton-abyzov/specweave/tests/unit/core/doctor/checkers/installation-health-checker.test.ts | Test: cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/doctor/checkers/installation-health-checker.test.ts --config vitest.unit.config.ts
- [x] done by claude@antons-macbook-m4max 2026-09-21T20:33:43.788Z — cd repositories/anton-abyzov/specweave && npx vitest run tests/unit/core/doctor/checkers/installation-health-checker.te…

### T-04 Black-box proof: build, run from a temp dir and from the umbrella with timeouts
- AC: AC-01, AC-03 | Files: .specweave/increments/0879-refresh-plugins-walks-the-filesystem-from-cwd-when-no-project-is-found/scripts/blackbox.sh, .specweave/increments/0879-refresh-plugins-walks-the-filesystem-from-cwd-when-no-project-is-found/reports/blackbox.md | Test: bash .specweave/increments/0879-refresh-plugins-walks-the-filesystem-from-cwd-when-no-project-is-found/scripts/blackbox.sh
- [x] done by claude@antons-macbook-m4max 2026-09-21T20:33:45.150Z — bash .specweave/increments/0879-refresh-plugins-walks-the-filesystem-from-cwd-when-no-project-is-found/scripts/blackbox…
