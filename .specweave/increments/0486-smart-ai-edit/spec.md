---
increment: 0486-smart-ai-edit
title: "AI Edit with Eval Change Suggestions"
status: active
priority: P1
type: feature
created: 2026-03-11
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# AI Edit with Eval Change Suggestions

## Problem Statement

The Skill Studio's AI Edit feature currently only modifies SKILL.md content. When a user changes skill instructions, the associated test cases (evals) often become stale -- assertions may no longer match the updated behavior, new capabilities lack coverage, and removed features still have eval cases testing them. Users must manually audit and update evals after every AI Edit, which is tedious and error-prone.

## Goals

- Extend AI Edit to suggest eval changes alongside SKILL.md content edits in a single LLM call
- Present eval changes as a selectable checklist so users retain full control over which changes to apply
- Support eval suggestions even when no evals exist yet, making AI Edit a one-stop creation tool

## User Stories

### US-001: LLM Returns Eval Change Suggestions
**Project**: vskill

**As a** skill author
**I want** the AI Edit LLM call to analyze my current evals and suggest test case changes alongside SKILL.md edits
**So that** I get a complete picture of what needs updating in one pass

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a skill with existing evals, when the user submits an AI Edit instruction, then the improve endpoint sends current evals to the LLM and returns an `evalChanges` array alongside `improved` and `reasoning`
- [ ] **AC-US1-02**: Given a skill with no evals.json, when the user submits an AI Edit instruction, then the LLM receives an empty evals array and may suggest new test cases from scratch
- [ ] **AC-US1-03**: Each eval change object contains `action` (add | modify | remove), `reason` string, and the full eval case data (for add/modify) or the target eval id (for remove)
- [ ] **AC-US1-04**: Given the LLM response does not contain a valid `---EVAL_CHANGES---` section, then the endpoint returns the SKILL.md result normally with an empty `evalChanges` array (graceful degradation)

---

### US-002: Combined Review Panel
**Project**: vskill

**As a** skill author
**I want** to see both the SKILL.md diff and suggested eval changes in the AI Edit panel
**So that** I can review everything before applying

**Acceptance Criteria**:
- [ ] **AC-US2-01**: When AI Edit returns eval changes, the panel shows eval change cards below the SKILL.md diff, grouped by type: removes first, then modifies, then adds
- [ ] **AC-US2-02**: Each eval change card displays a compact summary (eval name, action badge, reason) with an expandable section showing full eval content
- [ ] **AC-US2-03**: For modify actions, the expanded detail shows a mini-diff of which fields changed between the original and proposed eval case
- [ ] **AC-US2-04**: When AI Edit returns no eval changes, the eval changes section is hidden entirely
- [ ] **AC-US2-05**: Each eval change card has a checkbox that is checked by default; users can toggle individual changes on/off before applying

---

### US-003: Selective Apply of Eval Changes
**Project**: vskill

**As a** skill author
**I want** to choose which eval changes to apply when I click Apply
**So that** I maintain control over my test suite

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When the user clicks Apply, the system saves the improved SKILL.md content AND computes merged evals from the selected eval changes (adds inserted, modifies replaced, removes deleted)
- [ ] **AC-US3-02**: Unchecked eval changes are ignored during apply; only checked changes are merged into the evals file
- [ ] **AC-US3-03**: The merged evals are saved via the existing PUT /evals endpoint
- [ ] **AC-US3-04**: If SKILL.md save succeeds but evals save fails, the SKILL.md change is kept and an error message is shown; the user can retry the evals save
- [ ] **AC-US3-05**: If no eval change checkboxes are checked, only the SKILL.md content is saved (existing behavior preserved)

---

### US-004: Workspace State for Eval Changes
**Project**: vskill

**As a** developer
**I want** the workspace state to track eval change suggestions and checkbox states
**So that** the UI can render and the apply logic can compute the merge correctly

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `WorkspaceState` is extended with `aiEditEvalChanges` (array of eval change objects) and `aiEditEvalSelections` (map of change index to boolean)
- [ ] **AC-US4-02**: New reducer actions handle: setting eval changes from the API response, toggling individual change selections, select-all/deselect-all, and clearing on discard
- [ ] **AC-US4-03**: The `submitAiEdit` function in WorkspaceContext sends current evals to the API and dispatches eval changes from the response

## Out of Scope

- Auto-running affected evals after apply (future increment)
- AI Edit in "auto" improve mode -- this only extends "instruct" mode
- Eval assertion-level diffs (diffs are at the eval case field level, not individual assertion text)
- Undo/revert after apply (users can use "Try Again" or manual editing)
- Streaming/SSE for the improve endpoint (remains a single request/response)

## Technical Notes

### Dependencies
- `improve-routes.ts` -- extend instruct mode prompt and response parsing
- `AiEditBar.tsx` -- add eval changes panel
- `workspaceTypes.ts` / `workspaceReducer.ts` -- new state fields and actions
- `WorkspaceContext.tsx` -- extend `submitAiEdit` and `applyAiEdit`
- `api.ts` -- extend `instructEdit` to send evals and receive eval changes

### Constraints
- LLM response parsing must be fault-tolerant: malformed `---EVAL_CHANGES---` section falls back to empty array
- Eval change IDs for "add" actions need new unique IDs computed client-side (max existing ID + 1, incrementing)

### Architecture Decisions
- Single LLM call returns both SKILL.md and eval changes via structured text sections (`---EVAL_CHANGES---` delimiter), not separate API calls
- Eval changes are represented as a JSON array in the LLM response, parsed server-side
- The merge logic (applying selected changes to existing evals) runs client-side before calling PUT /evals
- No new API endpoints; the existing improve endpoint response shape is extended

## Success Metrics

- AI Edit returns relevant eval suggestions for 80%+ of instructions that change skill behavior
- Users apply at least one eval change in 60%+ of AI Edit sessions that produce suggestions
- Zero regressions in existing AI Edit (SKILL.md-only) flow
