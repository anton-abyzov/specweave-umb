# Plan: Fix stale/inconsistent skill metadata display

## Approach

Targeted bug-fix across 7 existing files in vskill-platform. No new services, no schema changes, no new dependencies. All changes are backwards-compatible -- `UNKNOWN` is additive to the existing union type, verdict mapping is a pure expansion, and the eval-store change converts fire-and-forget to awaited with no API surface change.

## Change Map

### Bug 1: False OFFLINE badge (US-001)

**Root cause**: `checkRepoHealth` treats every non-ok response and every caught error as `OFFLINE`. Rate limits (403/429), server errors (5xx), and network failures all produce `OFFLINE` cached for 5 minutes.

**Fix**: Introduce `UNKNOWN` status. Only HTTP 404 maps to `OFFLINE`. All other failures produce `UNKNOWN`.

| File | Change | Lines |
|------|--------|-------|
| `src/lib/repo-health-store.ts` | Add `"UNKNOWN"` to `RepoHealthResult.status` union. Set `UNKNOWN` TTL to `OFFLINE_TTL_SECONDS` (300s). | ~3 |
| `src/lib/repo-health-checker.ts` | In `checkRepoHealth`: check `res.status === 404` for `OFFLINE`; all other non-ok responses return `UNKNOWN`. Catch block returns `UNKNOWN` instead of `OFFLINE`. Non-GitHub URL still returns `OFFLINE` (genuinely unreachable). | ~8 |
| `src/app/api/v1/skills/.../repo-health/route.ts` | Change the `getCloudflareContext` fallback from `OFFLINE` to `UNKNOWN`. | ~2 |
| `src/app/skills/.../RepoHealthBadge.tsx` | Return `null` early when `status === "UNKNOWN"` (no badge is better than a misleading one). | ~2 |

**Data flow** (after fix):

```
GitHub API
   |
   +-- 200 ok ---------> ONLINE / STALE (24h TTL)
   +-- 404 ------------> OFFLINE (5min TTL)
   +-- 403/429/5xx ----> UNKNOWN (5min TTL)
   +-- network error --> UNKNOWN (5min TTL)
   +-- not github.com -> OFFLINE (5min TTL)

RepoHealthBadge
   |
   +-- ONLINE ---------> green badge
   +-- STALE ----------> gray badge
   +-- OFFLINE --------> red badge
   +-- UNKNOWN --------> null (no badge rendered)
```

### Bug 2: Broken eval verdict mapping (US-002)

**Root cause**: The `ScanChip` status ternary in `page.tsx` line 348 only handles `EFFECTIVE -> PASS` and `DEGRADING -> FAIL`. The three remaining verdicts (`MARGINAL`, `INEFFECTIVE`, `ERROR`) all fall through to the else branch returning `"PENDING"`.

**Fix**: Replace the ternary chain with an exhaustive lookup object.

| File | Change | Lines |
|------|--------|-------|
| `src/app/skills/.../page.tsx` | Replace inline ternary (line 348) with a `VERDICT_TO_STATUS` map: `{ EFFECTIVE: "PASS", MARGINAL: "WARN", INEFFECTIVE: "NEUTRAL", DEGRADING: "FAIL", ERROR: "ERROR" }`. Add `WARN`, `NEUTRAL`, `ERROR` entries to `scanColor`. | ~12 |

**Verdict-to-chip mapping** (after fix):

```
EvalVerdict     ScanChip status   scanColor
-----------     ---------------   ---------
EFFECTIVE   --> PASS              #10B981 (green)
MARGINAL    --> WARN              #F59E0B (amber)
INEFFECTIVE --> NEUTRAL           #6B7280 (gray)
DEGRADING   --> FAIL              #EF4444 (red)
ERROR       --> ERROR             #EF4444 (red)
```

### Bug 3: Stale eval data from silent DB failures (US-003)

**Root cause**: `eval-store.ts` lines 101-114 fire-and-forget the Skill DB update via `.catch()`. If the DB write fails, the skill detail page shows stale eval data with no indication of failure.

**Fix**: Await the Skill update and let errors propagate to the caller.

| File | Change | Lines |
|------|--------|-------|
| `src/lib/eval/eval-store.ts` | Replace lines 101-114 with `await db.skill.update(...)` wrapped in try/catch that logs and re-throws. KV write (lines 117-143) stays fire-and-forget. | ~10 |
| `src/app/skills/.../page.tsx` | Add `lastEvalAt` freshness timestamp inline after run count using existing `formatTimeAgo` helper. Show only when `lastEvalAt` is non-null. | ~6 |

## Test Impact

### Existing tests to update

| Test file | Current behavior | Required change |
|-----------|-----------------|-----------------|
| `src/lib/__tests__/repo-health-checker.test.ts` TC-010 | Asserts `OFFLINE` for 404 | Keep as-is (404 still returns `OFFLINE`) |
| TC-011 | Asserts `OFFLINE` for network error | Change to assert `UNKNOWN` |
| TC-013 | Asserts `OFFLINE` for 403 | Change to assert `UNKNOWN` |

### New tests to add

| Test | Description |
|------|-------------|
| TC-014 | 429 response returns `UNKNOWN` |
| TC-015 | 500 response returns `UNKNOWN` |
| TC-016 | `scanColor("WARN")` returns `#F59E0B` |
| TC-017 | `scanColor("NEUTRAL")` returns `#6B7280` |
| TC-018 | `scanColor("ERROR")` returns `#EF4444` |
| TC-019 | `VERDICT_TO_STATUS` maps all five verdicts correctly |
| TC-020 | `storeEvalRun` propagates Skill DB update errors |
| TC-021 | `storeEvalRun` still returns evalRun.id on KV failure |

### Verification strategy

1. **Unit tests**: `npx vitest run src/lib/__tests__/repo-health-checker.test.ts` -- covers UNKNOWN status
2. **Component snapshot**: verify RepoHealthBadge returns null for UNKNOWN (can test via mocked fetch)
3. **Manual verification gate**: Inspect skill detail page for a skill with eval data to confirm verdict chip colors and freshness timestamp

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `UNKNOWN` status breaks KV consumers that only expect 3 values | Low | KV TTL is 5min; any stale `OFFLINE` entries expire quickly. Badge component already handles unknown statuses gracefully (falls through to gray). |
| Awaiting Skill DB update slows down eval-store | Low | Single row update by PK is <10ms on D1. The DB write was already happening -- we are only changing error handling, not adding work. |
| `scanColor` callers pass unexpected status strings | None | The fallback `|| "#6B7280"` is preserved -- unknown statuses still get gray. |

## Complexity

**Low**. Seven file edits, all additive/corrective. No schema migration. No new dependencies. No API surface changes. Estimated implementation: single task batch.
