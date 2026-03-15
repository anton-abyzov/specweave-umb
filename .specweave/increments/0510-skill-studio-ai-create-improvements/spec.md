---
increment: 0510-skill-studio-ai-create-improvements
title: "Skill Studio AI-Assisted Create Improvements"
type: feature
priority: P1
status: active
created: 2026-03-12
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio AI-Assisted Create Improvements

## Overview

Polish the AI-assisted skill creation UX in Skill Studio by removing unnecessary UI elements, fixing preview rendering, and improving button labels. The core AI generation, draft-saving, folder visualization, and plugin recommendation features are already implemented — this increment focuses on streamlining the create experience and eliminating code duplication.

## User Stories

### US-001: Streamline AI Create UI (P1)
**Project**: vskill

**As a** skill creator
**I want** a clean, focused AI creation interface without unnecessary banners or test case generation
**So that** I can quickly create skills without visual clutter

**Acceptance Criteria**:
- [x] **AC-US1-01**: The AI mode prompt area does not display verbose help text below the textarea (remove "The AI will generate the name, description, system prompt, and test cases" paragraph)
- [x] **AC-US1-02**: AI generation does not pass or save test cases (evals) during skill creation — evals are handled separately in the workspace after creation
- [x] **AC-US1-03**: The SkillFileTree does not show an evals directory when creating via AI (since evals are no longer generated during creation)

---

### US-002: Fix Create Button Labels (P1)
**Project**: vskill

**As a** skill creator
**I want** the create button to always say "Create Skill" regardless of creation method
**So that** the action is clear and consistent

**Acceptance Criteria**:
- [x] **AC-US2-01**: The submit button shows "Create Skill" for both manual and AI-generated skills (not "Save" for AI-generated)
- [x] **AC-US2-02**: The button label change applies to both CreateSkillPage and CreateSkillInline components

---

### US-003: Fix Preview Mode in Create Flow (P1)
**Project**: vskill

**As a** skill creator
**I want** the SKILL.md preview to render markdown correctly when toggling to Preview mode
**So that** I can review how my skill definition will look before creating it

**Acceptance Criteria**:
- [x] **AC-US3-01**: The Write/Preview toggle in CreateSkillInline renders markdown body content correctly in Preview mode
- [x] **AC-US3-02**: The Write/Preview toggle in CreateSkillPage renders markdown body content correctly in Preview mode
- [x] **AC-US3-03**: Empty body in Preview mode shows a placeholder message

---

### US-004: Deduplicate Create Skill Components (P2)
**Project**: vskill

**As a** developer
**I want** shared logic between CreateSkillPage and CreateSkillInline extracted into a reusable hook
**So that** changes only need to be made in one place

**Acceptance Criteria**:
- [x] **AC-US4-01**: A `useCreateSkill` custom hook encapsulates shared state and handlers (layout detection, form state, AI generation, draft saving, plugin recommendation)
- [x] **AC-US4-02**: Both CreateSkillPage and CreateSkillInline consume the shared hook instead of duplicating logic
- [x] **AC-US4-03**: Both components behave identically to before the refactor (no functional regression)

## Functional Requirements

### FR-001: Remove AI Help Text
Remove the descriptive paragraph below the AI prompt textarea that explains what AI will generate. The placeholder text in the textarea itself is sufficient guidance.

### FR-002: Remove Eval Generation from Create Flow
Stop passing evals to `createSkill` and `saveDraft` API calls. The `pendingEvals` state should be removed from create components. Evals are a workspace concern handled in the Tests panel after skill creation.

### FR-003: Consistent Button Label
Change the conditional `aiGenerated ? "Save" : "Create Skill"` to always render "Create Skill".

### FR-004: Preview Mode Correctness
Verify the Write/Preview toggle renders correctly via `renderMarkdown`. Empty-state placeholder must show properly.

### FR-005: Shared Hook Extraction
Extract `useCreateSkill` hook from the ~90% shared logic between CreateSkillPage and CreateSkillInline to eliminate code duplication.

## Success Criteria

- AI create flow is visually cleaner with no verbose help text
- Button label is always "Create Skill"
- No eval/test case generation during skill creation
- Code duplication between CreateSkillPage and CreateSkillInline is eliminated via shared hook
- All existing tests pass

## Out of Scope

- Changes to AI Edit flow (AiEditBar) — that's a separate workspace feature
- Changes to the generation API endpoint itself
- New AI generation features
- Changes to the eval/test workspace panels

## Dependencies

- Existing Skill Studio eval-ui codebase in `repositories/anton-abyzov/vskill/src/eval-ui/`
- Existing skill creation API routes in `repositories/anton-abyzov/vskill/src/eval-server/skill-create-routes.ts`
