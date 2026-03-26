# Implementation Plan: Skip native plugin install for Claude

## Overview

Add `isSwPluginInstalledNatively()` to `plugin-copier.ts` that runs `claude plugin list` and parses output. Add a check in `init.ts` before `installAllPlugins()` to skip when native plugin is detected.

## Architecture

### Components
- **isSwPluginInstalledNatively()**: New utility in `plugin-copier.ts` — runs `claude plugin list`, parses output for `sw@specweave` with enabled status
- **init.ts skip branch**: New conditional between `continueExisting` and `installAllPlugins()` calls

### Key Design Decisions
- **CLI over file parsing**: Uses `claude plugin list` instead of reading `installed_plugins.json` — cross-platform, won't break on internal format changes
- **Placed in plugin-copier.ts**: Canonical home for plugin installation concerns, already imports `execFileNoThrowSync`
- **Minimal change**: Only adds a new branch in the existing if/else, no restructuring

## Files to Modify

1. `src/utils/plugin-copier.ts` — Add `isSwPluginInstalledNatively()` export
2. `src/cli/commands/init.ts` — Add skip branch at lines 558-570

## Testing Strategy

TDD with Vitest. New test file for the utility function, additions to existing test files for integration.
