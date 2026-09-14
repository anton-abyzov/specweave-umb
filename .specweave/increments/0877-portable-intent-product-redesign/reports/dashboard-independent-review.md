# Independent dashboard review

Reviewed original dashboard commit `b3d5df4053ecec955702b0895c286d8f783fbccc` against SpecWeave v2.0.3 in the separate `/tmp/specweave-0877-sync` worktree. Fix commit: `30d272e60`. All confirmed findings below are resolved. Parent owns final combined release checks.

## Findings and fixes

| Severity | Finding | Reproduction and resolution |
| --- | --- | --- |
| P1 | An unterminated final board history record swallowed the next acknowledged write. | In a disposable project, remove the final newline from a valid intent snapshot, then update revision 1. API/store acknowledged revision 2 but the next board contained no intent because both records became one invalid JSON line. The writer now checks the final byte and inserts a separator without changing existing bytes. Regressions cover both a valid final record without newline and an interrupted partial JSON record. |
| P2 | Open execution history never refreshed the independent native-session endpoint. | Headless E2E loaded `/sessions`, appended a new model to an existing local log, and created another local log while the page stayed open. It timed out at 35 seconds. The reconciliation timer now refetches session metadata whenever execution history or an intent dialog is open. The same unchanged regression passes for both continuation and new-session discovery. |
| P2 | Checklist-only legacy task counts disappeared; dashboard surfaces could disagree. | Existing async filesystem fixtures failed (2 tests). A separate real-file fixture confirmed checklist-only tasks returned zero instead of 3 total / 2 complete. A shared dashboard task reader now preserves legacy heading/checklist rows for board, increment list and detail. Parsed tasks and any existing ledger, including an empty ledger, always take precedence. Detail rows and statuses are verified alongside counts. Existing failing tests were not modified. |

## Persistence, projection and security assessment

- Board moves preserve increment metadata and verification. Declared intent state and engineering completion remain distinct; moving an intent to Done does not manufacture completed increment evidence.
- Existing optimistic revision checks reject stale writes from another browser window. History remains append-only. The newline fix retains malformed prior bytes and reports the bad line while allowing a new valid snapshot to persist.
- Ledger task states, spec acceptance criteria and verification reports remain authoritative. Shared legacy compatibility only applies when modern definitions and ledger state are absent. Engineering totals deduplicate linked increments.
- Local server binds to 127.0.0.1. Host validation rejects rebinding hosts, Origin validation rejects foreign origins, and JSON write requirements reject form bodies. The actual HTTP foreign-origin write test returns 403. No additional confirmed security blocker was found in the new work routes.
- Session metadata is project scoped and excludes prompt/response content. Observed model metadata, manually declared setup and ledger actor history remain distinguished. Large native logs explicitly disclose partial window coverage. This review does not claim worktree paths outside the selected project are automatically associated, universal harness coverage, inferred task intent, token-cost comparison or completion forecasting.

## Verification

All test data was disposable. Browser launch explicitly used `headless: true`; `PWDEBUG=0` and `PLAYWRIGHT_HTML_OPEN=never`. No personal browser or remote tracker writes.

- `npx vitest run tests/unit/dashboard tests/unit/core/dashboard/dashboard-data-aggregator.test.ts`: 25 files / 225 tests passed (`dashboard-review-tests.log`).
- Full `npm run build`: passed (`dashboard-review-build.log`).
- Client `npx tsc --noEmit -p src/dashboard/client/tsconfig.json`: exit 0 (`dashboard-review-client-tsc.log`).
- Final built-server headless E2E: all 13 flows passed (`dashboard-review-e2e.log`): modern ledger, create, accessible move, reload persistence, drag/drop, continuation, session association, ledger/spec/verification live refresh, evidence detail, origin rejection, native-session live refresh, mobile overflow and browser errors.
- Screenshots: `reports/artifacts/dashboard-independent-review/`, including `native-session-live-refresh.png`.
- Regression failure evidence: `dashboard-live-session-before-fix.log`, `dashboard-legacy-existing-before-fix.log`, `dashboard-legacy-real-before-fix.log`, and `dashboard-persistence-projection-before-fix.log`.
- `git diff --check` and commit malware/secret scan passed.

No version bump or publication was performed in this review lane.
