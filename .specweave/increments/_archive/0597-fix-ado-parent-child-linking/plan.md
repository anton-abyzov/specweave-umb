# Implementation Plan: Fix ADO Sync Parent-Child Linking Bug

## Overview

Fix three bugs in ADO sync that cause user stories to be linked to wrong parent epics. Changes are scoped to the ADO client error handling and the ExternalIssueAutoCreator metadata writing.

## Architecture

### Components Modified
- **AdoClient** (`src/integrations/ado/ado-client.ts`): Fix `linkWorkItems()` error handling
- **ExternalIssueAutoCreator** (`src/sync/external-issue-auto-creator.ts`): Fix metadata fallback

### Root Cause Chain
1. `linkWorkItems()` returns void on failure (warns, doesn't throw)
2. `createWorkItem()` reports success even when parent link failed
3. Metadata fallback writes Feature ID as Story ID when `storyItemMap` entry is missing
4. Subsequent syncs read corrupted metadata, building `FeatureData.externalRef` with wrong ID

## Implementation Phases

### Phase 1: Fix Error Handling (ado-client.ts)
- Make `linkWorkItems()` throw on non-409 failures
- Handle 409 as idempotent success (link already exists)
- This propagates through `createWorkItem()` to callers

### Phase 2: Fix Metadata (external-issue-auto-creator.ts)
- Remove `|| workItemId` fallback at line 1247
- Skip stories with no sync data instead of corrupting metadata
- Log a warning for skipped stories

### Phase 3: Add Tests
- ADO client: `linkWorkItems` behavior (throw, 409, parentId)
- ADO provider: `createIssue` parent linking (externalRef presence/absence, URL format)

## Testing Strategy

- Unit tests via Vitest
- Test both the error path (non-409 → throw) and the idempotent path (409 → success)
- Test metadata skipping when storyItemMap entry is missing
