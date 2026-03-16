# Architecture Plan: PR-Based Increment Closure

## Overview

This plan adds an opt-in PR-based workflow to SpecWeave's increment lifecycle. When `cicd.pushStrategy` is `"pr-based"`, `sw:do` creates a feature branch, commits land on that branch, and `sw:done` chains to a new `sw:pr` skill that pushes the branch and creates a pull request via `gh` CLI. The default `"direct"` strategy is completely untouched.

## Decision 1: PrRef Interface Location

**Decision**: Co-locate `PrRef` with `IncrementMetadataV2` in `src/core/types/increment-metadata.ts`.

**Rationale**: `PrRef` is structurally analogous to `SyncTarget` -- a small interface stored directly on `IncrementMetadataV2`. `SyncTarget` lives in the same file. The `PrRef` array is a metadata field, not a standalone concept. Placing it alongside the interface that consumes it keeps the import graph simple and follows the existing pattern.

```
increment-metadata.ts
─────────────────────────────────
SyncTarget         (existing)
PrRef              (new, ~6 fields)
IncrementMetadataV2
  ├── syncTarget?: SyncTarget
  └── prRefs?: PrRef[]        (new)
```

No new file needed.

## Decision 2: MetadataManager PR Helpers

**Decision**: Add `addPrRef` and `getPrRefs` static methods to `MetadataManager`, following the `setSyncTarget`/`getSyncTarget` pattern exactly.

**Pattern analysis** (from `metadata-manager.ts` lines 1020-1076):
- `setSyncTarget` reads metadata via `this.read()`, mutates the field, updates `lastActivity`, calls `this.write()`, logs via `this.logger.debug()`, and returns the updated metadata.
- `getSyncTarget` reads and returns the field (or undefined).
- Companion methods: `clearSyncTarget`, `hasSyncTarget`.

**PR helpers follow the same shape**:

```
addPrRef(incrementId, prRef, rootDir?)
  -> read metadata
  -> initialize prRefs array if absent
  -> append prRef
  -> update lastActivity
  -> write metadata
  -> log
  -> return updated metadata

getPrRefs(incrementId, rootDir?)
  -> read metadata
  -> return metadata.prRefs ?? []
```

No `clearPrRefs` or `hasPrRefs` needed at this stage -- YAGNI.

## Decision 3: CiCdConfig Extension

**Decision**: Extend the existing `CiCdConfig` interface in `src/core/config/types.ts` with nested `git` and `release`/`environments` sub-objects.

```
CiCdConfig (existing fields unchanged)
─────────────────────────────────────────
pushStrategy: 'direct' | 'pr-based'      (existing)
autoFix: { ... }                         (existing)
monitoring?: { ... }                     (existing)
git?: GitConfig                          (new, optional)
release?: ReleaseConfig                  (new, optional, P2)
environments?: EnvironmentConfig[]       (new, optional, P2)
```

**New interfaces** (in the same file):

```
GitConfig {
  branchPrefix: string;    // default: "sw/"
  targetBranch: string;    // default: "main"
  deleteOnMerge: boolean;  // default: true
}

ReleaseConfig {
  strategy: 'trunk' | 'env-promotion';  // default: "trunk"
}

EnvironmentConfig {
  name: string;     // e.g., "dev", "staging", "prod"
  branch: string;   // e.g., "develop", "staging", "main"
}
```

**Default values** update in `DEFAULT_CONFIG` (~line 1118):

```typescript
cicd: {
  pushStrategy: 'direct',
  autoFix: { enabled: true, maxRetries: 1, allowedBranches: ['develop', 'main'] },
  git: { branchPrefix: 'sw/', targetBranch: 'main', deleteOnMerge: true },
  release: { strategy: 'trunk' },
},
```

**Config loader** (`config-loader.ts`): The `RawConfig` interface and `loadFromConfigFile()` already parse `pushStrategy`. Extend `RawConfig.cicd` to include the new optional fields (`git`, `release`, `environments`). Pass them through in `mergeConfigs()`.

## Decision 4: sw:pr Skill Orchestration

