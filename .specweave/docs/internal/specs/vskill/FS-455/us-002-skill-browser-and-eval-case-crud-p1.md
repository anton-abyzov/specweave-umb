---
id: US-002
feature: FS-455
title: "Skill Browser and Eval Case CRUD (P1)"
status: completed
priority: P1
created: "2026-03-08T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 18
    url: "https://github.com/anton-abyzov/vskill/issues/18"
---

# US-002: Skill Browser and Eval Case CRUD (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** skill developer
**I want** to browse all discovered skills and create, read, update, and delete eval cases with inline assertion editing
**So that** I can manage evals visually instead of editing JSON by hand

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given the UI is loaded, when I view the skills list, then I see all skills discovered by `skill-scanner.ts` grouped by plugin, showing eval count and benchmark status per skill
- [x] **AC-US2-02**: Given I select a skill, when I view its eval cases, then I see each case's name, prompt (truncated), assertion count, and last benchmark status
- [x] **AC-US2-03**: Given I click "Add Eval Case", when I fill in name/prompt/expected_output and add at least one assertion, then the new case is appended to `evals.json` on disk with the next available ID
- [x] **AC-US2-04**: Given I edit an existing eval case's prompt or name, when I save, then `evals.json` is updated on disk immediately (direct filesystem persistence, no draft state)
- [x] **AC-US2-05**: Given I am editing an eval case, when I add, edit, or delete individual assertions inline, then each assertion change persists to `evals.json` on save with proper ID uniqueness validation

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Implement benchmark-history, comparator, and activation-tester eval modules
- [x] **T-004**: Implement REST API routes for skill browsing and eval CRUD
- [x] **T-005**: Build frontend skill browser and eval case CRUD pages
