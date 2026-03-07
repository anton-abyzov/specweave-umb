---
id: US-005
feature: FS-433
title: "Repo Re-Submission for Platform Scanning"
status: completed
priority: P1
created: 2026-03-05
tldr: "**As a** plugin consumer who encounters unregistered plugins."
project: vskill
---

# US-005: Repo Re-Submission for Platform Scanning

**Feature**: [FS-433](./FEATURE.md)

**As a** plugin consumer who encounters unregistered plugins
**I want** the option to trigger a repo re-submission for platform scanning
**So that** the repo author's new plugins get scanned and added to the verified marketplace

---

## Acceptance Criteria

- [x] **AC-US5-01**: Given a user declines `--force` install of an unregistered plugin, when the re-submission prompt appears and the user accepts, then `submitSkill({ repoUrl })` is called and a tracking URL or manual fallback message is printed
- [x] **AC-US5-02**: Given the `submitSkill()` API call fails, when re-submission is attempted, then an error message is printed with the manual submission URL as fallback, and the install flow continues for registered plugins
- [x] **AC-US5-03**: Given `--force` is used, when unregistered plugins are installed, then the re-submission prompt is not shown

---

## Implementation

**Increment**: [0433-marketplace-unregistered-plugin-discovery](../../../../../increments/0433-marketplace-unregistered-plugin-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: offerResubmission() calls submitSkill and handles errors
- [x] **T-011**: --force suppresses re-submission prompt
