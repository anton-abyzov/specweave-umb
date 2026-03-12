---
id: US-003
feature: FS-387
title: "Fix crawler discovery dedup race condition"
status: completed
priority: P1
created: "2026-02-27T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-003: Fix crawler discovery dedup race condition

**Feature**: [FS-387](./FEATURE.md)

**As a** platform operator
**I want** the crawler dedup to be robust against parallel batch processing races
**So that** the same skill is not submitted multiple times in a single discovery run

---

## Acceptance Criteria

- [x] **AC-US3-01**: `markDiscovered` is called BEFORE the HTTP POST to submissions (write-ahead pattern)
- [x] **AC-US3-02**: If the submission POST fails after `markDiscovered`, the record remains (prevents retry loops)
- [x] **AC-US3-03**: Successful submission updates the discovery record with the submissionId

---

## Implementation

**Increment**: [0387-blocklist-dedup-poisoning-fixes](../../../../../increments/0387-blocklist-dedup-poisoning-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
