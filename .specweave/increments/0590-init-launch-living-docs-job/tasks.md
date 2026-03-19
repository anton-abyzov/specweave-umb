# Tasks: Launch Living Docs Builder as Background Job from Init

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

## Phase 1: Implementation

### US-001: Auto-launch living docs after init (P1)

#### T-001: Add static type import to init.ts

**Description**: Add `import type { LivingDocsUserInputs } from '../../core/background/types.js';` at the top of `src/cli/commands/init.ts`.

**References**: AC-US1-01

**Implementation Details**:
- Locate the existing type-only imports section near the top of `src/cli/commands/init.ts`
- Add the type import (erased at compile time, zero runtime cost)

**Test Plan**: N/A — type-only import, verified by TypeScript compilation

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Insert living docs launch block in init.ts

**Description**: Insert the ~20-line living docs launch block into `initCommand()` after config.json write (after line ~454) and before the plugin install block.

**References**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06

**Implementation Details**:
- Guard: `if (!continueExisting && !isCI)`
- Try/catch wrapping entire block (silent catch — init must never fail)
- Dynamic imports: `launchLivingDocsJob` from `../../core/background/index.js`, `displayJobScheduled` and `estimateDuration` from `../helpers/init/living-docs-preflight.js`
- Build `userInputs` with `analysisDepth: 'quick'` and empty arrays
- Call `launchLivingDocsJob({ projectPath: targetDir, userInputs })`
- If `ldResult.isBackground`, call `displayJobScheduled(ldResult.job.id, duration, language)` where `duration = estimateDuration(targetDir, 'quick')`
- Do NOT save config to living-docs-config.json (plan.md omits this; spec.md detail not required by plan insertion point)

**Test Plan**:
- **File**: `tests/unit/cli/commands/init-living-docs-launch.test.ts`
- **Tests**:
  - **TC-001**: Happy path — launches job and displays scheduled message
    - Given a fresh init (continueExisting=false, isCI=false)
    - When `initCommand()` runs
    - Then `launchLivingDocsJob` is called with `analysisDepth: 'quick'` and empty arrays, and `displayJobScheduled` is called with the job ID
  - **TC-002**: Skips when `continueExisting` is true
    - Given `continueExisting=true`
    - When `initCommand()` runs
    - Then `launchLivingDocsJob` is NOT called
  - **TC-003**: Skips when `isCI` is true
    - Given `isCI=true`
    - When `initCommand()` runs
    - Then `launchLivingDocsJob` is NOT called
  - **TC-004**: Init succeeds when job launch throws
    - Given `launchLivingDocsJob` throws an error
    - When `initCommand()` runs
    - Then init completes without error and `displayJobScheduled` is not called
  - **TC-005**: Does not display message when worker not found (foreground fallback)
    - Given `launchLivingDocsJob` returns `{ isBackground: false }`
    - When `initCommand()` runs
    - Then `displayJobScheduled` is NOT called

**Dependencies**: T-001
**Status**: [x] Completed

## Phase 2: Verification

#### T-003: Run unit tests and verify existing tests pass

**Description**: Run `npx vitest run tests/unit/cli/commands/init-living-docs-launch.test.ts` and `npx vitest run tests/unit/cli/commands/init.test.ts` to confirm new tests pass and no regressions.

**References**: AC-US1-01 through AC-US1-06

**Test Plan**:
- All 5 new test cases green
- Existing init.test.ts suite unchanged (no regressions)

**Dependencies**: T-002
**Status**: [x] Completed
