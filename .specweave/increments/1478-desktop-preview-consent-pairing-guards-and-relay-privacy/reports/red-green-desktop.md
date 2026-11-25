# 1478 red and green: desktop lane (R1 to R4)

App repository `anton-abyzov/specwithcode`, branch `1474d-preview-pairing` from `origin/main` `2b7f17e8b`. Red runs used the test on unmodified source; green runs the same command after the fix. Raw logs: `~/.specwithcode/m4/scratch/2026-11-24-1478-desktop/`.

## R1 `ba640037e8`: preview permission consent and trusted annotation submit (T-06)

Commit `25d69116b`. Command: `cd apps/desktop && npx vp test run src/preview/BrowserSession.test.ts src/preview/AnnotationKeyboard.test.ts`.

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

What keeps working: `clipboard-sanitized-write` is still granted by both handlers without a prompt; a person's own Enter and Cmd/Ctrl+Enter still submit (unit test, and the real-Electron check below). The submit button's click handler now requires `event.isTrusted`; it has no unit test (the pick preload imports Electron), and the real-Electron check exercises only keyboard submit.

### Review follow-ups of R1 (PR #910 and #911 reviews)

The consent review's first finding (a page hijacks the submit listener in the shared JavaScript world) is closed by the isolation PR #911, so #910 and #911 merge together. Each commit below applies cleanly on `origin/main` alone (fixes 1 and 2) or on the #910 head `d843e7364` (fixes 3 and 4), without the isolation commit; checked with `git apply --check` on a temporary index.

1. Picker follows only the person's pointer, commit `62b12c2fb` (`apps/desktop/src/preview/PickPreload.ts`, 1,479 lines). The pick handlers for pointer move, down and up ignore `!event.isTrusted`. Real-Electron check, run 3 (`desktop-electron-check/result-decoy-red.json`, `result-decoy-green.json`): the person selects `#target`, then the page dispatches synthetic `pointermove`, `pointerdown`, `pointerup` and `click` on a decoy button, then the person types and presses Enter. Red (branch before the fix): the annotation names `["#decoy"]`. Green: `["#target"]`. Run 4 (green file) drives the pick with CDP `Input.dispatchMouseEvent`, `Input.insertText` and `Input.dispatchKeyEvent` through the tab's debugger, as the agent's relay does: it still selects `#target` and submits "via cdp".
2. Recordings show only the person's input, commit `3f2ed7b1c` (`apps/desktop/src/preview/RecordingCursor.ts`, new `RecordingCursor.test.ts`). Pointer move, down, up, cancel, out and key down and up ignore untrusted events. Command: `cd apps/desktop && npx vp test run src/preview/RecordingCursor.test.ts`. Red: `× records only the person's own keys and clicks`, `AssertionError: expected [ { type: 'pointer', …(5) }, …(5) ] to deeply equal []`. Green: `Tests 1 passed (1)`; the person's own down, up, key down and key up still emit.
3. Permission check reads the frame's own URL, commit `5fb87c56d` (`PreviewPermissionConsent.ts`, `BrowserSession.ts`, `BrowserSession.test.ts`). The check handler now passes Electron's `details.requestingUrl` and refuses when it has no readable origin, the same rule as the request handler; a check with no URL (a service worker) uses the requesting origin. Command: `cd apps/desktop && npx vp test run src/preview/BrowserSession.test.ts`. Red: `× refuses the check for a child frame without a readable origin of its own`, `AssertionError: about:blank: expected true to be false`. Green: `Tests 17 passed (17)`; the allowed `https://a.example/map` frame and the no-URL check still read granted.
4. Wrapped input waits too, commit `f1a57af7d` (`DesktopBrowserHost.ts`, `DesktopBrowserHost.test.ts`). While annotating, the relay refuses `Input.*` and any `Target.sendMessageToTarget` whose inner message is input, is unreadable or is wrapped more than four levels deep. A command on a flattened child session carries its own `Input.*` method and was already refused. Command: `cd apps/desktop && npx vp test run src/preview/DesktopBrowserHost.test.ts`. Red: `× refuses input wrapped in another command while the person annotates`, `TypeError: .toMatch() expects to receive a string, but got undefined` (no refusal reply; the wrapped input was sent). Green: `Tests 5 passed (5)`; a wrapped `DOM.enable` and wrapped input after the annotation ends still go through.

Residual, not fixed: a wheel event Chromium has already queued in its compositor before the annotation starts can still land on the page.

After all four: `cd apps/desktop && npx vp test run src/preview src/window src/electron`, `Tests 634 passed (634)`; desktop typecheck 0 errors.

