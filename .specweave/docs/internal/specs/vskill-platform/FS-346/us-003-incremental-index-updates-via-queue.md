---
id: US-003
feature: FS-346
title: Incremental Index Updates via Queue
status: complete
priority: P2
created: 2026-02-24
project: vskill-platform
---
# US-003: Incremental Index Updates via Queue

**Feature**: [FS-346](./FEATURE.md)

platform operator
**I want** the search index to update incrementally when skills are published, updated, or deprecated
**So that** the index stays current without full rebuilds

---

## Acceptance Criteria

- [x] **AC-US3-01**: After `publishSkill()` completes in `src/lib/submission-store.ts`, a `rebuild-search-index` queue message is dispatched containing `{ type: "rebuild_search_shard", skillName, action: "upsert" | "remove" }`
- [x] **AC-US3-02**: A new queue consumer handler processes `rebuild_search_shard` messages: reads the affected shard from KV, upserts or removes the skill entry, writes the shard back
- [x] **AC-US3-03**: The queue message is dispatched to the existing `SUBMISSION_QUEUE` (or a dedicated queue if type discrimination is cleaner) with a distinct `type` field to differentiate from `process_submission` messages
- [x] **AC-US3-04**: If the shard read/write fails, the message is retried via standard queue retry semantics
- [x] **AC-US3-05**: The metadata key `search-index:meta` is updated with `totalSkills` and `builtAt` after each incremental update

---

## Implementation

**Increment**: [0346-edge-first-search-performance](../../../../../increments/0346-edge-first-search-performance/spec.md)

