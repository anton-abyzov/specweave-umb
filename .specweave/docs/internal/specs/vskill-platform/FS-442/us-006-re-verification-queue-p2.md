---
id: US-006
feature: FS-442
title: "Re-Verification Queue (P2)"
status: completed
priority: P1
created: "2026-03-06T00:00:00.000Z"
tldr: "**As a** platform admin."
project: vskill-platform
external:
  github:
    issue: 27
    url: "https://github.com/anton-abyzov/vskill-platform/issues/27"
---

# US-006: Re-Verification Queue (P2)

**Feature**: [FS-442](./FEATURE.md)

**As a** platform admin
**I want** a `/api/v1/admin/eval/reverify` endpoint that enqueues all published skills for re-evaluation with V2 methodology
**So that** I can batch-validate the entire skill catalog under the new grading system

---

## Acceptance Criteria

- [x] **AC-US6-01**: Given a POST to `/api/v1/admin/eval/reverify`, when authenticated as SUPER_ADMIN or internal, then all non-deprecated published skills are enqueued to `EVAL_QUEUE` with `trigger: "REVERIFY"` and `methodologyVersion: 2`
- [x] **AC-US6-02**: The existing `EVAL_QUEUE` is reused -- no new queue is created
- [x] **AC-US6-03**: The `EvalTrigger` Prisma enum is extended with a `REVERIFY` value
- [x] **AC-US6-04**: Given a reverify run, when processing, then the eval consumer uses N=5 runs per test case
- [x] **AC-US6-05**: No auto-deprecation occurs -- skills with DEGRADING verdicts are flagged but remain published; admins decide next steps
- [x] **AC-US6-06**: The endpoint returns `{ queued: number, totalSkills: number }` response confirming enqueue count

---

## Implementation

**Increment**: [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-012**: Extend eval-consumer.ts and eval-types.ts for REVERIFY trigger
- [x] **T-013**: Implement POST /api/v1/admin/eval/reverify endpoint
- [x] **T-014**: Update eval-regression.ts cron for V2 support
