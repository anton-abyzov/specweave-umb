---
id: US-001
feature: FS-338
title: Smart Placement
status: not-started
priority: P1
created: 2026-02-23
project: vskill-platform
---
# US-001: Smart Placement

**Feature**: [FS-338](./FEATURE.md)

platform operator
**I want** Cloudflare Smart Placement enabled globally
**So that** Workers run in datacenters closest to the Neon database, reducing network latency on every DB call

---

## Acceptance Criteria

- [ ] **AC-US1-01**: `wrangler.jsonc` includes `"placement": { "mode": "smart" }` at the top level
- [ ] **AC-US1-02**: Deployment succeeds with Smart Placement enabled (no wrangler errors)

---

## Implementation

**Increment**: [0338-api-perf-optimization](../../../../../increments/0338-api-perf-optimization/spec.md)

