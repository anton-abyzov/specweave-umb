# Implementation Plan: Fix External Work Item Creation

## Overview

Two targeted fixes in the specweave repository:
1. Add a template guard to `ExternalIssueAutoCreator` to prevent creating GitHub issues from template spec.md files
2. Add `sync_living_docs` option to `post_increment_planning` hooks and wire it in `LifecycleHookDispatcher`

Both fixes are low-risk, additive changes to existing code paths.

## Architecture

### Fix 1: Template Guard

**File**: `repositories/anton-abyzov/specweave/src/sync/external-issue-auto-creator.ts`

In `createForIncrement()`, after loading config and detecting provider, call `isTemplateFile(specPath)` before `loadIncrementInfo()`. This is the earliest possible check and gives a clean skip reason.

```typescript
// After detecting provider, before loadIncrementInfo:
const specPath = path.join(this.projectRoot, '.specweave/increments', incrementId, 'spec.md');
const { isTemplateFile } = await import('../core/increment/template-creator.js');
if (isTemplateFile(specPath)) {
  this.logger.log(`Skipping ${incrementId}: spec.md is still a template`);
  return {
    success: true,
    provider: 'none',
    skipped: true,
    skipReason: 'spec.md is still a template - deferring until spec is complete',
  };
}
```

### Fix 2: Living Docs Sync in Planning Hook

**Files to modify**:
- `src/core/config/types.ts` - Add `sync_living_docs?: boolean` to `post_increment_planning`
- `src/core/hooks/LifecycleHookDispatcher.ts` - Wire living docs sync before auto-create
- `src/templates/config.json.template` - Add default
- `src/cli/helpers/init/directory-structure.ts` - Add default
- `src/cli/helpers/issue-tracker/sync-config-writer.ts` - Add default
- `src/cli/helpers/init/smart-defaults.ts` - Add default
- `src/core/schemas/specweave-config.schema.json` - Add schema property

Order in `onIncrementPlanned()`:
1. Living docs sync first (creates us-*.md files)
2. External issue auto-create second (can now use proper content)

## Technology Stack

- **Language**: TypeScript (ESM)
- **Testing**: Vitest
- **Existing utilities**: `isTemplateFile()` from template-creator.ts

## Implementation Phases

### Phase 1: Template Guard (US-001)
- Add `isTemplateFile` import to `external-issue-auto-creator.ts`
- Add template check in `createForIncrement()`
- Add unit tests

### Phase 2: Hook Wiring (US-002)
- Extend `HookConfiguration` type
- Update `LifecycleHookDispatcher.onIncrementPlanned()`
- Update config templates and defaults
- Update JSON schema
- Add unit tests

### Phase 3: Verification (US-003)
- Run existing test suite
- Verify no regressions

## Testing Strategy

- Unit tests for template guard in `ExternalIssueAutoCreator`
- Unit tests for `LifecycleHookDispatcher.onIncrementPlanned` with living docs sync
- All existing tests must pass

## Technical Challenges

### Challenge 1: Template guard false positives
**Solution**: The existing `isTemplateFile()` function has well-defined template markers. We reuse it directly without modification.
**Risk**: Very low - function is already battle-tested.

### Challenge 2: Living docs sync on template spec.md
**Solution**: Living docs sync handles template content gracefully. The template guard on external issue creation is the important safeguard. Living docs with placeholder content is harmless since they get overwritten when spec.md is completed.
**Risk**: Low.