**Decision**: Create `sw:pr` as a SKILL.md-only skill (no TypeScript runtime). It shells out to `gh` CLI, consistent with `github-push-sync.ts` using `execFileNoThrow` for `gh` calls.

### Skill location

`plugins/specweave/skills/pr/SKILL.md`

### Orchestration flow

```
sw:pr
  |-- 1. Pre-flight checks
  |     |-- Verify `gh` CLI available: `which gh`
  |     |-- Read config for pushStrategy, git.targetBranch
  |     \-- If pushStrategy != "pr-based", warn and exit
  |
  |-- 2. Determine target branch
  |     |-- Default: config.cicd.git.targetBranch
  |     \-- Override: if release.strategy == "env-promotion"
  |           -> use environments[0].branch (lowest env)
  |
  |-- 3. Single-repo flow
  |     |-- Check for commits: `git log {target}..HEAD --oneline`
  |     |-- If no commits -> skip with warning
  |     |-- Push branch: `git push -u origin {current-branch}`
  |     |-- Generate PR body from spec.md (user stories + ACs summary)
  |     |-- Create PR: `gh pr create --base {target} --title {title} --body {body}`
  |     |-- Parse PR URL and number from output
  |     \-- Store PrRef in metadata via MetadataManager.addPrRef()
  |
  |-- 4. Multi-repo flow (umbrella mode)
  |     |-- Read umbrella.childRepos from config
  |     |-- For each child repo:
  |     |     |-- cd to childRepo.path
  |     |     |-- Check `git status --porcelain` for changes
  |     |     |-- If no changes -> skip
  |     |     |-- Check if on feature branch (or create one)
  |     |     |-- Run single-repo flow (steps 3a-3f)
  |     |     \-- Continue on failure (log warning)
  |     \-- Report summary (successes + failures)
  |
  \-- 5. Error handling
        |-- gh not found -> warning + install instructions, no block
        |-- PR creation fails -> warning, no block
        \-- Partial multi-repo failure -> continue remaining repos
```

### PR body generation

The skill reads `spec.md` from the increment directory and constructs a PR body:

```markdown
## Summary
{spec.md title + problem statement, first 2-3 sentences}

## User Stories
- US-001: {title} ({N} ACs)
- US-002: {title} ({N} ACs)

## Acceptance Criteria
- [x] AC-US1-01: {description}
- [x] AC-US1-02: {description}
...

---
Generated by SpecWeave increment {increment-id}
```

This is pure markdown manipulation within SKILL.md instructions -- no TypeScript template engine needed.

## Decision 5: sw:do Branch Creation Integration

**Decision**: Add a new step (Step 2.7) to `sw:do` SKILL.md for conditional feature branch creation. No changes to the TypeScript runtime.

### Insertion point

After Step 2 (Load Context) and before Step 2.5 (Execution Strategy Check), add:

```
### Step 2.7: Feature Branch Setup (PR-Based Only)

1. Read `cicd.pushStrategy` from `.specweave/config.json`
2. If `pushStrategy` != "pr-based" -> skip entirely
3. Read `cicd.git.branchPrefix` (default "sw/") and `cicd.git.targetBranch` (default "main")
4. Determine current branch: `git branch --show-current`
5. If already on a non-target branch -> use as-is, log info
6. If on target branch:
   a. Compute branch name: `{branchPrefix}{increment-id}`
      (e.g., `sw/0520-pr-based-increment-closure`)
   b. Check if branch exists locally: `git branch --list {branch-name}`
   c. If exists -> `git checkout {branch-name}`
   d. If not -> `git checkout -b {branch-name}`
7. Log branch name for traceability
```

**Same logic applies to `sw:auto`**: The auto skill delegates to `sw:do` for task execution, so the branch creation happens automatically through the `sw:do` step.

## Decision 6: sw:done Integration Point

**Decision**: SKILL.md-level orchestration in `sw:done` is sufficient. No changes to `LifecycleHookDispatcher.onIncrementDone()`.

### Rationale

