---
increment: 0736-studio-update-clicks-and-plugins-retry-fix
title: "Studio update clicks broken + runaway plugins retry + SSE format mismatch"
type: bug
priority: P1
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
discovered_during: 0732 E2E + post-release user verification
---

# Bug: Studio update clicks broken + runaway plugins retry + SSE format mismatch

## Overview

Three intertwined production bugs in the vskill studio update / install / notification path, surfaced by user E2E verification on 2026-04-25 after vskill@0.5.112 shipped:

1. **Update click fails** — clicking "Update to 1.0.2" on the greet-anton skill detail page produces a "Couldn't update greet-anton — Stream error" toast. Console shows `GET http://localhost:3113/api/skills/.claude/greet-anton/update` returning `net::ERR_CONNECTION_REFUSED`. The click handler invokes a stream subscription and an update fetch that both fail.
2. **Plugins runaway retry** — `/api/plugins` is hammered with 7,521+ identical fetch requests with no backoff or cancellation. Browser network tab shows continuous failures throwing `Uncaught (in promise) TypeError: Failed to fetch` from `Ml.enabled (index-TyJIV4hi.js:65:94221)`. The retry loop has no exponential backoff, no max-retry cap, and no AbortController hook tied to component unmount or visibilityState.
3. **SSE format mismatch** — studio's `useSkillUpdates()` opens an `EventSource` whose `?skills=<csv>` filter contains `<plugin>/<skill>` IDs (e.g. `.claude/anymodel`, `.claude/greet-anton`). UpdateHub's filter accepts ONLY UUID and `sk_published_*` slug — the `<plugin>/<skill>` format is silently dropped. Filed as a follow-up of 0732, now triaged as part of this fix because it shares the same studio-side surface as Bug 1.

These bugs are intertwined: the update-button path (Bug 1) relies on the SSE event channel (Bug 3), and both share retry/lifecycle problems with `/api/plugins` (Bug 2).

## Personas

- **Skill Studio user** — the developer running `vskill studio` who tries to update a skill. Sees the broken UI flow described above.
- **Operator** — anyone with the studio open in a tab; their browser is wasting CPU + bandwidth on the runaway retry loop and contributing background load to the eval-server.

## User Stories

### US-001: Update button reliably installs the new version
**Project**: vskill

**As a** Skill Studio user
**I want** clicking "Update to X.Y.Z" on a skill detail page to install the new version
**So that** I can act on the update notifications I see, instead of getting a "Stream error" toast

**Acceptance Criteria**:
- [x] **AC-US1-01**: Clicking "Update to X.Y.Z" on a skill row whose `updateAvailable === true` issues a single `POST /api/skills/:plugin/:skill/update` request and renders inline progress (not a toast error) for at least the duration of the request.
- [x] **AC-US1-02**: When the API returns 200 with `{ status: "done", version: "X.Y.Z" }`, the UI updates the displayed installed version, removes the ↑ glyph, and decrements the bell badge count.
- [x] **AC-US1-03**: When the API returns a non-2xx response or a network error, the UI shows a specific error message (status code + body excerpt), keeps the "Update" button enabled, and does NOT silently swallow the failure as a generic "Stream error".
- [x] **AC-US1-04**: The update endpoint accepts whatever ID format the studio is currently using for the skill (`<plugin>/<skill>` per current behavior) — backend resolution must NOT require UUID/slug for this endpoint.
- [x] **AC-US1-05**: An E2E playwright test exercises the click-to-install flow against a real eval-server (not a mocked one) using a fixture skill with a deliberately stale version, and asserts the post-update UI state.

### US-002: Plugins polling stops being a runaway retry loop
**Project**: vskill

**As a** Skill Studio user
**I want** the `/api/plugins` endpoint to be polled at most a few times per minute, with backoff on failure and cancellation when my tab is hidden or unmounted
**So that** my browser doesn't pile up thousands of failed requests when the eval-server is briefly unreachable

**Acceptance Criteria**:
- [x] **AC-US2-01**: When the eval-server is unreachable, `/api/plugins` is retried at most 5 times with exponential backoff (e.g. 1s, 2s, 4s, 8s, 16s), then enters a paused state until the user explicitly retries (button) or the visibilityState toggles to "visible".
- [x] **AC-US2-02**: While `document.visibilityState === "hidden"`, no `/api/plugins` polling occurs.
- [x] **AC-US2-03**: Component unmount aborts any in-flight `/api/plugins` request via `AbortController.abort()`. No "Failed to fetch" warnings appear after navigation.
- [x] **AC-US2-04**: A single open studio tab over 60 minutes makes ≤ 60 `/api/plugins` requests in steady state (i.e. ≤ 1 per minute). Verified by counting `_logRequestCount` or by network tap.
- [x] **AC-US2-05**: A unit test covers the backoff schedule, max-retry cap, and AbortController cleanup of the plugins polling hook.

