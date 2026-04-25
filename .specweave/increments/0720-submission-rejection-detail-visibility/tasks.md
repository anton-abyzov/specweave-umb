# Tasks: Submission rejection detail visibility

> **TDD discipline**: Every GREEN task is preceded by a failing-test (RED) task. Tasks satisfy ACs from spec.md. Paths are relative to `repositories/anton-abyzov/vskill-platform/`.

## Phase 1 — US-002 backend foundation (synthetic ScanResult helper)

### T-001: RED — failing tests for `writeSyntheticScanResult` shape per kind
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given each `kind ∈ { blocklist, recovery-no-scan, admin-reject, admin-block, repo-block }` → When `writeSyntheticScanResult(submissionId, { kind, reason })` is called against a fresh KV/DB stub → Then a `StoredScanResult` is persisted with exactly one finding whose `patternId === kind`, `severity` matches the FR-002 default, `match === reason`, `concerns: [reason]`, and `findingsCount === 1`.
**Files**: `src/lib/submission/__tests__/synthetic-scan-result.test.ts` (NEW)

### T-002: GREEN — implement `writeSyntheticScanResult` helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, FR-001, FR-002 | **Status**: [x] completed
**Test Plan**: Given the failing tests from T-001 → When the helper is implemented to construct a `StoredScanResult` (tier=0, verdict="FAIL", score=0) with one synthetic finding from `KIND_DEFAULTS` and call existing `storeScanResult` → Then T-001 tests pass.
**Files**: `src/lib/submission/synthetic-scan-result.ts` (NEW)

### T-003: RED — failing tests for idempotency / skip-when-real-scan-exists
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 (idempotency clause), FR-003 | **Status**: [x] completed
**Test Plan**: Given a submission that already has a real `ScanResult` (finding with non-synthetic `patternId`) → When `writeSyntheticScanResult` is called → Then the existing scan is preserved (no overwrite). Given a submission with a prior synthetic ScanResult of the same `kind` → When called again with new reason → Then the row is upserted (last-write-wins on `match`/`context`/`concerns`).
**Files**: `src/lib/submission/__tests__/synthetic-scan-result.test.ts` (extend)

### T-004: GREEN — add idempotency guard to `writeSyntheticScanResult`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, FR-003 | **Status**: [x] completed
**Test Plan**: T-003 tests pass after introducing a `getSubmissionFull(id)` lookup that detects existing real findings and returns early.
**Files**: `src/lib/submission/synthetic-scan-result.ts` (modify)

## Phase 2 — US-002 wiring into 5 bare paths

### T-005: RED — failing test for early blocklist in `process-submission.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given a submission whose URL hits the blocklist → When `processSubmission` runs → Then `writeSyntheticScanResult` is invoked with `{ kind: "blocklist", reason: blocklistEntry.reason, evidenceUrls: blocklistEntry.evidenceUrls }` BEFORE the state transition to `BLOCKED`.
**Files**: `src/lib/queue/__tests__/process-submission-blocklist.test.ts` (NEW or extend existing)

### T-006: GREEN — wire `process-submission.ts:250` to call helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: T-005 passes. State transition order preserved.
**Files**: `src/lib/queue/process-submission.ts` (modify line ~250)

### T-007: RED — failing test for early blocklist in `finalize-scan/route.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a finalize-scan callback whose URL hits the blocklist → When the route handler runs → Then `writeSyntheticScanResult({ kind: "blocklist", … })` is invoked before the BLOCKED transition.
**Files**: `src/app/api/v1/internal/finalize-scan/__tests__/blocklist.test.ts` (NEW or extend)

### T-008: GREEN — wire `finalize-scan/route.ts:279`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: T-007 passes.
**Files**: `src/app/api/v1/internal/finalize-scan/route.ts` (modify line ~279)

### T-009: RED — failing test for recovery-no-scan path
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given a stuck submission with no prior scan → When recovery resolves it → Then `writeSyntheticScanResult({ kind: "recovery-no-scan", reason: "Submission expired before scanning completed" })` is called before the REJECTED transition.
**Files**: `src/lib/queue/__tests__/recovery.test.ts` (NEW or extend)

### T-010: GREEN — wire `recovery.ts:120`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan**: T-009 passes.
**Files**: `src/lib/queue/recovery.ts` (modify ~line 120)

### T-011: RED — failing tests for admin reject + block endpoints
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Test Plan**: For both `/admin/submissions/[id]/reject` and `/block`: Given a submission with NO prior scanResult → When admin POSTs with `{ reason }` → Then synthetic ScanResult is written with the appropriate kind. Given a submission WITH a prior scanResult → When admin POSTs → Then the prior scan is preserved (no synthetic write).
**Files**: `src/app/api/v1/admin/submissions/[id]/reject/__tests__/route.test.ts` (extend), `src/app/api/v1/admin/submissions/[id]/block/__tests__/route.test.ts` (extend)

