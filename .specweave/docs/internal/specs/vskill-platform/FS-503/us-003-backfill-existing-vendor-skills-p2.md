---
id: US-003
feature: FS-503
title: "Backfill existing vendor skills (P2)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-003: Backfill existing vendor skills (P2)

**Feature**: [FS-503](./FEATURE.md)

**As a** platform operator
**I want** all existing vendor skills that were published with incorrect VERIFIED status to be updated to CERTIFIED/T4
**So that** `vskill find` displays accurate certification status for all vendor skills

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given existing skills in the DB with `author` matching a vendor org and `certTier = "VERIFIED"`, when the admin backfill endpoint is invoked, then those skills are updated to `certTier = "CERTIFIED"`, `certMethod = "VENDOR_AUTO"`, `trustTier = "T4"`, `trustScore = 100`
- [x] **AC-US3-02**: Given the backfill runs, when a vendor skill already has `certTier = "CERTIFIED"`, then it is skipped (idempotent)

---

## Implementation

**Increment**: [0503-vendor-auto-certification-fix](../../../../../increments/0503-vendor-auto-certification-fix/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-004**: Create admin backfill-vendor-cert endpoint
