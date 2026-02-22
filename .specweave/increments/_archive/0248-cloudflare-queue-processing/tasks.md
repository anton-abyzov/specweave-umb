# Tasks: Cloudflare Queue Admin Dashboard Completion

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

---

### T-001: Write spec.md and update increment metadata
**User Story**: ALL | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given spec.md is a template → When written → Then ACs are defined and spec is valid

---

### T-002: Extend status endpoint with paused flag and stuckList
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-05, AC-US2-05 | **Status**: [x] completed
**Test**: Given queue:paused is set in KV → When GET /api/v1/admin/queue/status → Then paused=true and stuckList contains stuck submissions

**Files**: `src/app/api/v1/admin/queue/status/route.ts`

---

### T-003: Add queue pause endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given SUPER_ADMIN token → When POST /api/v1/admin/queue/pause → Then queue:paused is set in KV; When DELETE → Then flag cleared

**Files**: `src/app/api/v1/admin/queue/pause/route.ts` (NEW)

---

### T-004: Add pause check to queue consumer
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given queue:paused flag is set → When handleSubmissionQueue called → Then batch.retryAll() called and function returns without processing

**Files**: `src/lib/queue/consumer.ts`

---

### T-005: Add bulk-requeue endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given 3 stuck submissions → When POST /api/v1/admin/queue/bulk-requeue → Then returns {requeued: 3, failed: 0, total: 3}

**Files**: `src/app/api/v1/admin/queue/bulk-requeue/route.ts` (NEW)

---

### T-006: Enhance admin queue page with health badge, stuck panel, pause toggle, bulk requeue
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-03, AC-US3-01 | **Status**: [x] completed
**Test**: Given queue is degraded with 2 stuck submissions → When admin opens queue page → Then health badge shows DEGRADED and stuck panel lists both submissions

**Files**: `src/app/admin/queue/page.tsx`

---

### T-007: Write unit tests for pause and bulk-requeue endpoints
**User Story**: US-002, US-003 | **Satisfies ACs**: ALL | **Status**: [x] completed
**Test**: Given mocked KV and auth → When pause/bulk-requeue routes called → Then correct KV operations performed and responses returned

**Files**:
- `src/app/api/v1/admin/queue/pause/route.test.ts` (NEW)
- `src/app/api/v1/admin/queue/bulk-requeue/route.test.ts` (NEW)
