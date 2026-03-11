---
increment: 0474-ai-command-history
title: "AI commands not recording to history"
type: bug
priority: P1
status: planned
created: 2026-03-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: AI commands not recording to history

## Problem Statement

Skill Studio's History tab does not consistently show entries for all AI-powered commands. While the backend `improve-routes.ts` does call `writeHistoryEntry` for both "improve" (auto) and "instruct" (smart edit) modes, and `model-compare-routes.ts` records model-compare entries, two AI commands never record to history:

1. **AI Skill Generation** (`POST /api/skills/generate` in `skill-create-routes.ts`) -- generates a complete skill definition via LLM but writes no history entry.
2. **AI Eval Generation** (`POST /api/skills/:plugin/:skill/generate-evals` in `api-routes.ts`) -- generates test cases via LLM but writes no history entry.

Additionally, the UI has inconsistencies in how AI command types are handled in the History tab:

- `HistoryPanel.tsx` filter type union omits `"instruct"`, so instruct-type entries cannot be filtered in the workspace panel.
- `HistoryPage.tsx` `TYPE_PILL` map lacks an `"instruct"` key, so instruct entries render without a styled type badge on the full history page.

## Goals

1. Record AI skill generation and AI eval generation to benchmark history so users have a complete audit trail of all AI operations.
2. Ensure all AI command types display correctly in both the workspace History panel and the full History page, including proper filter options and type badges.
3. Maintain backward compatibility with existing history entries and the history file format.

## User Stories

### US-001: AI Skill Generation Appears in History (P1)
**Project**: vskill

**As a** skill author using Skill Studio
**I want** AI-generated skill definitions to appear in the History tab
**So that** I have an audit trail of when and how skills were AI-generated

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `POST /api/skills/generate` successfully returns a generated skill, a history entry with `type: "ai-generate"` is written to the target skill's `evals/history/` directory
- [x] **AC-US1-02**: The history entry includes the model used, provider, timestamp, and the generated skill's name in the `skill_name` field
- [x] **AC-US1-03**: The history entry stores the generation prompt and resulting skill content in a `generate` field (analogous to the `improve` field used by improve entries)

---

### US-002: AI Eval Generation Appears in History (P1)
**Project**: vskill

**As a** skill author using Skill Studio
**I want** AI-generated test cases to appear in the History tab
**So that** I can track when evals were auto-generated and which model was used

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `POST /api/skills/:plugin/:skill/generate-evals` successfully returns generated evals, a history entry with `type: "eval-generate"` is written to the skill's `evals/history/` directory
- [x] **AC-US2-02**: The history entry includes the model used, provider, timestamp, skill name, and the number of generated test cases
- [x] **AC-US2-03**: The history entry is visible in the History tab timeline alongside benchmark and improve entries

---

### US-003: All AI Types Display Correctly in History UI (P2)
**Project**: vskill

**As a** skill author using Skill Studio
**I want** all AI command types to have proper type badges and filter options in the History tab
**So that** I can distinguish and filter between different types of AI operations

**Acceptance Criteria**:
- [x] **AC-US3-01**: `HistoryPanel.tsx` filter type union includes `"instruct"` so instruct entries can be filtered in the workspace panel
- [x] **AC-US3-02**: `HistoryPage.tsx` `TYPE_PILL` map includes entries for `"instruct"`, `"ai-generate"`, and `"eval-generate"` with distinct colors and labels
- [x] **AC-US3-03**: `HistoryPage.tsx` `FilterBar` type dropdown includes options for "AI Edit", "AI Generate", and "Eval Generate"
- [x] **AC-US3-04**: Backend `HistorySummary` and `HistoryFilter` type unions include the new `"ai-generate"` and `"eval-generate"` types
- [x] **AC-US3-05**: Frontend `types.ts` type unions are updated to match backend types

## Functional Requirements

### FR-001: History Entry for AI Skill Generation
After a successful LLM call in `POST /api/skills/generate`, call `writeHistoryEntry` with `type: "ai-generate"`. Since the skill may not yet exist on disk (it is generated before being created), the history entry should be written after the skill is actually created via `POST /api/skills/create`, or alternatively stored at a project-level history location.

### FR-002: History Entry for AI Eval Generation
After a successful LLM call in `POST /api/skills/:plugin/:skill/generate-evals`, call `writeHistoryEntry` with `type: "eval-generate"`. The skill directory already exists at this point, so the entry goes to the standard `evals/history/` path.

### FR-003: Type System Alignment
All type unions across backend (`benchmark-history.ts`, `benchmark.ts`) and frontend (`types.ts`) must include the new types. The `HistoryFilter` type in the backend API route's type validation must accept the new type values.

## Success Criteria

- All 6 AI command types (benchmark, baseline, comparison, improve, instruct, model-compare, ai-generate, eval-generate) appear in the History tab when executed
- Filter dropdowns in both History views include all AI command types
- Type badges render with distinct colors for each AI command type
- Existing history entries continue to display correctly (no regressions)

## Out of Scope

- Activation test history recording (activation tests are ephemeral and do not persist results)
- Changing the history file format or storage location
- Adding undo/revert capabilities for AI-generated content
- History entries for non-AI operations (manual SKILL.md edits, manual eval edits)

## Dependencies

- `benchmark-history.ts` `writeHistoryEntry` function (already exists, supports arbitrary `type` strings)
- `BenchmarkResult` type (may need extension for new `generate` field)
- Eval server route handlers (`skill-create-routes.ts`, `api-routes.ts`)

## Technical Notes

### Files to Modify (Backend)
- `src/eval-server/skill-create-routes.ts` -- add `writeHistoryEntry` call after successful generation
- `src/eval-server/api-routes.ts` -- add `writeHistoryEntry` call in `generate-evals` handler
- `src/eval/benchmark-history.ts` -- extend `HistorySummary.type` and `HistoryFilter.type` unions
- `src/eval/benchmark.ts` -- extend `BenchmarkResult.type` if needed

### Files to Modify (Frontend)
- `src/eval-ui/src/types.ts` -- extend type unions for `HistorySummary`, `HistoryFilter`, `BenchmarkResult`, `CaseHistoryEntry`
- `src/eval-ui/src/pages/workspace/HistoryPanel.tsx` -- add `"instruct"` to filter type union
- `src/eval-ui/src/pages/HistoryPage.tsx` -- add missing entries to `TYPE_PILL` map and `FilterBar` dropdown

### Key Observation
The `writeHistoryEntry` function accepts `type` as a string union but the actual JSON file format is flexible -- any string type is written and read back. The primary concern is type safety in TypeScript and correct rendering in the UI.
