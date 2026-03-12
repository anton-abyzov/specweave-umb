---
id: US-005
feature: FS-472
title: "Unit Tests for Classification Logic"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** developer maintaining the activation tester."
project: vskill
external:
  github:
    issue: 71
    url: "https://github.com/anton-abyzov/vskill/issues/71"
---

# US-005: Unit Tests for Classification Logic

**Feature**: [FS-472](./FEATURE.md)

**As a** developer maintaining the activation tester
**I want** comprehensive unit tests for the new classification flow
**So that** regressions are caught early

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given a mock LLM returning `{"related": true}`, when `classifyExpectation` is called, then it returns `"should_activate"`
- [ ] **AC-US5-02**: Given a mock LLM returning `{"related": false}`, when `classifyExpectation` is called, then it returns `"should_not_activate"`
- [ ] **AC-US5-03**: Given a mock LLM that throws an error, when `classifyExpectation` is called, then it returns `"should_activate"` (fallback)
- [ ] **AC-US5-04**: Given prompts with mixed prefixes (none, `+`, `!`), when `testActivation` runs with `SkillMeta`, then only unprefixed prompts go through classification

---

## Implementation

**Increment**: [0472-activation-auto-classify](../../../../../increments/0472-activation-auto-classify/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [ ] **T-007**: Write comprehensive unit tests for classifyExpectation and two-phase testActivation
