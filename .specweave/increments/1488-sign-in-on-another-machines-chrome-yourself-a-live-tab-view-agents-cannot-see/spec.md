# Sign in on another machine's Chrome yourself: a live tab view agents cannot see

Auth change, accepted by Anton on November 25, 2026 (D-01): build, merge and release all slices.

## Problem

On November 25, 2026 the m1 EasyChamp routine "DCFC Square daily dues sync" ended with "Blockers: On m1: sign in to Square at https://app.squareup.com in the Chrome m1 profile." Anton was on M5, away from m1, and wrote: "I don't have access to the M1 machine. Just use the stored password for it. Just log in to it and complete the job." He then asked to "support some kind of logging into this remote machine securely, so that on the UI you could see and choose, for example, and log in with Chrome".

A helper thread on m1 found the Square session valid a few minutes later, so this time the routine's blocker was a false positive or a session Square had refreshed. Either way, nothing in SpecWithCode lets the owner finish a sign-in on a machine they are not sitting at. They can only reach that machine by hand (Screen Sharing, a trip to the desk) or ask an agent to type a password. The project's rules forbid the second option:

- **Passwords are typed only by the owner, in a prompt the machine itself draws** (1438 D-01, `decision_admin_password_prompt.md`). The stated reason: an in-app field "would send the password over the WebSocket and the Connect relay, and any command can print a fake `Password:` line to fish for it."
- **Signed-in browser work goes through the SpecWithCode Browser extension** (`feedback_chrome_extension_first.md`). A machine lends its Chrome to another machine only after the owner allows it there (`reference_fleet_phone_permissions.md`, "fleet chrome peer allow cli").
- **An agent must never type into a vendor's sign-in page** (1413 Scope, Out: "typing anything into a vendor's page (a password, a 2FA or emailed code)").
- **Extra access is asked for with the access card** (`decision_elevated_access_card_pattern.md`). Personal data is granted per machine and per source (`decision_personal_data_permission.md`).

What the code does today (app at `origin/main` `660fa63fd`):

1. **Any thread can see and take any tab.** `chrome_tabs` lists every tab in the profile with its address (`apps/server/src/browserExtension/chromeTools.ts:274-294`). A tab is held only while its thread acted in the last 120 seconds (`relayHub.ts:32`, `:544-567`). Settings › Chrome › Stop with no thread clears every hold (`relayHub.ts:614-631`).
2. **Every action is audited with its address**, readable by every client (`relayHub.ts:597-607`).
3. **The relay hub drops CDP events** except dialogs (`relayHub.ts:331-363`). There is no way to stream a tab.
4. **The extension already forwards** `chrome.debugger.onEvent` for attached tabs, and `chrome.tabs.onCreated` for popups against their opener (`apps/chrome-extension/src/relayConnection.js:118-125`, `:201-213`). Screencast frames and OAuth popups reach the server with no extension change.
5. **Connect is a Cloudflare tunnel** (`docs/studio/security.md:15`). TLS ends at Cloudflare's edge, so traffic is not end-to-end encrypted between devices. Fleet file transfer seals secrets with X25519 and AES-GCM (`apps/server/src/fleet/fileTransfer/seal.ts`) so the relay sees only ciphertext.

## Options compared

| Option | Owner types the secret | Agent can see it | Works with owner away | Effort | Verdict |
|---|---|---|---|---|---|
| A. Live tab view (CDP frames plus input relay) | Yes, into m1's page | No, if the tab is held for a person | Yes | Medium | **Recommended** |
| B. Passkey or OAuth handoff | No secret is typed | No | Only if the vendor offers it; cross-device passkeys need Bluetooth near m1 | Per vendor | Later, where available |
| C. Copy session cookies from another machine | No | Yes, the cookie is the account | Yes | Low | **Rejected** |
| D. Chrome's saved-password autofill on m1, pressed by an agent | No | The agent drives the page | Only with no macOS or Touch ID gate and no 2FA | Low | Narrow fallback |

