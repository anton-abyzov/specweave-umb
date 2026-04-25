# Tasks: Studio search API extension + same-origin proxy + telemetry endpoints

Project: vskill-platform | Test mode: TDD (strict) | Coverage target: 90%

---

## US-001: `publisher` field + `offset/total` pagination on `/api/v1/skills/search`

### T-001: [RED] Failing tests — publisher join, null safety, offset/total, clamp header
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- Given a seeded skill whose Submission has a publisherId pointing to a verified Publisher
- When `GET /api/v1/skills/search?q=<name>&limit=20&offset=0` is called
- Then the response includes `results[0].publisher = { slug, name, verified: true }` AND envelope includes `total: <int>` AND `offset: 0`
- Given a seeded skill whose Submission.publisherId is null
- When the same query runs
- Then `results[0].publisher` is `null` (no 500)
- Given `?limit=99`
- When the request runs
- Then response sets `X-Limit-Clamped: 30` header and returns at most 30 results
- Tests live in `vskill-platform/src/app/api/v1/skills/search/route.test.ts` (extending existing suite); they MUST fail RED before implementation

---

### T-002: [GREEN] Implement publisher join + offset/total + clamp header
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- Given the RED tests from T-001
- When the search-result builder includes Publisher via Prisma `include`, the route accepts and clamps `offset`, computes `total` via parallel `count()`, and clamps `limit` with the response header
- Then T-001 tests turn green
- Re-run all pre-existing route.test.ts cases — must remain green (BWC)

**Implementation notes**:
- Extend `src/lib/search.ts::searchSkills` (or equivalent enrichment function) with a left-join on Submission→Publisher; map to `{ slug, name, verified } | null`
- In `src/app/api/v1/skills/search/route.ts`: parse `offset` (default 0), launch `db.skill.count({ where })` in parallel with the existing search query (`Promise.all`), include both in the envelope
- Clamp `limit` at 30 with `X-Limit-Clamped: 30` header set when input exceeded

---

### T-003: [REFACTOR] Server-Timing publisher segment + 50ms soft-timeout degrade path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed

**Test Plan**:
- Given the green implementation from T-002
- When the publisher join is wrapped with a 50ms soft timeout (resolves to null on miss)
- Then `Server-Timing: enrichment;desc=publisher;dur=<ms>` is present on every response
- Given an injected slow Publisher query (mock returns after 100ms)
- When the search completes
- Then response returns `publisher: null` for all results AND `publisher_join_degraded` is logged AND search itself returns successfully
- Test in `route.test.ts` using a Prisma mock that delays the publisher fetch

---

### T-004: [VERIFY] Backward-compat regression — `vskill find` integration tests pass unchanged
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- Given the green implementation from T-002 + T-003 deployed to the local dev Worker
- When existing `vskill find` integration tests in `repositories/anton-abyzov/vskill/` run against the new response
- Then all assertions pass without code change in `vskill/src/api/client.ts` or `vskill/src/commands/find.ts`
- Add this as a CI gate in vskill-platform's pipeline (cross-repo integration step, or a contract test that re-imports the parsing code)

---

## US-002: Same-origin `/api/v1/studio/search` proxy

### T-005: [RED] Failing tests — LRU cache, RL, AbortController, 502 sanitize, ETag/304
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-08 | **Status**: [x] completed

**Test Plan**:
- Given the proxy route does not exist yet
- When `GET /api/v1/studio/search?q=react&limit=20&offset=0` is issued (upstream mocked via MSW)
- Then upstream is called once; second identical request within 60s does not call upstream and returns from cache
- Given the client sends `If-None-Match: <etag from prior response>`
- When the proxy serves the cache hit
- Then the response is `304 Not Modified` with empty body
- Given 61 requests fired within 60s from the same IP, cache cold
- When the 61st arrives
- Then it returns `429` with `Retry-After: 60`; cache hits in the same window do NOT count
- Given the client aborts mid-flight
- When the proxy is in-flight to upstream
- Then upstream's `AbortSignal` receives an abort event (verify via mock spy)
- Given upstream returns 503
- When the proxy receives it
- Then the proxy returns `502 { error: "search_unavailable" }` and the upstream URL is NOT in the response body
- Given `?limit=99&offset=10000`
- When parsed
- Then `limit` is clamped to 30, `offset` is clamped to 5000

Tests in `src/app/api/v1/studio/search/route.test.ts` (new file). MUST fail RED.

---

### T-006: [GREEN] Implement proxy + LRU + token-bucket + AbortController + ETag
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-08 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-005
- When the route handler is implemented per the plan.md handler outline
- Then T-005 turns green AND `X-Cache: HIT|MISS` debug header is set for observability

