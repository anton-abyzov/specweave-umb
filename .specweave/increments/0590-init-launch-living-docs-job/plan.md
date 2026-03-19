# Implementation Plan: Launch Living Docs Builder as Background Job from Init

## Overview

Wire `launchLivingDocsJob()` into `initCommand()` so that `specweave init` launches the living docs builder as a background job immediately after config.json creation. This is a ~20-line change to a single file (`src/cli/commands/init.ts`) using three existing, already-exported APIs.

## Architecture

### Existing Components (no changes)

| Component | Location | Role |
|-----------|----------|------|
| `launchLivingDocsJob()` | `src/core/background/job-launcher.ts:404` | Spawns detached background worker, returns `LaunchResult` |
| `displayJobScheduled()` | `src/cli/helpers/init/living-docs-preflight.ts:549` | Prints job ID, estimated duration, and monitor instructions |
| `estimateDuration()` | `src/cli/helpers/init/living-docs-preflight.ts:220` | Returns human-readable duration string based on file count + depth |
| `LivingDocsUserInputs` | `src/core/background/types.ts:131` | Input shape: `additionalSources`, `priorityAreas`, `knownPainPoints`, `analysisDepth` |

### Modified Component

| Component | Location | Change |
|-----------|----------|--------|
| `initCommand()` | `src/cli/commands/init.ts` | Add ~20 lines after line 454 (config.json write) to launch the job |

### No New Files

Zero new files, interfaces, or exports. The change exclusively wires existing APIs.

## Insertion Point

```
init.ts flow (simplified):
  ...
  createConfigFile()                          // line 407
  config batch updates (provider, smart defaults, umbrella, LSP)
  fs.writeJsonSync(configPath, config, ...)   // line 450
  <<<--- INSERT HERE --->>>                   // after line 454 (end of config block)
  Plugin install (Claude only)                // line 456
  Git hooks                                   // line 494
  Summary banner                              // line 499
```

## Implementation Detail

### Code to Add (after line 454, before line 456)

```typescript
// Launch living docs builder as background job (non-blocking)
// Uses 'quick' depth with empty user inputs — init should be fast
if (!continueExisting) {
  try {
    const { launchLivingDocsJob } = await import('../../core/background/index.js');
    const { displayJobScheduled, estimateDuration } = await import('../helpers/init/living-docs-preflight.js');

    const ldResult = await launchLivingDocsJob({
      projectPath: targetDir,
      userInputs: {
        additionalSources: [],
        priorityAreas: [],
        knownPainPoints: [],
        analysisDepth: 'quick',
      },
    });

    if (ldResult.isBackground) {
      const duration = estimateDuration(targetDir, 'quick');
      displayJobScheduled(ldResult.job.id, duration, language);
    }
  } catch {
    // Non-critical — init succeeds even if living docs job fails to launch
    console.log(chalk.yellow('   Warning: Could not launch Living Docs builder (non-critical)'));
  }
}
```

### Design Decisions

1. **Dynamic import** (`await import(...)`) rather than top-level import — keeps init startup time unchanged; these modules are only needed at this point in the flow.

2. **`continueExisting` guard** — skip for re-init (`specweave init .` on existing project). Re-init preserves plugins and config; launching a new docs job would be disruptive.

3. **`'quick'` depth default** — init should complete fast. Users wanting deeper analysis can run `specweave living-docs --depth deep-native` afterward. This matches the CI-mode default in `collectLivingDocsInputs()`.

4. **Empty user inputs** — init has no interactive living-docs prompts (those live in the dedicated `living-docs` command). Defaults are safe: no additional sources, no priority areas, no pain points.

5. **Fire-and-forget error handling** — init must never fail because the docs job couldn't start. Worker not found, permissions, disk full — all silently caught with a yellow warning. Matches the pattern used by `ensureSkillCreator()` on line 478.

6. **No dependency chain** — unlike the full `living-docs` command which can chain clone/import jobs via `dependsOn`, init launches the docs job standalone. If clone jobs run later, the user can re-run `specweave living-docs` to get a fresh analysis.

7. **Placement after config.json write** — the job launcher reads config.json to resolve the project. Config must exist before launch (AD-3 pattern, already noted in init.ts line 323 comment).

## Technology Stack

- **Language**: TypeScript (ESM, `.js` extensions)
- **Existing APIs**: `launchLivingDocsJob`, `displayJobScheduled`, `estimateDuration`
- **Testing**: Vitest with ESM mocking (`vi.hoisted()` + `vi.mock()`)

## Testing Strategy

### Unit Tests

Single test file: `tests/unit/cli/commands/init-living-docs-launch.test.ts`

| Test Case | Validates |
|-----------|-----------|
| Launches living docs job after config.json write | Happy path: `launchLivingDocsJob` called with correct args |
| Skips launch when `continueExisting` is true | Re-init guard |
| Displays job scheduled message when background launch succeeds | `displayJobScheduled` called with job ID |
| Continues init when job launch throws | Error resilience |
| Does not launch when worker not found (foreground fallback) | `isBackground: false` path |
| Uses 'quick' depth and empty user inputs | Default arguments |

### Mocking Strategy

- Mock `../../core/background/index.js` to stub `launchLivingDocsJob`
- Mock `../helpers/init/living-docs-preflight.js` to stub `displayJobScheduled` and `estimateDuration`
- Use existing init test patterns from `tests/unit/cli/commands/init.test.ts`

### Integration Verification

- Run `specweave init . --quick` in a temp directory and verify a job appears in `specweave jobs`

## Technical Challenges

### Challenge 1: Dynamic Import in Test Mocking

**Problem**: Dynamic `await import(...)` is harder to mock than static imports.

**Solution**: Use `vi.mock()` at module level — Vitest intercepts dynamic imports the same way. The mock must be hoisted before the module under test loads.

**Risk**: Low. This pattern is already used elsewhere in the codebase (e.g., `enableAgentTeamsEnvVar` on line 483 uses dynamic import and is tested).

### Challenge 2: Init Flow Ordering

**Problem**: The job launcher needs config.json to exist. Placing the launch before config write would fail.

**Solution**: Insertion point is after line 454 (config write), guaranteed by code structure. The `createMinimalConfig()` call on line 324 also provides a safety net.

**Risk**: None — the ordering is explicit and tested by the existing config-ordering integration tests.

## Scope Boundaries

**In scope**:
- Add ~20 lines to `init.ts`
- Add unit test file
- Verify existing tests still pass

**Out of scope**:
- Interactive living docs prompts during init (separate command)
- Deep analysis during init (too slow)
- Dependency chaining with clone/import jobs
- Changes to `launchLivingDocsJob`, `displayJobScheduled`, or `estimateDuration`
