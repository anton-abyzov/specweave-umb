# 1478 Desktop preview consent, pairing guards and relay privacy

## Problem

The November 14 to 25, 2026 review of the last open T3 Code copy (increment 1474, wave 1 group D) found 17 security and privacy defects in our desktop preview, client pairing code and Connect relay. Lane notes: `.specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/lanes/` (`s1-security.md`, `s2-security.md`, `c1-platform.md`, `c2-platform.md`, `d1-web.md`, `d2-web.md`, `e-mobile.md`).

- Desktop preview: any preview page gets clipboard read, notifications and location without asking (`apps/desktop/src/preview/BrowserSession.ts:31`); a page script can submit the annotation box with a synthetic Enter or click (`AnnotationKeyboard.ts:15`, `PickPreload.ts:1422`); agent input relayed through CDP reaches the page while the person annotates (`DesktopBrowserHost.ts:106`); preview guests share one JavaScript world with an IPC preload (`WebviewPreferences.ts:42`) and app popups can open editor schemes (`DesktopWindow.ts:963`); any HTTP 200 on the backend port counts as our backend (`DesktopBackendManager.ts:617`).
- Clients: Push on a clean default branch runs commit and push, so files changed while the confirm dialog is open get committed (`GitActionsControl.logic.ts:316`); the terminal block cursor draws concealed text (`renderer.ts:265`); SSH onboarding can add a route to a saved environment it does not own (`onboarding.ts:326`); relay spans carry machine labels (`supervisor.ts:230`); internal hostnames reach the public favicon service (`hostClassification.ts:130`); Android link mode shows and cleartext-checks one host while pairing with the `?host=` target (`PairingInput.kt:77-80`).
- Relay: traces record callers' IP address and user agent (`Api.ts:273`); an account bearer can relink an active environment under another key (`EnvironmentLinks.ts:265`); switching accounts leaves the previous account's link active (`EnvironmentLinks.ts:242`); account deletion cannot remove a live host's tunnel (`ManagedEndpointProvider.ts:766`); queued APNs jobs deliver when the activity recheck fails (`ApnsDeliveries.ts:603`); Android pushes send the account user id to Google (`FcmDeliveries.ts:301`); relay data outlives a Clerk-side account deletion (`Api.ts:830`).

## Scope

In: the 17 rows below (18 upstream commits), each rewritten in our own code with a test that fails before and passes after (`reports/red-green.md`). Files: `apps/desktop/*`, `apps/web/src/components/GitActionsControl.logic.ts`, `apps/web/src/terminal/ghostty/renderer.ts`, `packages/client-runtime/src/connection/*`, `packages/shared/src/hostClassification.ts`, `apps/android/app/src/main/kotlin/com/specwithcode/android/app/PairingInput.kt`, `infra/relay/*`, plus their tests.

Out: `apps/web/src/cloud/managedAuth.tsx` (1434 owns it); `packages/contracts/src/relay.ts` and `apps/server/src/cloud/relayResponse.ts` (not ours in wave 1; a dedicated key-mismatch reason and hint is a follow-up); `packages/shared/src/relayTracing.ts` error-message export (follow-up); creating the Clerk webhook and its secret (owner step).

