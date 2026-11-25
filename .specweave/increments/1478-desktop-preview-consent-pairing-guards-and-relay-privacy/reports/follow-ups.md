# 1478 follow-ups, residuals and items held for other owners

Written November 24, 2026 from `spec.md` and the three lane reports: `reports/red-green-clients.md`, `reports/red-green-desktop.md`, `reports/red-green-relay.md`. App checkout `repositories/anton-abyzov/specwithcode`, branch `1474d-preview-pairing` (from `origin/main` `2b7f17e8b`). Commit shas below are from that branch.

Ownership used here: group A owns `apps/server` auth, http and config. `packages/contracts/*` and `apps/server/src/cloud/relayResponse.ts` are not wave-1 group D files. `PairingViewModel.kt`, `apps/mobile` and `packages/shared/src/relayTracing.ts` sit outside the 1478 file lists.

## Index

| ID | Item | Kind | Owner | Status |
|---|---|---|---|---|
| O-1 | Clerk webhook and signing secret | Owner decision | Owner | Not started |
| O-2 | Clerk replay key is `svix-id` plus timestamp | Owner decision | Coordinator | Awaiting accept |
| O-3 | FCM `user_hash` can be confirmed from a known user id | Owner decision | Owner | Accepted by lane, needs owner |
| O-4 | Leftover-tunnel teardown before a brand-new link not ported | Owner decision | Owner | Held |
| O-5 | `Runtime.evaluate` while the person annotates | Owner decision | Owner | Residual |
| O-6 | Wheel event already queued in the compositor | Owner decision | Owner | Residual |
| O-7 | Proof and challenge nonces spent before the key check | Owner decision | Owner | Left as is |
| O-8 | Open `mailto:` from app-window popups? | Owner decision | Owner | Not blocking |
| E-1 | R4 readiness proof (server route, contracts field) | Engineering | Group A, contracts, shared, desktop | T-09 blocked |
| E-2 | Dedicated `environment_key_mismatch` reason and unlink hint | Engineering | Contracts, `relayResponse.ts`, relay | Not started |
| E-3 | Feature-branch route for a clean default-branch Push | Engineering | `GitManager.ts` or `GitActionsControl.tsx` | Not started |
| E-4 | Android refusal wording for unreadable hosts | Engineering | `PairingViewModel.kt` | Not started |
| E-5 | `apps/mobile` receiver still reads `user_id` | Engineering | `apps/mobile` | Not started |
| E-6 | `relayTracing.ts` exports error messages and stacks | Engineering | `packages/shared` | Not started |
| E-7 | CDP input attribution | Engineering | Desktop preview | Design needed |
| E-8 | Relink race: losing racer reconfigures the winner's tunnel | Engineering | Relay | Narrowed by `a15bdc383`; residual open |
| E-9 | A to B to A DNS cleanup race | Engineering | Relay | Residual; the next link restores the record |
| E-10 | Main-window `openExternal` permission (voice handler) | Engineering | Desktop `voice.ts` | Not started |
| E-11 | R13 credential insert not in the link batch | Engineering | Relay | Not started |
| E-12 | PR #910 and #911 must merge together | Engineering | Coordinator | #911 merged as `8dea0b339`; #910 open |
| E-13 | File-size and lint leftovers | Engineering | Relay, desktop | Not started |
| E-14 | Favicon split-DNS label list is a heuristic | Engineering | `packages/shared` | Accepted limit |
| E-15 | #909 round 3: PR-diff refusal text exported through `relayTracing.ts` | Engineering | `packages/shared` | Not changed (E-6) |
| P-1 | Android red and green from CI | Proof pending | Clients lane, Android CI | Pending CI |
| P-2 | R14 tunnel binding proven only by deploy | Proof pending | Relay deploy | Pending deploy |
| P-3 | Desktop proof limits | Proof pending | Desktop lane | Open |
| P-4 | Relay client-address headers without a test | Proof limit | Relay lane | Accepted |
| C-1 | PR #910 carries neither `0db9045b9` nor `235e720cc` | Coordinator check | Coordinator | Checked clean |
| I-1 | Relay round 2: live start ownership | Relay round 2 | Relay lane | Shipped on PR #912 |
| I-2 | Relay round 2: ingress race | Relay round 2 | Relay lane | Shipped on PR #912 |
| I-3 | Relay round 2: deletion marker | Relay round 2 | Relay lane | Shipped on PR #912 |
| I-4 | Relay round 2: nonce expiry | Relay round 2 | Relay lane | Shipped on PR #912 |

