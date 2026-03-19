# Architecture Plan: 0571-fix-init-multirepo-wiring

## Summary

Fix the `specweave init` multi-repo flow so that selecting "multiple repos" during init actually wires into the real infrastructure (`multiProject.enabled`, `repositories/` directory) instead of setting dead config keys. Reorder the post-scaffold block so it fires before git init, and delete ~2400 lines of dead code.

## Relevant ADRs

- **ADR-0138** (Init Command Modular Architecture) -- defines the helper module boundaries in `src/cli/helpers/init/`. All edits follow the existing orchestrator pattern.
- **ADR-0142** (Umbrella Multi-Repo Support) -- defines `multiProject.enabled` and `umbrella.childRepos` as the canonical config keys. This increment wires init to `multiProject.enabled` (the simpler of the two, appropriate for "I will have multiple repos" without yet knowing which).
- **ADR-0156** (Multi-Repo Init UX Architecture) -- confirms root-level cloning and modular helpers.
- **ADR-0157** (Root-Level Repository Structure) -- repos clone at root level, not under `services/`.

## Architecture Decisions

### AD-1: Reorder init.ts so post-scaffold fires before git init

**Problem**: The post-scaffold block (lines 433-467 in init.ts) checks `!hasGit && !hasRepos` before showing the repo-connect prompt. But git init runs at lines 352-359, creating `.git` before the post-scaffold check. This means `hasGit` is always true for greenfield projects, making the entire post-scaffold block dead code.

**Decision**: Move the post-scaffold block (lines 431-468) to execute BEFORE the git init block (lines 351-360). The post-scaffold prompt asks how the user wants to set up code (existing, clone repos, start from scratch) -- none of these operations require `.git` to exist. If repos are cloned, they bring their own `.git` directories. The parent directory's git init should happen after so it captures the full initial state including cloned repos.

**Impact**: Low risk. The post-scaffold block uses `promptProjectSetup()`, `promptRepoUrls()`, and `cloneReposIntoWorkspace()` -- none depend on `.git` existing. The `scanUmbrellaRepos()` re-scan inside the block reads the filesystem, not git.

**Revised flow order**:
1. Create directory structure + copy templates (lines 330-341)
2. Non-Claude adapter install (lines 343-349)
3. **Post-scaffold repo-connect prompt** (moved up)
4. Git init + initial commit (captures cloned repos)
5. Config file creation + batch updates (lines 377-429)

### AD-2: Wire multi-repo question to `multiProject.enabled`

**Problem**: When the user answers "yes" to the multi-repo question (line 312), init sets `config.repository.structure = 'multiple'` (line 421). This key is not read by any production code. The real infrastructure reads `multiProject.enabled` (used by `multi-project-detector.ts`, `structure-level-detector.ts`, `project-resolution.ts`, `sync-profile-helpers.ts`).

**Decision**: Replace the dead config write with:

```typescript
if (isMultiRepo) {
  config.multiProject = { enabled: true };
}
```

Also create `repositories/` directory when multi-repo is selected, matching what `resolve-structure.ts` does for the deferred case. Remove `config.project.structureDeferred` (no longer set by init since v1.0.415, confirmed by resolve-structure.ts deprecation note).

Do NOT set `config.umbrella.enabled` without `childRepos` -- the umbrella config requires actual repo entries (per ADR-0142). `multiProject.enabled` without `umbrella` is the correct state for "I plan to have multiple repos but haven't cloned any yet."

**Config diff**:
```
// Before (dead)
config.repository = { ...config.repository, structure: 'multiple' };
config.project = { ...config.project, structureDeferred: false };

// After (wired)
config.multiProject = { enabled: true };
```

### AD-3: Post-scaffold handles multi-repo context naturally

**Problem**: Currently `repo-connect.ts` offers 3 options: "I have existing code here", "Clone GitHub repositories", "Starting from scratch". The multi-repo question is asked separately earlier in init.ts (line 312) and has no follow-through because the post-scaffold block never fires (AD-1 bug).

**Decision**: No new prompt option needed in repo-connect. Once AD-1 unblocks the post-scaffold block, the existing "Clone GitHub repositories" path already handles multi-repo correctly via `cloneReposIntoWorkspace()` which clones into `repositories/{org}/{name}/`. After cloning, the existing re-scan with `scanUmbrellaRepos()` wires umbrella config (code already exists at lines 452-462).

The `isMultiRepo` flag is passed through to the post-scaffold context so the prompt can adjust messaging if needed, but the core flow is unchanged.

### AD-4: Optional sync-setup chain after multi-repo setup

**Problem**: After multi-repo setup, users need to connect external tools (GitHub Issues, JIRA, ADO) to complete the workflow. Currently next-steps shows `specweave sync-setup` as step 2, but there is no in-flow prompt.

**Decision**: After the multi-repo config is written, offer a single confirm prompt:

```
Would you like to connect external tools now? (GitHub Issues, JIRA, ADO)
```

If accepted, dynamically import and call `syncSetupCommand()` from `src/cli/commands/sync-setup.ts`. If declined, the existing next-steps display already shows the command. This is non-blocking -- failure or cancellation does not affect init success.

Implementation: Add the prompt in init.ts after the config batch-update block, gated on `isMultiRepo`. Keep it minimal -- a single `confirm()` call.

### AD-5: Delete ~2400 lines of dead code

**File: `repository-setup.ts` (1921 lines) -- DELETE**

Confirmed zero production imports. The two grep hits in `selection-strategy.ts:893` and `ado-repo-cloning.ts:16` are JSDoc comments referencing the file by name, not import statements. The barrel export `index.ts` does not export anything from `repository-setup.ts`. This file contains the pre-v1.0.415 repository hosting setup flow (GitHub/Bitbucket/ADO multi-repo wizard) that was replaced by `sync-setup` and `repo-connect`.

