---
id: US-003
feature: FS-327
title: Fix submit path to use individual submissions endpoint
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-003: Fix submit path to use individual submissions endpoint

**Feature**: [FS-327](./FEATURE.md)

skill author
**I want** skill submission to actually work from the browser
**So that** clicking submit doesn't silently fail

---

## Acceptance Criteria

- [x] **AC-US3-01**: `handleSubmitAll` submits all discovered skills (not just selected) since selection is removed
- [x] **AC-US3-02**: The submission flow uses the legacy individual `POST /api/v1/submissions` endpoint (which accepts user auth cookies) instead of attempting the internal-only `/api/v1/submissions/bulk` endpoint first
- [x] **AC-US3-03**: Each skill submission includes `repoUrl`, `skillName`, and `skillPath` fields
- [x] **AC-US3-04**: The progress bar tracks submission progress across all skills
- [x] **AC-US3-05**: On error during submission, remaining skills still attempt to submit (no early abort)
- [x] **AC-US3-06**: The done phase shows per-skill results: "Already verified" badge, "Already pending" badge, error message, or "Track >>" link

---

## Implementation

**Increment**: [0327-submit-page-discovery-fix](../../../../../increments/0327-submit-page-discovery-fix/spec.md)

