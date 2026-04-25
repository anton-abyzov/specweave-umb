---
increment: 0708-skill-update-push-pipeline
title: "Skill Update Push Pipeline (Scanner + UpdateHub DO + SSE + Studio UI)"
type: tasks
---

# Tasks: Skill Update Push Pipeline

## Foundations

### T-001: Prisma schema migration — add 4 Skill columns + index
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**:
  - Given: existing Skill model in prisma/schema.prisma
  - When: migration is applied against a test DB
  - Then: `sourceRepoUrl`, `sourceBranch`, `lastSeenSha`, `lastCheckedAt` columns exist as nullable; `sourceBranch` defaults to "main"; composite index `[sourceRepoUrl, lastCheckedAt(sort: Asc)]` is present
**Files**:
  - `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` (update)
  - `repositories/anton-abyzov/vskill-platform/prisma/migrations/<ts>_skill_source_tracking/migration.sql` (new)

### T-002: Shared types — SkillUpdateEvent, ScanReport
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-02, AC-US3-04 | **Status**: [x] completed
**Test Plan**:
  - Given: types module imported in scanner, DO, SSE endpoint, and Studio hook
  - When: TypeScript compiler checks the project
  - Then: no type errors; SkillUpdateEvent and ScanReport are the single source of truth used by all consumers
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/types.ts` (new)

### T-003: Seed script for tracked skills
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**:
  - Given: `scripts/tracked-skills-seed.json` contains entries for anthropic-skills/* and verified-skill/* repos
  - When: `pnpm tsx scripts/seed-tracked-skills.ts` runs twice against a test DB
  - Then: `sourceRepoUrl` and `sourceBranch` are populated for known skills; second run produces zero duplicate or destructive writes (idempotent)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/seed-tracked-skills.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/scripts/tracked-skills-seed.json` (new)

### T-004: wrangler.jsonc — DO binding, cron bump, AE binding, dev.vars.example
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed
**Test Plan**:
  - Given: wrangler.jsonc is the deployment descriptor
  - When: `wrangler deploy --dry-run` validates the config
  - Then: `UPDATE_HUB` DO binding is present, cron changed from `0 * * * *` to `*/10 * * * *`, `UPDATE_METRICS_AE` Analytics Engine binding exists, `.dev.vars.example` lists `GITHUB_WEBHOOK_SECRET` and `GITHUB_TOKEN` placeholders
**Files**:
  - `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (update)
  - `repositories/anton-abyzov/vskill-platform/.dev.vars.example` (update)

---

## US-001: Central Upstream Scanner

### T-005: [TDD-RED] GitHub API wrapper — ETag caching and error variants
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06 | **Status**: [x] completed
**Test Plan**:
  - Given: a mock GitHub API returning a commit SHA with an ETag header
  - When: `fetchLatestCommit(repoUrl, branch, etag?, env)` is called with a cached ETag
  - Then: the request carries `If-None-Match` header; a 304 response returns `{ unchanged: true }`; a 200 response returns `{ sha, etag, commit }`; a 4xx/5xx response returns `{ error }` without throwing
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/github-api.test.ts` (new)

### T-006: [TDD-GREEN] GitHub API wrapper implementation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-06 | **Status**: [x] completed
**Test Plan**: T-005 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/github-api.ts` (new)

### T-007: [TDD-RED] scanOneSkill — SHA compare, SkillVersion upsert, lastCheckedAt advance
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**:
  - Given: a Skill row with `lastSeenSha = "abc"` and a mock GitHub response returning `sha = "def"`
  - When: `scanOneSkill(skill, env)` runs
  - Then: a new `SkillVersion` row is upserted with `gitSha`, `contentHash`, `diffSummary`; `Skill.lastSeenSha` advances to "def"; `Skill.lastCheckedAt` is updated; `publishToUpdateHub` is called once
  - Given: SHA matches `lastSeenSha = "def"`
  - When: `scanOneSkill(skill, env)` runs
  - Then: no SkillVersion insert, no publish call, only `lastCheckedAt` advances
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (new)

### T-008: [TDD-GREEN] scanOneSkill implementation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: T-007 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (new)

### T-009: [TDD-RED] scanOneSkill — provenance suppression for locally-promoted skills
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
  - Given: a Skill row with a 0688 provenance sidecar where `origin !== "upstream"` or `locallyPromoted === true`
  - When: `scanOneSkill(skill, env)` detects a new SHA
  - Then: `publishToUpdateHub` is NOT called; `lastSeenSha` and `lastCheckedAt` are advanced; a `scanner.suppressed.locally-promoted` metric is emitted
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (update)

### T-010: [TDD-GREEN] scanOneSkill — provenance suppression implementation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: T-009 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (update)

### T-011: [TDD-RED] runSkillUpdateScan — error isolation and structured metrics
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test Plan**:
  - Given: a batch of 3 skills where skill #2 causes a GitHub 500 error
  - When: `runSkillUpdateScan(env)` runs
  - Then: skill #1 and #3 are processed normally; skill #2 error is caught and logged with `{skillId, repoUrl, error}`; `report.errors === 1`; structured metrics include `scanner.runs.total`, `scanner.updates.detected`, `scanner.errors.total`, `scanner.duration.ms`
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scanner.test.ts` (update)

