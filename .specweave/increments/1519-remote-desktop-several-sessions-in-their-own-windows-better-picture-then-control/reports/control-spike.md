# Control spike (AC-09)

November 28, 2026, on M5 (macOS 27.2.1), under the installed signed app (`/Applications/SpecWithCode.app`, identifier `com.specweave.studio`, team `NMCB2JZ7QG`) with its Accessibility grant on. Scratch sources and binaries: `~/.specwithcode/m4/scratch/2026-11-28-1519-control-spike/` (`probe.swift`, `disclaim.c`, `helper.swift`, `focus.swift`).

## Result

Control can work as planned. A helper started by the app runs under the app's Accessibility grant, and secure input and system prompts can be detected from inside the helper at the moment it posts.

## 1. Does a helper run under the app's grant?

The probe process descends from the app (`SpecWithCode` → `claude` → `zsh` → probe). It is a separately built Swift binary with an ad-hoc signature, not the app's signature.

| Run | `AXIsProcessTrusted()` | `CGPreflightPostEventAccess()` |
|---|---|---|
| Started normally, 3 runs | true | true |
| Same binary, started with `responsibility_spawnattrs_setdisclaim` (its own responsible process) | false | false |

So macOS charges the grant to the responsible process, the app, not to the helper's own signature. The disclaimed run is the control: the same binary with no app behind it has no grant. The shipped helper is signed with the app's identity anyway (as `resources/voice` is today), and the app must start it normally, never disclaimed.

This matches what the app already does: computer use posts `CGEvent`s from a child `osascript` (`apps/desktop/src/computerUse/MacComputerUse.ts`), and that works under the same grant.

## 2. Speed of a long-lived helper

`helper.swift` reads one command per line on stdin and posts a mouse move to where the pointer already is (nothing on screen changes). 300 commands from a parent over a pipe:

| | p50 | p95 | max |
|---|---|---|---|
| Pipe write to reply | 19 µs | 45 µs | 118 ms (first command) |
| `CGEvent.post` alone | 4 µs | 12 µs | 44 ms (first command) |

Startup is about 50 ms. The helper exited 0 when its stdin closed. Input cost is negligible next to the network round trip; a process per action (the computer-use path, `osascript`) costs 50 ms or more and is not used.

## 3. Detecting secure input and system prompts

`focus.swift` reads, at one instant: `IsSecureEventInputEnabled()`, the front app (`NSWorkspace.shared.frontmostApplication`), and the on-screen windows owned by `SecurityAgent`, `loginwindow`, `coreautha` (from `CGWindowListCopyWindowInfo`, owner names only; no window titles are read).

| Moment | Front app | Secure input | System windows on screen |
|---|---|---|---|
| Baseline (M5 was locked) | `com.apple.loginwindow` | false | `loginwindow` at layers 2001, 2004 (lock shield) |
| An administrator prompt up (`osascript ... with administrator privileges`, closed after 3 s) | `com.apple.loginwindow` | false | the same plus `SecurityAgent` at layer 1000 |
| After it closed | `com.apple.loginwindow` | false | lock shield only |

What follows for the rules (AC-13):

- A `SecurityAgent` or `coreautha` window on screen means a system prompt: no clicks and no typing. The window list catches it even when the prompt is not the front app.
- `loginwindow` in front, or its shield windows on screen, means locked or switching user: no input at all. The session already shows the "locked" placard then.
- `IsSecureEventInputEnabled()` is the system's own flag for a focused password field in any app: no typing while it is on. The probe saw it false only because M5 was locked; a focused password field turning it on is documented behaviour, not measured here.
- The browser rule (D-04) uses the front app's bundle identifier against a fixed list.
- Every check runs in the helper right before each key or button post, not in a cached state sent ahead, so a prompt that appears between two events still stops the second one. Pointer moves reuse a reading at most 100 ms old.
- One full check (secure input, front app, window list) costs 0.26 ms p50 on M5, small next to the 33 ms the viewer batches input over.

## Not measured here

- Secure input turning on (needs a focused password field on an unlocked screen; M5 was locked).
- Which process owns the Touch ID sheet window (`coreautha` is assumed from its process name; the sheet was never shown on an unlocked screen).
- Whether `loginwindow` owns on-screen windows on an unlocked Mac. If it does at layer 2000 or above, the "locked" rule would block control; the helper reports the reason, so a false block would be visible, not silent.
- Posting real clicks and keys on another person's screen: done only in the live proof after release, with the owner's approval at m1.
