---
id: US-001
feature: FS-283
title: Trust Tier Model
status: active
priority: P1
created: 2026-02-21
project: vskill-platform
---
# US-001: Trust Tier Model

**Feature**: [FS-283](./FEATURE.md)

platform user
**I want** a formal trust tier classification (T0-T4) for every skill
**So that** I can assess the trustworthiness of a skill independently from its extensibility level

---

## Acceptance Criteria

- [x] **AC-US1-01**: The `Skill` model includes a `trustTier` field with values: T0 (blocked), T1 (unscanned), T2 (scanned -- passed tier1), T3 (verified -- passed tier1 + tier2 LLM judge), T4 (certified -- passed all tiers + human review + provenance verified)
- [x] **AC-US1-02**: The `trustScore` field (0-100) is computed from: tier1 scan result (30%), tier2 LLM score (30%), provenance verification (20%), community signals (20% -- age, reports, installs)
- [ ] **AC-US1-03**: Trust tier is recomputed when any input changes: new scan result, blocklist status change, provenance check result, or security report resolution
- [x] **AC-US1-04**: The `/api/v1/skills/:name` endpoint includes `trustTier` and `trustScore` in the response
- [x] **AC-US1-05**: Skills on the blocklist are automatically set to T0 regardless of scan results

---

## Implementation

**Increment**: [0283-skill-trust-security-scanning](../../../../../increments/0283-skill-trust-security-scanning/spec.md)

