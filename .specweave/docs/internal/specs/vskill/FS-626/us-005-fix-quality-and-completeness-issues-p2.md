---
id: US-005
feature: FS-626
title: Fix Quality and Completeness Issues (P2)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** developer using the appstore skill."
project: vskill
external_tools:
  jira:
    key: SWE2E-741
  ado:
    id: 1580
---

# US-005: Fix Quality and Completeness Issues (P2)

**Feature**: [FS-626](./FEATURE.md)

**As a** developer using the appstore skill
**I want** complete menus, correct namespaces, and proper shell quoting
**So that** the skill is production-quality

---

## Acceptance Criteria

- [x] **AC-US5-01**: Default interactive menu shows all 10 modes (not just 4)
- [x] **AC-US5-02**: Metadata bulk localization uses correct namespace
- [x] **AC-US5-03**: METADATA MODE includes version selection step
- [x] **AC-US5-04**: Submit mode checks for existing draft versions before creating new
- [x] **AC-US5-05**: Phantom related skills removed or replaced with real ones
- [x] **AC-US5-06**: Env var table split into secrets vs config sections
- [x] **AC-US5-07**: All shell variables properly quoted (`"$APP_ID"` not `$APP_ID`)
- [x] **AC-US5-08**: vskill install section added with correct `npx vskill i` command

---

## Implementation

**Increment**: [0626-fix-appstore-skill-md](../../../../../increments/0626-fix-appstore-skill-md/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