## Owner decisions

### O-1 Create the Clerk webhook and its signing secret

What is left: R17 shipped the Svix-verified route `POST /v1/webhooks/clerk` (`infra/relay/src/webhooks/ClerkWebhook.ts`, commit `5be90e66b`) and the deploy line `CLERK_WEBHOOK_SIGNING_SECRET: ${{ secrets.CLERK_WEBHOOK_SIGNING_SECRET }}` in `.github/workflows/deploy-relay.yml`. Nobody has created the Clerk webhook or the secret, so the route answers 503 to every request (D-03) and Clerk-side deletions still leave relay records behind.

Why not here: creating the webhook and secret is an owner step (spec Scope "Out"), and it touches auth configuration.

Owner: owner, Clerk dashboard and the `anton-abyzov/specwithcode` repository secrets.

Suggested change: in Clerk, add an endpoint for `user.deleted` pointing at the relay's `/v1/webhooks/clerk`, copy its `whsec_...` signing secret into the repository secret `CLERK_WEBHOOK_SIGNING_SECRET`, redeploy the relay, then send a test `user.deleted` for a throwaway user and confirm a 204 and that the user's rows are gone.

### O-2 Clerk replay key is `<svix-id>.<svix-timestamp>`, not `svix-id` alone

What is left: relay fix 5 (`040b3a23b`) dedupes on `<svix-id>.<svix-timestamp>` in the `DpopProofReplay` store (scope `clerk-webhook`), a deviation from the review's "dedupe by `svix-id`". The lane asks the coordinator to accept or reverse it.

Why not here: a deliberate deviation needs the reviewer's or coordinator's sign-off.

Owner: coordinator of PR #912.

