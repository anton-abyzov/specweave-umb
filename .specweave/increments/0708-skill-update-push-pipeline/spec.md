---
increment: 0708-skill-update-push-pipeline
title: "Skill Update Push Pipeline (Scanner + UpdateHub DO + SSE + Studio UI)"
type: feature
priority: P1
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
supersedes:
  - 0683-studio-update-notifications
---

# Feature: Skill Update Push Pipeline (Scanner + UpdateHub DO + SSE + Studio UI)

## Overview

When an upstream skill repository (e.g. `anthropic-skills/frontend-design`) publishes a new commit, Skill Studio tabs and installed CLI clients have no live path to learn about the change — today they either don't check at all or each client polls GitHub independently, wasting rate limit and leaving UIs stale until the next manual `vskill outdated`.

This increment delivers a centralized, push-based update pipeline hosted entirely on Cloudflare Workers: one shared scanner detects new upstream SHAs on a 10-minute cadence, a Durable Object (`UpdateHub`) holds a hibernatable fan-out channel across edge isolates, a public SSE endpoint streams filtered events to connected Skill Studio tabs, and first-party repositories push instant notifications via a signed GitHub webhook. The Skill Studio UI subscribes via `EventSource` and surfaces updates as a foreground toast / background silent badge, falling back to a 5-minute poll if streaming is blocked. **0683 is superseded** — its planned UpdateBell, row indicator, and sidebar chip components are absorbed into this increment and fed from the SSE stream instead of a 5-minute poll.

**Target repos:** `repositories/anton-abyzov/vskill-platform` (scanner, DO, SSE endpoint, webhook) and `repositories/anton-abyzov/vskill` (Skill Studio UI).
**Sync projects:** `vskill-platform` (US-001, US-002, US-003, US-004, US-006, US-007, and the endpoint side of US-008), `vskill` (US-005 and the Studio UI side of US-008).
**Scale target (v1):** 100 tracked skills **platform-wide** (the catalog), 100 concurrent SSE clients **platform-wide** (one connection per open Studio tab across all users), <1 s webhook→fan-out latency, <10 min poll→fan-out staleness, $5–15/mo marginal cost.

**Explicit non-limits:** there is **no per-user cap** on how many skills a user can have installed locally. A single Studio tab opens **one** SSE connection whose subscription filter is the user's installed-skill list — regardless of whether that list contains 5 skills or 500. The SSE protocol does **not** paginate, page, chunk, or rate-limit updates per user; filtering is done server-side at the `UpdateHub` DO against the subscription list, so a user's browser only sees messages for skills they actually have. Catalog scaling beyond the 100-skill target is a silent infrastructure concern (bump cron cadence, shard the DO) and must never surface a user-facing "waiting" or "upgrade to tier X" state.

## Personas

- **Skill Studio developer (P1 — primary):** A user editing or browsing skills in the verified-skill.com Skill Studio with one to ten tabs open. Wants to see an "Update available" cue appear without refreshing the page when an upstream repo they've installed from pushes a new commit, and wants the cue to be non-disruptive when their tab is in the background.
- **Skill publisher / maintainer (P2 — secondary):** The person responsible for a skill listed in the verified-skill.com catalog. Wants upstream changes detected centrally by the platform so their users see updates without bespoke per-client polling.
- **First-party repo maintainer (P3 — tertiary):** Owner of a verified-skill.com-controlled repository that supports GitHub webhook pushes. Expects a push to the default branch to propagate to every connected Skill Studio tab within ~1 second via webhook, not up to 10 minutes via poll.

## User Stories

### US-001: Central upstream scanner (P1)
**Project**: vskill-platform

