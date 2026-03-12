---
id: US-005
feature: FS-493
title: "Error Handling with Retry (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author whose AI generation failed."
project: vskill
---

# US-005: Error Handling with Retry (P1)

**Feature**: [FS-493](./FEATURE.md)

**As a** skill author whose AI generation failed
**I want** to see the error inline with an option to retry
**So that** I can recover without starting over

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given AI generation fails with a classified error, when the error event arrives, then an ErrorCard is rendered with the error details and a "Retry" button
- [x] **AC-US5-02**: Given AI generation fails with an unclassified error, when the error occurs, then a simple inline error message is displayed
- [x] **AC-US5-03**: Given an error is displayed, when the user clicks "Retry", then the generation is re-attempted with the same prompt
- [x] **AC-US5-04**: Given an empty prompt, when the user clicks generate, then an inline error "Describe what your skill should do" is shown without making an API call

---

## Implementation

**Increment**: [0493-ai-assisted-skill-authoring](../../../../../increments/0493-ai-assisted-skill-authoring/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Write failing tests for error scenarios
- [x] **T-012**: Render ErrorCard and inline error with retry