### T-012: GREEN — wire admin reject + block endpoints
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Test Plan**: T-011 passes.
**Files**: `src/app/api/v1/admin/submissions/[id]/reject/route.ts`, `src/app/api/v1/admin/submissions/[id]/block/route.ts` (modify both)

### T-013: RED — failing test for repo-block synthesizes per affected submission
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Test Plan**: Given a repo-block call affecting 3 submissions, none with prior scans → When the route handler runs → Then `writeSyntheticScanResult` is called 3 times with `kind: "repo-block"`. Submissions with prior scans are skipped.
**Files**: `src/app/api/v1/admin/repo-block/__tests__/route.test.ts` (NEW or extend)

### T-014: GREEN — wire `repo-block/route.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Test Plan**: T-013 passes.
**Files**: `src/app/api/v1/admin/repo-block/route.ts` (modify)

### T-015: REGRESSION — verify detail-rich paths unchanged
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed
**Test Plan**: Given the existing scanner-pipeline test suite (Tier 1, Tier 2, dependency, script scan) → When run unchanged → Then all tests pass and produce real findings (not synthetic).
**Files**: `src/lib/scanner/__tests__/**`, `src/app/api/v1/internal/finalize-scan/__tests__/**` (run only)

## Phase 3 — US-001 UI fallback

### T-016: RED — failing test for `RejectionReasonCard` with `blockInfo`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given a `<RejectionReasonCard scanResult={null} state="BLOCKED" blockInfo={{...}} stateHistory={[]} />` → When rendered → Then DOM contains the reason text, threatType badge, severity-colored border, and clickable evidence URL anchors.
**Files**: `src/app/submit/[id]/__tests__/RejectionReasonCard.test.tsx` (NEW)

### T-017: GREEN — implement `RejectionReasonCard` blockInfo branch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: T-016 passes.
**Files**: `src/app/submit/[id]/RejectionReasonCard.tsx` (NEW)

### T-018: RED — failing test for stateHistory fallback
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given `state="REJECTED"`, `blockInfo=null`, `stateHistory=[{ state:"RECEIVED",… }, { state:"REJECTED", message:"Tier 1 score 35/100", timestamp:"…" }]` → When rendered → Then DOM contains "Tier 1 score 35/100" pulled from the latest terminal entry.
**Files**: `src/app/submit/[id]/__tests__/RejectionReasonCard.test.tsx` (extend)

### T-019: GREEN — extend RejectionReasonCard with stateHistory walker
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: T-018 passes.
**Files**: `src/app/submit/[id]/RejectionReasonCard.tsx` (modify)

### T-020: RED — failing tests for empty-findings explainer + isolation when scanResult present
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: (a) Given a page render with `scanResult: null` and terminal state → When the page renders → Then the FindingsSection region shows "No line-level findings — this submission was rejected before/outside the scanner pipeline." (b) Given `scanResult` non-null → When the page renders → Then RejectionReasonCard does NOT appear.
**Files**: `src/app/submit/[id]/__tests__/page.test.tsx` (NEW or extend)

### T-021: GREEN — wire RejectionReasonCard into `page.tsx` with conditional render
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: T-020 passes. RejectionReasonCard mounts only when `state ∈ {REJECTED, BLOCKED, TIER1_FAILED} && !scanResult`. FindingsSection shows the explainer when its findings list is empty AND state is terminal.
**Files**: `src/app/submit/[id]/page.tsx` (modify)

## Phase 4 — E2E + REFACTOR

### T-022: E2E — Playwright rejection-detail-visibility spec
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-02 (combined flow) | **Status**: [x] completed
**Test Plan**: Given a fresh submission whose URL hits a test blocklist entry → When the queue processes it → Then `/submit/<id>` renders with: status badge "Blocked", RejectionReasonCard visible (or FindingsSection populated by the synthetic ScanResult), reason text matching the blocklist entry, evidence URLs as anchors.
**Files**: `tests/e2e/rejection-detail-visibility.spec.ts` (NEW)

### T-023: REFACTOR — simplify, dedupe, type-tighten
**User Story**: US-001, US-002 | **Satisfies ACs**: code quality | **Status**: [x] completed
**Test Plan**: All prior tests still pass. Extract any duplicated severity-color logic into a small util if shared between RejectionReasonCard and existing FindingsSection. Replace any `as any` introduced during GREEN with proper types.
**Files**: any modified file (review pass)