### T-012: [TDD-GREEN] runSkillUpdateScan batch runner with error isolation and metrics
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test Plan**: T-011 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (update)

### T-013: [TDD-REFACTOR] Extract publishToUpdateHub helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: all T-007/T-009/T-011 tests still pass after extraction
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/publish.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (update)

### T-014: Cron wiring — worker entry exports UpdateHub + minute-based scanner dispatch
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
  - Given: cron fires at minute 10
  - When: the cron handler runs
  - Then: `runSkillUpdateScan` is called via `ctx.waitUntil` after existing enrichment; scanner failure does not propagate to the cron handler; `UpdateHub` class is exported from the worker entry
**Files**:
  - `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` (update)

---

## US-002: UpdateHub Durable Object

### T-015: [TDD-RED] UpdateHub — connection map and filtered broadcast
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-06 | **Status**: [x] completed
**Test Plan**:
  - Given: two WebSocket clients connected to the DO — client A with filter `["skillA"]`, client B with filter `["skillB"]`
  - When: an event for `skillId = "skillA"` is published to `/publish`
  - Then: only client A receives the message; client B does not; if client A's socket throws on send, it is removed from the session map and broadcast to remaining clients completes without error
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/update-hub.test.ts` (new)

### T-016: [TDD-GREEN] UpdateHub — DO class (connection accept, publish, filter)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: T-015 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/update-hub.ts` (new)

### T-017: [TDD-RED] UpdateHub — hibernation round-trip preserves filter
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-06 | **Status**: [x] completed
**Test Plan**:
  - Given: a client connects with filter `["skillX"]` and the DO undergoes simulated eviction (Miniflare reset, constructor re-invoked)
  - When: an event for `skillId = "skillX"` is published after wake
  - Then: the client still receives the event; `ws.deserializeAttachment()` returns `{filter: ["skillX"]}`; session map is correctly rehydrated from `state.getWebSockets()`
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/update-hub.test.ts` (update)

### T-018: [TDD-GREEN] UpdateHub — hibernation rehydration in constructor
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test Plan**: T-017 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/update-hub.ts` (update)

---

## US-003: Public SSE Endpoint + Internal Publish

### T-019: [TDD-RED] Internal publish endpoint — HMAC auth and DO forwarding
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**:
  - Given: POST to `/api/v1/internal/skills/publish` with valid `X-Internal-Key` and body `{type: "skill.updated", skillId, version, publishedAt}`
  - When: the endpoint handles the request
  - Then: DO `handlePublish` is called with the enriched payload; response is HTTP 202 `{ok: true, enqueued: true}`
  - Given: missing or invalid `X-Internal-Key`
  - Then: response is HTTP 401 with zero side effects (DO not called)
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/skills/publish/__tests__/route.test.ts` (new)

### T-020: [TDD-GREEN] Internal publish endpoint implementation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test Plan**: T-019 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/internal/skills/publish/route.ts` (new)

### T-021: [TDD-RED] SSE stream endpoint — event framing, keepalive, missing skills param
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05 | **Status**: [x] completed
**Test Plan**:
  - Given: `GET /api/v1/skills/stream?skills=skill-uuid-1,skill-uuid-2`
  - When: the DO publishes a `skill.updated` event for `skill-uuid-1`
  - Then: SSE stream delivers a frame formatted as `event: skill.updated\nid: <uuid>\ndata: <json>\n\n`; a `: keepalive` comment is sent every 25 seconds
  - Given: `GET /api/v1/skills/stream` with no `skills` param
  - Then: HTTP 400 is returned immediately
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/__tests__/route.test.ts` (new)

### T-022: [TDD-GREEN] SSE stream endpoint implementation (WS bridge to DO)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-05 | **Status**: [x] completed
**Test Plan**: T-021 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/route.ts` (new)

