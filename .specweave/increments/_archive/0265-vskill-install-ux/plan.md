# Implementation Plan: vskill install UX: smart directory resolution and agent selection

## Overview

Two surgical changes to `src/commands/add.ts` and `src/index.ts`, supported by two new utility modules. No architectural changes -- both features are additive and backward-compatible.

## Architecture

### New Modules

- **`src/utils/project-root.ts`**: `findProjectRoot(startDir)` -- walks up from `startDir` looking for project markers (`.git/`, `package.json`, etc.). Returns absolute path or `null`.
- **`src/utils/agent-filter.ts`**: `filterAgents(agents, requestedIds?)` -- returns subset of agents matching the requested IDs, or all agents if no filter. Throws descriptive error for unknown IDs.

### Modified Modules

- **`src/index.ts`**: Add `--agent <id>` option (repeatable) and `--cwd` flag to the `install` command definition. Pass to `addCommand`.
- **`src/commands/add.ts`**:
  - `AddOptions` interface gains `agent?: string[]` and `useCwd?: boolean`.
  - Before computing `baseDir`, call `findProjectRoot(process.cwd())` unless `--cwd` or `--global` is set.
  - After `detectInstalledAgents()`, call `filterAgents()` if `--agent` was provided.
  - Print resolved project root in output.

### Data Flow

```
CLI args (--agent, --cwd)
  |
  v
addCommand(source, opts)
  |
  +-> resolve install dir:
  |     opts.global?  -> agent.globalSkillsDir (unchanged)
  |     opts.useCwd?  -> process.cwd() (explicit fallback)
  |     default       -> findProjectRoot(cwd) || cwd (with warning)
  |
  +-> detect + filter agents:
        detectInstalledAgents()
          |-> filterAgents(agents, opts.agent)
```

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Testing**: Vitest
- **Dependencies**: None new (uses `node:fs`, `node:path`)

**Architecture Decisions**:
- **Walk-up strategy over config file**: Simpler, works immediately, no user setup required. `.git/` is the strongest signal since almost all projects use git.
- **`--agent` as repeatable option over comma-separated**: Commander supports `.option('--agent <id>', '...', collect, [])` pattern natively. More composable.
- **No interactive selection**: Keeps the CLI scriptable and CI-friendly. Interactive selection is out of scope.

## Implementation Phases

### Phase 1: Project Root Discovery
1. Create `src/utils/project-root.ts` with `findProjectRoot()`
2. Create `src/utils/project-root.test.ts` with comprehensive tests
3. Wire into `addCommand` -- use resolved root for local installs

### Phase 2: Agent Selection
4. Create `src/utils/agent-filter.ts` with `filterAgents()`
5. Create `src/utils/agent-filter.test.ts`
6. Add `--agent` option to CLI in `src/index.ts`
7. Wire into `addCommand` -- filter agents before install loop

### Phase 3: Integration
8. Update `add.test.ts` with integration-level tests
9. Verify existing tests pass unchanged

## Testing Strategy

- **Unit tests**: `project-root.test.ts` and `agent-filter.test.ts` for the utility functions
- **Integration tests**: Updated `add.test.ts` to verify the new options flow through correctly
- **TDD**: RED -> GREEN -> REFACTOR for each utility

## Technical Challenges

### Challenge 1: Mocking filesystem for project root tests
**Solution**: Use `vi.mock("node:fs")` to mock `existsSync` with path-based logic simulating directory trees. Same pattern already used in `add.test.ts`.
**Risk**: Low -- well-established pattern in this codebase.

### Challenge 2: Commander repeatable options
**Solution**: Use Commander's `.option('--agent <id>', 'desc', collect, [])` pattern or process the option post-parse.
**Risk**: Low -- Commander supports this natively.
