# Signed out of Connect: say so plainly, warn before it ends, and label each machine by the real reason

## Problem

On November 18, 2026 at 11:38 AM the m4 window lost its SpecWithCode Connect sign-in with no warning. From then on the Threads panel put all five M5 threads under **Offline** with **Not connected** on each row, while M5 was running and m4's own server still reached it (`studio_machine_list`: M5 `ready`, `reachable: true`). The only hint was "Not signed in" in small type at the bottom of the sidebar. m1, m3 and linux-mini threads kept working, which made the account state look unrelated.

What happened, from Clerk's records and the window's traces (`reports/2026-11-18-signout-findings.md`):

1. **Expiry, not a sign-out, revoke, update or device-approval change.** The window's Clerk session was created November 11 at 11:38:00 AM and ended at 11:38:00 AM today with status `expired`. Every session on the instance has `expire_at = created + 7 days`: the Hobby plan's fixed maximum lifetime. The account has no `ended`, `revoked` or `removed` sessions, so `ConnectSessionGuard`'s `signOut()`, a device removal (1406, 1416) and the 1.0.357 update did not end it. Short-lived tokens refresh silently today; nothing can stretch a session past its maximum lifetime.
2. **Why only M5.** 22 seconds after expiry (11:38:22 AM) the window's attempt to M5 was refused with `ConnectionBlockedError{reason:"authentication"}`, "Your cloud sign-in changed. Sign in again to authorize the environment." M5 is reached from this window only through the Connect relay (`RelayConnectionTarget`). m1, m3 and linux-mini are also saved with a direct paired route (`BearerConnectionTarget`, a stored credential over Tailscale or the LAN), which needs no Connect sign-in. It is not the `identity-mismatch` pattern.
3. **Why "Offline / Not connected".** A blocked connection stops retrying, its phase becomes `error`, its reach state `stopped`, and `hostDownWord` maps `stopped` to "Not connected". The Threads panel groups every down host's threads under "Offline". Nothing on the row says the fix is one sign-in.
4. **It will happen again every week on every window.** The account has 11 more Electron window sessions; one ends today at 2:43 PM and five on November 19. Each window signs out on its own 7-day clock.

Side findings, handed to their owners: linux-mini is `grant_revoked` in the fleet yet the window still connects by bearer (device trust, 1416); one of m1's saved bearer routes fails with "The environment credential is invalid." every attempt while another works; the window's first relay attempt at start can be refused with "sign-in changed" for about one second before the session activates.

## Scope

In:

1. **Labels (ship after review and green CI).** Every place that names a machine's state says the real reason: needs sign-in, not reachable from here, offline. A banner says the window is signed out and what that breaks, with a Sign in button.
2. **Session behaviour (needs Anton's acceptance before release).** A warning before a sign-in ends with a one-click renew, no silent sign-out by `ConnectSessionGuard`, and the Clerk lifetime decision (D-01).

Out: device approval and the device list (1416); "Needs you" and blocked thread labels (1412); the Settings > Connect machine list `CloudEnvironmentConnectList.tsx` (1416 edits it); retry behaviour of any connection; re-pairing m1's stale route; letting a window reach relay-only machines through its own machine's Connect link (D-01 option C, a separate increment if chosen).

## Acceptance Criteria

### Labels

- [ ] AC-01: A connection refused because this window has no Connect sign-in carries a structured flag (`connectSignInRequired` on `ConnectionBlockedError` and on the connection presentation), set only where the Connect session is missing, unavailable or changed. A machine's own credential refusal (m1's "environment credential is invalid", a revoked pairing, a reapproval) never sets it. No retry, backoff or route choice changes.
- [ ] AC-02: A thread row, thread link chip and project thread card on a machine down for that reason read **Needs sign-in** instead of "Not connected" or "Host offline".
- [ ] AC-03: A down machine that this machine's server reaches (the fleet snapshot says `reachable`) and that does not need a sign-in reads **Not reachable from here** instead of "Not connected", "Not answering" or "Host offline". With no fleet snapshot, today's words stay.
- [ ] AC-04: Priority when several apply: "Different machine at address", then "Needs sign-in", then "Not reachable from here", then today's reach words. "No network" on this device keeps its own words.
- [ ] AC-05: The Threads panel group that holds unreachable machines' threads is headed **Not reachable from here** instead of "Offline". Its key, order and collapse state stay the same.
- [ ] AC-06: The chat banner of a thread on a machine that needs sign-in reads "Sign in to reach {machine}" with the line "{machine} is reached through SpecWithCode Connect and this window is signed out. Work there keeps running." The composer's machine picker and Settings > Machines say "Needs sign-in" for it.
- [ ] AC-07: When this window is signed out and at least one saved machine needs sign-in, a banner at the top of the Threads panel says "Signed out of SpecWithCode Connect", names the machines it cuts off ("M5 can't be opened from this window"), says what still works ("Agents keep running there; m1, m3 and linux-mini are not affected" when those are connected), and has a **Sign in** button that opens the existing sign-in. With nothing cut off, no banner shows: Connect stays optional.
- [ ] AC-08: The account button reads "Signed out" with a warning tone while a machine needs sign-in; otherwise it keeps "Not signed in".
- [ ] AC-09: After signing in, machines that needed sign-in reconnect without a restart (the blocked connection wakes on `credentials-changed`), and the banner and labels clear.
- [ ] AC-10: New strings exist in all eight phrase files.

