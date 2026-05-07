# Tasks — 0832 Skill Studio process lifecycle

12 tasks across 4 phases. TDD: each task ships failing tests → impl → green.

## Phase 1 — Lock file infrastructure (CLI side)

### T-001: Write `vskill/src/cli/lib/lockfile.ts` — atomic write + cleanup
**Satisfies ACs**: AC-US4-04, AC-US4-05
**Test**: Given a CLI start with --port 7077 → When `vskill studio` boots → Then `~/.vskill/runtime/studio-7077.lock` exists with `{pid, port, cmdline, startedAt}`. On SIGTERM/SIGINT the file is removed.

### T-002: Wire lockfile.ts into `cli/commands/studio.ts` start path + SIGTERM/SIGINT handler
**Satisfies ACs**: AC-US4-04, AC-US4-05
**Test**: Given Ctrl-C during running studio → Then lock file is gone within 1s.

### T-003: Add `vskill studio --status` flag
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Test**: Given two running studio instances → When `vskill studio --status` runs → Then stdout has 2 tab-separated lines + exit 0. No instances → empty stdout + exit 0.

### T-004: Add `vskill studio --replace` flag
**Satisfies ACs**: AC-US4-01, AC-US4-03
**Test**: Given one running external instance → When `vskill studio --replace` runs → Then old PID exits within 4s and new instance is bound. Help text includes both flags.

## Phase 2 — Rust process_discovery scanner

### T-005: `src-tauri/src/process_discovery/mod.rs` — define `ProcessRecord` struct + scan() with 500ms timeout
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05
**Test**: Given lock file at ~/.vskill/runtime/studio-7077.lock → When scan() runs → Then returns ProcessRecord{pid, port: 7077, source: "npx-cli", ...}. Mock slow enumeration → scan returns empty + log warning if >500ms.

### T-006: Lock-file fast path with stale pruning + PID-cmdline cross-check
**Satisfies ACs**: AC-US1-02, AC-US4-05
**Test**: Given lock file with PID for a non-vskill process (PID reuse) → Then scanner prunes the lock file and excludes from result. Lock files >1d old + no matching PID → pruned.

### T-007: Platform-native fallback (macOS lsof, Linux /proc, Windows Get-Process)
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Test**: Given a vskill-server process with no lock file → Then platform fallback discovers it via `pgrep -f vskill-server` + `lsof -p PID -P -n -iTCP -sTCP:LISTEN` and extracts the bound port.

### T-008: Pre-flight gate in `sidecar::spawn_sidecar` — invoke scanner before binding
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Test**: Given external instance detected → spawn_sidecar emits a `lifecycle-modal-required` event with the ProcessRecord and pauses. Given none detected → spawn_sidecar continues normal flow.

## Phase 3 — Lifecycle modal UI

### T-009: New Tauri WebviewWindow for the modal — `src-tauri/src/lifecycle_modal.rs`
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Test**: Given `lifecycle-modal-required` event → Then 720x320 modal window opens centered, shows port + source + relative-time, three primary buttons + Cancel, default focus on first button. Cmd+Q during modal exits desktop cleanly.

### T-010: Three IPC handlers — `lifecycle_use_existing`, `lifecycle_stop_existing`, `lifecycle_run_alongside`
**Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-06
**Test**: use_existing → main window navigates to http://127.0.0.1:{port}/. stop_existing → SIGTERM, 3s grace, SIGKILL → spawn fresh sidecar. run_alongside → spawn fresh sidecar without touching existing.

### T-011: "Don't ask again" preference + Preferences → Advanced → Studio lifecycle dropdown
**Satisfies ACs**: AC-US2-07, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Test**: Checkbox persists to settings.json::studio.lifecycleDefault via existing 0830 store. Subsequent boots with non-"ask" value skip modal and execute the saved action. Resetting via Preferences brings the modal back.

## Phase 4 — Window > Studio Instances submenu

### T-012: Dynamic submenu populated on open + Switch/Stop actions
**Satisfies ACs**: AC-US3-01..05
**Test**: Given the user opens Window > Studio Instances → Then submenu rebuilds with one row per ProcessRecord (this app row disabled). Click Switch → main window navigates. Click Stop → confirmation dialog → SIGTERM. Empty state shows disabled `No other instances` placeholder.
