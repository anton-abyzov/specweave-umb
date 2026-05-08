---
increment: 0832-studio-process-lifecycle
title: >-
  Skill Studio process lifecycle — detect existing instances +
  kill/reuse/replace actions
type: feature
priority: P1
status: completed
created: 2026-05-07T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
projects:
  - vskill
parent: 0830-skill-studio-settings-and-updates
---

# Feature: Skill Studio process lifecycle — detect existing instances + kill/reuse/replace actions

## Overview

Skill Studio runs as a Tauri desktop app **and** via `npx vskill@latest studio` (a Node.js process that spawns the same studio runtime in a browser tab). Today these two paths are unaware of each other — if the user runs both, they end up with two studio instances on different ports, two browser tabs, two separate ops journals, and no way to reconcile them from inside the desktop app.

This increment makes the **desktop app the primary surface** and gives the user clear actions to manage any pre-existing `npx`-launched instance: switch to it, stop it and replace, or run alongside.

## Problem statement

1. **Silent duplication** — launching the desktop app while `npx vskill studio` is running starts a second sidecar on a different port. Nothing tells the user.
2. **No "switch to existing"** — if the user already has the npx-launched browser tab open, the desktop app should be able to bring that tab forward instead of opening a fresh one.
3. **No "kill the old one"** — there's no in-app action to terminate a pre-existing npx process. User has to fall back to Activity Monitor / `pkill`.
4. **No status of running instances** — power users running multiple projects with multiple `npx vskill studio --port X` workers have no visibility from the desktop app.
5. **CLI lacks `--replace` flag** — `npx vskill studio` blindly starts a new instance even if one is already bound.

## Goals (v1)

1. **On desktop launch**: detect running studio processes and their bound ports.
2. **First-launch modal** when one is detected, with three actions: **Use that instance**, **Stop it and use desktop app**, **Run alongside**.
3. **Window menu → Studio Instances** — submenu listing every detected instance with **Switch** / **Stop** actions.
4. **CLI flag `vskill studio --replace`** — kill any existing studio process before starting.
5. **CLI flag `vskill studio --status`** — print one-line summary of detected studio processes without starting one.
6. **Clean shutdown propagation** — when the desktop's main window closes, all child sidecars are torn down (already handled by 0828).

## Out of scope (v1)

- Cross-machine instance discovery (mDNS broadcast)
- Process management for non-studio vskill workers (eval-server, sidecar of a different project)
- Persistent registry of "known instances" across reboots
- Privileged kill for processes owned by a different macOS user
- Windows / Linux equivalents of macOS-specific bits — detection logic IS cross-platform; modal ships everywhere

## Inherited givens

- Tauri 2 sidecar spawn at `src-tauri/src/sidecar.rs` (port 0 → auto-pick)
- `tauri-plugin-shell` available for safe `kill` + child-process spawn
- 0830 menu plumbing (`src-tauri/src/menu.rs`) supports adding submenus
- `vskill studio` CLI lives at `repositories/anton-abyzov/vskill/src/cli/commands/studio.ts`

## Personas

### P-1: Daily power user
Has the desktop app installed AND uses `npx vskill studio` from terminal for projects outside their default workspace. Expects desktop launch to coexist gracefully or offer a clear merge.

### P-2: Curious first-time user
Saw a tutorial mentioning `npx vskill studio`, ran it, then later installed the desktop app. Confused why two browser tabs are open with the same UI.

## User stories

---

### US-001: Detect running studio processes on desktop launch (P0)
**Project**: vskill

**As a** Skill Studio user
**I want** the desktop app to know if studio is already running before it spawns another sidecar
**So that** I don't end up with two parallel instances by accident

**Acceptance Criteria**:
- [x] **AC-US1-01**: At desktop boot, before `sidecar::spawn_sidecar` runs, a new `process_discovery::scan()` enumerates running processes matching `vskill-server`, `node.*vskill.*studio`, or `npm exec vskill.*studio`.
- [x] **AC-US1-02**: For each match, scanner extracts: `pid`, `port` (from `--port N` arg or `~/.vskill/runtime/` lock file), `started_at`, `source: "tauri" | "npx-cli" | "node-direct"`, `cmdline` (truncated to 120 chars).
- [x] **AC-US1-03**: If exactly one external (`source != "tauri"`) instance found, desktop shows the lifecycle modal (US-002) before completing boot.
- [x] **AC-US1-04**: Zero external instances → desktop boots normally (existing 0828 path).
- [x] **AC-US1-05**: Scanner has hard 500ms timeout — never blocks cold-launch.

---

### US-002: Lifecycle modal with three explicit actions (P0)
**Project**: vskill

**As a** user with `npx vskill studio` already running
**I want** the desktop app to ask me what to do, not silently spawn another instance
**So that** I can pick the behavior I actually want

