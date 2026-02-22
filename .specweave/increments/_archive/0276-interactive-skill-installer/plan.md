# Implementation Plan: Interactive Skill Installation Wizard

## Overview

Add interactive prompts to the `vskill add` / `vskill install` command for multi-skill repos. The implementation introduces a zero-dependency prompt module (Node.js `readline`), a canonical `.agents/skills/` directory with symlink fan-out, and a `--yes` flag for non-interactive CI usage. The existing single-skill and non-interactive flows remain completely unchanged.

## Architecture

### Components

```
src/
  utils/
    prompts.ts          # NEW - readline-based interactive prompts
  commands/
    add.ts              # MODIFIED - integrate interactive wizard flow
  installer/
    canonical.ts        # NEW - canonical dir + symlink/copy logic
```

### Component Responsibilities

1. **`src/utils/prompts.ts`** -- Interactive prompt primitives:
   - `promptCheckboxList()`: Multi-select with numbered toggle and "all" option
   - `promptChoice()`: Single choice (numbered list, user types number)
   - `promptConfirm()`: Y/n confirmation
   - `isTTY()`: Detect interactive terminal

2. **`src/installer/canonical.ts`** -- Canonical directory + install methods:
   - `installSymlink()`: Copy to `.agents/skills/<name>/`, create relative symlinks to each agent dir
   - `installCopy()`: Copy directly to each agent's skills directory
   - `ensureCanonicalDir()`: Create `.agents/skills/` if not present

3. **`src/commands/add.ts`** (modified) -- Orchestration:
   - After skill discovery + security scan, enters interactive wizard if multiple skills and TTY
   - Calls prompt functions for skill selection, agent selection, scope, method
   - Delegates to canonical installer or existing direct-copy logic

### Data Flow

```
vskill add owner/repo
  |
  v
Parse source, discover skills (existing)
  |
  v
Security scan each skill (existing)
  |
  v
Multi-skill detected? ----no----> Single-skill install (existing path, unchanged)
  |
  yes
  v
Is TTY and no --yes? ----no----> Use defaults (all skills, all agents, project, symlink)
  |
  yes
  v
Step 1: Skill selection prompt (checkboxList)
  |
  v
Step 2: Agent target prompt (checkboxList)
  |
  v
Step 3: Scope prompt (choice: project/global)
  |
  v
Step 4: Method prompt (choice: symlink/copy)
  |
  v
Step 5: Summary + confirmation
  |
  v
Install selected skills to selected agents via chosen method
  |
  v
Update lockfile
```

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Runtime**: Node.js >= 20
- **Prompt library**: `node:readline` (built-in, zero dependencies)
- **File operations**: `node:fs` (symlink, copy, mkdir)
- **Testing**: Vitest

**Architecture Decisions**:

- **Zero dependencies for prompts**: The existing project has only `commander` and `simple-git` as runtime deps. Adding `@clack/prompts` or `inquirer` would increase bundle size and attack surface. Node.js `readline` provides everything needed.
- **Canonical directory pattern**: Matches `npx skills` behavior. `.agents/skills/` is the universal standard directory. Symlinks from agent-specific dirs avoid file duplication and ensure single-point updates.
- **Symlink as default**: Symlink mode is recommended because it deduplicates content across agents and allows in-place updates. Copy mode exists as fallback for environments where symlinks fail (some Windows configurations).

## Implementation Phases

### Phase 1: Prompt Utilities
- Create `src/utils/prompts.ts` with `promptCheckboxList`, `promptChoice`, `promptConfirm`, `isTTY`
- Unit tests with mocked readline interface

### Phase 2: Canonical Installer
- Create `src/installer/canonical.ts` with `installSymlink` and `installCopy`
- Ensure canonical dir creation (`.agents/skills/`)
- Relative symlink calculation
- Symlink fallback to copy on failure
- Unit tests for both install modes

### Phase 3: Interactive Wizard Integration
- Modify `src/commands/add.ts` to detect multi-skill repos
- Add `--yes` / `-y` flag to commander definition in `src/index.ts`
- Wire up interactive prompts for skill, agent, scope, method selection
- Add pre-install summary display
- Non-TTY auto-detection (behave as `--yes`)

### Phase 4: Testing and Polish
- Integration tests for the full wizard flow (mocked stdin)
- Verify existing single-skill installs are unchanged
- Update `--help` text
- Update README if needed

## Testing Strategy

- **Unit tests**: Each prompt function tested with mocked readline
- **Unit tests**: Canonical installer tested with temp directories (symlink + copy)
- **Integration tests**: Full wizard flow with simulated user input
- **Regression tests**: Ensure existing `addCommand` behavior unchanged for single-skill repos
- **TTY detection**: Tests for non-TTY behavior (CI mode)

## Technical Challenges

### Challenge 1: Readline prompt UX in terminal
**Solution**: Use raw mode for keypress detection if needed, but simple numbered input (type a number, press Enter) is more portable and easier to test. The `npx skills` installer uses `@clack/prompts` for fancy UI, but numbered input achieves the same functional result with zero dependencies.
**Risk**: Low -- Node.js readline is stable and well-documented.

### Challenge 2: Relative symlink calculation
**Solution**: Use `path.relative()` to compute the relative path from the agent's skills directory to the canonical `.agents/skills/<name>/` directory. This ensures symlinks work regardless of absolute paths.
**Risk**: Low -- path.relative handles edge cases. Fallback to copy if symlink fails.

### Challenge 3: ESM import extensions
**Solution**: All new files follow the existing pattern -- imports use `.js` extensions as required by `--moduleResolution nodenext`.
**Risk**: None -- established pattern in the codebase.