### Session behaviour (held for Anton's acceptance)

- [ ] AC-11: From 24 hours before the window's Connect session ends (`session.expireAt`), the account button shows "Sign-in ends in {time}" and its menu offers **Sign in again now**. From 2 hours before, the Threads panel banner says "Your Connect sign-in ends at {time}. Sign in again to keep reaching {machines}." The warning shows only when a machine depends on the sign-in.
- [ ] AC-12: **Sign in again now** renews without leaving the window signed out longer than the browser step: with multi-session on, the new session is made active before the old one ends; with single-session (today), it signs out and opens the sign-in in the same click, and a cancelled sign-in shows the signed-out banner (AC-07), never a silent state.
- [ ] AC-13: `ConnectSessionGuard` never signs out by itself. When the relay refuses a fresh token twice, the window shows "SpecWithCode Connect did not accept this sign-in" with **Sign in again**; signing out stays a person's choice. A local key or proof error (`ManagedRelayDpopKeyLoadError`, proof creation) never counts as a refusal.
- [ ] AC-14: A token refresh that fails for a network reason keeps reading as reconnecting, never as signed out (regression test on today's mapping).
- [ ] AC-15: The Clerk instance's maximum session lifetime matches D-01, set in the Clerk dashboard (Sessions). Only new sessions get it.

## Approach

Labels, in order:

1. `packages/client-runtime/src/connection/model.ts`: `connectSignInRequired?: boolean` on `ConnectionBlockedError`, next to `reapprovalRequired`.
2. Set it at the three Connect-session refusals: `authorization/service.ts` `sessionChanged()`; `apps/web/src/connection/platform.ts` `clerkToken` (no session, null token); `apps/mobile/src/connection/platform.ts`, the same two.
3. `connection/presentation.ts`: carry `connectSignInRequired: true` on a blocked presentation, as it carries `reapprovalRequired`.
4. `apps/web/src/lib/machineStatus.ts`: one `HostDownNote` (`identity-mismatch | needs-sign-in | reachable-from-machine`) replaces the `identityMismatch` boolean in `hostDownWord`, `machineReachWords` and `identityMismatchShown`, with AC-04's priority. New words: NEEDS_SIGN_IN, REACHABLE_FROM_MACHINE.
5. `apps/web/src/studio/unreachableHosts.tsx`: one `HostDownNoteContext` (environment id to note) built from the presentations (`connectSignInRequired`), the fleet snapshot's `identity-mismatch` and `reachable` statuses; `useHostIdentityMismatch` becomes `useHostDownNote`. Call sites: `ThreadsPane.tsx`, `ThreadLinkChip.tsx`, `ProjectThreadCards.tsx`, `projectThreadCards.ts`, `threadMachine.ts`, `ChatView.tsx`, `ProjectExecutionHistory.tsx`, `ProjectWorkspaceSurface.tsx`, `environmentUnavailableBanner.ts`, `shellModel.ts` `threadStatusWord`.
6. Group heading: a display label for the `Offline` group key in `ThreadsPane.tsx`; the key stays.
7. `SignedOutBanner` in the Threads panel and the account button tone, reusing `useStudioConnectAuthPrompt().openAuthPrompt`.
8. Phrases in `apps/web/src/i18n/phrases/*.ts`.

Session behaviour (after D-01): read `useSession().session.expireAt` in `ConnectSidebarAccountMenu.tsx`; a renew action in the account menu; `ConnectSessionGuard.tsx` reports instead of `signOut()`; the Clerk dashboard change.

Rejected:

- Matching error text ("Sign in to SpecWithCode Connect") to find the reason: brittle and translated; a structured flag is what `reapprovalRequired` already does.
- A new `MachineReachState` in the client runtime: every exhaustive switch, the mobile app and the Android port would change for a wording fix. The note lives in the web layer.
- Keying "needs sign-in" on `blockedReason === "authentication"`: m1's stale bearer refusal has the same reason and is fixed by pairing again, not by signing in.
- Retrying blocked relay connections on a timer: a missing sign-in never fixes itself, and the wake on `credentials-changed` already covers the fix.

Risks: 1412 edits `shellModel.ts` and `ThreadsPane.tsx` (rebase after it merges); the fleet snapshot can be stale by one poll, so "Not reachable from here" can lag a machine going down by up to one fleet read.

## Mockup

`mockups/signed-out.html`, screenshot `mockups/signed-out.png`: today's panel, the labelled panel with the signed-out banner, the chat banner, and the held expiry warning.

## Review

Adversarial reviewer: Muse Wonderful (`muse-wonder-full-1.0`, xhigh, full access), spec first, then the labels PR. Rounds in `reports/reviews/`.

## Decisions

### Asked
- D-01 How long a Connect sign-in lasts and how a window renews it → pending (Anton). Options: A, a paid Clerk Pro plan with a 90-day lifetime, plus AC-11 to AC-14; B, stay on the free plan's fixed 7 days, plus AC-11 to AC-14; C, B now and a separate increment where a window reaches its own machines through its machine's long-lived Connect link. Recommended: A.
### Defaulted (change any before sw-do)
- D-02 The reason is a structured flag on the refusal, not error text → default.
- D-03 The group heading reads "Not reachable from here" → default.
- D-04 The signed-out banner shows only when a saved machine needs the sign-in → default.
- D-05 Labels (AC-01 to AC-10) ship after review and green CI; AC-11 to AC-15 wait for Anton's acceptance → default.
### Open
- D-01

## Tasks

### T-01 Flag Connect-session refusals and carry the flag to the presentation
- AC: AC-01, AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/model.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/service.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/presentation.ts, repositories/anton-abyzov/specwithcode/apps/web/src/connection/platform.ts, repositories/anton-abyzov/specwithcode/apps/mobile/src/connection/platform.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/presentation.test.ts | Test: `node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/connection/presentation.test.ts`

### T-02 Say the real reason on rows, chips, cards, banners and pickers
- AC: AC-02, AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/lib/machineStatus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/unreachableHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectThreadCards.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadLinkChip.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectThreadCards.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/threadMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/environmentUnavailableBanner.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/lib/machineStatus.test.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/lib/machineStatus.test.ts apps/web/src/studio/shellModel.test.ts apps/web/src/components/chat/environmentUnavailableBanner.test.ts`

### T-03 Head the unreachable group "Not reachable from here"
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/ThreadsPane.test.tsx`

### T-04 Signed-out banner and account button tone
- AC: AC-07, AC-08, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/SignedOutBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/signedOutBanner.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/accountMenuModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ConnectSidebarAccountMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/signedOutBanner.test.ts apps/web/src/components/account/accountMenuModel.test.ts`

### T-05 Headless proof of the signed-out window
- AC: AC-02, AC-05, AC-07, AC-09 | Files: none in the repository; evidence in reports/ | Test: headless fixture with a relay-only machine and no Connect session, screenshots before and after sign-in

### T-06 Warn before a sign-in ends and renew in one click (after D-01)
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ConnectSidebarAccountMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/accountMenuModel.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/account/accountMenuModel.test.ts`

### T-07 No silent sign-out by the relay guard (after D-01)
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectSessionGuard.tsx | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/cloud/ConnectSessionGuard.test.tsx`

### T-08 Clerk session lifetime (Anton, Clerk dashboard)
- AC: AC-15 | Files: none | Test: a new session's `expire_at` minus `created_at` equals the chosen lifetime (Clerk Backend API, read-only)
