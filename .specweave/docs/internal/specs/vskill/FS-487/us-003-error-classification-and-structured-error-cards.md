---
id: US-003
feature: FS-487
title: "Error Classification and Structured Error Cards"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 76
    url: "https://github.com/anton-abyzov/vskill/issues/76"
---

# US-003: Error Classification and Structured Error Cards

**Feature**: [FS-487](./FEATURE.md)

**As a** skill developer
**I want** errors from AI operations to be classified into categories with actionable hints
**So that** I can quickly understand what went wrong and how to fix it

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given an AI operation fails, then the server-side error is classified into one of these categories: `rate_limit`, `context_window`, `auth`, `timeout`, `provider_unavailable`, `parse_error`, `unknown`
- [x] **AC-US3-02**: Given a `rate_limit` error occurs, then the error card shows a countdown timer (using `retry-after` header value, defaulting to 30 seconds if absent) and an inline Retry button
- [x] **AC-US3-03**: Given a `context_window` error occurs, then the error card shows a hint like "SKILL.md content is too large for this model. Try a model with a larger context window or reduce the skill content."
- [x] **AC-US3-04**: Given any classified error occurs, then the frontend renders a structured error card with: category icon, error title, description, actionable hint, and Retry button -- replacing the current plain red error box
- [x] **AC-US3-05**: Given a CLI provider (claude-cli, codex-cli, gemini-cli) returns an error via stderr, then regex pattern matching classifies it into the appropriate error category rather than showing the raw stderr text

---

## Implementation

**Increment**: [0487-skill-studio-execution-observability](../../../../../increments/0487-skill-studio-execution-observability/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-008**: Create ErrorCard component
- [x] **T-009**: Wire ErrorCard into all AI operation components
