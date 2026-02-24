---
id: US-001
feature: FS-340
title: Smart Placement
status: complete
priority: P1
created: 2026-02-24
project: vskill-platform
---
# US-001: Smart Placement

**Feature**: [FS-340](./FEATURE.md)

platform operator
**I want** Cloudflare Smart Placement enabled globally
**So that** Workers run in datacenters closest to the Neon database, reducing network latency on every DB call

---

## Acceptance Criteria

- [x] **AC-US1-01**: `wrangler.jsonc` includes `"placement": { "mode": "smart" }` at the top level
- [x] **AC-US1-02**: Deployment succeeds with Smart Placement enabled (no wrangler errors)

---

## Implementation

**Increment**: [0340-api-perf-optimization](../../../../../increments/0340-api-perf-optimization/spec.md)

