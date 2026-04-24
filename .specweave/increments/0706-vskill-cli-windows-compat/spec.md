---
increment: 0706-vskill-cli-windows-compat
title: Windows compatibility fixes for vskill install/update/studio
type: bug
priority: P2
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Windows compatibility fixes for vskill install/update/studio

## Overview

Fix five concrete Windows blockers in the vskill CLI that prevent Windows users from installing skills into their AI agents, updating installed skills, or running the Skill Studio. These bugs were documented in the cross-platform audit on 2026-04-24 — surgical fixes, no API changes, no user-visible behavior changes on macOS/Linux.

## Context

Cross-platform audit (2026-04-24) of `repositories/anton-abyzov/vskill/` found five Windows-specific bugs, all in shell-out / path-handling / symlink code:

| File:line | Bug | Impact |
|---|---|---|
| `src/agents/agents-registry.ts:84–290,831` | ~30 entries use `detectInstalled: 'which <bin>'`; copilot row (line 139) pipes `which code && ls ~/.vscode/extensions/github.copilot-* 2>/dev/null`. Executed via `exec()` through `cmd.exe` on Windows where `which`/`&&`/`~`/`2>/dev/null` are not valid | `detectInstalledAgents()` returns empty on Windows → `vskill install`/`add` installs into zero agents |
| `src/installer/canonical.ts:47` | Path-traversal guard uses `resolved.startsWith(normalizedRoot + "/")` | False-positives on Windows (mixed separators) → `vskill install` throws "path traversal" error |
| `src/installer/canonical.ts:83` | `symlinkSync(relTarget, linkPath, "dir")` with only a claude-code-specific copy fallback | Non-claude-code agents silently fail on Windows without Administrator or Developer Mode |
| `src/commands/update.ts:43,56` | Ghost-file cleanup uses `target.startsWith(resolvedBase + "/")` | No-ops on Windows; stale files left behind (benign — not data loss) |
| `src/commands/eval/serve.ts:83,86` | Port-conflict detection uses `execSync("lsof -ti:${port}")` and `ps -p ${pid} -o command=` | `vskill studio` crashes on Windows — no lsof, no POSIX ps |

Note: `vskill submit` itself is already Windows-safe (pure `fetch` + OS-aware `openBrowser`). `vskill diff` from increment 0705 is being built Windows-safe. This increment focuses exclusively on the five bugs above — the rest of the CLI already works on Windows.

## Goals

- `vskill install <skill>` successfully detects and installs into all supported AI agents on Windows.
- `vskill update <skill>` cleans up stale files on Windows (no-op → correct cleanup).
- `vskill studio` port conflict detection works on Windows.
- All changes are no-ops on macOS/Linux (zero regression).
- CI matrix runs on `windows-latest` and green.

## Non-Goals

- Rewriting the CLI on top of a cross-platform wrapper library. Five surgical fixes only.
- Extending agent detection to new AI agents. In-scope: only the ones already in `agents-registry.ts`.
- Windows UI work. The Studio is a React SPA served from localhost — already cross-platform.

## User Stories

### US-001: Install detects agents on Windows
**Project**: vskill

**As a** Windows user running `vskill install <skill>`
**I want** the CLI to correctly detect the AI agents installed on my system (Claude Code, Cursor, Codex, Copilot, etc.)
**So that** my skill gets installed into every agent I have, not zero.

**Acceptance Criteria**:
- [x] **AC-US1-01**: On `process.platform === "win32"`, `detectInstalledAgents()` does NOT use `which`, `&&`, `~`, or `2>/dev/null`. Instead it uses `where` (the Windows equivalent of `which`) via a helper, or direct `fs.existsSync` for location-based checks.
- [x] **AC-US1-02**: On macOS/Linux the detection logic uses `which` as before — no regression.
- [x] **AC-US1-03**: For each of the ~30 entries in `agents-registry.ts`, a unit test with `process.platform` mocked to both `"win32"` and `"darwin"` verifies the detection command chosen is platform-appropriate.
- [x] **AC-US1-04**: The Copilot row specifically (current line 139) replaces the shell pipe with `fs.existsSync(path.join(os.homedir(), ".vscode/extensions"))` + a pattern match using `fs.readdirSync`, and detects a `github.copilot-*` directory on both platforms.

### US-002: Install uses correct path comparison on Windows
**Project**: vskill

