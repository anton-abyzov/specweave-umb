# 1490 Remote desktop: see and control another of your machines from your own devices

This increment holds the whole plan (`plan.md`) and builds slice 1: view another Mac's screen, view-only. Control, WebRTC, TURN, the phone, Windows and Linux are later increments, listed in `plan.md`.

Access change. Anton approved building it on November 25, 2026. Nothing here is on by default and nothing gives an agent the screen.

## Problem

On November 25, 2026 Anton asked: "is there some kind of a remote control where I could technically go ahead and see and control, through the UI, what is exactly happening on my machine? Maybe clicking some buttons, like logging in to the server in Google Chrome, leveraging my Touch ID." Then: "add passkey QR, and plan full remote desktop, go ahead and implement it with security in mind."

Today the owner can reach another of their machines only through threads, the terminal and files. To see what is on its screen they need macOS Screen Sharing, a third-party tool, or a trip to the desk. 1488 covers one Chrome tab for a website sign-in. Nothing shows the whole screen.

What the code has today (app at `origin/main` `61f3e8baa`):

1. **Capture is one still per request.** Computer use runs `/usr/sbin/screencapture` to a temp file (`apps/desktop/src/computerUse/MacComputerUse.ts:221`), main display only. Measured on M5: 0.5 to 0.8 s per capture, 3024x1986, about 750 KB as JPEG.
2. **Input is one `osascript` per action**, yields to the person at the machine and refuses the app's own windows (`computerUseJxaScripts.ts:54-58`, `MacComputerUse.ts:336-338`). It is built for agents, not for a person's pointer.
3. **The computer-use host is the app window's renderer.** A Mac with no window open has no host (`apps/web/src/state/computerUse.ts:68-101`). Any session with `terminal:operate` can register as host with a self-declared platform (`apps/server/src/auth/RpcAuthorization.ts:51-53`).
4. **No guard means "a person's approved device".** `principal.kind === "device"` is the default for every session (`SessionStore.ts:945`). `deviceApprover` also admits the startup link and dev tokens (`deviceApprover.ts:43-48`). `access.answerRequest` needs only `orchestration:operate`, so a remote window or a management key can answer an access card (`RpcAuthorization.ts:208`).
5. **Connect ends TLS at Cloudflare.** The tunnel is a proxied hostname to `http://127.0.0.1:<port>` (`infra/relay/src/environments/ManagedEndpointProvider.ts:1268-1313`). No client pins a machine key (`seal.ts:7-9`). A WebSocket ticket is valid 5 minutes and is not single-use (`SessionStore.ts:568`).
6. **No WebRTC sender, STUN or TURN exists.** The one `RTCPeerConnection` is a viewer for simulator streams (`packages/client-runtime/src/device/stream.ts:911`).

## Threat model

- **Adversary: the network path, Cloudflare's edge included.** It can read, drop, replay and change traffic, and replay a WebSocket ticket it saw. It must not see the screen, start a session, or change one.
- **Adversary: any session that is not a person's approved device.** Agent threads, worker grants, outside MCP clients, management keys, the local CLI credential, pairing tokens, the startup link. None may view, host, approve or switch the feature on.
- **Adversary: an agent with a shell on the target or on the viewing machine.** It must not be able to switch the feature on, add a grant, answer the prompt or read frames by writing files or calling local routes.
- **Trusted:** the relay Worker as a broker of who owns which machine (`docs/studio/security.md:58`), the approved-device list of 1327, macOS privacy grants, and the app's own code signature.
- **Out of reach (stated, not solved):** a process that already runs as the user and can inject code into the signed app or replace it; a person at the unlocked machine; macOS itself. A viewer opened in a plain browser tab cannot stop a screenshot taken by something else on that device.

## Scope

In (slice 1, macOS, view-only):

- A switch per machine, "Screen sharing", off by default, changed only in that machine's own app with a native confirmation.
- A viewer for the owner's approved Connect devices (the desktop app or a browser signed in to Connect): "View screen" on a connected machine's card.
- Approval on the target for each session, drawn by the app's main process, or a per-device "Always allow" grant made there.
- An always-on-top banner with Stop on the target for the whole session.
- An end-to-end encrypted session between the viewer and the target app, signed with the viewer's approved device key and with a machine key the viewer pins.
- Frames: JPEG, up to about 3 per second, sent only when the screen changes, with the pointer position. A locked Mac shows a placard, never the lock screen.
- A session list on the target (audit), timeouts, one session at a time.

Out (later increments, see `plan.md`): pointer and keyboard control; WebRTC video and TURN; the iPhone app; Windows and Linux targets; clipboard and file transfer (off by default when they come; files stay on `studio_file_transfer`); audio; several viewers at once; viewers on LAN, SSH or pairing-code routes (they hold no approved device key); a Mac with no app running or no logged-in desktop; any MCP tool, RPC or agent path to the screen.

## Acceptance Criteria

