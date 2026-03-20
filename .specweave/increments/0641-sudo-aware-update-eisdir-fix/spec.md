---
increment: 0641-sudo-aware-update-eisdir-fix
title: Sudo-aware self-update and EISDIR fix
type: bug
priority: P1
status: completed
created: 2026-03-20T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Sudo-aware self-update and EISDIR fix

## Overview

Two bugs in the specweave CLI update flow:

1. `computePluginHash` in `src/utils/plugin-copier.ts` calls `statSync(fullPath).isFile()` on recursive directory entries. On some platforms/edge cases, this throws EISDIR for directory entries, producing noisy debug log lines. The fix is to use the non-throwing variant `statSync(fullPath, { throwIfNoEntry: false })?.isFile()` and add an explicit directory guard.

2. `selfUpdateSpecWeave` in `src/cli/commands/update.ts` runs `npm install -g specweave@version` without sudo. When specweave was installed via `sudo npm i -g`, the npm global prefix is root-owned and the install fails with EACCES. The current error message suggests `sudo npm install -g specweave@latest` which is confusing — users expect `sudo specweave update` to work. The fix is to auto-detect when the npm global prefix is not writable, auto-retry the install with a `sudo` prefix using `stdio: 'inherit'` (so the user can type their password), and update the fallback error message to suggest `sudo specweave update`.

## User Stories

### US-001: Silent plugin hash computation (P1)
**Project**: specweave

**As a** specweave user
**I want** plugin hash computation to silently skip directories
**So that** my terminal output is not cluttered with EISDIR debug noise during normal operations

**Acceptance Criteria**:
- [x] **AC-US1-01**: `computePluginHash` does not throw or log when encountering directory entries from `readdirSync({ recursive: true })`
- [x] **AC-US1-02**: `computePluginHash` still correctly hashes all file contents and produces a deterministic hash
- [x] **AC-US1-03**: `computePluginHash` still returns empty string for non-existent directories

---

### US-002: Sudo-aware self-update with auto-elevation (P1)
**Project**: specweave

**As a** specweave user who installed with `sudo npm i -g specweave`
**I want** `specweave update` to auto-detect the need for sudo and retry with privilege elevation
**So that** updates succeed without me needing to know npm internals or manually prepend sudo

**Acceptance Criteria**:
- [x] **AC-US2-01**: Before running `npm install -g`, the update logic checks if the npm global prefix directory is writable by the current user
- [x] **AC-US2-02**: If the prefix is not writable, the install command is retried with `sudo` prepended and `stdio: 'inherit'` so the user can enter their password
- [x] **AC-US2-03**: If the prefix IS writable (nvm, volta, user-owned), the install runs without sudo — zero behavioral change
- [x] **AC-US2-04**: The sudo retry uses the same `buildPublicRegistryEnv()` clean environment as the non-sudo path
- [x] **AC-US2-05**: On Windows, sudo detection is skipped entirely — no `sudo` attempts

---

### US-003: Clear error messaging when permissions fail (P1)
**Project**: specweave

**As a** specweave user
**I want** clear, actionable error messages when the update still fails after sudo retry
**So that** I know exactly what command to run to fix the issue

**Acceptance Criteria**:
- [x] **AC-US3-01**: If EACCES persists after sudo retry (or sudo is unavailable), the error message suggests `sudo specweave update` (not `sudo npm install -g specweave@latest`)
- [x] **AC-US3-02**: On Windows, the error message suggests running the terminal as Administrator
- [x] **AC-US3-03**: The spinner/progress text shows "Retrying with sudo..." before the elevated retry so the user understands what is happening

## Functional Requirements

### FR-001: Non-throwing stat in computePluginHash
In `src/utils/plugin-copier.ts`, replace `statSync(fullPath).isFile()` (line 115) with a guard that:
1. Calls `statSync(fullPath, { throwIfNoEntry: false })` to avoid throws on vanished entries
2. Checks `stat?.isFile()` before reading content — directories and symlinks are silently skipped
3. The outer catch block remains for genuinely unreadable files (permission errors, etc.)

### FR-002: Writable prefix detection
Add a helper `isNpmGlobalWritable()` in `src/cli/commands/update.ts` that:
1. Gets the npm global prefix via `execSync('npm prefix -g')`
2. Checks `fs.accessSync(path.join(prefix, 'lib', 'node_modules'), fs.constants.W_OK)` (or just the prefix itself)
3. Returns `true` if writable, `false` if not
4. On Windows (`process.platform === 'win32'`), always returns `true`
5. Wraps in try/catch — returns `false` on any error (safe default)

### FR-003: Sudo-retrying npm install
Modify `installWithFallback` (or the calling code in `selfUpdateSpecWeave`) to:
1. Call `isNpmGlobalWritable()` before the first install attempt
2. If not writable, show spinner text "Retrying with sudo..." and re-run with `sudo` prefix
3. When using sudo, use `stdio: 'inherit'` instead of `['pipe', 'pipe', 'pipe']` so the user can enter their password
4. Pass the same `buildPublicRegistryEnv()` via the `env` option

### FR-004: Updated error messages
Update the EACCES error handler in `selfUpdateSpecWeave` (line 953) to:
1. On Unix: suggest `sudo specweave update` instead of `sudo npm install -g specweave@latest`
2. On Windows: suggest "Run your terminal as Administrator"

## Success Criteria

- Zero EISDIR debug log lines during normal `computePluginHash` operation
- `specweave update` succeeds on root-owned npm global prefixes without manual sudo
- Users on nvm/volta/non-sudo installs see zero behavioral change
- Error messages reference `specweave update`, not raw npm commands

## Out of Scope

- Changing how plugins are installed (only self-update is affected)
- Supporting privilege elevation on Windows (UAC prompt) — only error message improvement
- Changing the npm registry or authentication logic
- Refactoring the overall update command structure

## Dependencies

- Node.js `fs.accessSync` for writability check (built-in, no new deps)
- `sudo` binary availability on Unix (standard, not installed by specweave)
