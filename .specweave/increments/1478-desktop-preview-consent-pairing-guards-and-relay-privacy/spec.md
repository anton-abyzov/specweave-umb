# 1478 Desktop preview consent, pairing guards and relay privacy

## Problem

The November 14 to 25, 2026 review of the last open T3 Code copy (increment 1474, wave 1 group D) found 17 security and privacy defects in our desktop preview, client pairing code and Connect relay. Lane notes: `.specweave/increments/1474-t3-code-changes-since-november-14-the-last-open-copy/reports/lanes/` (`s1-security.md`, `s2-security.md`, `c1-platform.md`, `c2-platform.md`, `d1-web.md`, `d2-web.md`, `e-mobile.md`).

- Desktop preview: any preview page gets clipboard read, notifications and location without asking (`apps/desktop/src/preview/BrowserSession.ts:31`); a page script can submit the annotation box with a synthetic Enter or click (`AnnotationKeyboard.ts:15`, `PickPreload.ts:1422`); agent input relayed through CDP reaches the page while the person annotates (`DesktopBrowserHost.ts:106`); preview guests share one JavaScript world with an IPC preload (`WebviewPreferences.ts:42`) and app popups can open editor schemes (`DesktopWindow.ts:963`); any HTTP 200 on the backend port counts as our backend (`DesktopBackendManager.ts:617`).
- Clients: Push on a clean default branch runs commit and push, so files changed while the confirm dialog is open get committed (`GitActionsControl.logic.ts:316`); the terminal block cursor draws concealed text (`renderer.ts:265`); SSH onboarding can add a route to a saved environment it does not own (`onboarding.ts:326`); relay spans carry machine labels (`supervisor.ts:230`); internal hostnames reach the public favicon service (`hostClassification.ts:130`); Android link mode shows and cleartext-checks one host while pairing with the `?host=` target (`PairingInput.kt:77-80`).
- Relay: traces record callers' IP address and user agent (`Api.ts:273`); an account bearer can relink an active environment under another key (`EnvironmentLinks.ts:265`); switching accounts leaves the previous account's link active (`EnvironmentLinks.ts:242`); account deletion cannot remove a live host's tunnel (`ManagedEndpointProvider.ts:766`); queued APNs jobs deliver when the activity recheck fails (`ApnsDeliveries.ts:603`); Android pushes send the account user id to Google (`FcmDeliveries.ts:301`); relay data outlives a Clerk-side account deletion (`Api.ts:830`).

## Scope

In: the 18 upstream rows below, each rewritten in our own code with a test that fails before and passes after (`reports/red-green.md`). Files: `apps/desktop/*`, `apps/web/src/components/GitActionsControl.logic.ts`, `apps/web/src/terminal/ghostty/renderer.ts`, `packages/client-runtime/src/connection/*`, `packages/shared/src/hostClassification.ts`, `apps/android/app/src/main/kotlin/com/specwithcode/android/app/PairingInput.kt`, `infra/relay/*`, plus their tests.

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

## Acceptance Criteria