- **A. Live tab view.** The server on m1 opens a fresh tab in the paired profile and holds it for a person. While the hold lasts, no thread can see or act in that tab. The owner's window (another Mac, the phone) shows frames of that tab and sends clicks and keys. The secret reaches only m1's page. Limits: Chrome's own UI (the autofill drop-down, passkey and Touch ID sheets, the permission bubble) is not part of the page, so it never shows in the view. OAuth popups open as new tabs, which the view follows (AC-08).
- **B. Passkey or OAuth handoff.** Signing in on the phone with a QR code (hybrid passkey) needs the phone within Bluetooth range of m1, which fails exactly when the owner is away. "Continue with Google" works only if Google is already signed in in m1's profile, and that is what D tries first.
- **C. Cookie transfer.** It moves a bearer credential across machines and through the relay. It breaks the vendor's device binding and risk checks, and it violates the "agents never hold sign-ins" rule. Rejected.
- **D. Saved-password autofill.** It does not cover a missing password, 2FA, or Chrome's re-authentication prompt. An agent driving a vendor's sign-in page also conflicts with 1413's Out list. It may stay as the first try in a routine's own instructions, with no product work.

## Scope

In:

- A server-held sign-in tab on the machine that owns the Chrome profile. It opens fresh, is hidden from every thread, sends frames and accepts input, shows its real origin, and ends on Done, on timeout or when the tab closes.
- Sealing of typed text to the session's key (seal.ts), so the relay and logs carry only ciphertext.
- Slice 2 (after D-01): an RPC for person sessions only, a "Sign-in needed on m1: Square" card raised through the access card, and the viewer in web and mobile.

Out: an agent typing into a vendor page. Copying cookies or passwords between machines. Reading Chrome's password store. Chrome's own UI (autofill drop-down, passkey and Touch ID sheets). Captchas that need audio. Machines whose Chrome is not paired. Video codecs and WebRTC (frames are JPEG over the existing connection).

## Acceptance Criteria

- [ ] AC-01: Starting a sign-in view opens a new tab in the named profile at the given https address, attaches the debugger, and holds the tab for a person. A thread's tab is never reused.
- [ ] AC-02: While the hold lasts, no thread sees or acts in that tab. `chrome_tabs` leaves it out. Every `chrome_*` tool that names it, or falls back to it as the thread's last tab, is refused. Settings › Chrome › Stop does not release it. `chrome_peer` goes through the same tools on the lending machine and is covered by the same refusal.
- [ ] AC-03: Nothing from the held tab reaches a thread, the audit list or a log. No `record` call, no frame or address in thread items, and no input text is ever stored.
- [ ] AC-04: The view gets frames of the tab (JPEG, at most about 2 per second, and only while a viewer listens). Each frame carries the page's origin as Chrome reports it over CDP (`Page.getNavigationHistory`), never as an agent or vendor states it.
- [ ] AC-05: The viewer sends clicks, scrolls, key presses and text. Coordinates are clamped to the frame. Text arrives sealed to the session's X25519 key and is unsealed only on the machine that owns the tab. A plain-text `text` input is refused.
- [ ] AC-06: The session ends on Done, after 10 minutes with no input (pulling frames does not keep it open), or when the tab closes. Ending detaches the debugger and releases the hold. Done leaves the tab open, so the signed-in session stays in the profile. Cancel closes the tab.
- [ ] AC-07: Only a person's device session may start, view or drive a sign-in view. A worker grant, an outside MCP client and an agent thread are refused (slice 2, with the new RPC). The card that offers it uses the access card pattern with a new subject kind.
- [ ] AC-08: A popup the held tab opens (OAuth) is held, viewed and ended with it.
- [ ] AC-10: When a page in the held tab asks for a passkey (`navigator.credentials.get` or `create` with `publicKey`), the next frame carries a notice with the kind and the site. The notice says that Chrome's passkey window is outside the view and that a phone passkey works only next to the machine, and it offers another way to sign in. The page's WebAuthn call runs unchanged. No challenge, credential, QR or hybrid data is read, relayed or proxied. The notice clears when the page navigates.
- [ ] AC-09: Agents ask for a sign-in with one tool: `chrome_sign_in_needed {url, reason, clientRequestId, profile?}`. It raises a sign-in card in the caller's thread and waits up to 4 minutes. It returns one word (done, cancelled, timed_out, tab_closed, declined, expired or signing_in) and never the address history, frames or keys. Calling it again with the same `clientRequestId` keeps waiting without a second card. A sign-in card stores no grant. It works on the machine whose Chrome it uses (slice 2).