### US-003: SSE EventSource subscribes with an ID format the platform accepts
**Project**: vskill

**As a** Skill Studio user
**I want** the live SSE notification stream to actually deliver events for my installed skills
**So that** I see the bell badge update without having to refresh the page or rely solely on the polling fallback

**Acceptance Criteria**:
- [x] **AC-US3-01**: `useSkillUpdates()` constructs the `?skills=<csv>` filter from the resolved Skill UUID OR canonical slug (`sk_published_<owner>/<repo>/<skill>`) for each installed skill — NOT the `<plugin>/<skill>` local filename pair.
- [x] **AC-US3-02**: When the studio cannot resolve a UUID or slug for an installed skill (e.g. local-only skill, no platform record), it omits that skill from the SSE filter rather than sending a malformed third-format ID.
- [x] **AC-US3-03**: A real-SSE integration test (extending the slug-test pattern from 0732) proves that a `skill.updated` event published for skill X reaches a studio subscriber whose installed list contains X resolved through the new resolver.
- [x] **AC-US3-04**: A doc-comment block at the top of `useSkillUpdates.ts` and `platform-proxy.ts` describes the ID-format contract from the studio side, mirroring the contract block 0732 added to `update-hub.ts` on the platform side.

## Functional Requirements

- **FR-001 (update-click handler)**: Click handler in the skill detail RightPanel posts to `/api/skills/:plugin/:skill/update`, awaits the response, and dispatches a single store update. No EventSource side-channel for the simple update path. Existing batch-update SSE remains for multi-skill flows.
- **FR-002 (error UX)**: Update failures render a structured banner with status code + first 200 chars of body, plus a "Retry" link that re-issues the same request.
- **FR-003 (plugins polling hook)**: `/api/plugins` polled via a single `usePluginsPolling()` hook with: AbortController on unmount, visibilityState pause, exponential backoff capped at 16s, max 5 consecutive failures before pausing.
- **FR-004 (SSE ID resolver)**: New helper `resolveSubscriptionIds(installedSkills): { uuid?: string, slug?: string }[]` that maps each installed skill to its tracked UUID/slug via `/api/skills/installed` enrichment. Used by `useSkillUpdates()`.
- **FR-005 (graceful degradation)**: If a skill has no UUID/slug, `useSkillUpdates()` does not throw or block — it simply doesn't subscribe for that skill, and the polling fallback covers it.
- **FR-006 (doc comments)**: Top-of-file comment blocks in `useSkillUpdates.ts`, `usePluginsPolling.ts`, and platform-proxy.ts describe the contracts and the "why" so the next dev doesn't reintroduce these regressions.

## Non-Functional Requirements

- **NFR-001 (perf)**: Single tab with 100 installed skills makes ≤ 1 `/api/plugins` request per minute steady-state (vs. current 7500+/min).
- **NFR-002 (correctness)**: Update click success rate ≥ 99% under normal conditions (eval-server reachable, valid auth).
- **NFR-003 (testability)**: All FRs covered by unit + integration tests; AC-US1-05 by Playwright E2E; AC-US3-03 by real-SSE harness.

## Success Criteria

- **SC-001**: Clicking "Update to X.Y.Z" on greet-anton in a fresh studio session installs the version and the UI reflects the new state — verified by Playwright E2E and by manual screenshot proof.
- **SC-002**: Network tap of an idle studio tab over 5 minutes shows ≤ 5 `/api/plugins` requests (down from thousands).
- **SC-003**: SSE subscription with installed skills delivers `skill.updated` events end-to-end, captured in a real-SSE integration test.
- **SC-004**: vskill@0.5.113 (or whatever the next patch is) ships the fixes, and a clean `npm install -g vskill@latest && vskill studio` repro shows all three bugs resolved.

## Out of Scope

- Redesigning the update flow to be SSE-progress-driven (current REST POST is fine for v1).
- Migrating UpdateHub to accept the `<plugin>/<skill>` format as a third option (we're fixing the studio side, which is the authoritative source of installed-skill identity).
- 100-skill batch limit on `/api/skills/updates` (filed as separate finding in 0732 closure).