Suggested change: accept. Svix resends a failed delivery with the same `svix-id` and a new `svix-timestamp`; keyed on the id alone, Clerk's retry after a 500 would get a 204 and delete nothing. A captured request replayed unchanged still hits the stored nonce, and a fresh timestamp needs the secret. The test `acts on Clerk's retry, which signs the same message with a new timestamp` covers this.

### O-3 FCM `user_hash` can be confirmed from a known user id

What is left: R16 (`e204140a9`) replaced `user_id` with `user_hash` = SHA-256 of `<userId>:<deviceId>`. The hash has no key, by design, so the phone can recompute it. Anyone holding a user id and the device id can still confirm a match against a captured payload.

Why not here: the lane kept it unkeyed on purpose; changing it changes the phone-side check (E-5) and the threat model, which is the owner's call.

Owner: owner; files `infra/relay/src/agentActivity/FcmDeliveries.ts` and the mobile receiver.

Suggested change: keep it for now. If confirmability matters, issue a random per-device token at device registration, store it with the device row, send `HMAC-SHA256(token, userId)` and let the phone compare with its own token. Google then sees nothing it can link to a user id.

### O-4 Leftover-tunnel teardown before a brand-new link was not ported

What is left: the upstream R12 commit finishes a leftover tunnel teardown before every brand-new link. Ours does not.

Why not here: an unlink of an online machine deliberately leaves its tunnel for later (`ManagedEndpointProvider.ts` comment "The machine being removed is often still online" at the `tunnels.delete` call). Forcing teardown first would refuse that machine's relink until its old connector drops. Tunnel name and hostname derive from user and environment, so a fresh tunnel gets the same address anyway. The lane holds it for the owner.

Owner: owner; relay, `infra/relay/src/environments/EnvironmentLinker.ts` and `ManagedEndpointProvider.ts`.

Suggested change: leave it unported. If wanted later, run the teardown only when the old tunnel has no active connectors, so an online machine's relink is never refused.

### O-5 `Runtime.evaluate` while the person annotates

What is left: the annotation guard in `apps/desktop/src/preview/DesktopBrowserHost.ts` refuses only `Input.*` (and wrapped input). An agent can still scroll or change the page through `Runtime.evaluate` during annotation (desktop round-2 item D).

Why not here: AC-02 covers input only; page JavaScript is the agent's ordinary page control.

Owner: owner; desktop preview files `DesktopBrowserHost.ts`, `CdpRelay.ts`.

Suggested change: accept as is. If the owner wants a quiet page during annotation, hold `Runtime.evaluate`, `Runtime.callFunctionOn` and `DOM.*` mutations in a per-tab queue while annotating and release them when it ends, rather than refusing them, so agent scripts do not fail.

### O-6 Wheel event already queued in the compositor

What is left: a wheel event Chromium queued in its compositor before the annotation started can still land on the page (desktop R1 follow-ups, "Residual, not fixed").

Why not here: the event is queued below the CDP relay, so the dispatch check cannot see it.

Owner: owner; `apps/desktop/src/preview/PickPreload.ts`.

Suggested change: accept. The effect is one stray scroll at annotation start. If it must close, the overlay can add a non-passive `wheel` listener in the isolated world for the annotation's lifetime that calls `preventDefault()` on wheel events whose `timeStamp` predates the annotation start.

### O-7 Proof and challenge nonces are spent before the key check

What is left: in the relay link path, the proof and challenge nonces are consumed before the key-mismatch check (relay fix 2, "Left as is").

Why not here: not fail-open. A refused link only spends a nonce the machine made for that attempt.

Owner: owner; `infra/relay/src/environments/EnvironmentLinker.ts`.

Suggested change: none. Keep the order and record the acceptance.

### O-8 Open `mailto:` from app-window popups?

What is left: app-window popups open externally only for http and https (`ElectronShell.parseWebExternalUrl`, `SAFE_WEB_PROTOCOLS`). `mailto:` was never opened by `ElectronShell.openExternal` and still is not (desktop R3). The original AC-03 wording promised `mailto` too; the spec now says http and https only.

Why not here: shipping http and https only keeps the app's behaviour from before 1478. Opening `mailto:` would loosen it, so it is an owner option, not a fix. Not blocking.

Owner: owner; `apps/desktop/src/electron/ElectronShell.ts`, `apps/desktop/src/window/DesktopWindow.ts`.

Suggested change: keep http and https only unless the owner wants mail links from the app window. If so, add `mailto:` to the popup allowlist only (not to `openExternal` in general) with a `DesktopWindow.test.ts` case, and keep every editor scheme denied.

## Engineering follow-ups

### E-1 R4 readiness proof (server route and contracts field)

What is left: AC-04 is unmet and T-09 is blocked. The desktop still counts any HTTP 200 on the backend port as its backend (`apps/desktop/src/backend/DesktopBackendManager.ts:617`).

Why not here: a desktop-only half can never become ready; the backend has to answer the proof, and those files are outside group D.

Owner: group A for `apps/server/src/http.ts`, `apps/server/src/config.ts`, `apps/server/src/cli/config.ts`; the contracts owner for `packages/contracts/src/desktopBootstrap.ts`; the shared owner for `packages/shared/src/httpReadiness.ts` and a new `packages/shared/src/desktopReadinessProof.ts`; then the desktop lane for `apps/desktop/src/backend/DesktopBackendConfiguration.ts` and `DesktopBackendManager.ts`. Needs a new increment (or T-09 reopened once the server side lands).

Suggested change:

- Contracts: optional `desktopReadinessSecret` in `DesktopBackendBootstrap`, optional so older backends and desktops stay compatible.
- Server: carry it into `ServerConfig`; add a `GET` route that answers a `challenge` query with hex `HMAC-SHA256(secret, "<prefix>:" + challenge)`, and 404 when no secret was handed over or the challenge is empty or longer than 128 characters.
- Shared: an `accept(body)` hook on the readiness poller plus the proof derive and timing-safe compare.
- Desktop: a fresh secret per launch in the bootstrap, a fresh challenge per probe, readiness only on a matching proof. Check a normal local launch and a WSL launch.

### E-2 Dedicated `environment_key_mismatch` reason and unlink hint

What is left: R12 refuses a key change with the existing wire reason `descriptor_mismatch` (stage `validate_existing_link`, warning log `environment_key_mismatch`). The server shows "Relay rejected the environment link proof (descriptor_mismatch)" and the hint for every proof-invalid reason, "Check this machine's date and time", which is wrong for this case. AC-12 expects a machine whose key changed to be unlinked in Connect first; nothing tells the person that.

Why not here: D-01. `packages/contracts/src/relay.ts` and `apps/server/src/cloud/relayResponse.ts` are not group D files, and older servers would not decode a new literal.

Owner: contracts owner and `apps/server/src/cloud/relayResponse.ts` owner; then the relay (`infra/relay/src/environments/EnvironmentLinker.ts`).

Suggested change: ship in two steps. First, add `environment_key_mismatch` to the reason union in `relay.ts` and teach `relayResponse.ts` to decode it with the hint "This machine's key changed. Unlink it in Connect, then restart SpecWithCode." and to fall back to a generic message for unknown reasons. Second, once servers that decode it are released, switch the relay's refusal from `descriptor_mismatch` to the new reason.

### E-3 Feature-branch route for a clean default-branch Push

What is left: after R5, "Check out feature branch & continue" on a clean default branch that is ahead still fails. The server refuses `featureBranch` for anything but commit actions (`apps/server/src/git/GitManager.ts:2753`). It failed before 1478 too ("Cannot create a feature branch because there are no changes to commit.", covered by `GitManager.test.ts:3505`); only the error text changed (clients F3).

Why not here: the route is chosen in `apps/web/src/components/GitActionsControl.tsx:1495` and `GitManager.ts`, neither of which is in T-01's files.

Owner: `apps/server/src/git/GitManager.ts` owner (recommended), or `apps/web/src/components/GitActionsControl.tsx` owner for the smaller fix.

Suggested change (recommended): at `GitManager.ts:2753` allow `input.featureBranch` when `input.action === "push"`; name the branch from the head commit's subject (`git log -1 --format=%s`, then `sanitizeFeatureBranchName` and `resolveAutoFeatureBranchName`), `createRef` and `switchRef`, run no commit step, push the new branch. Server test: a clean default branch one commit ahead, `push` with `featureBranch: true`, yields a created branch, `commit.status` `skipped_not_requested`, a push of that branch, and a file written before the call left uncommitted. Smaller alternative: at `GitActionsControl.tsx:2226`, disable the button while `pendingDefaultBranchAction.includesCommit` is false.

### E-4 Android refusal wording for unreadable hosts

What is left: after clients G3 (`8df8474f1`, `459944608`), `PairingInput.isPublicCleartext` also refuses a link from another app when no machine address can be read. The refusal shows the existing "unencrypted over the internet" text, which is wrong for an unreadable link.

Why not here: the message lives in `PairingViewModel.kt`, outside T-05's files.

Owner: `apps/android/app/src/main/kotlin/com/specwithcode/android/ui/pairing/PairingViewModel.kt` owner (guard at `PairingViewModel.kt:103`).

Suggested change: branch on `PairingInput.host(link) == null` before the cleartext check and show its own message, for example "This link does not name a machine SpecWithCode can reach.", with a `ViewModelTest` case for `not a pairing link` from another app.

### E-5 `apps/mobile` receiver still reads `user_id`

What is left: the relay now sends `user_hash` instead of `user_id` (R16). The undistributed Expo module `apps/mobile/modules/studio-agent-notifications/android/src/main/java/expo/modules/studioagentnotifications/AgentNotifications.kt:126` still compares `user_id`, so its account check would fail once it ships. The native Android app (`apps/android`) reads no FCM data key and is unaffected.

Why not here: `apps/mobile` is outside the relay lane's files.

Owner: `apps/mobile` owner.

Suggested change: before the module ships, compute lowercase hex SHA-256 of `<userId>:<deviceId>` on the phone and compare it with `user_hash`; drop the `user_id` read. If O-3 moves to a keyed token, follow that instead.

### E-6 `relayTracing.ts` exports error messages and stacks

What is left: `packages/shared/src/relayTracing.ts` still exports error messages with stacks. Clients F2 and G1 wrap the client-runtime relay tracer (`packages/client-runtime/src/connection/relaySpanPrivacy.ts`) so machine names, host refusal text and approval codes are masked on that path, but the exporter itself still sends any message and stack it is given.

Why not here: D-05. Not a group D file; relay tracing has no endpoint configured in our builds.

Owner: `packages/shared` owner. The server has its own `apps/server/src/cloud/relayTracing.ts`, which the lanes did not review; check it in the same change.

Suggested change: export the error's tag or type and a fixed code, never `message`, `stack` or `cause` text; or route every relay exporter through the same redaction that `relaySpanPrivacy.ts` applies. Add a test that an error carrying a machine name exports no trace of it.

### E-7 CDP input attribution (per-input correlation, remote viewers, guest-drawn cursor)

What is left: CDP `Input.*` events are trusted in the page, so an agent's click or key reaches the human-input channel (takeover) and the recording overlays as the person's. This predates 1478. Round-2 C (`0db9045b9`, a 300 ms mark after each relayed input) was taken back out (`235e720cc`) and moved here.

Why not here: the timer design failed review; a correct design needs per-input correlation and tracing of the remote-viewer path, which is more than a review fix.

Owner: desktop preview, `apps/desktop/src/preview/DesktopBrowserHost.ts`, `CdpRelay.ts`, `Manager.ts`, `RecordingCursor.ts`, `PickPreload.ts`. New increment.

Suggested change, answering the five review points:

1. Correlate per input: tag each relayed `Input.*` dispatch with an id and match the guest's report to it, so attribution does not depend on IPC or debugger-reply timing.
2. No expiring marks: an input stays the agent's until its report arrives, however slow or wrapped.
3. No sticky marks: clear pending ids when the session detaches or a reply is lost, so the person's input is never dropped afterwards.
4. Remote viewers: trace how a remote viewer's input reaches the guest and attribute by source (agent dispatch versus person, wherever the person sits), not by "relay busy".
5. Guest-drawn cursor: the recording overlay's human cursor must follow the attributed source, not every trusted pointer event.

### E-8 Relink race: a losing racer can reconfigure the winner's tunnel

What is left: inside the race window only, provisioning runs before the write and reuses the account's tunnel for that environment, so a losing racer's `putConfiguration` (`infra/relay/src/environments/ManagedEndpointProvider.ts:1221`) can point the winner's tunnel at the loser's local origin port until the winner links again. Availability effect only; the connector token is not returned to the refused caller.

Why not here: closing it means checking the key inside the allocation claim before configuring; the lane report left it.

Owner: relay, `ManagedEndpointProvider.ts`, `EnvironmentLinker.ts`.

Suggested change: check the proof key against the active link inside the allocation claim and skip `putConfiguration` when it does not match.

Status: narrowed by relay round 2 (I-2): `a15bdc383` on PR #912 (lane branch `d701401ef`). A link that lost the race re-checks the active link before writing the tunnel ingress and writes nothing; a key mismatch gets the same refusal. Residual: the re-check and the Cloudflare write cannot be atomic, so a winner that commits inside the loser's one Cloudflare call can still be repointed until it links again. Source: PR #912 review round 2. Review round 3 is running.

### E-9 A to B to A DNS cleanup race

What is left: relay fix 4 (`68d10c983`) rereads the previous account's link after `prepareDeprovision` and removes its tunnel only while that link is still revoked. In the window between that reread and the delete, account A can relink and lose its fresh DNS record; A's next link restores it.

Source: PR #912 review round 2 (the lane report says nothing about the DNS record).

Why not here: closing the window needs the check and the deprovision under one claim; round 2 left it as a residual.

Owner: relay, `EnvironmentLinker.ts`, `ManagedEndpointProvider.ts`.

Suggested change: make the delete conditional on the link still being revoked at delete time (do the check and the deprovision under the same allocation claim), or recheck after the delete and reprovision the record when the previous account is active again. Add a test that interleaves A's relink between the reread and the DNS delete.

### E-10 Main-window `openExternal` permission (voice handler)

What is left: upstream R3 also refuses the `openExternal` session permission. Ours did not port it.

Why not here: the main window shares `session.defaultSession`, whose permission request handler `apps/desktop/src/ipc/methods/voice.ts:341` already owns; that file is outside T-08.

Owner: desktop, `apps/desktop/src/ipc/methods/voice.ts`.

Suggested change: in that handler, answer `false` for `permission === "openExternal"` and keep the voice (media) answers unchanged; add a unit test for both. Editor links keep working because the web app opens them through `desktopBridge.openExternal` over IPC (`apps/web/src/localApi.ts:31`), not through the permission.

### E-11 R13 credential insert is not in the link batch

What is left: the upsert and the revocation of other accounts' links run as one `RelayDb.batch`, but the credential insert does not. A failure there leaves a retryable link, as today, so AC-13's "same atomic D1 batch" holds for link plus revocation only.

Why not here: making it batchable needs a reshaped `EnvironmentCredentials.create`.

Owner: relay, `infra/relay/src/environments/EnvironmentLinks.ts` and the credentials module.

Suggested change: have `EnvironmentCredentials.create` return a prepared statement (or a build-statement function) and append it to the existing batch after the upsert; extend `EnvironmentLinks.integration.test.ts` with a failing credential insert that must leave no new link and no revocation.

### E-12 PR #910 and #911 must merge together

What is left: the consent review's first finding (a page hijacks the submit listener in the shared JavaScript world) is closed only by the isolation PR #911, so #910 alone would ship that hole.

Why not here: merge order is the coordinator's step.

Owner: coordinator.

Suggested change: merge #910 and #911 back to back, or fold them into one PR.

Status: #911 merged as `8dea0b339`. #910 review round 4 is running; merge it next.

### E-13 File-size and lint leftovers

What is left: `infra/relay/src/http/Api.ts` is 1,511 lines, over the 1,500 rule (it was 1,515). `infra/relay/src/environments/ManagedEndpointProvider.test.ts` (2,064) and `infra/relay/src/http/Api.test.ts` (1,960) are over it too. `apps/desktop/src/preview/PickPreload.ts` is at 1,488. `vp lint` in `infra/relay` keeps two pre-existing findings: an unused `HookForwarder` import in `Api.ts` and the node import style in `src/testing/sqliteD1.ts`.

Why not here: all pre-existing; the lanes only kept the files from growing.

Owner: relay and desktop.

Suggested change: drop the unused import (brings `Api.ts` under 1,500 if one more block moves out), split the two test files by feature, and move the next new `PickPreload.ts` logic into its own module.

### E-14 Favicon split-DNS label list is a heuristic

What is left: the split-DNS rule in `packages/shared/src/hostClassification.ts` (clients G4) marks a host private when a label `corp`, `home`, `internal`, `intranet`, `lan`, `localdomain` or `private` appears anywhere except its last two labels. Internal zones with other names still reach the favicon service (`wiki.ops.example.com` is public), and a public host with a listed label gets no favicon (`home.apache.org`). Raised in PR #909 review round 3.

Why not here: no list of names can know a company's internal zones; the rule is a heuristic by design. Accepted limit.

Owner: `packages/shared` owner.

Suggested change: accept. If it matters later, let the person mark a host private (or turn remote favicons off) in settings rather than growing the list.

### E-15 PR #909 round 3: a PR-diff refusal exports its text through `relayTracing.ts`

What is left: a PR-diff request refused while device approval is pending exports its refusal text through `packages/shared/src/relayTracing.ts`. Raised in PR #909 review round 3; not changed.

Why not here: this is the exporter itself, which is E-6 (D-05).

Owner: `packages/shared` owner, with E-6.

Suggested change: fold into E-6 and add the PR-diff refusal to E-6's test.

### PR #909 review round 3 (shipped)

Fixed in `apps/android/app/src/main/kotlin/com/specwithcode/android/app/PairingInput.kt`: a plain-http link from another app to a name with no dot (`http://build:3773`) is refused, since the phone's DNS search domain picks which machine it reaches. https, `localhost`, `.local` and private addresses are unchanged; typed-in hosts still pair. Test commit `153acd030`, fix `9ae03cd54` on PR branch `1478-client-guards`; CI red and green pending (P-1). Not changed: E-15 and E-14.

