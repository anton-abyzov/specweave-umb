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
- [ ] AC-06: The session ends on Done, after 10 minutes with no frame pulled and no input, or when the tab closes. Ending detaches the debugger and releases the hold. Done leaves the tab open, so the signed-in session stays in the profile. Cancel closes the tab.
- [ ] AC-07: Only a person's device session may start, view or drive a sign-in view. A worker grant, an outside MCP client and an agent thread are refused (slice 2, with the new RPC). The card that offers it uses the access card pattern with a new subject kind.
- [ ] AC-08: A popup the held tab opens (OAuth) is held, viewed and ended with it.
- [ ] AC-09: Agents ask for a sign-in with one tool: `chrome_sign_in_needed {profile, url, reason}`. It raises the card and returns at once. When the session ends the thread hears only "signed in: done or cancelled", never the address history or frames (slice 2).

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

### T-04 RPC for person sessions, access card subject, viewer (slice 2, after D-01)
- AC: AC-07, AC-08, AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/browserExtension.ts, repositories/anton-abyzov/specwithcode/apps/server/src/browserExtension/BrowserExtension.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/SignInViewCard.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/browserExtension/
