---
id: US-005
feature: FS-522
title: "Single-repo backward compatibility"
status: completed
priority: P1
created: 2026-03-14
tldr: "**As a** developer,."
project: specweave
---

# US-005: Single-repo backward compatibility

**Feature**: [FS-522](./FEATURE.md)

**As a** developer,
**I want** existing `specweave get owner/repo` behavior unchanged,
**So that** bulk mode doesn't break single-repo usage.

---

## Acceptance Criteria

- [x] **AC-US5-01**: Source without glob chars and no `--all` flag → single-repo foreground clone (existing path)
- [x] **AC-US5-02**: All existing options (`--branch`, `--prefix`, `--role`, `--no-init`) still work in single-repo mode

---

## Implementation

**Increment**: [0522-specweave-get-bulk](../../../../../increments/0522-specweave-get-bulk/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
