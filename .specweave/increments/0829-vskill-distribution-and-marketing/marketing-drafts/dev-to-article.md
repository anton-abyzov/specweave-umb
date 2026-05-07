# dev.to deep-dive article draft

**Status:** DRAFT — publish day-of launch or +1 day after HN.
**Series:** "Building vSkill" (this is post 1 of 3).

---

## Title

Building a Tauri + Node SEA hybrid: lessons from vSkill Desktop

## Tags

#tauri #nodejs #rust #electron #ai

## Cover image

`/og/devto-cover.png` — 1000x420 PNG showing a stylized Tauri shell hosting a Node sidecar.

## Body (~1500 words)

Two months ago I shipped vSkill Desktop — a native Mac/Windows/Linux app for browsing,
installing, and running AI agent skills. Cold launch is 1.5 s on Apple Silicon. The bundle
is 114 MB. Auto-update works on every platform. And the entire eval runtime is the same
Node.js code that ships in `npx vskill studio`, packaged as a Single-Executable-Application
inside the Tauri shell.

This post is about why I picked that architecture, what almost broke, and what I'd do
differently.

### The constraint stack

vSkill needs three things from its desktop layer:

1. **A real menu bar tray.** Skill installs are short — most users open the app, search,
   click install, close it. A persistent tray icon plus a global Cmd/Ctrl-K palette makes
   that flow feel native.
2. **A bundled Node.js runtime.** The eval-server (the bit that A/B benchmarks skills across
   Claude, GPT, Llama, Gemini) is 4 KLOC of TypeScript. Rewriting it in Rust would have
   doubled the project timeline. Shipping it as a sidecar lets the same code run in browser
   mode (`npx vskill studio`) and in the desktop shell.
3. **Sub-100 MB binary.** Electron starts at ~150 MB. We have a hard "respect the user's
   disk" goal.

These constraints rule out Electron. They also rule out a pure-Rust shell that re-implements
eval-server.

### Why Tauri 2

Tauri 2 ships a Rust shell that uses the system WebView (WebKit on macOS, WebView2 on
Windows, WebKitGTK on Linux). The base shell is ~3 MB. The shell exposes a JS bridge so
the WebView can call signed Rust commands. That's almost everything I want: native UI
chrome (menu bar, tray, hotkeys) in Rust, app UI in HTML/CSS/JS, and a security model
where every Rust call is allowlisted.

What I had to add: a way to ship eval-server.

### The Node SEA sidecar

Node 20 added Single-Executable-Application support — you can take a Node program plus
its dependencies and bake them into a single, codesignable binary. It's not as fast to
build as `pkg` (more on that below) but the output works with macOS notarization out of
the box, which `pkg` does not.

The pattern is:

1. Build eval-server.ts → CommonJS → run `node --experimental-sea-config` → get a 114 MB
   `eval-server` binary that contains the Node runtime + all deps + the JS itself.
2. Codesign it (separately from the Tauri shell binary on macOS — both must be signed).
3. Ship it inside the Tauri bundle as a sidecar.
4. On launch, the Tauri Rust process spawns the sidecar on a deterministic per-project port.
5. The WebView talks to the sidecar over localhost HTTP + SSE — same protocol as
   `npx vskill studio` browser mode.

This means the runtime is shared between the two transports. A bug fix to eval-server lands
in both modes simultaneously. There's no "desktop branch" of the eval logic to drift.

### The bits that almost broke

**Apple notarization quirks.** The sidecar binary has its own embedded JIT (V8). Apple's
notary service flags JIT writable+executable pages by default. Solution: ship the JIT
entitlement (`com.apple.security.cs.allow-jit`) on the sidecar binary and only on the
sidecar, not on the parent Tauri shell.

**Windows SmartScreen.** New Authenticode certs trigger SmartScreen warnings until the
binary builds reputation. We documented "click More info → Run anyway" prominently on
the /desktop landing page. Reputation clears around install #100 or 7 days, whichever
comes first.

**Linux AppImage FUSE requirement.** The AppImage runtime needs `libfuse2`. Modern Ubuntu
ships `libfuse3` and breaks the binary unless `libfuse2` is also installed. We documented
this on the /desktop Linux card and ship a `--appimage-extract-and-run` fallback.

**Cmd-K hotkey on macOS.** Tauri 2's global shortcut plugin races with the WebView's own
keyboard handling. The fix was to register the hotkey in Rust and dispatch a message into
the WebView via the bridge, rather than letting the WebView handle it. Single source of
truth for the keystroke.

### What I'd do differently

If I were starting today:

- **Skip pkg entirely**, go straight to SEA. The notarization story is just better.
- **Sign the sidecar with the same cert as the shell** but with separate entitlements.
  Two-cert setups create headaches that aren't worth saving the cert money.
- **Ship a healthcheck endpoint earlier.** When the sidecar dies, the shell needs to know
  fast. We added `/healthz` in week 6; should have been week 1.
- **Plan for self-update on Linux .deb / .rpm from day one.** AppImage auto-update via the
  Tauri Updater plugin works, but .deb users today have to `apt upgrade` manually. That's
  a long-term papercut.

### Try it

vSkill Desktop is open source (MIT) at github.com/anton-abyzov/vskill. Downloads for Mac,
Windows, and Linux at verified-skill.com/desktop. The eval-server architecture is in
src/server/ if you want to see how the sidecar is structured.

Next post in this series: how the three-tier security scan works, and why I added an
LLM-intent classifier as the third tier.

---

## Cross-post checklist

- [ ] Canonical URL set to verified-skill.com/blog/building-tauri-node-sea-vskill
- [ ] Cross-post to Hashnode 24 hours later (with canonical pointing back to dev.to)
- [ ] Tweet thread (twitter-thread.md) links here
- [ ] Reply to comments for first 24 hours