| Row | Upstream | Our code |
|---|---|---|
| R1 | `ba640037e8` | `apps/desktop/src/preview/BrowserSession.ts:31`, `AnnotationKeyboard.ts:15`, `PickPreload.ts:1422` |
| R2 | `fb04b4d199`, `4948c9afbe` | `apps/desktop/src/preview/DesktopBrowserHost.ts:106` |
| R3 | `5e62206e7d` | `apps/desktop/src/preview/WebviewPreferences.ts:42`, `apps/desktop/src/window/DesktopWindow.ts:963` |
| R4 | `c9e22e5ff4` | `apps/desktop/src/backend/DesktopBackendManager.ts:617` |
| R5 | `a5d86e6382` | `apps/web/src/components/GitActionsControl.logic.ts:316` |
| R6 | `a3708b5180` | `apps/web/src/terminal/ghostty/renderer.ts:265` |
| R7 | `d6a28f4faa` | `packages/client-runtime/src/connection/onboarding.ts:326` |
| R8 | `ec844a3995` | `packages/client-runtime/src/connection/supervisor.ts:230` |
| R9 | `528c77fe83` | `packages/shared/src/hostClassification.ts:130` |
| R10 | `97b8c9c7c2` | `apps/android/app/src/main/kotlin/com/specwithcode/android/app/PairingInput.kt:77-80` |
| R11 | `4eccb0ecfc` | `infra/relay/src/http/Api.ts:273` |
| R12 | `aa685426e7` | `infra/relay/src/environments/EnvironmentLinker.ts:371` |
| R13 | `7da318e2d5` | `infra/relay/src/environments/EnvironmentLinks.ts:242` |
| R14 | `c9ba6b4b6e` | `infra/relay/src/environments/ManagedEndpointProvider.ts:766` |
| R15 | `9b1ea43cc4` | `infra/relay/src/agentActivity/ApnsDeliveries.ts:603` |
| R16 | `2a11e76561` | `infra/relay/src/agentActivity/FcmDeliveries.ts:301` |
| R17 | `3380585e1b` | `infra/relay/src/http/Api.ts:830` |

Line numbers in the table and in Problem are from `origin/main` before the change. On PR #912 head `f9108a042`, R17's `deleteAccount` route is at `infra/relay/src/http/Api.ts:826`.

## Acceptance Criteria

