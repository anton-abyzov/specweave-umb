---
increment: 0505-fix-stale-search-404
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004]
total_tasks: 4
completed_tasks: 4
---

# Tasks: Fix Stale Search Results Returning 404

## User Story: US-001 - Delete Endpoint KV Cleanup

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

---

### T-001: Write failing tests for delete endpoint KV cleanup (TDD Red)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the delete endpoint exists and has no KV cleanup logic
- **When** the failing tests are run
- **Then** all new test cases fail (red phase confirmed)

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/skills/[owner]/[repo]/[skill]/delete/__tests__/route.test.ts`
   - `callsUpdateSearchShardWithRemoveAction()`: Given a skill exists in Postgres and KV, when DELETE is called, then `updateSearchShard` is called with action `"remove"` and a SearchIndexEntry built from SEARCH_ENTRY_SELECT fields
   - `callsUpdateSearchShardBeforeDbDelete()`: Given a skill exists, when DELETE is called, then `updateSearchShard` is called before `db.$transaction`
   - `callsInvalidateSearchIndexAfterShardRemoval()`: Given shard removal succeeds, when DELETE is called, then `invalidateSearchIndex` is called after `updateSearchShard`
   - `fetchesSkillWithSearchEntrySelectFields()`: Given the delete endpoint runs, when fetching the skill record, then the select includes all SEARCH_ENTRY_SELECT fields (not just id/name/displayName/author)
   - `includesKvCleanupTrueInResponseOnSuccess()`: Given KV operations succeed, when DELETE returns 200, then response body contains `kvCleanup: true`
   - `doesNotBlockDbDeletionWhenKvFails()`: Given `updateSearchShard` throws a network error, when DELETE is called, then `db.$transaction` still runs and the skill is deleted
   - `includesKvCleanupFalseInResponseOnKvFailure()`: Given KV operations fail, when DELETE returns 200, then response body contains `kvCleanup: false`
   - `logsKvFailureForAuditTrail()`: Given `updateSearchShard` throws, when DELETE completes, then `console.error` or `console.warn` is called with KV failure details
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/app/api/v1/admin/skills/[owner]/[repo]/[skill]/delete/__tests__/route.test.ts`
2. Mock `@/lib/search-index` (updateSearchShard, invalidateSearchIndex, buildSearchEntry, SEARCH_ENTRY_SELECT)
3. Mock `@/lib/env-resolve` (resolveEnv returning mock SEARCH_CACHE_KV)
4. Mock `@/lib/db` (getDb returning mock db with findFirst, $transaction)
5. Mock auth helpers (`@/lib/auth`, `@/lib/internal-auth`)
6. Write all 8 test cases in RED state (assert on behavior that does not yet exist)
7. Run `npx vitest run` to confirm all 8 fail

---

