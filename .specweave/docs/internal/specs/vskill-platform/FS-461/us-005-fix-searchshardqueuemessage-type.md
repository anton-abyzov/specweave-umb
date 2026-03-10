---
id: US-005
feature: FS-461
title: "Fix SearchShardQueueMessage Type"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** developer."
project: vskill-platform
---

# US-005: Fix SearchShardQueueMessage Type

**Feature**: [FS-461](./FEATURE.md)

**As a** developer
**I want** `SearchShardQueueMessage.entry` to include all fields that `SearchIndexEntry` expects
**So that** incremental shard updates produce complete index entries

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given the `SearchShardQueueMessage` type in `queue/types.ts`, when reviewed, then `entry` includes optional fields `ownerSlug`, `repoSlug`, `skillSlug`, and `trustTier` matching `SearchIndexEntry`
- [ ] **AC-US5-02**: Given all callers that construct `SearchShardQueueMessage`, when they build the `entry` object, then they populate `ownerSlug`, `repoSlug`, `skillSlug`, and `trustTier` from the skill's DB record

---

## Implementation

**Increment**: [0461-skill-star-freshness](../../../../../increments/0461-skill-star-freshness/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