**Implementation notes**:
- New files per plan.md: `src/lib/studio/lru.ts`, `src/lib/studio/rate-limit.ts`, `src/lib/studio/etag.ts`, `src/app/api/v1/studio/search/route.ts`
- Use `cf-connecting-ip` for IP, fallback to `req.socket.remoteAddress`
- ETag = SHA-256 of canonical-JSON of body, base64url-truncated to 16 chars

---

### T-007: [REFACTOR] Extract LRU + token-bucket utilities for telemetry reuse
**User Story**: US-002 (also US-003) | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed

**Test Plan**:
- Given LRU and rate-limit are extracted to `src/lib/studio/`
- When the same modules are imported by both `studio/search/route.ts` and `studio/telemetry/[kind]/route.ts`
- Then the unit tests for both modules pass and the integration tests for both routes use independent bucket maps (no cross-talk)
- Given a perf-smoke shell loop of 20 cache-hit requests
- When measured locally with `curl -w '%{time_total}'`
- Then p50<5ms p95<15ms (AC-US2-07; smoke only — production smoke is part of T-010)

---

## US-003: Studio telemetry endpoints

### T-008: [RED] Failing tests — Zod validation, RL, 204-on-DB-fail, no-PII guard
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-05, AC-US3-06, AC-US3-07 | **Status**: [x] completed

**Test Plan**:
- Given the telemetry route does not exist yet
- When `POST /api/v1/studio/telemetry/submit-click` with `{ repoUrl: "https://github.com/x/y", ts: <int> }` is called
- Then response is 204 and a row exists in `StudioTelemetry` with `kind="submit-click"`
- Given `POST /api/v1/studio/telemetry/install-copy` with `{ skillName: "foo", ts: <int> }`
- Then 204 with `kind="install-copy"`
- Given an invalid payload (missing `ts`, oversized `q`, non-URL `repoUrl`)
- Then 400 with `{ error: "invalid_payload", issues: [...] }`
- Given 11 telemetry requests in 60s from same IP
- Then 11th returns 429 with Retry-After
- Given the DB write throws
- Then 204 is returned anyway AND a `telemetry_db_failed` log entry is recorded
- **Static check**: a Vitest test that reads the route source file and asserts no occurrence of `x-forwarded-for`, `user-agent`, or `req.headers` outside the IP-extraction helper (PII guard)

Tests in `src/app/api/v1/studio/telemetry/route.test.ts`. MUST fail RED.

---

### T-009: [GREEN] Implement telemetry routes + StudioTelemetry Prisma migration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07 | **Status**: [x] completed

**Test Plan**:
- Given the RED suite from T-008
- When the dynamic `[kind]` route handler is implemented + Prisma migration applied
- Then T-008 turns green

**Implementation notes**:
- Prisma migration `add_studio_telemetry` with the model from plan.md §3
- Reuse `src/lib/studio/rate-limit.ts` with a separate bucket map (10/min bucket capacity)
- `kind` param validated via switch; unknown kinds return 404

---

### T-010: [INTEGRATION] Contract doc + perf smoke + Playwright roundtrip + sibling unblock
**User Story**: US-001 + US-002 + US-003 | **Satisfies ACs**: AC-US1-05, AC-US2-07, FR-001 | **Status**: [x] completed

**Test Plan**:
- Given all unit + integration tests are green
- When a Playwright spec issues a sequence of {studio search → install-copy telemetry → submit-click telemetry} against the running dev Worker
- Then all roundtrip assertions pass and DB rows are created for telemetry
- Given the dev Worker is up
- When a shell smoke loop fires 20 sequential cache-hit + 20 cache-miss requests
- Then p50/p95 budgets are met (AC-US2-07) — record results in `reports/perf-smoke-0716.md`
- Given the contract document is published at `.specweave/docs/contracts/studio-search-api-v1.md`
- When linked from this increment's spec.md and from sibling increments 0717/0718 spec.md
- Then siblings can replace their MSW mocks with the live response shape from the contract

**Deliverables**:
- `.specweave/docs/contracts/studio-search-api-v1.md` (response envelope, ETag/cache headers, telemetry payload schemas)
- `reports/perf-smoke-0716.md` (numbers measured against deployed dev Worker)
- Playwright spec `vskill-platform/tests/e2e/studio-search-and-telemetry.spec.ts`

---

## Task summary

| Task | US | TDD phase | Effort |
|---|---|---|---|
| T-001 | US-001 | RED | S |
| T-002 | US-001 | GREEN | M |
| T-003 | US-001 | REFACTOR | S |
| T-004 | US-001 | VERIFY (BWC) | S |
| T-005 | US-002 | RED | M |
| T-006 | US-002 | GREEN | L |
| T-007 | US-002 | REFACTOR | S |
| T-008 | US-003 | RED | M |
| T-009 | US-003 | GREEN | M |
| T-010 | All   | INTEGRATION | M |

Sequencing: T-001..T-004 can run before/in-parallel-with T-005..T-007 (different code paths). T-008..T-009 depends on T-007 (extracted RL module). T-010 depends on all others.
