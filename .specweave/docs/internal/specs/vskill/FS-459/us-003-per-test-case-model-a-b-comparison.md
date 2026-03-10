---
id: US-003
feature: FS-459
title: "Per-Test-Case Model A/B Comparison"
status: completed
priority: P1
created: 2026-03-09T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 38
    url: https://github.com/anton-abyzov/vskill/issues/38
---

# US-003: Per-Test-Case Model A/B Comparison

**Feature**: [FS-459](./FEATURE.md)

**As a** skill developer
**I want** to compare two different models on the same eval test case
**So that** I can identify which model performs best for specific scenarios and make informed model selection decisions

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given an eval case on the SkillDetailPage, when the user clicks "Compare Models", then a modal appears with two model selectors (Model A and Model B) allowing independent provider and model selection
- [x] **AC-US3-02**: Given both models are selected and the comparison starts, when executing, then models run sequentially (Model A first, then Model B) with progress indicators showing which model is currently running (e.g., "Model A running..." then "Model A done, Model B running...")
- [x] **AC-US3-03**: Given both models complete, when results are displayed, then the modal shows side-by-side output with assertion pass/fail results for each model, duration, and token counts
- [x] **AC-US3-04**: Given the backend endpoint `POST /api/skills/:plugin/:skill/compare-models` receives `{ eval_id, modelA: { provider, model }, modelB: { provider, model } }`, when processing, then it uses `createLlmClient(overrides)` for each model, runs the eval case with the skill's system prompt, judges assertions for both outputs, and streams results via SSE
- [x] **AC-US3-05**: Given a model comparison completes, when results are shown, then the results are ephemeral (not saved to benchmark history) and the modal can be dismissed

---

## Implementation

**Increment**: [0459-skill-eval-enhancements](../../../../../increments/0459-skill-eval-enhancements/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
