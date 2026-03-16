# Implementation Plan: AI commands not recording to history

## Overview

This is a P1 bug fix addressing missing history entries for AI-powered commands in Skill Studio. Two backend endpoints (`/api/skills/generate` and `/api/skills/:plugin/:skill/generate-evals`) do not call `writeHistoryEntry`, and the frontend has gaps in type handling for `"instruct"` entries. The fix is entirely additive -- no existing behavior changes.

## Architecture

### Components Affected

- **eval-server/skill-create-routes.ts**: Add history recording after AI skill creation
- **eval-server/api-routes.ts**: Add history recording after AI eval generation
- **eval/benchmark-history.ts**: Extend `HistorySummary.type` and `HistoryFilter.type` unions with new values
- **eval/benchmark.ts**: Extend `BenchmarkResult.type` union if needed
- **eval-ui/src/types.ts**: Mirror backend type extensions
- **eval-ui/src/pages/workspace/HistoryPanel.tsx**: Add missing `"instruct"` to filter union
- **eval-ui/src/pages/HistoryPage.tsx**: Add `TYPE_PILL` entries and filter options for all AI types

### Data Model

No schema changes. History entries are JSON files in `evals/history/` with flexible structure. New entries use the same `BenchmarkResult` shape with:
- `type: "eval-generate"` for AI-generated evals
- `type: "ai-generate"` for AI-generated skills (recorded at creation time)

New optional fields on `BenchmarkResult`:
- `generate?: { prompt: string; result: string }` -- stores the generation input/output

## Architecture Decisions

### ADR-1: Record AI Skill Generation at Creation Time
AI skill generation (`/api/skills/generate`) returns a definition the user may discard. Recording history only when the skill is actually saved via `/api/skills/create` avoids phantom entries. The `evals` presence in the create request indicates AI generation was used.

### ADR-2: New Type Values
Two new types: `"ai-generate"` and `"eval-generate"`. Distinct from `"improve"`/`"instruct"` because generation creates new content rather than modifying existing content.

### ADR-3: Backward Compatibility
All changes are additive. Existing history files with old types continue to render. New type values only appear for new operations. The `writeHistoryEntry` function already handles arbitrary type strings at runtime.

## Implementation Phases

### Phase 1: Backend Type Extensions
Extend TypeScript unions in `benchmark-history.ts` and `benchmark.ts`. This is pure type-level work with no runtime impact.

### Phase 2: Backend History Recording
Add `writeHistoryEntry` calls in `api-routes.ts` (generate-evals) and `skill-create-routes.ts` (create with AI content). Import `writeHistoryEntry` where needed.

### Phase 3: Frontend Fixes
Update `types.ts` unions. Fix `HistoryPanel.tsx` filter. Add `TYPE_PILL` entries and filter options in `HistoryPage.tsx`.

### Phase 4: Testing
Unit tests for new history recording. Verify existing tests still pass.

## Testing Strategy

- **Unit tests**: Verify `writeHistoryEntry` is called with correct type and payload in the generate-evals and skill-create handlers
- **Type tests**: TypeScript compilation verifies type union correctness
- **Manual verification**: Run Skill Studio, generate evals, check History tab

## Technical Challenges

### Challenge 1: Skill Generation Has No Skill Directory Yet
**Solution**: Record history when skill is created (POST /api/skills/create), not when generated. The skill directory exists after creation.
**Risk**: Low -- the create endpoint already has the skill directory path computed.
