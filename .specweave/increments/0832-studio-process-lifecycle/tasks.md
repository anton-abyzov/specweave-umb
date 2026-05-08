# Tasks — 0832 Skill Studio process lifecycle

12 tasks across 4 phases. TDD: each task ships failing tests → impl → green.

## Phase 1 — Lock file infrastructure (CLI side)

### T-001: Write studio-runtime/lockfile.ts — atomic write + cleanup
**Status**: Completed
**Satisfies ACs**: AC-US4-04, AC-US4-05
**Test**: Given a CLI start with --port 7077 → When `vskill studio` boots → Then `~/.vskill/runtime/studio-7077.lock` exists with `{pid, port, cmdline, startedAt}`. On SIGTERM/SIGINT the file is removed.
**Notes**: Implemented at `src/studio-runtime/lockfile.ts`. Renamed from the original `src/cli/lib/lockfile.ts` plan path because vskill keeps CLI commands at `src/commands/` (no `src/cli/` tree exists). 18 vitest cases cover write, read, atomic-tmp, idempotent remove, list, prune, isPidAlive, registerCleanup.

### T-002: Wire lockfile.ts into the studio start path + SIGTERM/SIGINT handler
**Status**: Completed
**Satisfies ACs**: AC-US4-04, AC-US4-05
**Test**: Given Ctrl-C during running studio → Then lock file is gone within 1s.
**Notes**: `src/commands/eval/serve.ts` writes the lock right after the HTTP server binds; `registerCleanup(port)` installs SIGINT/SIGTERM/SIGHUP/exit handlers, and the existing `shutdown()` helper also calls `removeLock` for belt-and-suspenders idempotency.

### T-003: Add `vskill studio --status` flag
**Status**: Completed
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Test**: Given two running studio instances → When `vskill studio --status` runs → Then stdout has 2 tab-separated lines + exit 0. No instances → empty stdout + exit 0.
**Notes**: `--status` runs before any side-effect path; calls `pruneStaleLocks()` so output is always live, then `process.stdout.write` per row + exit 0. Help text registered in `src/index.ts`.

### T-004: Add `vskill studio --replace` flag
**Status**: Completed
**Satisfies ACs**: AC-US4-01, AC-US4-03
**Test**: Given one running external instance → When `vskill studio --replace` runs → Then old PID exits within 4s and new instance is bound. Help text includes both flags.
**Notes**: `--replace` SIGTERMs every external lock owner (3s grace → SIGKILL), then proceeds through the existing `--force` port-conflict path so a foreign lockfile-less server on the target port is still cleared.

## Phase 2 — Rust process_discovery scanner

### T-005: `src-tauri/src/process_discovery/mod.rs` — define `ProcessRecord` struct + scan() with 500ms timeout
**Status**: Completed
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05
**Test**: Given lock file at ~/.vskill/runtime/studio-7077.lock → When scan() runs → Then returns ProcessRecord{pid, port: 7077, source: "npx-cli", ...}. Mock slow enumeration → scan returns empty + log warning if >500ms.
**Notes**: `scan()` wraps `scan_inner()` in `tokio::time::timeout(500ms)`. Returns `Ok(Vec::new())` on timeout with a log::warn. ProcessRecord serialised to JSON with serde for Tauri-IPC consumption.

### T-006: Lock-file fast path with stale pruning + PID-cmdline cross-check
**Status**: Completed
**Satisfies ACs**: AC-US1-02, AC-US4-05
**Test**: Given lock file with PID for a non-vskill process (PID reuse) → Then scanner prunes the lock file and excludes from result. Lock files >1d old + no matching PID → pruned.
**Notes**: `lock_is_stale()` checks (a) >1d age via `parse_iso8601_to_unix`, (b) `pid_is_alive` via `kill(pid, 0)`, (c) cmdline mismatch via `/proc/PID/cmdline` (Linux) or `ps -o command= -p PID` (macOS). Stale entries are unlinked.

### T-007: Platform-native fallback (macOS lsof, Linux /proc, Windows Get-Process)
**Status**: Completed
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Test**: Given a vskill-server process with no lock file → Then platform fallback discovers it via `pgrep -f vskill-server` + `lsof -p PID -P -n -iTCP -sTCP:LISTEN` and extracts the bound port.
**Notes**: macOS uses `pgrep -f` for two patterns (`vskill-server`, `vskill.*studio`) + `lsof -Fn` listen-port extraction. Linux walks `/proc/{pid}/cmdline`. Windows shells to PowerShell `Get-NetTCPConnection`. Dedup by PID at the end.

### T-008: Pre-flight gate in `sidecar::spawn_sidecar` — invoke scanner before binding
**Status**: Completed
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Test**: Given external instance detected → spawn_sidecar emits a lifecycle event with the ProcessRecord and pauses. Given none detected → spawn_sidecar continues normal flow.
**Notes**: Top of `spawn_sidecar` checks `skip_spawn_to_port` first (use-existing flow) then runs `scan()`. If the scanner returns an external-source record AND `studio.lifecycleDefault == "ask"` it opens the modal and returns `Err("lifecycle-modal-pending")` (treated as non-fatal in lib.rs). Other lifecycleDefault values auto-execute (use-existing → load URL + return Ok, stop-and-replace → SIGTERM/SIGKILL + fall through, run-alongside → fall through).

## Phase 3 — Lifecycle modal UI

