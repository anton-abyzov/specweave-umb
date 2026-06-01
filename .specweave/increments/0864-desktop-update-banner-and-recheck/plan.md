# Plan — 0864 Desktop update banner + reliable re-check

## Approach

Frontend-led fix (detection is a frontend cadence bug), plus a small Rust
robustness tweak and a new banner component. Reuse the existing signed update
plumbing end-to-end; add no new IPC commands.

## Components

### 1. `useAppUpdater.tsx` (hook) — re-check cadence + banner-dismiss split
- Add a `lastCheckAtRef` (ms). `checkNow()` stamps it on a successful check.
- Add a `maybeCheck()` that calls `checkNow()` only if `now - lastCheckAt >= 30min`.
- New effect (desktop only): attach `window` `focus` + `document`
  `visibilitychange` (when `visible`) listeners → `maybeCheck()`; plus a
  `setInterval(maybeCheck, 60min)`. Clean up all three on unmount.
- Split visibility:
  - `available` = `Boolean(update)` (update exists & not suppressed) → drives the
    TopRail pill (unchanged for that component).
  - `bannerDismissed` (per `latestVersion`) state + `dismissBanner()`.
  - Expose `bannerVisible = available && !bannerDismissed` for the banner.
- Keep all existing fields/behaviour (install/restart/error/progress).

### 2. `UpdateBanner.tsx` (new) — full-width top banner
- `useAppUpdater()`; render null unless `bannerVisible`.
- In-flow `<aside role="status" aria-live="polite" data-testid="app-update-banner">`
  styled like `DisconnectBanner` (inline styles + var tokens, `--color-own`).
- "Update" badge + "Skill Studio {latestVersion} is available" + clamped notes.
- Primary button: `Update now` → `installAndRestart()`; reflects
  `Installing… / Restart now / Restarting…`; disabled while in-flight.
- Error row when `phase==='error'`; action stays retryable.
- Dismiss × → `dismissBanner()`.

### 3. `App.tsx` — wiring
- `banner={<><UpdateBanner /><DisconnectBanner connected={sseConnected} /></>}`.
- Remove `<AppUpdateToast />` mount + import. Keep `<AppUpdateButton />` slot.

### 4. Remove `AppUpdateToast.tsx` + its test
- Banner subsumes it. Delete component + `__tests__/AppUpdateToast.test.tsx`.

### 5. Rust `updater.rs` — error backoff
- Add `AUTO_CHECK_ERROR_RETRY_SECS` (3600). In `spawn_auto_check_task`, when the
  check returns `Err`, sleep the short retry instead of the 24h interval.
  Success path unchanged (24h).

## Test Strategy (TDD)
- `__tests__/UpdateBanner.test.tsx`: shows on available; version + Update now;
  install→restart wiring; error stays retryable; hidden when not available.
- `__tests__/useAppUpdater.recheck.test.tsx`: focus triggers re-check; throttle
  blocks a second check within 30min; interval re-checks; dismissBanner hides
  banner but keeps `available` true (pill stays).
- Existing `AppUpdateButton.test.tsx` must stay green (no dismiss coupling).
- Rust: extend updater test module to assert the error-retry constant wiring is
  reachable (or a focused unit on the backoff selection if feasible).

## Verify
- `npm run build` (tsc) + `npm run build:eval-ui` (vite) green.
- `npx vitest run src/eval-ui` green.
- `cargo build` (src-tauri) green for the Rust change.

## Release
- `bash scripts/release/release-desktop.sh 1.0.52` → tag desktop-v1.0.52, CI
  signs/notarizes, route handler + latest.json redeployed. Confirm
  `curl https://verified-skill.com/desktop/latest.json` shows 1.0.52.

## Risks
- Banner desktop-gated → unit tests (mocked bridge) are the proof; full native
  e2e proven once v1.0.52 ships and a v1.0.51 app updates to it.
- Throttle must not block the very first foreground check (lastCheckAtRef starts
  at 0).
