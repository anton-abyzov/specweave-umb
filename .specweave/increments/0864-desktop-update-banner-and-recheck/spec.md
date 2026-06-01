# 0864 — Desktop update banner + reliable re-check

## Problem

Skill Studio desktop (Tauri) does not reliably surface a newer version to a
running app. The update plumbing exists (Rust `tauri-plugin-updater` +
`useAppUpdater` + a TopRail pill + a floating toast — all added untracked in
commit `94c4738`, never specced), but **detection cadence is broken**:

- The frontend (`useAppUpdater`) checks **only on mount**. A continuously
  running app never re-checks.
- The Rust auto-check loop is gated to **once per 24h** (`last_checked_at + 24h`).
- The only surfaces are a small TopRail pill and a dismissible floating toast —
  easy to miss. There is no prominent "big update button at the top."

### Reproduction (this Mac, 2026-06-01)
- Installed app: **v1.0.50**; latest published: **v1.0.51**.
- `~/.vskill/settings.json`: `auto_check: true`, `skipped_version: null`,
  `last_checked_at: "2026-05-31T23:27:55Z"`.
- App launched May 31 23:27 UTC → on-mount check found 1.0.50 (latest at the
  time) → "up to date". v1.0.51 published **5h later** (Jun 1 04:23 UTC). The
  running app will not re-check until Jun 1 23:27 UTC (~18h), so no update is
  ever surfaced. The user perceives auto-update as "not working."

## Goal

Make a published desktop release surface **promptly and prominently** in every
running app, via a reliable foreground re-check and a big full-width top banner.

## User Stories

### US-001 — Prompt background re-check
As a Skill Studio desktop user who keeps the app open, I want the app to detect
a newly published version within minutes of focusing it, so I am not stuck on a
stale build for up to 24h.

**Acceptance Criteria**
- [ ] AC-US1-01: `useAppUpdater` re-checks for updates on `window` focus and on
  `document.visibilitychange` → visible (desktop bridge only).
- [ ] AC-US1-02: `useAppUpdater` runs a foreground interval re-check while the
  app is open (≈ hourly), independent of the Rust 24h gate.
- [ ] AC-US1-03: All foreground re-checks are throttled to a minimum spacing
  (≥ 30 min since the last successful check) so focus/blur churn cannot spam the
  update endpoint.
- [ ] AC-US1-04: The on-mount check behavior is preserved (still checks at boot
  when `autoCheck` is on).

### US-002 — Big top-of-window update banner
As a user, I want an unmissable full-width banner at the very top of the studio
when a newer Skill Studio is available, with a one-click update.

**Acceptance Criteria**
- [ ] AC-US2-01: A full-width `<UpdateBanner/>` renders above the top rail (in
  `StudioLayout`'s `banner` slot) when an app update is available and not
  banner-dismissed. `data-testid="app-update-banner"`.
- [ ] AC-US2-02: The banner shows "Skill Studio vX.Y.Z is available", release
  notes (if any), an "Update now" primary button, and a dismiss (×) control.
- [ ] AC-US2-03: Clicking "Update now" downloads+installs then restarts (drives
  the existing `installAndRestart` flow); progress and "Restart now" states are
  reflected in the banner.
- [ ] AC-US2-04: On install error the banner stays visible, shows the error, and
  the action remains retryable.
- [ ] AC-US2-05: The banner only renders inside the Tauri desktop shell; in
  `npx vskill studio` (browser) it renders nothing.

### US-003 — Dismiss without losing the update path
As a user, I want to dismiss the big banner but still have a compact way to
update.

**Acceptance Criteria**
- [ ] AC-US3-01: Dismissing the banner hides the banner for that version but the
  compact TopRail pill (`AppUpdateButton`) remains visible while the update
  exists.
- [ ] AC-US3-02: The redundant floating `AppUpdateToast` is removed (its
  responsibilities — progress, error, restart — move into the banner) so a
  single "update available" signal does not appear in three places.
- [ ] AC-US3-03: A newly detected, higher version re-shows the banner even if a
  previous version was dismissed.

### US-004 — Resilient background checks
As a user on a flaky network, I want a failed background check to retry soon, not
blackhole for a full day.

**Acceptance Criteria**
- [ ] AC-US4-01: The Rust auto-check loop retries after a short backoff
  (≈ 1h) when a check errors, instead of sleeping the full 24h interval.
- [ ] AC-US4-02: A successful background check keeps the existing 24h cadence.

### US-005 — Ship it
- [ ] AC-US5-01: `npm run build`, `npm run build:eval-ui`, and the eval-ui unit
  suite pass.
- [ ] AC-US5-02: A new signed desktop release **v1.0.52** is published via
  `scripts/release/release-desktop.sh 1.0.52`; `verified-skill.com/desktop/latest.json`
  serves 1.0.52.

## Out of Scope
- Beta/channel infra, in-app changelog viewer, system tray indicator.
- Browser-mode (npx studio) self-update / CLI-update nudge.
- Changing the signing keys or release transport (route handler stays).

## Notes
- Desktop version stream (Cargo/tauri, 1.0.51) is independent of the npm CLI
  `vskill` package.json (1.0.19) — by design. Only the desktop stream bumps.
