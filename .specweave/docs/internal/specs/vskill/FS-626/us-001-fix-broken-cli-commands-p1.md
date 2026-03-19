---
id: US-001
feature: FS-626
title: Fix Broken CLI Commands (P1)
status: completed
priority: P1
created: 2026-03-19T00:00:00.000Z
tldr: "**As a** developer using the appstore skill."
project: vskill
external_tools:
  jira:
    key: SWE2E-737
  ado:
    id: 1576
---

# US-001: Fix Broken CLI Commands (P1)

**Feature**: [FS-626](./FEATURE.md)

**As a** developer using the appstore skill
**I want** correct `asc` CLI commands and flags
**So that** the generated commands actually work

---

## Acceptance Criteria

- [x] **AC-US1-01**: All `--app-id` flags replaced with `--app`
- [x] **AC-US1-02**: All `--build-id` flags replaced with `--build`
- [x] **AC-US1-03**: All `--file` flags in upload contexts replaced with `--ipa`
- [x] **AC-US1-04**: `asc apps` replaced with `asc apps list`
- [x] **AC-US1-05**: `--workflow-name` replaced with `--workflow-id` for Xcode Cloud
- [x] **AC-US1-06**: Install commands fixed: `brew install asc` (no tap), install script URL `https://asccli.sh/install`
- [x] **AC-US1-07**: Troubleshooting section install command fixed

---

## Implementation

**Increment**: [0626-fix-appstore-skill-md](../../../../../increments/0626-fix-appstore-skill-md/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