**As a** Windows user running `vskill install`
**I want** the canonical path traversal guard to work with Windows path separators
**So that** legitimate install targets are not rejected as "path traversal".

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/installer/canonical.ts:47` replaces `resolved.startsWith(normalizedRoot + "/")` with `!path.relative(normalizedRoot, resolved).startsWith("..")`. The new check works on Windows (backslash) and POSIX (forward slash).
- [x] **AC-US2-02**: Unit test: given `normalizedRoot = "C:\\Users\\x\\.claude"` and `resolved = "C:\\Users\\x\\.claude\\skills\\foo"`, the guard returns true (safe); given `resolved = "C:\\Windows\\System32"`, the guard returns false.
- [x] **AC-US2-03**: Same check applied to `src/commands/update.ts:43` and `:56` — ghost-file cleanup works correctly on Windows.

### US-003: Install falls back to copy on symlink EPERM
**Project**: vskill

**As a** Windows user without Administrator / Developer Mode
**I want** `vskill install` to fall back to copying files when symlinking is not permitted
**So that** every agent I have gets the skill, not just claude-code (the one with a hardcoded fallback today).

**Acceptance Criteria**:
- [x] **AC-US3-01**: `src/installer/canonical.ts:83` wraps `symlinkSync()` in a try/catch that catches `EPERM`/`EACCES` and falls back to `copyFileSync` + recursive directory copy for ALL agents (not just claude-code).
- [x] **AC-US3-02**: When the fallback triggers, a single warning is logged to stderr: "Symlinks not available — copying files (enable Developer Mode to use symlinks)". Subsequent files in the same install do NOT re-log.
- [x] **AC-US3-03**: On macOS/Linux, symlink remains the default. Copy fallback is only triggered by EPERM/EACCES.
- [x] **AC-US3-04**: Unit test with `fs.symlinkSync` mocked to throw EPERM verifies the fallback is used and the install completes successfully.

### US-004: Studio port-conflict detection works on Windows
**Project**: vskill

**As a** Windows user running `vskill studio`
**I want** the port-conflict check to work without crashing
**So that** I can open the Studio in my browser.

**Acceptance Criteria**:
- [x] **AC-US4-01**: `src/commands/eval/serve.ts:83,86` replaces `execSync("lsof -ti:${port}")` and `ps -p ${pid} -o command=` with a pure Node approach: attempt an HTTP GET to `http://localhost:${port}/api/config` with a 1000ms timeout using the existing `probeVskillServer` helper.
- [x] **AC-US4-02**: If the probe succeeds and returns a vskill-identity response, the CLI reuses the existing server and prints its URL.
- [x] **AC-US4-03**: If the probe fails (connection refused OR non-vskill response), the CLI prints "port ${port} is in use by a non-vskill process — please free it manually" and exits 1. The CLI does NOT attempt to discover or kill the PID.
- [x] **AC-US4-04**: No regression on macOS/Linux — same exit behavior as before.

### US-005: CI matrix includes windows-latest
**Project**: vskill

**As a** maintainer
**I want** CI to run the full vskill CLI test suite on `windows-latest` on every PR
**So that** Windows regressions are caught automatically.

**Acceptance Criteria**:
- [x] **AC-US5-01**: `.github/workflows/ci.yml` has a matrix entry with `runs-on: windows-latest` that runs `npm ci`, `npm run build`, `npm test`, and a smoke sequence: `npx vskill --version`, `npx vskill install --help`, `npx vskill update --help`, `npx vskill studio --help`. Exit 0 required for all.
- [x] **AC-US5-02**: The same job runs `npx vskill install <a-test-skill>` against a local fixture, and verifies the skill is installed into every detected agent OR that graceful fallback messaging is printed when zero agents are detected. Exit 0 required.

## Success Metrics

- `windows-latest` CI green on 3 consecutive runs.
- User report from a Windows user confirming `vskill install <skill>` installs into multiple agents.
- No macOS/Linux regressions (existing CI jobs stay green).

## References

- Cross-platform audit report (this session, 2026-04-24).
- File:line evidence for all five bugs (table in Context section).
- Existing helpers to reuse: `src/utils/resolve-binary.ts` (where/which swap), `probeVskillServer` in eval/serve.ts, `COPY_FALLBACK_AGENTS` in canonical.ts.
