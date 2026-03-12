---
id: US-004
feature: FS-387
title: "Auto-block on critical scan violations"
status: completed
priority: P1
created: "2026-02-27T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-004: Auto-block on critical scan violations

**Feature**: [FS-387](./FEATURE.md)

**As a** platform operator
**I want** skills with critical-severity scan violations (command injection, credential theft, privilege escalation) to be immediately BLOCKED after scan
**So that** dangerous skills don't sit as TIER1_FAILED waiting for manual review or a second failure

---

## Acceptance Criteria

- [x] **AC-US4-01**: When Tier 1 scan finds any `critical`-severity pattern match, submission state transitions to BLOCKED (not TIER1_FAILED)
- [x] **AC-US4-02**: A scoped blocklist entry is auto-created for the skillName + repoUrl on critical block
- [x] **AC-US4-03**: The BLOCKED reason includes which critical patterns were found (e.g., "Immediate block: critical violations CI-001, CT-003")
- [x] **AC-US4-04**: Non-critical failures (high/medium/low only) continue to use TIER1_FAILED as before
- [x] **AC-US4-05**: The blocklist entry created uses `discoveredBy: "system:critical-scan"` to distinguish from manual blocks and auto-block threshold

---

## Implementation

**Increment**: [0387-blocklist-dedup-poisoning-fixes](../../../../../increments/0387-blocklist-dedup-poisoning-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