### T-002: Implement KV cleanup in delete endpoint (TDD Green + Refactor)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the failing tests from T-001 exist
- **When** the delete endpoint is modified to add KV cleanup
- **Then** all 8 test cases pass (green phase) and code meets quality bar (refactor phase)

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/skills/[owner]/[repo]/[skill]/delete/__tests__/route.test.ts`
   - All 8 cases from T-001 must pass
   - **Coverage Target**: 95%

**Implementation**:
1. Add imports to `src/app/api/v1/admin/skills/[owner]/[repo]/[skill]/delete/route.ts`:
   - `updateSearchShard`, `invalidateSearchIndex`, `buildSearchEntry`, `SEARCH_ENTRY_SELECT` from `@/lib/search-index`
   - `resolveEnv` from `@/lib/env-resolve`
2. Expand `db.skill.findFirst` select from `{ id, name, displayName, author }` to `{ id: true, ...SEARCH_ENTRY_SELECT }`
3. Before the `$transaction`, add best-effort KV cleanup block:
   ```
   let kvCleanup = false;
   try {
     const cfEnv = await resolveEnv();
     const searchKv = cfEnv.SEARCH_CACHE_KV;
     if (searchKv) {
       const entry = buildSearchEntry(skill);
       await updateSearchShard(searchKv, entry, "remove");
       await invalidateSearchIndex(searchKv);
       kvCleanup = true;
     }
   } catch (kvErr) {
     console.error("[admin] KV shard cleanup failed for delete of", skillName, kvErr);
   }
   ```
4. Add `kvCleanup` field to the response JSON
5. Run `npx vitest run` -- all 8 tests must pass
6. Refactor: ensure KV block mirrors block endpoint pattern exactly

---

## User Story: US-002 - Search Result Existence Validation

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 0 completed

---

### T-003: Add edge-only existence validation to search route (TDD Red → Green → Refactor)

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** the search route returns edge-only results containing a stale skill name
- **When** the route processes the results
- **Then** the stale skill is filtered out before the response is returned

**Test Cases**:
1. **Unit**: `src/app/api/v1/skills/search/__tests__/route.test.ts` (extend existing file)
   - `filtersStaleEdgeResultsAgainstDb()`: Given searchSource is "edge" and one result name is not in Postgres, when GET is called, then the stale result is absent from the response
   - `keepsAllEdgeResultsThatExistInDb()`: Given searchSource is "edge" and all result names exist in Postgres, when GET is called, then all results are returned
   - `skipsValidationForEdgePlusPostgresSource()`: Given searchSource is "edge+postgres" (both sources returned results), when GET is called, then no extra DB query for existence is made
   - `skipsValidationForPostgresSource()`: Given searchSource is "postgres" (edge returned 0), when GET is called, then no extra DB query for existence is made
   - `skipsValidationForEmptyEdgeResults()`: Given edge returns 0 results, when GET is called, then no extra DB query is made
   - `returnsAllEdgeResultsUnfilteredWhenDbValidationFails()`: Given searchSource is "edge" and the DB existence query throws, when GET is called, then all edge results are returned (graceful degradation) and a warning is logged
   - **Coverage Target**: 90%

**Implementation**:
1. **RED phase**: Add the 6 test cases to `src/app/api/v1/skills/search/__tests__/route.test.ts`
   - Mock `getDb` returning a mock db with `skill.findMany` for existence check
   - Run `npx vitest run` -- confirm 6 new cases fail
2. **GREEN phase**: Modify `src/app/api/v1/skills/search/route.ts`
   - After merge and before `enrichWithBlocklistAndRejected`, add:
     ```typescript
     if (searchSource === "edge" && results.length > 0) {
       try {
         const db = await getDb();
         const names = results.map((r) => r.name);
         const existing = await db.skill.findMany({
           where: { name: { in: names } },
           select: { name: true },
         });
         const existingSet = new Set(existing.map((s) => s.name));
         results = results.filter((r) => existingSet.has(r.name));
       } catch (err) {
         console.warn("GET /api/v1/skills/search: existence validation failed, returning unfiltered edge results", err);
       }
     }
     ```
   - Add `import { getDb } from "@/lib/db";` if not already present
   - Run `npx vitest run` -- all 6 cases pass
3. **REFACTOR phase**: Ensure single batch query (no per-result lookups), guard against empty names array

---

## User Story: US-003 - KV Shard TTL Defense-in-Depth

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 1 total, 0 completed

---

### T-004: Add expirationTtl to all KV shard writes in search-index.ts (TDD Red → Green → Refactor)

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Test Plan**:
- **Given** `buildSearchIndex()` and `updateSearchShard()` write to KV without TTL
- **When** modified to include `expirationTtl: 604800`
- **Then** every `kv.put()` call in both functions passes `{ expirationTtl: 604800 }` as the options argument

**Test Cases**:
1. **Unit**: `src/lib/__tests__/search-index.test.ts` (extend existing file)
   - `buildSearchIndexPassesTtlToNameShardPuts()`: Given `buildSearchIndex` is called, when it writes name shards, then every `kv.put` call for shard keys includes `{ expirationTtl: 604800 }`
   - `buildSearchIndexPassesTtlToAuthorShardPuts()`: Given `buildSearchIndex` is called, when it writes author shards, then every `kv.put` call for author shard keys includes `{ expirationTtl: 604800 }`
   - `buildSearchIndexPassesTtlToMetaKeyPut()`: Given `buildSearchIndex` is called, when it writes the meta key, then the `kv.put` call includes `{ expirationTtl: 604800 }`
   - `updateSearchShardPassesTtlToNameShardPuts()`: Given `updateSearchShard` is called with any entry, when it writes name shards, then every `kv.put` call includes `{ expirationTtl: 604800 }`
   - `updateSearchShardPassesTtlToAuthorShardPut()`: Given `updateSearchShard` is called, when it writes the author shard, then `kv.put` includes `{ expirationTtl: 604800 }`
   - `updateSearchShardPassesTtlToMetaKeyPut()`: Given `updateSearchShard` is called, when it writes the meta key, then `kv.put` includes `{ expirationTtl: 604800 }`
   - **Coverage Target**: 90%

**Implementation**:
1. **RED phase**: Add the 6 test cases to `src/lib/__tests__/search-index.test.ts`
   - Update `createMockKv()` to capture options in `put` calls: `put: vi.fn(async (key, value, options?) => { ... })`
   - Assert on `mockKv.put.mock.calls[n][2]` to verify options argument
   - Run `npx vitest run` -- confirm 6 new cases fail (current kv.put has no options)
2. **GREEN phase**: Modify `src/lib/search-index.ts`
   - Add constant near top: `const SHARD_TTL_SECONDS = 604800; // 7 days`
   - In `buildSearchIndex()`: change all `kv.put(key, value)` calls to `kv.put(key, value, { expirationTtl: SHARD_TTL_SECONDS })` (3 call sites: name shards, author shards, meta)
   - In `updateSearchShard()`: change all `kv.put(key, value)` calls to `kv.put(key, value, { expirationTtl: SHARD_TTL_SECONDS })` (name shard loop put, author shard put, meta put — 3 call sites)
   - Check `QueueKV.put()` signature in `src/lib/queue/types.ts` to confirm options parameter is accepted
   - Run `npx vitest run` -- all 6 cases pass
3. **REFACTOR phase**: Verify no other `kv.put` call sites in this file were missed; confirm constant name is self-documenting
