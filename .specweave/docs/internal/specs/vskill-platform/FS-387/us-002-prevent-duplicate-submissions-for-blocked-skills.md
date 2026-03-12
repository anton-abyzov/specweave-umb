---
id: US-002
feature: FS-387
title: "Prevent duplicate submissions for blocked skills"
status: completed
priority: P1
created: "2026-02-27T00:00:00.000Z"
tldr: "**As a** platform operator."
project: vskill-platform
---

# US-002: Prevent duplicate submissions for blocked skills

**Feature**: [FS-387](./FEATURE.md)

**As a** platform operator
**I want** the submission endpoint to reject new submissions for skills that are already BLOCKED
**So that** blocked repos do not accumulate duplicate submission records

---

## Acceptance Criteria

- [x] **AC-US2-01**: `checkSubmissionDedup` returns `kind: "blocked"` when the most recent submission is in BLOCKED state
- [x] **AC-US2-02**: POST `/api/v1/submissions` returns HTTP 200 with `{ blocked: true, submissionId }` for blocked skills
- [x] **AC-US2-03**: `checkSubmissionDedupBatch` also returns `kind: "blocked"` for batch submissions
- [x] **AC-US2-04**: Internal/crawler submissions respect blocked dedup via existing `checkSubmissionDedup` call

---

## Implementation

**Increment**: [0387-blocklist-dedup-poisoning-fixes](../../../../../increments/0387-blocklist-dedup-poisoning-fixes/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