**Acceptance Criteria**:
- [x] **AC-US2-01**: Modal title: "Skill Studio is already running". Body shows detected instance: `port {N} · {source} · started {relative time}`.
- [x] **AC-US2-02**: Three primary actions, keyboard-accessible: **Use that instance**, **Stop it and use desktop app**, **Run alongside**. Default focus on **Use that instance**.
- [x] **AC-US2-03**: **Cancel** secondary action exits desktop cleanly (don't leave half-booted Tauri window).
- [x] **AC-US2-04**: "Use that instance" → desktop window navigates to `http://127.0.0.1:{detected.port}/` and skips spawning its own sidecar.
- [x] **AC-US2-05**: "Stop it and use desktop app" → SIGTERM to `detected.pid`, 3s grace, escalate to SIGKILL, then proceed with normal sidecar spawn.
- [x] **AC-US2-06**: "Run alongside" → spawn own sidecar on fresh port; both instances coexist.
- [x] **AC-US2-07**: "Don't ask again — always X" checkbox persists choice to `~/.vskill/settings.json::studio.lifecycleDefault` (`"ask" | "use-existing" | "stop-and-replace" | "run-alongside"`). Honored on subsequent boots until reset in Preferences → Advanced.

---

### US-003: Window menu → Studio Instances submenu (P1)
**Project**: vskill

**As a** power user running multiple studio sessions
**I want** to see every running studio instance from inside the desktop app
**So that** I can switch between them or kill stale ones without leaving the UI

**Acceptance Criteria**:
- [x] **AC-US3-01**: Native menu bar gains `Window → Studio Instances` submenu, populated dynamically when opened.
- [x] **AC-US3-02**: Each row: `port {N} · {source-shorthand} · {pid}`. Tauri-spawned instances marked `(this app)` and disabled.
- [x] **AC-US3-03**: External rows have **Switch** (load instance URL) and **Stop** (kill with confirmation) actions.
- [x] **AC-US3-04**: Submenu refreshes within 1s of being opened (not on a poll).
- [x] **AC-US3-05**: Empty state shows disabled `No other instances` placeholder.

---

### US-004: CLI `vskill studio --replace` and `--status` flags (P1)
**Project**: vskill

**As a** terminal user
**I want** explicit control of running instances from the CLI
**So that** I'm not forced to use the desktop UI for every action

**Acceptance Criteria**:
- [x] **AC-US4-01**: `vskill studio --replace` runs scan, kills every external instance (SIGTERM 3s → SIGKILL), then starts fresh studio.
- [x] **AC-US4-02**: `vskill studio --status` runs scan, prints one line per instance (`port {N}\tsource={src}\tpid={pid}\tstarted={iso8601}`), exits 0. No output + exit 0 if none found.
- [x] **AC-US4-03**: Both flags documented in `vskill studio --help`.
- [x] **AC-US4-04**: When CLI starts, writes `~/.vskill/runtime/studio-{port}.lock` with PID + start timestamp + cmdline. Rust scanner reads this directory as a fast path.
- [x] **AC-US4-05**: Lock files atomically removed on graceful shutdown (CLI: SIGTERM/SIGINT handler; desktop: existing `RunEvent::Exit`). Stale (>1d, no matching PID) pruned by scanner.

---

### US-005: "Don't ask again" preference + reset (P1)
**Project**: vskill

**As a** user who already picked a default lifecycle action
**I want** to change my mind from Preferences without editing JSON
**So that** the modal can come back if I change workflow

**Acceptance Criteria**:
- [x] **AC-US5-01**: Preferences → Advanced → new "Studio lifecycle" section with dropdown: `Ask each time` (default) | `Use existing instance` | `Stop existing + use this app` | `Run alongside`.
- [x] **AC-US5-02**: Selecting `Ask each time` clears `studio.lifecycleDefault` to `"ask"` and modal resumes appearing.
- [x] **AC-US5-03**: Tooltip explains each option in plain language.
- [x] **AC-US5-04**: Setting roundtrips through existing 0830 settings store (atomic write, 0600 perms, 250ms debounce).

---

## Glossary

- **Lifecycle modal** — first-launch dialog from US-002 offering Use/Stop/Run-alongside.
- **External instance** — running studio process whose `source != "tauri"` (started via npx CLI, not by desktop app).
- **Lock file** — `~/.vskill/runtime/studio-{port}.lock` written by CLI on start; consumed by scanner as fast-path enumeration.
- **Sidecar** — Node.js studio runtime spawned by desktop app (Tauri sidecar pattern from 0828).

## Open Questions

- **Q1**: "Use that instance" navigates the existing Tauri window vs opens a new web-only window? **Resolved**: navigate existing window — cheap path, single visible surface.
- **Q2**: Confirm before kill when existing instance has unsaved local state? **Resolved**: SIGTERM-not-SIGKILL gives 3s autosave grace; if not enough, user accepts loss.
- **Q3**: Is `lsof` reliable enough for per-PID port extraction on macOS without root? **Resolved**: yes for own processes; lock files first, lsof second.
- **Q4**: How to discover bound port for instance started with `--port 0`? **Resolved**: lock files — runtime writes resolved port after binding.
