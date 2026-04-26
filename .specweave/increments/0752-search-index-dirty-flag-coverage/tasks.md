---
increment: 0752-search-index-dirty-flag-coverage
title: "Search-index dirty-flag on all state transitions"
test_mode: TDD
---

# Tasks: Search-index dirty-flag coverage on all state transitions

## Phase 1 — Foundation helper (US-001 + US-002)

### T-001a: [RED] Unit tests for `markSearchIndexDirty()` helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] pending

**Test Plan**:
- Given worker env is available and `SEARCH_CACHE_KV` is bound → When `markSearchIndexDirty()` is called → Then `KV.put('search-index:dirty', '1', { expirationTtl: 86400 })` is invoked exactly once
- Given `getWorkerEnv()` returns null but CF context resolves `SEARCH_CACHE_KV` → When `markSearchIndexDirty()` is called → Then `KV.put` is called via CF context fallback
- Given both `getWorkerEnv()` and `getCloudflareContext()` are unavailable → When `markSearchIndexDirty()` is called → Then it resolves without throwing
- Given `KV.put` rejects with an error → When `markSearchIndexDirty()` is called → Then it resolves without throwing (best-effort swallow)

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/search-index/__tests__/mark-dirty.test.ts` (new — write tests first, module does not exist yet)

---

### T-001b: [GREEN] Implement `markSearchIndexDirty()` helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- Given T-001a tests are RED → When helper is implemented → Then all four T-001a cases pass green

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/search-index/mark-dirty.ts` (new, ~25 LOC)

**Implementation notes**: Extract from `publish.ts:657-674`. Dual env-resolve: `getWorkerEnv()` first, then `getCloudflareContext({ async: true })`. Write `'1'` to key `'search-index:dirty'` with `{ expirationTtl: 86400 }`. Wrap entire body in try/catch — never throw.

---

### T-002a: [RED] Tests asserting `markSearchIndexDirty` called once on publish success, zero on rollback
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- Given `markSearchIndexDirty` is mocked at the import boundary via `vi.mock` → When `publishSkill()` completes a successful DB transaction → Then the mocked helper is called exactly once
- Given `markSearchIndexDirty` is mocked → When the surrounding DB transaction throws and rolls back → Then the mocked helper is called zero times
- Given existing publish tests are present → When no code changes are made → Then all existing test cases still pass (regression guard)

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/submission/__tests__/publish.test.ts` (modify — add mock + two new cases)

---

### T-002b: [GREEN] Replace inline block in `publish.ts` with `markSearchIndexDirty()`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- Given T-002a tests are RED → When inline block at `publish.ts:657-674` is replaced with `await markSearchIndexDirty()` and import is added → Then all T-002a cases pass green

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts` (modify lines 657-674; -17 lines, +2 lines: 1 import + 1 call)

---

## Phase 2 — BLOCKED coverage in finalize-scan (US-003)

### T-003a: [RED] Tests for three BLOCKED transitions in finalize-scan
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [ ] pending

**Test Plan**:
- Given blocklist-BLOCKED path (L292), prior state = `PUBLISHED` → When `markSearchIndexDirty` is mocked → Then it is called exactly once
- Given blocklist-BLOCKED path (L292), prior state = `RECEIVED` → When `markSearchIndexDirty` is mocked → Then it is NOT called
- Given LLM-confirmed-threat-BLOCKED path (L417), prior state = `PUBLISHED` → When helper is mocked → Then called exactly once
- Given LLM-confirmed-threat-BLOCKED path (L417), prior state = `RECEIVED` → When helper is mocked → Then NOT called
- Given DCI-violation-BLOCKED path (L485), prior state = `PUBLISHED` → When helper is mocked → Then called exactly once
- Given DCI-violation-BLOCKED path (L485), prior state = `RECEIVED` → When helper is mocked → Then NOT called

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/finalize-scan/__tests__/route.test.ts` (modify — add 6 new cases with mocked helper)

---

### T-003b: [GREEN] Add conditional `markSearchIndexDirty()` at the three BLOCKED sites in finalize-scan
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- Given T-003a tests are RED → When conditional block is added at each of lines 292, 417, 485 → Then all six T-003a cases pass green

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/finalize-scan/route.ts` (modify — add 3 conditional blocks + 1 import)

