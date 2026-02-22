# Implementation Plan: SpecWeave Doctor Command - Installation Health Scanner

## Overview

Add an `InstallationHealthChecker` to the existing doctor module, register it in the checker pipeline, and create a `/sw:doctor` skill. All new logic lives in one new checker file plus one new skill file. The existing doctor infrastructure (types, orchestrator, formatter, CLI command) needs only minimal wiring changes.

## Architecture

### Components
- **InstallationHealthChecker** (`src/core/doctor/checkers/installation-health-checker.ts`): New `HealthChecker` implementation with 4 check methods: `checkGhostCommands()`, `checkStaleCacheDirs()`, `checkLockfileIntegrity()`, `checkNamespacePollution()`
- **Doctor orchestrator** (`src/core/doctor/doctor.ts`): Add `InstallationHealthChecker` to the checkers array and extend `determineFix()` for installation health issues
- **Doctor index** (`src/core/doctor/index.ts`): Re-export `InstallationHealthChecker`
- **/sw:doctor skill** (`plugins/specweave/skills/doctor/SKILL.md`): New skill file invoking `specweave doctor`

### Data Flow
```
specweave doctor
  -> runDoctor()
    -> [existing 7 checkers]
    -> InstallationHealthChecker.check(projectRoot, options)
      -> checkGhostCommands(commandsDir, options.fix)
      -> checkStaleCacheDirs(cacheDir, installedPlugins, options.fix)
      -> checkLockfileIntegrity(projectRoot, commandsDir)
      -> checkNamespacePollution(commandsDir, options.fix)
    -> CategoryResult { category: "Installation Health", checks: [...] }
  -> formatDoctorReport()
```

### Key Paths
- `~/.claude/commands/` - where slash commands live (scan target for ghosts/pollution)
- `~/.claude/plugins/cache/` - plugin cache (scan target for stale dirs)
- `~/.claude/plugins/installed_plugins.json` - installed plugins manifest
- `<projectRoot>/vskill.lock` - lockfile with skill SHAs

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Dependencies**: Only Node.js built-ins (`fs`, `path`, `os`, `crypto`). Reuse `shouldSkipFromCommands()`, `computePluginHash()`, `readLockfile()` from `plugin-copier.ts`
- **Testing**: Vitest with temp directories (never touch real `~/.claude/`)

**Architecture Decisions**:
- **Single new file for all checks**: All 4 installation health checks belong together conceptually and share the same scanning context (`~/.claude/` paths). A single checker class keeps the doctor pipeline clean (one more entry in the array) while the internal methods are well-separated.
- **Reuse `shouldSkipFromCommands()`**: The filter logic already defines exactly which `.md` files are "ghost commands." Reusing it ensures detection and prevention use the same rules -- no drift possible.
- **Conservative `--fix`**: Only delete files that are unambiguously wrong (ghost .md files, temp_local_* dirs, namespace pollution). Never auto-delete cache dirs that might belong to other plugins. Never auto-run `specweave refresh-plugins` (suggest only).
- **No new dependencies**: The checker uses only Node.js built-ins and existing utility functions.

## Implementation Phases

### Phase 1: Core Checker (US-001, US-002, US-003)
1. Create `InstallationHealthChecker` class with ghost command detection, stale cache detection, and lockfile integrity checks
2. Wire into `doctor.ts` orchestrator
3. Unit tests for all 3 check methods

### Phase 2: Namespace Pollution + Skill (US-004, US-005)
1. Add namespace pollution detection using `shouldSkipFromCommands()`
2. Create `/sw:doctor` skill SKILL.md
3. Unit tests for pollution detection

### Phase 3: Integration & Fix Mode
1. Test `--fix` mode for each remediable issue type
2. Verify idempotency of fixes
3. Manual testing of `/sw:doctor` skill in Claude Code

## Testing Strategy

- **Unit tests**: `tests/unit/core/doctor/checkers/installation-health-checker.test.ts`
  - Each check method tested with: clean state (pass), issue present (warn/fail), fix mode (remediation)
  - Use `fs.mkdtempSync()` for isolated temp directories simulating `~/.claude/` structure
  - Never touch the real `~/.claude/` directory
- **Test for CLI command**: Verify `InstallationHealthChecker` appears in doctor output
- **Coverage target**: >90% for the new checker

## Technical Challenges

### Challenge 1: Safe Home Directory Scanning
**Problem**: The checker needs to read `~/.claude/` but tests must not touch the real directory.
**Solution**: Accept `commandsDir` and `cacheDir` as constructor parameters with defaults to `~/.claude/commands/` and `~/.claude/plugins/cache/`. Tests inject temp paths.

### Challenge 2: Cross-Platform Path Handling
**Problem**: `~/.claude/` expands differently on Windows vs Unix.
**Solution**: Use `os.homedir()` + `path.join()` consistently (same pattern as existing `PluginsChecker`).

### Challenge 3: `installed_plugins.json` Format Stability
**Problem**: This is Claude Code's internal file; its format could change.
**Solution**: Parse defensively with try/catch. If unreadable, skip the stale cache check with status "skip" rather than failing.
