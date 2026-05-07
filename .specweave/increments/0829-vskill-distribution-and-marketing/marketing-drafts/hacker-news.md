# Hacker News — Show HN draft

**Status:** DRAFT — do not post until launch date is set.
**Recommended posting window:** Tuesday or Wednesday, 8:30-10:00 AM ET.

---

## Title (under 80 chars)

Show HN: vSkill — Local skill marketplace for AI agents (Tauri + Node sidecar)

## Alternate titles to A/B with maker

- Show HN: vSkill Desktop — native skill manager for Claude/GPT/Llama agents
- Show HN: A local-first registry for AI agent skills (open source, MIT)

## URL

https://verified-skill.com/desktop

## First comment (post immediately after submission)

Hi HN — Anton here, sole maintainer of vSkill.

Quick context on what this is and how it's built:

**Problem.** AI agent ecosystems (Claude Code, Cursor, Copilot, Codex, Windsurf, ~50 others) all
use a similar concept of "skills" — small Markdown + glue-code units that teach an agent how to
do a thing. Today these get copy-pasted between repos. There's no install command, no version
control, no eval to confirm a skill actually improves the model, and Snyk's recent ToxicSkills
report found 36.82% have security flaws. We wanted a real package manager for skills, with a
three-tier verification pipeline (52 static patterns → blocklist → LLM-intent scan) and an
A/B eval harness so you can prove a skill makes the model better.

**Architecture.** This is the bit I most want feedback on. The desktop app is Tauri 2 (Rust
shell + WebView for UI) plus a 114 MB Node.js Single-Executable-Application sidecar that
hosts the eval-server runtime. Cold launch is ~1.5 s on Apple Silicon. Updates are signed
with minisign and the Tauri Updater plugin polls a Cloudflare R2 manifest daily. The same
eval-server runs identically in `npx vskill studio` (browser mode) and inside the desktop
shell — one runtime, two transports, no code duplication.

Why Tauri + Node sidecar instead of Electron? We wanted a native menu bar tray, real Cmd/Ctrl-K
hotkey palette, and a binary under 100 MB before sidecar — Electron lost on all three. Why
SEA instead of pkg or nexe? Single-file output that codesigns cleanly on macOS notarization.

**Open source, MIT.** All source on GitHub (anton-abyzov/vskill). Self-host the registry with a
single Cloudflare Worker and a SQLite/D1 backing store. No telemetry by default. Skills work
across 53 agent platforms.

What's still rough:

- Linux signing — using GPG-signed AppImages for now; Snap and Flatpak are TODO
- Windows SmartScreen will warn until we get enough installs to clear reputation (Authenticode signed but new cert)
- Auto-update on Linux only works for AppImage today; .deb / .rpm are manual

Roadmap, source, and the desktop downloads are all at verified-skill.com — would love feedback
on the Tauri+Node SEA pattern, the three-tier scan model, and the A/B eval harness.

## Posting checklist

- [ ] Maker comment ready (above) and copied to clipboard
- [ ] Submit during 8:30-10:00 AM ET window
- [ ] Reply to first 5 comments within first hour (signal of engaged maker)
- [ ] Do NOT astroturf upvotes from accounts you control — HN auto-flags vote rings
- [ ] If a moderator emails about title shenanigans, reply within 30 minutes
