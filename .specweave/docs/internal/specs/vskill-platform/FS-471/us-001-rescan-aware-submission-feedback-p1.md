---
id: US-001
feature: FS-471
title: "Rescan-aware submission feedback (P1)"
status: completed
priority: P1
created: "2026-03-10T00:00:00.000Z"
tldr: "**As a** skill author resubmitting a repo with existing verified skills."
project: vskill-platform
external:
  github:
    issue: 44
    url: "https://github.com/anton-abyzov/vskill-platform/issues/44"
---

# US-001: Rescan-aware submission feedback (P1)

**Feature**: [FS-471](./FEATURE.md)

**As a** skill author resubmitting a repo with existing verified skills
**I want** the submit results to distinguish between new submissions and rescans of existing skills
**So that** I understand which skills are being freshly evaluated vs re-evaluated

---

## Acceptance Criteria

- [x] **AC-US1-01**: Given the discovery endpoint returns skills with `status: "verified"`, when the `DiscoveredSkill` interface is used in the frontend, then it includes an optional `status` field of type `"new" | "verified" | "pending" | "rejected"` and preserves the value from the API response
- [x] **AC-US1-02**: Given a mixed submission with N new skills and M verified (rescan) skills, when results are displayed, then the summary line reads "N new, M rescanning" instead of "N+M submitted"; when all are rescans (N=0) it reads "M rescanning"; when all are new (M=0) it reads "N submitted" (existing behavior preserved)
- [x] **AC-US1-03**: Given a skill result where the original discovery status was `"verified"`, when the result row is rendered with a successful submission (has `id`), then it shows a "Rescan >>" link (instead of "Track >>") pointing to `/submit/{id}`
- [x] **AC-US1-04**: Given skills with discovery status `"rejected"` or `"new"`, when counted for the summary line, then both are treated as "new" submissions (no separate category for rejected)

---

## Implementation

**Increment**: [0471-submit-rescan-feedback](../../../../../increments/0471-submit-rescan-feedback/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Extend DiscoveredSkill interface to include status field
- [x] **T-002**: Thread discoveryStatus through SubmissionResult
- [x] **T-003**: Rescan-aware summary line
- [x] **T-004**: Show "Rescan >>" link label for verified skill results
