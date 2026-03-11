---
increment: 0472-activation-auto-classify
title: "Auto-classify activation test expectations"
type: bug
priority: P1
status: planned
created: 2026-03-10
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Auto-classify Activation Test Expectations

## Problem Statement

In the Skill Studio Activation Panel, test prompts without a `!` prefix default to `expected: "should_activate"`. When users type irrelevant prompts (e.g., "I built my test" for a Slack messaging skill), the system incorrectly expects activation, producing false FN results and corrupting precision/recall metrics. This makes the activation panel unreliable for iterating on skill descriptions.

## Goals

- Eliminate false FN results caused by ambiguous unlabeled prompts
- Introduce LLM-based auto-classification using skill name and tags
- Maintain backward compatibility for existing `!` prefix convention
- Add explicit `+` prefix for force-activate labeling

## User Stories

### US-001: Two-Phase Activation Evaluation
**Project**: vskill
**As a** skill author
**I want** unlabeled prompts to be auto-classified before evaluation
**So that** irrelevant prompts are correctly expected to not activate, producing accurate metrics

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a prompt with no prefix and skill metadata (name + tags) available, when the activation test runs, then Phase 1 classifies expected behavior via LLM before Phase 2 evaluates activation
- [x] **AC-US1-02**: Given multiple unlabeled prompts, when the test runs, then all auto-classifications are batched in Phase 1 before any Phase 2 evaluations begin
- [x] **AC-US1-03**: Given a prompt with `+` prefix, when the test runs, then it is treated as explicit `should_activate` and skips Phase 1 classification
- [x] **AC-US1-04**: Given a prompt with `!` prefix, when the test runs, then it is treated as explicit `should_not_activate` and skips Phase 1 classification (existing behavior preserved)

---

### US-002: Classification Prompt and Cross-Model Compatibility
**Project**: vskill
**As a** skill author using different LLM providers
**I want** the classification prompt to work across Claude, Llama, Qwen, and other models
**So that** auto-classification is reliable regardless of the selected provider

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a classification request, when the LLM is called, then the prompt uses only skill name and tags (NOT the full description) and requests minimal JSON output `{"related": true/false}`
- [x] **AC-US2-02**: Given the classification LLM returns invalid JSON or errors, when processing the result, then the system defaults to `should_activate` (backward compatibility)
- [x] **AC-US2-03**: Given a SKILL.md with no frontmatter name or tags, when the test runs, then classification is skipped entirely and unlabeled prompts default to `should_activate`

---

### US-003: Server-Side Metadata Extraction
**Project**: vskill
**As a** the activation test API route
**I want** to extract skill name and tags from SKILL.md frontmatter
**So that** the classification phase has the metadata it needs without accessing the full description

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a SKILL.md with frontmatter containing `name` and `metadata.tags`, when the activation-test endpoint is called, then name and tags are extracted and passed to `testActivation` as `SkillMeta`
- [x] **AC-US3-02**: Given a SKILL.md with missing or empty tags, when metadata is extracted, then `tags` is an empty array and classification falls back to `should_activate`

---

### US-004: Client Prefix Handling and UI Updates
**Project**: vskill
**As a** skill author using the Activation Panel
**I want** clear visual feedback on which prompts were auto-classified
**So that** I can understand and trust the test results

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given a prompt with no prefix, when sent to the server, then the client sends `expected: "auto"` instead of `"should_activate"`
- [x] **AC-US4-02**: Given a prompt with `+` prefix, when sent to the server, then the client sends `expected: "should_activate"` with the prefix stripped
- [x] **AC-US4-03**: Given activation results containing auto-classified prompts, when displayed in the UI, then an "Auto" badge is shown next to the resolved expectation
- [x] **AC-US4-04**: Given the Activation Panel help text, when viewing the prompt input area, then it documents all three conventions: no prefix (auto), `+` (activate), `!` (not activate)

---

### US-005: Unit Tests for Classification Logic
**Project**: vskill
**As a** developer maintaining the activation tester
**I want** comprehensive unit tests for the new classification flow
**So that** regressions are caught early

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a mock LLM returning `{"related": true}`, when `classifyExpectation` is called, then it returns `"should_activate"`
- [x] **AC-US5-02**: Given a mock LLM returning `{"related": false}`, when `classifyExpectation` is called, then it returns `"should_not_activate"`
- [x] **AC-US5-03**: Given a mock LLM that throws an error, when `classifyExpectation` is called, then it returns `"should_activate"` (fallback)
- [x] **AC-US5-04**: Given prompts with mixed prefixes (none, `+`, `!`), when `testActivation` runs with `SkillMeta`, then only unprefixed prompts go through classification

## Out of Scope

- User-overridable classification results in the UI
- Separate "cheap model" selection for the classification phase
- Classification using the full skill description (intentionally uses only name + tags)
- Persisting classification results between test runs

## Technical Notes

### Architecture Decision: Two-Phase Batched Flow

Phase 1 (classify) runs for ALL auto-labeled prompts first, then Phase 2 (evaluate) runs for ALL prompts. This is more efficient than interleaving and keeps the phases cleanly separated.

### Key Types

- `SkillMeta`: `{ name: string; tags: string[] }` -- passed to `testActivation`
- `ActivationPrompt.expected`: extended to accept `"auto"` in addition to existing values
- `ActivationResult.autoClassified`: boolean flag for UI badge rendering

### Files Changed

1. `src/eval/activation-tester.ts` -- `SkillMeta` interface, `classifyExpectation()`, two-phase `testActivation` flow
2. `src/eval-server/api-routes.ts` -- extract name/tags from SKILL.md frontmatter, pass as `SkillMeta`
3. `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` -- send `"auto"` for unlabeled prompts
4. `src/eval-ui/src/pages/workspace/ActivationPanel.tsx` -- help text update, auto badge
5. `src/eval-ui/src/types.ts` -- `autoClassified` field on `ActivationResult`
6. `src/eval/__tests__/activation-tester.test.ts` -- 4+ new test cases

## Success Criteria

- Unlabeled irrelevant prompts are correctly classified as `should_not_activate`, eliminating false FN
- All existing `!`-prefixed test prompts continue to work identically
- Metrics (precision, recall, reliability) reflect accurate expectations
