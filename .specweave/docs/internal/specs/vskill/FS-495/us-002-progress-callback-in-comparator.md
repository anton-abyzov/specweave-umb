---
id: US-002
feature: FS-495
title: "Progress Callback in Comparator"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** backend developer."
project: vskill
---

# US-002: Progress Callback in Comparator

**Feature**: [FS-495](./FEATURE.md)

**As a** backend developer
**I want** an optional `onProgress` callback parameter on `generateComparisonOutputs()` and `runComparison()`
**So that** callers can receive phase transition events at each of the 3 LLM call boundaries

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given `generateComparisonOutputs(prompt, skillContent, client, onProgress)` is called, when the skill generation LLM call starts, then `onProgress` fires with phase `generating_skill`
- [x] **AC-US2-02**: Given `generateComparisonOutputs()` is executing, when the baseline generation LLM call starts, then `onProgress` fires with phase `generating_baseline`
- [x] **AC-US2-03**: Given `runComparison(prompt, skillContent, client, onProgress)` is called, when the rubric scoring LLM call starts, then `onProgress` fires with phase `scoring`
- [x] **AC-US2-04**: Given no `onProgress` callback is provided, when `runComparison()` is called, then it behaves identically to the current implementation (no regression)

---

## Implementation

**Increment**: [0495-comparison-progress-observability](../../../../../increments/0495-comparison-progress-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add `onProgress` callback to `generateComparisonOutputs()` and `runComparison()`
- [x] **T-004**: Verify no regression when `onProgress` is omitted