- [ ] AC-01: A preview page asking for clipboard read, notifications or location gets it only after the person allows it for that origin (remembered for the session); a frame whose origin is not `http` or `https` (`file:`, `data:`, `about:blank`, `about:srcdoc`) is refused without a prompt. Annotation submit (Enter and the submit button) accepts only trusted events. The prompt names the full origin (scheme, host, port). A failed prompt blocks and is not remembered. A permission check reads the requesting frame's own URL. Picking, the overlay's Escape and tool keys, and recordings react only to trusted events. Must keep working: a person's own Enter, Ctrl/Cmd+Enter and click submit an annotation (the click half is proven only once a test exists, P-3); other preview permissions keep their current answer.
- [ ] AC-02: While the person annotates a preview tab, relayed `Input.*` commands, direct or wrapped in `Target.sendMessageToTarget` (unreadable or deeper than four levels counts as input), are refused at dispatch. A tab's debugger sessions reach only that tab's page and frames. Non-input commands and input after annotation ends keep working. `Runtime.evaluate` is not held (O-5). On a tab's page and frame sessions, `Target.*` commands other than `setAutoAttach`, `detachFromTarget` of its own child and `getTargetInfo` of its own targets are refused, annotating or not.
- [ ] AC-03: Preview guests run with `contextIsolation=true`; page script cannot reach `ipcRenderer`, `require` or the preload's own objects. App-window popups open externally only for http and https links. Editor schemes were allowed before #910 and are now denied, and `mailto:` stays denied as before (opening `mailto:` is owner decision O-8). The popup rule ships in #910, the isolation in #911. Must keep working: element picking, annotations, the human-input and recording channels of the pick preload, and http(s) links opened from the app window.
- [ ] AC-04: The desktop app counts its backend ready only when the listener proves it holds this launch's readiness secret; a listener answering 200 without the proof keeps readiness waiting. A normal local launch and a WSL launch still become ready.
- [ ] AC-05: Push on a clean default branch that is ahead runs `push`, never `commit_push`, with and without an upstream; a dirty default branch keeps its commit actions.
- [ ] AC-06: Concealed (SGR 8) terminal text is not drawn under the block cursor or decorated; visible text under the cursor still draws.
- [ ] AC-07: Untargeted SSH onboarding that reports an environment already saved under another address fails with the known-address guard and leaves the registry unchanged; targeted SSH reconnects and new SSH hosts still register.
- [ ] AC-08: Spans exported to the relay carry no machine name or host-supplied refusal text or approval code, in attributes, events, error messages, stacks or causes. What the person sees (`detail`, `message`, `deviceApprovalCode`), local spans and logs are unchanged.
- [ ] AC-09: Hosts under `.lan`, `.localdomain`, `.corp`, `.home`, `.intranet`, `.private` (and the other RFC 6762 Appendix G names) are never sent to the favicon service, and a host whose labels include one of those names anywhere except its last two labels (`build.corp.example.com`) is private too; public hosts still are. Registrable domains spelled the same under a one-part suffix (`corp.com`, `home.page`) and look-alikes (`corporate.example.com`, `lanes.example.co.uk`) stay public. A registrable domain under a two-part public suffix, such as `corp.co.uk`, counts as private: a known false positive that only hides its favicon. The label list is a heuristic: internal zones with other names (`wiki.ops.example.com`) are not caught.
- [ ] AC-10: On Android, the banner host and cleartext guard read the machine pairing actually contacts (`PairingLink.parse` after the same unwrap Connect does, so `?host=` and nested wrappers count), with hosts read by the same parser. `ws://` counts as cleartext. A link from another app with no readable address is refused, and so is a plain-http link from another app to a name with no dot (`http://build:3773`), since the phone's DNS search domain picks its machine; https, `localhost`, `.local` and private addresses keep their answers. Plain https links and manual entries (typed-in hosts still pair) keep today's answers.
- [ ] AC-11: Relay request spans record neither the caller's IP address, user agent, nor any client-address header (`forwarded`, `x-forwarded-*`, `x-real-ip`, `cf-connecting-ip` and the like), on API and hook paths. Route handlers still receive the original request.
- [ ] AC-12: The relay refuses to relink an active environment under a different key with `EnvironmentLinkProofInvalid` (`descriptor_mismatch`, stage `validate_existing_link`). It checks before replacement, provisioning or write, and again in the link write itself, so a racing relink is refused too; a link that lost the race re-checks the active link before writing the tunnel ingress and writes nothing. A refused link leaves the stored key, other accounts' links and tunnels unchanged. Relinking with the same key, relinking after an unlink and the same-machine replacement path still work. A machine whose key changed while its environment id survived (secret store reset) must be unlinked in Connect first; the server does not yet say so (E-2).
- [ ] AC-13: When an environment and key link under a new account, the link upsert and the revocation of other accounts' active links for that environment and key run in one D1 batch, and the revocation applies only if the new row holds the proof key and is active. The credential insert follows the batch (E-11). Credentials belong to the key and stay. The previous account's tunnel is removed best effort, unless that account has relinked meanwhile.
- [ ] AC-14: Account deletion removes a live host's tunnel by dropping its connectors and then deleting it, and frees the allocation; an ordinary unlink of a live host keeps today's behaviour (tunnel left for later).
- [ ] AC-15: A queued APNs job whose activity recheck fails is skipped, not delivered. A queued Live Activity start is sent only if every machine in its content is still linked to that user under the same key.
- [ ] AC-16: Android push data sent to Google carries no account user id; it carries `user_hash`, the lowercase hex SHA-256 of `<userId>:<deviceId>`. The phone does not check `user_hash` yet: `apps/android` reads no FCM data key, and the `apps/mobile` receiver still reads `user_id` (follow-up E-5).
- [ ] AC-17: A Clerk `user.deleted` webhook with a valid Svix signature inside a 5-minute window deletes that user's relay records; a bad signature, an old timestamp or a missing signing secret is refused and deletes nothing. A missing Svix header answers 401. An unreadable body, a body that is not a Clerk event, or a `user.deleted` without a user id answers 400 and deletes nothing. A failed replay check answers 500. A delivery already handled (same `svix-id` and `svix-timestamp`) answers 204 and deletes nothing again; its replay record expires at the timestamp plus 300 s plus 60 s. A failed deletion answers 500 so Clerk retries. Other event types answer 204. An account marked deleting or deleted is refused on every DPoP call, the token exchange and every Clerk-bearer route except `DELETE /v1/client/account`, so the deletion can still be retried.

