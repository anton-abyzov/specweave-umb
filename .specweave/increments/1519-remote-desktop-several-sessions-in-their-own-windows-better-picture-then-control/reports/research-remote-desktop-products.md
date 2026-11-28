# Remote desktop products compared, for SpecWithCode slices 2 to 7

Research date: November 28, 2026. Scope: macOS Screen Sharing, Chrome Remote Desktop (CRD), Parsec, RustDesk, and a do-it-yourself macOS stack (ScreenCaptureKit plus CGEvent), with the Windows and Linux platform APIs and Cloudflare TURN.

Sourcing rules used here:

- Every factual line carries the URL that was read. "Unverified" means no primary source was found.
- Parsec's help center (`support.parsec.app`) returned HTTP 403 to every fetch. Lines marked "unverified: search summary only" rest on a search engine's summary of that page and are paraphrased, not quoted. Table cells marked (u) rest on those lines.
- Numbers in the "away from home" section are computed estimates. Each one shows its arithmetic.

## 1. Summary table

| | macOS Screen Sharing | Chrome Remote Desktop | Parsec | RustDesk | DIY (SCK + CGEvent) |
|---|---|---|---|---|---|
| Transport | RFB/VNC with Apple security types; High Performance over UDP 5900-5902 | WebRTC (ICE, STUN/TURN) | Own UDP protocol "BUD", DTLS 1.2 | Own protocol over TCP/UDP, hole punching, hbbr relay | Your choice |
| Codecs | Apple-registered RFB encodings (undocumented); High Performance codec unverified | VP8, VP9 (incl. 4:4:4), AV1; H.264 only with a GPU and not on macOS builds | H.264; H.265 and 4:4:4 options (u) | VP8, VP9, AV1, H.264, H.265 (hardware) | VideoToolbox H.264/HEVC, or stills |
| Frame rate | Standard adapts; High Performance 30 or 60 fps | 30 fps target constant | "smooth 60 FPS", up to 4K60; 240 fps lab test | 30 default, 5-120 custom, adaptive | `minimumFrameInterval` |
| Several hosts at once | Connections window lists saved hosts; window model unverified | One browser tab per session | No; separate app instances (u) | Tabs by default, optional separate windows | Your choice |
| Host-side consent | Ask permission, or allowed users/password | Share dialog, banner, 30-minute recheck, PIN for unattended | Host approves guests, per-guest input permissions (u) | Accept window with permission toggles; password, click, or both | Your choice; macOS shows capture indicator |
| Elevated prompts | Unverified | Windows service, SAS injection, input desktop switch | Windows SYSTEM service (u) | Windows service or elevation via portable service, SendSAS | macOS login window and SecurityAgent: unverified, likely blocked |
| Hosts | macOS | Windows, macOS, Linux (X11; Wayland in progress) | Windows, macOS; no Linux host (u) | Windows, macOS, Linux X11 and Wayland | macOS only |

## 2. macOS Screen Sharing (built in)

**Transport and codec.**

- The RFB registry assigns security types 31-35 and encodings 1000-1002, 1011 and 1100-1105 to "Apple Inc.". It documents none of Apple's messages. https://raw.githubusercontent.com/rfbproto/rfbproto/master/rfbproto.rst
- The codec used in High Performance mode is unverified; Apple does not name it.

**High Performance mode (macOS 14+).** All quotes are from https://support.apple.com/guide/mac-help/mchl1883115d/mac :

- "available on Mac computers with Apple silicon and macOS Sonoma 14 or later".
- "requires high network bandwidth (75 megabits per second for a single 4K display) and consistent low network latency"; "A wired network connection is recommended."
- "Both Mac computers must be able to communicate with each other over UDP ports 5900, 5901, and 5902."
- Features: "stereo audio, HDR video reference mode, 4:4:4 chroma subsampling, high frame rates (30 or 60 fps), and low latency". Standard mode will "Adapt resolution and frame rate to network conditions."
- One or two virtual displays, up to "4K (3840 x 2160 pixels or 1920 x 1080 HiDPI)".
- "Only one High Performance screen sharing session can be active on each Mac at a time."
- When you sign in as the logged-in user, the host's hardware displays "are blanked".

**Several sessions and windows.**

