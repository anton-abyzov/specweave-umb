# Implementation Plan: Complete Uninstall Support

## Overview

Add three levels of uninstall support using existing infrastructure (lockfile, agent registry, git-hooks-installer, instruction-file-merger).

## Architecture

### Components
- **`vskill remove`**: New CLI command in vskill — removes single skill from all agents
- **`specweave uninstall`**: New CLI command in specweave — full project cleanup
- **`stripSwSections()`**: New utility in instruction-file-merger.ts — strips SW markers from CLAUDE.md/AGENTS.md
- **preuninstall.cjs**: Standalone lifecycle scripts for npm uninstall cleanup

### Reused Infrastructure
- `removeSkillFromLock()`, `readLockfile()` — vskill lockfile module
- `detectInstalledAgents()`, `AGENTS_REGISTRY` — vskill agent registry
- `uninstallGitHooks()`, `areGitHooksInstalled()` — specweave git-hooks-installer
- `parseFile()` — specweave instruction-file-merger (private, used by new `stripSwSections()`)
- `resolveTilde()` — vskill path utilities

## Implementation Phases

### Phase 1: stripSwSections utility
Add `stripSwSections(content: string): string | null` to instruction-file-merger.ts.
Uses existing `parseFile()` to extract user segments, returns null if no user content.

### Phase 2: vskill remove command
New `src/commands/remove.ts` + registration in `src/index.ts`.
Pattern mirrors `add.ts`: detect agents → iterate dirs → delete → update lockfile → summary.

### Phase 3: specweave uninstall command
New `src/cli/commands/uninstall.ts` + registration in `bin/specweave.js`.
Orchestrates: discovery → confirm → delete .specweave/ → strip instruction files → unhook git → remove skills → delete lockfile.

### Phase 4: npm preuninstall scripts
Standalone `.cjs` files in `scripts/` for both packages. Warn about remaining artifacts.

## Files

### vskill repo (repositories/anton-abyzov/vskill/)
| File | Action |
|------|--------|
| `src/commands/remove.ts` | NEW |
| `src/commands/remove.test.ts` | NEW |
| `src/index.ts` | EDIT — register command |
| `scripts/preuninstall.cjs` | NEW |
| `package.json` | EDIT — add preuninstall script |

### specweave repo (repositories/anton-abyzov/specweave/)
| File | Action |
|------|--------|
| `src/cli/commands/uninstall.ts` | NEW |
| `src/cli/commands/uninstall.test.ts` | NEW |
| `src/cli/helpers/init/instruction-file-merger.ts` | EDIT — add stripSwSections |
| `src/cli/helpers/init/instruction-file-merger.test.ts` | EDIT — add tests |
| `bin/specweave.js` | EDIT — register command |
| `scripts/preuninstall.cjs` | NEW |
| `package.json` | EDIT — add preuninstall script |
