---
id: US-003
feature: FS-522
title: "Filtering options"
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** developer,."
project: specweave
---

# US-003: Filtering options

**Feature**: [FS-522](./FEATURE.md)

**As a** developer,
**I want to** skip archived repos and forks when bulk cloning,
**So that** I only get active, first-party repositories.

**Acceptance Criteria:**
- [x] AC-US3-01: `--no-archived` filters out repos where `archived: true`
- [x] AC-US3-02: `--no-forks` filters out repos where `fork: true`
- [x] AC-US3-03: `--limit <n>` caps the number of repos fetched (default: 1000)

---

## Acceptance Criteria

- [x] **AC-US3-01**: `--no-archived` filters out repos where `archived: true`
- [x] **AC-US3-02**: `--no-forks` filters out repos where `fork: true`
- [x] **AC-US3-03**: `--limit <n>` caps the number of repos fetched (default: 1000)

---

## Implementation

**Increment**: [0522-specweave-get-bulk](../../../../../increments/0522-specweave-get-bulk/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