- [ ] AC-01: A preview page asking for clipboard read, notifications or location gets it only after the person allows it for that origin (remembered for the session); a frame whose origin cannot be read is refused. Annotation submit (Enter and the submit button) accepts only trusted events. Must keep working: a person's own Enter, Ctrl/Cmd+Enter and click submit an annotation; other preview permissions keep their current answer.
- [ ] AC-02: While the person annotates a preview tab, relayed `Input.*` CDP commands are refused, including commands queued before annotation started and dispatched after. Non-input CDP commands and input after annotation ends keep working.
- [ ] AC-03: Preview guests run with `contextIsolation=true`; page script cannot reach `ipcRenderer`, `require` or the preload's own objects. App-window popups open externally only for http, https and mailto links. Must keep working: element picking, annotations, the human-input and recording channels of the pick preload, and http(s) links opened from the app window.
- [ ] AC-04: The desktop app counts its backend ready only when the listener proves it holds this launch's readiness secret; a listener answering 200 without the proof keeps readiness waiting. A normal local launch and a WSL launch still become ready.
- [ ] AC-05: Push on a clean default branch that is ahead runs `push`, never `commit_push`, with and without an upstream; a dirty default branch keeps its commit actions.
- [ ] AC-06: Concealed (SGR 8) terminal text is not drawn under the block cursor or decorated; visible text under the cursor still draws.
- [ ] AC-07: Untargeted SSH onboarding that reports an environment already saved under another address fails with the known-address guard and leaves the registry unchanged; targeted SSH reconnects and new SSH hosts still register.
- [ ] AC-08: Relay connection spans carry no machine label attribute.
- [ ] AC-09: Hosts under `.lan`, `.localdomain`, `.corp`, `.home`, `.intranet`, `.private` (and the other RFC 6762 Appendix G names) are never sent to the favicon service; public hosts still are.
- [ ] AC-10: On Android, a pairing link's banner host and cleartext guard read the target that pairing actually uses (`?host=` when present); a plain link and a manual entry keep today's answers.
- [ ] AC-11: Relay request spans record neither the caller's IP address nor user agent, while route handlers still receive both.
- [ ] AC-12: The relay refuses to relink an active environment under a different key, before any replacement, provisioning or write, and leaves the stored key unchanged; relinking with the same key, relinking after an unlink and the same-machine replacement path still work. A machine whose key changed while its environment id survived (secret store reset) must be unlinked in Connect first.
- [ ] AC-13: When an environment and key link under a new account, the previous account's active link for that environment and key is revoked in the same atomic D1 batch as the new link (credentials belong to the key and stay), and the previous account's tunnel is removed best effort.
- [ ] AC-14: Account deletion removes a live host's tunnel by dropping its connectors and then deleting it, and frees the allocation; an ordinary unlink of a live host keeps today's behaviour (tunnel left for later).
- [ ] AC-15: A queued APNs job whose activity recheck fails is skipped, not delivered.
- [ ] AC-16: Android push data sent to Google carries no account user id.
- [ ] AC-17: A Clerk `user.deleted` webhook with a valid Svix signature inside a 5-minute window deletes that user's relay records; a bad signature, an old timestamp or a missing signing secret is refused and deletes nothing.

## Approach

Three lanes with disjoint files, one PR each, all from current `origin/main` of `anton-abyzov/specwithcode`:

1. Clients (PR "clients"): R5 change both clean-branch quick actions to `push`; R6 skip invisible cells in the decoration loop and in cursor text; R7 pass `knownAddressOnly` for untargeted SSH registration; R8 drop the `environment.label` span annotation; R9 extend the private suffix list; R10 read the target through the transport's `PairingLink.parse` (its `httpBase`) in `PairingInput.host` and `isCleartext`.
2. Desktop preview (PR "preview"): R1 a per-origin, per-session consent prompt in `BrowserSession.ts` for the three permissions, `isTrusted` checks in the annotation keyboard and submit click; R2 an `annotating()` check on the debuggee before dispatch and again just before send; R3 `contextIsolation=true` with the pick and annotation calls exposed through a narrow bridge, and a popup allowlist of http, https and mailto; R4 a per-launch readiness secret handed to the child, a challenge route answering with its HMAC, and readiness bound to that proof.
3. Relay (PR "relay"): R11 the tracer gets a request copy without remote address and user agent; R12 read the active link before provisioning and refuse a key change; R13 revoke other accounts' active links for the same environment and key and write link plus credential in one D1 batch; R14 a tunnel `disconnect` (rotate secret, drop connections) used only by account deletion when the tunnel is in use; R15 fail closed in both recheck catch arms; R16 replace the user id with a per-device hash or drop it; R17 a Svix-verified Clerk webhook route behind a missing-secret refusal.

Files already over 1,500 lines (`ManagedEndpointProvider.ts`, `Manager.ts`, `DesktopWindow.ts`, `Api.ts`) do not grow: new logic goes in new files.