## Proof still pending

### P-1 Android red and green from CI

What is left: R10, F1 and G3 have no recorded run. M5 has no Java runtime, so red and green come from the Android CI job (`.github/workflows/android.yml`, `./gradlew --console=plain test`).

Owner: clients lane and the coordinator.

Suggested change: push each test commit alone, then its fix, and record both runs: `671e661e5` then `b9995b37d` (R10), `60f9c6d5d` then `cd53a9251` (F1), `8df8474f1` then `459944608` (G3), `153acd030` then `9ae03cd54` (#909 round 3, bare names over http). The same CI run that shows the fixes green must also show `ViewModelTest` green: its external-link cases (`attacker.example`, a LAN http link) were checked by inspection only (clients G3).

### P-2 R14 tunnel binding proven only by the relay deploy

What is left: the binding swap (`d47eff025`, `ManagedTunnelBinding.ts` with `disconnect`, wired in `worker.ts`) is proven only by `deploy-relay.yml` on `main` and a real account deletion of a connected machine; unit tests stub Cloudflare.

Owner: relay lane after merge.

Suggested change: after deploy, delete a throwaway account whose machine is online and confirm the tunnel is gone and the allocation freed. `d47eff025` reverts alone if the deploy fails.

### P-3 Desktop proof limits

What is left: the submit button's `isTrusted` click check has no unit test and the real-Electron check drives only keyboard submit. The out-of-process iframe path in `CdpRelay.ts` (announce, command, detach) is unit-tested only. The picker's `WeakSet` overlay check (`7f8f056ff`) has no unit test. The isolation check used a `BrowserWindow` with the guest's preferences, not a `<webview>` in the app window; passkeys, recording input and the recording cursor were not exercised.

Owner: desktop lane.

Suggested change: add a submit-by-click run and an iframe run to `reports/desktop-electron-check/check.cjs`, and one packaged-app check of a `<webview>` preview with a recording.

### P-4 Relay client-address headers without a test

What is left: relay fix 1 drops 10 client-address headers from request spans, but its red test sends only 7 (`cf-connecting-ip`, `cf-connecting-ipv6`, `cf-pseudo-ipv4`, `x-forwarded-for`, `x-real-ip`, `true-client-ip`, `forwarded`). `x-client-ip`, `x-cluster-client-ip` and `fastly-client-ip` are dropped without a test.

Owner: relay lane.

Suggested change: add the three headers to the `traceRequestPrivacy.test.ts` request when the file is next touched. Accepted as a proof limit.

### C-1 PR #910 carries neither `0db9045b9` nor `235e720cc`

Desktop round 3 dropped round-2 C (`0db9045b9`) from the PR branch, and the local undo `235e720cc` was for the lane checkout only. Checked by the coordinator against `origin/1478-preview-consent`: PR #910 contains neither commit. Closed.

## Relay round 2 (shipped)

All four shipped on PR #912, head `f9108a042`. Lane-branch shas for the same commits are in the last column. Relay review round 3 is running.

| ID | Item | What shipped | PR #912 | Lane branch |
|---|---|---|---|---|
| I-1 | Live start ownership | A queued Live Activity start is sent only if every machine in its content is still linked to that user under the same key | `29862a0f7` | `155482293` |
| I-2 | Ingress race | A link that lost the race re-checks the active link before writing the tunnel ingress and writes nothing; a key mismatch gets the same refusal. Residual in E-8 | `a15bdc383` | `d701401ef` |
| I-3 | Deletion marker | An account marked deleting or deleted is refused on every DPoP call, the token exchange and every Clerk-bearer route except `DELETE /v1/client/account` | `ba17b533d` | `fadfb1acf` |
| I-4 | Nonce expiry | The Clerk replay record expires at the timestamp plus 300 s plus 60 s | `f9108a042` | `0a5c626c4` |

Residuals from round 2: the ingress re-check and the Cloudflare write cannot be atomic (E-8), and the A to B to A cleanup race can delete A's fresh DNS record until A's next link restores it (E-9).

## F-1: one serialized writer per environment (relay)

#912's rounds 5 and 6 showed that repairing the tunnel ingress and DNS after the D1 write only moves the stale-write window. Next increment: put every Cloudflare tunnel config and DNS write for an environment behind one serialized writer (a Durable Object, or a generation-fenced D1 row), with a reconciler that converges Cloudflare to D1. Write its invariants before any code. It closes the same-account ingress race, the publish-only teardown window, and the removal of a previous account's tunnel after an account move. All three stay as residuals in #912.

## After #912 merged (November 25, 2026)

- The relay deploy for #912 (run 45558658803) succeeded, but Clerk's `user.deleted` test answered 500. #936 added the failing step and its cause to the warning (the user id is taken out). That showed D1 rejecting the deletion batch with `near ")": syntax error`. In production, `RelayDb` is alchemy's chain proxy, so the `db.select()` subquery inside `notExists` rendered as nothing. Account deletion had been failing in production for every caller, not only the webhook. #938 builds the subquery with `new QueryBuilder()`, with a test on the Worker's construction, and GPT-6.2 Sol reviewed it: ship. After deploy run 45566461114, the Clerk test answered 204 (`msg_3Maa5U5GuUD4BjOZecaXRoJTFUt`).
- The endpoint has received no real `user.deleted` deliveries, so there is nothing to replay. The four failed attempts are our own test sends, which Svix does not retry.
- Each test send adds a `relay_account_deletions` row for Clerk's example user id. The rows are harmless and stay.
- The `apps/mobile` Android receiver (undistributed) still checks `user_id`, so it drops pushes from this relay until it checks `user_hash` (E-5).
