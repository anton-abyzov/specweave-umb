---
increment: 0720-submission-rejection-detail-visibility
title: Submission rejection detail visibility
type: hotfix
priority: P1
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Submission rejection detail visibility

## Overview

Submission review pages on verified-skill.com (`/submit/sub_<id>`) currently show bare "Rejected" / "Blocked" status with no detail for 7 of 20 rejection code paths. The UI rendering code (`FindingsSection` at `src/app/submit/[id]/page.tsx:645-785`) is intact — the gap is **data**, not UI: scan-driven rejections write `ScanResult.findings`, but pre-scan blocklist hits, recovery-no-scan, admin reject/block, and repo-level blocks either skip `ScanResult` entirely or stash the reason in `stateEvent.metadata` where the page never surfaces it.

This increment closes that gap with a two-prong fix:

1. **UI fallback** — a `RejectionReasonCard` component renders from `stateHistory[]` / `blockInfo` when `scanResult` is `null`, so historical bare submissions and any future edge cases never look broken.
2. **Synthetic ScanResult writes** — a `writeSyntheticScanResult` helper produces a minimal scan record at the 5 bare paths so the existing `FindingsSection` lights up uniformly going forward.

## User Stories

### US-001: Surface a rejection reason even when no scan ran (P1)
**Project**: vskill-platform

**As a** submitter or admin viewing `/submit/sub_<id>?from=queue`
**I want** to see the actual reason a submission was rejected or blocked, even when the scanner pipeline never ran (or ran but produced no `ScanResult`)
**So that** I can understand why my skill was flagged, fix it, and resubmit — without digging through logs or asking support

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the API returns `scanResult: null` and `state: "BLOCKED"` with a populated `blockInfo`, the page renders a `RejectionReasonCard` showing `blockInfo.reason`, `threatType` badge, severity color, and the list of `evidenceUrls` as clickable links.
- [x] **AC-US1-02**: When the API returns `scanResult: null` and `state ∈ {REJECTED, TIER1_FAILED}` with no `blockInfo`, the page falls back to `stateHistory[]` — walks newest → oldest, finds the first entry whose state is in the terminal set, and renders that entry's `message` in `RejectionReasonCard`.
- [x] **AC-US1-03**: The empty `FindingsSection` region shows the explainer "No line-level findings — this submission was rejected before/outside the scanner pipeline." instead of nothing.
- [x] **AC-US1-04**: When `scanResult` is non-null (the existing detail-rich path), `RejectionReasonCard` does **not** render — no duplication with the existing UI.

---

### US-002: Persist a rejection reason at every bare path (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** every rejection code path to write a `ScanResult` with at least one finding describing why
**So that** the submission page renders consistently regardless of which path triggered the rejection, and analytics/admin tooling can filter rejections uniformly

**Acceptance Criteria**:
- [x] **AC-US2-01**: A `writeSyntheticScanResult(submissionId, { kind, reason, evidenceUrls?, severity?, patternName?, concerns? })` helper exists in `src/lib/submission/synthetic-scan-result.ts` and writes a `ScanResult` row + KV entry containing exactly one finding whose `patternId` matches the kind, `severity` matches the kind's default (or override), `match` is the reason, and `concerns: [reason]`. The write is idempotent (skips if a real `ScanResult` already exists).
- [x] **AC-US2-02**: Early blocklist hit at `process-submission.ts:250` calls `writeSyntheticScanResult({ kind: "blocklist", reason: blocklistEntry.reason, evidenceUrls: blocklistEntry.evidenceUrls })` **before** transitioning to `BLOCKED`.
- [x] **AC-US2-03**: Same wiring at `finalize-scan/route.ts:279` (the VM scanner callback path).
- [x] **AC-US2-04**: Recovery path `recovery.ts:120` (where no prior scan exists) writes `{ kind: "recovery-no-scan", reason: "Submission expired before scanning completed" }` before transitioning to `REJECTED`.
- [x] **AC-US2-05**: Admin reject endpoint `/api/v1/admin/submissions/[id]/reject` writes `{ kind: "admin-reject", reason: <admin-supplied reason> }` **only when no prior `scanResult` exists** — preserves the prior scanner findings for transparency when present.
- [x] **AC-US2-06**: Admin block endpoint `/api/v1/admin/submissions/[id]/block` writes `{ kind: "admin-block", reason: <admin-supplied reason> }` under the same condition (no prior scan).
- [x] **AC-US2-07**: Repo-level block `/api/v1/admin/repo-block` writes `{ kind: "repo-block", reason: <admin-supplied reason> }` for each affected submission (when that submission has no prior scan).
- [x] **AC-US2-08**: All 9 existing detail-rich rejection paths continue to produce real `findings` — no regression. Verified by re-running the existing scanner-pipeline test suite unchanged.