Risks: R3 can break picking (the pick preload relies on page-world access, for example the React DevTools hook); R4 must stay wire-compatible with the server child the desktop launches; R14 replaces the Worker's tunnel binding and is only proven by the relay deploy.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01 R12 keeps `packages/contracts/src/relay.ts` unchanged (not in this group's files, and older servers would not decode a new literal): the relay refuses with an existing wire reason and logs `environment_key_mismatch` with its own stage. A dedicated reason and recovery hint is a follow-up for the owners of the contract and `apps/server/src/cloud/relayResponse.ts`.
- D-02 R1 asks for clipboard read, notifications and location once per origin per preview session, with Block as the default button; other permissions keep today's answer.
- D-03 R17 answers 503 to every webhook request while the signing secret is unset, 401 to a bad signature or a timestamp more than 5 minutes off. The owner creates the Clerk webhook and secret.
- D-04 All three APNs delivery-time rechecks fail closed: the state identity check, the aggregate rows check and the live-work start check skip the job when their read fails (the start recheck since the PR #912 review).
- D-05 R8 drops only the label in `supervisor.ts`; the error-message export in `packages/shared/src/relayTracing.ts` is reported as a follow-up (not in this group's files; relay tracing has no endpoint configured in our builds).
- D-06 R10 is checked by a JVM unit test; this machine has no Java runtime, so the Gradle run is the PR's Android CI job.

### Open
- none

## Tasks

### T-01 Push on a clean default branch only pushes
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/GitActionsControl.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/GitActionsControl.logic.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/components/GitActionsControl.logic.test.ts

### T-02 Concealed text stays hidden under the cursor
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/terminal/ghostty/renderer.ts, repositories/anton-abyzov/specwithcode/apps/web/src/terminal/ghostty/renderer.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run --passWithNoTests --project unit src/terminal/ghostty/renderer.test.ts

### T-03 Connection guards and span privacy
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/onboarding.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/onboarding.test.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/connection/supervisor.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/client-runtime && node ../../node_modules/vite-plus/bin/vp test run src/connection

### T-04 Private hosts never reach the favicon service
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/hostClassification.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/hostClassification.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/hostClassification.test.ts

### T-05 Android pairing banner reads the real target
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/android/app/src/main/kotlin/com/specwithcode/android/app/PairingInput.kt, repositories/anton-abyzov/specwithcode/apps/android/app/src/test/kotlin/com/specwithcode/android/PairingInputTest.kt | Test: grep -q "host=" repositories/anton-abyzov/specwithcode/apps/android/app/src/test/kotlin/com/specwithcode/android/PairingInputTest.kt

### T-06 Preview permission consent and trusted annotation submit
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/BrowserSession.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/BrowserSession.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PreviewPermissionConsent.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/AnnotationKeyboard.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/AnnotationKeyboard.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PickPreload.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/preview/BrowserSession.test.ts src/preview/AnnotationKeyboard.test.ts

### T-07 Agent input waits while the person annotates
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/DesktopBrowserHost.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/DesktopBrowserHost.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/Manager.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/preview/DesktopBrowserHost.test.ts

### T-08 Isolated preview guests and narrow popups
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/WebviewPreferences.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/WebviewPreferences.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PageWorld.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PageWorldBridge.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/PickPreload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preview/Manager.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/electron/ElectronShell.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/DesktopWindow.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/window/DesktopWindow.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/vite.config.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/preview src/window

### T-09 Backend readiness bound to this launch
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/backend/ | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/backend

### T-10 Push privacy and fail-closed rechecks
- AC: AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/agentActivity/ | Test: cd repositories/anton-abyzov/specwithcode/infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/agentActivity

### T-11 Relay link integrity
- AC: AC-12, AC-13 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinker.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinker.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinks.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinks.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentLinks.integration.test.ts | Test: cd repositories/anton-abyzov/specwithcode/infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/environments/EnvironmentLink

### T-12 Trace privacy; account deletion removes live tunnels and follows Clerk deletions
- AC: AC-11, AC-14, AC-17 | Files: repositories/anton-abyzov/specwithcode/infra/relay/src/http/, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedEndpointProvider.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/ManagedTunnelBinding.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/account/, repositories/anton-abyzov/specwithcode/infra/relay/src/worker.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/Config.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/Config.test.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/environments/EnvironmentUnlink.ts, repositories/anton-abyzov/specwithcode/infra/relay/src/webhooks/, repositories/anton-abyzov/specwithcode/infra/relay/alchemy.run.ts, repositories/anton-abyzov/specwithcode/infra/relay/README.md, repositories/anton-abyzov/specwithcode/.github/workflows/deploy-relay.yml | Test: cd repositories/anton-abyzov/specwithcode/infra/relay && npx vp test run --config ../../vite.config.ts --dir . src/http src/account src/environments/ManagedEndpointProvider

Verify and close 1478.
