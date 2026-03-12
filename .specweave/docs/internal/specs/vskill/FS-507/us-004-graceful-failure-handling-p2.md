---
id: US-004
feature: FS-507
title: "Graceful Failure Handling (P2)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** vskill user."
project: vskill
---

# US-004: Graceful Failure Handling (P2)

**Feature**: [FS-507](./FEATURE.md)

**As a** vskill user
**I want** partial update failures to not block successful updates
**So that** a single network error does not prevent other skills from updating

---

## Acceptance Criteria

- [x] **AC-US4-01**: When a source fetch fails (network error, 404, rate limit), a yellow warning is printed with the skill name and error message
- [x] **AC-US4-02**: The update loop continues to the next skill after a failure
- [x] **AC-US4-03**: The lockfile is written once after the loop with all successful updates applied
- [x] **AC-US4-04**: `GITHUB_TOKEN` from environment is propagated to GitHub API calls (branch detection, marketplace.json fetch) to reduce rate limiting
- [x] **AC-US4-05**: The final summary reports count of updated skills and lists any that failed

---

## Implementation

**Increment**: [0507-vskill-update-all-sources](../../../../../increments/0507-vskill-update-all-sources/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
