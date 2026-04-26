# Tasks — 0773

### T-001: Search route — drop `id` from OR, AND `reason`, reduce fetchLimit
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-06 | **Status**: [x] completed
**Test**: Given a query `?q=foo&state=rejected&reason=security` → When the route runs → Then `where.OR` has length 2 (skillName, repoUrl), `where.state.in` includes rejected states, `where.AND` (or merged) includes the reason mapping, and `take` equals `min(limit*2, 200)`.

### T-002: Search route — KV cache (read fast-path + non-blocking write)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: Given a cached entry at `submissions:search:foo:active:50:0` → When GET fires with `?q=foo` → Then `findMany` is NOT called and the cached payload is returned. Given a cache miss with `state=published` → When GET fires → Then `SUBMISSIONS_KV.put` is called with the expected key after the response is built. Given `state=active` → When GET fires → Then `put` is NOT called (skip-cache rule).

### T-003: Search route — server-side guard for short terms
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed
**Test**: Given `?q=a` → When GET fires → Then status is 400 with the existing message.

### T-004: SSR data.ts — skip list fetch when `q` present
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given `getQueueInitialDataSSR({q:"foo"})` → When called → Then neither `getQueueSubmissionsSSR` nor `getQueueSubmissionsDirectSSR` is invoked, and the returned object has `submissions: null` and `total: null` so the client knows to fetch.

### T-005: queue/page.tsx — forward `q` to SSR helper
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given a request to `/queue?q=foo` → When the page server-renders → Then `getQueueInitialDataSSR` receives `{q:"foo"}` (verified via mock).

### T-006: QueuePageClient — skip mount fetchQueue when search active; gate debounce on mount
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given the queue mounts with `searchQuery="foo"` from URL → When mount effects run → Then `fetchQueue` is NOT called on mount, and `doSearch` runs exactly once (not twice from debounce + filter effect).

### T-007: SubmissionTable — add `data-row-id` to row element
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given a rendered table with row `id="abc"` → When inspected → Then the row's outermost element has `data-row-id="abc"`.

### T-008: QueuePageClient — parse `?highlight=`, seed flashRef, scrollIntoView
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given `/queue?highlight=abc` and a submissions list containing `abc` → When the table renders → Then `flashRef.current.has("abc")` becomes true and the row's `scrollIntoView` is called once with `{behavior:"smooth", block:"center"}`.

### T-009: QueuePageClient — strip `?highlight=` from URL after first paint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given `/queue?highlight=abc&filter=active` → When the highlight effect fires → Then `router.replace` is called with a URL that no longer contains `highlight`, but preserves `filter=active`.

### T-010: QueuePageClient — fallback refetch with `filter=all` when ID not on page
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given `/queue?highlight=zzz` and submissions list does NOT contain `zzz` → When the highlight effect fires → Then exactly one `fetchQueue({filter:"all"})` is dispatched, and a second resolution flash + scroll attempt runs against the new list.

### T-011: QueuePageClient — cap highlight IDs to 50
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x] completed
**Test**: Given `?highlight=` with 100 comma-separated IDs → When parsed → Then the resulting array length is 50.

### T-012: submit/page.tsx — View Queue href includes filter + highlight
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given `results = [{id:"a"}, {id:"b"}, {error:"x"}, {status:"skipped"}]` → When rendered in `phase=done` → Then the View Queue link's href is `/queue?filter=active&highlight=a,b`. Given `results` with no IDs → When rendered → Then the View Queue button is hidden (existing `okCount > 0` guard).

### T-013: Verify with full vitest run
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test**: Given all task changes landed → When `npx vitest run` is executed in the vskill-platform repo → Then all tests pass with no regressions.

### T-014: Manual smoke via local studio + screenshot proof
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-02, AC-US2-01 | **Status**: [x] completed (verification deferred to post-deploy production smoke per user directive)
**Test**: Given local dev server (`npm run dev`) → When user submits a skill and clicks View Queue → Then the row scrolls into view + flashes. When user types `?q=hello-skill` twice in 60s → Then the second response is served from KV (verified via response timing or an added `x-cache-hit` header in dev).
