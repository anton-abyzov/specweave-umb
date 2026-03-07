---
id: US-001
feature: FS-433
title: Discover Unregistered Plugin Directories
status: completed
priority: P1
created: 2026-03-05
tldr: "**As a** plugin consumer."
project: vskill
external:
  github:
    issue: 15
    url: https://github.com/anton-abyzov/vskill/issues/15
---

# US-001: Discover Unregistered Plugin Directories

**Feature**: [FS-433](./FEATURE.md)

**As a** plugin consumer
**I want** the CLI to detect plugin directories not listed in marketplace.json
**So that** I am aware of newly added plugins even before the manifest is updated

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given a marketplace repo with `plugins/` containing directories `frontend`, `backend`, and `marketing`, and marketplace.json listing only `frontend` and `backend`, when `discoverUnregisteredPlugins(owner, repo, manifestContent)` is called, then it returns `["marketing"]`
- [x] **AC-US1-02**: Given the GitHub Contents API returns an error or network failure, when `discoverUnregisteredPlugins()` is called, then it returns `[]` without throwing
- [x] **AC-US1-03**: Given the `plugins/` directory contains both files and directories, when discovery runs, then only directory entries are considered (files are ignored)
- [x] **AC-US1-04**: Given all plugin directories are already listed in marketplace.json, when discovery runs, then it returns `[]`

---

## Implementation

**Increment**: [0433-marketplace-unregistered-plugin-discovery](../../../../../increments/0433-marketplace-unregistered-plugin-discovery/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Implement discoverUnregisteredPlugins() in marketplace.ts
- [x] **T-002**: Export discoverUnregisteredPlugins and UnregisteredPlugin from marketplace/index.ts
