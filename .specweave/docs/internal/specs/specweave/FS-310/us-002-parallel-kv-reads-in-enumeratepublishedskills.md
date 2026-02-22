---
id: US-002
feature: FS-310
title: Parallel KV reads in enumeratePublishedSkills
status: complete
priority: P1
created: 2026-02-22
project: specweave
external:
  github:
    issue: 1262
    url: https://github.com/anton-abyzov/specweave/issues/1262
---
# US-002: Parallel KV reads in enumeratePublishedSkills

**Feature**: [FS-310](./FEATURE.md)

marketplace user browsing published skills
**I want** `enumeratePublishedSkills` to read all `skill:*` KV keys in parallel
**So that** marketplace enumeration is fast even with hundreds of published skills

---

## Acceptance Criteria

- [x] **AC-US2-01**: `enumeratePublishedSkills` uses `Promise.allSettled` to read all `skill:*` keys concurrently instead of a sequential `for` loop
- [x] **AC-US2-02**: Individual KV read failures or malformed JSON are silently skipped, matching the existing `catch { /* skip malformed */ }` behavior
- [x] **AC-US2-03**: Alias keys (`skill:alias:*`) are still filtered out before reads

---

## Implementation

**Increment**: [0310-parallel-kv-asynclocalstorage](../../../../../increments/0310-parallel-kv-asynclocalstorage/spec.md)

