---
increment: 0493-ai-assisted-skill-authoring
title: AI-Assisted Skill Authoring in Skill Studio
type: feature
priority: P1
status: completed
created: 2026-03-11T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: AI-Assisted Skill Authoring in Skill Studio

## Problem Statement

The `CreateSkillInline` component (used in the Skill Studio right panel) displays a passive banner telling users to "Run /skill-creator in Claude Code" for AI-assisted authoring. This forces users out of the UI into a separate tool. Meanwhile, the standalone `CreateSkillPage` already has a fully working AI generation mode with Manual/AI toggle, prompt textarea, SSE streaming, progress logs, reasoning display, and error handling. The inline creation surface needs the same capability so users never have to leave Skill Studio.

## Goals

- Remove the passive "go somewhere else" banner from the inline create flow
- Add a Manual/AI mode toggle with prompt-based generation directly in CreateSkillInline
- Reuse the existing backend (`POST /api/skills/generate?sse`) and API client (`api.generateSkill()`)
- Match the UX patterns already established in `CreateSkillPage.tsx`
- Preserve the manual-only creation path for users who prefer it

## User Stories

### US-001: AI Mode Toggle (P1)
**Project**: vskill
**As a** skill author using the inline create panel
**I want** a Manual/AI mode toggle replacing the old passive banner
**So that** I can choose between manual form entry and AI-assisted generation without leaving Skill Studio

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the CreateSkillInline panel is open, when the component renders, then a Manual/AI-Assisted toggle is displayed in the header area where the old banner was, with Manual selected by default
- [x] **AC-US1-02**: Given the toggle is visible, when the user clicks "AI-Assisted", then the AI prompt section is shown and the manual form fields are hidden
- [x] **AC-US1-03**: Given the AI mode is active, when the user clicks "Manual", then the manual form fields are shown and the AI prompt section is hidden
- [x] **AC-US1-04**: Given the old passive banner ("AI-Assisted Authoring Available -- Run /skill-creator"), then it is completely removed from the component

---

### US-002: AI Prompt and Generation (P1)
**Project**: vskill
**As a** skill author in AI mode
**I want** a textarea to describe my skill and a "Generate with AI" button
**So that** I can generate a complete skill definition from a natural language description

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given AI mode is active, when the section renders, then a textarea with placeholder guidance and a "Generate Skill" button are displayed
- [x] **AC-US2-02**: Given the prompt textarea is empty, when the user looks at the generate button, then it is visually disabled (grayed out, not-allowed cursor)
- [x] **AC-US2-03**: Given a non-empty prompt, when the user clicks "Generate Skill", then the existing `POST /api/skills/generate?sse` endpoint is called with the prompt via SSE streaming
- [x] **AC-US2-04**: Given AI generation completes successfully, when the response arrives via SSE "done" event, then all form fields (name, description, model, allowedTools, body) are populated from the response and the view switches to manual mode for review
- [x] **AC-US2-05**: Given AI generation returns evals, when switching to manual mode, then pending evals are stored and included in the subsequent create request

---

### US-003: Loading State and Progress (P1)
**Project**: vskill
**As a** skill author waiting for AI generation
**I want** clear loading feedback with progress updates and the ability to cancel
**So that** I know the system is working and can abort if needed

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the generate button is clicked, when generation starts, then the button changes to "Cancel Generation" and the textarea is disabled
- [x] **AC-US3-02**: Given generation is in progress, when SSE progress events arrive, then progress messages are displayed (using the ProgressLog component)
- [x] **AC-US3-03**: Given generation is in progress, when the user clicks "Cancel Generation", then the fetch is aborted via AbortController and the UI returns to the pre-generation state

---

### US-004: AI Reasoning Display (P1)
**Project**: vskill
**As a** skill author reviewing AI-generated content
**I want** to see the AI's reasoning for its design choices
**So that** I can understand and evaluate the generated skill before creating it

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given AI generation completed and populated the form, when the manual mode form is shown, then a collapsible reasoning banner appears at the top showing the AI's reasoning text and pending eval count
- [x] **AC-US4-02**: Given the reasoning banner is visible, when the user clicks the dismiss (X) button, then the banner and pending evals are cleared

---

### US-005: Error Handling with Retry (P1)
**Project**: vskill
**As a** skill author whose AI generation failed
**I want** to see the error inline with an option to retry
**So that** I can recover without starting over

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given AI generation fails with a classified error, when the error event arrives, then an ErrorCard is rendered with the error details and a "Retry" button
- [x] **AC-US5-02**: Given AI generation fails with an unclassified error, when the error occurs, then a simple inline error message is displayed
- [x] **AC-US5-03**: Given an error is displayed, when the user clicks "Retry", then the generation is re-attempted with the same prompt
- [x] **AC-US5-04**: Given an empty prompt, when the user clicks generate, then an inline error "Describe what your skill should do" is shown without making an API call

---

### US-006: Manual Flow Preservation (P1)
**Project**: vskill
**As a** skill author who prefers manual entry
**I want** the manual creation form to work exactly as before
**So that** the AI feature is additive and does not break the existing workflow

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the component loads with Manual mode selected by default, when the user fills in name, description, and body, then the Create Skill button functions identically to the current behavior
- [x] **AC-US6-02**: Given the user never switches to AI mode, when creating a skill, then no AI-related API calls are made

## Out of Scope

- Provider/model selection UI in the inline panel (use defaults from config; the standalone page already has this)
- Modifying the standalone `CreateSkillPage.tsx` (already complete)
- Changes to the backend `/api/skills/generate` endpoint
- Changes to the `api.ts` client methods
- Persisting AI prompt text across mode switches or navigation

## Technical Notes

### Existing Infrastructure
- Backend: `POST /api/skills/generate?sse` in `skill-create-routes.ts` -- fully implemented with SSE streaming, progress events, error classification
- Client: `api.generateSkill()` in `api.ts` -- available but the inline component should use direct `fetch` with SSE like `CreateSkillPage.tsx` does for streaming
- Components: `ProgressLog`, `ErrorCard` -- already exist and are imported in `CreateSkillPage.tsx`
- Reference implementation: `CreateSkillPage.tsx` -- contains the complete working pattern to port

### Key Patterns from CreateSkillPage.tsx
- SSE streaming via `fetch` + `ReadableStream` reader (not the `api.generateSkill()` non-streaming method)
- `AbortController` for cancel support with cleanup on unmount
- Mode state: `"manual" | "ai"` with auto-switch to manual after successful generation
- Purple accent color (`#a855f7`) for AI-related UI elements
- `SparkleIcon` SVG component for AI branding

### Adaptation for Inline Context
- The inline component uses callbacks (`onCreated`, `onCancel`) instead of router navigation
- No breadcrumb navigation needed (inline context)
- Layout is more compact (no side-by-side preview panel needed; existing inline component is single-column)

## Success Metrics

- Banner removal: The passive "/skill-creator" banner no longer appears anywhere in CreateSkillInline
- AI generation works: Users can describe a skill, generate it, review populated fields, and create -- all within the inline panel
- Manual path unbroken: Creating a skill manually without touching AI mode works identically to before