## Approach

Slice 1 (this PR) builds the server primitive with no client entry point:

- `apps/server/src/browserExtension/relayHub.ts`: a person hold per profile (`personTabs`), kept apart from `tabOwners`. `claimTab` refuses a held tab with `tab_held_for_person`. `stop()` leaves it. `onEvent` hands screencast and navigation events for held tabs to a listener, and `chrome.tabs.onCreated` popups of a held tab are held too.
- `apps/server/src/browserExtension/chromeTools.ts`: `tabs()` leaves held tabs out. `useTab` already goes through `claimTab`.
- `apps/server/src/browserExtension/signInView.ts`, a new file: `SignInViews.start`, `frame`, `input`, `done`, `cancel`, plus an idle timer. Frames come from `Page.captureScreenshot` (JPEG, quality 60) polled while a viewer listens. `Page.startScreencast` sends no frames for a background or occluded tab, and the lending Mac's display may be asleep. It never calls `hub.record`.
- Sealed text uses `seal.ts`: the session makes a receiving key, the viewer gets its public half, and `input({type:"text", sealed})` unseals and sends `Input.insertText`.

Slice 2, after D-01:

- A guarded RPC (`browserExtension.signInView.*`) for device principals only, forwarded to the owning machine like `chrome_peer`.
- The access card subject `browser-sign-in`, and the viewer component in web (canvas, pointer and keyboard capture) and mobile.
- The `chrome_sign_in_needed` tool, and the routine wording "Sign-in needed on m1: Square" instead of a "Blockers" paragraph.

Risks: an active relay could swap the session key (seal.ts states that fleet machines pin by environment id, not by key). The viewer shows a 4-word key fingerprint that the card on the owner's own machine also shows. Frames of a signed-in page cross the relay, which is no worse than thread screenshots today.

## Passkeys (added November 25, 2026 at Anton's request: "add passkey QR")

The request was for the view to show Chrome's cross-device (hybrid) passkey QR, so the owner could approve with the iPhone's Face ID from anywhere. That cannot work, for two reasons:

- The hybrid flow requires a Bluetooth Low Energy advertisement from the phone to the computer that shows the QR. The data then travels through the vendor's tunnel. The Bluetooth step is a proximity check, and it exists precisely so that a QR relayed to a distant phone fails. This is the defence against "PoisonSeed"-style relayed-QR phishing. Sources: [mojoauth](https://mojoauth.com/blog/cross-device-passkey-qr-flow-where-users-drop-off), [The Hacker News](https://thehackernews.com/2025/07/poisonseed-hackers-bypass-fido-keys.html). An iPhone next to M5 cannot complete a QR that m1 shows.
- Chrome draws the passkey window and its QR in its own UI, outside the page. `Page.captureScreenshot` never sees it. Only a whole-screen capture of m1 would, and that belongs to the remote desktop work, which has the same Bluetooth limit.

What 1488 builds instead (AC-10, T-05): the view detects the request and tells the owner, who then picks the site's other sign-in method (password plus code, an emailed link). If the owner's phone is physically next to m1, the native flow works as usual. Nothing in WebAuthn is relayed, proxied or emulated: no virtual authenticator and no `WebAuthn.enable`.

## Review round 1 (GPT-6.2 Sol, November 25, 2026): FIX FIRST, 7 findings, all addressed in `31d793f77`

