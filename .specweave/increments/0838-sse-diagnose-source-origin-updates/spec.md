---
increment: 0838-sse-diagnose-source-origin-updates
title: 'Skill Studio: SSE diagnose mode + source-origin update tracking'
type: feature
priority: P0
status: completed
project: vskill
created: 2026-05-09T18:33:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
parent_scope: vskill-redesign-around-login
---

# Feature: SSE diagnose mode + source-origin update tracking

## Overview

The Skill Studio macOS desktop app does not surface SSE update toasts to the
user, despite the SSE wiring being correct end-to-end and the production
endpoint being healthy. Three independent failure modes have been confirmed by
research (`researcher-sse-desktop`, 2026-05-09) and reproduced against the
live `https://verified-skill.com/api/v1/skills/stream` endpoint:

1. **Source-origin skills are excluded from the SSE filter.** The browser-side
   consumer (`useSkillUpdates.ts`) only opens an `EventSource` when at least
   one installed skill resolves to a UUID or slug
   (`utils/resolveSubscriptionIds.ts:51`). Locally-authored skills
   (`origin === "source"`) and plugin-bundled skills without a published
   registry entry are filtered out — so a Studio whose installed-skill list is
   100% source-origin never opens an `EventSource` at all.
2. **Source-origin skills are excluded from polling.** `/api/skills/updates`
   walks `vskill.lock`; source-origin skills have no lockfile entry, so the
   polling fallback never produces an update record either. The bell counter
   stays at zero even after a publish.
3. **Visibility-gated toast suppression silently drops events.** The
   `EventSource` `onmessage` handler dispatches `studio:toast` only when
   `document.visibilityState === "visible"`. If the window is backgrounded at
   the moment the event lands, the bell counter increments but no toast is
   ever shown — and there is no replay on the next `visibilitychange`. Users
   who multitask through long publishes lose every toast.

There is also no in-app affordance to tell which of these branches is firing.
A user reporting "I never see updates" cannot distinguish between (a) the
EventSource never opening, (b) the EventSource opening but reconnecting, (c)
the polling fallback running but producing zero results, or (d) toasts being
suppressed by visibility. The bell tooltip currently surfaces only one signal
(`usePlatformHealth().degraded`), which is upstream-platform health — not
local SSE health.

This increment ships:

- A user-facing SSE diagnostic surface (status indicator + debug logging) so
  the failing branch can be identified in <60s with DevTools open.
- Source-origin update tracking across both polling and SSE so locally
  authored skills with a published registry twin produce toasts and bell
  updates the same way installed skills do.
- A bounded toast queue across visibility transitions so backgrounded users
  do not lose update notifications.
