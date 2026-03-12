---
id: US-002
feature: FS-503
title: "Add vendor org fallback in publishSkill (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-002: Add vendor org fallback in publishSkill (P1)

**Feature**: [FS-503](./FEATURE.md)

**As a** platform operator
**I want** `publishSkill()` to check `isVendorOrg(owner)` as a fallback when `sub.isVendor` is `false`
**So that** vendor skills are correctly certified even if the submission flag was not propagated (defense-in-depth)

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a submission where `sub.isVendor` is `false` but the repo owner is a vendor org (e.g., `anthropics`), when `publishSkill()` runs, then the skill receives CERTIFIED cert tier, VENDOR_AUTO cert method, T4 trust tier, trust score 100, and labels `["vendor", "certified"]`
- [x] **AC-US2-02**: Given a submission where `sub.isVendor` is `false` and the repo owner is NOT a vendor org, when `publishSkill()` runs, then the skill receives VERIFIED cert tier and community labels (no change from current behavior)
- [x] **AC-US2-03**: Given a submission where `sub.isVendor` is `true`, when `publishSkill()` runs, then the existing vendor path is used (no double-checking needed, current behavior preserved)

---

## Implementation

**Increment**: [0503-vendor-auto-certification-fix](../../../../../increments/0503-vendor-auto-certification-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Add isVendorOrg fallback inside publishSkill
