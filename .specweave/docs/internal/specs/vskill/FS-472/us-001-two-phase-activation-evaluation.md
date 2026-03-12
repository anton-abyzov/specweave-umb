---
id: US-001
feature: FS-472
title: "Two-Phase Activation Evaluation"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 67
    url: "https://github.com/anton-abyzov/vskill/issues/67"
---

# US-001: Two-Phase Activation Evaluation

**Feature**: [FS-472](./FEATURE.md)

**As a** skill author
**I want** unlabeled prompts to be auto-classified before evaluation
**So that** irrelevant prompts are correctly expected to not activate, producing accurate metrics

---

## Acceptance Criteria

- [ ] **AC-US1-01**: Given a prompt with no prefix and skill metadata (name + tags) available, when the activation test runs, then Phase 1 classifies expected behavior via LLM before Phase 2 evaluates activation
- [ ] **AC-US1-02**: Given multiple unlabeled prompts, when the test runs, then all auto-classifications are batched in Phase 1 before any Phase 2 evaluations begin
- [ ] **AC-US1-03**: Given a prompt with `+` prefix, when the test runs, then it is treated as explicit `should_activate` and skips Phase 1 classification
- [ ] **AC-US1-04**: Given a prompt with `!` prefix, when the test runs, then it is treated as explicit `should_not_activate` and skips Phase 1 classification (existing behavior preserved)

---

## Implementation

**Increment**: [0472-activation-auto-classify](../../../../../increments/0472-activation-auto-classify/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-001**: Add SkillMeta type and classifyExpectation function to activation-tester.ts
- [ ] **T-002**: Implement two-phase flow in testActivation
