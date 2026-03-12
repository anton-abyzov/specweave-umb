---
id: US-001
feature: FS-516
title: "File-system-only install (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** developer installing vskill plugins."
project: vskill
---

# US-001: File-system-only install (P1)

**Feature**: [FS-516](./FEATURE.md)

**As a** developer installing vskill plugins
**I want** plugin install to always use file-system copy
**So that** install never fails due to stale Claude Code native plugin caches

---

## Acceptance Criteria

- [x] **AC-US1-01**: `vskill install` never calls `claude plugin marketplace add` or `claude plugin install`
- [x] **AC-US1-02**: `vskill install` never calls `claude plugin marketplace remove` or `claude plugin uninstall`
- [x] **AC-US1-03**: All agents including Claude Code receive skill files via extraction (file copy)
- [x] **AC-US1-04**: `src/utils/claude-cli.ts` is deleted; no import of it remains in `add.ts`
- [x] **AC-US1-05**: `npm run build` succeeds with no TypeScript errors

---

## Implementation

**Increment**: [0516-remove-native-plugin-install](../../../../../increments/0516-remove-native-plugin-install/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: GREEN — Remove all native install code from add.ts and add.test.ts
