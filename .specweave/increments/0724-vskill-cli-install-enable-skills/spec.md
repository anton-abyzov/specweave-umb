---
increment: 0724-vskill-cli-install-enable-skills
title: vskill CLI — Install / Enable / Disable Skills (Claude Code wiring)
type: feature
priority: P1
status: completed
created: 2026-04-25T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill CLI — Install / Enable / Disable Skills

## Overview

The vskill CLI today exposes a rich catalog surface — `install`, `remove`, `find`, `list`, `info`, `pin`, `unpin`, `outdated`, `marketplace`, `blocklist`, `audit`, `diff`, `versions`, `update`, `cleanup`, `init`, `keys`, `studio`, `eval`, `submit`, `scan`. Each one is well-tested and covers a step in the catalog/version lifecycle. The gap is the **activation surface**: once a skill is on disk (installed under `<agent>.localSkillsDir` or `<agent>.globalSkillsDir`, with a marketplace plugin entry written into `enabledPlugins` of `~/.claude/settings.json`), there is no first-class way to toggle it off without removing files, and no first-class way to toggle a previously-disabled skill back on without re-running `vskill install`. The user can only achieve this today by hand-editing `~/.claude/settings.json` (which `src/settings/settings.ts` correctly forbids vskill from touching directly) or by chaining `claude plugin install/uninstall` invocations.

This increment closes that gap by adding two new commands — `vskill enable <skill-name>` and `vskill disable <skill-name>` — that wrap `claude plugin install` / `claude plugin uninstall` (the only sanctioned write path to `enabledPlugins`) without touching the on-disk skill files. Disable is reversible: the SKILL.md and lockfile entry stay put, only the `enabledPlugins[<plugin-id>]` flag flips. Enable re-asserts the registration. Both commands respect `--scope=user|project` and report which agent surfaces were affected, mirroring the multi-agent awareness already encoded in `agents-registry.ts` (53 agents, 8 universal). For non-Claude-Code agents that do not use `enabledPlugins` semantics, enable/disable degrade gracefully — they document that those agents auto-discover skills from their `localSkillsDir`/`globalSkillsDir` and there is nothing to toggle, so we report a clear no-op rather than a silent skip.

The secondary UX improvements are tighter: `vskill list` gains an `--installed` view that joins the lockfile with `enabledPlugins` per scope, showing an explicit `enabled / disabled / n/a` column per skill per scope; `vskill install` documents (and exposes via `--no-enable`) that it currently always enables on install; `vskill add`/`install` and `vskill remove` continue to behave exactly as today, with the new commands layered on top so existing users see no behaviour change unless they opt in. All file/CLI writes are atomic (tmp-then-rename for any vskill-managed JSON; CLI delegation for `enabledPlugins`) and all operations are idempotent — running `vskill enable foo` twice produces one warning and exit 0.

The third UX improvement is **agent-surface clarity**: when the user runs `vskill enable foo`, the output names every agent surface that received the registration (e.g., `Claude Code (user scope) — enabled` / `Cursor — auto-discovers, no toggle needed` / `Codex CLI — auto-discovers, no toggle needed`). This replaces the current opaque "Plugin uninstalled" one-liner in `remove.ts` with a structured per-agent report.

## User Stories

### US-001: Install a skill and have it ready to use immediately
**Project**: vskill
**As a** developer using Claude Code
**I want** `vskill install <source>` to install AND enable the skill so it works on my next Claude Code restart
**So that** I do not have to chain `claude plugin install` myself or hand-edit `settings.json`