**Implementation notes**:
```ts
if (priorState === 'PUBLISHED' || priorState === 'AUTO_APPROVED') {
  await markSearchIndexDirty();
}
```
`priorState` is already in scope at all three sites per plan.md. Add import once at top.

---

## Phase 3 — Admin reject, repo-block, approve (US-004, US-005, US-006)

### T-004a: [RED] Tests for PUBLISHED→REJECTED vs RECEIVED→REJECTED in admin reject route
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] pending

**Test Plan**:
- Given submission prior state = `PUBLISHED` → When admin reject handler runs → Then mocked `markSearchIndexDirty` is called exactly once
- Given submission prior state = `RECEIVED` → When admin reject handler runs → Then mocked `markSearchIndexDirty` is NOT called

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/submissions/[id]/reject/__tests__/route.test.ts` (modify — add 2 new cases)

---

### T-004b: [GREEN] Add conditional `markSearchIndexDirty()` at admin reject route ~line 99
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [ ] pending

**Test Plan**:
- Given T-004a tests are RED → When conditional is added at ~line 99 → Then both T-004a cases pass green

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/submissions/[id]/reject/route.ts` (modify ~line 99 + import)

**Implementation notes**:
```ts
if (submission.state === 'PUBLISHED') {
  await markSearchIndexDirty();
}
```

---

### T-005a: [RED] Tests for bulk repo-block — helper called once on PUBLISHED match, never on zero match
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [ ] pending

**Test Plan**:
- Given repo-block targets a repo with 3 PUBLISHED submissions → When admin repo-block handler runs → Then mocked `markSearchIndexDirty` is called exactly 1 time (not 3)
- Given repo-block targets a repo with 0 PUBLISHED submissions (all in RECEIVED state) → When admin repo-block handler runs → Then mocked `markSearchIndexDirty` is NOT called

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/repo-block/__tests__/route.test.ts` (modify — add 2 new cases)

---

### T-005b: [GREEN] Add conditional `markSearchIndexDirty()` at admin repo-block route ~line 116
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [ ] pending

**Test Plan**:
- Given T-005a tests are RED → When count-before-update + single conditional call is added → Then both T-005a cases pass green

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/repo-block/route.ts` (modify ~line 116 + import)

**Implementation notes**:
```ts
const publishedCount = await prisma.submission.count({
  where: { repoId, state: 'PUBLISHED' },
});
// ... existing updateMany ...
if (publishedCount > 0) {
  await markSearchIndexDirty();
}
```

---

### T-006a: [RED] Tests for admin approve — belt-and-suspenders dirty flag fires even when publishSkill throws
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [ ] pending

**Test Plan**:
- Given `publishSkill` is mocked to succeed → When admin approve handler runs → Then mocked `markSearchIndexDirty` is called at least once (belt-and-suspenders at line 134 + inside publishSkill)
- Given `publishSkill` is mocked to throw AFTER the `updateMany` commits → When admin approve handler runs → Then mocked `markSearchIndexDirty` was still called (early call at line 134 fired before the throw)

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/submissions/[id]/approve/__tests__/route.test.ts` (modify — add 2 new cases using existing mock-KV pattern at lines 180-186)

---

### T-006b: [GREEN] Add belt-and-suspenders `markSearchIndexDirty()` at admin approve line 134
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [ ] pending

**Test Plan**:
- Given T-006a tests are RED → When helper call is inserted immediately after `updateMany` at line 134 → Then both T-006a cases pass green

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/submissions/[id]/approve/route.ts` (modify line 134 + import)

**Implementation notes**: Insert `await markSearchIndexDirty();` after `updateMany` succeeds, before the `publishSkill()` call at line 193. Double-set on success path is idempotent per AD-003.

---

## Phase 4 — Architectural canary (US-007)

### T-007a: [RED] Write the state-transition coverage canary test (initially fails)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
**Status**: [ ] pending

