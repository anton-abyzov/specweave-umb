# Implementation Plan: Fix Remaining ADO Sync Gaps

## Overview

Fix 3 ADO sync gaps identified by brainstorm team. Follows the same pattern as increment 0597.

## Changes

1. **P0**: Remove `sync-progress.ts:397-416` ADO auto-mapping block (writes Feature ID as Story IDs)
2. **P1**: Add `title` filter to `AdoWorkItemFilter` + `searchWorkItemByTitle()` method + Layer 3 dedup in `createAdoIssues()`
3. **P1**: Add `response.ok` check to `providers/ado.ts` `updateIssue()`

## Files

| File | Change |
|------|--------|
| `src/cli/commands/sync-progress.ts` | Remove ADO auto-mapping block |
| `src/integrations/ado/ado-client.ts` | Add title filter + searchWorkItemByTitle() |
| `src/sync/external-issue-auto-creator.ts` | Use Layer 3 dedup before Feature creation |
| `src/sync/providers/ado.ts` | Add response.ok check to updateIssue() |
| `tests/unit/integrations/ado/ado-client.test.ts` | Test searchWorkItemByTitle |
| `tests/unit/sync/providers/ado-provider.test.ts` | Test updateIssue throws on failure |