- Distinct color-coded status in the bell tooltip ("connected | reconnecting
  | offline").
- Per-session telemetry pings so SSE health regressions are visible at the
  fleet level.

Out of scope: Tauri auto-updater work, changes to the Cloudflare Worker SSE
producer (already healthy per the researcher run), and any redesign of the
update dropdown body itself.

## Personas

- **End user reporting "I never see updates"** — installed Studio, has at
  least one source-origin or installed skill, may multitask between Studio
  and other apps. Wants to know whether updates are working without filing
  a bug.
- **Skill author working on locally-authored skills** — runs `vskill studio`
  on a project containing source-origin skills (authored via `SKILL.md`,
  never `vskill install`-ed). Publishes new versions via
  `vskill skill publish`. Expects to see update notifications when the
  registry version surpasses the local version.
- **Studio operator on the platform team** — needs aggregate SSE health
  metrics (open rate, fallback rate, error rate per session) to spot
  regressions before they hit support tickets.

## Scope

### In scope
- Modify `useSkillUpdates.ts` (eval-ui) to surface debug logging behind a
  `VSKILL_DEBUG_SSE=1` flag, queue toasts across visibility transitions,
  emit telemetry on stream lifecycle, and accept a wider tracking list that
  includes source-origin skills.
- Modify `resolveSubscriptionIds.ts` to optionally include source-origin
  skills that match a published-registry skill by `name + author` (or
  whichever stable identity the platform exposes).
- Modify `StudioContext.tsx` to pass source-origin skills through to the
  hook's `trackingSkillIds` list (already partially wired) and to the new
  source-origin matcher.
- Modify `UpdateBell.tsx` to render a 3-state status pip in the tooltip
  (connected | reconnecting | offline) distinct from
  `usePlatformHealth().degraded`.
- Modify `eval-server/platform-proxy.ts` to log proxied SSE requests with
  status code, duration, and the upstream URL behind the debug flag.
- Modify `vskill-platform` `/api/v1/skills/updates` handler so source-origin
  skills with a registry twin appear in polling results.
- Add new endpoint `POST /api/v1/studio/telemetry/sse` accepting
  once-per-session SSE lifecycle events.
- Vitest unit coverage for: `resolveSubscriptionIds` source-origin matching,
  the visibility queue, the status indicator state machine.
- Playwright E2E covering: open Studio with a source-origin skill that has a
  registry twin → trigger publish → assert toast.

### Out of scope
- Tauri auto-updater changes (separate concern; tracked elsewhere).
- Changes to the Cloudflare Worker SSE producer
  (`vskill-platform/src/app/api/v1/skills/stream/route.ts` is healthy per the
  research run; we forward events verbatim).
- Redesign of the update dropdown body / row layouts.
- A native macOS notification path (only in-app toasts are in scope).

## User Stories

### US-001: User-initiated SSE diagnostic mode (P0)
**Project**: vskill

**As a** user reporting "I never see updates"
**I want** a one-click way to verify whether SSE is working
**So that** I can determine in <60 seconds which branch is degraded without
filing a support ticket

**Acceptance Criteria**:
- [x] **AC-US1-01**: Setting `VSKILL_DEBUG_SSE=1` in the environment
  (forwarded to the Studio iframe) OR appending `?debugSse=1` to the Studio
  URL enables verbose `console.debug` logging of every EventSource lifecycle
  event (`open`, `error`, `message`, `gone`, `reconnect-scheduled`,
  `fallback-armed`, `fallback-flipped`). Each log line is prefixed with
  `[sse]` and includes ISO timestamp + relevant event fields.
- [x] **AC-US1-02**: With `VSKILL_DEBUG_SSE=1` active, every proxied SSE
  request through `eval-server/platform-proxy.ts` emits a structured server
  log line: `proxy.sse.start{requestId, upstreamUrl}` on dispatch and
  `proxy.sse.end{requestId, status, durationMs}` on completion. Request IDs
  match those returned to the client via the `X-Request-Id` response header
  so client and server logs can be correlated.
- [x] **AC-US1-03**: When `VSKILL_DEBUG_SSE` is unset (or `0`), the
  `console.debug` logs are silent and `proxy.sse.*` logs revert to the
  pre-existing summary-only level (no per-request logging in production).
  No console output, no perf cost on the hot path.
- [x] **AC-US1-04**: The bell tooltip exposes the current SSE state
  (`status` from `useSkillUpdates`) as plain text, e.g. `Live updates:
  connected` / `reconnecting` / `offline`. The text is keyboard-accessible
  via the tooltip and announced to screen readers via `aria-describedby`.
- [x] **AC-US1-05**: A diagnostic test scenario in the developer notes
  (`docs/internal/runbooks/sse-diagnose.md`) walks through the 60-second
  procedure: open DevTools → enable debug flag → reload → identify failing
  branch from console + tooltip + Network tab.

### US-002: Source-origin update tracking (P0)
**Project**: vskill, vskill-platform

**As a** skill author working on locally-authored skills (`origin=source`)
**I want** update notifications when the upstream registry version surpasses
my local version
**So that** I can pull the published twin without polling the registry by
hand

**Acceptance Criteria**:
- [x] **AC-US2-01**: Source-origin skills with a published registry twin
  (matched by `name + author` derived from `SKILL.md` frontmatter) are
  included in the SSE subscription filter via `resolveSubscriptionIds()` —
  the helper accepts a new `includeSourceOriginMatches: true` option that
  resolves the source skill's identity to a registry UUID/slug via a single
  batch lookup against `/api/v1/skills/lookup-by-name`.
- [x] **AC-US2-02**: `/api/v1/skills/updates` in vskill-platform accepts a
  new `?include=source-origin` query param. When present, source-origin
  skills passed in the request body (with `name`, `author`, `version`) are
  matched against the registry the same way installed skills are, and
  results include `latest`, `updateAvailable`, `versionBump`, and
  `diffSummary` for matched entries.
- [x] **AC-US2-03**: Skills that match no registry twin are silently
  excluded from the response (no error, no 404), matching the existing
  contract for installed skills without a registry entry.
- [x] **AC-US2-04**: When a source-origin skill matches a registry twin and
  the registry version is newer than the local frontmatter version, a toast
  fires (subject to the AC-US3 visibility queue) and the bell counter
  increments — identical user-visible behavior to installed skills.
- [x] **AC-US2-05**: The match key is `name + author` (case-insensitive on
  name; exact on author). SHA-based matching is explicitly out of scope —
  source skills are local working copies, their content hash will diverge
  from the registry by definition.
- [x] **AC-US2-06**: When `vskill.lock` is absent (pure source-origin
  project), polling still runs and produces results for matched skills.
  When `vskill.lock` is present alongside source-origin skills, both code
  paths run and results are merged with installed entries taking precedence
  on `name` collisions.

### US-003: Toast queue across visibility transitions (P0)
**Project**: vskill

**As a** user who multitasks through long publish runs
**I want** to NOT lose update toasts when the Studio window is backgrounded
at the moment of arrival
**So that** I see every update I would have seen if the window had been in
the foreground

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `document.visibilityState === "hidden"` at the
  moment a `skill.updated` SSE event lands, the toast payload (`message`,
  `severity`, `skillId`, `version`, `eventId`) is enqueued to a bounded
  FIFO queue persisted to `localStorage` under key `vskill:toast-queue`.
  The bell counter increments as today (existing behavior preserved).
- [x] **AC-US3-02**: The queue capacity is 10 entries. When full, the
  oldest entry is dropped (FIFO eviction). Drop count is logged via
  `console.debug` when `VSKILL_DEBUG_SSE=1`.
- [x] **AC-US3-03**: On the next `visibilitychange` event with
  `visibilityState === "visible"`, queued entries are replayed at 250ms
  intervals (so they don't pile up as a stack) by dispatching the same
  `studio:toast` CustomEvent the live-event handler dispatches. The queue
  is cleared after replay.
- [x] **AC-US3-04**: Entries older than 30 minutes at replay time are
  dropped silently — they're considered stale and likely already
  reconciled by the polling fallback.
- [x] **AC-US3-05**: Duplicate `eventId` entries in the queue are
  deduplicated against the `seenEventIds` set in `useSkillUpdates` before
  replay, so a queued event already reconciled by polling does not
  double-toast.
- [x] **AC-US3-06**: Queue persistence storage choice is documented in
  `plan.md` ADR-001 (localStorage vs sessionStorage) and verified by a
  multi-window test scenario; default is `localStorage` with per-window
  in-memory dedupe to prevent cross-window double-toasts.

### US-004: Status indicator in bell tooltip (P1)
**Project**: vskill

**As a** user glancing at the bell
**I want** an at-a-glance signal of whether live updates are connected,
reconnecting, or offline
**So that** I notice degraded state before missing an update

**Acceptance Criteria**:
- [x] **AC-US4-01**: The bell renders a 6px colored pip in the bottom-right
  quadrant of the icon (anchored against the badge if both are present).
  Color tokens: green (`var(--status-success-text)`) when
  `status === "connected"`; amber (`var(--color-own)`) when
  `status === "fallback"` (reconnecting); grey (`var(--text-secondary)`)
  when `status === "connecting"` and the watchdog has not yet flipped to
  fallback.
- [x] **AC-US4-02**: The pip is hidden when there are zero installed +
  zero tracked source-origin skills (no SSE attempted, no signal to show).
- [x] **AC-US4-03**: The bell tooltip text appends one of:
  `Live updates: connected` / `Live updates: reconnecting` /
  `Live updates: offline`. Distinct from the existing
  `Update checks paused — verified-skill.com crawler is degraded` tooltip
  used by `usePlatformHealth().degraded`. When BOTH signals are degraded,
  the platform-degraded text takes precedence.
- [x] **AC-US4-04**: The pip and tooltip text are accessible:
  `aria-describedby` links the bell button to the live-updates state, and
  state changes trigger a polite `aria-live` announcement (debounced 500ms
  to avoid spam during reconnect storms).
- [x] **AC-US4-05**: Existing `UpdateBell` test selectors
  (`update-bell`, `update-bell-icon`, `update-bell-badge`) are preserved.
  New selectors: `update-bell-status-pip`, `update-bell-status-text`.

### US-005: Telemetry counter for SSE health (P1)
**Project**: vskill, vskill-platform

**As a** Studio operator on the platform team
**I want** aggregate SSE health metrics across the fleet
**So that** I notice regressions before they hit support tickets

**Acceptance Criteria**:
- [x] **AC-US5-01**: When the EventSource transitions through one of the
  states `connected`, `fallback`, `reconnect-scheduled`, or
  `gone-frame-received`, the hook fires a `POST` to
  `/api/v1/studio/telemetry/sse` with a payload of
  `{ event, sessionId, sourceTier, timestamp, durationSinceOpenMs? }`.
  At most one ping per (event, session) tuple — subsequent transitions of
  the same kind are deduped.
- [x] **AC-US5-02**: `sourceTier` is one of `platform-proxy` (forwarded via
  eval-server, default for `vskill studio`), `direct-browser` (Studio
  served from `verified-skill.com` directly, no proxy), or
  `tauri-native` (placeholder for future native EventSource). The current
  default is `platform-proxy`.
- [x] **AC-US5-03**: `sessionId` is generated client-side as a v4 UUID at
  Studio boot, persisted to `sessionStorage` for the duration of the tab.
  No PII is sent — no skill IDs, no user identifiers, no message content.
- [x] **AC-US5-04**: The telemetry endpoint is a thin Worker handler that
  writes to a Cloudflare Analytics Engine dataset
  (`STUDIO_SSE_TELEMETRY`). Failures (4xx, 5xx, network) are swallowed
  silently — telemetry never blocks the user-visible SSE path.
- [x] **AC-US5-05**: A user-visible opt-out flag `VSKILL_DISABLE_TELEMETRY=1`
  (env or `?disableTelemetry=1` query param) suppresses all telemetry
  pings. The opt-out is documented in the runbook from AC-US1-05.

## Non-functional Requirements

- **Performance**: The visibility-queue replay must not block the main
  thread for >16ms across all 10 entries. Dispatch is async + spaced.
- **Privacy**: Telemetry payloads contain no skill IDs, no user IDs, no URLs
  beyond a fixed enum of source-tier values.
- **Backward compatibility**: All existing tests in
  `src/eval-ui/src/__tests__/StudioContext.*.test.tsx` and
  `src/eval-ui/src/components/__tests__/UpdateBell*.test.tsx` MUST continue
  to pass without modification (status pip is additive; status text is
  appended to existing tooltip via `aria-describedby`).
- **Test coverage**: 90% line / branch on the four files touched in the
  hook + helper (`useSkillUpdates`, `resolveSubscriptionIds`, `UpdateBell`,
  the new toast queue module). 100% AC scenario coverage in Playwright.
