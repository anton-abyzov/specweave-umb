# Plan — 0369: Fix Duplicate Processing False Rejections

## Files to modify
1. `src/lib/submission-store.ts` — Add `opts?: { force?: boolean }` param, SUCCESS_LOCKED guard
2. `src/lib/queue/process-submission.ts` — Add idempotency check at function start
3. `src/app/api/v1/admin/submissions/restore-published/route.ts` (new) — Bulk restore endpoint
4. `src/lib/queue/__tests__/state-guard.test.ts` (new) — Tests for guard + idempotency

## Approach
- Silent skip + warn for blocked transitions (non-breaking)
- Only PUBLISHED/VENDOR_APPROVED are locked; REJECTED/TIER1_FAILED/DEQUEUED remain overridable for admin reprocess
- Restore uses `force: true` and existing scan data (no re-scan)
- No existing callers need changes — guard only blocks FROM success states
