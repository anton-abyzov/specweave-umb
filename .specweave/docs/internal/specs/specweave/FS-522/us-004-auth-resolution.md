---
id: US-004
feature: FS-522
title: "Auth resolution"
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** developer,."
project: specweave
---

# US-004: Auth resolution

**Feature**: [FS-522](./FEATURE.md)

**As a** developer,
**I want** the command to automatically use my existing GitHub credentials,
**So that** I don't need to manually pass a token.

---

## Acceptance Criteria

- [x] **AC-US4-01**: Auth resolved from `GH_TOKEN` env var first
- [x] **AC-US4-02**: Falls back to `gh auth token` CLI
- [x] **AC-US4-03**: Helpful error if neither is available

---

## Implementation

**Increment**: [0522-specweave-get-bulk](../../../../../increments/0522-specweave-get-bulk/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
