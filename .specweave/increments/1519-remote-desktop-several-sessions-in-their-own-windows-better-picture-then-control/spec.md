# Remote desktop: several sessions in their own windows, better picture, then control

Follow-up to [1490](../1490-remote-desktop-see-and-control-another-of-your-machines-from-your-own-devices/spec.md) (slice 1, view-only, shipped in 1.0.443, PR #955). Its threat model, access rules, sealed channel and `plan.md` sections 5 to 9 stand and are not repeated here. Two pull requests: PR 1 (sessions, windows, picture; no security rule changes), then PR 2 (control, 1490 slice 2).

## Problem

On November 28, 2026 the owner viewed m1 from M5 and said: "I cannot click anything, also. ... I should be able to run multiple remote desktop connections connecting to different machines. ... Maybe it could even be detached from the window, or down in a separate window ... research the best implementation." Then: "go and complete the job as recommended".

What the code has today (app `origin/main` `7cf4849eb`, 1.0.460):

1. **One view at a time, inside the window.** `apps/web/src/components/screenShare/ViewScreenButton.tsx` opens a Dialog over the app window. There is no window of its own, no way to watch two machines side by side, and the dialog covers the app.
2. **Computer use can resume while a remote screen is still shown.** `apps/desktop/src/ipc/methods/screenShare.ts` keeps `screenShareViewing` as a Set of window ids. Two views in one window both call `setViewing(true)`; closing one calls `setViewing(false)` and clears the window, so computer use resumes while the other still shows another machine's screen. Each `setViewing(true)` also adds another `destroyed` listener.
3. **The picture is fixed and slow.** Frames are at most 1920 px on the long edge whatever the window size (m1's screen is 3456x2234), at most one every 330 ms, JPEG quality 60. `ScreenCapture.ts` calls `desktopCapturer.getSources` on every tick and encodes JPEG before it compares, so a still screen costs capture and encode every 330 ms. Nothing measures frame rate, bytes or delay.
4. **No control.** Slice 1 accepts only four viewer records (1490 AC-10). D-05 (November 28, 2026) decided how control is granted; nothing implements it.

## Research

Sources and the full comparison: `reports/research-remote-desktop-products.md`. Summary of what decides this increment:

| | Transport and codec | Several hosts at once | Host consent | Input and elevated prompts |
|---|---|---|---|---|
| macOS Screen Sharing | RFB/VNC with Apple security types; High Performance over UDP, 30 or 60 fps; codec not named by Apple | saved hosts in a Connections window; window model unverified | ask permission, or allowed users and password | unverified |
| Chrome Remote Desktop | WebRTC (ICE, STUN/TURN); VP8, VP9, AV1; 30 fps target | one browser tab per session | share dialog, banner, 30-minute recheck, PIN for unattended | Windows service injects, including SAS |
| Parsec (u) | own UDP protocol over DTLS 1.2; H.264, H.265 options | separate app instances | host approves guests, per-guest input permission | Windows SYSTEM service |
| RustDesk | own protocol over TCP/UDP with relay; VP8, VP9, AV1, H.264, H.265; 30 fps default, adaptive | tabs, or separate windows | accept window with permission toggles; password, click or both | Windows service, SendSAS |
| ScreenCaptureKit + CGEvent | `SCStream` with `minimumFrameInterval`; stills or VideoToolbox | up to the app | up to the app; macOS shows its capture indicator | `CGEventPost` needs Accessibility; secure input cannot be bypassed (`IsSecureEventInputEnabled`) |

(u): Parsec's help pages refused every fetch; those cells rest on search summaries. Each cell's source URL is in the report.

What follows for SpecWithCode: one native window per machine is the common pattern and the one the owner asked for. A still-frame protocol is bounded by one round trip per frame because of its backpressure, so away from home (owner in Boston, m1 at home) the frame rate is limited by the round trip through Cloudflare, not by capture. That is an estimate: no TURN or WebRTC path exists yet to measure. WebRTC video (slice 3) removes the per-frame round trip; TURN (slice 4) is the fallback when no direct path forms. Windows (DXGI or Windows Graphics Capture with `SendInput`) and Linux (xdg-desktop-portal ScreenCast and RemoteDesktop through PipeWire and libei) stay later slices, 6 and 7 of 1490 `plan.md`.

## Scope

In, PR 1 (no change to who may view, the switch, grants, prompt or banner):

- Several sessions at once, each to a different machine. One session per target machine stays (the target answers "busy" to a second viewer).
- One native window per machine, titled "Screen of <machine>", resizable, remembering its size and place; "View screen" opens it or brings it forward. A view can still open inside the current window. In a plain browser tab, where there is no desktop bridge, the in-page viewer stays.
- Computer use on the viewing machine pauses while any window shows a remote screen, counted per view.
- A sharper, faster picture: capture sized to the viewer's window times its pixel ratio, more frames while the screen changes, change detection before JPEG encoding, a size guard before sealing, and a "Low bandwidth" choice.
- Measurement: frame rate, bytes per frame and capture-to-confirm time on the target's own clock, shown in the viewer on request.
- Version skew: the new parts run only when both ends support them.

In, PR 2 (1490 slice 2, macOS): pointer, keys and scroll from the viewer, a separate control grant (D-05), the banner saying "is controlling", computer use paused on the target, D-04's typing rules, held keys released at every end.

Out: WebRTC video, TURN, the iPhone viewer, Windows and Linux targets, clipboard, audio, files (all later slices of 1490 `plan.md`); several viewers on one machine; tabs or a grid of sessions inside one window.

## Acceptance Criteria

PR 1:

- [ ] AC-01: On the desktop app, "View screen" on a machine's card opens a native window for that machine on the viewer route, titled "Screen of <name>", or brings forward the one already open. The window is resizable, remembers its bounds per machine, and shows only the viewer: it follows no other route and opens no other page. Opening views of two different machines gives two windows, each with its own session.
- [ ] AC-02: The card also offers "View in this window". When a view of that machine is already open (in a window or in another app window), either choice brings that view forward instead of starting a second session. In a browser tab with no desktop bridge the button opens the in-page viewer as before.
- [ ] AC-03: The main process counts every view that shows a remote screen by a token per view, from start to end: a repeated start or end with the same token changes nothing, a renderer that reloads, crashes or closes drops its tokens, and a native viewer window counts from creation to close whatever its page says. Computer use on this machine refuses a whole-screen screenshot while the count is above zero. A test opens two views in one window, closes one, and computer use stays paused until the second closes.
- [ ] AC-04: The machine announces what it supports inside the sealed session, in the `live` state (`features`). The viewer sends a new record only to a machine that announced it, and the machine sends new frame fields only after it received a new record from that viewer. A test with the slice-1 state, frame-header and record rules frozen from 1.0.443 shows: a new machine and an old viewer run a full session with no new record and no new field the old viewer rejects; a new viewer and an old machine run a full session with no new record sent.
- [ ] AC-05: A viewer that knows the feature sends its picture area (`viewport`: integer device pixels, the window's size times its pixel ratio) when live and when the window is resized, at most 4 a second. The machine clamps the long edge between 640 px and the display's native size and 2,880 px, ignores extra viewport records beyond the rate, and ends the session on a malformed one.
- [ ] AC-06: While the picture changes the machine looks again after 100 ms; after 3 unchanged looks it goes back to 330 ms. One unconfirmed frame at a time stays. A look whose picture is unchanged is detected before JPEG encoding and costs no encode. A frame whose encoded size would pass 3.5 MB is re-encoded smaller (lower quality, then smaller size) and never sent over the record limit.
- [ ] AC-07: The viewer has a "Low bandwidth" choice (long edge at most 1,280 px, quality 50) and shows, on request, frames per second, kilobytes per frame and the machine's capture-to-confirm time for the last frame (measured on the machine's clock, sent in the next frame's header). Measurements over Connect from M5 to m1, before and after, are in `reports/picture-measurements.md`.
- [ ] AC-08: No access rule changes: the server's guards, the knock, the handshake, the transcript, the prompt, the grants, the banner and the store are byte-for-byte the same in PR 1, and `noAgentPath.test.ts` stays green.

PR 2:

- [ ] AC-09: A spike report (`reports/control-spike.md`) shows, under the installed signed app on a Mac, whether a signed helper inside the bundle posting `CGEvent`s runs under the app's Accessibility grant, and how secure input and a focused system prompt are detected. If it cannot work safely as planned, PR 2 stops and the report says what blocks it and the options.
- [ ] AC-10: Control is its own grant (D-05). From a live view the viewer's "Request control" asks the machine inside the sealed session, only when the machine announced `control`. The first time a device controls a machine, a person there sees "<device> wants to control this Mac" with Deny and "Always allow control"; Always allow needs system authentication run by the main process, under the same dialog rules as the view grant (1490 AC-02, AC-08). After that the device controls with nobody there until 30 days after the grant's last use. A view grant never allows control and a control grant never skips the view rules.
- [ ] AC-11: The new store opens a slice-1 store as it is: switch, view grants, machine key, devices that typed the code, cooldowns and audit all kept (fixture test from a 1.0.443 store). A store written by PR 2 that an older app opens reads as slice 1 did, or as reset with the reason shown, never as a broken session.
- [ ] AC-12: While a device controls the machine, the banner reads "<device> is controlling this screen", Stop ends control and the session within 1 second, and computer use on the machine is paused.
- [ ] AC-13: The machine forwards pointer moves, buttons, scroll and keys only while live and in control mode, mapped from frame pixels to the display. Typed text is not forwarded while secure input is on, while a system prompt (SecurityAgent, loginwindow) has focus, or while a browser is the front app (D-04, browser list in `docs/studio/screen-sharing.md`); clicks are not sent while a system prompt has focus. The viewer says why typing is off.
- [ ] AC-14: At every end of control (Stop, session end, viewer gone, helper exit, app quit) every held key, modifier and button is released. The helper runs only during a live control session, takes commands only over a pipe inherited from the app, and exits when the pipe closes or after 2 minutes of silence.
- [ ] AC-15: The viewer shows clearly whether it is viewing or controlling, and sends control records only to a machine that announced `control`. Old viewer against new machine and new viewer against old machine are tested as in AC-04.
- [ ] AC-16: Before merge, an adversarial security review on the project's reviewer order (not Claude) finds no open blocker or major.

## Approach

**Sessions and windows (PR 1).**

- `apps/desktop/src/screenShare/ScreenViewerWindows.ts`: a service on the pattern of `ArtifactAppWindows.ts` (same sandbox, context isolation and preload; route-locked navigation; new windows go to the browser). One window per environment id, window role `screen-viewer`, bounds kept in `screen-viewer-windows.json` in the state folder. It stays out of `DesktopWindow.ts` (1,716 lines).
- `apps/desktop/src/screenShare/screenViewing.logic.ts`: the per-token view count and the "open elsewhere" lookup; `ipc/methods/screenShare.ts` exposes `openViewer`, `beginView`, `endView` and feeds computer use's refusal.
- Web: `apps/web/src/routes/screen.$environmentId.tsx` with a bare layout in `__root.tsx`; `ViewScreenButton.tsx` gains the window path and "View in this window"; the viewer body moves to `ScreenViewerRun.tsx` so the dialog and the window share it.
- Contracts: the bridge methods in `packages/contracts/src/screenShare.ts`; one role literal in `ipc.ts`.

**Picture (PR 1).** Sealed records only, so the transcript and handshake do not change (AC-08). New: `live.features` (machine to viewer), `viewport` record 20 (viewer to machine), optional frame-header `stats`. Capture asks `desktopCapturer` for the clamped size, hashes the raw bitmap before encoding, and picks quality and size from the viewer's choice. The viewer's "Low bandwidth" and stats are in `ScreenViewer.tsx`. A hidden "classic" choice (slice-1 numbers) exists only to measure before and after on one build.

**Control (PR 2).** As 1490 `plan.md` sections 5 and 7, with these choices: control is an upgrade inside a live view session (a new handshake mode would get `unsupported_mode` from an old machine), gated by the `control` feature; the helper is Swift, signed with the app and placed in `Contents/Helpers`; the grant sits beside view grants in the same sealed store with its own last-used time.

Risks: the measurement depends on m1 installing the release; until then M5 can only run new viewer against old machine. A fresh scratch-data app holds another device key that m1 has not approved, so it proves windows and refusal states only. The Accessibility grant may not cover a separately signed helper; the spike decides.

## Decisions

### Asked
- D-01 to D-04: 1490, unchanged.
- D-05 Control grant → separate grant; first time "Always allow control" with Touch ID at the machine, then unattended until 30 days after last use; a view grant never implies control (owner, November 28, 2026).

### Defaulted (change any before sw-do)
- D-06 One native window per machine on the desktop app; "View in this window" kept; no tabs or grid in this increment.
- D-07 Capture capped at 2,880 px long edge; "Low bandwidth" 1,280 px at quality 50.
- D-08 Faster looks at 100 ms while changing, 330 ms when still.
- D-09 Control starts inside a view session ("Request control"), not as a new handshake mode.

### Open
- Whether m1 installs the PR 1 release soon enough to measure after; the report says which runs were old against new.

## Review

- Reviewer: gemini (gemini-4-neon) on Copilot Enterprise, effort high; fallback GPT-6.2 Sol. Never Grok (memory `decision_adversarial_reviewer_model`).
- Depth: deep for PR 2 (security); standard for PR 1.
- Required: yes.

## Tasks

### T-01 Research and spec
- AC: AC-04 | Files: .specweave/increments/1519-remote-desktop-several-sessions-in-their-own-windows-better-picture-then-control/reports/research-remote-desktop-products.md | Test: manual: the report cites a source for each product row

### T-02 View count and computer-use pause
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenViewing.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenViewing.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/methods/screenShare.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/ipc/channels.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/preload.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/screenShare.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/screenShare/screenViewing.logic.test.ts

### T-03 Viewer windows
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenViewerWindows.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenViewerWindows.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenViewerWindows.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/main.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/ipc.ts, repositories/anton-abyzov/specwithcode/apps/web/src/routes/screen.$environmentId.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/__root.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/lib/projectWindow.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/ViewScreenButton.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/ScreenViewerRun.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/screenShare/screenViewerWindows.logic.test.ts

### T-04 Picture: features, viewport, faster looks, stats
- AC: AC-04, AC-05, AC-06, AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/screenShare.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenShareSession.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenSharePicture.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenSharePicture.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/ScreenCapture.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenCapture.logic.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/screenShareSkew.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/screenViewer.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/screenViewer.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/screenShareClient.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/ScreenViewer.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/screenShare/ apps/web/src/components/screenShare/

### T-05 Docs, measurements and release proof for PR 1
- AC: AC-01, AC-07 | Files: repositories/anton-abyzov/specwithcode/docs/studio/screen-sharing.md, .specweave/increments/1519-remote-desktop-several-sessions-in-their-own-windows-better-picture-then-control/reports/picture-measurements.md, .specweave/increments/1519-remote-desktop-several-sessions-in-their-own-windows-better-picture-then-control/reports/pr1-proof.md | Test: manual: screenshot of two viewer windows on M5 in the report

### T-06 Control spike
- AC: AC-09 | Files: .specweave/increments/1519-remote-desktop-several-sessions-in-their-own-windows-better-picture-then-control/reports/control-spike.md | Test: manual: the report holds the measured result under the installed signed app

### T-07 Control: grant, helper, banner, input rules
- AC: AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/desktop/src/screenShare/, repositories/anton-abyzov/specwithcode/apps/web/src/components/screenShare/, repositories/anton-abyzov/specwithcode/packages/contracts/src/screenShare.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/desktop/src/screenShare/ apps/web/src/components/screenShare/
