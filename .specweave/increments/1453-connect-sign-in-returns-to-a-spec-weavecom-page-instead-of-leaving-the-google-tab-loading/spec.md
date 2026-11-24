# Connect sign-in returns to a spec-weave.com page instead of leaving the Google tab loading

## Problem

After a Connect sign-in from the desktop app, the browser tab can stay on Google's "Choose an account… to continue to spec-weave.com" page, greyed out with its progress bar stuck, even though the app receives the sign-in.

Cause, confirmed November 23, 2026 on M5:

- The desktop app asks Clerk to send the browser back to `studio://app/` (`apps/desktop/src/app/DesktopClerkOAuthTransport.ts:101-105`; the SDK's `buildRedirectUrl` in `@clerk/electron` 0.0.44 `dist/esm/index.js:38-40`). Clerk's `oauth_callback` answers with a 302 straight to that custom scheme.
- Chrome hands a custom-scheme navigation to the OS and commits no page, so the tab keeps the last committed page. When that is Google's account chooser, it stays in its "submitting" state forever.
- Evidence (browser history, not a live run): copies of every Chrome profile's `History` on M5 hold 115, 8 and 17 Google sign-in URLs for `clerk.spec-weave.com`, and zero URLs under `https://clerk.spec-weave.com/`. The last Connect sign-in in the Default profile (November 23, 00:06:41) ends on `accounts.google.com/v3/signin/accountchooser` with nothing after it. Loopback sign-ins by other tools in the same profile do commit their `127.0.0.1/oauth2callback` page.
- Why it varies by account (inference): an account that goes straight through hands off from the chooser, which keeps its overlay; an account that needs a password, 2-step or consent page hands off from that page, which looks finished. A profile that has not ticked "Always allow" shows Chrome's "Open SpecWithCode?" dialog, which makes the hand-off visible.

## Scope

In: an https return page on spec-weave.com that forwards to `studio://app/` with the same query; the production desktop app sending Clerk to that page; the Clerk redirect allowlist entry, applied by a reviewed workflow; the Connect setup docs.

Out: development builds (`studio-dev://app/` stays direct); iOS, Android and the CLI sign-in; the app's callback matching, token storage and passkeys.

## Acceptance Criteria

- [ ] AC-01: `https://spec-weave.com/connect/return/` loads with no external scripts and `no-referrer`. With a successful callback query it says "Signed in. Return to SpecWithCode", removes the query from the address bar, navigates once to `studio://app/` plus the exact original query, and shows an "Open SpecWithCode" button that repeats that navigation. With `__clerk_status=failed` it says sign-in did not finish and still forwards, so the app shows Clerk's error. With no query it shows neutral text and does not navigate. The target scheme and host are fixed in the page and never read from the URL.
- [ ] AC-02: The production desktop app answers the SDK's `clerk:oauth-transport:get-redirect-url` request with `https://spec-weave.com/connect/return/`, from a window's main frame only. Development keeps `studio-dev://app/`. The callback listener still accepts only `studio://app/` (unchanged `isClerkOAuthCallbackUrl`). Unit tests cover both answers, the main-frame refusal, and cleanup.
- [ ] AC-03: A `workflow_dispatch` workflow on `main`, in the `production` environment, adds `https://spec-weave.com/connect/return/` to the Clerk instance's redirect URLs if missing and never prints the secret. After it runs, the FAPI probe (`POST https://clerk.spec-weave.com/v1/client/sign_ins?_is_native=true`, `strategy=oauth_google`) accepts that redirect and still refuses `https://evil.example/x`.
- [ ] AC-04: `docs/operations/connect-setup.md` and `connect-launch.md` list the new allowlist entry and say why.
- [ ] AC-05: Release order holds: allowlist accepted and page live (a headless load of the live page with a fake query attempts `studio://app/?<same query>`) before the app release is requested.

## Approach

1. Page: `repositories/anton-abyzov/specweave/docs-site/static/connect/return/index.html`, a static file deployed by `deploy-docs.yml` on push to `develop`. Inline script and style only.
2. Desktop: `installClerkOAuthTransport` gets a separate `browserRedirectUrl` and takes over the SDK's redirect-URL channel; `redirectUrl` (callback match) is unchanged. `DesktopClerk.ts` passes the page for production.
3. Workflow `.github/workflows/clerk-redirect-allowlist.yml` (Clerk Backend API `GET/POST /v1/redirect_urls`).
4. Docs.

Risks: the callback query (Clerk's single-use `rotating_token_nonce`) now reaches spec-weave.com's host logs. It is bound to the app's Clerk client and used within seconds; the page strips it from history and sends no referrer. If Clerk refuses the https entry, stop: the design depends on it. The real Clerk round trip is only tested by the user after release.

Rejected: a page that closes the tab (Chrome refuses `window.close()` for tabs a script did not open); Clerk popup mode (no popup in the system browser).

## Decisions

### Asked
- D-01 Return to an https page on spec-weave.com that forwards to the app → approved by the user (November 23, 2026; auth change)
### Defaulted (change any before sw-do)
- D-02 Production only; development stays on `studio-dev://app/` → default (reversible)
- D-03 Allowlist applied by a reviewed workflow, because the Clerk secret lives only in the `production` GitHub environment → default
### Open
- none

## Tasks

### T-01 Return page on spec-weave.com
- AC: AC-01 | Files: repositories/anton-abyzov/specweave/docs-site/static/connect/return/index.html | Test: headless load of the page with and without a query records the attempted navigation

### T-02 Desktop sends Clerk to the return page
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerkOAuthTransport.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerkOAuthTransport.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerk.ts | Test: vp test run apps/desktop/src/app/DesktopClerkOAuthTransport.test.ts

### T-03 Clerk allowlist workflow and docs
- AC: AC-03, AC-04 | Files: repositories/anton-abyzov/specwithcode/.github/workflows/clerk-redirect-allowlist.yml, repositories/anton-abyzov/specwithcode/docs/operations/connect-setup.md, repositories/anton-abyzov/specwithcode/docs/operations/connect-launch.md | Test: FAPI probe accepts the page and refuses evil.example

### T-04 Ship in order
- AC: AC-05 | Files: none | Test: live page check, then request-release.sh
