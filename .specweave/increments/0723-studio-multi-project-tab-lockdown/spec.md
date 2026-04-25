---
increment: 0723-studio-multi-project-tab-lockdown
title: "Studio Multi-Project Tab Lockdown"
type: feature
priority: P2
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Multi-Project Tab Lockdown

## Overview

Detect cross-tab project changes in Skill Studio and enter a non-dismissable lockdown modal. Server fingerprint + BroadcastChannel + visibility-change detection. Defence-in-depth via `X-Workspace-Fingerprint` header → HTTP 409. Beautiful modal designed via the `frontend-design` skill.

## Problem

Skill Studio is a local-launched Next.js process bound to one workspace folder via the `STUDIO_WORKSPACE_ROOT` environment variable (fallback: `process.cwd()`). The binding is computed once at process start — see `repositories/anton-abyzov/vskill-platform/src/app/api/v1/studio/workspace-info/route.ts:10`.

If a user launches `vskill studio` from `/projects/alpha`, opens the UI in a browser tab, then later launches `vskill studio` from `/projects/beta`, the second invocation rebinds the local Studio process to the new workspace. The first browser tab is now **stale**: it still believes it's editing alpha (its UI state, unsaved drafts, telemetry, deeplinks), but every API call now hits beta's backend.

Today the system has **no detection, no warning, and no protection**. Mutations from the stale tab silently land on the wrong workspace — corrupting telemetry, overwriting in-progress edits, and producing submissions that reference the wrong skill source. The user has no signal that the project has changed; the UI looks identical to the moment they left it.

This is a class of silent data-corruption bug that becomes very expensive to debug after the fact (telemetry attributed to the wrong skill, lost drafts, "I swear I submitted that already" reports).

## Users

- **Skill Studio user (primary)** — a developer using `vskill studio` to author, preview, and submit skills locally. Often runs Studio from multiple project directories during a session (switching between client projects, between an experiment and a real skill repo, etc.).
- **Studio backend (secondary actor)** — the local Next.js process that needs to refuse stale writes as defence-in-depth, even if the client misbehaves.
- **Operator (observability consumer)** — Anton (and future operators) needs to verify the lockdown actually fires in production telemetry to know the protection is working.

## Success Criteria

A stale Studio tab can no longer silently corrupt the wrong workspace. Specifically:

1. **Detection** — When workspace changes, every other open Studio tab enters lockdown within ~1s through at least one of the three detection paths (broadcast / visibility / 409).
2. **Containment** — While locked, the tab refuses all mutating HTTP verbs (POST/PUT/PATCH/DELETE) at the `authFetch` layer; submit buttons render disabled.
3. **Defence-in-depth** — Even if the client is buggy or paused, the server rejects mutations whose `X-Workspace-Fingerprint` header is stale with HTTP 409 and a structured error body.
4. **Communication** — The user sees a non-dismissable, accessible modal explaining what happened, what they were on (`was`), what they're on now (`now`), and three clear actions (reload / open original in new window / close tab).
5. **Observability** — Every lockdown trigger is recorded in both the database (`studioTelemetry` row with `kind = "lockdown"`) and Analytics Engine (`STUDIO_LOCKDOWN_AE` with `reason` dimension), so the operator can verify the feature fires correctly in production.
6. **Zero overhead when single-tab** — A solo Studio session pays no extra network calls beyond the initial `/workspace-info` fetch.

## User Stories

### US-001 — Each tab learns its workspace identity at mount

**Project**: vskill-platform

**As a** Studio user
**I want** my tab to know which workspace it's bound to from load
**So that** any later change can be detected reliably

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `GET /api/v1/studio/workspace-info` returns `{ repoUrl, fingerprint, root }` (extends the current `{ repoUrl }` shape).
- [ ] **AC-US1-02**: `fingerprint = sha256(BOOT_ID:resolvedRoot).slice(0,12)`, stable for the entire process lifetime.
- [ ] **AC-US1-03**: `LockdownProvider` (new client component mounted in `layout.tsx`) fetches `/workspace-info` once on mount and stores `initialFingerprint` in a module-level singleton, so `authFetch` can read it without React-context plumbing.
- [ ] **AC-US1-04**: If the initial `/workspace-info` fetch fails or returns no fingerprint, the lockdown infra stays inert (graceful degradation — the feature must never break Studio for users on older builds).