### T-009: New Tauri WebviewWindow for the modal — `src-tauri/src/lifecycle_modal.rs`
**Status**: Completed
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Test**: Given `lifecycle-modal-required` event → Then 720x320 modal window opens centered, shows port + source + relative-time, three primary buttons + Cancel, default focus on first button. Cmd+Q during modal exits desktop cleanly.
**Notes**: `lifecycle.html` is a new vite entry point in `src/eval-ui/lifecycle.html` + `src/eval-ui/src/lifecycle/{main,LifecycleApp,InstancesApp,styles}.tsx/css`. The Rust `lifecycle_modal::open` builds a 720×320 non-resizable WebviewWindow. Default focus on the primary button via React useEffect + ref. Cancel calls `quit` IPC.

### T-010: Three IPC handlers — `lifecycle_use_existing`, `lifecycle_stop_existing`, `lifecycle_run_alongside`
**Status**: Completed
**Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-06
**Test**: use_existing → main window navigates to http://127.0.0.1:{port}/. stop_existing → SIGTERM, 3s grace, SIGKILL → spawn fresh sidecar. run_alongside → spawn fresh sidecar without touching existing.
**Notes**: All three handlers wired in `commands.rs` and registered via `tauri::generate_handler!`. `kill_external_pid` (3s SIGTERM grace → SIGKILL) is shared by `lifecycle_stop_existing` and the Window > Studio Instances `stop_studio_instance` action. Plus `get_detected_instance` so the React layer fetches state on mount without a render-time event-listen race.

### T-011: "Don't ask again" preference + Preferences → Advanced → Studio lifecycle dropdown
**Status**: Completed
**Satisfies ACs**: AC-US2-07, AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Test**: Checkbox persists to settings.json::studio.lifecycleDefault via existing 0830 store. Subsequent boots with non-"ask" value skip modal and execute the saved action. Resetting via Preferences brings the modal back.
**Notes**: `StudioSettings { lifecycle_default }` added to settings.rs with allow-list path `studio.lifecycleDefault`, validated against the four-value enum. The modal's checkbox writes via `set_setting`, the Advanced tab dropdown reads/writes the same key. The `spawn_sidecar` gate honours the saved value (use-existing auto-loads URL, stop-and-replace auto-kills, run-alongside falls through). 4 new vitest-style cargo tests cover accept/reject/persist/default.

## Phase 4 — Window > Studio Instances submenu

### T-012: Dynamic submenu populated on open + Switch/Stop actions
**Status**: Completed
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Test**: Given the user opens Window > Studio Instances → Then submenu rebuilds with one row per ProcessRecord (this app row disabled). Click Switch → main window navigates. Click Stop → confirmation dialog → SIGTERM. Empty state shows disabled `No other instances` placeholder.
**Notes**: Window menu gains a "Studio Instances..." item that opens a 540×420 dedicated window backed by the same `lifecycle.html` entry point (`?mode=instances` query param switches the React app to `InstancesApp`). The list is fetched via `list_studio_instances` IPC on mount AND on a Refresh button click — no polling. Tauri-spawned rows are disabled with `(this app)` label. Stop click confirms via `window.confirm` then calls `stop_studio_instance` IPC. Empty state renders the disabled placeholder per AC-US3-05.

## Test summary

- `cargo test --manifest-path src-tauri/Cargo.toml`: **57/57 passing** (14 process_discovery + 4 studio settings + 3 commands IPC-helper + 1 ProcessRecord camelCase contract + 35 inherited)
- `npx vitest run src/studio-runtime/`: **21/21 passing** (18 base + 3 F-007 race-protection cases)
- `npx vitest run src/commands/eval/`: **40/40 passing** (existing serve tests unchanged)
- `npm run build:eval-ui`: produces `dist/eval-ui/{main,preferences,lifecycle}.html` and corresponding asset bundles.
- `cargo build --manifest-path src-tauri/Cargo.toml`: clean (3 warnings, all unused-helper, kept for future extensibility).
- `npx tsc --noEmit`: clean.

## Closure-time fixes (applied during sw:done iteration)

- **Code-review iteration 1 (11 fixes)**: F-001 stale Tauri pid clear, F-002 bypass_scan_once for run-alongside, F-003 explicit errno capture in pid_is_alive, F-004 modal gates on `external.len()==1`, F-005 pid validation defense-in-depth, F-006 commands.rs IPC-helper unit tests, F-007 lockfile live-foreign-pid race protection, F-008+F-013 doc/comment cleanup, F-009 npx _npx-cache detection, F-010 atomic rollback on lifecycle_use_existing failure.
- **Code-review iteration 2 (2 fixes)**: F-LOGIC-01 dedupe-by-PID in scan_inner, F-LOGIC-03 unparseable timestamp treated as stale.
- **Simplify pass (1 consolidation)**: kill_external_pid in commands.rs delegates to shared sidecar::sigterm_with_grace (eliminating SIGTERM/SIGKILL pattern duplication).
- **Grill iteration 1 → 2 (3 fixes)**: F-GRILL-01 ProcessRecord camelCase serde rename (was rendering "just now" forever), F-GRILL-02 instances window refresh-on-reopen via studio-instances://refresh event, F-GRILL-03 desktop sidecar writes lock file with source="tauri".

## Deferred to v1.0.15+ polish

- F-LOGIC-02 RAII-guard for bypass_scan_once (refactoring-risk hardening, current behavior correct).
- F-SEC-01 TOCTOU mitigation via pidfd_open (Linux) / EVFILT_PROC (macOS).
- F-PERF-01/02 parallelize lsof + async ps inside scan_macos.
- F-SEC-02 rate-limit + audit log on stop_studio_instance.
- F-TYPES-02 closed-enum refactor for studio.lifecycleDefault.
