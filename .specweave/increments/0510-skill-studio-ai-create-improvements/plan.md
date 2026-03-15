# Implementation Plan: Skill Studio AI-Assisted Create Improvements

## Overview

This increment streamlines the AI-assisted skill creation UX by removing unnecessary UI elements, fixing labels, and extracting shared logic into a reusable hook. All changes are frontend-only in the vskill eval-ui codebase.

## Architecture

### Components Modified
- `CreateSkillInline.tsx` — Sidebar create component (766 lines → ~150 lines after hook extraction)
- `CreateSkillPage.tsx` — Standalone route component (963 lines → ~250 lines after hook extraction)
- `SkillFileTree.tsx` — Folder structure visualization (109 lines, minor change)

### New Components
- `useCreateSkill.ts` — Shared custom hook extracting ~600 lines of duplicated logic

### Data Flow (unchanged)
```
UI Form → POST /api/skills/generate (SSE) → Populate Form → POST /api/skills/create
                                            → POST /api/skills/save-draft (auto)
```

### Key Change: Remove Evals from Create Flow
- `pendingEvals` state removed from both components
- `evals` field no longer passed to `createSkill()` or `saveDraft()` calls
- Backend API already treats `evals` as optional — no server changes needed
- SkillFileTree `hasEvals` prop always `false` during creation

## Technology Stack

- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **Test**: Vitest (lightweight component tests using direct function calls)

**Architecture Decisions**:
- **Custom hook over HOC/render props**: `useCreateSkill` hook is the idiomatic React approach for sharing stateful logic between components with different UI
- **No backend changes**: The `evals` parameter in API routes is already optional; frontend simply stops sending it
- **Keep both components**: CreateSkillPage (full route) and CreateSkillInline (sidebar) serve different UI contexts and have different navigation/layout needs

## Implementation Phases

### Phase 1: Extract Shared Hook (US-004)
- Create `useCreateSkill.ts` with all shared state and handlers
- Refactor both components to use the hook
- Verify no functional regression

### Phase 2: UI Cleanup (US-001, US-002, US-003)
- Remove AI help text from both components
- Remove pendingEvals usage (hook doesn't expose it)
- Change button label to always "Create Skill"
- Verify preview mode works correctly

### Phase 3: Testing
- Write unit tests for `useCreateSkill` hook
- Write component tests for UI changes
- Run full test suite

## Testing Strategy

- Vitest with direct function/component calls (no DOM — matches existing test patterns)
- Test the shared hook's state transitions and handler behavior
- Test that components render correct labels and omit removed elements
- Run `npx vitest run` from vskill repo root

## Technical Challenges

### Challenge 1: Different Navigation Patterns
**Problem**: CreateSkillPage uses `useNavigate()` from react-router, while CreateSkillInline uses callback props (`onCreated`, `onCancel`).
**Solution**: The hook accepts an `onCreated` callback. CreateSkillPage wraps it with `navigate()`, CreateSkillInline passes it directly.

### Challenge 2: Different Config Patterns
**Problem**: CreateSkillPage has explicit provider/model dropdowns, CreateSkillInline uses shared config context.
**Solution**: The hook handles both — exposes `resolveAiConfig()` that components can override with explicit selections.
