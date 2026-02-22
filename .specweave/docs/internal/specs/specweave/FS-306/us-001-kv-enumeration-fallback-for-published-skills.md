---
id: US-001
feature: FS-306
title: KV Enumeration Fallback for Published Skills
status: complete
priority: P0
created: 2026-02-21
project: specweave
external:
  github:
    issue: 1245
    url: "https://github.com/anton-abyzov/specweave/issues/1245"
---
# US-001: KV Enumeration Fallback for Published Skills

**Feature**: [FS-306](./FEATURE.md)

marketplace visitor
**I want** all published skills to appear in the skill listing
**So that** I can discover community skills even when the KV index blob is stale or corrupted

---

## Acceptance Criteria

- [x] **AC-US1-01**: New function `enumeratePublishedSkills()` in `submission-store.ts` uses `kv.list({ prefix: "skill:" })` with pagination to discover all individual skill keys, excluding `skill:alias:*` keys
- [x] **AC-US1-02**: `getPublishedSkillsList()` calls both the index blob AND `enumeratePublishedSkills()`, returns whichever has MORE entries (with dedup by slug)
- [x] **AC-US1-03**: When enumeration finds more skills than the index, the index is rebuilt from the enumerated data (write-through repair)
- [x] **AC-US1-04**: `enumeratePublishedSkills()` handles KV list pagination correctly (cursor-based, handles `list_complete` flag)
- [x] **AC-US1-05**: Performance: KV enumeration adds at most 500ms latency for up to 5000 keys; results are cached in the existing `_publishedCache` for 60s
- [x] **AC-US1-06**: Unit tests cover: empty index + populated keys scenario, populated index + fewer keys scenario, pagination with multiple pages, alias key exclusion

---

## Implementation

**Increment**: [0306-fix-marketplace-skill-loss](../../../../../increments/0306-fix-marketplace-skill-loss/spec.md)

