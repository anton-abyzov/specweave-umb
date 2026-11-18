# Signed out of Connect: say so plainly, warn before it ends, and label each machine by the real reason

## Problem

On November 18, 2026 at 11:38 AM the m4 window lost its SpecWithCode Connect sign-in with no warning. From then on the Threads panel put all five M5 threads under **Offline** with **Not connected** on each row, while M5 was running and m4's own server still reached it (`studio_machine_list`: M5 `ready`, `reachable: true`). The only hint was "Not signed in" in small type at the bottom of the sidebar. m1, m3 and linux-mini threads kept working, which made the account state look unrelated.

What happened, from Clerk's records and the window's traces (`reports/2026-11-18-signout-findings.md`):

1. **Expiry, by strong inference.** No trace names the window's Clerk session, so this is inference, not proof. The session that fits is `sess_3Ly8jIf9…`: created November 11 at 11:38:00 AM, `expired` at 11:38:00 AM today, last active 11:32:51 AM. M5 RPCs succeed until 11:36:38 AM, and the refusal lands at 11:38:22 AM. Every session on the instance has `expire_at = created + 7 days`: the Hobby plan's fixed maximum lifetime. The account has no `ended`, `revoked` or `removed` sessions. That rules out `ConnectSessionGuard`'s `signOut()`, assuming Clerk records a programmatic sign-out as `ended`. It also rules out a device removal (1406, 1416) and the 1.0.357 update. Two sessions stay unexplained:
   - a second Mac Electron session (`sess_3Ly8j3on…`, last active 8:50 AM) expired two seconds earlier;
   - a new Mac Electron session (`sess_3MHuSLYz…`) signed in at 11:36:52 AM and was last active at 11:38:21 AM. It is not this window, which stayed signed out. Which window it is remains unknown.
