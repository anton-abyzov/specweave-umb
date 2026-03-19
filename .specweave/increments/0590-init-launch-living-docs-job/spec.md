---
increment: 0590-init-launch-living-docs-job
title: Launch Living Docs Builder as Background Job from Init
type: feature
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Launch Living Docs Builder as Background Job from Init

## Overview

`specweave init` scaffolds empty README.md files in `.specweave/docs/` but never launches the living docs builder to populate them with actual content. The background job infrastructure (`launchLivingDocsJob()` in `src/core/background/job-launcher.ts`) exists and works — the standalone `specweave living-docs` command already calls it — but the init flow never invokes it. Users must manually discover and run `specweave living-docs` after init, which most never do.

**Fix**: Wire `init.ts` to call `launchLivingDocsJob()` after scaffolding completes, using sensible defaults (no interactive prompts). Save the config so the standalone command can reuse it.

**Scope**: Single file change — `src/cli/commands/init.ts` (~20 lines added). All APIs already exist.

## User Stories

### US-001: Auto-launch living docs after init (P1)
**Project**: specweave

**As a** developer running `specweave init`
**I want** the living docs builder to start automatically as a background job
**So that** my `.specweave/docs/` directory gets populated with real content without requiring a separate command

**Acceptance Criteria**:
- [x] **AC-US1-01**: After init scaffolding + config creation, `launchLivingDocsJob()` is called with default inputs (`analysisDepth: 'quick'`, empty arrays for `priorityAreas`, `additionalSources`, `knownPainPoints`)
- [x] **AC-US1-02**: Config is saved to `.specweave/state/living-docs-config.json` before launching, so standalone `specweave living-docs` can reuse it
- [x] **AC-US1-03**: Job ID and monitoring instructions are displayed via `displayJobScheduled()`
- [x] **AC-US1-04**: Skipped when `continueExisting === true` (re-init already has docs)
- [x] **AC-US1-05**: Skipped when `isCI === true` (no background processes in CI)
- [x] **AC-US1-06**: Entire block wrapped in try/catch — failure to launch living docs NEVER breaks init
- [x] **AC-US1-07**: Tool-agnostic — works with any AI tool (Claude, Cursor, OpenCode, etc.)

## Functional Requirements

### FR-001: Insertion point in init flow
The living docs launch goes after git hooks installation (line ~496) and before the summary banner (line ~499) in `init.ts`. At this point: scaffolding is done, config is finalized, plugins are installed, git hooks are set up. Living docs is fire-and-forget — it does not affect the banner.

### FR-002: Dynamic imports
`launchLivingDocsJob` and `displayJobScheduled` are dynamically imported (`await import(...)`) to avoid adding cold-start weight to init. Only the `LivingDocsUserInputs` type is statically imported (type-only, erased at compile time).

### FR-003: Sensible defaults — no prompts
Uses hardcoded defaults: `analysisDepth: 'quick'` (completes in ~5-10 min), empty arrays for all optional fields. Init already has enough interactive prompts.

### FR-004: Config persistence
Config is written to `.specweave/state/living-docs-config.json` before launching the job. The standalone `specweave living-docs` command checks this path via `loadSavedLivingDocsConfig()` at `living-docs.ts:518` and uses it as defaults.

### FR-005: Silent failure
Empty catch block — if the job fails to launch (worker not found, spawn error, etc.), init still succeeds. User can always run `specweave living-docs` manually later.

## Technical Design

### Code shape (inserted after git hooks, before summary banner in init.ts)

```typescript
// Launch living docs builder (background job — never blocks init)
if (!continueExisting && !isCI) {
  try {
    const { launchLivingDocsJob } = await import('../../core/background/job-launcher.js');
    const { displayJobScheduled } = await import('../helpers/init/living-docs-preflight.js');

    const userInputs: LivingDocsUserInputs = {
      analysisDepth: 'quick',
      priorityAreas: [],
      additionalSources: [],
      knownPainPoints: [],
    };

    // Save config so standalone `specweave living-docs` can reuse it
    const livingDocsConfigPath = path.join(targetDir, '.specweave', 'state', 'living-docs-config.json');
    fs.ensureDirSync(path.dirname(livingDocsConfigPath));
    fs.writeFileSync(livingDocsConfigPath, JSON.stringify({ userInputs }, null, 2));

    const result = await launchLivingDocsJob({
      projectPath: targetDir,
      userInputs,
    });

    displayJobScheduled(result.job.id, '~5-10 min', language);
  } catch {
    // Non-critical — living docs can always be launched later with `specweave living-docs`
  }
}
```

### Import addition (type-only, at top of file)

```typescript
import type { LivingDocsUserInputs } from '../../core/background/types.js';
```

## Interview Decisions

### Architecture
Single insertion in `init.ts` after git hooks, before summary banner. Dynamic imports for runtime dependencies, static type-only import for `LivingDocsUserInputs`. No new files, no new modules.

### Integrations
Uses existing APIs only: `launchLivingDocsJob()` from `job-launcher.ts`, `displayJobScheduled()` from `living-docs-preflight.ts`. Config saved to `.specweave/state/living-docs-config.json` for reuse by standalone `specweave living-docs` command via `loadSavedLivingDocsConfig()`.

### UI/UX
No new interactive prompts. `displayJobScheduled()` shows job ID and monitoring instructions (`/sw:jobs`). Silent on failure — no error messages shown to user since init must feel clean.

### Performance
Dynamic imports keep init cold-start fast when living docs launch is skipped (re-init, CI). `analysisDepth: 'quick'` means background job completes in ~5-10 min. Fire-and-forget — does not block init completion.

### Security
No new user input handling. No secrets involved. Background job runs with same permissions as the init process. No network calls added to init itself (the background worker handles its own I/O).

### Edge Cases
- **Re-init** (`continueExisting`): Skipped — existing projects already have docs
- **CI** (`isCI`): Skipped — background detached processes are inappropriate in CI
- **Worker not found**: Handled gracefully by `launchLivingDocsJob` itself (returns `isBackground: false`)
- **Missing state dir**: `fs.ensureDirSync` before writing config
- **Spawn failure**: Caught by outer try/catch, init continues
- **Config write failure**: Caught by outer try/catch, init continues

## Success Criteria

- Fresh `specweave init` launches a living docs background job automatically
- Re-init (`specweave init .` on existing project) does NOT re-launch
- CI runs complete without spawning background jobs
- Init never fails due to living docs launch errors
- `specweave living-docs` picks up the saved config from init

## Out of Scope

- Changing the living docs worker infrastructure
- Adding new CLI flags to control this behavior from init
- Modifying the standalone `specweave living-docs` command
- Adding tests for the background job itself (already covered by existing test suite)
- Interactive configuration during init (use `specweave living-docs` for that)

## Dependencies

- `launchLivingDocsJob()` — `src/core/background/job-launcher.ts` (exists)
- `displayJobScheduled()` — `src/cli/helpers/init/living-docs-preflight.ts` (exists)
- `LivingDocsUserInputs` type — `src/core/background/types.ts` (exists)