**As a** skill publisher / platform operator
**I want** a single scanner task that runs every 10 minutes against every tracked upstream skill repository and records new SHAs as `SkillVersion` rows
**So that** the platform owns one authoritative view of upstream state instead of N clients polling independently and burning GitHub rate limit

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A scheduled Cloudflare Worker task runs at a 10-minute cadence (Cron Trigger `*/10 * * * *`), iterates every `Skill` row that has a non-null `sourceRepoUrl`, and for each skill calls `GET /repos/:owner/:repo/commits/:branch` against the GitHub REST API, authenticating with a fine-grained PAT stored as Cloudflare secret `GITHUB_TOKEN` (scope: `public_repo` read only).
- [ ] **AC-US1-02**: When the returned commit SHA differs from `Skill.lastSeenSha`, the scanner upserts a new `SkillVersion` row (with `gitSha`, `contentHash`, `diffSummary` populated from the commit payload), advances `Skill.lastSeenSha` and `Skill.lastCheckedAt`, and publishes a `skill.updated` event to the internal broadcast endpoint `POST /api/v1/internal/skills/publish` authenticated with HMAC header `X-Internal-Key` keyed on secret `INTERNAL_BROADCAST_KEY`.
- [ ] **AC-US1-03**: If the upstream repo's latest commit SHA equals `lastSeenSha`, the scanner performs no DB writes, no publish, and advances only `lastCheckedAt` — idempotent re-runs produce zero user-visible side effects.
- [ ] **AC-US1-04**: If the `Skill` has a `.vskill-meta.json` provenance sidecar (introduced by 0688) with `origin !== "upstream"` or `locallyPromoted === true`, the scanner suppresses the publish call, logs a `scanner.suppressed.locally-promoted` metric, and advances `lastCheckedAt` only — no false update notifications for scope-transferred skills.
- [ ] **AC-US1-05**: A Prisma migration adds four nullable columns to `Skill`: `sourceRepoUrl: String?`, `sourceBranch: String? @default("main")`, `lastSeenSha: String?`, `lastCheckedAt: DateTime?`. A one-time seed script (`scripts/seed-tracked-skills.ts`) populates these columns for known upstream skills (`anthropic-skills/pdf`, `pptx`, `xlsx`, `docx`, and `verified-skill/*` first-party) and is idempotent (re-runs produce no duplicate or destructive writes).
- [ ] **AC-US1-06**: Scanner GitHub call failures (4xx/5xx, timeouts) are caught per-skill, logged with `{skillId, repoUrl, error}`, and do NOT abort the remaining iterations — one bad repo does not block the batch.
- [ ] **AC-US1-07**: Scanner emits structured metrics (`scanner.runs.total`, `scanner.updates.detected`, `scanner.suppressed.locally-promoted`, `scanner.errors.total`, `scanner.duration.ms`) on each run, queryable via Cloudflare Analytics Engine.
- [ ] **AC-US1-08** (outbox-write): Every `SkillVersion` insert — whether from scanner, `process-submission`, or admin `rescan-published` — is wrapped in a single DB transaction that also inserts an `UpdateEvent` row `{eventId (uuid), skillId, version, gitSha, createdAt, publishedAt: null, publishAttempts: 0}`. Either both rows commit or neither does. This is the outbox write-side of the delivery guarantee.
- [ ] **AC-US1-09** (outbox reconciler): A Cloudflare Cron-triggered `outbox-reconciler` task runs every 30 seconds, selects `UpdateEvent` rows where `publishedAt IS NULL AND createdAt < NOW() - 10s`, re-issues each to `POST /api/v1/internal/skills/publish` with the row's `eventId`, and on success sets `publishedAt = NOW()` + increments `publishAttempts`. Rows with `publishAttempts >= 10` emit a `delivery.outbox.stuck` alert metric and are skipped on subsequent runs until manually cleared.
- [ ] **AC-US1-10** (schema): The Prisma migration from AC-US1-05 also adds a new model `UpdateEvent { eventId String @id @default(uuid()), skillId String, version String, gitSha String, createdAt DateTime @default(now()), publishedAt DateTime?, publishAttempts Int @default(0) }` with an index on `(publishedAt, createdAt)` to support the reconciler's selection query.

---

### US-002: UpdateHub Durable Object with hibernation (P1)
**Project**: vskill-platform

**As a** skill publisher / platform operator
**I want** a single Durable Object (`UpdateHub`) that holds the list of connected clients, supports hibernation, and fans out publish events to clients whose installed-skill filter matches the event's skill
**So that** clients connected to different Cloudflare edge isolates all receive the same broadcast — which the existing per-isolate `event-bus.ts` cannot deliver today

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A `UpdateHub` Durable Object class is bound in `wrangler.jsonc` with singleton name `"global"` (v1 sharding strategy: one DO instance) and uses the hibernatable WebSocket API (`acceptWebSocket` + `webSocketMessage` / `webSocketClose` handlers) so idle connections do not bill for wall time.
- [ ] **AC-US2-02**: The DO maintains `Map<connId, {ws, installedSkills: string[]}>` where `installedSkills` is the client-provided filter list sent once at connection open; on publish, only clients whose filter contains the event's `skillId` receive the message.
- [ ] **AC-US2-03**: Publish events arriving at the DO from the internal publish endpoint are fanned out within the same DO turn — no queue, no retry — and any dead WebSocket (send throws) is removed from the connection map without blocking the broadcast to remaining live clients.
- [ ] **AC-US2-04**: On client WebSocket close or error, the DO removes the entry from the connection map; after hibernation + wake, the map is restored via `serializeAttachment` so filters survive isolate restarts without requiring client reconnect.
- [ ] **AC-US2-05**: The DO sustains at least 100 concurrent connections in v1 testing (load test in verification plan), with publish-to-fanout latency <50 ms at p95 for a 100-client broadcast.
- [ ] **AC-US2-06**: Unit tests (via Miniflare) assert: (a) an event published for `skillId="A"` reaches only clients whose filter contains `"A"`; (b) hibernation + wake preserves each client's filter; (c) a dead socket is removed on next publish without throwing.

---

### US-003: Public SSE endpoint + filtered fan-out + internal publish (P1)
**Project**: vskill-platform

**As a** Skill Studio developer
**I want** to subscribe via `EventSource` to a public SSE endpoint that streams only events for skills I have installed, with auto-reconnect and keepalives
**So that** I receive updates live without polling, and my connection survives transient network blips and idle proxy closures

