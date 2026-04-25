# Tasks: Local Studio /studio/find — discovery UI

Project: vskill-platform | Test mode: TDD (strict) | Coverage target: 90%

---

## US-001: As-you-type search with debounce, abort, and client cache

### T-001: [SETUP] MSW handlers + fixture data
**User Story**: US-001 | **Satisfies ACs**: FR-001 | **Status**: [x] completed

**Test Plan**:
- Given MSW handlers + fixture file are added
- When a Vitest run imports the handlers and runs a smoke test against `useStudioSearch`
- Then a query `q=hyperf` returns the 1 fixture result with `total=1`
- Fixture file at `vskill-platform/src/test-fixtures/studio-search.json` covers: verified+certified, verified-only, unknown publisher, blocked, and a 40-result superset for LoadMore tests

---

### T-002: [RED] Failing tests — debounce, abort, LRU, min-length, error preservation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Test Plan**:
- Given the `useStudioSearch` hook does not exist yet
- When user types `r`, `re`, `rea`, `reac`, `react` rapidly within 100ms
- Then exactly one network call is made (debounce 200ms, only the last query fires)
- Given an in-flight request and a new query that supersedes it
- Then the abort signal fires on the older fetch (verified via MSW spy)
- Given a query is cached (LRU hit)
- Then the second identical query within session does not call the network (zero MSW invocations)
- Given query length 0 or 1
- Then no fetch fires at all
- Given a network error
- Then state transitions to 'error' BUT prior `list` is preserved (not cleared)
- Given debounce settles
- Then `state === 'loading'` for at least 100ms before the response arrives (skeleton visibility)

Tests in `vskill-platform/src/app/studio/find/hooks/useStudioSearch.test.ts`. MUST fail RED.

---

### T-003: [GREEN] Implement useStudioSearch hook
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-08 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-002
- When the hook is implemented per plan.md (debounce timer, AbortController, ClientLRU, ETag map, fetch loop)
- Then T-002 tests turn green
- Implementation: `src/app/studio/find/hooks/useStudioSearch.ts` + `src/app/studio/find/lib/client-lru.ts`

---

### T-004: [REFACTOR] Deep-link URL state + ETag/304 reuse
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07, AC-US1-08 | **Status**: [x] completed

**Test Plan**:
- Given the green hook from T-003
- When the URL contains `?q=react&offset=20` and the page mounts
- Then `useStudioSearch` initializes from URL and fetches the right page
- Given the user types
- Then `history.replaceState` is called (NOT pushState) so the back button doesn't replay every keystroke
- Given a 304 response from the server
- Then the cached body is reused without re-parse and `state` returns to 'idle'

---

### T-005: [PERF] Playwright trace — composite as-you-type budget AC-US1-09
**User Story**: US-001 | **Satisfies ACs**: AC-US1-09 | **Status**: [x] completed

**Test Plan**:
- Given the implementation from T-003 + T-004 with MSW handlers
- When a Playwright spec types "hyperf" (5 chars within 50ms each)
- Then time from last keystroke to rendered results is <250ms on cache hit
- Use `page.tracing.start({ screenshots: true })` and assert `responseEnd - lastInputEvent < 250ms`
- Spec at `vskill-platform/tests/e2e/studio-find-perf.spec.ts`

---

## US-002: Result cards with trust, publisher, and threat signals

### T-006: [RED] Failing tests — TrustBadge, PublisherChip, ThreatBanner, StatsRow
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08 | **Status**: [x] completed

**Test Plan**:
- Given component tests for each card sub-component
- When TrustBadge renders with `tier='VERIFIED'` then green; `tier='CERTIFIED'` then gold; `tier=null` then 'Unknown' gray
- When PublisherChip renders with `publisher.verified=true` → checkmark; with `publisher=null` → "Unknown publisher"
- When ThreatBanner renders with `isBlocked=true` → red banner with threatType+severity; AND ResultCard's InstallButton is replaced by a "Do not install" pill
- When StatsRow formats numbers >1000 as `1.2k`
- When ResultCard receives a description >300 chars → CSS line-clamp:2 applied
- When ResultCard tabs through children → focus order: name → publisher chip → install button → next card
- When name/description contain `<script>` strings → rendered as text, not HTML (no XSS)

Tests in `vskill-platform/src/app/studio/find/components/*.test.tsx`. MUST fail RED.

---

### T-007: [GREEN] Implement card sub-components
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-006
- When each component is implemented per plan.md
- Then T-006 tests turn green

**Implementation notes**:
- Reuse existing TailwindCSS utility classes; no new design tokens
- All deep-links use `target="_blank" rel="noopener noreferrer"` (AC-US2-02 / AC-US2-03)
- ARIA labels on every badge + button

---

## US-003: Install action via clipboard copy