- [ ] AC-01: Screen sharing is off on every machine until its owner turns it on there. While it is off a viewer gets "off" at once: no prompt, no capture, no banner.
- [ ] AC-02: The switch and the per-device grants change only through the target app's own window, each turn-on and each grant behind a confirmation the main process draws. No HTTP route, RPC, MCP tool or `settings.json` key changes them. A store file that was edited, replaced or copied from another machine reads as off with no grants.
- [ ] AC-03: The server opens a viewer socket only for a Connect or phone-link session whose device key (`jkt:`) is on this machine's approved list and that holds no coordinator principal. A test refuses each other class by name: management key, `mcp-client`, `local-cli-owner`, `one-time-token`, startup link, dev tokens, the desktop app's own session, a phone link with no key, a Connect session with an unapproved or missing key, and a session carrying `boundDevice`.
- [ ] AC-04: The server accepts a host socket only from the machine's own app session (`desktop-bootstrap`, loopback, not over Connect, not a bot). Every other class is refused in a test. A second host replaces the first only with the same proof.
- [ ] AC-05: A session starts only after the viewer signs the handshake (machine id, session nonce, both session keys, mode) with its device key, in a JWS whose `typ` is not DPoP's. The target refuses a signature from another key, a key that differs from the one the server attested, a stale or replayed nonce and a changed handshake. The DPoP verifier refuses this JWS and the session verifier refuses a DPoP proof.
- [ ] AC-06: The target signs the handshake with its screen-sharing key. A viewer that has seen this machine before refuses any other key and says so. A viewer with no saved key shows a code that the target's prompt also shows, and the target then ignores any grant and asks.
- [ ] AC-07: After the handshake every message is sealed between the viewer and the target app. A test relay that flips a bit, replays a record or reorders two ends the session and shows nothing. The server process, logs, threads and audit list never hold a frame. No frame is written to disk except the fallback capture's own file, in a `0700` folder, deleted after the read.
- [ ] AC-08: With no grant, the target shows a prompt naming the device, its short ID and the code, with Deny, Allow once and Always allow. No answer in 60 seconds is Deny. Three refusals or timeouts for one device in 10 minutes stop further prompts for that device for 10 minutes. Only the prompt window's own click answers it.
- [ ] AC-09: From before the first frame until the session ends, the target shows an always-on-top banner on every desktop naming the device, with the elapsed time and Stop. Stop ends the session within 1 second. If the banner cannot be shown or is destroyed, the session ends. Turning the switch off ends it too.
- [ ] AC-10: Slice 1 is view-only: the target accepts only "frame received", "show display N" and "end" from the viewer. Any other message ends the session. The host code imports nothing from `computerUse`.
- [ ] AC-11: A session ends after 2 hours, after 2 minutes with no "frame received", when the device is removed or its sign-in ends (within 5 seconds, the existing socket watch), or when the app quits. A grant ends 30 days after its last use. One session at a time: a second viewer gets "busy".
- [ ] AC-12: The target keeps the last 500 session attempts: time, device name and short ID, how it was allowed or why it was refused, start, end and the reason it ended. Settings > Machines > Screen sharing lists them on that machine. No entry holds a frame.
- [ ] AC-13: While the target is locked the viewer gets a "This Mac is locked" placard and no frame. During a session the display is kept awake and is woken at the start.
- [ ] AC-14: Frames are at most 1920 px on the long edge, sent only when the picture changed, one unconfirmed frame at a time. In the fixture run the viewer draws each frame and the pointer mark at the reported position.
- [ ] AC-15: "View screen" shows on another machine's card only when that machine reports the capability and this device is approved there. The viewer shows each state in words: connecting, waiting for approval (with the code), live, locked, ended (with the reason), off, busy, not available on this system. With two displays the viewer can switch. End closes it.
- [ ] AC-16: No MCP tool, RPC or thread item reaches screen sharing: a test lists the MCP tools and the guarded RPC map and finds none. While the app shows another machine's screen, a whole-screen computer-use screenshot on the viewing machine is refused with a reason.
- [ ] AC-17: A Windows or Linux target, or a Mac with no app running, answers "not available" and the card says why. No switch shows there.

## Approach

Full design, alternatives and later slices: `plan.md`. In short:

- **The target app's main process is the authority.** It holds the switch, the grants, the machine key and the audit list in one store sealed with `safeStorage`, draws the prompt and the banner, captures the screen and ends the encryption. The server only checks who is calling and passes sealed bytes between two sockets.
- **Transport: two WebSockets through the existing server**, `GET /api/screen-share/host` (the app) and `GET /api/screen-share/view` (the viewer), on the pattern of `/api/preview-stream/ws`. No new RPC group, so `rpc.ts` and `ws.ts` are untouched.
- **Channel:** X25519 key agreement, HKDF-SHA256, AES-256-GCM with a counter per direction, in one WebCrypto module shared by the browser and the app (`packages/shared/src/screenShareChannel.ts`).
- **Capture:** `desktopCapturer` stills in the main process, with `screencapture` as the fallback (`reports/capture-spike.md`).
- Order: contracts and channel, server guard and relay, desktop store and session logic, desktop windows and IPC, web viewer and settings, docs.