**Acceptance Criteria**:
- [ ] **AC-US3-01**: A public endpoint `GET /api/v1/skills/stream?skills=<csv>` streams `text/event-stream` responses; no caller auth required (public read is intentional for v1), but `skills` query param is required and is forwarded to the `UpdateHub` DO as the client's installed-skill filter list on connection open.
- [ ] **AC-US3-02**: The endpoint sends a `:keepalive` comment frame every 25 seconds so intermediate proxies (Cloudflare, corporate) do not idle-close the connection; `EventSource` in the browser auto-reconnects on any transport error using its built-in backoff.
- [ ] **AC-US3-03**: An internal publish endpoint `POST /api/v1/internal/skills/publish` requires header `X-Internal-Key: <hmac>` matching secret `INTERNAL_BROADCAST_KEY` via the existing timing-safe compare in `src/lib/webhook-auth.ts`; unauthorized calls return HTTP 401 with zero side effects.
- [ ] **AC-US3-04**: The internal publish payload `{type: "skill.updated", skillId, version, diffSummary?, publishedAt}` is forwarded verbatim to the `UpdateHub` DO via stub RPC; the publish request returns HTTP 202 once the DO has accepted the event (fire-and-forget fan-out).
- [ ] **AC-US3-05**: Events delivered over the SSE stream are framed as `event: skill.updated\ndata: <json>\n\n` with one JSON object per frame; clients can subscribe via `EventSource.addEventListener("skill.updated", handler)`.
- [ ] **AC-US3-06**: End-to-end integration test: scanner mock-publishes an update for `skillId="X"`; a test SSE client subscribed with `skills=X` receives the event within 2 seconds; a second client subscribed with `skills=Y` does NOT receive it.
- [ ] **AC-US3-07** (publish idempotency): `POST /api/v1/internal/skills/publish` accepts an `eventId` in the payload and is idempotent on it — the `UpdateHub` DO maintains an in-memory replay log of `Map<eventId, {event, expiresAt}>` with a 5-minute TTL; if an `eventId` is seen a second time within the window, the DO fans out to any new subscribers but does NOT re-broadcast to already-delivered clients. Returns HTTP 202 either way.
- [ ] **AC-US3-08** (Last-Event-ID replay): The SSE endpoint honors the standard `Last-Event-ID` request header on reconnect; the `UpdateHub` replays every event from its in-memory log whose `eventId` is newer than the header value and whose `skillId` matches the caller's subscription filter, then resumes live. Each SSE frame emitted by the endpoint carries an `id:` field equal to the event's `eventId` so the browser's `EventSource` sets `Last-Event-ID` automatically on reconnect.
- [ ] **AC-US3-09** (gone frame): If a reconnecting client presents a `Last-Event-ID` that is older than the DO's 5-minute replay window (no longer resident), the endpoint sends a single `event: gone\ndata: {"reason": "replay-window-expired"}\n\n` frame before streaming live events, signaling the client to reconcile via `GET /api/v1/skills/check-updates` rather than assume no events were missed.

---

### US-004: GitHub webhook fast-path for first-party repos (P1)
**Project**: vskill-platform

**As a** first-party repo maintainer
**I want** a push to my default branch to propagate to every connected Skill Studio tab within ~1 second via a signed GitHub webhook
**So that** my updates feel instant for first-party content, instead of waiting up to 10 minutes for the next scanner cycle

**Acceptance Criteria**:
- [ ] **AC-US4-01**: A webhook endpoint `POST /api/v1/webhooks/github` verifies the `X-Hub-Signature-256` header against Cloudflare secret `GITHUB_WEBHOOK_SECRET` using HMAC-SHA256 timing-safe compare (via existing `src/lib/webhook-auth.ts`); unsigned, missing-signature, or mismatched-signature requests return HTTP 401 with zero side effects.
- [ ] **AC-US4-02**: On a valid `push` event whose branch matches the targeted `Skill.sourceBranch` for a tracked repo, the webhook triggers the scanner logic **scoped to that single Skill row** (not the full batch) — reusing the same `SkillVersion` upsert + publish path as the scheduled scanner.
- [ ] **AC-US4-03**: Pushes to branches that do not match any tracked `Skill.sourceBranch` for that repo, and pushes to repos that have no `Skill.sourceRepoUrl` match, are acknowledged (HTTP 204) but perform no scanner work.
- [ ] **AC-US4-04**: End-to-end latency from webhook receipt to SSE fan-out completion is <1 second at p95 under the 100-client load target, measured in integration test with a real (Miniflare) DO and a mock GitHub payload.
- [ ] **AC-US4-05**: Webhook replays (same `X-GitHub-Delivery` UUID seen within 5 minutes) are suppressed via KV anti-replay using the existing pattern in `src/lib/webhook-auth.ts`; the second delivery returns HTTP 200 with no publish side effect.

---

### US-005: Skill Studio live update UI (P1) — supersedes 0683
**Project**: vskill

