---
id: US-006
feature: FS-396
title: "Scheduler Integration and VM Deployment (P2)"
status: completed
priority: P1
created: 2026-03-02T00:00:00.000Z
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-006: Scheduler Integration and VM Deployment (P2)

**Feature**: [FS-396](./FEATURE.md)

**As a** platform operator
**I want** the sast-scanner source registered in the scheduler with appropriate timeout/cooldown and deployed to VM-2
**So that** SAST scans are continuously pulled and processed

---

## Acceptance Criteria

- [x] **AC-US6-01**: `scheduler.js` SOURCE_TIMEOUTS includes `"sast-scanner": 30 * 60 * 1000` (30 min timeout -- scans are quick, each cycle dispatches to scanner-worker which handles the actual work)
- [x] **AC-US6-02**: `scheduler.js` SOURCE_COOLDOWNS includes `"sast-scanner": 30 * 1000` (30s cooldown -- check for new work frequently but not aggressively)
- [x] **AC-US6-03**: `.env.vm2` has `sast-scanner` appended to ASSIGNED_SOURCES
- [x] **AC-US6-04**: The callbackUrl constructed by sast-scanner.js uses `config.platformUrl` (defaults to `https://verified-skill.com`) so webhook results route back to the platform

---

## Implementation

**Increment**: [0396-pull-based-sast-scanner](../../../../../increments/0396-pull-based-sast-scanner/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
