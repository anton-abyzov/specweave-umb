---
title: "M5 OBS audio, NDI tiles and CalDigit check"
thread: "thread:delegated-task:command%3Amcp%3Afa43f133-3057-4a60-a8c7-bcc96542ad30%3Adelegate-task%3Af577262e-6c1e-46d3-ade2-85a0d9195c64"
threadTitle: "OBS audio and wired network"
savedAt: "2026-11-19T23:01:36.421Z"
---

# M5 OBS audio, NDI tiles and CalDigit check

November 19, 2026, M5 (`Anton M5MAX PROLED`, macOS 27.2.1, OBS 33.0.1, obs-websocket 5.7.6).

## Incident: OBS crashed at 5:58:44 PM

My third read-only obs-websocket batch (mute, volume, monitor type, tracks, settings, property list items, profile parameters) crashed OBS: `EXC_BAD_ACCESS` in `_platform_strlen` called from `obs-websocket` (`~/Library/Logs/DiagnosticReports/OBS-2026-11-19-175844.ips`). Before the crash: stream, recording and virtual camera were all off. Program scene was `All 4 Screens`. OBS has not been relaunched.

## Game and mic audio (from live state before the crash and the saved collection)

| Source | What it captures | State | Verdict |
|---|---|---|---|
| `Mic/Aux` | system default input, currently Studio Display Microphone (AirPods connect switched it to AirPods at 24 kHz earlier today) | unmuted, monitor off, all tracks | signal shown in screenshot; pin the device |
| `Video sound` | application capture of `com.google.Chrome` | muted | wrong app: the game is `RemotePlay.app` (`com.playstation.RemotePlay`) |
| `M5 Screen` | display capture of the screen showing Remote Play | muted | keep muted, otherwise it duplicates game audio |
| `Background Music` | `bg-mix-m5.mp3` | hidden in scenes, monitor and output | not part of this |

Output mode Advanced, stream on Track 1 (`AdvOut TrackIndex=1`), every source on all tracks (mixers 255). Monitoring device: default (Studio Display Speakers).

Planned change once OBS is running: `Video sound` application to `com.playstation.RemotePlay`, unmute it, monitoring Off (Anton already hears Remote Play directly, so monitoring would double it); `M5 Screen` stays muted; `Mic/Aux` pinned to Studio Display Microphone so AirPods never drop it to 24 kHz call audio. Echo: Remote Play plays through the Studio Display speakers next to the Studio Display mic, so the mic also picks up the game. Use AirPods for listening (output only) or keep speaker volume low.

## All 4 Screens tiles

| Tile | Source | NDI name | State |
|---|---|---|---|
| top left | `LG display` | `ANTONS-MACBOOK-M4MAX.LOCAL (M4 Dell)` | 0x0, no frames |
| top right | `M5 Screen` | local display | working |
| bottom left | `NDI M1 Screen` | `MACBOOKPRO.LAN (M1 Screen)` | 0x0, no frames |
| bottom right | `NDI Ministorm Screen` (Linux) | `MINISFORUM (Ministorm Screen)` | working |

mDNS browse of `_ndi._tcp` lists only `MINISFORUM (Ministorm Screen)`. M4 resolves at 192.168.40.201 but advertises no NDI sender. `macbookpro.local` does not resolve. OBS side is configured correctly; the senders on M4 and M1 are not running. M5 has no grant to run work on M4 (`needs_reverse_grant`).

## Ethernet and CalDigit

M5 today: default route `en10`, ASIX AX88179A USB adapter (`0b95:1790`), 1000baseT full duplex, plugged directly into a Mac USB-C port (no hub). Thunderbolt tree has only the Studio Display. No CalDigit is attached to M5.

M5 remembers `en9` "USB 10/100/1G/2.5G LAN": Realtek RTL8156 (`0bda:8156`) behind a USB 3 hub, and a USB "Mac" link (`anri3`) behind a hub at the same port. That fits a dock attached to M5 earlier with a USB-only connection. Model not provable from M5.

