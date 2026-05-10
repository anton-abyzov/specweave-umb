---
increment: 0838-sse-diagnose-source-origin-updates
title: 'Tasks: SSE diagnose mode + source-origin update tracking'
type: tasks
---

# Tasks

### T-001: Wire `VSKILL_DEBUG_SSE` flag + `?debugSse=1` query in `useSkillUpdates`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given `VSKILL_DEBUG_SSE` is unset and the EventSource opens, When the hook runs, Then no `[sse]` console output is emitted; Given `VSKILL_DEBUG_SSE=1` (or `?debugSse=1`) is set and the EventSource emits open/error/message/gone/reconnect/fallback events, When the hook runs, Then each event produces exactly one `console.debug("[sse] ...")` line with ISO timestamp and the event payload.

### T-002: Structured proxy logging in `eval-server/platform-proxy.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given a `text/event-stream` request hits the proxy with `process.env.VSKILL_DEBUG_SSE === "1"`, When the request is dispatched and completes, Then `console.log` emits `proxy.sse.start{requestId, upstreamUrl}` followed by `proxy.sse.end{requestId, status, durationMs}` with matching `requestId`s, AND the response carries an `X-Request-Id` header equal to the same `requestId`; Given the flag is unset, When a `text/event-stream` request flows through, Then no per-request logs are emitted (existing summary-only behavior preserved).

### T-003: Bell tooltip status text + `aria-describedby` wiring in `UpdateBell`
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-04, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given the hook returns `status === "connected"`, When `UpdateBell` renders, Then a hidden `data-testid="update-bell-status-text"` span contains `Live updates: connected` and the bell button has `aria-describedby` pointing to it; Given `status` flips to `fallback`, When the next render commits, Then the text updates to `Live updates: reconnecting` and (after 500ms debounce) an `aria-live="polite"` announcement fires; Given `usePlatformHealth().degraded === true`, When `status === "fallback"` simultaneously, Then the platform-degraded tooltip text takes precedence over the live-updates text.

### T-004: Status pip rendering + color tokens in `UpdateBell`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given `status === "connected"` and there is at least one tracked skill, When `UpdateBell` renders, Then a `data-testid="update-bell-status-pip"` element exists at the bottom-right of the icon with `background: var(--status-success-text)`; Given `status === "fallback"`, Then the pip uses `var(--color-own)`; Given `status === "connecting"`, Then the pip uses `var(--text-secondary)`; Given there are zero installed and zero tracked source-origin skills, When the bell renders, Then the pip element is absent from the DOM.

### T-005: New `toastQueue.ts` module — localStorage-backed FIFO with TTL
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given an empty queue, When `enqueue(entry)` is called 11 times, Then the queue contains 10 entries and the oldest was dropped (FIFO eviction); Given an entry is enqueued at `t=0`, When `drain()` is called at `t=30min + 1ms`, Then that entry is dropped silently and not returned; Given `typeof window === "undefined"`, When `enqueue` is called, Then it returns without throwing (SSR-safe); Given a payload with `eventId="abc"` is enqueued and then `enqueue` is called again with the same `eventId`, Then the queue contains exactly one entry for `abc`.

### T-006: Visibility-gated enqueue + replay integration in `useSkillUpdates`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Given `document.visibilityState === "hidden"` and a `skill.updated` SSE event arrives, When the hook's `onMessage` runs, Then the toast is enqueued (NOT dispatched as `studio:toast`) and the bell counter still increments; Given the queue contains 3 entries with distinct `eventId`s, When `visibilitychange` fires with `visibilityState === "visible"`, Then 3 `studio:toast` CustomEvents dispatch at 250ms intervals (verified via `vi.useFakeTimers()`) and the queue is empty afterward; Given a queued entry's `eventId` is already in `updateStore.seenEventIds` at replay time, When the queue drains, Then that entry is dropped (no double-toast).

### T-007: `resolveSubscriptionIds` source-origin option + batch lookup helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given installed skills `[{plugin:"a",skill:"x",uuid:"u1"}]` and `includeSourceOriginMatches: false`, When `resolveSubscriptionIds` runs, Then it returns `[{uuid:"u1"}]` (existing behavior, unchanged); Given a source-origin skill `{plugin:".claude",skill:"hi-anton",origin:"source",author:"Anton",localVersion:"1.0.0"}` and the lookup helper returns `{uuid:"u-hi"}` for `(name="hi-anton", author="Anton")`, When the resolver runs with `includeSourceOriginMatches: true`, Then the merged result includes `{uuid:"u-hi"}`; Given a source-origin skill with no `author`, Then it is silently excluded from the lookup batch (no error).

### T-008: `StudioContext.tsx` passes source-origin skills to the hook
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given the user has 2 installed skills + 1 source-origin skill (all with registry twins), When `StudioContext` renders and `useSkillUpdates` is called, Then the hook's `sourceOriginSkills` option contains the one source-origin entry with `name`, `author`, `version`, AND the SSE filter URL `?skills=` includes the resolved uuid for the source-origin twin; Given a source-origin skill with no registry twin, When the resolver returns no match, Then the SSE filter URL excludes that skill silently.

