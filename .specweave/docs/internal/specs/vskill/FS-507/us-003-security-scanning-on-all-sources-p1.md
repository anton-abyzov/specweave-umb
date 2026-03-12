---
id: US-003
feature: FS-507
title: "Security Scanning on All Sources (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill user."
project: vskill
---

# US-003: Security Scanning on All Sources (P1)

**Feature**: [FS-507](./FEATURE.md)

**As a** vskill user
**I want** Tier 1 security scanning applied to all fetched content regardless of source type
**So that** malicious content is blocked even from trusted-seeming origins like GitHub or local paths

---

## Acceptance Criteria

- [x] **AC-US3-01**: `runTier1Scan()` is called on every fetched content blob before writing to disk
- [x] **AC-US3-02**: Scan verdict FAIL prevents the skill from being updated (same as current registry behavior)
- [x] **AC-US3-03**: Scan verdict and score are printed for every updated skill
- [x] **AC-US3-04**: `local:*` sources are excluded from scanning since they are skipped entirely

---

## Implementation

**Increment**: [0507-vskill-update-all-sources](../../../../../increments/0507-vskill-update-all-sources/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Write failing tests for source-fetcher.ts
- [x] **T-004**: Implement src/updater/source-fetcher.ts to pass tests
- [x] **T-005**: Add new test cases to src/commands/update.test.ts
- [x] **T-006**: Modify src/commands/update.ts to use parseSource + fetchFromSource
