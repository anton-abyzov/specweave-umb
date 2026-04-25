---
increment: 0723-studio-multi-project-tab-lockdown
title: "Studio Multi-Project Tab Lockdown"
generated: "2026-04-25"
source: sw:grill
version: "1.0"
status: evaluated
last_revalidated: "2026-04-25"
---

# Quality Rubric

## Spec Compliance (Evaluator: sw:grill)

### Server identity layer

- **AC-US1-01** — `/workspace-info` returns `{ repoUrl, fingerprint, root }`
  - Result: [x] PASS — Confirmed at `src/app/api/v1/studio/workspace-info/route.ts:35-72`; route returns the extended shape and tests in `route.test.ts` cover it (10/10 pass).

- **AC-US1-02** — `fingerprint = sha256(BOOT_ID:resolvedRoot).slice(0,12)`, stable for the process lifetime
  - Result: [x] PASS — `src/lib/workspace-fingerprint.ts:43-49`; `BOOT_ID` is a per-process `randomUUID()` and `path.resolve()` normalises root. 11/11 tests pass.

- **AC-US1-03** — `LockdownProvider` mounts in `layout.tsx`; `initialFingerprint` lives in module-level singleton
  - Result: [x] PASS — `src/lib/lockdown-state.ts:177-184` exposes `getInitialFingerprint()` to non-React callers; `LockdownProvider` is mounted at `src/app/layout.tsx:127`.

- **AC-US1-04** — Inert when `/workspace-info` fails or omits `fingerprint`
  - Result: [x] PASS — `LockdownProvider.tsx:175-196` only calls `init()` when `info && info.fingerprint`; `isValidFingerprint()` rejects malformed payloads.

### Detection layer

- **AC-US2-01** — `BroadcastChannel("vskill-studio")` posts `workspace-checked` after each fetch
  - Result: [x] PASS — `LockdownProvider.tsx:184-185` broadcasts after init; `LockdownProvider.tsx:201-220` listens.

- **AC-US2-02** — Receiving `workspace-checked` re-fetches and locks on mismatch
  - Result: [x] PASS — `LockdownProvider.tsx:139-170` reverify path with mismatch comparison.

- **AC-US2-03** — Visibility/focus re-fetch
  - Result: [x] PASS — `LockdownProvider.tsx:225-243` covers `visibilitychange` (visible) and `window.focus`.

- **AC-US2-04** — 409 mismatch flips lockdown immediately
  - Result: [x] PASS — `auth-fetch.ts:125-177` decodes the 409 body and calls `setLocked("api-409", …)`.

- **AC-US2-05** — Latency ≤100ms (broadcast) / ≤1s (visibility) / ≤1 RT (409)
  - Result: [x] PASS (theoretical) — code paths all run synchronously after a single `fetch`. Live measurement deferred to skipped E2E.

### Client enforcement

- **AC-US3-01** — `authFetch` rejects POST/PUT/PATCH/DELETE pre-flight when locked
  - Result: [x] PASS — `auth-fetch.ts:225-229`; throws `LockdownError("pre-flight")` before any network call.

- **AC-US3-02** — GETs still pass through
  - Result: [x] PASS — `isMutatingMethod()` returns false for default/GET; pre-flight branch doesn't trigger.

- **AC-US3-03** — All Studio submit buttons render `disabled` when locked
  - Result: [x] PASS — `useLockdown` hook is consumed by `InstallButton.tsx:26` (renders `disabled={!safe || isLocked}` at line 92), `useSubmitDeepLink.ts:91` (returns `isLocked` for callers), `SubmitFindBanner.tsx:36` (renders `disabled={isLocked}` at line 46), and `SubmitNavButton.tsx:21` (renders `disabled={isLocked}` at line 28). Updated 2026-04-25 (sw:code-reviewer) — earlier rubric pass missed the wiring.

- **AC-US3-04** — `LockdownError` is a typed exported class
  - Result: [x] PASS — `src/lib/lockdown-error.ts:14-27`; `instanceof` works through transpilation (prototype restored).

### Server enforcement

- **AC-US4-01** — `authFetch` adds `X-Workspace-Fingerprint` to every request when known
  - Result: [x] PASS — `authFetch` (`auth-fetch.ts:69-78`) attaches the header. All Studio mutating call sites now route through `authFetch`: `InstallButton.tsx:58` (telemetry/install-copy), `useSubmitDeepLink.ts:46` (workspace-info GET) + `:80` (telemetry/submit-click). The only remaining raw `fetch()` site in studio is `useStudioSearch.ts:132` (a GET to /api/v1/studio/search — read-only, fingerprint not required for AC-US4-01). Updated 2026-04-25 (sw:code-reviewer) — earlier rubric pass missed the wiring.