### T-009: `/api/v1/skills/lookup-by-name` route in vskill-platform
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given a POST to `/api/v1/skills/lookup-by-name` with body `{entries:[{name:"hi-anton",author:"Anton"}]}` and the registry contains a matching `Skill` row, When the route runs, Then the response is `{results:[{name:"hi-anton",author:"Anton",uuid:"<id>",slug:"<slug>"}]}`; Given a body with `name="HI-ANTON"` (different case), Then the case-insensitive match still resolves; Given an entry with no matching registry skill, Then the response includes the entry with `uuid` and `slug` undefined; Given a body of 51 entries, Then the route returns 400 (cap is 50).

### T-010: `/api/v1/skills/updates` accepts `?include=source-origin`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06 | **Status**: [x] completed (implemented on `/api/v1/skills/check-updates`, the actual existing endpoint)
**Test Plan**: Given a POST to `/api/v1/skills/updates?include=source-origin` with body `{sourceOrigin:[{name:"hi-anton",author:"Anton",version:"1.0.0"}]}` and the registry has version `1.1.0` of that skill, When the route runs, Then the response includes `{name:"hi-anton",installed:"1.0.0",latest:"1.1.0",updateAvailable:true,versionBump:"minor"}`; Given a source-origin entry with no registry twin, Then the entry is silently excluded from `results` (no error, no 404); Given both an installed entry and a source-origin entry collide on `name`, Then the installed entry's row appears in the response (precedence preserved).

### T-011: `/api/v1/studio/telemetry/sse` Worker route + Analytics Engine write
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-04 | **Status**: [x] completed
**Test Plan**: Given a POST to `/api/v1/studio/telemetry/sse` with valid body `{event:"connected",sessionId:"<uuid>",sourceTier:"platform-proxy",timestamp:1234,durationSinceOpenMs:42}`, When the route runs (with the `STUDIO_SSE_TELEMETRY` binding mocked), Then `env.STUDIO_SSE_TELEMETRY.writeDataPoint` is invoked once with the payload mapped to a data point and the response is `204 No Content`; Given the Analytics Engine binding throws, When the route runs, Then it still returns `204` (failure is swallowed); Given an invalid body (missing `event`), Then the route returns `204` and writes nothing (silent reject).

### T-012: Telemetry pings + dedupe in `useSkillUpdates`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [x] completed
**Test Plan**: Given the hook runs and the EventSource transitions `connecting → connected`, When the `connected` event fires, Then exactly one `fetch("/api/v1/studio/telemetry/sse", ...)` call is made with `{event:"connected",sessionId:<v4 uuid persisted to sessionStorage>,sourceTier:"platform-proxy",timestamp:<now>}`; Given a second `connected` transition occurs in the same session, When the hook fires the telemetry path, Then NO additional fetch is made (deduped per (event, session) tuple); Given `?disableTelemetry=1` is in the URL or `VSKILL_DISABLE_TELEMETRY=1` is set, When any transition fires, Then no telemetry fetch is made.

### T-013: Add `STUDIO_SSE_TELEMETRY` Analytics Engine binding to `wrangler.toml`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed (binding added to `wrangler.jsonc`; `wrangler deploy --dry-run` lists `env.STUDIO_SSE_TELEMETRY` as Analytics Engine Dataset)
**Test Plan**: Given the existing `wrangler.toml` does not have `STUDIO_SSE_TELEMETRY` declared, When the binding block is added under `[[analytics_engine_datasets]]` and a local `wrangler dev` boot is performed, Then the dataset binding is available in `env` (verified by a smoke test that calls `env.STUDIO_SSE_TELEMETRY.writeDataPoint({})` and asserts no throw); Given `wrangler deploy --dry-run`, Then the deploy plan lists the new binding without errors.

### T-014: Author runbook `docs/internal/runbooks/sse-diagnose.md`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US5-05 | **Status**: [x] completed (runbook at `repositories/anton-abyzov/vskill/docs/internal/runbooks/sse-diagnose.md`)
**Test Plan**: Given a fresh contributor opens `docs/internal/runbooks/sse-diagnose.md`, When they follow the steps (open DevTools → set `VSKILL_DEBUG_SSE=1` → reload Studio → inspect console + Network tab + bell tooltip), Then they identify within 60 seconds whether the failure is at (a) EventSource opening, (b) reconnecting, (c) polling fallback, or (d) toast suppression; Given the runbook documents the `VSKILL_DISABLE_TELEMETRY` opt-out, When a privacy-conscious user reads it, Then they find the exact env var and query-param syntax in a callout block.

### T-015: Playwright E2E — source-origin publish → toast (with visibility flip)
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-04, AC-US3-01, AC-US3-03 | **Status**: [x] completed (spec at `repositories/anton-abyzov/vskill/e2e/sse-source-origin-toast.spec.ts`; 3/3 passing)
**Test Plan**: Given a fixture project with one source-origin skill `hi-anton@1.0.0` matching a staging-registry twin, When `vskill studio` is started and the page is opened in Chromium, Then the bell tooltip shows `Live updates: connected` within 5s; Given the staging registry receives a publish bumping the twin to `1.1.0`, When the SSE event arrives, Then a `studio:toast` CustomEvent fires AND the bell counter increments to 1; Given the same scenario but with the page hidden via `Object.defineProperty(document, "visibilityState", {value:"hidden"})` at the moment of arrival, Then no toast fires immediately, the bell counter still increments to 1, AND on the next visibility flip to `visible` exactly one `studio:toast` is dispatched (replayed from the queue).
