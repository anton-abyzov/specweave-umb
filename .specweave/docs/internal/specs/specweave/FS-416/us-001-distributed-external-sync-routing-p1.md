---
id: US-001
feature: FS-416
title: "Distributed External Sync Routing (P1)"
status: completed
priority: P1
created: 2026-03-03T00:00:00.000Z
tldr: "**As a** SpecWeave user with an umbrella project containing multiple repos."
project: specweave
---

# US-001: Distributed External Sync Routing (P1)

**Feature**: [FS-416](./FEATURE.md)

**As a** SpecWeave user with an umbrella project containing multiple repos
**I want** GitHub issues, Jira tickets, and ADO work items to route to the correct per-repo target
**So that** each project's increments are tracked in their own external tracker instead of all landing in one repo

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given `umbrella.syncStrategy` is `"distributed"` and an increment's project matches a `childRepos[].name`, when GitHub sync runs, then issues are created using that child repo's `sync.github.owner` and `sync.github.repo`
- [x] **AC-US1-02**: Given `umbrella.syncStrategy` is `"centralized"` or is absent, when sync runs, then all issues route to the global `sync.github` config (current behavior preserved)
- [x] **AC-US1-03**: Given `syncStrategy` is `"distributed"`, when `sync-progress` syncs AC checkboxes, then updates are sent to the correct per-project GitHub repo
- [x] **AC-US1-04**: Given `syncStrategy` is `"distributed"`, when `ExternalIssueAutoCreator` creates a Jira issue, then it uses the matched `childRepos[].sync.jira.projectKey`
- [x] **AC-US1-05**: Given `syncStrategy` is `"distributed"`, when `ExternalIssueAutoCreator` creates an ADO work item, then it uses the matched `childRepos[].sync.ado.project`

---

## Implementation

**Increment**: [0416-umbrella-sync-consolidation](../../../../../increments/0416-umbrella-sync-consolidation/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add ChildRepoSyncConfig types and syncStrategy to UmbrellaConfig
- [x] **T-002**: Create resolveSyncTarget() utility
- [x] **T-003**: Wire LivingDocsSync.syncToGitHub() for distributed mode
- [x] **T-004**: Wire sync-progress GitHub AC sync for distributed mode
- [x] **T-005**: Wire Jira/ADO routing for distributed mode
- [x] **T-009**: Integration tests covering all ACs
- [x] **T-010**: Run consolidation and enable distributed sync in umbrella config