The `onIncrementDone` hook handles living docs sync, GitHub Project sync, and issue closure -- all about syncing spec metadata to external trackers. PR creation is a fundamentally different operation: it is about the git workflow, not spec sync. Mixing PR creation into the hook dispatcher would conflate two unrelated concerns.

Instead, `sw:done` gets a new step between Step 8 (PM Decision / `specweave complete`) and Step 9 (Post-Closure Sync):

```
### Step 8.5: PR Creation (PR-Based Only)

1. Read `cicd.pushStrategy` from config
2. If `pushStrategy` != "pr-based" -> skip
3. Invoke: `Skill({ skill: "sw:pr" })` with increment ID
4. sw:pr handles all branching, pushing, PR creation, and metadata storage
5. PR creation failure does NOT block closure (already completed in Step 8)
```

**Key design property**: Step 8.5 runs AFTER `specweave complete` succeeds. The increment is already closed. PR creation is a post-closure distribution step, not a gate. This means:

- If PR creation fails, the increment is still closed (correct -- work is done)
- If PR creation succeeds, the PrRef is stored in metadata (traceability)
- The human reviewer sees the completed spec in the PR description

## Decision 7: No New Lifecycle Hook

**Decision**: Do NOT add an `onPrCreated` hook to `LifecycleHookDispatcher`.

**Rationale**: There is no downstream consumer for such a hook today. The PrRef is stored in metadata, which is the audit trail. Adding an empty hook point would be speculative. If a future increment needs PR-triggered actions (e.g., auto-assign reviewers, post Slack notification), a hook can be added then with real requirements driving its shape.

## Component Boundary Summary

```
+--------------------------------------------------------------+
|                     Config Layer                              |
|                                                               |
|  types.ts                                                     |
|  |-- CiCdConfig.pushStrategy  (existing)                     |
|  |-- CiCdConfig.git?: GitConfig  (NEW)                       |
|  |-- CiCdConfig.release?: ReleaseConfig  (NEW, P2)           |
|  \-- CiCdConfig.environments?: EnvironmentConfig[]  (NEW, P2)|
|                                                               |
|  config-loader.ts                                             |
|  \-- RawConfig.cicd.git / release / environments  (NEW)      |
|                                                               |
|  DEFAULT_CONFIG.cicd.git  (NEW defaults)                      |
+--------------------------------------------------------------+

+--------------------------------------------------------------+
|                    Metadata Layer                              |
|                                                               |
|  increment-metadata.ts                                        |
|  |-- PrRef interface  (NEW)                                   |
|  \-- IncrementMetadataV2.prRefs?: PrRef[]  (NEW)             |
|                                                               |
|  metadata-manager.ts                                          |
|  |-- addPrRef(incrementId, prRef, rootDir?)  (NEW)           |
|  \-- getPrRefs(incrementId, rootDir?)  (NEW)                 |
+--------------------------------------------------------------+

+--------------------------------------------------------------+
|                     Skill Layer                               |
|                                                               |
|  skills/pr/SKILL.md  (NEW)                                    |
|  \-- Orchestrates: gh CLI, spec.md parsing, metadata update  |
|                                                               |
|  skills/do/SKILL.md  (MODIFIED)                               |
|  \-- Step 2.7: Feature branch creation (pr-based only)       |
|                                                               |
|  skills/done/SKILL.md  (MODIFIED)                             |
|  \-- Step 8.5: Invoke sw:pr (pr-based only)                  |
|                                                               |
|  skills/auto/SKILL.md  (UNCHANGED)                            |
|  \-- Delegates to sw:do which handles branching              |
+--------------------------------------------------------------+

+--------------------------------------------------------------+
|                    Runtime Layer                               |
|                                                               |
|  LifecycleHookDispatcher  (UNCHANGED)                         |
|  \-- No PR-related hooks -- PR is git workflow, not spec sync|
|                                                               |
|  github-push-sync.ts  (UNCHANGED)                             |
|  \-- Handles issue sync, not PR creation                     |
+--------------------------------------------------------------+
```

## Data Flow

