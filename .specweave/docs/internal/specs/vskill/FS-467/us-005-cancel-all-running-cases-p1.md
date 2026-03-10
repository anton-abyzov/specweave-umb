---
id: US-005
feature: FS-467
title: Cancel All Running Cases (P1)
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 57
    url: https://github.com/anton-abyzov/vskill/issues/57
---

# US-005: Cancel All Running Cases (P1)

**Feature**: [FS-467](./FEATURE.md)

**As a** skill developer
**I want** a "Cancel All" action that aborts every in-flight case at once
**So that** I can quickly stop a bulk run without clicking cancel on each case individually

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given multiple cases in "running" or "queued" state, when I click "Cancel All", then all running cases' AbortControllers are aborted and all queued cases are removed from the queue
- [ ] **AC-US5-02**: Given a "Cancel All" action, then every affected case transitions to "cancelled" state and no further SSE events are processed for those cases
- [ ] **AC-US5-03**: Given a "Cancel All" during a bulk run, then server-side semaphore slots are properly released for all cancelled cases (no resource leaks)

---

## Implementation

**Increment**: [0467-parallel-per-case-benchmark](../../../../../increments/0467-parallel-per-case-benchmark/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-011**: Implement `cancelAll()` — abort all running/queued cases and release semaphore slots
