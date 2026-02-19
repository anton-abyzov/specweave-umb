---
id: US-002
feature: FS-238
title: "Uninstall SpecWeave from a project (P1)"
status: completed
priority: P1
created: 2026-02-18T00:00:00.000Z
tldr: "**As a** developer
**I want** to run `specweave uninstall` to completely remove SpecWeave from my project
**So that** I can cleanly decommission the framework without manual cleanup."
project: specweave
related_projects: [vskill, specweave, vskill]
---

# US-002: Uninstall SpecWeave from a project (P1)

**Feature**: [FS-238](./FEATURE.md)

**As a** developer
**I want** to run `specweave uninstall` to completely remove SpecWeave from my project
**So that** I can cleanly decommission the framework without manual cleanup

---

## Acceptance Criteria

- [x] **AC-US2-01**: `.specweave/` directory is deleted
- [x] **AC-US2-02**: SW-managed sections stripped from CLAUDE.md (user content preserved)
- [x] **AC-US2-03**: SW-managed sections stripped from AGENTS.md (user content preserved)
- [x] **AC-US2-04**: Files deleted entirely when 100% SW-managed (no user content)
- [x] **AC-US2-05**: SpecWeave git pre-commit hook removed (non-SW hooks untouched)
- [x] **AC-US2-06**: All locally installed skills removed from agent directories
- [x] **AC-US2-07**: `vskill.lock` deleted
- [x] **AC-US2-08**: `--keep-data` archives `.specweave/` to `.specweave-backup-{timestamp}/`
- [x] **AC-US2-09**: `--dry-run` shows removal manifest without deleting anything
- [x] **AC-US2-10**: `--force` skips confirmation prompt
- [x] **AC-US2-11**: `--global` additionally cleans global agent dirs, plugin cache, shell env vars
- [x] **AC-US2-12**: Summary printed after completion with counts

---

## Implementation

**Increment**: [0238-complete-uninstall-support](../../../../../increments/0238-complete-uninstall-support/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