### Round-2 follow-ups of R1 and R2 (PR #910 review at `0bf5a9fcf`)

Each commit applies on the #910 head `0bf5a9fcf` (checked with `git apply --check` on a temporary index).

A. The prompt names the whole origin, commit `10dbfdbbf` (`PreviewPermissionConsent.ts`, `BrowserSession.test.ts`). The prompt cut origins at 79 characters, so two origins sharing a long prefix read the same and the person could allow a different site (fail-open). It now shows scheme, full host and port; the dialog wraps long text. Command: `cd apps/desktop && npx vp test run src/preview/BrowserSession.test.ts`. Red: `× names the whole origin in the prompt, so two long origins never look alike`, `AssertionError: expected 'https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaa…' to not equal 'https://aaaaaaaaaaaaaaaaaaaaaaaaaaaaa…'`. Green: `Tests 18 passed (18)`; each message contains its full origin (`…trusted.example:8443`, `…attacker.example:8443`).

B. Only the person's Escape cancels, commit `a0b7b7039` (`PickPreload.ts`, 1,481 lines). The overlay's key handler (Escape and the tool keys) ignores `!event.isTrusted`. Real-Electron check, run 5 (`desktop-electron-check/result-escape-red.json`, `result-escape-green.json`): after the person selects `#target`, the page dispatches a synthetic Escape on `window`, `document` and the focused element. Red: the annotation is cancelled (`escapeCancelled: true`, the person's later Enter submits nothing). Green: not cancelled, and the person's Enter submits `["#target"]`. Run 6 (green file): the person's own Escape through `sendInputEvent` still cancels (`realEscapeCancelled: true`); runs 1 to 4 unchanged (no synthetic submit, decoy refused, CDP pick works).

C. Taken back out in round 3, follow-up below. Commit `0db9045b9` (agent input not counted as the person's) was dropped from the PR branch; the local checkout undoes it in `235e720cc`. What it tried and why it is out is under "Follow-up: agent input attributed to the person".

D. Residual, no change: while the person annotates, an agent can still scroll or change the page through `Runtime.evaluate` (the annotation guard in `DesktopBrowserHost.ts` checks only input). The guard covers `Input.*` as AC-02 says; page JavaScript is the agent's ordinary page control.

After A, B (and the since-removed C): `cd apps/desktop && npx vp test run src/preview src/window src/electron`, `Tests 636 passed (636)`; desktop typecheck 0 errors.

### Round-3 follow-ups of R1 and R2 (PR #910 review at `4449d7669`, with #911)

Base: #910 head `4449d7669` with `0db9045b9` removed, which is `a8925aa73`. Each commit was checked with `git format-patch -1 --stdout <sha> | GIT_INDEX_FILE=<temp> git apply --cached --check -` on a temporary index read from `a8925aa73`, alone and both together: both apply.

Local undo `235e720cc`: restores `DesktopBrowserHost.ts`, `DesktopBrowserHost.test.ts` and `Manager.ts` to before `0db9045b9`. It is for this checkout only; the coordinator drops `0db9045b9` from the PR branch, and nothing below builds on it.

E. A tab's debugger sessions reach only its own page and frames, commit `afc0a5000` (`CdpRelay.ts`, `CdpRelay.test.ts`, `DesktopBrowserHost.test.ts`). Fail-open: a CDP session from idle tab A could address tab B (`Target.attachToTarget` with B's target id, then any command on the returned session, or input through `Target.sendMessageToTarget`), and the annotation guard checked only tab A, so it never applied to B. Agent features checked first: Playwright's Chromium client uses only `Target.setAutoAttach`, `Target.detachFromTarget` and `Runtime.runIfWaitingForDebugger` on a page session; browser-level `Target.attachToTarget` already goes through the relay's own-target check; `Target.sendMessageToTarget` is used only by the WebKit client; the server's own `Target.createTarget` and `attachToTarget` calls are in its headless Chrome path, not the relay. Refusing cross-target commands breaks none of them, so the relay refuses rather than resolving the destination. It now tracks child sessions from `Target.attachedToTarget` and `Target.detachedFromTarget` events, allows `Target.setAutoAttach`, `Target.detachFromTarget` for a known child, and `Target.getTargetInfo` for its own or a child target; any other `Target.*` errors with "Not supported for a desktop preview tab: <method>", and a command on an unknown session errors with "Only this preview tab's page and its frames can be reached." Command: `cd apps/desktop && npx vp test run src/preview/CdpRelay.test.ts src/preview/DesktopBrowserHost.test.ts`. Red (test first, old relay): `Tests 2 failed | 9 passed`, `× CDP relay target scope` (the attach to another target got a session) and the wrapped-input test (the old relay sent `Target.sendMessageToTarget`). Green: `src/preview src/window src/electron` `Tests 636 passed (636)`; desktop typecheck 0 errors. Real Electron (headless, two hidden windows, relay bundled from the source, `desktop-electron-check/cross-tab.cjs`, `bundle-relay.mjs`): old relay `result-crosstab-old.json`, `attachToOtherTab` returned a session and `otherTabClicks: 1`; new relay `result-crosstab-new.json`, `"error": "Not supported for a desktop preview tab: Target.attachToTarget"`, unknown session refused, `otherTabClicks: 0`, own page still reached. Proof limit: the check had no out-of-process iframe, so the child-frame path (announce, command, detach) is covered by the unit test only.

F. The picker knows its overlay by reference, commit `7f8f056ff` (`PickPreload.ts`, 1,488 lines). Fail-open: the picker treated any element under a `data-studio-annotation-ui` host as its own overlay, and a page can put that attribute on its own elements, so a click on a marked page button passed through to the page during annotation and the button could not be picked. The isolated world now keeps the hosts it created in a `WeakSet`, and `isAnnotationNode` walks up (through shadow roots) looking for one of those nodes; the attribute stays only for styling. Real Electron (headless, `desktop-electron-check/check.cjs` run 6, a page button `#marked` carrying the marker and counting its own clicks, `fixture-app.jsx`): red `result-marked-red.json`, `markedClicks: 1`, `markedPick: null`; green `result-marked-green.json`, `markedClicks: 0`, `markedPick: ["#marked"]`, and runs 1 to 5 and 7 unchanged (no synthetic submit, decoy refused, synthetic Escape ignored, real Escape cancels, CDP pick works, the page sees no `ipcRenderer` or `require`). Unit: `src/preview src/window src/electron` `Tests 636 passed (636)`; typecheck 0 errors. Proof limit: no unit test for this path (the preload's DOM handling is checked in real Electron only).

### Follow-up: agent input attributed to the person (was round-2 C, out of #910)

The gap, which predates #910: CDP `Input.*` events are trusted in the page, so an agent's click or key reaches the human-input channel (takeover) and the recording overlays as the person's. Round-2 C marked a guest while the relay dispatched input and for 300 ms after the reply, and the manager dropped human-input and recording messages from a marked guest. Review points against it, to answer in the follow-up design:

1. Correlate per input, not by a timer: tag each relayed `Input.*` dispatch and match the guest's report to it, so attribution does not depend on IPC and debugger-reply timing.
2. Marks can expire before wrapped or slow input lands in the guest, so agent input is still counted as the person's.
3. Marks stick when a reply is lost (a dropped or detached session), so the person's real input is dropped until the mark clears.
4. A remote viewer's real input would be dropped while a mark is set (the reviewer's point; the path it takes into the guest is to be traced in the follow-up), so attribution must tell an agent's dispatch from a person's, wherever that person sits.
5. The human cursor that the recording overlay draws in the guest follows any trusted pointer, so it still moves with agent input; it has to follow the attributed source, not the raw event.

## R2 `fb04b4d199`, `4948c9afbe`: agent input waits while the person annotates (T-07)

Commit `44e3d463e`. Command: `cd apps/desktop && npx vp test run src/preview/DesktopBrowserHost.test.ts`.

Red, 1 failed, 3 passed:

```
× refuses relayed input while the person annotates the tab
AssertionError: expected [ 'Input.dispatchMouseEvent', …(2) ] to deeply equal [ 'Input.dispatchMouseEvent' ]
```

Green: `Tests 4 passed (4)`; with `src/preview/Manager.test.ts`, `Tests 104 passed (104)`.

Ours has no input queue between the relay and the debugger (`CdpRelay.ts:168` dispatches each command as it arrives), so the second upstream row (input queued before annotation starts) is covered by the same check, made at dispatch in `DesktopBrowserHost.ts` `send`. Non-input commands (`DOM.enable`) and input after the annotation ends still reach the page (same test).

## R3 `5e62206e7d`: isolated preview guests and web-only popups (T-08)

Two commits: popups `6d6817e19` (stands alone), isolation `9d85eab2a` (isolation only).

Popups. Command: `cd apps/desktop && npx vp test run src/window/DesktopWindow.test.ts -t popups`. Red:

```
× opens only web links from popups a frame in the app window asks for
AssertionError: expected [ 'https://example.com/docs', …(3) ] to deeply equal [ 'https://example.com/docs', …(1) ]
```

(today `vscode://vscode-remote/ssh-remote+…` and `zed://ssh/…` popups open). Green: `src/window/DesktopWindow.test.ts src/electron/ElectronShell.test.ts`, `Tests 62 passed (62)`. Editor links from the app still open: the web app calls `desktopBridge.openExternal` over IPC (`apps/web/src/localApi.ts:31`), which keeps `parseSafeExternalUrl`. `mailto:` was never opened by `ElectronShell.openExternal` and still is not. The upstream `openExternal` session permission refusal was not ported: the main window shares `session.defaultSession`, whose permission request handler `apps/desktop/src/ipc/methods/voice.ts:341` already owns.

Isolation unit. Command: `cd apps/desktop && npx vp test run src/preview/WebviewPreferences.test.ts`. Red: `× isolates the picker preload from the page`, `expected 'false' to be 'true'`. Green: `Tests 6 passed (6)`. Whole folder after both commits: `npx vp test run src/preview src/window src/electron`, `Test Files 43 passed (43)`, `Tests 631 passed (631)`. Desktop typecheck: 0 errors.

Isolation in a real Electron 44.10.1 (headless: hidden offscreen window, run by PID with `timeout 60`). Scripts and results: `reports/desktop-electron-check/` (`check.cjs`, `build-fixture.mjs`, `fixture-app.jsx`, `result-*.json`). The fixture is a React 19 development app whose page script, before the app loads, records `typeof ipcRenderer/require/process/electron` and patches `Element.prototype.attachShadow` to steal the overlay's closed shadow root. Each run starts a pick, selects the button with real `sendInputEvent` mouse input, lets the page try to submit its own text through the stolen root (synthetic Enter and Ctrl+Enter), then picks again as the person: real typed text and a real Enter.

| Run | Shadow root stolen | Synthetic submits | Person's pick |
|---|---|---|---|
| `origin/main` preload, `contextIsolation=false` (`result-old-shared.json`) | yes | 1 (page text sent as the person's annotation) | `FixtureButton`, `#target`, 4 stack frames |
| This branch's preload, `contextIsolation=true` (`result-new-isolated.json`) | no | 0 | `FixtureButton`, `#target`, 4 stack frames, comment "hello from the person", submission `attach` |

In the isolated run the page sees `ipcRenderer`, `require`, `process` and `electron` as `undefined`, and none of the bridge names (`readPageElementContext`, `pageWorld`, `installPageWorld`). The React component lookup runs in the page's world (`PageWorld.ts`, installed by `contextBridge.executeInMainWorld` in `PageWorldBridge.ts`); the build inlines `react-grab` into that function (`pageWorldFunction` in `apps/desktop/vite.config.ts`), and the built `dist-electron/preview-pick-preload.cjs` requires only `electron`. The new preload with isolation off (`result-new-shared.json`) does not load, as expected; nothing ships that way (`DesktopWindow.ts` forces isolation on for preview partitions).

Proof limits: the check uses a `BrowserWindow` with the guest's preferences, not a `<webview>` inside the app window; passkeys, recording input and the recording cursor were not exercised (they use DOM events and `ipcRenderer` inside the preload's own world, which isolation does not change).

## R4 `c9e22e5ff4`: backend readiness bound to this launch (T-09), blocked

Not shipped. Our desktop polls `GET` readiness over HTTP for every backend (`apps/desktop/src/backend/DesktopBackendManager.ts:617`), so a proof needs the backend to answer it. That needs files outside group D:

- `apps/server/src/http.ts` (group A): a `GET` route that answers a `challenge` query with `HMAC-SHA256(secret, "<prefix>:" + challenge)` in hex, and 404 when no secret was handed over or the challenge is empty or longer than 128 characters.
- `apps/server/src/config.ts` and `apps/server/src/cli/config.ts` (group A): carry an optional `desktopReadinessSecret` from the bootstrap into `ServerConfig`.
- `packages/contracts/src/desktopBootstrap.ts`: optional `desktopReadinessSecret` in `DesktopBackendBootstrap` (optional, so older backends and desktops stay compatible).
- `packages/shared/src/httpReadiness.ts` plus a new `packages/shared/src/desktopReadinessProof.ts`: an `accept(body)` hook on the poller, and the shared proof derive and timing-safe compare.

The desktop half (fresh secret per launch in the bootstrap, a fresh challenge per probe, readiness only on a matching proof) would then live in `apps/desktop/src/backend/DesktopBackendConfiguration.ts` and `DesktopBackendManager.ts`. A desktop-only half can never become ready, so T-09 is blocked with that reason.
