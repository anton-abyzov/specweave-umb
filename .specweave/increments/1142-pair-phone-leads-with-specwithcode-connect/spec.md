# 1142 Pair phone leads with SpecWithCode Connect

## Problem

Anton (2026-10-29, queued in the mobile Codex session and repeated after build 13 was accepted): "Why choose Tailscale? Should use our specwithcode connect tool because Tailscale is just a fallback." The screenshot shows the desktop "Pair your iPhone with a QR code" dialog whose first instruction is "Install Tailscale on your iPhone." The Settings page order is already correct (PhoneConnectSettings first; PairPhoneSettings folded when Connect is shown), and iOS build 13 fixed reconnect priority. What still reads wrong is the QR dialog itself: it names Connect only as a comparison and gives no action to switch to the Connect path, so anyone landing in it is led down the Tailscale route.

## Scope

In: desktop web pairing dialog only (`apps/web/src/components/settings/PhoneSetupDialog.tsx`, `PairPhoneSettings.tsx`). Out: iOS app (increment 1139 / PR #999 covers it), pairing credential server flow, Tailscale HTTPS setup.

## Acceptance Criteria

- [ ] AC-01: The QR pairing dialog names SpecWithCode Connect as the recommended way first and offers one clear action to go there (close dialog and scroll to the Connect section) before any Tailscale step.
- [ ] AC-02: Tailscale wording reads as the private fallback it is ("Only for the private fallback…"), while the QR flow itself still works unchanged for people who choose it.
- [ ] AC-03: Existing pairing behavior (generate, expiry, route-changed, copy address/code) is unchanged; web typecheck and the pairing component tests pass.
- [ ] AC-04: Anton accepts the new UI in the installed app before it ships (manual acceptance for new UI).

## Approach

Add a Connect action to the dialog header/description (new callback prop from PairPhoneSettings that closes the dialog and scrolls to PhoneConnectSettings), reorder description copy Connect-first, keep instructions per address hint. Visual check via the installed app after release; headless component evidence before.

## Decisions

### Asked
- D-01 Connect primary, Tailscale fallback (Anton, twice, 2026-10-29).
### Defaulted (change any before sw-do)
- D-02 Keep the QR dialog and flow; change hierarchy + copy + one navigation action only (reversible).
### Open
- AC-04 manual UI acceptance by Anton.

## Tasks

### T-01 Connect-first pairing dialog
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/settings/PhoneSetupDialog.tsx, apps/web/src/components/settings/PairPhoneSettings.tsx | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave-studio && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json

## Receipts

- 2026-10-29 evidence: queued Codex screenshot reviewed; dialog is the folded QR alternative in ConnectionsSettings (PhoneConnectSettings renders first, PairPhoneSettings folded={isPhoneConnectShown()}), so the remaining defect is dialog hierarchy/copy, not route priority. iOS side accepted as build 13 on iPhoneA (increment 1139).
