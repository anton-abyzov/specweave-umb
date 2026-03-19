---
increment: 0598-fix-ado-sync-parent-linking
type: architecture
status: draft
---

# Architecture Plan: Fix ADO Sync Parent Linking

## Problem Analysis

Two bugs in `plugins/specweave/lib/integrations/ado/ado-spec-sync.ts`:

### Bug 1: Global US-ID title matching (line 674-706)

`findStoryByTitle(usId)` searches WIQL for `[System.Title] CONTAINS '[US-001]'` scoped only to the ADO project. If two features (FS-591, FS-592) both have a US-001, the query returns whichever was created first — potentially from a completely different feature. This causes the sync to update the wrong story or silently skip creating the correct one.

**Root cause**: The WIQL query at line 683 uses only `[${usId}]` in the CONTAINS clause but the actual story titles created by `syncUserStories()` (line 454) use format `[${us.id}] ${us.title}` — no feature ID disambiguation.

**Observation**: The `external-issue-auto-creator.ts` (line 486) uses `[${incrementInfo.featureId}][${usId}] ${usTitle}` format — it includes the feature ID. The spec sync does not.

### Bug 2: Silent 409 on parent link mismatch (lines 816-836)

`updateStory()` blindly adds a `System.LinkTypes.Hierarchy-Reverse` relation. If the story already has a parent relation, ADO returns 409. The catch block (line 833-835) swallows the error assuming "parent already set." But the existing parent may be from a **different** feature/epic — the old parent stays, and the correct new parent is never set.

**Root cause**: No check whether the existing parent matches the intended parent. The 409 is treated as "already correct" when it might mean "conflicting parent."

## Design Decisions

### DD-1: Scope WIQL query with feature ID prefix

**Change**: Modify `findStoryByTitle()` to accept the feature/spec ID and include it in the WIQL CONTAINS clause.

**Title format alignment**: The story title created by `syncUserStories()` at line 454 is `[${us.id}] ${us.title}`. Change to `[${spec.metadata.id.toUpperCase()}][${us.id}] ${us.title}` so the WIQL query can match on the combined prefix `[FS-XXX][US-YYY]`.

This aligns with `external-issue-auto-creator.ts` line 486 which already uses `[${featureId}][${usId}]` format.

**WIQL change**: `CONTAINS '[${usId}]'` becomes `CONTAINS '[${featureId}][${usId}]'`

**Signature change**: `findStoryByTitle(usId: string)` → `findStoryByTitle(featureId: string, usId: string)`

**Migration**: Existing ADO stories with old `[US-001]` format will not match the new scoped query. The code will create new stories with the correct prefix and correct parent. The old orphaned stories remain untouched (manual cleanup by user if needed). This is acceptable because:
- Only affects users actively using ADO spec sync (niche feature)
- New stories get correct parent links immediately
- Old stories are harmless duplicates

### DD-2: Fetch and compare existing parent before re-linking

**Change**: In `updateStory()`, when `parentId` is provided:
1. Fetch the work item with `$expand=relations` to get current relations
2. Find existing `System.LinkTypes.Hierarchy-Reverse` relation
3. If no parent exists → add parent (current behavior)
4. If existing parent matches intended parent → skip (no-op)
5. If existing parent differs → remove old parent relation, add new one

**ADO API for relation removal**: Use JSON Patch with `op: 'remove'` and `path: '/relations/{index}'` where index is the position of the parent relation in the relations array.

**Implementation pattern** (from ADO REST API):
```typescript
// Fetch with relations
GET /wit/workitems/{id}?$expand=relations&api-version=7.0

// Remove relation at index + add new
PATCH /wit/workitems/{id}?api-version=7.0
[
  { "op": "remove", "path": "/relations/{idx}" },
  { "op": "add", "path": "/relations/-", "value": { "rel": "...", "url": "..." } }
]
```

Both remove + add in a single PATCH request — ADO processes them atomically.

## Affected Code

| File | Change |
|------|--------|
| `plugins/specweave/lib/integrations/ado/ado-spec-sync.ts` | Both fixes — single file |

### Specific method changes:

1. **`syncUserStories()`** (line 437-511):
   - Line 454: Change title from `[${us.id}] ${us.title}` to `[${spec.metadata.id.toUpperCase()}][${us.id}] ${us.title}`
   - Line 458: Pass `spec.metadata.id.toUpperCase()` to `findStoryByTitle()`

2. **`findStoryByTitle()`** (line 674-707):
   - Add `featureId: string` parameter
   - Line 683: Change WIQL from `CONTAINS '[${usId}]'` to `CONTAINS '[${featureId}][${usId}]'`

3. **`updateStory()`** (line 780-837):
   - Lines 816-836: Replace blind add+catch with fetch-compare-swap logic
   - Fetch work item with `$expand=relations`
   - Find parent relation by `rel === 'System.LinkTypes.Hierarchy-Reverse'`
   - Extract parent ID from relation URL (last path segment)
   - Compare with intended `parentId`
   - If different: single PATCH with remove at index + add new

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Title format change breaks existing matches | Intentional — creates new correctly-linked stories instead of updating wrong ones |
| Extra API call in updateStory (fetch relations) | Only happens when `parentId` is provided; one GET per story per sync — acceptable |
| ADO rate limits from extra calls | Already handled by `SyncCircuitBreaker` in place |
| Remove+add parent not atomic | Single PATCH with both ops — ADO processes atomically |

## Non-Goals

- Migrating existing incorrectly-linked stories (manual cleanup)
- Changing the SyncEngine adapter (`src/sync/providers/ado.ts`) — already handles parent linking correctly
- Changing `ado-client.ts` — different code path, already fixed in increment 0511
- Deduplication of stories created by both sync paths

## Test Strategy

Unit tests (Vitest) for the three modified methods, mocking the ADO HTTP client:

1. **`findStoryByTitle()`** — verify WIQL query includes `[featureId][usId]` in CONTAINS clause
2. **`updateStory()` — no existing parent** — verify parent link added normally
3. **`updateStory()` — same parent** — verify no-op (no PATCH for relations)
4. **`updateStory()` — different parent** — verify remove old + add new in single PATCH
5. **`syncUserStories()`** — verify title format is `[SPEC-ID][US-XXX] Title`
