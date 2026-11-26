# 1478 red and green: all rows (R1 to R17) and review rounds

Compiled November 24, 2026 from the three lane reports in this folder: `red-green-clients.md` (R5 to R10, PR #909), `red-green-desktop.md` (R1 to R4, PRs #910 and #911) and `red-green-relay.md` (R11 to R17, PR #912). Red and green excerpts below are copied from those files; nothing was rerun for this summary. Commit subjects were read with `git show -s --format=%s <sha>` in the app checkout.

App checkout: `repositories/anton-abyzov/specwithcode`, branch `1474d-preview-pairing` from `origin/main` `2b7f17e8b`. Every command below runs from that checkout unless it says otherwise. Red is the new test against unmodified code; green is the same command after the fix.

## Overview

| Row | Upstream | AC | PR | Verdict |
|---|---|---|---|---|
| R1 | `ba640037e8` | AC-01 | #910 | fixed |
| R2 | `fb04b4d199`, `4948c9afbe` | AC-02 | #910 | fixed |
| R3 | `5e62206e7d` | AC-03 | #911 | fixed |
| R4 | `c9e22e5ff4` | AC-04 | none | blocked |
| R5 | `a5d86e6382` | AC-05 | #909 | fixed |
| R6 | `a3708b5180` | AC-06 | #909 | fixed |
| R7 | `d6a28f4faa` | AC-07 | #909 | fixed |
| R8 | `ec844a3995` | AC-08 | #909 | fixed |
| R9 | `528c77fe83` | AC-09 | #909 | fixed |
| R10 | `97b8c9c7c2` | AC-10 | #909 | fixed in code; red and green pending Android CI |
| R11 | `4eccb0ecfc` | AC-11 | #912 | fixed |
| R12 | `aa685426e7` | AC-12 | #912 | fixed |
| R13 | `7da318e2d5` | AC-13 | #912 | fixed |
| R14 | `c9ba6b4b6e` | AC-14 | #912 | fixed (binding swap proven only by deploy) |
| R15 | `9b1ea43cc4` | AC-15 | #912 | fixed |
| R16 | `2a11e76561` | AC-16 | #912 | fixed |
| R17 | `3380585e1b` | AC-17 | #912 | fixed (red by absence) |

No row was "not reproduced" or "already fixed". The relay lane's round-2 follow-ups for PR #912 are in progress (see the last section).

## R1 `ba640037e8`: preview permission consent and trusted annotation submit

AC: AC-01. Task T-06.

Test files: `apps/desktop/src/preview/BrowserSession.test.ts`, `apps/desktop/src/preview/AnnotationKeyboard.test.ts`.

Command: `cd apps/desktop && npx vp test run src/preview/BrowserSession.test.ts src/preview/AnnotationKeyboard.test.ts`

Red, 7 failed, 13 passed:

```
× ignores synthetic key events a page script dispatches  (AssertionError: expected 'attach' to be null)
× asks once per origin before granting clipboard-read     (expected true to be false)
× asks once per origin before granting notifications      (expected true to be false)
× asks once per origin before granting geolocation        (expected true to be false)
× refuses consent permissions for frames whose origin cannot be read  (expected true to be false)
× shows one prompt for concurrent requests from the same origin       (expected +0 to equal 1)
× blocks without remembering when the prompt fails                    (expected true to be false)
```

Green: `Tests 20 passed (20)`.

Keeps working: `clipboard-sanitized-write` is still granted without a prompt; a person's own Enter and Cmd/Ctrl+Enter still submit (unit test and real-Electron check). Proof limit from the lane: the submit button's `event.isTrusted` check has no unit test (the pick preload imports Electron), and the real-Electron check exercises only keyboard submit.

Commit: `25d69116b` "1478: preview pages ask before clipboard read, notifications and location; only trusted input submits an annotation". Review fixes for this row are listed under PR #910.

Verdict: fixed.

## R2 `fb04b4d199`, `4948c9afbe`: agent input waits while the person annotates

AC: AC-02. Task T-07.

Test file: `apps/desktop/src/preview/DesktopBrowserHost.test.ts`.

Command: `cd apps/desktop && npx vp test run src/preview/DesktopBrowserHost.test.ts`

Red, 1 failed, 3 passed:

```
× refuses relayed input while the person annotates the tab
AssertionError: expected [ 'Input.dispatchMouseEvent', …(2) ] to deeply equal [ 'Input.dispatchMouseEvent' ]
```

Green: `Tests 4 passed (4)`; with `src/preview/Manager.test.ts`, `Tests 104 passed (104)`.

The second upstream sha (input queued before annotation starts) is covered by the same check: ours has no input queue between relay and debugger (`CdpRelay.ts:168` dispatches each command as it arrives), so the check sits at dispatch in `DesktopBrowserHost.ts` `send`. `DOM.enable` and input after annotation ends still reach the page (same test).

Commit: `44e3d463e` "1478: agent input waits while the person annotates a preview tab". Review fixes (wrapped input, cross-tab sessions) are listed under PR #910.

Verdict: fixed.

## R3 `5e62206e7d`: isolated preview guests and web-only popups

AC: AC-03. Task T-08.

Popups. Test file `apps/desktop/src/window/DesktopWindow.test.ts`. Command: `cd apps/desktop && npx vp test run src/window/DesktopWindow.test.ts -t popups`. Red:

```
× opens only web links from popups a frame in the app window asks for
AssertionError: expected [ 'https://example.com/docs', …(3) ] to deeply equal [ 'https://example.com/docs', …(1) ]
```

Green: `src/window/DesktopWindow.test.ts src/electron/ElectronShell.test.ts`, `Tests 62 passed (62)`.

Isolation. Test file `apps/desktop/src/preview/WebviewPreferences.test.ts`. Command: `cd apps/desktop && npx vp test run src/preview/WebviewPreferences.test.ts`. Red: `× isolates the picker preload from the page`, `expected 'false' to be 'true'`. Green: `Tests 6 passed (6)`. Whole folder after both commits: `npx vp test run src/preview src/window src/electron`, `Test Files 43 passed (43)`, `Tests 631 passed (631)`; desktop typecheck 0 errors.

Real Electron 44.10.1, headless (`reports/desktop-electron-check/check.cjs`): on the `origin/main` preload with `contextIsolation=false` (`result-old-shared.json`) the page stole the overlay's shadow root and made 1 synthetic submit; on this branch with `contextIsolation=true` (`result-new-isolated.json`) no stolen root, 0 synthetic submits, and the person's pick still reads `FixtureButton`, `#target`, 4 stack frames, comment "hello from the person", submission `attach`. The page sees `ipcRenderer`, `require`, `process` and `electron` as `undefined`.

Notes from the lane: editor links from the app still open through `desktopBridge.openExternal` (`apps/web/src/localApi.ts:31`); `mailto:` was never opened by `ElectronShell.openExternal` and still is not; the upstream `openExternal` session permission refusal was not ported because `apps/desktop/src/ipc/methods/voice.ts:341` owns `session.defaultSession`'s permission handler. Proof limits: a `BrowserWindow` with the guest's preferences, not a `<webview>`; passkeys, recording input and the recording cursor were not exercised.

Commits: `6d6817e19` "1478: popups from the app window open only web links"; `9d85eab2a` "1478: preview guests run in their own JavaScript world; the React lookup runs in the page's".

Verdict: fixed.

## R4 `c9e22e5ff4`: backend readiness bound to this launch

AC: AC-04. Task T-09.

Test file and command: none run. No red or green.

Verdict: blocked. Reason from the lane (ledger `block` on T-09, November 24, 2026): our desktop polls `GET` readiness over HTTP for every backend (`apps/desktop/src/backend/DesktopBackendManager.ts:617`), so a proof needs the backend to answer it, and that needs files outside group D. A desktop-only half can never become ready.

Server and contracts change the desktop lane wrote, quoted:

- `apps/server/src/http.ts` (group A): a `GET` route that answers a `challenge` query with `HMAC-SHA256(secret, "<prefix>:" + challenge)` in hex, and 404 when no secret was handed over or the challenge is empty or longer than 128 characters.
- `apps/server/src/config.ts` and `apps/server/src/cli/config.ts` (group A): carry an optional `desktopReadinessSecret` from the bootstrap into `ServerConfig`.
- `packages/contracts/src/desktopBootstrap.ts`: optional `desktopReadinessSecret` in `DesktopBackendBootstrap` (optional, so older backends and desktops stay compatible).
- `packages/shared/src/httpReadiness.ts` plus a new `packages/shared/src/desktopReadinessProof.ts`: an `accept(body)` hook on the poller, and the shared proof derive and timing-safe compare.

Desktop half once those land: a fresh secret per launch in the bootstrap, a fresh challenge per probe, readiness only on a matching proof, in `apps/desktop/src/backend/DesktopBackendConfiguration.ts` and `DesktopBackendManager.ts`.

Commits: none.

## R5 `a5d86e6382`: Push on a clean default branch only pushes

AC: AC-05. Task T-01.

Test file: `apps/web/src/components/GitActionsControl.logic.test.ts` ("resolveQuickAction only pushes when a clean ref is ahead", "resolveQuickAction uses push-only on default ref when no upstream exists and commits are ahead"; both existing tests had encoded the defect and now expect `push`).

Command: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/components/GitActionsControl.logic.test.ts`

Red:

```
 FAIL  |unit| src/components/GitActionsControl.logic.test.ts > when: on default ref without open PR > resolveQuickAction only pushes when a clean ref is ahead
AssertionError: expected { Object (label, disabled, ...) } to have deep property 'action' of 'push', but got 'commit_push'
      Tests  2 failed | 67 passed (69)
```

Green: `Test Files  2 passed (2)`, `Tests  81 passed (81)` (logic test plus `GitActionsControl.test.tsx`). The dirty default branch still returns `commit_push`.

Commit: `9c13e587d` "1478: Push on a clean default branch only pushes". Review finding F3 (feature-branch route) is listed under PR #909.

Verdict: fixed.

## R6 `a3708b5180`: concealed terminal text stays hidden under the block cursor

AC: AC-06. Task T-02.

Test file: `apps/web/src/terminal/ghostty/renderer.test.ts` ("keeps concealed text hidden under the block cursor and undecorated").

Command: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/terminal/ghostty/renderer.test.ts`

Red (unmodified `renderer.ts`):

```
AssertionError: expected [ [ 'p', 4, 15, 7.2 ] ] to deeply equal []
      Tests  1 failed | 8 passed (9)
```

Red with only the cursor half fixed:

```
AssertionError: expected [ [ 4, 18, 7.2, 1 ], …(3) ] to deeply equal []
```

Green: `Tests  9 passed (9)`; the whole `src/terminal/ghostty/` folder `Tests  95 passed (95)`. Visible text under the cursor still draws.

Commit: `4a3847f3c` "1478: concealed terminal text stays hidden under the block cursor".

Verdict: fixed.

## R7 `d6a28f4faa`: SSH add without a target cannot become a route to a saved machine

AC: AC-07. Task T-03.

Test file: `packages/client-runtime/src/connection/onboarding.test.ts`, "SSH onboarding and saved environments" (refuses the untargeted claim; keeps the targeted add and a new host working).

Command: `cd packages/client-runtime && node ../../node_modules/vite-plus/bin/vp test run src/connection`

Red (unmodified `onboarding.ts`):

```
AssertionError: expected [ Array(2) ] to deeply equal [ BearerConnectionTarget{ …(4) } ]
      Tests  1 failed | 15 passed (16)
```

Green: `onboarding.test.ts` plus `registry.accountSaves.test.ts` `Tests  25 passed (25)`.

Commit: `bf70379c5` "1478: SSH add without a target cannot become a route to a saved machine".

Verdict: fixed.

## R8 `ec844a3995`: relay attempt spans carry no machine label

AC: AC-08. Task T-03.

Test file: `packages/client-runtime/src/connection/supervisor.test.ts` ("keeps the machine label out of relay attempt spans").

Command: `cd packages/client-runtime && node ../../node_modules/vite-plus/bin/vp test run src/connection`

Red (unmodified `supervisor.ts`):

```
AssertionError: expected [ 'environment.id', …(5) ] to not include 'environment.label'
      Tests  1 failed | 89 passed (90)
```

Green: `Test Files  20 passed (20)`, `Tests  313 passed (313)`.

Follow-up outside this group: `packages/shared/src/relayTracing.ts` still exports error messages with stacks (D-05). Review rounds widened this row a lot (F2, G1, G2 under PR #909); after G2 the folder reads `Tests  317 passed (317)`.

Commits: `e0995a392` "1478: relay attempt spans carry no machine label"; review commits `ab8b44cab`, `ae8cb8a54`, `f6f45ade5`.

Verdict: fixed.

## R9 `528c77fe83`: internal network host names never go to the favicon service

AC: AC-09. Task T-04.

Test file: `packages/shared/src/hostClassification.test.ts` ("keeps internal-network names away from the favicon service").

Command: `cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/hostClassification.test.ts`

Red (unmodified `hostClassification.ts`):

```
AssertionError: nas.lan: expected true to be false // Object.is equality
      Tests  1 failed | 10 passed (11)
```

Green: `hostClassification` and `favicon` tests `Tests  41 passed (41)`; web `apps/web/src/browser/browserTargetResolver.test.ts` `Tests  19 passed (19)`. Only `isPublicFaviconHost` changed; `isPrivateNetworkHost` is untouched.

Commits: `195a2c2b9` "1478: internal network host names never go to the favicon service"; review commit `58154a340` (G4, split-DNS names).

Verdict: fixed.

## R10 `97b8c9c7c2`: Android pairing banner and cleartext guard read the machine the link pairs with

AC: AC-10. Task T-05.

Test file: `apps/android/app/src/test/kotlin/com/specwithcode/android/PairingInputTest.kt` (`hostedLinksShowAndCheckTheMachineTheyPairWith`; review cases `nestedWrappersAreJudgedByTheMachinePairingReaches` and `theBannerReadsHostsTheWayPairingDoes`).

Command: the PR's Android CI job (`.github/workflows/android.yml`, `./gradlew --console=plain test`). M5 has no Java runtime ("Unable to locate a Java Runtime"); the task's local check is only `grep -q "host=" .../PairingInputTest.kt` (D-06).

Red: none observed. The lane wrote the expected red: "`assertEquals("other.example", …)` fails with `my-mac.local`". Its own words: "Red and green: pending CI."

Green: none observed (pending CI).

Commit plan so CI shows both: test first, then fix. `671e661e5` "1478: test that Android pairing links show and check the machine they pair with", then `b9995b37d` "1478: Android pairing banner and cleartext guard read the machine the link pairs with". Review pairs: F1 `60f9c6d5d` then `cd53a9251`; G3 `8df8474f1` then `459944608`.

Verdict: fixed in code, not yet proven. Red and green wait on the PR #909 Android CI job run per commit pair.

## R11 `4eccb0ecfc`: relay traces drop the caller's IP address and user agent

AC: AC-11. Task T-12.

Test file: `infra/relay/src/http/traceRequestPrivacy.test.ts`.

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/http/traceRequestPrivacy.test.ts`

Red (2 failed of 2, a plain route and a `/v1/hooks/` route): `AssertionError: expected true to be false` on `server.attributes.has("client.address")`.

Green: `Tests 2 passed (2)`; `src/http` `Tests 61 passed`. The route still receives the original request (address `203.0.113.9` and the user agent reach the handler). `Api.ts` went from 1,515 to 1,511 lines.

Commits: `9ace5a205` "1478: relay request spans no longer record the caller's address or user agent"; `a61c9b45e` "1478: the span privacy test runs each path as its own case"; review commit `8054bc1a5` (client-address headers).

Verdict: fixed.

## R12 `aa685426e7`: no relink of an active environment under another key

AC: AC-12. Task T-11.

Test file: `infra/relay/src/environments/EnvironmentLinker.test.ts` ("refuses to move an active link to a different key").

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinker.test.ts`

Red: "refuses to move an active link to a different key" failed because the link succeeded, returning a managed endpoint and a fresh `environmentCredential`. (The lane file gives this as prose, not a raw log line.)

Green: `Tests 18 passed (18)` for `src/environments/EnvironmentLink`. The check runs after origin validation and before replacement, deprovisioning, provisioning and the upsert; the test asserts no upsert, provision or deprovision call. "relinks an active link proven by the same key" passes.

Wire reason (D-01): the existing `descriptor_mismatch`, stage `validate_existing_link`, warning log `environment_key_mismatch`. A dedicated reason and an "unlink it in Connect, then restart SpecWithCode" hint is a follow-up for the owners of `packages/contracts/src/relay.ts` and `apps/server/src/cloud/relayResponse.ts`. Not ported: tearing down a leftover tunnel before every brand-new link (held for the owner).

Commits: `76dee7bff` "1478: the relay refuses to move an active link to another key and removes a previous account's tunnel" (shared with R13); review commit `6aa5b3200` (key check in the write).

Verdict: fixed.

## R13 `7da318e2d5`: switching accounts revokes the previous link

AC: AC-13. Task T-11.

Test files: `infra/relay/src/environments/EnvironmentLinks.integration.test.ts` (real in-memory SQLite D1 with the relay migrations) and `infra/relay/src/environments/EnvironmentLinker.test.ts`.

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinks.integration.test.ts`

Red (1 failed of 3):

```
FAIL  EnvironmentLinks on SQLite D1 > revokes the previous account's link when the machine links under another
AssertionError: expected null not to be null
```

Linker red ("removes the previous account's tunnel after the machine moves accounts"): `expected [ 'upsert:user_123' ] to deeply equal [ 'upsert:user_123', 'deprovision:user_old' ]`.

Green: `Tests 8 passed (8)` for `src/environments/EnvironmentLinks`; linker green after it reads other accounts' managed links before the upsert and removes their tunnels best effort afterwards. Upsert and revocation run as one `RelayDb.batch`. Gap the lane reports: the credential insert is not in the batch (needs a reshaped `EnvironmentCredentials.create`); a failure there leaves a retryable link as today.

Commits: `5314eb615` "1478: a machine that links under another account ends the previous account's link"; `76dee7bff` (shared with R12); review commit `68d10c983` (A to B to A).

Verdict: fixed.

## R14 `c9ba6b4b6e`: account deletion removes a live host's tunnel

AC: AC-14. Task T-12.

Test files: `infra/relay/src/environments/ManagedEndpointProvider.disconnect.test.ts` (real provider and allocations on SQLite D1, Cloudflare stub with a live connector) and `infra/relay/src/account/AccountDeletion.test.ts`.

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments/ManagedEndpointProvider.disconnect.test.ts` and `src/account/AccountDeletion.test.ts`.

Red:

```
FAIL  removing a tunnel whose host is still connected > an account deletion drops the connectors, deletes the tunnel and frees it
AssertionError: expected false to be true
FAIL  account deletion > removes a still-connected machine's tunnel with the account
AccountDeletionIncomplete: Managed endpoints remain for account user-1: env-a.
```

Green: "both pass"; "an ordinary unlink leaves the tunnel for later" passes before and after. A third test runs through the Worker's `layerCloudflareBindings` to prove the binding carries `disconnect`. `ManagedEndpointProvider.ts` went from 1,588 to 1,442 lines (bindings moved unchanged to `ManagedEndpointCloudflareBindings.ts`).

Commits: `337cfe507` "1478: account deletion drops a connected machine's tunnel connectors and deletes the tunnel"; `d47eff025` "1478: the relay's tunnel binding can drop a tunnel's connectors" (revertable alone).

Proof limit: the binding swap is proven only by the relay deploy (`deploy-relay.yml` on `main`) and a real account deletion of a connected machine; unit tests stub Cloudflare.

Verdict: fixed (deploy proof outstanding).

## R15 `9b1ea43cc4`: queued APNs jobs skip delivery when the recheck fails

AC: AC-15. Task T-10.

Test file: `infra/relay/src/agentActivity/ApnsDeliveries.recheck.test.ts`.

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/agentActivity/ApnsDeliveries.recheck.test.ts`

Red (2 failed of 2):

```
FAIL  ApnsDeliveries when the delivery-time recheck fails > skips a queued alert instead of delivering it
-   "apnsReason": "Stale APNs delivery job skipped.",
+   "apnsReason": null,
FAIL  ... > skips a queued Live Activity update instead of delivering it
+   "apnsReason": null,
```

Green: `Test Files 3 passed (3) / Tests 53 passed (53)` for `src/agentActivity/ApnsDeliveries`.

The first pass left the live-work start recheck failing open; review fix 3 (`d517eb58e`) made it fail closed, and D-04 now says all three rechecks fail closed. The R15 section of the relay file still carries the older sentence "The separate live-work start recheck still fails open (D-04)"; fix 3 supersedes it.

Commits: `3bfd2b66c` "1478: queued phone alerts are skipped when the activity recheck fails"; review commit `d517eb58e`.

Verdict: fixed.

## R16 `2a11e76561`: Android pushes send a per-device hash, not the account id

AC: AC-16. Task T-10.

Test file: `infra/relay/src/agentActivity/FcmDeliveries.test.ts`.

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/agentActivity/FcmDeliveries.test.ts`

Red:

```
FAIL  Android delivery routing > keeps completion alerts working with ongoing activity disabled
AssertionError: expected { Object (studio_kind, device_id, ...) } to not have property "user_id"
+ Received:
"user"
```

Green: `Test Files 2 passed (2) / Tests 53 passed (53)` for `src/agentActivity/Fcm`. The payload carries `user_hash` = SHA-256 of `<userId>:<deviceId>` (lowercase hex). The undistributed Expo module `apps/mobile/modules/studio-agent-notifications/.../AgentNotifications.kt:126` still compares `user_id` and needs the matching receiver change before it ships (outside this group). The hash is unkeyed by design, so a known user id can be confirmed against it.

Commit: `e204140a9` "1478: Android pushes carry a per-device hash instead of the account id".

Verdict: fixed.

## R17 `3380585e1b`: delete a user's relay data when Clerk deletes the user

AC: AC-17. Task T-12.

Test files: `infra/relay/src/webhooks/` tests and `infra/relay/src/Config.test.ts`.

Command: `cd infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/webhooks src/Config.test.ts`

Red by absence: on `origin/main` the only deletion path is the in-app call (`infra/relay/src/http/Api.ts:826` `deleteAccount`), and `POST /v1/webhooks/clerk` falls through to `layerNotFoundRoute` (`Api.ts:184`, 404). The new test file imports the new module, so it cannot run against `main`.

Green: `Tests 36 passed (36)`: signed `user.deleted` deletes (204); a valid signature among several works; unset or blank secret answers 503 and deletes nothing; wrong key, missing signature, altered body and changed `svix-id` answer 401; a timestamp 6 minutes off answers 401; another event type answers 204; a deletion failure answers 500.

Commit: `5be90e66b` "1478: the relay deletes a user's records when Clerk reports the user deleted"; review commits `040b3a23b` (replay) and `eeff50166` (deadline).

Owner step (out of scope): create the Clerk webhook and the `CLERK_WEBHOOK_SIGNING_SECRET` secret (`.github/workflows/deploy-relay.yml` reads it).

Verdict: fixed.

## PR #909 client guards: review rounds

### Round 1 (review at `aab3de9ed`, hold)

- F1, nested Android pairing links judged by the outer wrapper (fail-open, AC-10). Fix: `target(link)` is `PairingLink.parse(unwrap(link))`, what Connect does. Test `PairingInputTest.nestedWrappersAreJudgedByTheMachinePairingReaches`. Expected red on `b9995b37d`: `assertEquals("203.0.113.5", …)` fails. Red and green pending Android CI. Commits `60f9c6d5d` "1478: test that nested Android pairing links are judged by the machine pairing reaches", `cd53a9251` "1478: nested Android pairing links are judged by the machine pairing reaches".
- F2, machine names reach relay spans through connection error messages and stacks (fail-open, AC-08). Fix: new `packages/client-runtime/src/connection/relaySpanPrivacy.ts` wraps the relay tracer per connection and replaces labels with `<machine>`; errors gain optional `machineLabel`. Red: `AssertionError: expected '{"name":"TestConnectionDriver.prepare…' not to contain 'Studio Mac Fixture'` and `… not to contain 'Test environment'`, `Tests  2 failed | 1 passed | 89 skipped (92)`. Green: `Test Files  20 passed (20)`, `Tests  315 passed (315)`; `tsc --noEmit` clean. Commit `ab8b44cab` "1478: relay spans never record machine names from connection errors".
- F3, the feature-branch route for a clean default-branch Push. Disposition: not fixable in this lane's files and not a regression (it failed before with "Cannot create a feature branch because there are no changes to commit."). Recommended change for the owner of `GitManager.ts`: allow `featureBranch` for `push` at `GitManager.ts:2753`, name the branch from the head commit subject, create and switch, push with no commit step, plus a server test. Smaller alternative for `GitActionsControl.tsx:2226`: disable "Check out feature branch & continue" while `pendingDefaultBranchAction.includesCommit` is false. No commit.

### Round 2 (review at `175445f1c`, hold)

- G1, a host's own refusal text and approval code reach relay spans (fail-open, AC-08). Fix: auth errors carry `hostText`; `relaySpanPrivacy.ts` also reads `deviceApprovalCode`, `teamRulesMessage` and `approvalCode`. Red: `expected '{"name":"RemoteEnvironmentAuthorizati…' not to contain 'Studio Attic Fixture'`, 1 failed. Green: `Tests  316 passed (316)`, `tsc` clean. Commit `ae8cb8a54` "1478: relay spans leave out a host's own refusal text and approval code".
- G2, a short saved label replaced inside a longer server name (fail-open, AC-08). Fix: dedupe, replace longest first. Red: `expected '{"name":"TestConnectionDriver.prepare…' not to contain 'Upstairs'`, 1 failed. Green: `Tests  317 passed (317)`. Commit `f6f45ade5` "1478: relay spans replace the longest machine name first".
- G3, Android banner host read with `java.net.URI`, which reads no host for `_svc.example.com` (fail-open, AC-10). Fix: read with OkHttp `HttpUrl`; `isPublicCleartext` refuses when no address can be read. Expected red on `cd53a9251`: `assertEquals("_svc.example.com", …)` gets null. Red and green pending Android CI. Commits `8df8474f1` "1478: test that the Android pairing banner reads hosts the way pairing does", `459944608` "1478: Android pairing banner reads the host with the parser pairing uses; no address means no Connect from another app". A more exact refusal message needs `PairingViewModel.kt` (not this lane's file).
- G4, split-DNS names under a public domain reach the favicon service (fail-open, AC-09). Fix: any private label except in the last two labels marks the host private; `lan.example.co.uk` moved to the private list. Red: `build.corp.example.com: expected true to be false`, 1 failed. Green: `Tests  42 passed (42)`; web `browserTargetResolver.test.ts` `Tests  19 passed (19)`. Commit `58154a340` "1478: split-DNS names under a public domain never go to the favicon service".

## PR #910 preview consent: review rounds

### Round 1 (reviews of #910 and #911, reported together)

- A page hijacks the submit listener in the shared JavaScript world. Disposition: closed by the isolation PR #911, so #910 and #911 merge together.
- 1, the picker followed synthetic pointer events. Fix: pick handlers ignore `!event.isTrusted`. Real Electron run 3: red `["#decoy"]` (`desktop-electron-check/result-decoy-red.json`), green `["#target"]` (`result-decoy-green.json`); run 4 drives the pick through CDP `Input.*` and still selects `#target`. Commit `62b12c2fb` "1478: the picker follows only the person's own pointer".
- 2, recordings showed synthetic input. Fix: recording cursor ignores untrusted events. Command `cd apps/desktop && npx vp test run src/preview/RecordingCursor.test.ts`. Red: `× records only the person's own keys and clicks`, `AssertionError: expected [ { type: 'pointer', …(5) }, …(5) ] to deeply equal []`. Green: `Tests 1 passed (1)`. Commit `3f2ed7b1c` "1478: recordings show only the person's own keys and clicks".
- 3, the permission check handler did not read the frame's own URL. Fix: pass `details.requestingUrl` and refuse without a readable origin. Command `cd apps/desktop && npx vp test run src/preview/BrowserSession.test.ts`. Red: `× refuses the check for a child frame without a readable origin of its own`, `AssertionError: about:blank: expected true to be false`. Green: `Tests 17 passed (17)`. Commit `5fb87c56d` "1478: a frame without a readable origin of its own reads no preview permission grant".
- 4, input wrapped in `Target.sendMessageToTarget` bypassed the annotation guard. Fix: refuse wrapped input, unreadable inner messages and wrapping deeper than four levels. Command `cd apps/desktop && npx vp test run src/preview/DesktopBrowserHost.test.ts`. Red: `× refuses input wrapped in another command while the person annotates`, `TypeError: .toMatch() expects to receive a string, but got undefined`. Green: `Tests 5 passed (5)`. Commit `f1a57af7d` "1478: input wrapped in another debugger command also waits while the person annotates".
- Residual, not fixed: a wheel event Chromium already queued in its compositor before annotation starts can still land on the page.

After all four: `Tests 634 passed (634)` for `src/preview src/window src/electron`; typecheck 0 errors.

### Round 2 (review at `0bf5a9fcf`)

- A, the prompt cut origins at 79 characters, so two long origins read the same (fail-open). Fix: show scheme, full host and port. Red: `× names the whole origin in the prompt, so two long origins never look alike`, `AssertionError: expected 'https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaa…' to not equal 'https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaa…'`. Green: `Tests 18 passed (18)`. Commit `10dbfdbbf` "1478: the preview permission prompt names the whole origin".
- B, a synthetic Escape cancelled the annotation. Fix: overlay key handler ignores `!event.isTrusted`. Real Electron run 5: red `escapeCancelled: true` (`result-escape-red.json`); green not cancelled and the person's Enter submits `["#target"]` (`result-escape-green.json`); run 6 shows the person's own Escape still cancels (`realEscapeCancelled: true`). Commit `a0b7b7039` "1478: only the person's own Escape cancels an annotation".
- C, agent input counted as the person's in recordings and takeover. Disposition: tried in `0db9045b9` "1478: the agent's relayed input is not counted as the person's in recordings or takeover", then taken out in round 3 (dropped from the PR branch; local undo `235e720cc` "1478: take the agent-input attribution change back out; it moves to a follow-up"). Moved to a follow-up with five design points (per-input correlation instead of a 300 ms timer, early expiry, stuck marks, remote viewers' real input, the recording cursor following raw events). The gap predates #910.
- D, an agent can still scroll or change the page through `Runtime.evaluate` while the person annotates. Disposition: no change; AC-02 covers `Input.*`, and page JavaScript is the agent's ordinary page control.

After A and B (and the since-removed C): `Tests 636 passed (636)`; typecheck 0 errors.

### Round 3 (review at `4449d7669`, with #911)

Base `a8925aa73` (#910 head with `0db9045b9` removed); both commits apply alone and together.

- E, a CDP session from tab A could reach tab B, which the annotation guard never checked (fail-open). Fix: the relay tracks child sessions and refuses other `Target.*` methods ("Not supported for a desktop preview tab: <method>") and unknown sessions ("Only this preview tab's page and its frames can be reached."). Command `cd apps/desktop && npx vp test run src/preview/CdpRelay.test.ts src/preview/DesktopBrowserHost.test.ts`. Red: `Tests 2 failed | 9 passed`, `× CDP relay target scope` and the wrapped-input test. Green: `Tests 636 passed (636)` for `src/preview src/window src/electron`. Real Electron: old relay `otherTabClicks: 1` (`result-crosstab-old.json`), new relay `"error": "Not supported for a desktop preview tab: Target.attachToTarget"` and `otherTabClicks: 0` (`result-crosstab-new.json`). Proof limit: no out-of-process iframe; the child-frame path is unit-tested only. Commit `afc0a5000` "1478: a preview tab's debugger sessions reach only its own page and frames".
- F, a page could copy the `data-studio-annotation-ui` marker so its button passed clicks through and could not be picked (fail-open). Fix: the isolated world keeps its overlay hosts in a `WeakSet`. Real Electron run 6: red `markedClicks: 1`, `markedPick: null` (`result-marked-red.json`); green `markedClicks: 0`, `markedPick: ["#marked"]` (`result-marked-green.json`). No unit test for this path. Commit `7f8f056ff` "1478: the picker knows its overlay by reference, not by a marker a page can copy".
- C follow-up: confirmed out of #910 (see round 2).

## PR #911 isolation: review rounds

The desktop lane file records #911's review only together with #910: round 1 is headed "Review follow-ups of R1 (PR #910 and #911 reviews)" and round 3 is "PR #910 review at `4449d7669`, with #911". It does not say which of those findings came from the #911 review. What it does tie to #911:

- The #910 round-1 finding that a page hijacks the submit listener in the shared JavaScript world is closed by #911's isolation commit `9d85eab2a`; #910 and #911 merge together.
- Round-3 F (`7f8f056ff`) relies on the isolated world #911 creates (the `WeakSet` lives there), and the real-Electron run 7 check that "the page sees no `ipcRenderer` or `require`" still passes.
- The round-1 and round-3 commits were checked to apply without the isolation commit (`git apply --check` on a temporary index), so #910 does not depend on #911 to build.

A finding list attributed only to #911: not in the lane file.

## PR #912 relay: review rounds

### Round 1 (review at `ddaa61ab6`)

- 1, client-address headers left request spans. Fix: the traced copy drops `forwarded`, `x-forwarded-for`, `x-real-ip`, `x-client-ip`, `x-cluster-client-ip`, `true-client-ip`, `fastly-client-ip`, `cf-connecting-ip`, `cf-connecting-ipv6` and `cf-pseudo-ipv4`. Command `npx vp test run --config ../../vite.config.ts --dir . src/http`. Red: `AssertionError: expected '[["http.request.method","POST"],["url…' not to contain '203.0.113.9'` for `/v1/mobile/devices` and `/v1/hooks/hook-token-secret`. Green: `Tests 61 passed (61)`. Commit `8054bc1a5` "1478: relay request spans drop the client-address headers Cloudflare and proxies add".
- 2, relink race: two writers could pass the read check. Fix: the upsert's `ON CONFLICT DO UPDATE` carries `setWhere` and `RETURNING`; the revoke runs only when the account's row holds the proof key. Command `npx vp test run --config ../../vite.config.ts --dir . src/environments`. Red: `refuses to move an active link to another key in the write itself` failed with `AssertionError: expected false to be true`; linker red: the store refusal surfaced as `EnvironmentLinkKeyConflict`. Green: `Tests 191 passed (191)`. Commit `6aa5b3200` "1478: the link write refuses to move an active link to another key". Left as is: nonces consumed before the key check (not fail-open). Residual inside the race window: a losing racer's `putConfiguration` (`src/environments/ManagedEndpointProvider.ts:1221`) can point the winner's tunnel at the loser's origin port until the winner links again (availability, not takeover).
- 3, the APNs live-start recheck failed open. Fix: `userStillHasLiveWork` logs `live-work recheck failed; skipping queued start` and skips. Command `npx vp test run --config ../../vite.config.ts --dir . src/agentActivity`. Red: `AssertionError: expected { deviceId: 'phone-1', …(5) } to match object { kind: 'live_activity_start', …(1) }`. Green: `Tests 195 passed (195)`. Commit `d517eb58e` "1478: a queued Live Activity start is skipped when its live-work recheck fails". D-04 updated.
- 4, A to B to A removed the previous account's tunnel although its link was active again. Fix: deprovision only when that link is still revoked. Command `npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLinker.test.ts`. Red: `expected [ 'upsert:user_123', …(1) ] to deeply equal [ 'upsert:user_123' ]`. Green: `Tests 192 passed (192)`. Commit `68d10c983` "1478: a machine move keeps the previous account's tunnel if that account relinked".
- 5, Clerk webhook replay acted twice. Fix: nonce in `DpopProofReplay` (scope `clerk-webhook`, expiry timestamp + 5 minutes). Command `npx vp test run --config ../../vite.config.ts --dir . src/webhooks`. Red: `expected [ 'user_2gone', 'user_2gone' ] to deeply equal [ 'user_2gone' ]`. Green: `Tests 8 passed (8)`. Commit `040b3a23b` "1478: a replayed Clerk webhook delivery answers 204 and does nothing". Deviation for the coordinator to accept or reverse: the nonce is `<svix-id>.<svix-timestamp>`, not `svix-id` alone, so Clerk's retry with a new timestamp still deletes.
- 6, the Clerk webhook had the 9 s deadline. Fix: `/v1/webhooks/clerk` joins the 25 s provisioning paths. Command `npx vp test run --config ../../vite.config.ts --dir . src/http/Api.test.ts`. Red: "504 at 9 s". Green: `Tests 49 passed (49)`. Commit `eeff50166` "1478: the Clerk webhook gets the 25-second deadline account deletion needs".
- Not changed: FCM `user_hash` stays unkeyed by design; `ManagedEndpointProvider.test.ts` (2,064 lines) untouched.

Whole relay package after round 1: `Test Files 53 passed (53) / Tests 668 passed (668)`; `tsc --noEmit` no errors; `vp lint .` only pre-existing findings.

### Round 2: in progress

The relay lane file (last written November 24, 2026 at 23:00) has no round-2 section yet. Expected topics, all in progress with no red, green or commit recorded:

- live-work start ownership
- ingress race
- deletion marker
- nonce expiry