1. Races around the hold. The hub now refuses held-tab calls at dispatch and drops their answers. While a sign-in tab is being created, no thread takes a new tab. The debugger must detach cleanly, and "already attached" is refused.
2. Popups that close unseen. Popups are attached at once, a popup closed without an event is dropped after `tabs.get`, and a tab whose opener is held is held too, both in `chrome_tabs` and in `useTab`.
3. Frame and origin binding. Each frame names `tabId:navigationEntryId`, a frame taken across a navigation is discarded, input must name the current frame, and text goes only to https pages.
4. Cleanup. Holds stay until Chrome confirms. Cancel and idle close the tabs. In-flight calls settle first. Holds survive a reconnect, and a failed teardown finishes on reconnect.
5. Frames in clear. Frames are sealed to the viewer's X25519 key. Only named keys with no character of their own are sent as keys. Every failure of a secret-bearing command returns one fixed message. Proof limit: the view key is not authenticated against a pinned identity of the machine. A fingerprint is shown instead (follow-up).
6. Replay. Sealed text carries a sequence number, which is spent before dispatch, and its size is capped before decoding.
7. Leaks. A refused thread gets a generic "not available", held tabs are not counted in Settings, and `dispose()` unsubscribes.

## Review round 2 (Meta Muse Wonder Full 1.0, high, November 25, 2026): FIX FIRST, 9 findings, all addressed in `de316f0ca`

1. A failed `tabs.get` counted as a closed tab. Now only Chrome's "No tab with id" proves a tab is closed. Transport errors keep the hold, and orphaned teardowns retry every 30 s as well as on reconnect.
2. Popups found by their opener were held forever. `holdForPerson` now reports them to their view. Teardown walks every tab held for the view, and a popup reported after the end is closed (Cancel) or released (Done).
3. A closed main tab left its popups open. They now close with it.
4. `callTabId` missed some shapes. `tabs.remove` with a list is now checked id by id, and `tabs.update` without an id is refused.
5. The passkey notice named the page's `rpId`. It now names the host from Chrome's navigation history.
6. The passkey binding was unproven on real Chrome. `Runtime.enable` was added (`2c519246c`) and checked on real headless Chrome. Proof limit: a popup that asks for a passkey before it is attached is not reported.
7. Legacy holds were lost when an install started sending an `instanceId`. They now carry over.
8. Frames had a fail-open sentinel. Input must name a frame the view sent, with the same origin and a history entry. Residual: a navigation between the check and `Input.insertText`.
9. The Settings tab count included held tabs. It no longer does.

## Review round 3 (Meta Muse Wonder Full 1.0, high, November 25, 2026): FIX FIRST, 5 findings, all addressed in `520c45efa`

Round 3 also confirmed all nine round 2 fixes.

1. High: `start` did not check that the card was allowed, and an agent can compute the request id. Now `start` waits up to 10 s for the card's Allow and otherwise opens nothing in Chrome. The sign-in RPCs were already owner-only, so a thread cannot call `start` itself.
2. Medium: the view id worked as a bearer secret. Each view now has a random token that travels only inside sealed frames. Input and Done need it. Cancel does not, since it only closes the tab.
3. Medium: closing the window while the view opened left the tab held, and a failed start had no retry. The viewer now cancels a view that finishes opening after its window closed, and offers "Try again" after a failed start.
4. Low: pulling frames counted as activity. Only input resets the 10 minute idle limit now.
5. Low: nothing capped the requests or popups. A thread may have 5 sign-ins waiting, and a view may hold 10 popups.

## Review round 4 (Meta Muse Wonder Full 1.0, high, November 25, 2026): SHIP at `520c45efa`, 5 low findings

All five round 3 fixes hold. No path carries typed text or the held tab to a thread.

1. A decline or expiry during the 10 s Allow wait did not wake `start`, which then answered "Allow first". Fixed in `29ea2acf6`: it hears "has ended" at once and opens nothing.
2. A start already waiting may win the view when the person allows from another device. That device then shows "already open" and the person types nothing, so no secret moves. This is closed by the person-device guard follow-up (see Proof limits).
3. Frame pulls need only the view id, so another owner session could take the one-shot dialog notice. Accepted: the frames are sealed, and a frame is how the window gets the token.
4. The popup cap counts popups the view follows, not hub holds, which stay until teardown. Accepted: teardown releases every hold for the view.
5. Regression tests. `29ea2acf6` adds tests for a decline while Chrome attaches (tab closed), for a decline during the Allow wait, and for frame pulls that do not keep a view open. The unmount cancel and Try again in the web viewer have no automated test yet.

