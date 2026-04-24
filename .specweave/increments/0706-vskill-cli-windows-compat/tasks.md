---
increment: 0706-vskill-cli-windows-compat
title: "Windows compatibility fixes for vskill install/update/studio"
---

# Tasks: Windows compatibility fixes for vskill install/update/studio

TDD: write failing vitest test first → implement → refactor. All changes must be no-op on macOS/Linux.

## Phase A — Agent detection (US-001)

### T-001: Extract `detectCommand`/`detectBinary` helper in resolve-binary.ts
**AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/utils/resolve-binary.ts`, `src/utils/__tests__/resolve-binary-platform.test.ts` (NEW)
**Test Plan**:
- Given `process.platform` stubbed to "win32"
- When `buildDetectCommand("node")` runs
- Then result is `"where node"`
- And given `process.platform = "darwin"`, result is `"which node"`
- And given `detectBinary("node")` with exec mocked to succeed, returns true; with exec throwing, returns false

### T-002: Migrate agents-registry.ts to function-based detectInstalled
**AC**: AC-US1-01, AC-US1-03 | **Status**: [x] completed <!-- 2026-04-24 re-applied in 986d6bd after earlier reset. 52 rows migrated; type widened to `string | (() => Promise<boolean>)`; consumer in detectInstalledAgents() handles both shapes; agents-registry.test.ts updated for new shape. -->

**Files**: `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts`, `src/agents/__tests__/registry-platform.test.ts` (NEW)
**Test Plan**:
- Given each registry entry with `detectInstalled: 'which <bin>'` rewritten to `detectInstalled: () => detectBinary(<bin>)`
- When the entry is read on Windows
- Then the function returns correctly based on `where <bin>` (via mocked exec)
- And on macOS, based on `which <bin>`
- And the registry TypeScript types accept both string (legacy) and function (new) so rollout can be incremental

### T-003: Rewrite copilot detection to pure-Node (fs.existsSync + readdirSync)
**AC**: AC-US1-04 | **Status**: [x] completed <!-- 2026-04-24 re-applied in 986d6bd. copilot row now uses `detectBinary('code')` + `fsExistsSync(~/.vscode/extensions)` + `fsReaddirSync().some(e => e.startsWith('github.copilot-'))`. -->

**Files**: `repositories/anton-abyzov/vskill/src/agents/agents-registry.ts` (line ~139)
**Test Plan**:
- Given `~/.vscode/extensions/github.copilot-1.234.0/` exists AND `which code` succeeds
- When the copilot detect function runs
- Then result is true
- And given no `github.copilot-*` subdirectory, result is false
- And given `code` not on PATH, result is false (regardless of extensions dir)

## Phase B — Path-traversal guard (US-002)

### T-004: Swap startsWith guard to path.relative in canonical.ts:47
**AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/installer/canonical.ts`, `src/installer/__tests__/canonical-platform.test.ts` (NEW)
**Test Plan**:
- Given `normalizedRoot = "C:\\Users\\x\\.claude"` and `resolved = "C:\\Users\\x\\.claude\\skills\\foo"` on Windows
- When the guard runs
- Then it passes (returns safe)
- And given `resolved = "C:\\Windows\\System32"`, the guard throws "Path traversal"
- And on macOS/Linux, same semantics with forward slashes

### T-005: Apply same fix to update.ts:43 and :56
**AC**: AC-US2-03 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/commands/update.ts`, `src/commands/__tests__/update-platform.test.ts` (NEW)
**Test Plan**:
- Given ghost-file cleanup scanning targets under the installed base directory
- When running on Windows with mixed-separator target paths
- Then files inside the base are cleaned (not skipped as before)
- And files outside the base are still rejected

## Phase C — Symlink fallback (US-003)

### T-006: Generalize copy fallback in canonical.ts:83
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/installer/canonical.ts`
**Test Plan**:
- Given `fs.symlinkSync` mocked to throw `EPERM` for agent "cursor"
- When `canonicalInstall(...)` runs
- Then copyRecursive is called instead, the install completes without error, and stderr receives the warning "Symlinks not available — copying files..." exactly once
- And given a second install in the same process, the warning is NOT repeated (module-scoped `warnedAboutSymlinkFallback` flag)
- And given a non-EPERM error, the original error propagates
- And on macOS with real fs, symlink is used (no copy)

## Phase D — Port-probe replacement (US-004)

### T-007: Replace lsof/ps with probeVskillServer in eval/serve.ts
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/src/commands/eval/serve.ts`, `src/commands/eval/__tests__/serve-port-probe.test.ts` (NEW)
**Test Plan**:
- Given port 3077 is occupied and `probeVskillServer(3077, 1000)` returns `{ok:true, version:"0.5.x"}`
- When `serveCommand` runs
- Then it reuses the existing server (no crash, no new spawn)
- And given probe returns null (port occupied by non-vskill)
- Then stderr contains "Port 3077 is in use by a non-vskill process" and `process.exit(1)` is called
- And given port is free, probe returns null quickly (<1s)
- And code path works identically on Windows and macOS — no `lsof`/`ps` calls

## Phase E — CI matrix (US-005)

### T-008: Add windows-latest to CI matrix
**AC**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Files**: `repositories/anton-abyzov/vskill/.github/workflows/ci.yml`
**Test Plan**:
- Given the updated workflow
- When a PR is opened
- Then three matrix jobs run: ubuntu-latest, macos-latest, windows-latest
- And each job runs `npm ci && npm run build && npm test`
- And each job runs the smoke sequence: `vskill --version`, `install --help`, `update --help`, `studio --help` — exit 0 required
- And the Windows job runs an install against a local fixture skill and verifies at least one agent is detected OR graceful fallback message printed

## Execution notes

- Tasks 1–3 (Phase A) are independent — agent detection only.
- Tasks 4–5 (Phase B) share a path helper pattern — do T-004 first, copy pattern to T-005.
- Task 6 (Phase C) only touches canonical.ts — independent.
- Task 7 (Phase D) only touches serve.ts — independent.
- Task 8 (Phase E) requires T-001..T-007 to be merged before it goes green on Windows.
- Total: 8 tasks. All on vskill CLI repo. Single agent can own the whole increment.