### T-023: [TDD-RED] SSE integration — filtered delivery end-to-end
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**:
  - Given: two SSE test clients — client X subscribed with `skills=skill-A`, client Y with `skills=skill-B`
  - When: a `skill.updated` event for `skillId = "skill-A"` is published via `/api/v1/internal/skills/publish`
  - Then: client X receives the event within 2 seconds; client Y does NOT receive it
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/sse-integration.test.ts` (new)

### T-024: [TDD-GREEN] Wire DO stub into SSE stream endpoint for integration path
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**: T-023 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/route.ts` (update)

---

## US-004: GitHub Webhook Fast-Path

### T-025: [TDD-RED] Webhook — HMAC verification and anti-replay KV gate
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-05 | **Status**: [x] completed
**Test Plan**:
  - Given: POST to `/api/v1/webhooks/github` with valid `X-Hub-Signature-256` and `X-GitHub-Delivery` UUID
  - When: first delivery is processed
  - Then: HMAC verified using `GITHUB_WEBHOOK_SECRET` with timing-safe compare; request proceeds
  - Given: same `X-GitHub-Delivery` UUID repeated within 5 minutes
  - Then: HTTP 200 returned with no publish side effect; KV key `gh-delivery:<uuid>` exists with TTL ≤ 300s
  - Given: missing or mismatched `X-Hub-Signature-256`
  - Then: HTTP 401 with zero side effects
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/__tests__/route.test.ts` (new)

### T-026: [TDD-GREEN] Webhook endpoint — HMAC verify and anti-replay implementation
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-05 | **Status**: [x] completed
**Test Plan**: T-025 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` (new)

### T-027: [TDD-RED] Webhook — push event routing to single-skill scanner
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed
**Test Plan**:
  - Given: valid push payload for a `repository.html_url` matching a tracked Skill's `sourceRepoUrl` and `ref` matching its `sourceBranch`
  - When: the webhook endpoint processes the event
  - Then: `scanOneSkill` is called for that skill only (not the full batch); response is HTTP 200 `{ok: true, processed: 1}`
  - Given: push to a branch not matching any tracked `sourceBranch` for that repo
  - Then: HTTP 204 returned; `scanOneSkill` NOT called
  - Given: push for a repo not in tracked skills
  - Then: HTTP 204 with no scanner invocation
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/__tests__/route.test.ts` (update)

### T-028: [TDD-GREEN] Webhook — push routing to scanOneSkill via ctx.waitUntil
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test Plan**: T-027 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` (update)

---

## US-005: Skill Studio Live Update UI

### T-029: [TDD-RED] useSkillUpdates — EventSource lifecycle and update store
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-07, AC-US5-08 | **Status**: [x] completed
**Test Plan**:
  - Given: `useSkillUpdates(["skill-A", "skill-B"])` is mounted
  - When: a `skill.updated` event arrives with `skillId = "skill-A"`
  - Then: `updates.get("skill-A")` returns the event data; `status` progresses from `"connecting"` to `"connected"`; the EventSource URL contains `?skills=skill-A,skill-B` (filter scoped to installed list per AC-US5-08)
  - When: `onerror` fires
  - Then: reconnect occurs without losing the filter; `?skills=skill-A,skill-B` is preserved in the new EventSource URL
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/__tests__/use-skill-updates.test.ts` (new)

### T-030: [TDD-GREEN] useSkillUpdates — EventSource, update store, reconnect
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-08 | **Status**: [x] completed
**Test Plan**: T-029 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/use-skill-updates.ts` (new)

### T-031: [TDD-RED] useSkillUpdates — visibility-gated toast vs silent badge
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, AC-US5-07 | **Status**: [x] completed
**Test Plan**:
  - Given: `document.visibilityState === "visible"` when a `skill.updated` event arrives
  - When: hook processes the event
  - Then: toast fires (accessible, `role="status"`, `aria-live="polite"`, 4-second duration with skill name, version, "View changes" link) and `updates` map increments
  - Given: `document.visibilityState === "hidden"` when an event arrives
  - Then: no toast fires; `updates` map still increments (badge-only)
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/__tests__/use-skill-updates.test.ts` (update)

### T-032: [TDD-GREEN] useSkillUpdates — visibility gating for toast
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02 | **Status**: [x] completed
**Test Plan**: T-031 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/use-skill-updates.ts` (update)