```
User configures:
  config.json -> cicd.pushStrategy: "pr-based"
                 cicd.git.branchPrefix: "sw/"
                 cicd.git.targetBranch: "main"

/sw:do starts:
  Step 2.7 -> reads config
           -> if pr-based: git checkout -b sw/0520-pr-based-increment-closure
           -> all task commits land on this branch

/sw:done runs:
  Steps 1-8 -> quality gates, specweave complete (increment closed)
  Step 8.5  -> invoke sw:pr
                -> git push -u origin sw/0520-pr-based-increment-closure
                -> gh pr create --base main --title "..." --body "..."
                -> MetadataManager.addPrRef(id, { repo, prNumber, prUrl, ... })
  Steps 9+  -> post-closure sync (unchanged)
```

## Multi-Repo Data Flow

```
Umbrella config:
  umbrella.childRepos: [
    { id: "frontend", path: "repositories/org/frontend", ... },
    { id: "backend",  path: "repositories/org/backend",  ... },
  ]

sw:pr in umbrella mode:
  For each childRepo with changes:
    |-- cd to childRepo.path
    |-- git push -u origin {branch}
    |-- gh pr create in that repo's context
    |-- PrRef stored: { repo: "org/frontend", prNumber: 42, ... }
    \-- Continue even if one repo fails

metadata.json result:
  {
    "prRefs": [
      { "repo": "org/frontend", "prNumber": 42, "prUrl": "...", ... },
      { "repo": "org/backend",  "prNumber": 17, "prUrl": "...", ... }
    ]
  }
```

## File Change Summary

| File | Change | Priority |
|------|--------|----------|
| `src/core/types/increment-metadata.ts` | Add `PrRef` interface, add `prRefs?` to `IncrementMetadataV2` | P1 |
| `src/core/config/types.ts` | Add `GitConfig`, extend `CiCdConfig.git?`, update `DEFAULT_CONFIG` | P1 |
| `src/core/config/types.ts` | Add `ReleaseConfig`, `EnvironmentConfig`, extend `CiCdConfig` | P2 |
| `src/core/increment/metadata-manager.ts` | Add `addPrRef()` and `getPrRefs()` static methods | P1 |
| `src/core/cicd/config-loader.ts` | Extend `RawConfig` to parse `git`, `release`, `environments` | P1 |
| `plugins/specweave/skills/pr/SKILL.md` | New skill: PR creation orchestration | P1 |
| `plugins/specweave/skills/do/SKILL.md` | Add Step 2.7: feature branch setup | P1 |
| `plugins/specweave/skills/done/SKILL.md` | Add Step 8.5: invoke sw:pr | P1 |

## Test Strategy

**Unit tests** (Vitest):
- `metadata-manager.test.ts`: `addPrRef` appends to array, creates array if absent, `getPrRefs` returns empty array when no refs
- `config-loader.test.ts`: Parses `git` sub-object, applies defaults when absent, validates `pushStrategy` enum
- Type tests: `PrRef` interface fields, `GitConfig` defaults

**Integration tests** (SKILL.md behavioral):
- `sw:do` on `direct` strategy: no branch creation
- `sw:do` on `pr-based` strategy: branch created with correct name
- `sw:done` on `pr-based`: `sw:pr` invoked after `specweave complete`
- `sw:pr` with missing `gh`: warning logged, no block
- `sw:pr` multi-repo: partial failure continues

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| SKILL.md branch logic is error-prone without runtime enforcement | Branch step uses simple `git` commands; failure just means commits land on current branch (safe) |
| `gh` auth state varies across machines | Pre-flight check with clear error message; graceful degradation |
| PR body too long for complex specs | Truncate to first 3 user stories + first 10 ACs; link to full spec |
| Enterprise config adds cognitive overhead | P2 fields are fully optional; core flow works without them |

## Non-Goals Confirmed

- No `onPrCreated` lifecycle hook (speculative)
- No TypeScript runtime for `sw:pr` (SKILL.md-only, shells out to `gh`)
- No changes to `LifecycleHookDispatcher`
- No changes to `github-push-sync.ts`
- No auto-merge capability
- No branch protection management
