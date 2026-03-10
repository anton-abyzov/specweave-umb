---
id: US-004
feature: FS-455
title: "WITH vs WITHOUT Skill Comparison (P1)"
status: completed
priority: P1
created: 2026-03-08T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 20
    url: https://github.com/anton-abyzov/vskill/issues/20
---

# US-004: WITH vs WITHOUT Skill Comparison (P1)

**Feature**: [FS-455](./FEATURE.md)

**As a** skill developer
**I want** to run each eval prompt both WITH and WITHOUT the skill loaded, then see a blind comparison
**So that** I can measure whether my skill actually improves LLM output quality

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given I click "Run Comparison", when the system executes, then each eval prompt is sent twice: once with SKILL.md as system context and once without, producing two outputs per case
- [x] **AC-US4-02**: Given both outputs are generated, when the blind comparator scores them, then each output receives a content score (1-5) and a structure score (1-5), plus a "which is better" verdict -- without the comparator knowing which output had the skill loaded
- [x] **AC-US4-03**: Given comparison results are ready, when I view them in the UI, then I see a side-by-side view with scores, verdict, and the ability to reveal which response was WITH-skill vs WITHOUT-skill
- [x] **AC-US4-04**: Given a comparison completes, when results are persisted, then they are stored in the same `evals/history/` timestamped file with a `type: "comparison"` discriminator

---

## Implementation

**Increment**: [0455-skill-eval-ui](../../../../../increments/0455-skill-eval-ui/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Implement SSE comparison endpoint with blind A/B scoring
- [x] **T-009**: Build comparison UI with side-by-side view and reveal toggle