Risks: the Screen Recording grant is read once at launch, so a fresh grant needs the existing relaunch step. `MachinesSettings.tsx` (1,351 lines) and `MacComputerUse.ts` (1,451) are near the 1,500 limit, so new code goes in new files. Live capture on a signed build cannot be proven from a worktree; see Decisions, Open.

## Decisions

### Asked
- D-01 Turning screen sharing on for a machine the owner is away from → waiting for Anton. Built as: only at that machine.
- D-02 A locked Mac → waiting for Anton. Built as: placard only.
- D-03 TURN relay spend (slice 4) → waiting for Anton. Nothing built yet.
- D-04 Typing into password fields over remote control (slice 2, 1438 D-01) → waiting for Anton. Nothing built yet.

### Defaulted (change any before sw-do)
- D-05 Slice 1 sends encrypted JPEG frames over the existing connection, not WebRTC. The brief asked for WebRTC over the relay with TURN; that is slices 3 and 4. Reasons: no sender-side WebRTC exists, Connect is optional so a non-WebRTC path is needed anyway, the iPhone app has no WebRTC library, TURN is spend, and frames need no new network path to review.
- D-06 Viewers are approved Connect devices only. A window paired by code, on LAN or over SSH has no device key to sign with and is refused.
- D-07 The app's main process, not the server, decides and encrypts. The server is one more hop that sees ciphertext.
- D-08 Approval is a main-process window, not the access card: a remote window or a management key can answer `access.answerRequest`.
- D-09 "Always allow" is per device and view-only, ends 30 days after its last use, and is offered only when a person presses it at the machine.
- D-10 Numbers: prompt 60 s, session 2 h, silence 2 min, cooldown 3 in 10 min, 500 audit entries, 3 frames per second, 1920 px.
- D-11 A locked Mac shows a placard; the lock screen itself is never streamed.
- D-12 Control comes before WebRTC (slice 2 before slice 3): clicking a button works at a few frames per second, and it is what the owner asked for first.

### Open
- Live capture on a Developer ID build is unproven until a release is installed and the owner turns the switch on at a Mac. Recorded as a proof limit in `reports/`.
- 1488 needs the same person-device guard (its AC-07). Whoever merges second imports the other's.

## Review
Adversarial review on Meta Muse (`muse-wonder-full-1.0`, high effort) for the plan and for each pull request. GPT-6.2 Sol only if Muse is unavailable. Never Grok.

## Tasks

### T-01 Capture spike and decision
- AC: AC-14 | Files: .specweave/increments/1490-remote-desktop-see-and-control-another-of-your-machines-from-your-own-devices/reports/capture-spike.md | Test: manual: the report holds the measured capture times and the chosen path

### T-02 Contracts and the sealed channel
- AC: AC-05, AC-06, AC-07, AC-10 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/screenShare.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/screenShareChannel.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/screenShareChannel.test.ts, repositories/anton-abyzov/specwithcode/packages/shared/package.json | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/screenShareChannel.test.ts

### T-03 Server: person-device guard, host guard and the relay
- AC: AC-03, AC-04, AC-07, AC-11, AC-16, AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/auth/personDevice.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/personDevice.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/screenShare/ScreenShareRelay.ts, repositories/anton-abyzov/specwithcode/apps/server/src/screenShare/ScreenShareRelay.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/screenShare/ScreenShareHttp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/screenShare/noAgentPath.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/personDevice.test.ts apps/server/src/screenShare/

### T-04 Desktop: sealed store, session rules, capture and the host
- AC: AC-01, AC-02, AC-05, AC-06, AC-08, AC-10, AC-11, AC-12, AC-13, AC-14 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenShareStore.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenShareStore.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenShareSession.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenShareSession.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenCapture.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenShareHost.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenShareHost.test.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/screenShare/

### T-05 Desktop: prompt, banner, IPC and the computer-use pause
- AC: AC-02, AC-08, AC-09, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenShareWindows.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenShareWindows.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenShareWindows.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screen-share-preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/screenShare.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/computerUse.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/DesktopIpcHandlers.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/apps/desktop/vite.config.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/scripts/build-desktop-artifact.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/screenShare/ && node node_modules/typescript/bin/tsc --noEmit --project apps/desktop/tsconfig.json

### T-06 Web: the switch, View screen and the viewer
- AC: AC-01, AC-06, AC-12, AC-14, AC-15, AC-17 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/ScreenShareSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/ViewScreenButton.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/ScreenViewer.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/screenViewer.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/screenViewer.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/screenShareClient.ts, repositories/anton-abyzov/specwithcode/apps/web/src/cloud/dpop.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/MachinesSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/screen-share/index.html, repositories/anton-abyzov/specwithcode/apps/web/tests/screen-share/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/screen-share/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/screen-share/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/components/screenShare/ && node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json

### T-07 Docs
- AC: AC-01, AC-15 | Files: repositories/anton-abyzov/specwithcode/docs/studio/security.md, repositories/anton-abyzov/specwithcode/docs/studio/screen-sharing.md, repositories/anton-abyzov/specwithcode/docs/operations/checks.md | Test: cd repositories/anton-abyzov/specwithcode && node scripts/studio-brand-audit.mjs