2. **The 22 seconds.** Clerk noticed the expiry on its next token refresh and flipped the window to signed out. `ManagedRelayAuthProvider` then cleared the relay account, which emits `credentials-changed`. The supervisor replaced the live relay lease (`supervisor.ts:704`), and the new attempt was refused with `ConnectionBlockedError{reason:"authentication"}`: "Your cloud sign-in changed. Sign in again to authorize the environment."
3. **Why only M5.** M5 is reached from this window only through the Connect relay (`RelayConnectionTarget`). m1, m3 and linux-mini are also saved with a direct paired route (`BearerConnectionTarget`, a stored credential over Tailscale or the LAN), which needs no Connect sign-in. A learned bearer route can also borrow the Connect credential (`authorization: "studio-connect"`, `routes.ts:248`) and dies with the session the same way. It is not the `identity-mismatch` pattern.
4. **Why "Offline / Not connected".** A blocked connection stops retrying, its phase becomes `error`, its reach state `stopped`, and `hostDownWord` maps `stopped` to "Not connected". The Threads panel groups every down host's threads under "Offline". Nothing on the row says the fix is one sign-in.
5. **The merged labels likely miss the relay-only case (found after #621 and #628 merged).** `ManagedRelayAuthProvider` runs account cleanup on every settled sign-out, including a natural expiry and a cold load that starts signed out. The provider's first observed account is `undefined`, and the test is `!== null`. A probe of the provider counted one `removeRelayEnvironments` call on a cold signed-out load and one on signed-in to signed-out. That cleanup deletes every machine whose only route is the relay, with its cache and its data (`registry.test.ts`, "removes all relay-owned data"). So a machine like M5 can be gone before any surface says "Needs sign-in". Two things are unproven. It is unknown why M5 still showed after the incident: either its row came from another source, or the cleanup did not finish. A platform-owned entry fails `removeRoute` with `PlatformEnvironmentRemovalError`, which `removeRelayEnvironments` does not catch. AC-16 keeps the machines.
6. **It will happen again every week on every window.** The account has 11 more active Electron window sessions; one ends today at 2:43 PM and four on November 19. Each window signs out on its own 7-day clock.

Side findings, handed to their owners:
- linux-mini is `grant_revoked` in the fleet, yet the window still connects by bearer (device trust, 1416).
- One of m1's saved bearer routes fails with "The environment credential is invalid." on every attempt, while another works.
- At start, the window's first relay attempt is refused with "sign-in changed" for about a second, before Clerk hands the session to the relay client (AC-02 keeps that from reading as a sign-out).

## Scope

In:

1. **Labels (ship after review and green CI).** Every place that names a machine's state says the real reason: needs sign-in, not reachable from here, offline. A banner says the window is signed out and what that breaks, with a Sign in button.
2. **Session behaviour (needs Anton's acceptance before release).** A warning before a sign-in ends, a one-click renew, and no silent sign-out by `ConnectSessionGuard`. The lifetime stays Clerk's free 7 days (D-01).

Out:
- Device approval and the device list (1416).
- "Needs you" and blocked thread labels (1412).
- The Settings > Connect machine list `CloudEnvironmentConnectList.tsx` (1416 edits it).
- Retry behaviour and route choice of any connection, including a machine whose direct route only times out (see AC-02).
- Re-pairing m1's stale route.
- The phone apps: `apps/mobile` sets the flag (shared refusal code) but shows no new words. Phones get the same 7 days; that is a separate increment.
- The CLI's OAuth credential and the server's environment link.
- Letting a window reach relay-only machines through its own machine's Connect link (D-01 option C, a separate increment if chosen).

## Acceptance Criteria

### Labels

- [ ] AC-01: A connection refused because this window has no Connect session carries a structured flag (`connectSignInRequired` on `ConnectionBlockedError` and on the connection presentation). It is set only when the window has no Connect session at refusal time: the cloud identity is `None`, or there is no Clerk token. These never set it:
  - an account switch (the identity is another account's);
  - a relay refusal of a token (`RelayAuthInvalidError`, proof expiry), which can mean a wrong account or a server fault. When the session has really ended, Clerk flips to signed out within one refresh and the next attempt is flagged;
  - a machine's own credential refusal (m1's "environment credential is invalid", a revoked pairing, a reapproval).

  No retry, backoff or route choice changes.
- [ ] AC-02: A thread row, thread link chip and project thread card on a machine down for that reason read **Needs sign-in** instead of "Not connected" or "Host offline". The words show only once Clerk has loaded and says this window is signed out. While Clerk loads, or while a signed-in session is still being handed to the relay client, the flag is dropped and today's words stay, so a cold start never flashes "Needs sign-in". This covers attempts that end blocked. The driver reports a transient route error over a blocked one (`driver.ts:143`), so a machine whose direct route only times out keeps its retrying words. That is a stated limit, and none of today's machines is such a machine.
- [ ] AC-03: A machine this window is still retrying ("Not answering", "Offline", "Can't reach host") that the primary's fleet snapshot lists as `reachable` reads **Not reachable from here**. These keep today's words:
  - a stopped connection, which already knows its reason (needs an update, pair again, a refused credential);
  - a machine nobody asked to connect;
  - a saved machine missing from the fleet file, or no fleet at all;
  - "No network" on this device.
- [ ] AC-04: Priority when several apply:
  1. "Different machine at address";
  2. "Needs sign-in";
  3. a stopped connection's own reason ("Needs update", "Not connected", pair again);
  4. "Not reachable from here", for retrying states only;
  5. today's reach words.
- [ ] AC-05: Where threads are grouped by status, the group that holds unreachable machines' threads is headed **Not reachable from here** instead of "Offline". That is the Threads panel and the sidebar Chats list; `projectWorkspaceModel.ts` only orders groups and shows no heading. The group key, order and fold state stay "Offline".
- [ ] AC-06: The chat banner of a thread on a machine that needs sign-in is a warning, not an error. It reads "Sign in to reach {machine}" with the line "This window reaches it through SpecWithCode Connect and is signed out. Sign in to reach it again." It has no Retry. These also say "Needs sign-in" for it:
  - the composer's machine picker (`DraftMachinePicker.tsx`);
  - Settings > Machines (`MachinesSettings.tsx`);
  - the saved machine rows in Settings > Connections (`ConnectionsSettings.tsx`).

  This machine never shows it.
- [ ] AC-07: When Clerk says this window is signed out and at least one saved machine needs sign-in, a banner at the top of the Threads panel reads "Signed out of SpecWithCode Connect", with a **Sign in** button that opens the existing sign-in. Its body says only what the window knows:
  - "{machine} is running, but this window can't reach it until you sign in" for a machine the fleet says is reachable;
  - "{machines} can't be reached from this window until you sign in" for the others;
  - "This machine is not affected.";
  - "Still connected: {machines}." for machines with a live session now.

  Names are joined in the window's language (`Intl.ListFormat`). With nothing cut off, no banner shows: Connect stays optional.
- [ ] AC-08: The account button reads "Signed out" with a warning tone while a machine needs sign-in; otherwise it keeps "Not signed in".
- [ ] AC-09: After signing in, machines that needed sign-in reconnect without restarting the app, and the banner and labels clear. The blocked connection wakes on `credentials-changed` (`supervisor.ts:1117`, test `supervisor.test.ts:1081`). An Electron sign-in may reload the window.
- [ ] AC-10: New strings exist in all eight phrase files.

### Session behaviour (held for Anton's acceptance)

- [ ] AC-11: From 24 hours before the window's Connect session ends (`session.expireAt`), the account button shows "Sign-in ends in {time}" and its menu offers **Sign in again now**. From 2 hours before, the Threads panel banner says "Your Connect sign-in ends at {time}. Sign in again to keep reaching {machines}." The warning shows only when a saved machine depends on the sign-in: it has no session-free route (a bearer route without `authorization: "studio-connect"`, SSH, or the primary), computed from its routes.
- [ ] AC-12: **Sign in again now** renews without emptying the window. It signs out of Clerk, then opens the sign-in again by itself, after the reload where there is one. Account cleanup keeps the saved machines (AC-16). A cancelled renew leaves the saved machines in place and shows the signed-out banner (AC-07), never a silent or emptied state. After a renew, the Connect onboarding dialog does not open again. Spike result (clerk-js 6.32.1, in `node_modules`):
  - In single-session mode, `openSignIn` is a no-op while signed in (`cannot_render_single_session_enabled`).
  - Multi-session mode would not help: signing in the same account on the same client fails with `identifier_already_signed_in`.
  - Nothing on the client extends `expireAt`.
  - So a renew is a sign-out, then a sign-in.
- [ ] AC-13: `ConnectSessionGuard` never signs out by itself. When the relay refuses a fresh token twice, the window shows "SpecWithCode Connect did not accept this sign-in" with **Sign in again**; signing out stays a person's choice. A local key or proof error (`ManagedRelayDpopKeyLoadError`, proof creation) never counts as a refusal. That needs a structured marker on the discovery error (`errors.ts:112`), because both collapse into blocked `authentication` today.
- [ ] AC-14: A token refresh that fails for a network reason keeps reading as reconnecting, never as signed out (regression test on today's mapping).
- ~~AC-15: The Clerk instance's maximum session lifetime matches D-01.~~ Dropped by D-01: the lifetime stays 7 days.
- [ ] AC-16: An expired or renewed sign-in keeps the saved machines, and keeps them across a reload, so "Needs sign-in" (AC-07) has machines to name.
  - While signed in, the window stores `{accountId, expireAt}` in local storage. A renew adds the time it started.
  - At a settled sign-out, the relay machines are kept only if that record shows the session passed `expireAt` (one minute of skew), or a renew started. Every other sign-out removes them as today: a person's sign-out, a revoked or removed session, and a window with no record.
  - A different account signing in removes the kept machines before its session starts, so account B never sees account A's machines or cached threads.
  - Trade: a signed-out window keeps the cached threads of the machines it keeps.

## Approach

Labels, in order:

1. `packages/client-runtime/src/connection/model.ts`: `connectSignInRequired?: boolean` on `ConnectionBlockedError`, next to `reapprovalRequired`.
2. Set it at the Connect-session refusals: `authorization/service.ts` `sessionChanged()` only when the current identity is `None`; `apps/web/src/connection/platform.ts` `clerkToken` (no session, null token); `apps/mobile/src/connection/platform.ts`, the same two.
3. `connection/presentation.ts`: carry `connectSignInRequired: true` on a blocked presentation, as it carries `reapprovalRequired`.
4. `apps/web/src/cloud/connectAccountState.ts`: an atom with Clerk's settled account state (`unknown | signed-in | signed-out`), set by `ManagedRelayAuthProvider`. It returns to `unknown` while Clerk reloads and on unmount. `state/environments.ts` drops the flag from the projected connection unless the state is `signed-out`, together with the refusal's `blockedReason: "authentication"`. Every label reads the projected list, so the startup race never shows, not even as "Signed out".
4a. Words keyed on `blockedReason` put the Connect case first: `projectWorkspaceModel.ts` (`hostDisconnectedLabel`, `composerHostStatus`, `projectAdmissionReason`), `threadResolveAccess.ts` and `threadTitles.ts`. A machine's own refused credential keeps today's words.
5. `apps/web/src/lib/machineStatus.ts`: a `HostDownNote` (`needs-sign-in | reachable-from-machine`) next to the existing identity-mismatch check, applied in `hostDownWord` and `machineReachWords` with AC-04's priority; `NEEDS_SIGN_IN_STATUS` in `machineStatus`, `savedMachineStatus` and `machineUnavailableTitle`.
6. `apps/web/src/studio/unreachableHosts.tsx`: `HostDownNoteContext` and `FleetReachableContext`, built from the projected presentations and the primary fleet snapshot. Call sites: `ThreadsPane.tsx`, `ThreadLinkChip.tsx`, `ProjectThreadCards.tsx`, `projectThreadCards.ts`, `ChatView.tsx`, `environmentUnavailableBanner.ts`, `shellModel.ts` `threadStatusWord`; after review round 2 also `BoardThreads.tsx`, `ProjectExecutionHistory.tsx`, `IntegrationsTabStrip.tsx`, `StudioOverview.tsx` (`overviewMachines.ts`) and `HostLimits.tsx` (`hostLimitsModel.ts`).
7. Group heading: `threadGroupHeading` in `shellModel.ts`, used by the Threads panel and `buildChatGroups`; the key stays.
8. The signed-out banner (`signedOutBannerModel.ts`, `ConnectSignedOutBanner.tsx` behind the lazy `SignedOutBanner.tsx`) and the account button tone, reusing `useStudioConnectAuthPrompt().openAuthPrompt`.
9. Phrases in `apps/web/src/i18n/phrases/*.ts`.

Session behaviour (built in draft PR #632, held for acceptance):
- AC-16: `cloud/connectSessionRecord.ts` stores `{accountId, expireAt, renewStartedAt?}`; `managedAuth.tsx` skips `removeRelayEnvironments` only when the record says expired or renewing, and cleans up before a different account's session starts.
- AC-11: `cloud/connectSessionEnd.ts` (stages, recheck, `dependsOnConnectSignIn`), `useConnectSessionEnd` (one timer, plus focus and visibility), the account button's `sessionEndsIn`, and `sessionEndingBanner`.
- AC-12: `useConnectRenew` writes the renew mark and the open note, then `clerk.signOut`; `ConnectRenewResume` opens the sign-in with origin `renew`, which the onboarding dialog does not follow.
- AC-13: `ConnectSessionGuard` sets `connectSessionRejectedAtom` instead of `signOut()`; `localProofFailure` on the three local proof errors.
- AC-14: `readConnectClerkToken` extracted from `platform.ts` and tested.

Rejected:

- Matching error text ("Sign in to SpecWithCode Connect") to find the reason: brittle and translated; a structured flag is what `reapprovalRequired` already does.
- A new `MachineReachState` in the client runtime: every exhaustive switch, the mobile app and the Android port would change for a wording fix. The note lives in the web layer.
- Keying "needs sign-in" on `blockedReason === "authentication"`: m1's stale bearer refusal has the same reason and is fixed by pairing again, not by signing in.
- Retrying blocked relay connections on a timer: a missing sign-in never fixes itself, and the wake on `credentials-changed` already covers the fix.
- Ranking a flagged refusal above a transient one in the driver, as `reapprovalRequired` is: it would stop retries of a direct route that may come back by itself. That is a retry change, out of scope.
- A grace timer before showing "Needs sign-in": Clerk's own settled state is exact; a timer guesses.

Risks:
- 1412 edits `shellModel.ts` and `ThreadsPane.tsx`; rebase after it merges.
- The fleet snapshot is polled every ten seconds, so "Not reachable from here" and "is running" can lag by one fleet read.
- Down words wait out the 60-second reconnect grace (`reach.ts:18`) as today.

## Mockup

`mockups/signed-out.html`, screenshot `mockups/signed-out.png`: today's panel, the labelled panel with the signed-out banner, the chat banner, and the held expiry warning.

## Review

Adversarial reviewer: Muse Wonderful (`muse-wonder-full-1.0`, xhigh, full access), spec first, then the labels PR. Rounds in `reports/reviews/`.

## Decisions

### Asked
- D-01 How long a Connect sign-in lasts and how a window renews it → **stay on the free plan's fixed 7 days and warn** (Anton, November 18, 2026). AC-11 to AC-14 are in; AC-15 is dropped (no Clerk plan change). Offered and not chosen: a paid Clerk plan with a longer lifetime (Clerk documents a configurable lifetime on paid plans; the exact length was not checked), and a window reaching its own machines through its machine's Connect link.
### Defaulted (change any before sw-do)
- D-02 The reason is a structured flag on the refusal, not error text → default.
- D-03 The group heading reads "Not reachable from here" → default.
- D-04 The signed-out banner shows only when a saved machine needs the sign-in → default.
- D-05 Labels (AC-01 to AC-10) ship after review and green CI; AC-11 to AC-14 wait for Anton's acceptance → default.
- D-06 "Needs sign-in" waits for Clerk's settled signed-out state (review round 1) → default.
- D-07 Saved machines are kept only after an expiry or a renew; every other sign-out removes them as today (fail-closed) → default, held with AC-16 for Anton.
### Open
- none

## Tasks

### T-01 Flag Connect-session refusals and carry the flag to the presentation
- AC: AC-01, AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/model.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/service.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/authorization/layer.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/presentation.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/presentation.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/connection/platform.ts, repositories/anton-abyzov/specwithcode/apps/mobile/src/connection/platform.ts | Test: `node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/connection/presentation.test.ts packages/client-runtime/src/authorization/layer.test.ts packages/client-runtime/src/connection/supervisor.test.ts`

### T-02 Say the real reason on rows, chips, cards, banners and pickers
- AC: AC-02, AC-03, AC-04, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/lib/machineStatus.ts, repositories/anton-abyzov/specwithcode/apps/web/src/lib/hostDownNoteWords.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectAccountState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectAccountState.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/managedAuth.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/state/environments.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/unreachableHosts.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectThreadCards.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ThreadLinkChip.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectThreadCards.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/environmentUnavailableBanner.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/ChatView.tsx | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/lib/hostDownNoteWords.test.ts apps/web/src/cloud/connectAccountState.test.ts apps/web/src/lib/machineStatus.test.ts apps/web/src/studio/shellModel.test.ts`

### T-03 Head the unreachable group "Not reachable from here"
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/shellModel.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/ThreadsPane.test.tsx apps/web/src/lib/hostDownNoteWords.test.ts`

### T-04 Signed-out banner and account button tone
- AC: AC-07, AC-08, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/SignedOutBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/signedOutBannerModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/signedOutBannerModel.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ConnectSignedOutBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/accountMenuModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/AccountMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ConnectSidebarAccountMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/signedOutBannerModel.test.ts apps/web/src/components/account/accountMenuModel.test.ts apps/web/src/i18n`

### T-05 Headless proof of the signed-out window
- AC: AC-02, AC-05, AC-07, AC-09 | Files: none in the repository; evidence in reports/ | Test: headless fixture with a relay-only machine and no Connect session: screenshots of the signed-out panel, a signed-in cold start with no "Needs sign-in" flash, and the panel after sign-in

### T-06 Warn before a sign-in ends and renew in one click
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ConnectSidebarAccountMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/useConnectRenew.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/useStudioConnectAuthPrompt.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ConnectSignedOutBanner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/signedOutBannerModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/signedOutBannerModel.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/accountMenuModel.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/accountMenuModel.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/account/AccountMenu.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/useConnectSessionEnd.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AccountJoinCard.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachineSummary.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/connect-signed-out, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectSessionEnd.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectSessionEnd.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectSignInStarted.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectSignInStarted.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectRenewResume.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/cloud/connectSessionEnd.test.ts apps/web/src/components/account/accountMenuModel.test.ts apps/web/src/components/studio/shell/signedOutBannerModel.test.ts apps/web/src/cloud/connectSignInStarted.test.ts`

### T-08 Keep saved machines across an expiry and a renew
- AC: AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectSessionRecord.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/connectSessionRecord.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/managedAuth.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/managedAuth.accountState.test.tsx | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/cloud/connectSessionRecord.test.ts apps/web/src/cloud/managedAuth.accountState.test.tsx`

### T-07 No silent sign-out by the relay guard
- AC: AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectSessionGuard.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/ConnectSessionGuard.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/errors.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/errors.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/model.ts, repositories/anton-abyzov/specwithcode/apps/web/src/connection/platform.ts, repositories/anton-abyzov/specwithcode/apps/web/src/connection/platform.test.ts | Test: `node node_modules/vite-plus/bin/vp test run apps/web/src/cloud/ConnectSessionGuard.test.ts`