### T-033: [TDD-RED] useSkillUpdates — 60s disconnect fallback to poll mode
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05, AC-US5-07 | **Status**: [x] completed
**Test Plan**:
  - Given: `useSkillUpdates` with an EventSource that fails to open for >60 seconds
  - When: the 60-second timeout elapses
  - Then: `status` transitions to `"fallback"`; poll against `/api/v1/skills/check-updates?skills=<csv>` fires every 5 minutes; when EventSource later succeeds, `status` returns to `"connected"` and polling stops
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/__tests__/use-skill-updates.test.ts` (update)

### T-034: [TDD-GREEN] useSkillUpdates — poll fallback after 60s failure
**User Story**: US-005 | **Satisfies ACs**: AC-US5-05 | **Status**: [x] completed
**Test Plan**: T-033 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/use-skill-updates.ts` (update)

### T-035: [TDD-RED] UpdateBell — unread count badge and dropdown
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**:
  - Given: `updates` map contains 2 entries
  - When: `UpdateBell` renders
  - Then: badge count is 2; `aria-label` communicates "2 updates available"; clicking opens a dropdown listing each skill with `diffSummary` and "View changes" action
  - Given: user clicks "View changes" for a skill
  - Then: `dismiss(skillId)` is called and the entry is removed from the dropdown
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/__tests__/UpdateBell.test.tsx` (new)

### T-036: [TDD-GREEN] UpdateBell component implementation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed
**Test Plan**: T-035 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/UpdateBell.tsx` (new)

### T-037: [TDD-RED] UpdateChip and SkillRow — update dot and not-tracked dot indicators
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-09 | **Status**: [x] completed
**Test Plan**:
  - Given: a skill present in the `updates` map
  - When: `SkillRow` renders
  - Then: a blue dot with tooltip showing the new version appears; the indicator clears after `dismiss(skillId)`
  - Given: a skill whose `sourceRepoUrl` is null on the server (not tracked)
  - When: `SkillRow` renders
  - Then: a dim gray status dot with hover tooltip "Not tracked — run `vskill outdated` manually" appears; no toast fires, no bell increments, no warning color used (visually quieter than the blue update dot per AC-US5-09)
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/__tests__/UpdateChip.test.tsx` (new)

### T-038: [TDD-GREEN] UpdateChip, SkillRow indicator, and not-tracked dot implementation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-09 | **Status**: [x] completed
**Test Plan**: T-037 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/UpdateChip.tsx` (new)
  - `repositories/anton-abyzov/vskill/src/studio/components/SkillRow.tsx` (update)

### T-039: UpdateAction — RightPanel "Install update" button
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04 | **Status**: [x] completed
**Test Plan**:
  - Given: a skill with an available update displayed in RightPanel
  - When: user clicks "View changes"
  - Then: `UpdateAction` renders an "Install update" button that invokes `vskill update <skill>` via studio IPC; clicking calls `dismiss(skillId)` and clears the indicator
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/UpdateAction.tsx` (new)
  - `repositories/anton-abyzov/vskill/src/studio/components/RightPanel.tsx` (update)

### T-040: Wire useSkillUpdates into StudioRoot + TopRail + SidebarSection
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test Plan**:
  - Given: StudioRoot mounts with the user's installed skill IDs
  - When: the Studio renders
  - Then: a single `useSkillUpdates` instance is hoisted to root; `UpdateBell` in TopRail receives `updates`; `SidebarSection` renders `UpdateChip` for sections with updates; filter changes (install/uninstall) reconnect EventSource with updated `?skills=` param
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/layout/StudioRoot.tsx` (update)
  - `repositories/anton-abyzov/vskill/src/studio/components/TopRail.tsx` (update)
  - `repositories/anton-abyzov/vskill/src/studio/components/SidebarSection.tsx` (update)

### T-041: 0683 supersession — flip metadata.json and remove stub files
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [x] completed
**Test Plan**:
  - Given: `.specweave/increments/0683-studio-update-notifications/metadata.json`
  - When: the file is updated
  - Then: `status` is `"superseded"` and `supersededBy` references `"0708-skill-update-push-pipeline"`; any 0683 stub component files are removed or redirected to 0708 components
**Files**:
  - `.specweave/increments/0683-studio-update-notifications/metadata.json` (update)

---

## End-to-End Playwright Tests

### T-042: E2E — webhook → DO fan-out → Studio badge within 2s
**User Story**: US-001, US-002, US-003, US-004, US-005 | **Satisfies ACs**: AC-US4-04, NFR-002 | **Status**: [x] completed
**Test Plan**:
  - Given: a Studio tab open subscribed to `skill-A`
  - When: a mock GitHub push webhook is posted for `skill-A`'s repo
  - Then: `UpdateBell` badge increments to 1 within 2 seconds; no toast fires if the tab is backgrounded; `SkillRow` for `skill-A` shows the blue update dot
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline.spec.ts` (new)

### T-043: E2E — SSE reconnect after drop, fallback poll activation
**User Story**: US-003, US-005 | **Satisfies ACs**: AC-US5-05, AC-US5-07 | **Status**: [ ] pending
**Test Plan**:
  - Given: a Studio tab with an open SSE connection
  - When: the connection is forcibly dropped and 60 seconds elapse without reconnect
  - Then: `status` becomes `"fallback"`; the 5-minute poll fires and delivers pending updates; when SSE connection is restored, `status` returns to `"connected"`
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline.spec.ts` (update)

