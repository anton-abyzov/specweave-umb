---
id: US-002
feature: FS-507
title: "SHA-Based Change Detection (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill user."
project: vskill
---

# US-002: SHA-Based Change Detection (P1)

**Feature**: [FS-507](./FEATURE.md)

**As a** vskill user
**I want** update to compare SHA hashes before overwriting skill files
**So that** unchanged skills are skipped efficiently and I see clear before/after output

---

## Acceptance Criteria

- [x] **AC-US2-01**: SHA-256 hash (truncated to 12 chars) of fetched content is compared against `entry.sha` in lockfile
- [x] **AC-US2-02**: When SHA matches, skill is skipped with `dim` "already up to date" message
- [x] **AC-US2-03**: When SHA differs, the old SHA and new SHA are printed in the format `name: oldsha -> newsha`
- [x] **AC-US2-04**: Lockfile `sha` field is updated after successful write for all source types

---

## Implementation

**Increment**: [0507-vskill-update-all-sources](../../../../../increments/0507-vskill-update-all-sources/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-003**: Write failing tests for source-fetcher.ts
- [x] **T-004**: Implement src/updater/source-fetcher.ts to pass tests
- [x] **T-005**: Add new test cases to src/commands/update.test.ts
- [x] **T-006**: Modify src/commands/update.ts to use parseSource + fetchFromSource