**Acceptance Criteria**:
- [x] **AC-US1-01**: Running `vskill install anton-abyzov/skill-foo` extracts the SKILL.md to the resolved agent skills directory(s) AND, if the source is a marketplace plugin, calls `claudePluginInstall(<id>, <scope>)` exactly once per scope chosen, so `enabledPlugins[<id>] === true` in the corresponding `settings.json`.
- [x] **AC-US1-02**: When `--no-enable` is passed, `vskill install` performs the filesystem extraction and lockfile update but skips the `claudePluginInstall` call. The skill is on disk, registered in `vskill.lock`, but `enabledPlugins[<id>]` is absent or `false`.
- [x] **AC-US1-03**: `--scope project` writes the plugin enablement into `<projectDir>/.claude/settings.json` (via `claudePluginInstall(id, "project", { cwd })`), and `--scope user` writes to `~/.claude/settings.json`. Default scope when neither flag is set matches the existing `--global` semantics in `add.ts` (project unless `--global`).
- [x] **AC-US1-04**: When the source is NOT a marketplace plugin (e.g., a single-skill GitHub source resolved to a SKILL.md drop), `vskill install` skips the plugin enablement step entirely and prints `Auto-discovered by agents from skills dir — no enable step needed`. The exit code is 0.
- [x] **AC-US1-05**: If `claudePluginInstall` throws (claude CLI missing, or plugin not in marketplace), the filesystem extraction is rolled back (skill files removed, lockfile entry removed) and `vskill install` exits non-zero with a diagnostic naming the failed scope.

### US-002: Enable a previously-installed skill without re-installing
**Project**: vskill
**As a** developer who ran `vskill install --no-enable foo` or `vskill disable foo`
**I want** `vskill enable foo` to flip the skill back on
**So that** I can toggle skills without re-downloading them or hand-editing config

**Acceptance Criteria**:
- [x] **AC-US2-01**: `vskill enable foo` reads `vskill.lock`, locates the entry for `foo`, derives `<pluginId> = <skillName>@<marketplace>`, and calls `claudePluginInstall(<pluginId>, <scope>)`. After the call, `isPluginEnabled(<pluginId>, <opts>)` returns `true`.
- [x] **AC-US2-02**: `vskill enable foo` errors out with exit code 1 and a clear message if `foo` is not in `vskill.lock`. The message points the user to `vskill install foo`.
- [x] **AC-US2-03**: `vskill enable foo` is idempotent: a second invocation when `foo` is already enabled prints `foo already enabled in <scope> scope` and exits 0 without re-invoking the claude CLI.
- [x] **AC-US2-04**: `vskill enable foo --scope project` operates on `<cwd>/.claude/settings.json`; `--scope user` (default) operates on `~/.claude/settings.json`. Both scopes can be enabled independently (a skill can be enabled at user scope and disabled at project scope, or vice versa).
- [x] **AC-US2-05**: `vskill enable foo --dry-run` prints what it WOULD do (target scope, target settings.json path, claude CLI command) and exits 0 without invoking claude.

### US-003: Disable an installed skill without removing it
**Project**: vskill
**As a** developer who wants to silence a skill temporarily
**I want** `vskill disable foo` to remove the `enabledPlugins` entry while keeping all on-disk files intact
**So that** I can re-enable the skill quickly without re-downloading

**Acceptance Criteria**:
- [x] **AC-US3-01**: `vskill disable foo` calls `claudePluginUninstall(<pluginId>, <scope>)`. After the call, `isPluginEnabled(<pluginId>, <opts>)` returns `false` and the skill files at `<localSkillsDir>/<skillName>` and/or `<globalSkillsDir>/<skillName>` STILL exist on disk.
- [x] **AC-US3-02**: `vskill disable foo` does NOT modify `vskill.lock` — the lockfile entry survives so `vskill enable foo` can reverse it.
- [x] **AC-US3-03**: `vskill disable foo` is idempotent: when `foo` is already disabled (or never enabled), prints `foo already disabled in <scope> scope` and exits 0.
- [x] **AC-US3-04**: When the lockfile entry for `foo` lacks a `marketplace` field (i.e., it was installed as a non-marketplace skill that auto-discovers), `vskill disable foo` prints `foo is auto-discovered — no plugin entry to disable. To stop loading, run vskill remove foo.` and exits 0.
- [x] **AC-US3-05**: `vskill disable foo --scope project` only flips the project-scope settings; the user-scope `enabledPlugins[foo@m]` is untouched. Verified via `isPluginEnabled` for both scopes after the call.

### US-004: List installed skills with explicit enabled/disabled status per scope
**Project**: vskill
**As a** developer running `vskill list --installed`
**I want** to see, for every skill in `vskill.lock`, whether it is enabled in user scope, project scope, or auto-discovered (no scope)
**So that** I can audit my Claude Code state without grepping settings.json