### T-044: E2E — not-tracked indicator visible for skills without sourceRepoUrl
**User Story**: US-005 | **Satisfies ACs**: AC-US5-09 | **Status**: [x] completed
**Test Plan**:
  - Given: an installed skill with null `sourceRepoUrl` on the server
  - When: the Studio renders the skill in `SkillRow`
  - Then: a dim gray status dot is visible; hovering shows tooltip "Not tracked — run `vskill outdated` manually"; no toast fires, no bell increments, no warning color used
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/skill-update-pipeline.spec.ts` (update)

---

## Delivery Guarantee (US-001 ACs 08-10, US-003 ACs 07-09, US-005 ACs 10-11, NFR-007)

### T-045: Prisma migration — UpdateEvent outbox table + resolution columns on Skill
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [x] completed
**Test Plan**:
  - Given: existing schema with 4 sourceRepo* columns already added (T-001)
  - When: migration `<ts+1>_update_event_outbox` is applied
  - Then: `UpdateEvent` table exists with `id` (ULID), `skillId`, `versionId`, `payload`, `source`, `createdAt`, `publishedAt?`, `publishAttempts`, `lastAttemptErr?`; indexes on `[publishedAt, createdAt]` and `[skillId, createdAt DESC]`; Skill model gains `resolutionState?`, `resolutionAttempts`, `resolutionLastAt?` columns and `[resolutionState, resolutionLastAt]` index
**Files**:
  - `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` (update)
  - `repositories/anton-abyzov/vskill-platform/prisma/migrations/<ts+1>_update_event_outbox/migration.sql` (new)

### T-046: [TDD-RED] outbox-writer — transactional SkillVersion + UpdateEvent write
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08, AC-US1-10 | **Status**: [x] completed
**Test Plan**:
  - Given: a `scanOneSkill` call that detects a new SHA
  - When: `writeSkillVersionWithOutbox(tx, skill, commit, source, env)` is called
  - Then: `SkillVersion` and `UpdateEvent` are inserted atomically in a single Prisma `$transaction`; `UpdateEvent.id` is a ULID (`evt_01...`); if the transaction rolls back, neither row exists; after commit, `publishToUpdateHubWithEventId` is called fire-and-forget; on success `publishedAt` is set; on failure the row stays with `publishedAt = null` for reconciler pickup
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-writer.test.ts` (new)

### T-047: [TDD-GREEN] outbox-writer implementation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08, AC-US1-10 | **Status**: [x] completed
**Test Plan**: T-046 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-writer.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scanner.ts` (update — replace direct SkillVersion insert with `writeSkillVersionWithOutbox`)

### T-048: [TDD-RED] Submission-processing retrofit — UpdateEvent in same txn (AC-US1-09)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-09 | **Status**: [x] completed
**Test Plan**:
  - Given: the existing submission-processing consumer creates a `SkillVersion` row
  - When: `process-submission.ts` is modified to call `writeSkillVersionWithOutbox`
  - Then: `UpdateEvent` row is inserted in the same DB transaction as `SkillVersion`; source field is `"submission"`; existing submission-processing tests still pass; a new test asserts the outbox row is created on a successful submission
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.test.ts` (update)

### T-049: [TDD-GREEN] Submission-processing retrofit implementation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-09 | **Status**: [x] completed
**Test Plan**: T-048 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` (update)

### T-050: [TDD-RED] outbox-reconciler — 30s retry of stuck UpdateEvent rows
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08, AC-US1-10 | **Status**: [x] completed
**Test Plan**:
  - Given: an `UpdateEvent` row with `publishedAt = null` and `createdAt > 10s ago` and `publishAttempts < 10`
  - When: `reconcileOutbox(env)` runs
  - Then: `publishToUpdateHubWithEventId` is called with the stored payload and ULID; on success `publishedAt` is set; on failure `publishAttempts` is incremented and `lastAttemptErr` is recorded; a row with `publishAttempts >= 10` is skipped and an `outbox.attempts-exceeded` metric is emitted; fresh rows (<10s old) are not touched
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/outbox-reconciler.test.ts` (new)