- Saved hosts appear in "All Connections in the Connections window sidebar". https://support.apple.com/guide/mac-help/mchl89584923/mac
- You can choose which display of a multi-display host to view, and active sessions are ended from Window > Connections. https://support.apple.com/guide/mac-help/mh14066
- That each remote Mac opens in its own window: unverified (Apple's pages do not say).

**Consent and indicator.**

- Host settings: "Allow access for" (all users or only these users), "Anyone may request permission to control screen", and "VNC viewers may control screen with password". Screen Sharing and Remote Management cannot both be on. https://support.apple.com/guide/mac-help/mh11848/mac
- Apple Account connections can be limited by "Allow screen sharing requests from". https://support.apple.com/guide/mac-help/mh14066
- The on-screen indicator at the shared Mac and the wording of its accept dialog: unverified. The Remote Desktop client icon has an "Administered" state while an admin observes or controls. https://support.apple.com/guide/remote-desktop/apd03e60538/mac

**Secure input and the login window.** Unverified; no Apple document found.

## 3. Chrome Remote Desktop

**Transport and codec.**

- WebRTC transport lives in `remoting/protocol/webrtc_*`. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/
- The encoder factory advertises VP8, VP9 Profile 0/1 and AV1 Profile 0/1. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/webrtc_video_encoder_factory.h
- H.264 is added only if a GPU check passes. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/webrtc_video_encoder_factory.cc
- The GPU H.264 encoder builds only on Windows, Linux and ChromeOS, so a macOS host has no H.264. https://chromium.googlesource.com/chromium/src/+/main/remoting/codec/BUILD.gn
- VP9 uses `VP9E_CONTENT_SCREEN` and switches to profile 1 (I444) for lossless color. https://chromium.googlesource.com/chromium/src/+/main/remoting/codec/webrtc_video_encoder_vpx.cc
- The ICE config carries STUN/TURN servers on 3478 and 5349, each with a `maxRateKbps`. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/ice_config.cc
- A source comment notes that Google's TURN relay "limits the connection speed by dropping" packets. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/webrtc_transport.cc
- Which codec is picked by default today: unverified.

**Latency and adaptation.**

- `kTargetFrameRate = 30`. https://chromium.googlesource.com/chromium/src/+/main/remoting/base/constants.h
- The encoder wrapper clamps to 15-120 Hz with QP 10-50 and takes its bitrate from WebRTC `SetRates()`. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/webrtc_video_encoder_wrapper.cc
- `kMaxBitrateBps = 1e8` (100 Mbit/s), with periodic bandwidth probing. https://chromium.googlesource.com/chromium/src/+/main/remoting/protocol/webrtc_transport.cc
- VPX starts at a 500 kbit/s "conservative default" until an estimate exists. https://chromium.googlesource.com/chromium/src/+/main/remoting/codec/webrtc_video_encoder_vpx.cc
- No published latency figure was found.

**Sessions.**

- Google's help says to "close your tab to stop your session", so there is one browser tab per session. https://support.google.com/chrome/answer/1649523?hl=en An official statement that several hosts can run in parallel tabs: unverified.

**Consent.** Host strings, all from https://chromium.googlesource.com/chromium/src/+/main/remoting/resources/remoting_strings.grd :

- "Would you like to share this computer for another user to see and control?"
- The banner "Your desktop is currently shared with $1." with "Stop Sharing".
- The recurring prompt "Do you want to continue sharing?". Google's help says the host must confirm "every 30 minutes", and a support code works "one time". https://support.google.com/chrome/answer/1649523?hl=en
- Unattended access is PIN-based (same strings file).
- Curtain mode is policy `RemoteAccessHostRequireCurtain`. It needs Windows Pro or higher and is not supported on macOS Big Sur or later. https://support.google.com/chrome/a/answer/2799701?hl=en

**Input and elevation.**

- On Windows the host runs as the `chromoting` service with a SYSTEM daemon that follows the console session. https://chromium.googlesource.com/chromium/src/+/main/remoting/host/win/host_service.cc
- It turns Ctrl+Alt+Del into a Secure Attention Sequence and calls `SwitchToInputDesktop()` before each injected event. https://chromium.googlesource.com/chromium/src/+/main/remoting/host/win/session_input_injector.cc
- On macOS it needs Accessibility (for CGEventPost) and Screen Recording. https://chromium.googlesource.com/chromium/src/+/main/remoting/host/mac/permission_utils.mm

**Linux.**

- The host is a Debian package that starts `/etc/X11/Xsession`. https://support.google.com/chrome/answer/1649523?hl=en
- The source has PipeWire and portal remote-desktop sessions. https://chromium.googlesource.com/chromium/src/+/main/remoting/host/linux/
- A CRD engineer wrote on February 12, 2024 that GNOME is their "first priority to support for Wayland". https://discourse.gnome.org/t/persistent-remote-desktop-access-api/19415
- Whether Wayland hosting is generally available as of November 2026: unverified.

## 4. Parsec

**Transport and codec.**

- Parsec uses its own peer-to-peer protocol, BUD, with a "97% NAT traversal success rate". https://parsec.app/technology
- BUD is "based off of UDP", uses "a highly tuned and custom congestion control algorithm", and is "encrypted with DTLS 1.2". https://parsec.app/blog/a-networking-protocol-built-for-the-lowest-latency-interactive-game-streaming-1fd5a03a6007
- Capture is zero-copy on the GPU, and the codec is H.264. https://parsec.app/technology
- H.265 is a client toggle; 4:4:4 needs H.265 plus a prefer-4:4:4 setting (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381785123860-Improve-Stream-Quality-and-Color-Accuracy
- A "High-performance relay" is an Enterprise feature. https://unity.com/products/parsec

**Latency and adaptation.**

- Parsec says it adds "only 7 milliseconds of latency" on a LAN Ethernet test, targets "smooth 60 FPS", and adjusts bitrate dynamically. https://parsec.app/technology
- Its product page says "up to 4k at 60 frames per second". https://unity.com/products/parsec
- A 240 fps LAN test measured "roughly 4–8 milliseconds" of total pipeline latency (1 Gbit/s Ethernet, 100 Mbit/s bandwidth setting, H.264). https://parsec.app/blog/parsec-game-streaming-total-latency-at-240-frames-per-second-c0818cc0daa5
- Priority order is "latency, frame rates, and then video quality". https://parsec.app/blog/a-networking-protocol-built-for-the-lowest-latency-interactive-game-streaming-1fd5a03a6007
- `encoder_bitrate` defaults to 10 Mbit/s and is a maximum; the page warns that going above 50 adds latency (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381776828820-Setting-The-Maximum-Bitrate-Of-The-Stream

**Sessions.**

- There is no multi-host window. The documented workaround is one `parsecd.exe` per host, tiled by hand (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32361386926868-Connecting-to-multiple-computers-at-once
- Up to three host monitors open as extra windows (Add Screens) (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381733729044-Multiple-Monitors-and-Virtual-Displays , https://unity.com/products/parsec

**Consent.**

- The host approves guests (also with Ctrl+F1). Guests start with controller-only permissions, and the host grants keyboard and mouse per guest (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/4422936497165-Hosting-and-Permissions
- Privacy Mode blanks the physical displays and locks the host after the last guest leaves (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/4421515077773-Privacy-Mode
- An on-host banner while a guest is connected: unverified.

**Input and elevation.**

- The Windows Per Computer install runs as SYSTEM and reaches the login screen (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381368159124-Install-Parsec-App-on-Windows
- The service is what reaches UAC screens (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381334155412-Why-Is-Parsec-Running-in-the-Background-on-Startup
- A macOS host needs Screen Recording; Accessibility only for system shortcuts (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381394408596-Parsec-App-for-macOS

**Platforms.** Hosts run on Windows and macOS 10.15+. https://parsec.app/blog/macos-hosting-preview-available-now Linux is client-only; the page says Linux hosting is not supported (unverified: search summary only, page returned 403). https://support.parsec.app/hc/en-us/articles/32381552552340-Install-Parsec-App-on-Linux

## 5. RustDesk (source read at master `104ef2a8`)

**Transport.**

- The rendezvous server hbbs uses TCP 21115-21116, UDP 21116 and TCP 21118 (WebSocket); the relay hbbr uses TCP 21117 and 21119. Clients try hole punching first and fall back to the relay: "In the majority of cases, hole punching is successful." https://rustdesk.com/docs/en/self-host/
- `NatType` distinguishes ASYMMETRIC from SYMMETRIC, and `force_relay` exists. https://github.com/rustdesk/hbb_common/blob/main/protos/rendezvous.proto
- Frames are sealed with NaCl secretbox, keyed by a `box_` exchange. https://github.com/rustdesk/hbb_common/blob/main/src/tcp.rs

**Codecs and quality control.**

- Supported codecs are VP8, VP9, AV1, H264 and H265. https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/common/mod.rs
- The auto order is H265 > H264 > AV1/VP9, with VP8 on hosts with 4 GB of RAM or less. https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/common/codec.rs
- `custom-fps` runs from 5 to 120 (default 30), and `enable-abr` defaults to Y. https://rustdesk.com/docs/en/self-host/client-configuration/advanced-settings/
- `video_qos.rs` probes delay with a `TestDelay` round trip. https://github.com/rustdesk/rustdesk/blob/master/src/server/video_qos.rs
  - A reply 150 ms or more above the baseline counts as bad. Three bad replies cut fps; one second of excess halves it.
  - ABR lowers the bitrate before it lowers fps. The bitrate ratio is re-evaluated every 3 s, with a floor near 1 Mbit/s.
  - With several viewers, the host runs at the slowest viewer's fps.
- This is the closest published design to SpecWithCode's ack-based backpressure. It measures round trips per viewer and degrades fps.

**Capture.**

- Windows: DXGI `DuplicateOutput`/`AcquireNextFrame`. A source comment lists dirty and move rects as future work. https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/dxgi/mod.rs
- macOS: `CGDisplayStream`, not ScreenCaptureKit. https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/quartz/capturer.rs
- Linux X11: `xcb_shm_get_image`. https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/x11/capturer.rs
- Linux Wayland: ScreenCast portal plus PipeWire, storing a portal `restore_token`. https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/wayland/README.md , https://github.com/rustdesk/rustdesk/blob/master/libs/scrap/src/wayland/pipewire.rs

**Input.**

- Windows: `SendInput`. https://github.com/rustdesk/rustdesk/blob/master/libs/enigo/src/win/win_impl.rs
- macOS: `CGEventPost`. https://github.com/rustdesk/rustdesk/blob/master/libs/enigo/src/macos/macos_impl.rs
- X11: libxdo/XTest. https://github.com/rustdesk/rustdesk/blob/master/libs/enigo/src/linux/xdo.rs
- Wayland with the root server: uinput. https://github.com/rustdesk/rustdesk/blob/master/src/server/uinput.rs
- Wayland otherwise: RemoteDesktop portal `NotifyPointerMotionAbsolute` and `NotifyKeyboardKeycode`. https://github.com/rustdesk/rustdesk/blob/master/src/server/rdp_input.rs
- Where RustDesk calls `ConnectToEIS`: unverified.

**Elevation.**

- Windows uses `SendSAS(FALSE)`, `elevate` and `run_as_system`. https://github.com/rustdesk/rustdesk/blob/master/src/platform/windows.rs
- The portable (not installed) build cannot send the screen while a UAC prompt is open, and someone at the host must accept the elevation. https://rustdesk.com/docs/en/client/windows/windows-portable-elevation/
- Linux: "Login screen using Wayland is not supported yet." https://rustdesk.com/docs/en/client/linux/

**Sessions and windows.**

- `enable-open-new-connections-in-tabs` (default Y) puts each connection in a tab; otherwise it opens in a window. `displays-as-individual-windows` defaults to N. https://rustdesk.com/docs/en/self-host/client-configuration/advanced-settings/
- The protocol has `SwitchDisplay`, `CaptureDisplays` and `ToggleVirtualDisplay`. https://github.com/rustdesk/rustdesk/blob/master/libs/base/protos/message.proto

**Consent.**

- The host's connection manager window has Accept, Accept and Elevate, and Disconnect. Per-session toggles cover keyboard/mouse, clipboard, audio, files, recording and block input. https://github.com/rustdesk/rustdesk/blob/master/flutter/lib/desktop/pages/server_page.dart
- `approve-mode` is password, click, or both (the default). A permanent password gives unattended access. https://rustdesk.com/docs/en/self-host/client-configuration/advanced-settings/

## 6. Do-it-yourself macOS stack (ScreenCaptureKit + VideoToolbox + CGEvent)

**Capture.**

- `SCStream` (macOS 12.3+) captures screen content described by an `SCContentFilter`, with output set by an `SCStreamConfiguration`. https://developer.apple.com/tutorials/data/documentation/screencapturekit/scstream.json
- `SCStreamConfiguration.minimumFrameInterval` defaults to 0, meaning "the system uses the maximum supported frame rate"; set 1/60 for 60 fps (macOS 12.3+). https://developer.apple.com/tutorials/data/documentation/screencapturekit/scstreamconfiguration/minimumframeinterval.json
- `SCContentSharingPicker` (macOS 14+): Apple says "Avoid creating your own sharing picker." https://developer.apple.com/tutorials/data/documentation/screencapturekit/sccontentsharingpicker.json
- WWDC23 says every SCStream appears in a system video menu bar item with a live preview. https://developer.apple.com/videos/play/wwdc2023/10136/
- `com.apple.developer.persistent-content-capture` (macOS 14.4+, by request) "enables VNC apps to view and record the screen". https://developer.apple.com/tutorials/data/documentation/bundleresources/entitlements/com.apple.developer.persistent-content-capture.json
- macOS 15 re-asks for Screen Recording monthly (press report, not Apple). https://9to5mac.com/2024/08/14/macos-sequoia-screen-recording-prompt-monthly/
- That the purple menu bar icon means screen capture: unverified by Apple. https://www.macbartender.com/Bartender5/ScreenCaptureMenuBarItem/

**Encode.**

- `kVTVideoEncoderSpecification_EnableLowLatencyRateControl` (macOS 11.3+) gives no B-frames and no lookahead. https://developer.apple.com/tutorials/data/documentation/videotoolbox/kvtvideoencoderspecification_enablelowlatencyratecontrol.json
- WWDC21 says it is H.264 only, always hardware, and "can reduce the delay of up to 100 milliseconds for a 720p 30fps video". https://developer.apple.com/videos/play/wwdc2021/10158/
- A low-latency HEVC mode: unverified.

**Input.**

- `CGEventPost` (macOS 10.4+). https://developer.apple.com/tutorials/data/documentation/coregraphics/cgevent/post(tap:).json
- `CGEventCreateMouseEvent` (macOS 10.4+) takes the cursor position "in global coordinates". https://developer.apple.com/tutorials/data/documentation/coregraphics/cgevent/init(mouseeventsource:mousetype:mousecursorposition:mousebutton:).json `CGEventCreateKeyboardEvent` (macOS 10.4+) takes virtual key codes, and "All keystrokes needed to generate a character must be entered, including modifier keys." https://developer.apple.com/tutorials/data/documentation/coregraphics/cgevent/init(keyboardeventsource:virtualkey:keydown:).json
- `CGEventCreateScrollWheelEvent2` (macOS 10.13+). https://developer.apple.com/tutorials/data/documentation/coregraphics/cgevent/init(scrollwheelevent2source:units:wheelcount:wheel1:wheel2:wheel3:).json
- `CGPreflightPostEventAccess` and `CGRequestPostEventAccess` (macOS 10.15+). https://developer.apple.com/tutorials/data/documentation/coregraphics/cgrequestposteventaccess().json
- Apple DTS says "Both PostEvent and Accessibility map to Accessibility" in System Settings. PostEvent works inside the App Sandbox; the Accessibility APIs do not. https://developer.apple.com/forums/thread/820594

**Secure input (TN2150).**

- Secure input stops keyboard events from reaching event taps and other "intercept" processes "whether that process is in the foreground or background". `NSSecureTextField` turns it on automatically, and "You can check whether secure event input is enabled by calling `IsSecureEventInputEnabled`." https://developer.apple.com/library/archive/technotes/tn2150/_index.html
- TN2150 says nothing about posted events. Whether a CGEvent typed into a password field arrives: unverified, so test it.
- Login window: developers report that posted keyboard events fail before login while mouse events work (not Apple). https://developer.apple.com/forums/thread/724740
- Security prompts: 2018 research found WindowServer refuses synthetic events on some security prompts ("Sender is prohibited from synthesizing events"). https://objective-see.org/blog/blog_0x36.html
- Treat SecurityAgent and password dialogs as not controllable until tested.

## 7. Windows and Linux platform APIs

**Windows capture.**

- Desktop Duplication returns dirty rects and move rects; apply the moves first. https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/desktop-dup-api
- `AcquireNextFrame` returns `DXGI_ERROR_ACCESS_LOST` on a desktop switch or mode change, and the duplication must be recreated. https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_2/nf-dxgi1_2-idxgioutputduplication-acquirenextframe
- On the secure desktop, `DuplicateOutput` returns `E_ACCESSDENIED`: "only an application that runs at LOCAL_SYSTEM can access the secure desktop". There is a limit of 4 concurrent duplications per session. https://learn.microsoft.com/en-us/windows/win32/api/dxgi1_2/nf-dxgi1_2-idxgioutput1-duplicateoutput
- UAC prompts show on the secure desktop by default. https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/how-it-works
- Windows.Graphics.Capture (Windows 10 1803+) uses a system picker and draws a yellow border. Turning the border off needs a user prompt and a capability (build 20348+). https://learn.microsoft.com/en-us/windows/apps/develop/media-authoring-processing/screen-capture , https://learn.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturesession.isborderrequired

**Windows input.**

- `SendInput` "is subject to UIPI": a process can inject only into equal or lower integrity, and a block is silent. https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
- UIAccess needs a signature and an install in Program Files, and still cannot reach system-level UI. https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-securityoverview
- `SendSAS` (Ctrl+Alt+Del) needs a service or uiAccess, plus Group Policy permission. https://learn.microsoft.com/en-us/windows/win32/api/sas/nf-sas-sendsas

**Linux.**

- The ScreenCast portal hands out PipeWire streams (`OpenPipeWireRemote`). https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.ScreenCast.html
  - `persist_mode` 2 ("until revoked") and a single-use `restore_token` arrived in version 4.
- The RemoteDesktop portal has `NotifyPointerMotionAbsolute` and `NotifyKeyboardKeycode`. https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.RemoteDesktop.html
  - `ConnectToEIS` (version 2) returns a libei socket. After that, input must go only over EIS.
  - Version 2 also adds persistence.
- libei is emulated input for Wayland; the compositor-side libeis can tell emulated input from physical input. https://libinput.pages.freedesktop.org/libei/
- X11 fallback: XTEST `FakeInput`. https://xorg.freedesktop.org/archive/X11R7.7/doc/xextproto/xtest.html
- Wayland does not let applications snoop on, or inject, other programs' input (LWN, March 12, 2014). https://lwn.net/Articles/589147/
- A freedesktop page stating the capture restriction: unverified.
- gnome-remote-desktop is an example of the portal-era design: RDP/VNC backends, PipeWire for pixels, libei for input, and headless and remote-login modes. https://github.com/GNOME/gnome-remote-desktop/blob/master/README.md

## 8. Quality and latency away from home

Scenario: the owner is in Boston and the target Mac is at home behind NAT. Where "home" is changes the round-trip time (RTT), so the tables use three RTTs.

**RTT scenarios (estimates).** Cloudflare's rule of thumb is about 1 ms of RTT per 100 km of fiber (light in fiber travels about 200,000 km/s). https://blog.cloudflare.com/fastest-internet/

Scenarios: 20 ms (same metro or region); 80 ms (cross-country: Boston to the US West Coast is about 4,300 km great-circle, an unverified distance, so the fiber floor is 4,300 / 100 = 43 ms and real routes add more); 150 ms (intercontinental). All three are estimates.

Cloudflare says about 95% of the Internet-connected population is within roughly 50 ms of a Cloudflare location. https://blog.cloudflare.com/webrtc-turn-using-anycast The extra RTT the tunnel adds over a direct path is unverified, so these scenarios treat the tunnel path RTT as the end-to-end RTT.

### 8a. Still JPEG frames over WebSocket through Cloudflare Tunnel (today)

Model from the brief: one unconfirmed frame at a time, so

fps = min(capture rate, 1 / (RTT + transfer time)), where transfer time = frame bits / home uplink.

Frame bits use 1 KB = 1,000 bytes: 150 KB = 1.2 Mbit and 600 KB = 4.8 Mbit.

Transfer times (estimates):

| Frame | 10 Mbit/s uplink | 40 Mbit/s uplink |
|---|---|---|
| 150 KB | 1.2 / 10 = 120 ms | 1.2 / 40 = 30 ms |
| 600 KB | 4.8 / 10 = 480 ms | 4.8 / 40 = 120 ms |

Ack-bound frame rate, 1 / (RTT + transfer), before the 3 fps capture cap (estimates):

| Frame, uplink | RTT 20 ms | RTT 80 ms | RTT 150 ms |
|---|---|---|---|
| 150 KB, 40 Mbit/s | 1/0.050 = 20.0 | 1/0.110 = 9.1 | 1/0.180 = 5.6 |
| 150 KB, 10 Mbit/s | 1/0.140 = 7.1 | 1/0.200 = 5.0 | 1/0.270 = 3.7 |
| 600 KB, 40 Mbit/s | 1/0.140 = 7.1 | 1/0.200 = 5.0 | 1/0.270 = 3.7 |
| 600 KB, 10 Mbit/s | 1/0.500 = 2.0 | 1/0.560 = 1.8 | 1/0.630 = 1.6 |

What the tables mean (estimates):

- At today's 3 fps capture rate, the ack bound binds only on large frames over a slow uplink: 1.6 to 2.0 fps for 600 KB at 10 Mbit/s. Every other cell is capped at 3 fps.
- If control (slice 2) raises capture to 30 fps, the ack bound decides the frame rate: 9.1 fps for 150 KB at 40 Mbit/s and 80 ms, and 3.7 fps at 150 ms.
- One frame in flight wastes the link. The bandwidth-delay product at 40 Mbit/s and 80 ms is 40 × 0.080 = 3.2 Mbit = 400 KB, so one 150 KB frame fills 150 / 400 = 37.5% of it. Allowing 2 to 3 frames in flight would lift the bound roughly in proportion, until the uplink saturates (estimate).
- Bandwidth while the screen keeps changing at 3 fps:
  - 150 KB × 3 = 450 KB/s = 3.6 Mbit/s
  - 600 KB × 3 = 1.8 MB/s = 14.4 Mbit/s, more than a 10 Mbit/s uplink, so the ack bound throttles it as shown above.
- Reaction time for control: a click goes one way (RTT/2), the next capture waits up to 1/3 s (333 ms, about 167 ms on average), then the transfer, then RTT/2 back. For 150 KB at 10 Mbit/s and RTT 80 ms: 40 + 167 + 120 + 40 ≈ 367 ms on average, before encode time (estimate). That is usable for clicking buttons and poor for typing feedback or dragging.
- WebSocket runs over TCP, so one lost packet stalls every frame queued behind it (head-of-line blocking; standard TCP behavior, no source fetched here, so unverified). cloudflared uses QUIC to the edge when UDP works, else HTTP/2. https://developers.cloudflare.com/tunnel/advanced/run-parameters/
- Cloudflare closes idle WebSockets after an undocumented time and advises a heartbeat; code releases also drop WebSockets. https://developers.cloudflare.com/network/websockets/

### 8b. WebRTC peer to peer vs relayed through TURN

- **Peer to peer.**
  - ICE prefers host, then server-reflexive, then relay candidates (type preferences 126/100/0). https://datatracker.ietf.org/doc/html/rfc8445
  - Hole punching "generally fail[s]" when both sides have address- or port-dependent NAT mapping. Use TURN "only when a direct communication path cannot be found". https://datatracker.ietf.org/doc/html/rfc8656
  - Parsec reports 97% NAT traversal for its own protocol. https://parsec.app/technology
  - Over UDP, latency should be about the one-way path plus encode, decode and jitter buffer (estimate, unverified). Parsec's LAN figure of "only 7 milliseconds" added is the best published case. https://parsec.app/technology
  - There is no per-frame ack, so frame rate is set by the encoder and congestion control (GCC, with transport-wide feedback), not by RTT. https://datatracker.ietf.org/doc/html/draft-ietf-rmcat-gcc-02
- **Relayed through Cloudflare Realtime TURN.**
  - Anycast `turn.cloudflare.com` "connects to the Cloudflare location closest to them". Ports: UDP 3478/443, TCP 3478/80, TLS 5349/443. https://developers.cloudflare.com/realtime/turn/
  - Price: "$0.05 per GB of egress", and "The first 1,000 GB each month is free", shared with the SFU. https://developers.cloudflare.com/realtime/pricing/
  - Billing counts data "sent from the Cloudflare edge to the TURN client"; ingress is free, and STUN is free and unlimited. https://developers.cloudflare.com/realtime/turn/faq/
  - Per-allocation limits are ">50-100 Mbps" and ">5-10 kpps"; past them, packets drop. https://developers.cloudflare.com/realtime/turn/
  - Relays are IPv4 only, and credentials last up to 48 hours. https://developers.cloudflare.com/realtime/turn/faq/
  - The extra latency of the relay over a direct path is unverified. With anycast picking a nearby location, it is the detour through that location.
- **Free-tier hours (estimates, counting video bytes once at viewer egress).**

| Video bitrate | GB per hour | Hours inside 1,000 GB |
|---|---|---|
| 5 Mbit/s | 5 / 8 × 3,600 / 1,000 = 2.25 | 1,000 / 2.25 ≈ 444 |
| 10 Mbit/s | 10 / 8 × 3,600 / 1,000 = 4.5 | 1,000 / 4.5 ≈ 222 |
| 20 Mbit/s | 20 / 8 × 3,600 / 1,000 = 9.0 | 1,000 / 9.0 ≈ 111 |

  If both peers relay, egress to the target also counts (input plus RTCP, small). Whether relay-to-relay traffic inside Cloudflare is billed again: unverified.

- Apple's High Performance figure of 75 Mbit/s for one 4K display sits inside the 50-100 Mbit/s per-allocation limit, at its edge. 4K60 over Cloudflare TURN is not a safe target; 1080p to 1440p at 30 fps under 20 Mbit/s fits with headroom (estimate).

## 9. What this means for SpecWithCode

- **Window model.** Give each remote machine its own native window, titled with the machine name. Keep a single "Machines" or Connections list as the launcher, the same pattern as Apple's Connections sidebar.
  - Inside a window, a display picker switches displays. "Open display in new window" is opt-in, like RustDesk's `displays-as-individual-windows`, default off.
  - Avoid tabs as the default. Tabs (RustDesk, CRD) hide parallel sessions, which defeats watching two Macs at once.
  - Run backpressure per window. RustDesk runs at the slowest viewer's fps; each SpecWithCode window should have its own capture stream and its own frame-in-flight budget.
- **Slice 2 (control), input path.** Post CGEvents from the signed Swift helper. Use `CGPreflightPostEventAccess`/`CGRequestPostEventAccess`; in System Settings this appears as Accessibility, so the onboarding should say "Accessibility".
  - Send input as small ordered messages on the existing sealed WebSocket. Input is tiny, and the RTT is the floor anyway.
  - Map coordinates per display in points, not JPEG pixels.
  - When the 3 fps still pipeline is controlled, raise the capture rate and allow 2 to 3 frames in flight. One frame in flight caps a 150 KB frame at 80 ms RTT near 9 fps (estimate, section 8a).
- **Slice 2, secure input and system prompts.** Do not promise control of password fields, the login window or SecurityAgent prompts.
  - Apple documents only that secure input blocks taps. Developers report login-window keyboard injection failing, and WindowServer has refused synthetic events on security prompts.
  - Test `IsSecureEventInputEnabled()` on the target and show the viewer a plain state ("A password field is active on <Mac>; typing may not reach it"), rather than dropping keys silently.
  - Show a host-side banner while a session is active, with Stop, modeled on CRD's "Your desktop is currently shared with $1 / Stop Sharing". Owner-only unattended access is fine because both ends are the owner's machines, but the banner stays.
- **Slice 3 (WebRTC video).** Use Electron's `setDisplayMediaRequestHandler` plus `getDisplayMedia` (https://www.electronjs.org/docs/latest/api/desktop-capturer), and signal over the existing sealed WebSocket.
  - Set `contentHint = "detail"` (or `"text"`) and `degradationPreference = "maintain-resolution"` so text stays sharp and frame rate gives way first. https://www.w3.org/TR/mst-content-hint/ , https://developer.mozilla.org/en-US/docs/Web/API/RTCRtpSender/setParameters
  - Cap `maxBitrate` so a session fits the TURN budget. 10 Mbit/s gives about 222 free hours a month (estimate).
  - Which codecs Electron's WebRTC offers on macOS is unverified. CRD's own host encoder has no H.264 on macOS, but that is CRD's code, not Electron's. Check `RTCRtpSender.getCapabilities('video')` on each target before choosing.
  - Keep the JPEG still path as the fallback when ICE fails and TURN is unavailable.
- **TURN.** Mint Cloudflare TURN credentials server-side with short TTLs (48 hours at most) and keep the TURN key on the server, as Cloudflare advises. https://developers.cloudflare.com/realtime/turn/generate-credentials/ Use relay only when ICE fails, since relayed egress is billed and STUN is free. Keep per-session bitrate well under the 50-100 Mbit/s per-allocation limit, and track monthly GB against the 1,000 GB free allowance.
- **Slice 6 (Windows).**
  - Capture: Desktop Duplication, using dirty and move rects (RustDesk does not yet). Handle `DXGI_ERROR_ACCESS_LOST` on desktop switches. Prefer it over Windows.Graphics.Capture, which draws a yellow border and needs a picker or a prompt to remove it.
  - Input: `SendInput`. UIPI silently blocks injection into elevated windows, and UAC runs on the secure desktop, which only LOCAL_SYSTEM can capture. CRD and RustDesk solve this with a SYSTEM service plus SAS injection; Parsec uses a SYSTEM service (unverified, search summary).
  - Ship user-level first with an explicit "Elevated prompt open on <PC>; control paused" state. Treat the SYSTEM service as its own security-reviewed step.
- **Slice 7 (Linux).**
  - On Wayland, use the xdg-desktop-portal ScreenCast plus RemoteDesktop session, with PipeWire for pixels and `ConnectToEIS` (libei) for input. Use `persist_mode` 2 with the single-use `restore_token` so reconnects do not re-prompt; store each new token.
  - Fall back to XTest and XShm on X11.
  - State up front that the Wayland login screen is out of scope. RustDesk does not support it either; gnome-remote-desktop's headless remote-login mode is the GNOME-specific route.
- **Do not chase 4K60 first.** Apple asks 75 Mbit/s for one 4K display and recommends a wired connection. For an owner away from home, readable text at 1080p to 1440p, 30 fps, under 20 Mbit/s is the realistic target (estimate). RustDesk-style adaptation that cuts bitrate before fps, per window, is a proven pattern to copy.