**Test Plan**:
- Given the canary test is written with strict adjacency rules → When run against the src/ tree BEFORE Phase 1-3 code is in place → Then it fails citing each uncovered state-write
- Given a future source file contains `state: 'PUBLISHED'` without an adjacent helper call within 15 lines → When canary test runs → Then it fails with a message naming `file:line` and the matched pattern

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/search-index/__tests__/state-transition-coverage.test.ts` (new, ~80 LOC)

**Implementation notes**: Pure string-grep, no AST. Use `glob` + `readFileSync`. Exclude paths containing `__tests__`, `.test.ts`, `scripts/build-worker-entry.ts`, `migrations/`, type-definition files. Sliding window of 15 lines after each match. Assert window contains `markSearchIndexDirty(` or `publishSkill(`. Support inline-comment allowlist `// search-index-coverage-exempt: <reason>` for legitimate exemptions.

---

### T-007b: [GREEN] Tune canary — add exemptions where needed, get test green
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05
**Status**: [ ] pending

**Test Plan**:
- Given T-007a canary is RED with false positives → When allowlist entries or `// search-index-coverage-exempt` markers are added for legitimate non-index writes → Then canary passes green across the full src/ tree

**Files**:
- `repositories/anton-abyzov/vskill-platform/src/lib/search-index/__tests__/state-transition-coverage.test.ts` (modify — tune allowlist)
- Any source file requiring `// search-index-coverage-exempt: <reason>` comment (modify as needed)

---

## Phase 5 — Deploy and verify (US-008)

### T-008: Run full Vitest suite + TypeScript type-check
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [ ] pending

**Test Plan**:
- Given all Phase 1-4 tasks are complete → When `npx vitest run src/lib/search-index src/lib/submission src/app/api/v1/internal/finalize-scan src/app/api/v1/admin/submissions src/app/api/v1/admin/repo-block` is run → Then all tests pass with zero failures
- Given all changes are in place → When `npx tsc --noEmit` is run in `repositories/anton-abyzov/vskill-platform` → Then zero type errors are reported

**Files**: (verification only)

---

### T-009: Build and deploy Cloudflare Worker to production
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03
**Status**: [ ] pending

**Test Plan**:
- Given T-008 passes → When `npm run build:worker && npx wrangler deploy` is run from `repositories/anton-abyzov/vskill-platform` → Then the worker builds cleanly and wrangler reports a successful deployment URL

**Files**: (build/deploy step)

---

### T-010: [MANUAL] Live end-to-end verification — publish, wait for cron, confirm find + block
**User Story**: US-008 | **Satisfies ACs**: AC-US8-04, AC-US8-05, AC-US8-06
**Status**: [ ] pending

**Test Plan**:
- Given T-009 is deployed → When a fresh test skill is submitted via `vskill submit anton-abyzov/<test-repo> --skill <test-name>` and the next 2h-aligned cron tick fires → Then `wrangler tail` shows `[cron] search index rebuild completed` AND `vskill find <test-name>` returns the skill WITHOUT any manual rebuild
- Given the above succeeds → When the same skill is blocked via admin repo-block route and the next 2h-aligned tick fires → Then `vskill find <test-name>` no longer returns the skill WITHOUT any manual rebuild
- Given both manual verifications pass → When results are recorded → Then `reports/manual-verification.md` inside the increment folder contains observed timestamps and log lines

**Files**:
- `.specweave/increments/0752-search-index-dirty-flag-coverage/reports/manual-verification.md` (new — manual verification evidence)

---

## Closure

### T-011: Run `/sw:code-reviewer`
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01
**Status**: [ ] pending

**Test Plan**:
- Given all implementation tasks are complete → When `/sw:code-reviewer` is invoked → Then `code-review-report.json` is written with no critical/high/medium findings (fix loop if needed, max 3 iterations)

**Files**:
- `.specweave/increments/0752-search-index-dirty-flag-coverage/reports/code-review-report.json` (generated)

---

### T-012: Run `/sw:done 0752` — full closure pipeline
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03
**Status**: [ ] pending

**Test Plan**:
- Given T-011 passes → When `/sw:done 0752` is invoked → Then code-review, simplify, grill, judge-llm, and PM gates all pass and the increment is closed

**Files**:
- `.specweave/increments/0752-search-index-dirty-flag-coverage/reports/grill-report.json` (generated)
- `.specweave/increments/0752-search-index-dirty-flag-coverage/reports/judge-llm-report.json` (generated)