### T-051: [TDD-GREEN] outbox-reconciler implementation + 30s cron wiring
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08, AC-US1-10 | **Status**: [x] completed
**Test Plan**: T-050 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/outbox-reconciler.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` (update — add 30s branch in `scheduled()` to call `reconcileOutbox`)

### T-052: [TDD-RED] UpdateHub — replay log and Last-Event-ID resume
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07, AC-US3-08 | **Status**: [x] completed
**Test Plan**:
  - Given: the DO has published events for `skillId="A"` (eventId `evt_01`) and `skillId="B"` (eventId `evt_02`)
  - When: a client reconnects with `Last-Event-ID: evt_01` and filter `["A","B"]`
  - Then: the DO replays `evt_02` (events after `evt_01` matching the filter) in order, then starts live stream
  - Given: `Last-Event-ID` references an event older than 5 minutes (not in replay log)
  - Then: DO emits a synthetic `event: gone\ndata: {"reason":"too-old"}\n\n` frame and closes; `do.replay.miss.gone` metric is emitted
  - Given: replay log exceeds 10k entries
  - Then: LRU eviction removes oldest entries without throwing
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/update-hub.replay.test.ts` (new)

### T-053: [TDD-GREEN] UpdateHub — replay log implementation (in-memory, 5-min TTL, 10k LRU cap)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07, AC-US3-08 | **Status**: [x] completed
**Test Plan**: T-052 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/update-hub.ts` (update — add `replayLog: Map<eventId, {at, payload}>`, sweep on wake, `resumeSince(lastEventId, filter)` method, `gone` frame emit)
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/stream/route.ts` (update — forward `Last-Event-ID` header in DO upgrade URL as `lastEventId` param)

### T-054: [TDD-RED] UpdateHub — idempotent publish on duplicate eventId
**User Story**: US-003 | **Satisfies ACs**: AC-US3-09 | **Status**: [x] completed
**Test Plan**:
  - Given: an event with `eventId = "evt_01"` has already been published and is in the replay log
  - When: `POST /api/v1/internal/skills/publish` is called again with the same `eventId`
  - Then: the DO returns `{ok: true, deduped: true, delivered: 0}`; no fan-out occurs; `do.publish.deduped` metric is emitted; the response to the publish endpoint is HTTP 200 (not 202) to signal the no-op
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/update-hub.idempotency.test.ts` (new)

### T-055: [TDD-GREEN] UpdateHub — idempotency check in handlePublish
**User Story**: US-003 | **Satisfies ACs**: AC-US3-09 | **Status**: [x] completed
**Test Plan**: T-054 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/update-hub.ts` (update — guard in `handlePublish` against `replayLog.has(event.eventId)`)

### T-056: [TDD-RED] useSkillUpdates hook — client-side seenEventIds dedup (AC-US5-10)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-10 | **Status**: [x] completed
**Test Plan**:
  - Given: the hook receives a `skill.updated` SSE event with `lastEventId = "evt_01"`
  - When: the same event arrives a second time (replay race with live stream)
  - Then: the second event is silently dropped (early-return before updating the store or firing toast); `seenEventIds` Set holds `"evt_01"`; when the Set exceeds 500 entries, oldest entries are evicted FIFO
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/__tests__/use-skill-updates.test.ts` (update)

### T-057: [TDD-GREEN] useSkillUpdates hook — seenEventIds FIFO dedup implementation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-10 | **Status**: [x] completed
**Test Plan**: T-056 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/use-skill-updates.ts` (update)

### T-058: [TDD-RED] useSkillUpdates hook — gone-frame and 409 fallback to check-updates (AC-US5-11)
**User Story**: US-005 | **Satisfies ACs**: AC-US5-11 | **Status**: [x] completed
**Test Plan**:
  - Given: the SSE stream delivers `event: gone\ndata: {"reason":"too-old"}\n\n`
  - When: the hook receives the `gone` event
  - Then: hook immediately POSTs to `/api/v1/skills/check-updates?skills=<csv>` for full reconciliation; any skills with `updateAvailable: true` in the response are added to the `updates` store; `status` does NOT change (stream is still open after gone-frame)
  - Given: the SSE endpoint returns HTTP 409
  - Then: same fallback to `check-updates` is triggered
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/__tests__/use-skill-updates.test.ts` (update)

### T-059: [TDD-GREEN] useSkillUpdates hook — gone-frame and 409 fallback implementation
**User Story**: US-005 | **Satisfies ACs**: AC-US5-11 | **Status**: [x] completed
**Test Plan**: T-058 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/lib/use-skill-updates.ts` (update)

