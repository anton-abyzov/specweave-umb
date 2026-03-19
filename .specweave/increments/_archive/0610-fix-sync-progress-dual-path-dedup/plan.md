---
increment: 0610-fix-sync-progress-dual-path-dedup
---

# Architecture: Fix sync-progress dual-path dedup

## Approach

Expand `checkExistingIssue()` to check all known field name variants — same pattern already used in `pr-linker.ts` (lines 78-79, 96-97).

## Files

| File | Change |
|------|--------|
| `src/sync/external-issue-auto-creator.ts:582-591` | Add `epicKey` and `featureId` checks |
| `tests/unit/sync/external-issue-auto-creator.test.ts` | Add 4 dedup test cases |

## Why

- Backward compatible: existing checks preserved as fallbacks
- Minimal: 6 lines of production code
- Reference pattern exists in `pr-linker.ts`
