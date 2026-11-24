# Desktop Connect sign-in says it is waiting for the browser, and a second click starts over

## Problem

On the desktop app, "Continue with Google" (and every other sign-in through another site) looks dead when the browser round trip does not finish.

Evidence, linux-mini, November 16, 2026, desktop 1.0.322 (.deb), user journal:

- 03:03:34 EST: the first click. Chrome was not running; it started (`app-com.google.Chrome-358495.scope`) and restored three "New Tab" windows next to the sign-in page.
- 03:03:48, 03:03:53, 03:04:00, 03:04:10, 03:04:35: five more clicks, each refused in the main process with `Error occurred in handler for 'clerk:oauth-transport:open': Error: Clerk: an OAuth flow is already pending.`
- 03:06:34: `Clerk: OAuth callback timed out.` No `studio://app/` callback reached the app, so the sign-in in Chrome was never finished.
- The window showed nothing for any of this. Anton: "I clicked Continue with Google, and nothing happens."

Ruled out on that machine: keyring (`safe storage ready`, backend `gnome_libsecret`), the `studio://` handler (`specweave-studio-desktop.desktop`), the default browser (`google-chrome.desktop`), network to Google and the Clerk frontend API, and a launch without the desktop session (Chrome did open on the display).

Why it happens: `@clerk/electron` 0.0.44 opens the system browser with `shell.openExternal` and then waits up to 180 seconds for the `studio://app/` link (`dist/esm/index.js`, `setupOAuthTransportIpcHandlers`). While it waits, a new click throws. Nothing in our code shows the wait, the refusal, the timeout or a browser that failed to open (`apps/web/src/components/clerk/useStudioConnectAuthPrompt.tsx` only calls `clerk.openSignIn`).

The same gap exists on macOS and Windows; Linux only made it visible because the browser came up behind other windows.

## Scope

In: the desktop app's main-process handling of the Clerk OAuth open request, a state event to the window that asked, and a notice in the window. All three desktop platforms.

Out: the Clerk modal itself (it is Clerk's hosted UI), bringing the browser to the front, token storage, the machine's Connect link, sign-in in a plain browser at the machine's own address, the phone apps.

## Acceptance Criteria

- [ ] AC-01: When a sign-in through another site starts, the window that asked shows a notice within one second: the browser opened to finish signing in, and where to look if it is not in front. The notice stays until the sign-in finishes, fails or is replaced.
- [ ] AC-02: A second click while a sign-in is waiting opens the sign-in page in the browser again and keeps waiting. It is never refused, and the first wait ends without an error shown to the person.
- [ ] AC-03: When the browser cannot be opened, the window says so at once, with what to do. When the browser does not come back within 180 seconds, the window says the sign-in did not finish and that clicking again retries. Each message is one notice, not a stack.
- [ ] AC-04: When the callback arrives, the waiting notice goes away and the sign-in completes exactly as it does today (same callback match: scheme, host and path of the renderer origin; same main-frame check; same http/https check on the URL to open; `open-url` on macOS, `second-instance` on Windows and Linux).
- [ ] AC-05: A callback is delivered only to the newest waiting request. A replaced request can never receive one.
- [ ] AC-06: Every start, replacement, browser-open failure, timeout and completion is one main-process log line with no URL query, token or nonce in it.
- [ ] AC-07: A test fails when the SDK's channel name or callback rule changes, so a `@clerk/electron` bump cannot silently drop this handler.
- [ ] AC-08: Nothing changes for a window in a plain browser or for a build without Connect.

## Approach

1. `apps/desktop/src/app/DesktopClerkOAuthTransport.ts` (new): one function that owns the `clerk:oauth-transport:open` handler, with Electron's `ipcMain`, `app`, `shell.openExternal` and timers passed in. It keeps one waiting request. A new request replaces the old one (the old promise is rejected with a "replaced" error that the window never shows), opens the browser again and restarts the 180 second clock. It listens to `open-url` and `second-instance` itself and resolves with `{ callbackUrl }` in the shape the SDK returns. It reports `waiting`, `replaced`, `open-failed`, `timed-out` and `completed` to the window that asked.
2. `apps/desktop/src/app/DesktopClerk.ts`: after `createClerkBridge`, remove the SDK's handler for that one channel and install ours. The SDK's own listeners stay registered and never fire, because its waiting slot stays empty. `getRedirectUrl`, token storage, passkeys and the single-instance lock stay the SDK's.
3. `apps/desktop/src/ipc/channels.ts`, `apps/desktop/src/preload.ts`, `packages/contracts` (`DesktopBridge`): one event, `onConnectSignInState`.
4. `apps/web`: a small hook mounted inside `ElectronManagedAuthShell` turns the event into one toast (`toastManager`), replaced in place as the state changes.

Rejected:

- A `pnpm patch` of `@clerk/electron` that replaces the throw. Two lines, but it gives the window nothing to show, and it patches minified output in two module formats.
- Catching the rejection in the window (`unhandledrejection`). It cannot reopen the browser, and the refusal still costs the person three minutes.
- A shorter timeout. A real sign-in with a password manager and a second factor can take longer than a minute.

Risks:

- This replaces part of an auth SDK's transport. The rule that matches the callback and the two sender checks are copied, and AC-07 pins them to the installed SDK. It is an auth change: it needs Anton's acceptance before release.
- A browser tab from a replaced request can still finish later and send a callback. It reaches the newest request, as it does today after a timeout and a retry; Clerk decides whether that sign-in attempt is still good.

## Decisions

### Asked
- Anton accepted the auth change on November 16, 2026 ("yes, complete the job"), after the pull request and its report; the same answer covers the changed waiting sentence in D-04.

### Defaulted (change any before sw-do)
- D-01 A second click replaces the waiting sign-in and opens the browser again, instead of being refused. Reversible.
- D-02 The 180 second limit stays.
- D-03 The notice is a toast in the window that asked, not a change to Clerk's modal.
- D-04 Wording. Waiting: "Finish signing in in your browser" / "The sign-in page opened in your browser. If you don't see it, look for a new browser tab or window. To open it again, close this window and sign in again." (Changed November 16, 2026: Clerk disables its sign-in buttons while a sign-in waits, so a second click needs the dialog closed and opened again.) Browser did not open: "Couldn't open your browser" / "Open a browser on this computer, then click the button again." Timed out: "Sign-in didn't finish" / "The browser didn't come back within 3 minutes. Click the button again to retry."

### Open
- none

## Tasks

### T-01 Main process owns the OAuth open request
- AC: AC-02, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerkOAuthTransport.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerkOAuthTransport.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerk.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerk.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/app/DesktopClerkOAuthTransport.test.ts src/app/DesktopClerk.test.ts

### T-02 The handler stays in step with the SDK
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopClerkOAuthTransport.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/desktop && npx vp test run src/app/DesktopClerkOAuthTransport.test.ts

### T-03 State event reaches the window
- AC: AC-01, AC-03, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src | Test: cd repositories/anton-abyzov/specwithcode && npx vp run typecheck

### T-04 The window shows the notice
- AC: AC-01, AC-03, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/ElectronManagedAuthShell.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/useConnectSignInNotice.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/clerk/useConnectSignInNotice.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/clerk/useConnectSignInNotice.test.tsx

### T-05 Screenshots of the three notices
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/tests/connect-sign-in-notice | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node tests/connect-sign-in-notice/shoot.mjs