**As a** Skill Studio developer
**I want** an "Update available" cue that appears live when I have the Studio open — a toast when the tab is foreground, a silent badge when it's in the background — and a 5-minute polling fallback if `EventSource` is blocked
**So that** I learn about updates without refreshing, and the UI stays non-disruptive when I'm not actively looking at it

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A `useSkillUpdates()` React hook opens a single `EventSource` against `/api/v1/skills/stream?skills=<installed-skills>` on Studio mount, listens for `skill.updated` events, dispatches to a shared update store keyed by `skillId`, handles `EventSource.onerror` by letting the browser auto-reconnect (no custom backoff), and exposes a `status: "connecting" | "connected" | "fallback"` signal.
- [ ] **AC-US5-02**: When `document.visibilityState === "visible"` at the moment an update arrives, an accessible toast (`role="status"`, `aria-live="polite"`) appears for 4 seconds with the skill name, version, and a "View changes" link; when `visibilityState === "hidden"`, no toast fires — only the UpdateBell badge increments silently.
- [ ] **AC-US5-03**: The UpdateBell in TopRail shows an unread count (number of skills with pending updates since last dismiss); clicking it opens a dropdown listing each updated skill with its `diffSummary` and a "View changes" action — this replaces the equivalent UI originally planned for 0683. The badge carries an `aria-label` communicating the unread count.
- [ ] **AC-US5-04**: SkillRow in the SidebarSection and the active RightPanel both show a small "update available" indicator (blue dot + tooltip with the new version) for any skill present in the update store; indicator clears when the user invokes the "View changes" action or when a subsequent `vskill update` on that skill succeeds.
- [ ] **AC-US5-05**: If `EventSource` is unavailable (blocked by CSP, enterprise proxy, polyfill absent) or the connection fails for more than 60 seconds, the hook transparently falls back to polling `GET /api/v1/skills/check-updates?skills=<csv>` every 5 minutes and sets `status: "fallback"`; the UI does not differentiate visually, only the status signal is exposed for debugging.
- [ ] **AC-US5-06**: Increment 0683 is marked **superseded by 0708** in its `metadata.json`; any stub files or planning notes from 0683 are removed or redirected to 0708's components. The 5-minute polling path originally planned for 0683 is implemented here only as the fallback branch of `useSkillUpdates()`, not the primary.
- [ ] **AC-US5-07**: `useSkillUpdates()` unit tests cover: (a) event arrival while `visible` fires toast + increments badge; (b) event arrival while `hidden` increments badge without firing toast; (c) `onerror` triggers reconnect without losing the installed-skill filter; (d) >60 s disconnect flips to poll mode and sets `status: "fallback"`.
- [ ] **AC-US5-08**: The SSE subscription filter is scoped to the user's installed-skill list at the moment `EventSource` connects. The `UpdateHub` only broadcasts events whose `skillId` is in that filter list — events for other skills never reach the user's browser. This prevents unnecessary browser work, wake-from-sleep, and network traffic for skills the user does not have installed.
- [ ] **AC-US5-09**: Skill Studio renders a subtle "not tracked for updates" indicator (dim gray status dot + hover tooltip reading "Not tracked — run `vskill outdated` manually") on each installed skill whose upstream repo URL is NOT present in the `Skill.sourceRepoUrl` tracked catalog on the server. The indicator is persistent (no dismiss affordance) and MUST be visually quieter than the "update available" indicator (AC-US5-04) — no toast, no bell increment, no color that reads as a warning. It communicates "live updates unavailable for this skill" without suggesting anything is broken.
- [ ] **AC-US5-10** (client-side dedup): `useSkillUpdates()` maintains a `seenEventIds: Set<string>` with a FIFO capacity of 500 entries and persists the most recent event's `eventId` as `seenLastId` in `localStorage`. On each incoming SSE event, the hook checks `seenEventIds` before dispatching to the update store; duplicates (which can arise from reconnect replay) are silently dropped. On `EventSource` reconnect, the browser automatically sends `Last-Event-ID: <seenLastId>` so the server can replay from that point.
- [ ] **AC-US5-11** (gone-frame reconciliation): When the hook receives an `event: gone` frame (AC-US3-09), it clears its `seenEventIds` set, issues a one-shot `GET /api/v1/skills/check-updates?skills=<csv>` to reconcile state, merges any updates returned into the update store, and then resumes consuming live SSE events. The reconciliation is silent (no toast, no error banner) — the user should not observe the `gone` transition.

---

### US-006: Skill discovery + `sourceRepoUrl` resolver + user registration (P1)
**Project**: vskill-platform

**As a** platform operator and Skill Studio developer
**I want** the platform to auto-discover `sourceRepoUrl` for installed skills that don't yet have one recorded, and let users manually register a source repo for skills where discovery fails
**So that** the catalog self-heals over time and users can opt legacy or hand-authored skills into the update pipeline without DB access

**Acceptance Criteria**:
- [ ] **AC-US6-01** (discovery trigger): When `GET /api/v1/skills/check-updates` is called with skill IDs whose `Skill.sourceRepoUrl IS NULL`, the endpoint enqueues a `discovery-resolve` job to the `scan-normal` queue (US-007) for each such skill, subject to a per-skill backoff schedule stored in `Skill.resolutionBackoffStep`: attempt 1 immediate, then 1h, 6h, 24h, 72h, then stop. Subsequent `/check-updates` calls do NOT re-enqueue a skill whose next-attempt time has not yet elapsed.
- [ ] **AC-US6-02** (resolver logic): The resolver fetches the skill's current `SKILL.md` content and parses its frontmatter for a `repository:` field (YAML string). On match it writes `Skill.sourceRepoUrl`, `Skill.sourceBranch` (default `"main"` if absent), and sets `Skill.resolutionState = "resolved"`. On no-match it sets `Skill.resolutionState = "unresolvable"` and advances `resolutionBackoffStep`. After five consecutive unresolved attempts, `resolutionState` stays `"unresolvable"` and no further discovery jobs are enqueued.
- [ ] **AC-US6-03** (`/check-updates` response shape): The endpoint's response includes, per skill in the result list, two fields: `trackedForUpdates: boolean` (true iff `Skill.sourceRepoUrl IS NOT NULL`) and `resolutionState: "resolved" | "unresolvable" | "user-registered" | null` (null if no resolver attempt has been made yet).
- [ ] **AC-US6-04** (user-registration endpoint): `POST /api/v1/skills/:id/register-tracking` accepts body `{repoUrl: string, branch?: string}`, rate-limited to 10 requests per hour per session (via KV-tracked `registration-rl:<sessionId>`), and before writing verifies that fetching `SKILL.md` at `<repoUrl>/<branch>/SKILL.md` (or a skill-specific path if the skill is a nested directory) produces content whose content-hash matches `Skill.contentHash`. Mismatch returns HTTP 409 with `{error: "content-hash-mismatch"}` and writes nothing; match writes `sourceRepoUrl`, `sourceBranch` (default `"main"`), and `resolutionState = "user-registered"`.
- [ ] **AC-US6-05** (schema additions): The Prisma migration from AC-US1-05 additionally adds `Skill.resolutionState: String?` and `Skill.resolutionBackoffStep: Int @default(0)` columns. No separate discovery table — state is tracked per-skill.
- [ ] **AC-US6-06** (respects provenance): If a skill's `.vskill-meta.json` sidecar (from 0688) indicates `origin !== "upstream"`, discovery is skipped — `resolutionState` stays null and no job is enqueued. Locally-authored skills should never be auto-tracked.

