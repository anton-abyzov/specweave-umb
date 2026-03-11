---
id: US-004
feature: FS-485
title: Error Handling and Cancellation (P1)
status: completed
priority: P1
created: 2026-03-11
tldr: "**As a** skill author."
project: vskill
external:
  github:
    issue: 87
    url: https://github.com/anton-abyzov/vskill/issues/87
---

# US-004: Error Handling and Cancellation (P1)

**Feature**: [FS-485](./FEATURE.md)

**As a** skill author
**I want** clear error messages and the ability to cancel a running generation
**So that** I understand what went wrong and don't have to wait for a stuck request

---

## Acceptance Criteria

- [x] **AC-US4-01**: An empty prompt shows inline validation: "Describe what your skill should do"
- [x] **AC-US4-02**: SSE error events are classified (rate_limit, auth, timeout, provider_unavailable, parse_error, unknown) and shown via ErrorCard with category-specific titles, descriptions, and hints
- [x] **AC-US4-03**: Rate-limit errors show a countdown timer before retry is enabled
- [x] **AC-US4-04**: A "Cancel Generation" button appears during generation and aborts the SSE stream
- [x] **AC-US4-05**: Prompt length is validated server-side (max 10,000 characters)
- [x] **AC-US4-06**: Parse failures (non-JSON LLM response) return a 422 with actionable message

---

## Implementation

**Increment**: [0485-skill-studio-ai-create](../../../../../increments/0485-skill-studio-ai-create/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
