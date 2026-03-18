# 0573: Fix sw@specweave Silent Corruption

## Problem

`sw@specweave` gets silently set to `false` in `~/.claude/settings.json`, disabling all SpecWeave skills. Root causes:

1. `claude plugin install/uninstall` corrupts `enabledPlugins` object as a side effect
2. Claude Code updates wipe `installed_plugins.json`, causing settings sync corruption
3. Read-modify-write race conditions (no file locking on settings.json)
4. No session-start recovery mechanism
5. Defensive code in `migrateUserLevelPlugins()` is dead (never called)

## User Stories

### US-001: Session-Start Auto-Recovery
As a SpecWeave user, I want corrupted `sw@specweave` to be automatically repaired on session start, so that skills are always available.

- [x] AC-US1-01: SessionStart hook checks `sw@specweave` state in settings.json
- [x] AC-US1-02: If `sw@specweave` is `false` or missing, it is set to `true`
- [x] AC-US1-03: User receives a system message when corruption is detected and repaired
- [x] AC-US1-04: No-op when `sw@specweave` is already `true` (fast path)

### US-002: Refresh-Plugins Recovery
As a SpecWeave user, I want `specweave refresh-plugins` to restore `sw@specweave` after plugin operations, so that uninstall/install side effects are repaired.

- [x] AC-US2-01: `refresh-plugins` calls `migrateUserLevelPlugins` to activate defensive recovery
- [x] AC-US2-02: `sw@specweave` is restored to `true` after any plugin uninstall corruption

## Acceptance Criteria

- [x] AC-US1-01: SessionStart hook checks sw@specweave state
- [x] AC-US1-02: Auto-repair when false or missing
- [x] AC-US1-03: System message on repair
- [x] AC-US1-04: No-op fast path
- [x] AC-US2-01: refresh-plugins wires migrateUserLevelPlugins
- [x] AC-US2-02: sw@specweave restored after corruption