---

### US-007: Unified scanner queue (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** every GitHub scan path (webhook, user-trigger, cron, discovery) to flow through a single queue consumer with dedup and rate-limit guards
**So that** the platform has one chokepoint that can be tuned, observed, and protected from accidentally exhausting the GitHub rate limit

**Acceptance Criteria**:
- [ ] **AC-US7-01** (single consumer): A `queue-consumer.ts` worker is the **only** code path that issues outbound `GET /repos/:owner/:repo/commits/:branch` calls in production. All four scan triggers (webhook from US-004, user check-now from US-008, cron from US-001, discovery-resolve from US-006) enqueue scan jobs rather than calling GitHub directly; no direct GitHub fetch is permitted outside `queue-consumer.ts`. An architecture test (grep-based or AST-based) in CI enforces this invariant.
- [ ] **AC-US7-02** (queue split): Two Cloudflare Queues are bound: `scan-high` (webhook + user-trigger sources, target latency <1s from enqueue to consume) and `scan-normal` (cron + discovery sources, target latency <30s). Job payload shape: `{source: "webhook" | "user-trigger" | "cron" | "discovery", skillId, forceRefresh: boolean, requestId: string}`.
- [ ] **AC-US7-03** (dedup lock): The consumer, before processing a job, checks KV key `scan-lock:<skillId>` with a 30-second TTL. If present, the job is dropped as a duplicate (counter `queue.dedup.dropped` incremented); if absent, the consumer writes the lock and proceeds. Jobs with `forceRefresh === true` (user-trigger only) bypass the lock read AND overwrite it.
- [ ] **AC-US7-04** (rate-limit guard): The consumer reads `github-rl:remaining` from KV (updated by each GitHub response's `X-RateLimit-Remaining` header) before every GitHub call. When `remaining < 500`, jobs with `source === "cron"` or `source === "discovery"` are dropped (metric `queue.rl-guard.dropped`) while jobs with `source === "webhook"` or `source === "user-trigger"` are always served — the guard never starves user-facing paths.
- [ ] **AC-US7-05** (cron publishes a batch): The 10-minute cron trigger from US-001 does NOT call GitHub directly. It selects the top 100 `Skill` rows by `lastCheckedAt ASC NULLS FIRST`, enqueues one `{source: "cron", skillId, forceRefresh: false, requestId}` job per skill to `scan-normal`, and exits. Actual GitHub fetches happen in the consumer.
- [ ] **AC-US7-06** (observability): The consumer emits `queue.jobs.consumed`, `queue.dedup.dropped`, `queue.rl-guard.dropped`, `queue.duration.ms` metrics per job with a `source` dimension so cron/webhook/user-trigger/discovery paths can be analyzed independently.

---

### US-008: User-initiated "Check now" rescan (P2)
**Project**: vskill-platform (endpoint) + vskill (Studio UI button)

**As a** Skill Studio developer
**I want** a "Check now" button on any tracked skill that forces an immediate upstream rescan and reports back via the existing SSE stream
**So that** I can verify an upstream update is reflected without waiting for the next cron tick, with feedback in the same UI I already use

**Acceptance Criteria**:
- [ ] **AC-US8-01** (endpoint): `POST /api/v1/skills/:id/rescan` enqueues a `{source: "user-trigger", skillId, forceRefresh: true, requestId}` job to `scan-high` and returns HTTP 202 with body `{jobId: requestId}`. Rate-limited to 10 requests per minute per session via KV `rescan-rl:<sessionId>`; 11th request in the window returns HTTP 429 with `Retry-After` header.
- [ ] **AC-US8-02** (result via existing SSE): The rescan result arrives at the Studio client via the **same** `/api/v1/skills/stream` SSE channel the user is already subscribed to — if a new `SkillVersion` is created, a `skill.updated` event fires; if the SHA is unchanged, no event fires. No separate "rescan-complete" event type is introduced.
- [ ] **AC-US8-03** (Studio UI): The Studio RightPanel shows a "Check now" button for any skill where `trackedForUpdates === true` (per AC-US6-03). Clicking it disables the button, shows a spinner, and records the `jobId` returned. The spinner clears (a) when a `skill.updated` event matching the skill's ID arrives on SSE, or (b) after a 30-second timeout with no event, whichever comes first. The timeout case shows a small "No changes detected" tooltip (not a toast, not an error).
- [ ] **AC-US8-04** (button hidden on untracked): The "Check now" button is NOT rendered for skills with `trackedForUpdates === false` — those skills show the AC-US5-09 "not tracked" indicator instead. If the skill is in discovery backoff (US-006), the button is also hidden to avoid confusing users about why it's not firing.
- [ ] **AC-US8-05** (observability): `user.rescan.triggered` metric incremented per rescan request with a `resultWithin30s: boolean` dimension set from the spinner-clear outcome.

---

### US-009: End-to-end delivery guarantee (P1) — cross-cutting
**Project**: vskill-platform + vskill

**As a** platform operator
**I want** every `SkillVersion` write to produce a client-delivered event with at-least-once semantics
**So that** no upstream update is silently dropped between the DB commit and the Studio UI, and the delivery SLO is an independently-verifiable first-class concern rather than a side-effect of five other stories

This is a **cross-cutting guarantee** realized by the three-layer mechanism distributed across US-001 (outbox write + reconciler), US-003 (DO idempotency + `Last-Event-ID` replay + `gone` frame), and US-005 (client dedup + gone-frame reconcile). US-009 makes that guarantee a named story with its own sign-off checklist and SLO so it cannot be implicitly waived when the individual ACs pass in isolation.

**Acceptance Criteria**:
- [ ] **AC-US9-01** (outbox write — tied to AC-US1-08): Every `SkillVersion` insert across every code path (scanner, webhook fast-path, user rescan, submission processing, admin republish) commits in a single DB transaction with its paired `UpdateEvent` row. The transactional-pair invariant is enforced by a repository-layer helper (`writeSkillVersionWithEvent()`) that all call sites MUST use — a CI architecture test forbids raw `prisma.skillVersion.create()` outside that helper.
- [ ] **AC-US9-02** (reconciler — tied to AC-US1-09): The `outbox-reconciler` runs every 30 s, retries `UpdateEvent` rows with `publishedAt IS NULL AND createdAt < NOW() - 10s`, caps attempts at 10, and emits the `delivery.outbox.stuck` AE metric at WARN level for any row unpublished more than 5 minutes (feeds NFR-RELIABILITY-02).
- [ ] **AC-US9-03** (publish idempotency — tied to AC-US3-07): `POST /api/v1/internal/skills/publish` is idempotent on `eventId`; duplicate sends (from reconciler retries or at-least-once queue redelivery) return HTTP 202 and MUST NOT cause the DO to re-broadcast to clients that have already received the event within the 5-minute replay window.
- [ ] **AC-US9-04** (reconnect replay — tied to AC-US3-08, AC-US3-09): The SSE endpoint honors `Last-Event-ID`. On reconnect within the 5-minute window, a client receives every missed event matching its subscription filter. On reconnect outside the window, the client receives exactly one `event: gone` frame and then resumes live — the server never silently drops events without telling the client.
- [ ] **AC-US9-05** (client dedup — tied to AC-US5-10, AC-US5-11): The Studio hook dedups on `eventId` via a 500-capacity FIFO `Set`, persists the latest `eventId` in `localStorage`, and handles `event: gone` by silently reconciling via `/check-updates`. The user MUST NEVER see a double-rendered update card, a duplicate toast, or an error banner during normal delivery or reconnect.
- [ ] **AC-US9-06** (end-to-end SLO — ties to NFR-RELIABILITY-01): The `delivery.end-to-end.ms` AE metric, computed as `UpdateEvent.publishedAt - UpdateEvent.createdAt` for every successfully-delivered event, has a p99 ≤10 seconds measured over any rolling 24-hour window. Breaching this SLO in production is an incident (not a warning) and blocks increment-closure sign-off until either root-caused or formally accepted.
- [ ] **AC-US9-07** (at-least-once contract is explicit): The v1 delivery contract is **at-least-once + client-side dedup**, NOT exactly-once. This is documented in the living-docs SSE protocol reference so downstream consumers do not assume stronger semantics. Exactly-once is explicitly out of scope (see Out of Scope).

## Functional Requirements

### FR-001: Scanner cadence and GitHub rate-limit envelope
Scanner runs every 10 minutes (Cron Trigger `*/10 * * * *`). At the v1 scale target of 100 tracked skills × 1 GitHub request per cycle = 600 requests/hour — 12% of the fine-grained PAT rate limit (5,000 requests/hour).

### FR-002: Durable Object sharding
Single `UpdateHub` DO instance (`name="global"`) for v1. Shard-per-skill DO is explicitly deferred (see Out of Scope) until telemetry shows single-DO CPU or connection pressure warrants it.

### FR-003: Secrets management
All cryptographic material stored as Cloudflare Worker secrets (never in source or `wrangler.jsonc`), with a `.dev.vars`-based local-dev tier:
- `GITHUB_TOKEN` — fine-grained PAT, `public_repo` read scope only, anton-abyzov personal account
- `GITHUB_WEBHOOK_SECRET` — HMAC key for `X-Hub-Signature-256` verification
- `INTERNAL_BROADCAST_KEY` — HMAC key for `POST /api/v1/internal/skills/publish` (reused, not a new secret)

### FR-004: Binary delivery
This increment does NOT introduce a new tarball serving path. Clients fetch tarballs through the existing `/api/v1/skills/:name/versions/:ver/tarball` endpoint referenced by the `SkillVersion` rows the scanner creates. Pre-signed R2 URLs are explicitly out of scope.

### FR-005: Storage schema
Four nullable columns are added to the existing `Skill` Prisma model — `sourceRepoUrl`, `sourceBranch`, `lastSeenSha`, `lastCheckedAt` — plus two discovery-state columns from US-006: `resolutionState`, `resolutionBackoffStep`. One new model `UpdateEvent` (AC-US1-10) is added for the outbox pattern. No separate `TrackedSkillSource` table is introduced in v1 (avoids join overhead at 100-skill scale).

### FR-006: Backward compatibility with existing SSE infrastructure
The new `/api/v1/skills/stream` endpoint does NOT modify or interfere with the existing `/api/v1/submissions/stream` endpoint or the in-memory `src/lib/event-bus.ts`. The new code path is independent and runs alongside the existing infrastructure.

### FR-007: Delivery guarantee (transactional outbox)
Every `SkillVersion` write — from scanner (US-001), webhook fast-path (US-004), user rescan (US-008), submission processing, or admin republish — produces a transactionally-paired `UpdateEvent` row. The `outbox-reconciler` (AC-US1-09) retries any row whose `publishedAt` is still null 10 seconds after creation. The `UpdateHub` DO dedups on `eventId` (AC-US3-07) so retries cannot double-deliver. Clients dedup on the same `eventId` (AC-US5-10) as a third line of defense. This provides the end-to-end guarantee codified in NFR-007.

### FR-008: Single-consumer queue discipline
All outbound GitHub scan calls flow through `queue-consumer.ts` (US-007). No code path outside the consumer may call `GET /repos/:owner/:repo/commits/:branch` in production. The consumer's dedup lock (`scan-lock:<skillId>`) and rate-limit guard (`github-rl:remaining`) are the two chokepoints that keep the platform's GitHub budget predictable.

### FR-009: Discovery & user registration endpoints
`/check-updates` acts as both a reconciliation endpoint (AC-US5-11) and a discovery trigger (AC-US6-01). The `POST /skills/:id/register-tracking` endpoint (AC-US6-04) provides a user-facing escape hatch for skills whose frontmatter discovery fails. Both endpoints are additive — they do not change existing `/check-updates` behavior for skills that already have `sourceRepoUrl` populated.

## Success Criteria

- Skill Studio badge appears within 2 seconds of scanner detecting an update (integration test).
- Webhook-triggered updates reach the SSE stream within 1 second at p95 (load test).
- Zero false-positive updates for skills with locally-promoted provenance (0688 suppression integration).
- 100 concurrent SSE clients sustained with publish-to-fanout p95 <50 ms at the DO layer.
- Marginal monthly cost stays in the $5–15 band at v1 scale.
- Increment 0683's planned UI lands here via SSE; 0683's polling implementation is avoided entirely.
- **End-to-end delivery guarantee: ≥99% of `SkillVersion` writes produce a delivered client event within 10s at p99** (NFR-007), measured by `delivery.end-to-end.ms`.
- **Single-consumer invariant**: no code path outside `queue-consumer.ts` issues outbound GitHub commit lookups; CI architecture test passes.
- **Self-healing catalog**: skills with null `sourceRepoUrl` get a resolver attempt on the first `/check-updates` call and, within one backoff cycle (up to 72h), either become `"resolved"` or `"unresolvable"`; users have a working `register-tracking` escape hatch for the latter.

## Out of Scope

- **`vskill watch` CLI daemon** — dropped per user decision (2026-04-24); Skill Studio UI is the sole consumer of the SSE stream v1. Any future CLI daemon will be a separate increment.
- **Pre-signed R2 tarball URLs** — clients keep using the existing `/versions/:ver/tarball` HTTP path.
- **Shard-per-skill Durable Object** — v1 uses a single `"global"` DO; sharding becomes a separate increment when telemetry justifies it.
- **Anthropic Managed Agents** for classification/changelog generation — `diffSummary` is computed from the GitHub commit payload only; richer summarization is a later increment.
- **GCP / non-Cloudflare infrastructure** — every component lives on Cloudflare Workers (Scheduled Workers, Durable Objects, D1, KV, Analytics Engine), consistent with the platform's cost posture.
- **macOS/Windows native notifications** — no system-tray or OS notification surface; the Studio UI toast and badge are the only surfaces.
- **SSE endpoint authentication / per-user filtered streams with auth** — public read is intentional for v1.
- **Separate `TrackedSkillSource` table** — v1 adds columns on `Skill` instead; a normalized table can come later if one-skill-to-many-sources is needed.
- **Studio admin UI for registering tracked repos** — seed script only in v1.
- **Pagination, chunking, or per-user rate-limiting on the SSE stream** — the stream is a server-filtered push channel, not a query result set. No "page 2", no tier-based caps, no user-visible "waiting" state. See NFR-001a.
- **Per-user caps on installed-skill count** — a user may install any number of skills locally; the subscription filter at `EventSource` connect is simply the list they have installed.
- **Manual admin UI for listing/registering tracked skills** — v1 uses a curated seed script (AC-US1-05) plus reactive discovery (US-006) plus the per-skill user-registration endpoint (AC-US6-04); no aggregate admin console in v1.
- **Observability dashboard** — every metric called out in the ACs (scanner, DO, queue, delivery, outbox, discovery, rescan) emits to Cloudflare Analytics Engine, but v1 ships no bespoke dashboard UI. Operators query AE directly.
- **Exactly-once delivery semantics** — v1 contracts on **at-least-once + client-side dedup** (AC-US9-07). Exactly-once would require per-client acknowledgment state at the DO layer and is explicitly deferred.

## Dependencies

- **0688 studio-skill-scope-transfer (CLOSED)** — US-001 depends on 0688's `.vskill-meta.json` provenance sidecar format to suppress scope-transfer-triggered false updates (AC-US1-04).
- **0683 studio-update-notifications (PLANNED) — SUPERSEDED by 0708.** 0683's UpdateBell, SkillRow indicator, and sidebar chip components are absorbed into US-005 and fed from SSE instead of 0683's original 5-minute poll. 0683's `metadata.json` MUST be flipped to `status: superseded` as part of this increment's delivery.
- **0687 queue-truthful-load (12/13)** — low-risk coupling; US-001 scanner should use a distinct KV key prefix (`skill-updates:*`) to avoid collision with the queue's `queue:*` prefix.

## Non-functional Requirements

### NFR-001: Scale targets (v1) — platform-wide
- 100 tracked upstream skill repositories **platform-wide** (catalog total, not per user)
- 100 concurrent SSE clients **platform-wide** (one connection per open Studio tab across all users)
- Realistic update velocity: ~5 genuine upstream updates per day platform-wide; steady-state stream load should not exceed **1 message per minute per connected user** at peak catalog velocity. Users with large installed lists see no different rate than users with small lists — filtering is server-side.
- No per-user cap on locally installed skills — a user with 500 installed skills and a user with 5 both open exactly one SSE connection with their respective subscription filter.
- Scanner cadence: 10 minutes (cron `*/10 * * * *`)

### NFR-001a: No pagination, ever
The SSE protocol MUST NOT paginate, chunk, or rate-limit updates per user. Filtering is server-side at the `UpdateHub` against the subscription list, so a user's browser only receives events for skills they have installed. The stream is a filtered push channel, not a query result set; future "optimizations" that introduce paging, tier limits, or batching per user are explicitly disallowed by this spec. Catalog scaling is an infrastructure concern (bump cron cadence, shard the DO by skill) that MUST NOT surface as any user-facing "waiting" or "upgrade" state.

### NFR-002: Staleness SLOs
- Webhook path: <1 second from GitHub webhook receipt to SSE fan-out completion at p95 (first-party repos)
- Poll path: <10 minutes from upstream push to SSE fan-out (third-party repos, e.g. `anthropic-skills/*`)
- DO publish → Studio badge render: <2 seconds at p95

### NFR-003: Cost envelope
Marginal monthly cost $5–15 at v1 scale, driven by: Scheduled Worker invocations (~4,320/month at 10-min cadence), DO wall time (minimized by hibernation), D1 writes (≤1 row per genuine upstream update), KV reads/writes for anti-replay.

### NFR-004: Reliability
- Scanner per-row error isolation (one bad repo does not abort the batch)
- SSE auto-reconnect via browser `EventSource` default behavior
- 5-minute polling fallback when `EventSource` fails for >60 seconds
- Webhook anti-replay via KV-tracked `X-GitHub-Delivery` UUIDs
- DO hibernation + wake preserves connection map via `serializeAttachment`

### NFR-005: Security
- All secrets in Cloudflare Worker secrets store (none in source or wrangler config)
- HMAC timing-safe compare on every internal and webhook authentication path
- `GITHUB_TOKEN` minimum-privilege: fine-grained PAT with `public_repo` read scope only
- SSE events are strict JSON — no HTML, no injection surface
- Scope-transfer provenance suppression prevents false-positive updates for locally-promoted skills

### NFR-006: Observability
Structured metrics on scanner runs, DO fan-out, webhook receipts, SSE connection counts, fallback rate, queue job consumption (per-source), dedup drops, rate-limit guard drops, outbox reconciler retries, discovery attempts, and user rescan outcomes — all queryable via Cloudflare Analytics Engine.

### NFR-007 / NFR-RELIABILITY-01: End-to-end delivery SLO
At least **99% of `SkillVersion` writes MUST produce a delivered client event within 10 seconds at p99**, measured via the `delivery.end-to-end.ms` Analytics Engine metric where `delivery.end-to-end.ms = <timestamp of first client onmessage> − UpdateEvent.createdAt` for every successfully-delivered row. The three-layer mechanism (transactional outbox write, outbox reconciler retry, DO + client event-ID dedup) exists specifically to back this SLO; regressions below 99% at p99 are treated as incidents, not warnings. (NFR-007 is an alias for NFR-RELIABILITY-01 — both IDs refer to the same SLO.)

### NFR-RELIABILITY-02: Outbox backstop
No `UpdateEvent` row shall remain unpublished for more than 5 minutes. The `outbox-reconciler` (AC-US1-09, AC-US9-02) is the backstop that enforces this: it retries every 30 s, caps at 10 attempts, and fires the `delivery.outbox.stuck` AE metric at WARN level for any row that exceeds the 5-minute ceiling. Persistent breaches of NFR-RELIABILITY-02 are themselves incidents even when NFR-RELIABILITY-01's end-to-end SLO is otherwise met — a stuck row is a future SLO breach waiting to happen.

## Traceability (story ↔ interview decision)

| User story | Covers interview decision |
|---|---|
| US-001 | Q1 (GitHub PAT auth), Q2 (Skill-column seed strategy), scanner cadence, 0688 provenance suppression |
| US-002 | Architecture DO decision, single-global-shard v1 choice |
| US-003 | SSE transport + reuse of existing `INTERNAL_BROADCAST_KEY` HMAC pattern |
| US-004 | Q3 (webhook secret storage), webhook fast-path scope (first-party only), <1 s SLO |
| US-005 | Q5 (foreground toast + badge / background silent badge), supersedes 0683 with SSE-fed UI, platform-wide scale model (AC-US5-08 server-side filter, AC-US5-09 untracked indicator); delivery guarantee client side (AC-US5-10 dedup, AC-US5-11 gone-frame reconcile) |
| US-006 | Architect §Skill Discovery & Registration — `/check-updates` enqueues discovery under backoff, resolver reads frontmatter, user-registration endpoint with content-hash verify and 10/hr rate limit |
| US-007 | Architect §Unified Scanner Queue — single consumer, scan-high/scan-normal split, 30s dedup lock, rate-limit guard protects user paths, cron publishes batch instead of scanning directly |
| US-008 | Architect §Skill Discovery & Registration (user check-now) + delivery guarantee — result arrives via existing SSE, 10/min session rate limit, 30s spinner timeout |
| US-001 / US-003 / US-005 delivery ACs | Architect §Delivery Guarantee — transactional outbox write (AC-US1-08/09/10), DO idempotency + Last-Event-ID replay + gone frame (AC-US3-07/08/09), client dedup + reconcile (AC-US5-10/11), 99% @ 10s p99 SLO (NFR-007 / NFR-RELIABILITY-01) |
| US-009 | Cross-cutting consolidation of the delivery-guarantee ACs above; ties them to NFR-RELIABILITY-01 (end-to-end SLO) + NFR-RELIABILITY-02 (outbox backstop) + at-least-once contract documentation. Own sign-off checklist so guarantee cannot be implicitly waived when component ACs pass in isolation. |