**Acceptance Criteria**:
- [x] **AC-US4-01**: `vskill list --installed` prints a table with columns: `Skill | Version | Source | User Scope | Project Scope`. The two scope columns show `enabled`, `disabled`, or `n/a` (the latter for auto-discovered/non-marketplace skills).
- [x] **AC-US4-02**: The user-scope column reads `~/.claude/settings.json` once and the project-scope column reads `<cwd>/.claude/settings.json` once. Neither file is modified.
- [x] **AC-US4-03**: `vskill list --installed --json` outputs a JSON array of `{ name, version, source, enabledUser, enabledProject, autoDiscovered }` objects, suitable for piping into `jq`.
- [x] **AC-US4-04**: When `vskill.lock` does not exist, `vskill list --installed` exits with the same friendly message currently produced by `listSkills` (no crash).

### US-005: Multi-agent surface awareness when installing/enabling
**Project**: vskill
**As a** developer with Claude Code AND Cursor AND Codex CLI installed
**I want** `vskill install` and `vskill enable` to report exactly which agent surfaces received which write
**So that** I am not surprised by "this works in Claude but not Cursor"

**Acceptance Criteria**:
- [x] **AC-US5-01**: After `vskill install foo` succeeds, output contains a per-agent line for every detected agent: `<displayName> (<scope>) — <action>` where action is one of `enabled via claude CLI`, `auto-discovered (no plugin enable needed)`, or `skipped (agent not detected)`.
- [x] **AC-US5-02**: `vskill enable foo` produces the same per-agent report as install, but with action of `enabled` or `already enabled` or `not applicable for this agent`.
- [x] **AC-US5-03**: When the only detected agent is non-Claude (e.g., Cursor only), `vskill enable foo` prints `No agent requires explicit enable — Cursor auto-discovers from .cursor/skills/. Skill is already on disk and live.` and exits 0.
- [x] **AC-US5-04**: Output is suppressed (machine-friendly) when `--json` is passed; instead a JSON object `{ skill, scope, perAgent: [{ id, displayName, action }] }` is emitted to stdout.

### US-006: Reversibility, dry-run, and audit
**Project**: vskill
**As a** cautious developer
**I want** every enable/disable operation to be inspectable in advance and trivially reversible
**So that** I can integrate vskill into automated workflows without fearing irreversible state changes

**Acceptance Criteria**:
- [x] **AC-US6-01**: `--dry-run` is supported on `enable`, `disable`, and `install`. Dry-run prints the exact `claude plugin install/uninstall ...` invocation(s) it would run, the target settings.json path(s), and the lockfile mutation(s), without performing any of them. Exit code 0.
- [x] **AC-US6-02**: `--verbose` (or `-V`) on `enable`/`disable` prints, for every step: the scope, the resolved settings.json path, the resolved claude binary path, and the exit code of the claude CLI subprocess.
- [x] **AC-US6-03**: Running `vskill disable foo` followed by `vskill enable foo` returns `~/.claude/settings.json` to a byte-identical state (modulo whitespace normalisation by claude CLI). Verified by JSON-deep-equality on `enabledPlugins`.
- [x] **AC-US6-04**: All vskill-owned writes (lockfile mutations during install/remove) use the existing tmp-then-rename atomicity in `lockfile/lockfile.ts`. No new direct writes to `~/.claude/settings.json` are introduced.

### US-007: Cleanup and self-heal for stale plugin entries
**Project**: vskill
**As a** developer whose `enabledPlugins` got out of sync (stale entries left behind by a past `rm -rf` or a failed install)
**I want** `vskill cleanup` to detect and fix drift between `vskill.lock` and `enabledPlugins`
**So that** Claude Code does not log warnings about missing plugins on startup

