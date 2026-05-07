---
tasks: 14
completed: 14
phase: 1
note: |
  Phase 1 of the 60-task plan in plan.md. Tracks T-001..T-014 below correspond
  to the actual macOS Phase 1 work shipped in 0828; the remaining plan.md tasks
  were handed off to 0829-vskill-distribution-and-marketing.
---

# Tasks — 0828 vskill Desktop App (Phase 1)

This file ledgers the Phase 1 macOS work that was actually executed and verified
in 0828. The 60-task `plan.md` describes the full multi-phase vision; tasks for
phases 2–5 (signing/notarization, auto-update, telemetry, Windows port) were
handed off to 0829.

---

### T-001: Tauri 2 Rust scaffold
**User Story**: US-001 | **Satisfies ACs**: AC-US01-01, AC-US01-03, AC-US09-01 | **Status**: [x] completed
**Outcome**: `Cargo.toml`, `tauri.conf.json`, `build.rs` created under `repositories/anton-abyzov/vskill/vskill-desktop/src-tauri/`. Builds clean on macOS arm64.

### T-002: Tauri Rust source modules
**User Story**: US-006 | **Satisfies ACs**: AC-US06-01, AC-US06-02, AC-US07-03 | **Status**: [x] completed
**Outcome**: `main.rs`, `lib.rs`, `sidecar.rs`, `menu.rs`, `lifecycle.rs`, `commands.rs` implemented. Provides app entry, sidecar supervision, native macOS menu bar, window-state lifecycle, and Tauri command surface.

### T-003: Sidecar binary build (Node SEA)
**User Story**: US-009 | **Satisfies ACs**: AC-US01-03, AC-US09-01, AC-US09-02 | **Status**: [x] completed
**Outcome**: 114 MiB host-arch arm64 Mach-O at `src-tauri/binaries/vskill-server-aarch64-apple-darwin`. Built via Node 22 SEA + esbuild + postject pipeline orchestrated by `build.rs`.

### T-004: sidecar-entry.mjs wrapper
**User Story**: US-006 | **Satisfies ACs**: AC-US06-02 | **Status**: [x] completed
**Outcome**: Wrapper emits `LISTEN_PORT=N` on stdout once eval-server binds; applies SEA-compatible `fs` patches so vendored Node tooling reads bundled assets correctly.

### T-005: Studio Cmd+K hotkey fix
**User Story**: US-007 | **Satisfies ACs**: AC-US07-06 | **Status**: [x] completed
**Outcome**: Removed duplicate `keydown` listener in `AgentModelPicker`; introduced `openAgentModelPicker` CustomEvent so `Cmd+Shift+M` reliably opens the picker without colliding with the global Cmd+K Find Skills shortcut.

### T-006: e2e/studio-hotkeys-cmdk.spec.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US01-04, AC-US07-06 | **Status**: [x] completed
**Outcome**: 4 Playwright scenarios cover Cmd+K open, filter, navigate, close + Cmd+Shift+M opens AgentModelPicker. All 4 pass.

### T-007: keymap.md reference
**User Story**: US-007 | **Satisfies ACs**: AC-US07-06 | **Status**: [x] completed
**Outcome**: `src/eval-ui/src/lib/keymap.md` documents the canonical Studio hotkey table (Cmd+K, Cmd+Shift+M, Esc, Enter, etc.).

### T-008: dist/eval-ui rebuild
**User Story**: US-009 | **Satisfies ACs**: AC-US01-03, AC-US09-01 | **Status**: [x] completed
**Outcome**: Studio UI bundle rebuilt; WebView serves the same artifact `npx vskill studio` serves — zero duplication.

### T-009: Hotfix Bug A — sidecar leak on quit
**User Story**: US-004 | **Satisfies ACs**: AC-US04-01, AC-US12-05 | **Status**: [x] completed
**Outcome**: `lib.rs` `RunEvent::ExitRequested` now sends SIGTERM to the sidecar `Child` and awaits exit before resolving. Verified by macos-verify: clean `ps aux | grep vskill` after quit.

### T-010: Hotfix Bug B — Retina pixel scaling
**User Story**: US-004 | **Satisfies ACs**: AC-US04-05 | **Status**: [x] completed
**Outcome**: `lifecycle.rs` window-state schema bumped to v2 — stores logical points instead of physical pixels. New install opens at 1280x800 logical (not 2560x1600 physical). v1 → v2 migration drops stale pixel values.

### T-011: install-test verification
**User Story**: US-001 | **Satisfies ACs**: AC-US01-01, AC-US01-02, AC-US06-01, AC-US06-02 | **Status**: [x] completed
**Outcome**: install-test agent confirmed: window opens 1280x800 logical, `/api/health` returns 200, `/` returns 200, `/api/skills` returns 200, lifecycle quit clean.

### T-012: functional-test verification
**User Story**: US-001 | **Satisfies ACs**: AC-US01-04, AC-US07-06 | **Status**: [x] completed
**Outcome**: functional-test agent ran Cmd+K e2e suite (4/4 PASS) and the existing 27/27 unit suite. No regressions.

### T-013: Hotfix re-verification
**User Story**: US-004 | **Satisfies ACs**: AC-US04-01, AC-US04-05, AC-US12-05 | **Status**: [x] completed
**Outcome**: macos-verify confirmed Bug A and Bug B fixes are non-regressed: clean process tree on quit, 1280x800 logical window on first launch, persisted state honored across relaunches.

### T-014: macos-verify final pass
**User Story**: US-001 | **Satisfies ACs**: AC-US01-01, AC-US01-02, AC-US06-01, AC-US06-02, AC-US06-05, AC-US07-03, AC-US07-04, AC-US11-01, AC-US12-01 | **Status**: [x] completed
**Outcome**: Final macos-verify pass: window logical 1280x800, traffic-lights native, native menu bar populated, Help → Reveal Logs opens Finder, all HTTP endpoints respond 200, `npx vskill studio` coexists on a different port, no LaunchAgents created.