---

## US-006: Reactive Skill Discovery

### T-060: [TDD-RED] Discovery enqueue helper — check-updates triggers resolver for unresolved skills
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-05 | **Status**: [x] completed
**Test Plan**:
  - Given: a `/check-updates` request includes a skill with `sourceRepoUrl = null` and `resolutionState = null`
  - When: the `check-updates` handler processes the response
  - Then: `enqueueDiscovery(skillId, env)` is called; a `discovery-resolve` CF Queue message is sent; the response includes `trackedForUpdates: false` and `resolutionState: null` for that skill
  - Given: the same skill with `resolutionState = "unresolvable"` and `resolutionLastAt` within the active backoff window
  - Then: `enqueueDiscovery` is NOT called (backoff respected)
  - Given: `resolutionLastAt` past the backoff window for the current `resolutionAttempts` step (exponential: 1h, 6h, 24h, 72h)
  - Then: `enqueueDiscovery` is called again
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/discovery/__tests__/enqueue.test.ts` (new)

### T-061: [TDD-GREEN] Discovery enqueue helper + check-updates extension
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-05 | **Status**: [x] completed
**Test Plan**: T-060 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/discovery/enqueue.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/check-updates/route.ts` (update — call enqueue helper; add `trackedForUpdates` + `resolutionState` fields to response)

### T-062: [TDD-RED] Resolver consumer — infer sourceRepoUrl from SKILL.md frontmatter
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test Plan**:
  - Given: a `discovery-resolve` queue message for a skill whose `SKILL.md` frontmatter contains a `repository:` field pointing to a valid GitHub repo with a reachable `SKILL.md`
  - When: `resolveSkillSource(job, env)` processes the message
  - Then: `Skill.sourceRepoUrl`, `Skill.sourceBranch` are set; `resolutionState` becomes `"resolved"`; `resolutionLastAt` is updated
  - Given: the `SKILL.md` frontmatter lacks a `repository:` field and the plugin manifest also yields nothing
  - Then: `resolutionAttempts` is incremented; `resolutionState` becomes `"unresolvable"`; `resolutionLastAt` is set to now
  - Given: `resolutionAttempts` has reached 4 (all backoff steps exhausted)
  - Then: no further auto-retry is enqueued; state stays `"unresolvable"`
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/discovery/__tests__/resolver.test.ts` (new)

### T-063: [TDD-GREEN] Resolver consumer implementation
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test Plan**: T-062 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/discovery/resolver.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` (update — register `discovery-resolve` queue consumer)
  - `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (update — add `DISCOVERY_RESOLVE_QUEUE` binding: `max_batch_size: 10`, `max_batch_timeout: 3`, `max_concurrency: 5`, `max_retries: 2`, DLQ: `submission-dlq`)

### T-064: [TDD-RED] register-tracking endpoint — explicit opt-in with content-hash verification
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**Test Plan**:
  - Given: `POST /api/v1/skills/:id/register-tracking` with `{repoUrl, branch}` where the repo contains a `SKILL.md` whose content hash matches `Skill.contentHash`
  - When: the endpoint processes the request
  - Then: `Skill.sourceRepoUrl`, `Skill.sourceBranch` are updated; `resolutionState` becomes `"user-registered"`; HTTP 200 returned
  - Given: `SKILL.md` at the supplied `repoUrl` does NOT hash to `Skill.contentHash`
  - Then: HTTP 422 returned; no Skill update
  - Given: the session has already made 10 register-tracking calls this hour (rate limit)
  - Then: HTTP 429 returned; no Skill update
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[id]/register-tracking/__tests__/route.test.ts` (new)

### T-065: [TDD-GREEN] register-tracking endpoint implementation
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04 | **Status**: [x] completed
**Test Plan**: T-064 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[id]/register-tracking/route.ts` (new)

---

## US-007: Unified Scanner Queue

### T-066: wrangler.jsonc — SCAN_HIGH_QUEUE + SCAN_NORMAL_QUEUE bindings
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed
**Test Plan**:
  - Given: wrangler.jsonc is updated with queue bindings
  - When: `wrangler deploy --dry-run` validates
  - Then: `SCAN_HIGH_QUEUE` and `SCAN_NORMAL_QUEUE` producers and consumers are bound; `vars.SHARD_COUNT = "1"` is present; existing queue bindings are undisturbed
**Files**:
  - `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (update)