## Functional Requirements

### FR-001: Synthetic finding shape conformance
The synthesized finding MUST satisfy the existing `ScanFinding` interface (`patternId`, `patternName`, `severity`, `category`, `match`, `lineNumber`, `context`, optional `file`) so the existing `FindingsSection` rendering — including line-number buttons and context expansion — works without modification.

### FR-002: Severity / category defaults per kind

| `kind` | severity | patternName | category |
|---|---|---|---|
| `blocklist` | critical | Blocklist match | policy |
| `recovery-no-scan` | high | Submission expired | lifecycle |
| `admin-reject` | high | Admin rejection | manual |
| `admin-block` | critical | Admin block | manual |
| `repo-block` | critical | Repository blocked | policy |

Callers MAY override `severity` and `patternName` via the helper's options bag; defaults apply when omitted.

### FR-003: Idempotency
`writeSyntheticScanResult` MUST be safe to call multiple times for the same submission:
- If a real `ScanResult` (one whose findings include any `patternId` outside the synthetic set) exists, the synthetic write is a no-op.
- If a synthetic `ScanResult` of the same `kind` already exists, the write is upserted (last-write-wins on `match` / `context` / `concerns` only).

## Success Criteria

- Zero submission pages on verified-skill.com show "Rejected" / "Blocked" without a reason.
- New blocklist/admin-reject/admin-block/repo-block/recovery-no-scan submissions produce a queryable `ScanResult` row with a single synthetic finding.
- Existing scanner-driven rejections continue to render unchanged — no regression in Tier 1 / Tier 2 tests.
- Average submission-page support questions referencing "no reason shown" drops to ~0.

## Out of Scope

- Backfilling historical bare submissions (handled by a follow-up maintenance increment using the same helper).
- Changes to the scanner pipeline itself (Tier 1 / Tier 2 / dependency / script scan).
- DB schema changes — reuses the existing `ScanResult.findings` JSON shape.
- New analytics dashboards on rejection kinds (data is now uniformly queryable; UI for it is a separate increment).

## Dependencies

- Existing `storeScanResult()` in `src/lib/submission/kv-store.ts` (KV writer)
- Existing `persistScanResultToDb()` in `src/lib/submission/db-persist.ts` (DB upsert)
- Existing `ScanFinding` interface and Prisma `ScanResult` model
- Existing `FindingsSection` and `STATE_LABELS` / severity color tokens in `src/app/submit/[id]/page.tsx`

## Related Files

### Bare paths (will be wired to call `writeSyntheticScanResult`)

| File:Line | Trigger | Becomes |
|---|---|---|
| `src/lib/workers/process-submission.ts:250` | Early blocklist (queue consumer) | `kind: "blocklist"` |
| `src/app/api/v1/finalize-scan/route.ts:279` | Early blocklist (VM scanner callback) | `kind: "blocklist"` |
| `src/lib/workers/recovery.ts:120` | Stuck submission, no prior scan | `kind: "recovery-no-scan"` |
| `src/app/api/v1/admin/submissions/[id]/reject/route.ts` | Admin manual reject | `kind: "admin-reject"` (only when no prior scan) |
| `src/app/api/v1/admin/submissions/[id]/block/route.ts` | Admin manual block | `kind: "admin-block"` (only when no prior scan) |
| `src/app/api/v1/admin/repo-block/route.ts` | Admin repo-level block | `kind: "repo-block"` per affected submission |

### Detail-rich paths (MUST remain unchanged — regression guard)

`process-submission.ts:584,634,637,657,674`; `finalize-scan/route.ts:404,427,451,472`. These already write real findings via the scanner pipeline.

### New files

- `src/lib/submission/synthetic-scan-result.ts`
- `src/lib/submission/__tests__/synthetic-scan-result.test.ts`
- `src/app/submit/[id]/RejectionReasonCard.tsx`
- `src/app/submit/[id]/__tests__/RejectionReasonCard.test.tsx`
- `tests/e2e/rejection-detail-visibility.spec.ts`
