# Tasks: Enforce SKILL.md validation for internal/crawler submissions

### T-001: Add skillMdVerified flag to enqueue-submissions endpoint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given a POST to /api/v1/internal/enqueue-submissions with items missing skillMdVerified -> When the endpoint processes them -> Then those items are filtered out. Given items with skillMdVerified: true -> Then they are enqueued normally. Response includes skippedNoSkillMd count.

**Files**: `src/app/api/v1/internal/enqueue-submissions/route.ts`

---

### T-002: Update queue-processor to send skillMdVerified flag
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given the queue-processor validates SKILL.md exists for an item -> When it adds the item to validItems -> Then the item includes `skillMdVerified: true`

**Files**: `crawl-worker/sources/queue-processor.js`