### T-008: [RED] Failing tests — clipboard, toast, telemetry, fallback, sanitize
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- Given InstallButton with skill name "foo-bar"
- When clicked
- Then `navigator.clipboard.writeText` is called with `vskill install foo-bar`
- AND a toast with the hint text appears
- AND a POST to `/api/v1/studio/telemetry/install-copy` with `{ skillName: "foo-bar", q, ts }` is made (fire-and-forget — UI doesn't block on response)
- Given skill name with a slash or special char (defensive — shouldn't appear in real responses)
- Then sanitization rejects it and the button is disabled
- Given `navigator.clipboard` is undefined (older browser / insecure context)
- Then a fallback readonly input + "Select all" button is rendered instead
- Given `isBlocked=true`
- Then the button is replaced (not just disabled) by a red "Do not install" pill — clicking it does nothing or shows a warning

Tests in `vskill-platform/src/app/studio/find/components/InstallButton.test.tsx`. MUST fail RED.

---

### T-009: [GREEN] Implement InstallButton + toast wiring
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-008
- When the component is implemented per plan.md (clipboard.writeText, toast, fetch POST, sanitize regex, fallback)
- Then T-008 tests turn green
- Use existing toast/notification system already mounted in Studio root (no new dep)

---

## US-004: LoadMore pagination

### T-010: [RED] Failing tests — append, disable, count line, total drift
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06 | **Status**: [x] completed

**Test Plan**:
- Given a fixture with `total=45`
- When the page loads
- Then 20 cards render and ResultCount shows "Showing 20 of 45 results"
- When LoadMore is clicked once
- Then 40 cards render (offset advanced by 20, results appended) and count shows "Showing 40 of 45"
- When LoadMore is clicked again
- Then 45 cards render and LoadMore becomes disabled with label "All results loaded"
- Given the user edits the search bar
- Then offset resets to 0 and a fresh query fires
- Given `total` drifts down between requests (mock changes total from 45 to 25 after first fetch) and current `offset >= 25`
- Then page auto-resets `offset=0` and refetches

Tests in `vskill-platform/src/app/studio/find/components/LoadMore.test.tsx` + integration test in `FindClient.test.tsx`. MUST fail RED.

---

### T-011: [GREEN] Implement LoadMore + ResultCount + offset reset on edit
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-010
- When LoadMore + ResultCount components are added and FindClient wires offset advancement
- Then T-010 tests turn green
- Append (not rerender) — track via React key stability and a render-count assertion

---

## US-001..004: Page composition + integration

### T-012: [GREEN] Compose FindClient + page.tsx + URL params
**User Story**: US-001 + US-004 | **Satisfies ACs**: AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- Given all hooks and components from T-003/T-007/T-009/T-011
- When `page.tsx` reads `?q&offset` and FindClient orchestrates everything
- Then a Vitest integration test renders the full page with MSW handlers and asserts the golden path: type → wait 200ms → results → LoadMore → install copy
- File: `vskill-platform/src/app/studio/find/FindClient.test.tsx`

---

### T-013: [INTEGRATION] Playwright golden path + blocked-skill flow + clipboard assertion
**User Story**: US-001 + US-002 + US-003 + US-004 | **Satisfies ACs**: AC-US1-09, AC-US3-01, AC-US2-04 | **Status**: [x] completed

**Test Plan**:
- Given the dev Worker is running with MSW handlers (or live 0716 endpoints once available)
- When Playwright runs the golden path: visit `/studio/find` → type "hyperf" → see 1 card → tab to install → press Enter → assert clipboard contains "vskill install hyperf"
- AND the blocked-skill flow: query that returns a blocked result → assert ThreatBanner is visible AND no clipboard write occurs on click → "Do not install" pill is interactive
- AND the LoadMore flow: query returning >20 results → click LoadMore → assert 40 cards
- File: `vskill-platform/tests/e2e/studio-find.spec.ts`

---

### T-014: [REFACTOR + LIVE] Switch from MSW to live 0716 endpoints (gated by 0716 deploy)
**User Story**: US-001..004 | **Satisfies ACs**: All | **Status**: [x] completed

**Test Plan**:
- Given sibling 0716 has deployed `/api/v1/studio/search` and the telemetry endpoints to the dev Worker
- When the MSW gate is flipped off (`STUDIO_USE_MOCKS=false` env)
- Then the same Playwright spec from T-013 passes against live endpoints
- Smoke: telemetry rows appear in `StudioTelemetry` table after a click sequence
- Document any contract drift in `reports/contract-drift-0717.md` (expected: zero — siblings share the contract doc)

---

## Task summary

| Task | US | TDD phase | Effort |
|---|---|---|---|
| T-001 | US-001 | SETUP | S |
| T-002 | US-001 | RED | M |
| T-003 | US-001 | GREEN | L |
| T-004 | US-001 | REFACTOR | M |
| T-005 | US-001 | PERF | S |
| T-006 | US-002 | RED | M |
| T-007 | US-002 | GREEN | L |
| T-008 | US-003 | RED | M |
| T-009 | US-003 | GREEN | M |
| T-010 | US-004 | RED | M |
| T-011 | US-004 | GREEN | M |
| T-012 | US-001+004 | GREEN (compose) | M |
| T-013 | All | E2E | M |
| T-014 | All | LIVE switch | S |

Sequencing: T-001 first (mock harness unblocks all). T-002→T-003→T-004→T-005 sequential per RED→GREEN→REFACTOR. T-006→T-007 and T-008→T-009 and T-010→T-011 can run in parallel with the US-001 chain. T-012 needs T-003+T-007+T-009+T-011. T-013 needs T-012. T-014 gated on sibling 0716 deploy.