## Approach

Three lanes with disjoint files, all from current `origin/main` of `anton-abyzov/specwithcode`. The clients and relay lanes shipped one PR each (#909, #912). The desktop lane shipped as #910 (consent, popups) and #911 (isolation), and T-08's popup change is on #910.

1. Clients (PR "clients"): R5 change both clean-branch quick actions to `push`; R6 skip invisible cells in the decoration loop and in cursor text; R7 pass `knownAddressOnly` for untargeted SSH registration; R8 drop the `environment.label` span annotation; R9 extend the private suffix list; R10 read the target through `PairingLink.parse(unwrap(link))` (its `httpBase`, the same unwrap Connect does) in `PairingInput.host` and `isCleartext`, refusing a bare no-dot name over plain http from another app.
2. Desktop preview (PR "preview"): R1 a per-origin, per-session consent prompt in `BrowserSession.ts` for the three permissions, `isTrusted` checks in the annotation keyboard and submit click; R2 an `annotating()` check on the debuggee at dispatch (ours has no input queue); R3 `contextIsolation=true` with the pick and annotation calls exposed through a narrow bridge, and a popup allowlist of http and https; R4 a per-launch readiness secret handed to the child, a challenge route answering with its HMAC, and readiness bound to that proof.
3. Relay (PR "relay"): R11 the tracer gets a request copy without remote address and user agent; R12 read the active link before provisioning and refuse a key change; R13 revoke other accounts' active links for the same environment and key and write the link upsert and that revocation in one D1 batch; R14 a tunnel `disconnect` (rotate secret, drop connections) used only by account deletion when the tunnel is in use; R15 fail closed in both recheck catch arms; R16 replace the user id with a per-device hash; R17 a Svix-verified Clerk webhook route behind a missing-secret refusal.

Files already over 1,500 lines (`ManagedEndpointProvider.ts`, `Manager.ts`, `DesktopWindow.ts`, `Api.ts`) do not grow: new logic goes in new files.

Risks: R3 can break picking (the pick preload relies on page-world access, for example the React DevTools hook); R4 must stay wire-compatible with the server child the desktop launches; R14 replaces the Worker's tunnel binding and is only proven by the relay deploy.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 R12 keeps `packages/contracts/src/relay.ts` unchanged (not in this group's files, and older servers would not decode a new literal): the relay refuses with the existing wire reason `descriptor_mismatch` at stage `validate_existing_link`, and logs `environment_key_mismatch`. A dedicated reason and recovery hint is a follow-up for the owners of the contract and `apps/server/src/cloud/relayResponse.ts`.
- D-02 R1 asks for clipboard read, notifications and location once per origin per preview session, with Block as the default button; other permissions keep today's answer.
- D-03 R17 answers 503 to every webhook request while the signing secret is unset; 401 to a missing Svix header, a bad signature or a timestamp more than 5 minutes off; 400 to an unreadable body, a non-event body or a `user.deleted` without a user id; replays 204; a failed replay check or deletion 500; the route runs under the 25-second deadline. The owner creates the Clerk webhook and secret.
- D-04 All three APNs delivery-time rechecks fail closed: the state identity check, the aggregate rows check and the live-work start check skip the job when their read fails (the start recheck since the PR #912 review).
- D-05 R8 drops the label attribute from the relay-traced connection-attempt span in `supervisor.ts` (local spans keep it) and wraps the relay tracer per connection (`relaySpanPrivacy.ts`) to mask machine names and host text. The `relayTracing.ts` exporter itself is a follow-up (E-6; not in this group's files; relay tracing has no endpoint configured in our builds).
- D-06 R10 is checked by a JVM unit test; this machine has no Java runtime, so the Gradle run is the PR's Android CI job.

### Open
- none

## Tasks

### T-01 Push on a clean default branch only pushes
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/GitActionsControl.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/GitActionsControl.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/components/GitActionsControl.logic.test.ts

### T-02 Concealed text stays hidden under the cursor
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/terminal/ghostty/renderer.ts, repositories/anton-abyzov/specwithcode/apps/web/src/terminal/ghostty/renderer.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/terminal/ghostty/renderer.test.ts

### T-03 Connection guards and span privacy
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/onboarding.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/onboarding.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/relaySpanPrivacy.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/model.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/errors.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/compatibility.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/client-runtime && node ../../node_modules/vite-plus/bin/vp test run src/connection

### T-04 Private hosts never reach the favicon service
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/hostClassification.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/hostClassification.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/hostClassification.test.ts

### T-05 Android pairing banner reads the real target
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/android/app/src/main/kotlin/com/specwithcode/android/app/PairingInput.kt, repositories/anton-abyzov/specwithcode/apps/android/app/src/test/kotlin/com/specwithcode/android/PairingInputTest.kt | Test: grep -q "host=" repositories/anton-abyzov/specwithcode/apps/android/app/src/test/kotlin/com/specwithcode/android/PairingInputTest.kt

### T-06 Preview permission consent and trusted annotation submit
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/BrowserSession.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/BrowserSession.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PreviewPermissionConsent.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/AnnotationKeyboard.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/AnnotationKeyboard.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PickPreload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/RecordingCursor.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/RecordingCursor.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/preview/BrowserSession.test.ts src/preview/AnnotationKeyboard.test.ts

### T-07 Agent input waits while the person annotates
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/DesktopBrowserHost.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/DesktopBrowserHost.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/Manager.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/CdpRelay.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/CdpRelay.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/preview/DesktopBrowserHost.test.ts

### T-08 Isolated preview guests and narrow popups
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/WebviewPreferences.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/WebviewPreferences.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PageWorld.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PageWorldBridge.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PickPreload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/Manager.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/electron/ElectronShell.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/DesktopWindow.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/DesktopWindow.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/vite.config.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/preview src/window

### T-09 Backend readiness bound to this launch
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/backend/ | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/backend

### T-10 Push privacy and fail-closed rechecks
- AC: AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/agentActivity/, repositories/anton-abyzov/specwithcode/infra/relay/scripts/android-push-smoke.ts, repositories/anton-abyzov/specwithcode/infra/relay/scripts/android-push-watch.ts | Test: cd repositories/anton-abyzov/specwithcode/infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/agentActivity

### T-11 Relay link integrity
- AC: AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinker.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinker.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinks.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinks.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinks.integration.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentHardwareIdentity.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.originGuard.test.ts | Test: cd repositories/anton-abyzov/specwithcode/infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLink

### T-12 Trace privacy; account deletion removes live tunnels and follows Clerk deletions
- AC: AC-11, AC-14, AC-17 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/http/, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.originGuard.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedTunnelBinding.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointCloudflareBindings.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.disconnect.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/account/, repositories/anton-abyzov/specwithcode/infra/relay/src/admin/ConnectAdmin.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/admin/ConnectAdmin.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/worker.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/Config.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/Config.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentUnlink.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/webhooks/, repositories/anton-abyzov/specwithcode/infra/relay/alchemy.run.ts, repositories/anton-abyzov/specwithcode/infra/relay/README.md, repositories/anton-abyzov/specwithcode/.github/workflows/deploy-relay.yml | Test: cd repositories/anton-abyzov/specwithcode/infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/http src/account src/environments/ManagedEndpointProvider

Verify and close 1478.
