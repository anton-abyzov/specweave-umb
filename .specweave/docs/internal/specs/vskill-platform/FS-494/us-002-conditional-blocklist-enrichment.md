---
id: US-002
feature: FS-494
title: "Conditional Blocklist Enrichment"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** user searching for skills."
project: vskill-platform
---

# US-002: Conditional Blocklist Enrichment

**Feature**: [FS-494](./FEATURE.md)

**As a** user searching for skills
**I want** search to skip unnecessary blocklist DB queries for edge-only responses
**So that** search latency is not inflated by DB round-trips when KV already excludes blocked skills

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given search results came exclusively from edge KV, when blocklist enrichment runs, then `getBlockedSkillNames()` is NOT called (KV index already excludes blocked skills)
- [x] **AC-US2-02**: Given search results include Postgres data, when blocklist enrichment runs, then all 3 blocklist queries execute as before (getBlockedSkillNames, searchBlocklistEntries, searchRejectedSubmissions)
- [x] **AC-US2-03**: Given edge-only results, when blocklist enrichment runs, then `searchBlocklistEntries` and `searchRejectedSubmissions` still execute to surface blocked/rejected entries in results

---

## Implementation

**Increment**: [0494-search-performance-optimization](../../../../../increments/0494-search-performance-optimization/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: Skip getBlockedSkillNames when source is edge-only