**Acceptance Criteria**:
- [x] **AC-US7-01**: `vskill cleanup` (existing command, extended) calls `purgeStalePlugins({scope:"user"}, lock.skills)` and `purgeStalePlugins({scope:"project", projectDir: cwd}, lock.skills)`, then `claudePluginUninstall` each stale id. The current behaviour in `cleanup.ts` already does part of this — the increment ensures the new `enable`/`disable` flow does not introduce new stale-entry classes.
- [x] **AC-US7-02**: `vskill cleanup --dry-run` lists every stale plugin id (with scope) and the corresponding `claude plugin uninstall ...` invocation it would run, without performing any of them.
- [x] **AC-US7-03**: `vskill cleanup` prints a reconciliation summary: `<N> stale entries removed from user scope, <M> from project scope, <K> in-sync skills left untouched.`
- [x] **AC-US7-04**: A skill that is in `vskill.lock` but missing from `enabledPlugins` (because the user manually disabled it via this increment) is NOT treated as stale — `cleanup` only acts on `enabledPlugins` entries that have no lockfile backing.

## Non-Functional Requirements

- **NFR-001 (Atomicity)**: All vskill-managed JSON writes (lockfile) use tmp-then-rename. No direct writes to `~/.claude/settings.json` from vskill code — settings.json mutations go through `claudePluginInstall` / `claudePluginUninstall` exclusively.
- **NFR-002 (Idempotency)**: Every new command (`enable`, `disable`) produces the same final state when run twice; the second run exits 0 with a clear "already in target state" message and does not re-invoke `claude`.
- **NFR-003 (Performance)**: `vskill list --installed` completes in < 200ms on a lockfile with 50 skills, dominated by two `readFileSync` of `settings.json` files. No network calls.
- **NFR-004 (Cross-platform)**: All path handling uses `node:path` (`join`, `resolve`) and `os.homedir()`, no hardcoded `/` separators. Tests run on darwin and linux in CI; Windows path expectations covered by the existing Windows-aware probes in `agents-registry.ts`.
- **NFR-005 (Backward-compat)**: Existing `vskill install` / `vskill remove` / `vskill list` behaviour is unchanged unless the new flags (`--no-enable`, `--installed`, `--scope`, `--dry-run`) are passed. Lockfile schema (`SkillLockEntry`) is unchanged.
- **NFR-006 (Test coverage)**: Unit + integration tests for the new commands hit ≥ 90% line coverage. The claude CLI subprocess is mocked via dependency injection or `vi.mock` in tests.
- **NFR-007 (Error clarity)**: Every error path names the offending scope, the resolved settings.json path, and the underlying error message from the claude CLI subprocess. No `process.exit` without a diagnostic line.

## Functional Requirements

- **FR-001**: New command `vskill enable <skill-name>` registered in `src/index.ts` Commander program.
- **FR-002**: New command `vskill disable <skill-name>` registered in `src/index.ts` Commander program.
- **FR-003**: New flag `--no-enable` on `vskill install` / `vskill add`.
- **FR-004**: New flag `--installed` on `vskill list` (joined with existing `--json`).
- **FR-005**: New `--dry-run` and `--verbose` flags on `enable`, `disable`, `install`.
- **FR-006**: New helper module `src/lib/skill-lifecycle.ts` (or co-located in `src/commands/enable.ts`) that consumes `vskill.lock`, resolves the plugin id, picks the scope, and invokes `claudePluginInstall` / `claudePluginUninstall`.
- **FR-007**: Per-agent reporting helper that walks `detectInstalledAgents()` and classifies each as `claude-code-style (uses enabledPlugins)`, `auto-discover (just reads skills dir)`, or `not detected`. Used by `enable`, `disable`, `install`, and `list --installed`.

## Out of Scope

- vskill-platform marketing site changes (separate increment).
- Cloud-side skill provisioning, OAuth flows, billing.
- Auto-updating skills (covered by 0708-skill-update-push-pipeline).
- New skill manifest format or lockfile schema migration (the existing `SkillLockEntry` schema covers all needs).
- Per-agent enable/disable for non-Claude agents that do not have a `settings.json`-equivalent (Cursor, Codex CLI, Cline, etc. auto-discover from their `localSkillsDir`; toggling is achieved by `vskill remove` or by deleting the directory). This is documented but not implemented.
- A GUI for enable/disable inside Skill Studio (potential follow-up).