**File: `repository-setup.test.ts` -- DELETE**

Test file for dead code. Located at `tests/unit/cli/helpers/init/repository-setup.test.ts`.

**File: `resolve-structure.ts` (109 lines) -- REPLACE with deprecation stub**

Already marked `@deprecated` since v1.0.415. The function only operates on `project.structureDeferred` which is no longer set by init. Replace with a stub that:
1. Logs a deprecation warning
2. Returns `{ success: false, message: 'Deprecated since v1.0.415. Use specweave migrate-to-umbrella instead.', previouslyDeferred: false }`
3. Keeps the exported type and function signature for backward compatibility

This avoids breaking any CLI command registration or external callers while reducing the module to ~25 lines.

### AD-6: Update next-steps for multi-repo context

**Problem**: `showNextSteps()` currently hides the `migrate-to-umbrella` line when `context.isUmbrella` is true. When multi-repo is selected without cloning repos, `isUmbrella` is false (no repos discovered), so the line still shows even though the user already chose multi-repo.

**Decision**: Add `isMultiRepo` to `NextStepsContext`. When `isMultiRepo || isUmbrella`, hide the `migrate-to-umbrella` step.

**Change in `types.ts`**:
```typescript
export interface NextStepsContext {
  isUmbrella?: boolean;
  isMultiRepo?: boolean;  // NEW
  misplacedRepos?: string[];
}
```

**Change in `next-steps.ts`**:
```typescript
if (!context.isUmbrella && !context.isMultiRepo) {
  console.log(`   ${stepNumber + 2}. ...migrate-to-umbrella...`);
}
```

## Files to Modify

| File | Action | Lines Changed (est.) |
|------|--------|---------------------|
| `src/cli/commands/init.ts` | EDIT: reorder post-scaffold before git init, wire `multiProject.enabled`, add sync-setup prompt, remove dead `structure: 'multiple'` write | ~40 |
| `src/cli/helpers/init/next-steps.ts` | EDIT: check `isMultiRepo` in conditional | ~2 |
| `src/cli/helpers/init/types.ts` | EDIT: add `isMultiRepo` to `NextStepsContext` | ~1 |
| `src/cli/helpers/init/repository-setup.ts` | DELETE (1921 lines) | -1921 |
| `src/cli/commands/resolve-structure.ts` | REPLACE with deprecation stub | -80 (net) |
| `tests/unit/cli/helpers/init/repository-setup.test.ts` | DELETE | -N |
| `tests/unit/cli/commands/init-multirepo.test.ts` | CREATE | ~150 |

All paths are relative to `repositories/anton-abyzov/specweave/`.

**Net code change**: approximately -1800 lines (deletions far exceed additions).

## Test Strategy

New test file `tests/unit/cli/commands/init-multirepo.test.ts` using the existing ESM mocking pattern (`vi.hoisted()` + `vi.mock()`).

### Test Cases

**TC-001: Multi-repo writes multiProject.enabled**
- Given: user answers `isMultiRepo = true`
- When: init completes config batch-update
- Then: config.json contains `multiProject: { enabled: true }`
- Then: config.json does NOT contain `repository.structure`

**TC-002: Multi-repo creates repositories/ directory**
- Given: user answers `isMultiRepo = true`
- When: init completes
- Then: `repositories/` directory exists under project root

**TC-003: Post-scaffold fires for greenfield projects**
- Given: new project (no `.git`, no `repositories/`)
- When: init runs to post-scaffold step
- Then: `promptProjectSetup()` is called (not skipped)

**TC-004: Post-scaffold skipped for existing projects**
- Given: `continueExisting = true`
- When: init runs
- Then: `promptProjectSetup()` is NOT called

**TC-005: Sync-setup offered after multi-repo**
- Given: `isMultiRepo = true`
- When: post-scaffold completes
- Then: confirm prompt for sync-setup is shown

**TC-006: Sync-setup skipped when declined**
- Given: `isMultiRepo = true`, user declines sync-setup
- When: init continues
- Then: `syncSetupCommand()` is NOT called, init completes normally

**TC-007: Next-steps hides migrate-to-umbrella for multi-repo**
- Given: `isMultiRepo = true`, `isUmbrella = false`
- When: `showNextSteps()` runs
- Then: output does NOT contain `migrate-to-umbrella`

**TC-008: resolve-structure returns deprecation**
- Given: calling `resolveStructureCommand()`
- When: function executes
- Then: returns `{ success: false, message: containing 'deprecated' }`

## Component Boundaries

```
init.ts (orchestrator)
  |
  +--> repo-connect.ts (post-scaffold prompts + cloning)
  |      - No changes to module API
  |      - Called earlier in flow (AD-1)
  |
  +--> config batch-update block (inline in init.ts)
  |      - Writes multiProject.enabled instead of repository.structure
  |
  +--> sync-setup.ts (optional chain)
  |      - Dynamic import, fire-and-forget
  |
  +--> next-steps.ts (display)
  |      - Reads new isMultiRepo context flag
  |
  +--> types.ts
         - NextStepsContext gains isMultiRepo field
```

## Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Reordering breaks non-greenfield flows | Medium | Low | `continueExisting` and `isCI` guards remain unchanged; both paths tested |
| External callers depend on `repository.structure` | Low | Very Low | Grep confirms zero reads of this key outside init.ts |
| resolve-structure stub breaks CLI registration | Low | Low | Keep function signature and types identical |
| Tests miss edge case in post-scaffold timing | Medium | Medium | Test both greenfield and brownfield paths explicitly |

## Delegation

Implementation is a single-domain task (CLI/Node.js). Use `sw:architect` for implementation -- no additional domain plugins needed.
