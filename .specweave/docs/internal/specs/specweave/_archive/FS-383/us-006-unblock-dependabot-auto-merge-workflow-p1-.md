---
id: US-006
feature: FS-383
title: "Unblock Dependabot auto-merge workflow (P1)"
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
tldr: "**As a** maintainer relying on automated dependency updates
**I want** the Dependabot auto-merge workflow to successfully approve and merge PRs
**So that** dependency updates are processed without manual intervention."
project: specweave
---

# US-006: Unblock Dependabot auto-merge workflow (P1)

**Feature**: [FS-383](./FEATURE.md)

**As a** maintainer relying on automated dependency updates
**I want** the Dependabot auto-merge workflow to successfully approve and merge PRs
**So that** dependency updates are processed without manual intervention

---

## Acceptance Criteria

- [x] **AC-US6-01**: `dependabot-auto-merge.yml` documents that the repo setting "Allow GitHub Actions to create and approve pull requests" must be enabled
- [x] **AC-US6-02**: The workflow uses the correct token/permissions approach for PR approval
- [x] **AC-US6-03**: Workflow comments explain the required repo setting for future maintainers

---

## Implementation

**Increment**: [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