## Proof limits

- The view key is not authenticated against a pinned identity of the machine. A fingerprint is shown in the view.
- `chrome_sign_in_needed` uses the caller's own machine's Chrome. A thread on M5 asking for m1's Chrome is refused with a pointer to run it on m1 (follow-up: forward over `chrome_peer`).
- The web viewer is checked in a headless fixture (real card and view components, real WebCrypto sealing, a stand-in machine) and by unit tests. A live run with the real extension on m1 waits for the release.
- The sign-in methods refuse coordinator keys only. A local owner credential (for example `local-cli-owner`) could answer the card and open a view itself. It would get a fresh tab it can already reach with chrome tools. It would not get what the person types or sees: frames are sealed to the starting window's key, input and Done need a token carried only inside those frames, and one request opens one view. Follow-up: switch to the person-device guard that 1490 adds in `apps/server/src/auth/personDevice.ts`.
- The iOS app shows a sign-in card as an unknown subject kind (it treats kinds as an open enum). A native viewer is a follow-up.

## Decisions

### Asked
- D-01: 1438 D-01 says passwords are typed only in a prompt drawn by the machine itself. May the owner's keystrokes reach another machine's Chrome page over Connect through this view, as a narrow exception under (a) text sealed end to end to a per-view key, (b) only the owner's device sessions may open the view, (c) the origin always shown as that machine's Chrome reports it, (d) agents blind to the tab? → **Yes** (Anton, November 25, 2026: "yes yes, connect through it and control. Do everything you need. I allow fully."). Recorded in project memory `decision_remote_sign_in_view.md`; administrator passwords stay under 1438 D-01.
- D-05: change the Square password that a routine printed in plain text on November 25? → **No** (Anton: "No, don't change it. You have Obsidian notes, and it's all saved and stored there."). Accepted risk, see `reports/accepted-risk.md`. The routines on m1 are changed so they never read or print credentials.

### Defaulted (change any before sw-do)
- D-02: frames come from polled `Page.captureScreenshot` (JPEG q60, about 2 per second), not `Page.startScreencast`, because a background tab on an unattended Mac sends no screencast frames. Reversible.
- D-03: the idle timeout is 10 minutes. Done keeps the tab and Cancel closes it.
- D-04: option D (saved-password autofill pressed by an agent) gets no product work. Routines may try an existing session or "Continue with Google" first, as today.

### Open
- none

## Tasks

### T-01 Person hold in the relay hub and tab listing
- AC: AC-02, AC-03, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/relayHub.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/chromeTools.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/browserExtension/signInView.test.ts apps/server/src/browserExtension/chromeTools.test.ts

### T-02 Sign-in view session: open, frames, sealed input, end
- AC: AC-01, AC-03, AC-04, AC-05, AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/signInView.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/signInView.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/fakeChrome.testkit.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/browserExtension/signInView.test.ts

### T-03 Mockup of the card and the viewer
- AC: AC-07, AC-09 | Files: .specweave/increments/1488-sign-in-on-another-machines-chrome-yourself-a-live-tab-view-agents-cannot-see/reports/mockup.html | Test: manual: the mockup screenshot exists in reports/

### T-05 Passkey request notice (no WebAuthn relay)
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/signInView.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/signInView.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/browserExtension/signInView.test.ts

### T-04 RPC for person sessions, access card subject, viewer (slice 2, after D-01)
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/browserSignIn.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/signInRequests.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/BrowserExtension.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/chrome/signInTool.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/signInSeal.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/signIn/SignInViewer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AccessRequestCard.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/browserExtension/ apps/server/src/mcp/toolkits/chrome/ apps/server/src/access/AccessRequests.test.ts apps/server/src/auth/RpcAuthorization.away.test.ts