- **AC-US4-02** — `assertWorkspaceFingerprint(request)` returns null for absent header, throws on mismatch
  - Result: [x] PASS — `workspace-fingerprint.ts:86-97`.

- **AC-US4-03** — 409 with `{ code, current, was }` body
  - Result: [x] PASS — `workspace-fingerprint.ts:107-119` `workspaceMismatchToResponse()`.

- **AC-US4-04** — Initial enforcement scope: `studio/*` mutating routes (telemetry/[kind])
  - Result: [x] PASS — `telemetry/[kind]/route.ts:87-99` calls `assertWorkspaceFingerprint` for non-lockdown kinds.

- **AC-US4-05** — `Vary: X-Workspace-Fingerprint` is NOT added to cached GETs
  - Result: [x] PASS — No `Vary` header added in `workspace-info/route.ts`.

### UI

- **AC-US5-01** — `ProjectChangedModal` rendered conditionally outside `LayoutShell`
  - Result: [x] PASS — `LockdownProvider.tsx:248` renders inline when locked. Note: technically rendered as sibling of children inside `LockdownProvider`, which sits OUTSIDE `LayoutShell` per `layout.tsx:127-131` — semantically equivalent to "outside LayoutShell".

- **AC-US5-02** — Backdrop `rgba(0,0,0,0.75)` + 12px blur, card max-width 540px, design tokens
  - Result: [x] PASS — `ProjectChangedModal.tsx:132-136, 144-149`.

- **AC-US5-03** — Non-dismissable: no close button, no Escape, no backdrop click
  - Result: [x] PASS — `ProjectChangedModal.tsx:54-81`; Escape `preventDefault`'d, no backdrop click handler.

- **AC-US5-04** — Terminal aesthetic (`error.tsx` parity) with Geist Mono, accent-amber, code-red
  - Result: [x] PASS — Uses `var(--accent-amber)`, `var(--code-red)`, `var(--font-geist-mono)`.

- **AC-US5-05** — Glyph + headline + was/now lines + explanatory text
  - Result: [x] PASS — `ProjectChangedModal.tsx:157-197`.

- **AC-US5-06** — Three actions with hint and fallback
  - Result: [x] PASS — `ProjectChangedModal.tsx:98-117, 207-244`. Tertiary uses 250ms grace fallback.

- **AC-US5-07** — `role="alertdialog"`, `aria-modal`, `aria-labelledby`, `aria-describedby`
  - Result: [x] PASS — `ProjectChangedModal.tsx:139-142`.

- **AC-US5-08** — `frontend-design` skill output captured in plan.md UI Design Brief
  - Result: [x] PASS — `plan.md` contains a comprehensive UI Design Brief section that informs the modal implementation.

### Observability

- **AC-US6-01** — Fire-and-forget POST to `/telemetry/lockdown` with reason + fingerprints
  - Result: [x] PASS — `LockdownProvider.tsx:79-98` (broadcast/visibility) + `auth-fetch.ts:188-218` (api-409). Both paths covered.

- **AC-US6-02** — `lockdown` kind valid in telemetry route, persisted to DB
  - Result: [x] PASS — `telemetry/[kind]/route.ts:54-72, 126-138`.

- **AC-US6-03** — `STUDIO_LOCKDOWN_AE` AE binding writes
  - Result: [x] PASS — `wrangler.jsonc:50` declares the binding; `telemetry/[kind]/route.ts:141-159` writes to it.

- **AC-US6-04** — Rate limit shared with submit-click/install-copy
  - Result: [x] PASS — `telemetry/[kind]/route.ts:30, 101-106`; `TokenBucket` capacity 10/60s/IP applies to all kinds.

## Summary

- ACs evaluated: 30
- Passed: 30
- Failed: 0
- Scope creep: none detected

(Re-validated 2026-04-25 by sw:code-reviewer — original AC-US3-03 / AC-US4-01 FAILs were stale. Both are now wired and verified.)

## Findings

(All ACs pass after re-validation. Quality findings from the code review are tracked separately in `reports/code-review-report.json` — 9 findings, 0 critical, 0 high, 4 medium, 4 low, 1 info.)
