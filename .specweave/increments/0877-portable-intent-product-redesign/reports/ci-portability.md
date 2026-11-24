# CI portability repairs — T-14

Scope: test fixtures only, in `/tmp/specweave-0877-sync`. All behavioral assertions remain; no tests skipped, thresholds relaxed, or production behavior changed. Node 22.20.0. No browser automation or remote writes.

## Confirmed causes and changes

| Failure | Cause | Repair |
|---|---|---|
| 6 sync-throttle wiring unit tests | Source root hardcoded to Anton’s checkout; missing on GitHub Linux runner. | Resolve repository root from `import.meta.url`; test reads this worktree’s actual source. |
| 9 interactive init unit tests | TTY mocked interactive, but inherited `CI=true` / `GITHUB_ACTIONS=true` still selects noninteractive mode. | Clear all five recognized CI environment indicators inside the interactive fixtures and restore them after each test. Separate CI detection tests remain unchanged and pass. |
| 5 project-validation unit tests | Fixture placed directly in system temp; resolving two parents writes and deletes `/.specweave/config.json` on Linux. | Create a complete disposable project with `.specweave/increments/0001-test`; config and cleanup stay inside that fixture root. |
| 11 lifecycle CLI E2E tests | `init` refuses system-temp projects without explicit `--force`. macOS `/var` versus `/private/var` aliases masked this guard locally. | Disposable init fixtures explicitly pass `--force`, with `--quick` for deterministic noninteractive setup. Production temp-path guard remains unchanged. |
| 1 legacy pre-commit E2E | Fixture declared `/bin/sh` but contains Bash arrays. Linux dash fails syntax parsing before the intended legacy validation. | Declare Bash in the legacy fixture. The existing assertion still verifies the exact “ONLY 4 files allowed” rejection. |

## Evidence

Original Linux CI output: `ci-portability-original-github-failures.log` (22 unit failures and 13 E2E failures). Two old dashboard counter failures belong to T-08, which already repaired them without changing those failing tests.

Before repair:
- `CI=true GITHUB_ACTIONS=true npx vitest run` on the three interactive init files: 9 failed, 33 passed (`ci-portability-unit-red.log`).
- `TMPDIR=/private/tmp CI=true GITHUB_ACTIONS=true npx vitest run --config vitest.e2e.config.ts` on the three lifecycle files: 11 failed, 8 passed (`ci-portability-e2e-red.log`). The canonical temp path removes the macOS alias that otherwise hid the Linux guard failure.
- `dash -n tests/fixtures/git-hooks/pre-commit-1x.template`: exit 2, array syntax error (`ci-portability-legacy-shell-red.log`).
- Hardcoded source-path ENOENT and unsafe `/.specweave` EACCES are directly evidenced in original Linux CI. The unsafe fixture was not rerun before repair, to avoid deleting an external config.

After repair, with `TMPDIR=/private/tmp CI=true GITHUB_ACTIONS=true PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never`:
- Unit: 6 files, 61 tests passed, exit 0 (`ci-portability-unit-green.log`). Covers all five repaired unit files plus unchanged `init-ci-detection.test.ts`.
- CLI E2E config: 4 files, 31 tests passed, exit 0 (`ci-portability-e2e-green.log`). Covers all three repaired lifecycle suites and unchanged `update-command.e2e.ts`.
- Default workflow Vitest config (the same config used by `npm run test:e2e`): the same 4 affected files and 31 tests passed, exit 0 (`ci-portability-workflow-e2e-green.log`).
- `bash -n tests/fixtures/git-hooks/pre-commit-1x.template` and `git diff --check`: exit 0.

The source build was already current from the preceding committed dashboard/sync verification; this repair changes only tests and a test hook fixture. These are local macOS checks that reproduce the relevant CI environment and canonical temp-path semantics, not a claim that Linux GitHub CI has rerun.

## Remaining baseline

The original CI also failed the pre-existing performance comparison `tests/e2e/lsp/lsp-vs-grep-comparison.test.ts:86`: measured 26.0618 ms versus the 24.1391 ms bound (`avgGrep * 2`). This task deliberately leaves that timing-only assertion and its test unchanged. Root coordinates the fresh full CI run. T-15 separately owns Windows session filename portability and documentation server readiness.
