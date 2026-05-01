# Tasks: Studio Check-Updates Batching

## US-001: Batch checkSkillUpdates

### T-001: Add CHECK_UPDATES_BATCH_SIZE constant + chunkArray helper
**User Story**: US-001, US-003 | **AC**: AC-US3-01, AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given an empty array → When chunkArray([], 100) → Then returns []. Given 100 items → When chunkArray(arr, 100) → Then returns one chunk of length 100. Given 230 items → When chunkArray(arr, 100) → Then returns three chunks of length [100, 100, 30].

### T-002: Write failing tests for chunkArray helper edge cases
**User Story**: US-003 | **AC**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Add `describe('chunkArray', ...)` block to `src/eval-ui/src/api.test.ts` covering: empty input, exact-size input, sub-size input, N×size input, and the 230-element case.

### T-003: Write failing test for checkSkillUpdates 100-skill boundary (single fetch)
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-06 | **Status**: [x] completed
**Test Plan**: Given 100 skill IDs → When api.checkSkillUpdates is called with global fetch mocked → Then exactly 1 fetch invocation occurs and the fetch URL ends with `/api/v1/skills/check-updates`.

### T-004: Write failing test for checkSkillUpdates 230-skill chunking (three fetches)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given 230 skill IDs → When api.checkSkillUpdates is called with fetch mocked to return `{results: [...]}` per chunk → Then exactly 3 fetch invocations occur, request bodies have skills.length of 100, 100, 30 respectively, and the merged result preserves input order across all 230 entries.

### T-005: Write failing test for checkSkillUpdates partial chunk failure
**User Story**: US-001 | **AC**: AC-US1-04, AC-US1-07 | **Status**: [x] completed
**Test Plan**: Given 200 skill IDs and the first chunk's fetch rejects but the second resolves with `{results: [{skillId, version, eventId, publishedAt}]}` → When api.checkSkillUpdates is called → Then it returns only the second chunk's results (does not throw, does not return []).

### T-006: Implement chunking inside checkSkillUpdates (GREEN)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: All T-002, T-003, T-004, T-005 tests pass after implementation. Run `npx vitest run src/eval-ui/src/api.test.ts`.

---

## US-002: Batch resolveInstalledSkillIds

### T-007: Write failing test for resolveInstalledSkillIds 100-skill boundary (single fetch)
**User Story**: US-002 | **AC**: AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given 100 input skills with `{name, plugin, skill, currentVersion}` → When api.resolveInstalledSkillIds is called with fetch mocked → Then exactly 1 fetch invocation occurs.

### T-008: Write failing test for resolveInstalledSkillIds 230-skill chunking (three fetches, ordered)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given 230 input skills → When api.resolveInstalledSkillIds is called with fetch mocked to return chunked `{results: [{name, id, slug}]}` envelopes → Then exactly 3 fetch invocations occur, the function returns 230 entries in input order, and entries from chunk 2/3 carry their UUID/slug correctly.

### T-009: Write failing test for resolveInstalledSkillIds chunk failure degrades only that chunk
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given 150 input skills where the second chunk's fetch returns 400 → When api.resolveInstalledSkillIds is called → Then chunk 1's 100 skills carry uuid/slug from the response, chunk 2's 50 skills carry only `{plugin, skill}` (no uuid/slug), and the function does not throw.

### T-010: Implement chunking inside resolveInstalledSkillIds (GREEN)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: All T-007, T-008, T-009 tests pass after implementation. Run `npx vitest run src/eval-ui/src/api.test.ts`.

---

## Verification

### T-011: Full vitest suite green
**User Story**: US-001, US-002, US-003 | **AC**: All | **Status**: [x] completed
**Test Plan**: `npx vitest run` exits 0 from `repositories/anton-abyzov/vskill/`. No prior tests regress.

### T-012: Manual verification — Studio reload no longer shows 400
**User Story**: US-001, US-002 | **AC**: success criteria #1, #5 | **Status**: [x] completed
**Test Plan**: Rebuild Studio bundle. Restart `vskill studio`. Reload localhost:3157 in browser. Open devtools network panel, filter `check-updates`. Observe 2-3 requests, all status 200. Console has no `Failed to load resource: ... 400` error for `/api/v1/skills/check-updates`.