---

### US-002 — Stale tab detects project change and locks

**Project**: vskill-platform

**As a** Studio user
**I want** the stale tab to detect a workspace switch within ~1s
**So that** I never silently submit to the wrong project

**Acceptance Criteria**:
- [ ] **AC-US2-01**: A `BroadcastChannel("vskill-studio")` is established by `LockdownProvider`; sibling tabs broadcast `{ type: "workspace-checked" }` after each successful `/workspace-info` fetch.
- [ ] **AC-US2-02**: On receiving a `workspace-checked` message, the tab re-fetches `/workspace-info`; if the returned fingerprint differs from `initialFingerprint`, it sets `isLocked = true`.
- [ ] **AC-US2-03**: On `visibilitychange` (visible) and `focus` events, the tab re-fetches `/workspace-info` and compares (catches the cross-browser/cross-device case where `BroadcastChannel` doesn't carry).
- [ ] **AC-US2-04**: When a mutation returns HTTP 409 with body `{ code: "WORKSPACE_FINGERPRINT_MISMATCH", current, was }`, lockdown activates immediately using `current` as the new fingerprint.
- [ ] **AC-US2-05**: Trigger latency: ≤100ms cross-tab via `BroadcastChannel`; ≤1s on `visibilitychange`; ≤1 round-trip on a 409 response.

---

### US-003 — Lockdown blocks all mutations client-side

**Project**: vskill-platform

**As a** Studio user
**I want** the locked tab to refuse all writes
**So that** I cannot accidentally corrupt the active workspace

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When `isLocked = true`, `authFetch` (`src/lib/auth-fetch.ts:33`) rejects POST/PUT/PATCH/DELETE by throwing a typed `LockdownError` *before* the network call.
- [ ] **AC-US3-02**: GET requests still pass through (read-only is safe and is needed for the lockdown UI itself to render correctly).
- [ ] **AC-US3-03**: All form submit buttons across Studio render `disabled` when `isLocked = true`, via a `useLockdown()` hook backed by the same module-level singleton + a React subscription mechanism.
- [ ] **AC-US3-04**: `LockdownError` is an exported, typed error class so `try/catch` sites can distinguish lockdown rejection from generic network errors and avoid showing misleading "network error" toasts.

---

### US-004 — Server rejects mutations from stale tab (defence-in-depth)

**Project**: vskill-platform

**As a** Studio backend
**I want** to refuse mutations whose fingerprint header doesn't match the current workspace
**So that** a buggy or paused client cannot mutate the wrong workspace

**Acceptance Criteria**:
- [ ] **AC-US4-01**: `authFetch` adds the header `X-Workspace-Fingerprint: <initialFingerprint>` to every request when the fingerprint is known. (Header omitted when fingerprint is unknown — graceful degradation.)
- [ ] **AC-US4-02**: New helper `assertWorkspaceFingerprint(request)` in `src/lib/workspace-fingerprint.ts` returns `null` if the header is absent (back-compat with older clients), throws `WorkspaceMismatchError` if the header is present and differs from the current process fingerprint.
- [ ] **AC-US4-03**: A mismatch is serialised to HTTP 409 with body `{ code: "WORKSPACE_FINGERPRINT_MISMATCH", current, was }` via a small wrapper helper used by mutating route handlers.
- [ ] **AC-US4-04**: Initial enforcement scope (this increment): all `studio/*` mutating routes — concretely, `POST /api/v1/studio/telemetry/[kind]`. Non-Studio routes are deferred to a follow-up increment so we keep blast radius small.
- [ ] **AC-US4-05**: `Vary: X-Workspace-Fingerprint` is **NOT** added to cached GET responses (the header is only consumed by mutating routes; adding it to `Vary` would needlessly fragment the cache key).

---

### US-005 — User sees beautiful, non-dismissable lockdown modal

**Project**: vskill-platform

**As a** Studio user
**I want** the lockdown UI to be unmissable, calm, and obviously protective
**So that** I trust the system and immediately know what to do

**Acceptance Criteria**:
- [ ] **AC-US5-01**: New component `ProjectChangedModal.tsx` (in `src/app/components/`) is rendered conditionally by `LockdownProvider` at the end of `layout.tsx`, *outside* `LayoutShell` (so it sits above all app chrome).
- [ ] **AC-US5-02**: Full-screen overlay with backdrop `rgba(0,0,0,0.75)` + 12px backdrop blur (matches the existing sticky-nav glassmorphism). Card is centered, `max-width: 540px`, uses `var(--bg)` / `var(--border)` design tokens.
- [ ] **AC-US5-03**: NOT dismissable: no close button, no Escape key handler, no backdrop-click handler, `pointer-events` blocked on the background.
- [ ] **AC-US5-04**: Visual language follows the `error.tsx` terminal pattern: Geist Mono headers, `--code-amber` for the warning glyph, `--code-red` for the stale path label.
- [ ] **AC-US5-05**: Content shows: a warning glyph, headline `PROJECT CHANGED`, two labelled lines `was: <originalRepoUrl> (<originalRoot>)` and `now: <currentRepoUrl> (<currentRoot>)`, and an explanatory line `This tab is locked — any unsaved changes here are not persisted`.
- [ ] **AC-US5-06**: Three actions side-by-side, monospace, terminal-style: (1) **Reload as `<new>`** → `window.location.reload()`; (2) **Open `<original>` in new window** → `window.open(window.location.origin, "_blank")` + a 1-line hint `Run vskill studio from <originalRoot> to restore`; (3) **Close tab** → `window.close()` with a fallback message if the browser blocks it.
- [ ] **AC-US5-07**: `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby` and `aria-describedby` set so screen readers announce the lockdown immediately.
- [ ] **AC-US5-08**: The Architect phase MUST invoke the `frontend-design` skill explicitly to produce: visual hierarchy, action button affordances, warning glyph choice, and micro-copy. The output is captured in `plan.md` under a "UI Design Brief" section *before* any UI code is written.

---

### US-006 — Lockdown events are observable in production

**Project**: vskill-platform

**As an** operator
**I want** every lockdown trigger logged with reason
**So that** I can verify the feature fires correctly and detect abuse

**Acceptance Criteria**:
- [ ] **AC-US6-01**: When lockdown activates, `LockdownProvider` fires `POST /api/v1/studio/telemetry/lockdown` (fire-and-forget, no `await` blocking the modal render) with body `{ reason: "broadcast" | "visibility" | "api-409", originalFingerprint, newFingerprint }`.
- [ ] **AC-US6-02**: `"lockdown"` is added as a valid `kind` in `telemetry/[kind]/route.ts`; the payload is validated and persisted to the `studioTelemetry` table.
- [ ] **AC-US6-03**: Each event also writes to a new Analytics Engine binding `STUDIO_LOCKDOWN_AE` (mirroring the `0708 UPDATE_METRICS_AE` pattern in `wrangler.jsonc` lines 36–55) with dimensions `[reason]`.
- [ ] **AC-US6-04**: The telemetry endpoint enforces the same rate limit as the existing `submit-click`/`install-copy` kinds (10 req per 60s per IP) — abuse protection inherited from the existing infra.

## Architecture

The feature splits cleanly across three layers — the **server identity layer**, the **client detection layer**, and the **enforcement layer** (which exists on both sides).

**Server identity layer.** A per-process `BOOT_ID` is generated at module-load time (cryptographically random, stable for the process lifetime). The fingerprint is `sha256(BOOT_ID + ":" + resolvedRoot).slice(0, 12)`. Combining `BOOT_ID` with `resolvedRoot` means: (a) two processes for the same root produce different fingerprints, so a rebind to the same path is still detected as a change (catches the case where the user kills Studio and restarts it pointing at the same workspace — that's still a "new session" worth signalling); (b) the fingerprint is opaque (a hash, not a path), so it's safe to expose in headers and logs. The fingerprint is exposed by extending the `/api/v1/studio/workspace-info` response from `{ repoUrl }` to `{ repoUrl, fingerprint, root }` (US-001).

**Client detection layer.** A new client component, `LockdownProvider`, is mounted at the top of `layout.tsx` (above `LayoutShell`). On mount it fetches `/workspace-info` once and stores `{ initialFingerprint, originalRepoUrl, originalRoot }` in a module-level singleton in `src/lib/lockdown-state.ts`. The singleton (not React context) is chosen so `authFetch` can synchronously read the fingerprint without prop-drilling or context wiring through every API call site. A subscription mechanism (a `Set<() => void>` of listeners) lets React components re-render when `isLocked` flips. Three independent detection paths run concurrently: (1) `BroadcastChannel("vskill-studio")` for instant cross-tab notification within the same browser process (US-002 AC-01/02); (2) `visibilitychange`/`focus` event listeners for cases where `BroadcastChannel` doesn't carry — different browser, different device, browser focus restore from sleep (US-002 AC-03); (3) HTTP 409 responses from mutating APIs as the server's last word (US-002 AC-04).

**Enforcement layer.** Client-side, `authFetch` (`src/lib/auth-fetch.ts:33`) is the single chokepoint for outgoing requests; it reads the singleton, attaches `X-Workspace-Fingerprint` on every request when known, and short-circuits POST/PUT/PATCH/DELETE with a thrown `LockdownError` when `isLocked === true` (US-003 AC-01, US-004 AC-01). Server-side, a new helper `assertWorkspaceFingerprint(request)` lives in `src/lib/workspace-fingerprint.ts`; it returns `null` when the header is absent (back-compat) and throws `WorkspaceMismatchError` when the header is present and differs (US-004 AC-02). A small wrapper translates `WorkspaceMismatchError` to HTTP 409 with the structured body. Initial enforcement scope is the `studio/*` mutating routes — concretely the telemetry endpoint — so blast radius is bounded (US-004 AC-04).

**Observability layer.** Lockdown activation fires a fire-and-forget `POST /api/v1/studio/telemetry/lockdown` with `{ reason, originalFingerprint, newFingerprint }`. The route persists to `studioTelemetry` (durable record) AND writes to a new `STUDIO_LOCKDOWN_AE` Analytics Engine binding (queryable dashboard) — mirroring the dual-write pattern from increment 0708 (US-006).

## Integrations

- **`/api/v1/studio/workspace-info` route** (extending response shape from `{ repoUrl }` to `{ repoUrl, fingerprint, root }`) — `src/app/api/v1/studio/workspace-info/route.ts:10`.
- **`authFetch` in `src/lib/auth-fetch.ts:33`** — single chokepoint for client-side enforcement (header injection + lockdown short-circuit).
- **`/api/v1/studio/telemetry/[kind]` route** — adding `lockdown` as a new kind (US-006), reusing existing rate-limit infra and `studioTelemetry` table.
- **`studioTelemetry` Prisma table** — persisting lockdown rows (no schema migration needed; `kind` is a string column).
- **Cloudflare Analytics Engine** — new `STUDIO_LOCKDOWN_AE` binding declared in `wrangler.jsonc`, modelled exactly on the `UPDATE_METRICS_AE` pattern from increment 0708 (`wrangler.jsonc:36-55`).
- **`error.tsx` design tokens** (`var(--bg)`, `var(--border)`, `--code-amber`, `--code-red`, Geist Mono) — modal must visually match for consistent terminal aesthetic (US-005 AC-04).
- **`frontend-design` skill** — invoked by Architect during planning (US-005 AC-08) to produce the UI Design Brief that feeds modal implementation.
- **Increment 0708** — establishes the Analytics Engine binding pattern this increment follows.
- **Increment 0718** — established the 200ms `/workspace-info` SLA we must not regress.
- **No new third-party packages** — `BroadcastChannel`, `crypto.subtle.digest` (sha256), `visibilitychange`, `focus`, `window.close()`, `window.open()` are all browser/Node platform APIs.

## UI/UX

The modal is the most visible artefact of this feature; the user must encounter it at the worst possible moment (mid-edit, about to submit) and immediately understand what happened, why their work is blocked, and what to do next. The tone must be **calm, protective, and authoritative** — not panicked, not apologetic.

**Visual aesthetic.** Matches the existing `error.tsx` terminal pattern: Geist Mono headers, `var(--bg)` / `var(--border)` tokens, `--code-amber` for the warning glyph (signals caution without alarm), `--code-red` for the stale-path label (signals "this is the wrong place"). Full-screen overlay with `rgba(0,0,0,0.75)` backdrop + 12px backdrop blur — matches the sticky-nav glassmorphism so it feels native to the existing surface, not a foreign popup. Card is centered, `max-width: 540px`, with monospace text.

**Layout & content** (US-005 AC-05): a warning glyph at the top, headline `PROJECT CHANGED` (uppercase, monospace, terminal-style), two labelled diff lines (`was: <originalRepoUrl> (<originalRoot>)` and `now: <currentRepoUrl> (<currentRoot>)`), and an explanatory line `This tab is locked — any unsaved changes here are not persisted`. Three actions in a horizontal row: **Reload as `<new>`** (primary), **Open `<original>` in new window** (secondary, with a 1-line hint `Run vskill studio from <originalRoot> to restore`), **Close tab** (tertiary, with fallback message if `window.close()` is blocked).

**Non-dismissability** (US-005 AC-03) is intentional and protective: no close button, no Escape handler, no backdrop click, `pointer-events: none` on the background. The user *must* choose one of the three actions — there is no "ignore and keep working" path because that path is exactly what produces the silent corruption this feature exists to prevent.

**Accessibility** (US-005 AC-07): `role="alertdialog"`, `aria-modal="true"`, `aria-labelledby` pointing at the headline, `aria-describedby` pointing at the explanatory line. Screen readers announce immediately. Tab order traverses the three actions; the primary "Reload" action is auto-focused on mount.

**Architect handoff** (US-005 AC-08): the `frontend-design` skill is invoked explicitly during the Architect phase to produce the final visual hierarchy, action button affordances, warning glyph choice, and micro-copy. The skill's output is captured in `plan.md` under a "UI Design Brief" section *before* any UI code is written, so the Implementer has a concrete spec to follow rather than improvising.

**Disabled-button affordance** (US-003 AC-03): when `isLocked === true`, all submit buttons across Studio render `disabled` (greyed out, `aria-disabled="true"`, no hover state). This is a secondary signal — the modal is the primary signal — but it ensures the underlying UI doesn't *look* clickable while the modal is up.

## Performance

- **Solo-tab cost**: zero additional network calls beyond the initial `/workspace-info` fetch on mount. No polling, no heartbeat, no keep-alive.
- **Cross-tab detection latency**: `BroadcastChannel` round-trip is sub-millisecond; the re-fetch of `/workspace-info` it triggers is bounded by the existing 200ms SLA from increment 0718. End-to-end ≤100ms target (US-002 AC-05) is dominated by the re-fetch.
- **Visibility-change detection latency**: the listener fires within ~16ms of the tab becoming visible; the re-fetch is bounded by the same 200ms SLA. End-to-end ≤1s target leaves comfortable headroom (US-002 AC-05).
- **API-409 detection latency**: ≤1 round-trip — the failed mutation already paid the round-trip, so the lockdown activation cost is essentially zero on top.
- **Modal render latency**: `<50ms` from `isLocked` flipping to the modal being painted. Achievable because the modal component is statically imported in `layout.tsx` (no dynamic chunk), the singleton notifies React subscribers synchronously, and the modal markup is small (single card, no images, monospace text).
- **No regression to `/workspace-info` hot path**: the route only needs to compute the fingerprint *once per process* (cached at module load), so per-request work is `O(1)` — just spreading the cached fingerprint into the response. The 200ms SLA from increment 0718 holds.
- **Header overhead**: `X-Workspace-Fingerprint` is 12 chars + ~25 chars header name overhead = ~37 bytes per request. Negligible compared to existing auth headers.
- **Cache hygiene**: header is NOT added to `Vary` on cached GETs (US-004 AC-05) — would needlessly fragment the cache key per-tab and erase any benefit of caching.
- **Fire-and-forget telemetry**: lockdown activation fires the telemetry POST without `await`, so the modal render is never blocked on the network call (US-006 AC-01).

## Security

- **Fingerprint is opaque** — it's a sha256 truncation of `BOOT_ID:resolvedRoot`. The path is hashed, not exposed, so leaking the fingerprint in headers/logs does not leak the local filesystem layout.
- **`BOOT_ID` is per-process random** — derived from `crypto.randomBytes(16)` at module load. Not predictable, not enumerable.
- **No new authentication surface** — the fingerprint is identity-of-binding, not identity-of-user. It does NOT replace, weaken, or interact with existing auth (cookies, JWT). A request with a stale fingerprint but valid auth is still rejected (the lockdown triggers); a request with a current fingerprint but invalid auth is still rejected (auth runs first).
- **Server fingerprint check is opt-in via header presence** — `assertWorkspaceFingerprint` returns `null` when the header is absent (US-004 AC-02). This means a malicious client could trivially bypass the server check by omitting the header. This is **acceptable** because: (a) the server check is *defence-in-depth* against a buggy/paused legitimate client, not a security boundary against attackers; (b) the threat model is "user accidentally has two Studio sessions", not "attacker actively bypasses Studio"; (c) Studio binds to localhost and is not internet-exposed.
- **Telemetry rate-limiting** — the new `lockdown` kind inherits the existing 10 req/60s/IP limit (US-006 AC-04), preventing a malicious or buggy client from flooding the telemetry pipeline.
- **Telemetry payload validation** — the lockdown payload is validated server-side (string `reason` from a fixed enum `"broadcast" | "visibility" | "api-409"`, hex-string fingerprints), so injection or oversized payload attempts are rejected.
- **No PII in telemetry** — the payload contains only fingerprints (opaque hashes) and a reason enum. No paths, no repo URLs, no user identifiers beyond what existing telemetry already collects.
- **Modal cannot be exploited for clickjacking** — it's rendered inside the same-origin Studio page; no iframes, no postMessage handlers.
- **`window.open()` opens same-origin** — the "Open `<original>` in new window" action opens `window.location.origin` (US-005 AC-06). It does not navigate to a user-supplied URL, so no open-redirect risk.
- **`BroadcastChannel` is same-origin only** — the browser scopes channels to origin, so no cross-origin tab can send spoofed `workspace-checked` messages.
- **No secrets in headers/logs** — `X-Workspace-Fingerprint` is opaque; the 409 body returns `current` and `was` fingerprints (also opaque).

## Edge Cases

- **`BroadcastChannel` not supported** (rare browsers, Safari < 15.4 on iOS) → Visibility/focus re-fetch path (US-002 AC-03) covers this; lockdown still works, just slower (~1s instead of ~100ms).
- **`crypto.subtle.digest` not available** (very old browsers / non-secure context) → Lockdown infra stays inert per AC-US1-04 graceful-degradation rule. Studio still functions; protection is just absent.
- **Older Studio binary doesn't return `fingerprint`** → AC-US1-04 graceful degradation: feature stays inert, no errors, no broken UI. Mixed-version environments are safe.
- **Existing automation/scripts call `/telemetry/*` without the header** → AC-US4-02 makes header presence opt-in: helper returns `null` (allows request) when header is absent. No breakage for legacy callers.
- **`window.close()` blocked by browser** (tab not opened by script) → AC-US5-06 specifies a fallback message asking the user to manually close. Non-fatal.
- **Two tabs broadcast `workspace-checked` simultaneously and re-fetch in a tight loop** → Idempotent: re-fetching `/workspace-info` and comparing is cheap and stateless; the broadcast carries no payload that triggers further broadcasts. No exponential amplification possible.
- **User reloads while modal is rendering** → Reload wins; the new tab fetches `/workspace-info` fresh, captures the new fingerprint as `initialFingerprint`, lockdown infra stays inert (no mismatch).
- **`/workspace-info` re-fetch fails during detection** → Treated as "no signal"; `isLocked` does NOT flip. The next detection signal (broadcast, visibility, or 409) gets another chance. We avoid false-positive lockdowns from transient network errors.
- **Server returns a 409 with `current === initialFingerprint`** (impossible-but-defensive) → Client ignores the 409 as a no-op (the server is wrong but we don't lock unnecessarily). Defensive log emitted.
- **Lockdown telemetry POST itself returns 409** (it would, since the tab is locked and the server enforces) → Telemetry is fire-and-forget; the failed POST is swallowed. Acceptable trade-off: the *first* lockdown of a session may not log if the client's first POST is also the trigger, but subsequent triggers (or other tabs) will log. Operator can still see the activity via Analytics Engine writes that DO succeed (server-side dual-write happens before the 409 check, by design — the route handler logs the attempt then enforces).
- **Same workspace, fresh process** (user kills Studio, restarts pointing at same path) → Fingerprint changes (because `BOOT_ID` changes), so this IS detected as a workspace change. Intentional: a restart is a meaningful boundary; the user should see "PROJECT CHANGED" with `was: /alpha → now: /alpha (new session)`.
- **Symlinks in `STUDIO_WORKSPACE_ROOT`** → `resolvedRoot` is the realpath-resolved absolute path; symlink swaps that change the realpath are detected as workspace changes. Symlink swaps that don't change the realpath are not (correctly — same workspace).
- **Modal renders before `/workspace-info` returns initial fingerprint** → `LockdownProvider` mounts the modal conditionally on `isLocked === true`, which can only flip after `initialFingerprint` is set. So the modal cannot render in an indeterminate state.
- **User has 5+ Studio tabs open and switches workspace** → All non-current tabs detect via broadcast simultaneously and lock independently. Each fires its own telemetry. Rate limit (10/60s/IP) protects the endpoint; even 5 simultaneous lockdown POSTs is well under the limit.
- **Mixed Studio versions across tabs** (one tab on old build without lockdown, one on new) → Old tab is unprotected (degrades silently). New tab still detects and locks correctly. Acceptable transitional state.
- **Race between cross-tab broadcast and 409 from in-flight mutation** → Both can trigger lockdown; second trigger is a no-op (`isLocked` is already `true`). Telemetry may double-fire with different `reason` values, which is fine — operator sees both signals fired, confirming defence-in-depth worked.
- **User has Studio open in browser, sleeps laptop, resumes hours later, workspace was rebound mid-sleep** → On resume, `visibilitychange` (visible) fires, re-fetch detects mismatch, lockdown activates. Catches the long-sleep case where `BroadcastChannel` cannot help.

## Non-Functional Requirements

- **Lockdown trigger latency**: ≤100ms cross-tab via `BroadcastChannel`; ≤1s on `visibilitychange`; ≤1 round-trip on a 409 response.
- **Zero impact when single-tab**: A solo Studio session must pay no additional network calls beyond the initial `/workspace-info` fetch on mount. No polling, no heartbeat.
- **Modal render latency**: `<50ms` from `isLocked` flipping `true` to the modal being painted.
- **No regression to `/workspace-info` hot path**: The 200ms timeout requirement established by increment 0718 must continue to hold (this increment only extends the response payload shape; it does not add latency-sensitive logic to the route).
- **Accessibility**: Modal must be screen-reader announceable (`role="alertdialog"`, `aria-modal`, `aria-labelledby`, `aria-describedby`) and keyboard-navigable across the three actions.
- **Graceful degradation**: If `/workspace-info` doesn't return a fingerprint (older Studio binary), lockdown stays inert — no errors, no broken UI, just no protection.
- **Observability fidelity**: Every lockdown trigger MUST land in both `studioTelemetry` (durable) and Analytics Engine (queryable dashboard), so the operator can verify the feature fires in production.

## Technical Constraints

- **Stack**: Next.js 15 App Router (vskill-platform), React Server Components for layout, client components for lockdown infra.
- **Workspace identity source**: `STUDIO_WORKSPACE_ROOT` env var (fallback `process.cwd()`) resolved at process start — see `workspace-info/route.ts:10`. The fingerprint must be derived from this resolved root + a per-process `BOOT_ID` so two processes for the same root produce different fingerprints (rebind detection).
- **Singleton storage**: Module-level singleton (not React context) so `authFetch` can read the fingerprint without prop-drilling or context wiring through every API call site. Subscription mechanism (e.g. listener set) needed for React components that need to re-render when `isLocked` flips.
- **Header naming**: `X-Workspace-Fingerprint` (consistent with existing `X-*` custom headers in the platform).
- **Telemetry binding**: New Cloudflare Analytics Engine binding `STUDIO_LOCKDOWN_AE`, modelled exactly after `UPDATE_METRICS_AE` from increment 0708 (`wrangler.jsonc:36-55`).
- **Cache discipline**: Do NOT add `X-Workspace-Fingerprint` to `Vary` on cached GET responses (would fragment the cache key for no benefit — the header is only meaningful for mutating routes).

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `BroadcastChannel` not supported (rare browsers) | Low | Medium | Visibility/focus re-fetch path covers this; lockdown still works, just slower. |
| Older Studio binary doesn't return `fingerprint` | Medium | Low | Graceful degradation per AC-US1-04 — feature stays inert, no breakage. |
| Server fingerprint check breaks existing automation calling `/telemetry/*` without the header | Medium | High | AC-US4-02: helper returns `null` (allows request) when header absent — header presence is opt-in. |
| Modal blocks user from copying useful debug info before reload | Low | Low | Modal shows `was` and `now` paths inline so user can read them; future enhancement could add a "copy diagnostics" button. |
| Rate limit on `/telemetry/lockdown` could swallow real lockdown events | Low | Medium | AC-US6-04 inherits the existing 10/60s/IP limit; lockdown should fire at most a few times per session per IP, well under the limit. |
| `window.close()` blocked by browser when not opened by script | Medium | Low | AC-US5-06 specifies a fallback message; user can manually close. |
| Race: two tabs simultaneously broadcast `workspace-checked` and re-fetch in a tight loop | Low | Low | Idempotent: re-fetching `/workspace-info` and comparing is cheap and stateless; broadcast carries no payload that triggers further broadcasts. |

## Out of Scope

- **Guarding non-Studio mutating endpoints** (admin queue, problem-reports, auth refresh) — separate follow-up increment so this change stays scoped to the Studio surface area.
- **Cross-device coordination** — each device hits its own local Studio, and the server fingerprint check (US-004) naturally rejects cross-device stale writes via 409.
- **Persisting original `repoUrl` across reload** — held in component state only; reload is an explicit user action and the new tab is intentionally a clean session.
- **Auto-recovery** (re-binding to a newly-spawned Studio matching the original workspace) — reload is the only forward path. Auto-recovery would require process discovery that's out of scope.
- **UI lockdown for non-mutating side effects** (e.g. local component state changes, draft auto-save to localStorage) — out of scope; the contract is "no writes hit the wrong workspace", not "freeze the entire UI".

## Dependencies

- **Existing `/api/v1/studio/workspace-info` route** — extending its response shape (US-001).
- **Existing `authFetch` in `src/lib/auth-fetch.ts:33`** — hooking lockdown enforcement into it (US-003, US-004).
- **Existing `error.tsx` design tokens** (`var(--bg)`, `var(--border)`, `--code-amber`, `--code-red`, Geist Mono) — modal must visually match (US-005).
- **Existing telemetry route `/api/v1/studio/telemetry/[kind]`** — adding `lockdown` as a new kind (US-006).
- **Existing `studioTelemetry` table** — persisting lockdown rows (US-006).
- **Existing rate-limit infra** for `submit-click`/`install-copy` — reused for `lockdown` kind (US-006).
- **`frontend-design` skill** — invoked by Architect during planning to produce the UI Design Brief (US-005).
- **Cloudflare Analytics Engine** — new `STUDIO_LOCKDOWN_AE` binding modelled after the `0708 UPDATE_METRICS_AE` pattern.
- **Increment 0708** — establishes the Analytics Engine binding pattern this increment follows.
- **Increment 0718** — established the 200ms `/workspace-info` SLA we must not regress.