### T-067: [TDD-RED] scan-lock — KV-backed dedup with 30s TTL
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [x] completed
**Test Plan**:
  - Given: `acquireScanLock(skillId, env)` is called for `skillId = "abc"`
  - When: the KV key `scan-lock:abc` does not exist
  - Then: the key is written with TTL 30s; function returns `true`
  - When: the key already exists (lock held)
  - Then: function returns `false` without overwriting; a `queue.scan.dedup.hits` metric is emitted
  - Given: `releaseScanLock(skillId, env)` is called
  - Then: the KV key `scan-lock:abc` is deleted
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/scan-lock.test.ts` (new)

### T-068: [TDD-GREEN] scan-lock implementation
**User Story**: US-007 | **Satisfies ACs**: AC-US7-02 | **Status**: [x] completed
**Test Plan**: T-067 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/scan-lock.ts` (new)

### T-069: [TDD-RED] queue-consumer — rate-limit guard + scan dispatch
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x] completed
**Test Plan**:
  - Given: a `scan-high` message arrives for `skillId = "X"` and GitHub remaining rate is 600
  - When: the consumer dispatches the job
  - Then: `acquireScanLock("X", env)` is called; on lock acquired, `scanOneSkill` runs; lock is released after; `SkillVersion` is written only if SHA changed (idempotent)
  - Given: GitHub rate-limit KV key `github-rl:remaining` shows < 500
  - When: a `scan-normal` or discovery-triggered message arrives
  - Then: the job is dropped (not processed); a `queue.scan.shed` metric is emitted; HTTP 200 ack to the queue
  - Given: rate-limit < 500 but message is from `scan-high` queue
  - Then: `scan-high` messages are NOT dropped (high-priority bypass); only cron+discovery paths are shed
  - Given: a `scan-normal` message for `skillId = "Y"` where lock is already held
  - Then: job is dropped; `queue.scan.dedup.hits` metric emitted
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/__tests__/queue-consumer.test.ts` (new)

### T-070: [TDD-GREEN] queue-consumer implementation (unified scan-high + scan-normal)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x] completed
**Test Plan**: T-069 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/queue-consumer.ts` (new)
  - `repositories/anton-abyzov/vskill-platform/src/lib/skill-update/enqueue.ts` (new — producers: `enqueueScanHigh`, `enqueueScanNormal` helpers used by webhook, cron, and rescan)
  - `repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts` (update — register `SCAN_HIGH_QUEUE` + `SCAN_NORMAL_QUEUE` consumers; cron enqueues per-skill `scan-normal` batch instead of calling `runSkillUpdateScan` directly)
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/webhooks/github/route.ts` (update — replace `scanOneSkill` call with `enqueueScanHigh`)

---

## US-008: User-Triggered Check-Now

### T-071: [TDD-RED] rescan endpoint — enqueue scan-high, per-session rate limit
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] completed
**Test Plan**:
  - Given: `POST /api/v1/skills/:id/rescan` from a session that has made 9 rescan calls this minute
  - When: the endpoint processes the request
  - Then: `enqueueScanHigh(skillId, env, {forceRefresh: true})` is called; HTTP 202 `{ok: true, jobId: "<ulid>"}` returned; scan-lock is bypassed (forceRefresh) but rate-limit guard in the consumer is NOT bypassed
  - Given: the same session makes an 11th rescan call in the same minute
  - Then: HTTP 429 `{error: "rate_limited"}` returned; nothing enqueued
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[id]/rescan/__tests__/route.test.ts` (new)

### T-072: [TDD-GREEN] rescan endpoint implementation
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] completed
**Test Plan**: T-071 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[id]/rescan/route.ts` (new)

### T-073: [TDD-RED] Studio "Check now" button — per-skill spinner + SSE result delivery
**User Story**: US-008 | **Satisfies ACs**: AC-US8-04, AC-US8-05 | **Status**: [x] completed
**Test Plan**:
  - Given: a skill in `RightPanel` below the `DetailHeader`
  - When: user clicks "Check now"
  - Then: `POST /api/v1/skills/:id/rescan` is called; a per-skill spinner appears; on receiving a `skill.updated` event for that `skillId` via the existing SSE stream, the spinner clears and the update indicator appears; if no event arrives within 30 seconds, spinner clears without error
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/__tests__/UpdateAction.test.tsx` (update)

### T-074: [TDD-GREEN] "Check now" button + spinner state in UpdateAction
**User Story**: US-008 | **Satisfies ACs**: AC-US8-04, AC-US8-05 | **Status**: [x] completed
**Test Plan**: T-073 tests pass
**Files**:
  - `repositories/anton-abyzov/vskill/src/studio/components/UpdateAction.tsx` (update — add "Check now" button below DetailHeader, spinner state, 30s timeout)