CalDigit official TS5 page (https://www.caldigit.com/thunderbolt-5-dock-ts5/): 2.5GbE, compatible with Thunderbolt 5/4/3, USB4 and USB-C hosts; full features need an 80 Gb/s Thunderbolt 5 or USB4 v2 host connection. The dock's Ethernet serves only the computer on its host port. A computer plugged into a dock's downstream USB port gets no dock Ethernet; between two Macs it only makes a Mac-to-Mac USB link.

## Update, 6:20 PM

CalDigit on M5 is an Element 5 Hub (Thunderbolt tree: `CalDigit, Inc.` `Element 5 Hub`, USB4 v2, 80 Gb/s on receptacle 1). Official spec (https://www.caldigit.com/element-5-hub-support/): 1 host port, 3 Thunderbolt 5, 3 USB-A, 2 USB-C, no Ethernet. Internet stays on `en10` (ASIX AX88179A, 1000baseT), now plugged into the hub's USB tree, so its traffic goes through the CalDigit: 3/3 pings to 1.1.1.1, HTTPS 200 from apple.com via 192.168.40.47. The 2.5 GbE port `en9` (Realtek `USB 10/100/1G/2.5G LAN`) sits behind the Dell U2725QE's USB hub and has no link (`status: inactive`, `media: none`).

OBS audio applied: `Video sound` captures `com.playstation.RemotePlay`, unmuted, monitoring none, volume 0 dB, tracks 1-6. `M5 Screen` stays muted. `Mic/Aux` is the Shure MV7+, chosen by Anton in OBS Settings at 6:15:27 PM. Stream uses Track 1. Meters at 6:19 PM: both silent (PS5 on its home menu, Anton not speaking).

All 4 Screens: `NDI M1 Screen` hidden, `NDI Ministorm Screen` moved to bottom left, `NDI M4 Built-in` added bottom right under the camera. Linux frames are byte-identical 5 s apart with a clock of November 18, 3:41 AM: the Minisforum sender is frozen.

## Update, 6:20 PM: frozen Linux tile and blank M4 tiles

**Linux is a stalled sender, not a stuck receiver.** `NDI Ministorm Screen` is an `ndi_source` (DistroAV) reading `MINISFORUM (Ministorm Screen)`, `ndi_behavior` 0. OBS on M5 holds TCP `192.168.40.47:52911 -> 192.168.40.158:5961` and receives about 34 Mbit/s of NDI video on UDP 5960, yet three screenshots 10 s apart hash the same (`c8370f86…`) and the on-screen clock reads November 18, 3:41 AM. Frames keep arriving; they are the same picture. That matches the known linux-mini failure: a GNOME lock ends the PipeWire portal screencast and DistroAV keeps sending the last frame.

**Linux fix (on linux-mini, as anton):** unlock the GNOME session, then `systemctl --user restart obs-ndi-sender.service`. The saved restore token brings capture back with no dialog. Fresh-frame test: move a window or wait a minute on linux-mini and watch the top-bar clock in the M5 tile advance; I can confirm with two differing screenshot hashes.

**Privacy:** the frozen Linux frame shows the "A new device wants to use minisforum" pairing card with an account email (redacted) and a code field, plus a "SpecWithCode 1.0.349 is available" notice. Keep the tile hidden until a fresh frame without that card is showing.

**M4 advertises no NDI sender.** `dns-sd -B _ndi._tcp` at 6:19 PM lists only `MINISFORUM (Ministorm Screen)` and M5's own `M5 Screen`. M5 has no grant on M4, so I cannot start it.

**M4 fix (on M4):** open OBS, right-click the `NDI Out` scene and choose Fullscreen Projector or Windowed Projector, and leave it open. Its two Dedicated NDI Output filters send `ANTONS-MACBOOK-M4MAX.LOCAL (M4 Built-in)` and `(M4 Dell)` only while that projector is open. If macOS asks for Local Network or Screen Recording for OBS, allow it. Fresh-frame test: the M4 tiles on M5 show the M4 clock moving.

## Update, 6:22 PM: M4 senders started

With the new M5-to-M4 grant, worker thread `M4 NDI senders for M5 OBS` on M4 launched OBS (PID 16570) and opened a windowed projector of `NDI Out` with `OpenSourceProjector`. No macOS prompts. `dns-sd` now lists `ANTONS-MACBOOK-M4MAX.LOCAL (M4 Built-in)` and `(M4 Dell)`.

On M5: `NDI M4 Built-in` is live (two frames 3 s apart differ, clock in the tile reads Thu Nov 19 6:22 PM). `LG display` (`M4 Dell`) is connected (tally on program) but receives no frame: `GetSourceScreenshot` returns "Failed to render screenshot." even after re-applying its source name. Likely cause: the Dell U2725QE is cabled to M5 now (M5's `en9` sits in its hub), so M4's Dell capture has no display to send.

Linux unchanged (hash `c8370f86…`). linux-mini shows `grant_revoked` for M4, and M5 has no route there.

## Update, 6:40 PM: All 4 Screens re-laid out

Canvas 4096x2304, four 2048x1152 quadrants, all `SCALE_INNER`:

| Quadrant | Item | State |
|---|---|---|
| top left 0,0 | `M5 Screen` | live (hash changed over 70 s) |
| top right 2048,0 | `NDI M4 Built-in` | live (hash changed over 70 s) |
| bottom left 0,1152 | `NDI Ministorm Screen` | static since November 18, 3:41 AM (sender stalled) |
| bottom right 2048,1152 | `Camera Quadrant` (new) | live, crop 96 px left and right, centred, about 102 px black strips each side |

`Camera Quadrant` is a new `macos-avcapture` input on the Studio Display Camera with a copy of the original Color Correction filter and no portrait mask, because the shared `Video Capture Device` source carries an image mask and crop used by other scenes. The original item is hidden in this scene with its old transform restored; both camera inputs run at the same time (both hashed live). Hidden, not deleted: `LG display` (M4 Dell, no frames), `NDI M1 Screen`, `Video Capture Device`, `BG Music`. Audio unchanged: `Video sound` and `Mic/Aux` unmuted. Not streaming, not recording. Strip pixels sampled at (0,0,0).

M4 camera framing was not copied: M4 dispatch failed ("m4: The operation could not be completed."). M1: `NDI M1 Screen` in scene `M1 + iPhone16` is configured for `MACBOOKPRO.LAN (M1 Screen)`, but no M1 sender is advertised, `macbookpro.local` does not resolve and M1 is not in the machine list.

Evidence is a 64x36 render only (`~/.specwithcode/m4/scratch/2026-11-19-obs-audio/all4-layout-redacted.png`). Earlier full-resolution frames that showed a pairing dialog and account email were deleted, and the email is redacted above.

## Preflight, 6:45 PM: YouTube, X, Twitch (non-public)

Nothing was transmitted. Keys were read only as lengths. OBS not streaming or recording, PID 25871 throughout.

| Destination | OBS routing | Ingest | Verdict |
|---|---|---|---|
| YouTube | Main output, `rtmp_custom`, `rtmps://a.rtmps.youtube.com:443/live2`, key set (24 chars, YouTube format) | TLS to `a.rtmps.youtube.com:443` ok; stream not sent | No-go until event checked |
| X | obs-multi-rtmp target `X @aabyzov`, `rtmps://a.live.x.com/x`, key set (12 chars), enabled, sync-start with main stream, shares main encoders | TLS to `a.live.x.com:443` ok; stream not sent | No-go until Producer checked |
| Twitch | No target anywhere (main service is YouTube; multi-rtmp has only X) | TLS to `live.twitch.tv:443` ok | No-go: not configured |

Shared output: Advanced, Apple H.264 1920x1080 at 30 fps, 9000 kbps, keyframe 2 s, stream audio Track 1 (AAC 192 kbps). `Mic/Aux` (Shure MV7+, present, 0 dB, unmuted) and `Video sound` (`com.playstation.RemotePlay`, running) both on Track 1. Meters at 6:43 PM: both exactly 0 for 4 s, so audience audio is unverified, not proven broken. Advanced Scene Switcher has no stream-start macro. Starting the stream on YouTube also starts X.

The `[YouTube]` block in `basic.ini` (title "North & Central European League", Privacy public, AutoStart true) belongs to the OBS YouTube integration and is not used by the custom RTMP service; what goes live on YouTube depends on the event bound to the key in YouTube Studio, which was not checked (no headless signed-in session).

Not tested on purpose: any ingest send, because with YouTube auto-start or an X Producer broadcast armed it could go public.

Program safety: current program `All 4 Screens` includes the frozen Linux tile, the same stale frame that showed a pairing dialog and account email, plus a live M4 desktop. Not safe to broadcast until the Linux tile is hidden.

## 7:05 PM: destinations checked in Obsidian and the signed-in Chrome (read only)

Obsidian (`~/Documents/personal-docs`) has YouTube RTMPS notes in `003 Resources/Technical Knowledge/Tools-Applications/OBS local setup, plugins tricks.md` and a bitrate note (Twitch 6000, YouTube 9000). It holds no Twitch or X stream keys.

YouTube Studio: a stream-now event is waiting on the default stream key, titled "Fable 5.2 Takes Over My $7,500 MacBook Pro, Linux PC and iPhone", privacy Private, Low-latency, DVR on. No scheduled streams. Going live now would be private until the privacy is changed.

X: studio.x.com/producer redirects to a sign-in page in this Chrome; not touched. The OBS target "X @aabyzov" is configured, but the Producer broadcast is unverified.

Twitch: signed in as aabyzov; the primary stream key exists (not shown or copied), Low latency. OBS still has no Twitch output.

No key was revealed, copied or changed. No stream started.

## November 20, 12:55 AM: noon GTA 6 stream prepared

YouTube: scheduled Public stream `MZLPv4uP8nQ`, "I Let AI Make Every Choice in My First Hour of GTA 6 🔴 LIVE", November 20, 2026 at 12:00 PM ET, Gaming / Grand Theft Auto VI, thumbnail `kie-B-1280x720.jpg`, Default stream key (the key OBS uses). Auto-start and Auto-stop are still off: the extension's toggle clicks did not save, and Anton was using the screen, so no mouse takeover.

Twitch: title matches, category Grand Theft Auto VI. No schedule entry: Twitch only offers weekly recurring slots.

OBS: added a "Starting Soon" scene (first in the list) with `ai-controls-starting-soon-1920x1080.png` to `basic/scenes/Untitled.json` while OBS was closed; backup `Untitled.json.pre-starting-soon`. Verified by a background launch (scene renders full-frame, profile GTA6 Twitch, not streaming or recording), then quit OBS again, as Anton had left it.

linux-mini: `obs-ndi-sender.service` restarted and PipeWire is streaming; screen lock and blanking were already off. Not yet seen moving in M5's OBS.

Vault: the keys note now names the active `GTA6_Twitch` profile files; logged in `wiki/log.md`.

Announcement drafts (not posted): `.specweave/reports/threads/2026-11-19-gta6-live/announcement-noon-drafts.md`.

## November 20, 11:21 AM: YouTube Auto-start and Auto-stop on

The earlier clicks had opened a hidden "Enable Auto-start" confirmation dialog. Confirmed it, then turned on Auto-stop. After a reload, event `MZLPv4uP8nQ` shows Auto-start on, Auto-stop on, DVR on, scheduled for November 20, 2026, 12:00 PM. The title now reads "I Let AI Run My Life in GTA 6 (Chat Can Overrule It) 🔴 LIVE", changed by another thread.

## iPhone camera in OBS (November 20, 12:58 PM ET)
- Root cause: at 12:13:08 ContinuityCaptureAgent logged "skipping because Continuity Camera is disabled on the host side", so the Mac never searches for the phone ("No valid device to onboard").
- Also: rapportd was denied Local Network access (Don't Allow at 12:13); the rule sits in /Library/Preferences/com.apple.networkextension.plist, which macOS blocks even admin from editing. Backup: /Library/Preferences/com.apple.networkextension.plist.bak-20261120 (identical to original).
- No defaults key, profile or firewall rule disables it. Next: restart M5, check iPhone Continuity Camera switch, then check the camera list.
- Fallback: OBS source "Video Capture Device Full" (iPhoneA screen over USB) with the iPhone Camera app open in landscape, cropped.
