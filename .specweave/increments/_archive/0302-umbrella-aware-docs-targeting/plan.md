# Implementation Plan: Umbrella-Aware Project Targeting for Docs Command

## Overview

Add `--project <repo-id>` support to all `specweave docs` subcommands so that umbrella projects can target individual child repos. Refactor the existing `docs.ts` to extract a shared `resolveDocsRoot()` function that handles umbrella detection and project resolution. Update the `/sw:docs` SKILL.md to include umbrella-aware search.

## Architecture

### Components

1. **`resolveDocsRoot()`** (new, in `src/cli/commands/docs.ts`): Shared function that resolves the effective project root based on umbrella config and `--project` flag. All docs subcommands call this instead of using `process.cwd()` directly.

2. **`getUmbrellaConfig()`** (extract from existing `getUmbrellaChildRepoDocs()`): Parse umbrella config and return the enabled flag + child repos array. Reused by both `resolveDocsRoot()` and the existing child repo display logic.

3. **CLI registration** (in `bin/specweave.js`): Add `--project <id>` option to all `docs` subcommands.

4. **SKILL.md update**: Add umbrella-aware search paths to the `/sw:docs` skill definition.

### Data Flow

```
User runs: specweave docs preview --project vskill --scope internal

1. bin/specweave.js passes { project: "vskill", scope: "internal" } to docsPreviewCommand()
2. docsPreviewCommand() calls resolveDocsRoot({ project: "vskill" })
3. resolveDocsRoot():
   a. Reads .specweave/config.json from cwd
   b. Finds umbrella.childRepos[].id === "vskill"
   c. Returns { projectRoot: "repositories/anton-abyzov/vskill", repoName: "vskill" }
4. docsPreviewCommand() uses resolved projectRoot for all paths
5. Preview launches from vskill/.specweave/docs/internal/
```

## Technology Stack

- **Language**: TypeScript (existing)
- **Testing**: Vitest (existing)
- **Patterns**: ESM with `.js` extensions, `vi.hoisted()` + `vi.mock()` for test mocking

## Implementation Phases

### Phase 1: Core Resolution Logic (US-001)

1. Extract `getUmbrellaConfig()` from existing code
2. Create `resolveDocsRoot()` function with `--project` support
3. Add `project` field to all Options interfaces
4. Refactor all 5 docs subcommands to use `resolveDocsRoot()`
5. Register `--project <id>` in `bin/specweave.js`

### Phase 2: Guidance & UX (US-002)

1. Add umbrella detection notice when no `--project` given
2. Show child repo list with doc counts
3. Handle edge cases: no umbrella docs, invalid project ID

### Phase 3: Skill Update (US-003)

1. Update SKILL.md with umbrella-aware search paths
2. Add child repo doc listing to dashboard output

## Testing Strategy

- **Unit tests**: Add tests to `tests/unit/cli/commands/docs.test.ts` for:
  - `resolveDocsRoot()` with umbrella config + valid project
  - `resolveDocsRoot()` with umbrella config + invalid project
  - `resolveDocsRoot()` with no umbrella config
  - Each subcommand with `--project` option
  - Guidance output when umbrella detected but no `--project`
- **TDD mode**: RED -> GREEN -> REFACTOR per config

## Technical Challenges

### Challenge 1: Config reading is sync but needs to be reusable
**Solution**: Extract `getUmbrellaConfig()` as a sync function (config.json reads are already sync via `fs.readFileSync`). Return a typed interface for the umbrella config.

### Challenge 2: Avoid breaking existing behavior
**Solution**: `resolveDocsRoot()` returns cwd-based root when no umbrella config exists or `--project` is not given, preserving all existing behavior.
