---
increment: 0520-pr-based-increment-closure
title: "PR-Based Increment Closure"
total_tasks: 14
completed_tasks: 14
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-004, T-005]
  US-003: [T-006, T-007, T-008, T-009, T-010]
  US-004: [T-011, T-012, T-013, T-014]
---

# Tasks: PR-Based Increment Closure

---

## User Story: US-001 - PR-Based Push Strategy Configuration

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 3 total, 0 completed

---

### T-001: Add GitConfig interface and extend CiCdConfig with git sub-object

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the `CiCdConfig` TypeScript interface in `src/core/config/types.ts`
- **When** a developer inspects the type
- **Then** it contains `git?: { branchPrefix: string; targetBranch: string; deleteOnMerge: boolean }` and `pushStrategy` defaults to `"direct"` when absent

**Test Cases**:
1. **Unit**: `src/core/config/types.test.ts` (or compile-time via `npx tsc --noEmit`)
   - `testGitConfigFields()`: Construct `GitConfig` literal with all three fields — compiles without error
   - `testCiCdConfigGitIsOptional()`: Create `CiCdConfig` without `git` field — no TS error
   - `testDefaultDirectStrategy()`: `DEFAULT_CONFIG.cicd.pushStrategy` equals `"direct"`
   - **Coverage Target**: 95% (type correctness enforced at compile time; runtime in config-loader tests)

**Implementation**:
1. Open `src/core/config/types.ts`
2. Add `GitConfig` interface above `CiCdConfig`:
   ```typescript
   export interface GitConfig {
     branchPrefix: string;   // default: "sw/"
     targetBranch: string;   // default: "main"
     deleteOnMerge: boolean; // default: true
   }
   ```
3. Add `git?: GitConfig` to `CiCdConfig`
4. Update `DEFAULT_CONFIG.cicd` to include `git: { branchPrefix: 'sw/', targetBranch: 'main', deleteOnMerge: true }`
5. Run `npx tsc --noEmit` to verify zero type errors

---

### T-002: Extend config-loader RawConfig to parse cicd.git sub-object

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `config.json` with `cicd.pushStrategy: "pr-based"` and a `cicd.git` sub-object containing `branchPrefix`, `targetBranch`, `deleteOnMerge`
- **When** `loadFromConfigFile()` reads the file
- **Then** all three `git` fields are parsed and available on the returned config
- **Given** `cicd.pushStrategy` is absent from config
- **When** defaults are applied
- **Then** `pushStrategy` is `"direct"` and `git` has `{ branchPrefix: 'sw/', targetBranch: 'main', deleteOnMerge: true }`

**Test Cases**:
1. **Unit**: `src/core/cicd/config-loader.test.ts`
   - `testParsesGitSubObject()`: Config JSON with `cicd.git` fields — assert all three fields on result
   - `testDefaultsWhenGitAbsent()`: Config JSON without `cicd.git` — assert default `git` values applied
   - `testGitUserValueOverridesDefault()`: Config JSON with `cicd.git.branchPrefix: "feat/"` — assert `branchPrefix` is `"feat/"` (not `"sw/"`)
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/core/cicd/config-loader.ts`
2. Extend `RawConfig.cicd` with:
   ```typescript
   git?: {
     branchPrefix?: string;
     targetBranch?: string;
     deleteOnMerge?: boolean;
   };
   ```
3. In `loadFromConfigFile()`, after parsing `pushStrategy`, add:
   ```typescript
   if (rawConfig.cicd?.git) {
     config.git = rawConfig.cicd.git as GitConfig;
   }
   ```
4. In `mergeConfigs()`, merge `git` (spread default, then user values win):
   ```typescript
   git: { ...defaults.git, ...configFile.git },
   ```
5. Run `npx vitest run src/core/cicd/config-loader.test.ts`

---

### T-003: Add PrRef interface and prRefs field to IncrementMetadataV2

**User Story**: US-001
**Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the `PrRef` interface in `src/core/types/increment-metadata.ts`
- **When** a developer inspects the type
- **Then** it contains `repo` (string), `prNumber` (number), `prUrl` (string), `branch` (string), `targetBranch` (string), `createdAt` (ISO 8601 string)
- **Given** `IncrementMetadataV2`
- **When** inspected
- **Then** it has an optional `prRefs?: PrRef[]` field

**Test Cases**:
1. **Unit**: `src/core/types/increment-metadata.test.ts` (or `npx tsc --noEmit`)
   - `testPrRefAllFields()`: Construct `PrRef` literal with all 6 fields — compiles without error
   - `testPrRefsOptional()`: Create `IncrementMetadataV2` without `prRefs` — no TS error; `prRefs` is `undefined`
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/core/types/increment-metadata.ts`
2. Add `PrRef` interface after `SyncTarget` (co-located, same file, same pattern):
   ```typescript
   export interface PrRef {
     repo: string;          // e.g., "org/frontend"
     prNumber: number;      // GitHub PR number
     prUrl: string;         // Full URL to PR
     branch: string;        // Feature branch name
     targetBranch: string;  // PR target branch
     createdAt: string;     // ISO 8601 timestamp
   }
   ```
3. Add `prRefs?: PrRef[]` to `IncrementMetadataV2`
4. Run `npx tsc --noEmit` to verify zero type errors

---

## User Story: US-002 - Feature Branch Creation in sw:do and sw:auto

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 0 completed

---

### T-004: Add Step 2.7 (Feature Branch Setup) to sw:do SKILL.md

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** `pushStrategy` is `"pr-based"` and the developer is on `main` (the target branch)
- **When** `sw:do` reaches Step 2.7
- **Then** `git checkout -b sw/0520-pr-based-increment-closure` is executed and all subsequent commits land on that branch
- **Given** `pushStrategy` is `"pr-based"` and the developer is already on `sw/0520-pr-based-increment-closure`
- **When** `sw:do` starts
- **Then** no new branch is created; `git checkout sw/0520-pr-based-increment-closure` is used (no `-b`)
- **Given** `pushStrategy` is `"direct"`
- **When** `sw:do` starts
- **Then** Step 2.7 is skipped entirely

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Scenario A: pr-based + on target branch + branch not exists → `git checkout -b sw/{id}`
   - Scenario B: pr-based + on target branch + branch exists locally → `git checkout sw/{id}` (no `-b`)
   - Scenario C: pr-based + already on non-target branch → use as-is, no git command
   - Scenario D: direct strategy → skip step, no git branch commands
   - Scenario E: pr-based + uncommitted changes → changes carry over (standard `git checkout -b` behavior)
   - **Coverage Target**: All 5 ACs (AC-US2-01 through AC-US2-05) covered

**Implementation**:
1. Open `plugins/specweave/skills/do/SKILL.md`
2. Find the insertion point after "Load Context" step and before task execution loop
3. Insert new step:

```markdown
### Step 2.7: Feature Branch Setup (PR-Based Only)

1. Read `cicd.pushStrategy` from `.specweave/config.json`
2. If `pushStrategy` != `"pr-based"` → skip this step entirely and proceed
3. Read `cicd.git.branchPrefix` (default `"sw/"`) and `cicd.git.targetBranch` (default `"main"`)
4. Run: `git branch --show-current` to get current branch name
5. If current branch != `targetBranch` → log "Using existing branch: {current-branch}" and proceed (AC-US2-02)
6. If current branch == `targetBranch`:
   a. Compute branch name: `{branchPrefix}{increment-id}` (e.g., `sw/0520-pr-based-increment-closure`)
   b. Run: `git branch --list {branch-name}` to check if branch exists locally
   c. If branch exists → run `git checkout {branch-name}` and log "Checked out existing feature branch: {branch-name}" (AC-US2-03)
   d. If branch does not exist → run `git checkout -b {branch-name}` and log "Created feature branch: {branch-name}" (AC-US2-01, AC-US2-05)
7. All task commits in this sw:do session will land on this branch
```

---

### T-005: Verify sw:auto inherits branch creation via sw:do delegation

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** `pushStrategy` is `"pr-based"` and `sw:auto` is invoked
- **When** `sw:auto` delegates task execution to `sw:do`
- **Then** Step 2.7 fires automatically — no duplicate branch-creation logic needed in `auto/SKILL.md`
- **Given** `pushStrategy` is `"direct"` and `sw:auto` is invoked
- **When** `sw:auto` delegates to `sw:do`
- **Then** no branch creation occurs (Step 2.7 in `sw:do` skips itself)

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Read `plugins/specweave/skills/auto/SKILL.md` — confirm delegation to `sw:do` exists
   - Confirm no redundant branch-creation step in `auto/SKILL.md`
   - If `sw:auto` has its own execution loop not going through `sw:do`: add parallel Step 2.7
   - **Coverage Target**: AC-US2-01 and AC-US2-04 covered via delegation chain

**Implementation**:
1. Open `plugins/specweave/skills/auto/SKILL.md`
2. Search for `sw:do` invocation or equivalent task-execution delegation
3. If delegation confirmed → no change needed; document with a brief comment: `# Note: branch setup handled by sw:do Step 2.7`
4. If `sw:auto` has an independent task loop (no `sw:do` delegation): add the same Step 2.7 block from T-004 to `auto/SKILL.md` at the corresponding position before the task loop

---

## User Story: US-003 - PR Creation and Metadata Storage via sw:pr

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06
**Tasks**: 5 total, 0 completed

---

### T-006: Add addPrRef and getPrRefs helpers to MetadataManager

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-06
**Status**: [x] completed

**Test Plan**:
- **Given** an increment with no existing `prRefs` field in metadata
- **When** `MetadataManager.addPrRef(incrementId, prRef)` is called
- **Then** `metadata.prRefs` is initialized as `[prRef]` and persisted to `metadata.json`
- **Given** an increment with an existing `prRefs` array containing one entry
- **When** `addPrRef` is called with a second `PrRef`
- **Then** the array grows to 2 entries; original entry is preserved
- **Given** an increment with no `prRefs` field
- **When** `MetadataManager.getPrRefs(incrementId)` is called
- **Then** it returns `[]` (empty array, not `undefined`)

**Test Cases**:
1. **Unit**: `src/core/increment/metadata-manager.test.ts`
   - `testAddPrRefInitializesArray()`: `addPrRef` on fresh increment → `prRefs` array has 1 entry
   - `testAddPrRefAppends()`: `addPrRef` called twice → 2 entries, both intact
   - `testGetPrRefsEmptyDefault()`: `getPrRefs` when field absent → returns `[]`
   - `testGetPrRefsReturnsStored()`: `getPrRefs` after `addPrRef` → returns stored ref
   - `testAddPrRefUpdatesLastActivity()`: `metadata.lastActivity` is updated after `addPrRef`
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/core/types/increment-metadata.ts` — confirm `PrRef` is exported (done in T-003)
2. Open `src/core/increment/metadata-manager.ts`
3. Import `PrRef` from `../types/increment-metadata.js`
4. After `clearSyncTarget` method, add `addPrRef` following the `setSyncTarget` pattern:
   ```typescript
   static addPrRef(
     incrementId: string,
     prRef: PrRef,
     rootDir?: string
   ): IncrementMetadataV2 {
     const metadata = this.read(incrementId, rootDir) as IncrementMetadataV2;
     if (!metadata.prRefs) metadata.prRefs = [];
     metadata.prRefs.push(prRef);
     metadata.lastActivity = new Date().toISOString();
     this.write(incrementId, metadata, rootDir);
     this.logger.debug(`Added PrRef for ${incrementId}: PR#${prRef.prNumber} in ${prRef.repo}`);
     return metadata;
   }
   ```
5. Add `getPrRefs` following `getSyncTarget` pattern:
   ```typescript
   static getPrRefs(incrementId: string, rootDir?: string): PrRef[] {
     const metadata = this.read(incrementId, rootDir) as IncrementMetadataV2;
     return metadata.prRefs ?? [];
   }
   ```
6. Run `npx vitest run src/core/increment/metadata-manager.test.ts`

---

### T-007: Create sw:pr SKILL.md — pre-flight checks and single-repo PR creation

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `gh` CLI is installed, authenticated, and `pushStrategy` is `"pr-based"`
- **When** `sw:pr` runs (happy path)
- **Then** `git push -u origin {branch}` is executed followed by `gh pr create --base {targetBranch} --title {increment-title} --body-file {tempFile}`
- **Given** `gh` CLI is not installed (`which gh` fails)
- **When** `sw:pr` pre-flight check runs
- **Then** a warning is logged with install instructions (`brew install gh` / `https://cli.github.com`) and the skill exits without blocking
- **Given** PR creation fails (auth error, network error)
- **When** error is caught
- **Then** warning is logged and skill exits 0 (closure is NOT blocked)

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Scenario A: `which gh` non-zero → warning "gh CLI not found. Install: https://cli.github.com" → exit 0
   - Scenario B: `pushStrategy` != `"pr-based"` → warning "sw:pr requires pr-based strategy" → exit 0
   - Scenario C: `git log {target}..HEAD --oneline` empty → "No commits on branch, skipping PR" → exit 0
   - Scenario D: Happy path → push branch → create PR → parse URL/number → store PrRef → log PR URL
   - Scenario E: `gh pr create` exits non-zero → warning logged → skill exits 0 (no block)
   - **Coverage Target**: AC-US3-01, AC-US3-02, AC-US3-04 fully covered

**Implementation**:
1. Create directory: `plugins/specweave/skills/pr/`
2. Create `plugins/specweave/skills/pr/SKILL.md` with the following structure:

```markdown
# sw:pr — Pull Request Creation Skill

## Purpose
Push the current feature branch and create a pull request with an auto-generated description from spec.md. Invoked by sw:done Step 8.5 when pushStrategy is "pr-based".

## Step 1: Pre-Flight Checks
1. Run `which gh` — if non-zero: log "WARNING: gh CLI not found. Install at https://cli.github.com" and exit 0 (do NOT block)
2. Read `.specweave/config.json` → `cicd.pushStrategy`
3. If `pushStrategy` != `"pr-based"`: log warning and exit 0
4. Read `cicd.git.targetBranch` (default "main") and `cicd.git.branchPrefix` (default "sw/")

## Step 2: Determine Target Branch
1. Read `cicd.release.strategy` (default "trunk")
2. If `release.strategy` == `"env-promotion"`:
   - Read `cicd.environments` array
   - If non-empty: `targetBranch = environments[0].branch`
   - If empty: log warning, fall back to `cicd.git.targetBranch`
3. Else: `targetBranch = cicd.git.targetBranch`

## Step 3: Check for Commits
1. Run `git log {targetBranch}..HEAD --oneline`
2. If output is empty: log "No commits on feature branch vs {targetBranch}. Skipping PR creation." and exit 0
3. Get current branch: `git branch --show-current`

## Step 4: Push Branch
1. Run `git push -u origin {current-branch}`
2. On failure: log "WARNING: git push failed: {error}. PR creation skipped." and exit 0

## Step 5: Generate PR Body
1. Read `spec.md` from `.specweave/increments/{increment-id}/spec.md`
2. Extract `title` from frontmatter (use as PR title)
3. Extract Problem Statement section (first 2-3 sentences)
4. List User Stories: `- US-00N: {title} ({N} ACs)`
5. List ACs with completion status (first 10 max; append "...and N more" if exceeded)
6. Write body to a temp file: `/tmp/sw-pr-body-{increment-id}.md`

## Step 6: Create Pull Request
1. Run: `gh pr create --base {targetBranch} --title "{title}" --body-file /tmp/sw-pr-body-{increment-id}.md`
2. On success: capture PR URL from stdout
3. On failure: log "WARNING: PR creation failed: {error}. Increment is closed. Create PR manually." and exit 0

## Step 7: Store PrRef in Metadata
1. Parse PR number from URL (last path segment)
2. Get repo name from: `gh repo view --json nameWithOwner --jq .nameWithOwner`
3. Construct PrRef: `{ repo, prNumber, prUrl, branch: currentBranch, targetBranch, createdAt: new Date().toISOString() }`
4. Call `MetadataManager.addPrRef(incrementId, prRef)` via `specweave` CLI or direct metadata write
5. Log: "PR created: {prUrl}"

## Error Handling
- Any unhandled error in Steps 4-7: log warning with context, exit 0 (never block increment closure)
- Increment was already closed in sw:done Step 8 before this skill runs
```

---

### T-008: Add PR body generation detail to sw:pr SKILL.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** a spec.md with a `title` in frontmatter, a Problem Statement section, and 4 user stories each with multiple ACs
- **When** `sw:pr` generates the PR body
- **Then** the body contains: `## Summary` with problem statement text, `## User Stories` listing all 4 stories with AC counts, `## Acceptance Criteria` with checkboxed ACs (max 10), and a footer with the increment ID
- **Given** spec.md has more than 10 ACs
- **When** body is generated
- **Then** first 10 ACs are listed and "...and N more" is appended

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Scenario A: spec.md with 4 user stories → all 4 appear in `## User Stories` section
   - Scenario B: 12 ACs total → first 10 listed, "...and 2 more" appended
   - Scenario C: PR title matches `title` field from spec.md frontmatter exactly
   - Scenario D: Body is written to temp file, not passed as inline shell argument (avoids quoting issues)
   - **Coverage Target**: AC-US3-02 fully covered

**Implementation**:
1. Open `plugins/specweave/skills/pr/SKILL.md`
2. Expand Step 5 (Generate PR Body) with explicit markdown template:

```markdown
## Step 5 (expanded): PR Body Template

Write the following to `/tmp/sw-pr-body-{increment-id}.md`:

---
## Summary
{first 2-3 sentences from ## Problem Statement in spec.md}

## User Stories
{for each US in spec.md:}
- US-00N: {title} ({count} ACs)

## Acceptance Criteria
{for each AC (max 10):}
- [x] AC-USN-NN: {AC description, truncated to 100 chars}
{if total ACs > 10: append "...and N more ACs — see full spec"}

---
Generated by SpecWeave increment {increment-id}
---
```

3. Confirm `--body-file` flag is used with `gh pr create` (not `--body`) to avoid shell quoting problems
4. Clean up temp file after PR creation attempt (success or failure): `rm -f /tmp/sw-pr-body-{increment-id}.md`

---

### T-009: Add multi-repo (umbrella) flow to sw:pr SKILL.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** umbrella workspace with 2 child repos both having uncommitted/untracked changes
- **When** `sw:pr` runs
- **Then** 2 PRs are created (one per repo), both `PrRef` entries stored in metadata
- **Given** child repo A succeeds but repo B fails during `gh pr create`
- **When** `sw:pr` completes the loop
- **Then** repo A's `PrRef` is stored, repo B failure is logged as warning, skill exits 0
- **Given** a child repo has no changes (`git status --porcelain` empty)
- **When** `sw:pr` processes it
- **Then** the repo is skipped with an info log

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Scenario A: 2 repos with changes → 2 `PrRef` entries in `metadata.prRefs`
   - Scenario B: Repo has no changes → skip with "No changes in {repo}, skipping PR"
   - Scenario C: Second repo PR fails → first stored, warning for second, exit 0
   - Scenario D: Single-repo (no umbrella) → single-repo flow only (Steps 1-7)
   - **Coverage Target**: AC-US3-05 fully covered

**Implementation**:
1. Open `plugins/specweave/skills/pr/SKILL.md`
2. Before Step 3, add umbrella detection:

```markdown
## Step 2.5: Detect Single vs Multi-Repo Mode

1. Read `umbrella.enabled` from `.specweave/config.json`
2. Read `umbrella.childRepos` array (if any)
3. If `umbrella.enabled == true` AND `childRepos` is non-empty:
   → Enter **Multi-Repo Mode** (Step 4 below)
4. Else:
   → Run Steps 3-7 (Single-Repo Mode) for the current directory
```

3. Add Step 4 (Multi-Repo Flow):

```markdown
## Step 4: Multi-Repo Flow (Umbrella Mode)

For each `childRepo` in `umbrella.childRepos`:
  1. `cd {childRepo.path}`
  2. Run `git status --porcelain` — if empty: log "No changes in {childRepo.id}, skipping" and continue to next
  3. Get current branch: `git branch --show-current`
  4. If on `targetBranch`: ensure feature branch exists (same Step 2.7 logic from sw:do)
  5. Run Steps 3-7 (single-repo flow) scoped to this childRepo directory
  6. On success: store `PrRef` with `repo: "{childRepo.org}/{childRepo.name}"`
  7. On failure: log "WARNING: PR creation failed for {childRepo.id}: {error}" and continue (do NOT abort loop)

After loop: print summary table:
| Repo | Branch | PR URL | Status |
|------|--------|--------|--------|
| ...  | ...    | ...    | ...    |
```

---

### T-010: Add Step 8.5 (PR Creation) to sw:done SKILL.md

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `pushStrategy` is `"pr-based"` and `sw:done` completes Step 8 (`specweave complete` closes the increment)
- **When** Step 8.5 executes
- **Then** `Skill({ skill: "sw:pr" })` is invoked with the current increment ID
- **Given** `pushStrategy` is `"direct"`
- **When** `sw:done` runs
- **Then** Step 8.5 is skipped and Steps 9+ proceed unaffected
- **Given** `sw:pr` encounters an error
- **When** Step 8.5 handles it
- **Then** the increment remains closed, a warning is shown, and Step 9 continues normally

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Scenario A: pr-based strategy → `sw:pr` invoked after `specweave complete`
   - Scenario B: direct strategy → Step 8.5 block skipped entirely
   - Scenario C: `sw:pr` fails → increment still closed, warning displayed, Step 9 runs
   - **Coverage Target**: AC-US3-01 and AC-US3-04 covered

**Implementation**:
1. Open `plugins/specweave/skills/done/SKILL.md`
2. Find Step 8 (the `specweave complete` call that closes the increment)
3. Insert immediately after Step 8:

```markdown
### Step 8.5: PR Creation (PR-Based Only)

1. Read `cicd.pushStrategy` from `.specweave/config.json`
2. If `pushStrategy` != `"pr-based"` → skip this step, proceed to Step 9
3. Log: "Increment closed. Creating pull request for review..."
4. Invoke: `Skill({ skill: "sw:pr" })` passing the increment ID
5. `sw:pr` handles all branch pushing, PR creation, and metadata storage
6. If `sw:pr` returns an error or fails: log warning:
   "WARNING: PR creation failed. Increment is closed. Create PR manually from branch {branch}."
7. Proceed to Step 9 regardless of `sw:pr` outcome (increment closure is non-reversible)
```

4. Confirm Step 9 and all subsequent steps are untouched and correctly numbered

---

## User Story: US-004 - Enterprise Environment Promotion Configuration

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 4 total, 4 completed

---

### T-011: Add ReleaseConfig and EnvironmentConfig interfaces to CiCdConfig (P2)

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** the `CiCdConfig` TypeScript interface
- **When** a developer inspects the type
- **Then** it contains `release?: { strategy: 'trunk' | 'env-promotion' }` and `environments?: { name: string; branch: string }[]`
- **Given** `cicd.release` is absent from config
- **When** defaults are applied
- **Then** `release.strategy` defaults to `"trunk"` and `environments` is not required

**Test Cases**:
1. **Unit**: `src/core/config/types.test.ts` (or `npx tsc --noEmit`)
   - `testReleaseConfigOptional()`: Create `CiCdConfig` without `release` — no TS error
   - `testEnvironmentConfigShape()`: Construct `EnvironmentConfig` with `name` and `branch` — compiles
   - `testDefaultReleaseTrunk()`: `DEFAULT_CONFIG.cicd.release.strategy` equals `"trunk"`
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/core/config/types.ts` (T-001 already has the file open)
2. Add `ReleaseConfig` interface:
   ```typescript
   export interface ReleaseConfig {
     strategy: 'trunk' | 'env-promotion'; // default: "trunk"
   }
   ```
3. Add `EnvironmentConfig` interface:
   ```typescript
   export interface EnvironmentConfig {
     name: string;   // e.g., "dev", "staging", "prod"
     branch: string; // e.g., "develop", "staging", "main"
   }
   ```
4. Add `release?: ReleaseConfig` and `environments?: EnvironmentConfig[]` to `CiCdConfig`
5. Update `DEFAULT_CONFIG.cicd` to include `release: { strategy: 'trunk' }` (no default `environments`)
6. Run `npx tsc --noEmit`

---

### T-012: Extend config-loader to parse and merge release and environments (P2)

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `config.json` with `cicd.release.strategy: "env-promotion"` and `cicd.environments: [{name: "dev", branch: "develop"}, {name: "prod", branch: "main"}]`
- **When** the config loader reads the file
- **Then** `config.release.strategy` equals `"env-promotion"` and `config.environments` has 2 entries in original order
- **Given** config without `cicd.release`
- **When** merged
- **Then** `release.strategy` defaults to `"trunk"` and `environments` is `undefined`

**Test Cases**:
1. **Unit**: `src/core/cicd/config-loader.test.ts`
   - `testParsesEnvPromotion()`: Config with `release.strategy: "env-promotion"` + 3-item `environments` → both parsed
   - `testEnvironmentsOrderPreserved()`: 3-item array → merged result has same 3 items in same order
   - `testDefaultReleaseTrunk()`: Config without `release` → `release.strategy == "trunk"`
   - `testEnvironmentsUndefinedByDefault()`: Config without `environments` → `environments` is `undefined`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/core/cicd/config-loader.ts`
2. Extend `RawConfig.cicd` with:
   ```typescript
   release?: { strategy?: string };
   environments?: Array<{ name: string; branch: string }>;
   ```
3. In `loadFromConfigFile()`, parse and pass through `release` and `environments`:
   ```typescript
   if (rawConfig.cicd?.release) { config.release = rawConfig.cicd.release as ReleaseConfig; }
   if (rawConfig.cicd?.environments) { config.environments = rawConfig.cicd.environments; }
   ```
4. In `mergeConfigs()`, merge with defaults:
   ```typescript
   release: { ...defaults.release, ...configFile.release },
   environments: configFile.environments ?? defaults.environments,
   ```
5. Run `npx vitest run src/core/cicd/config-loader.test.ts`

---

### T-013: Implement env-promotion target branch selection in sw:pr (P2)

**User Story**: US-004
**Satisfies ACs**: AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `release.strategy` is `"env-promotion"` and `environments` is `[{name: "dev", branch: "develop"}, {name: "prod", branch: "main"}]`
- **When** `sw:pr` resolves the PR target branch
- **Then** `targetBranch` is `"develop"` (first environment branch)
- **Given** `release.strategy` is `"trunk"` (default)
- **When** `sw:pr` resolves the target branch
- **Then** `targetBranch` is `cicd.git.targetBranch` (e.g., `"main"`)
- **Given** `env-promotion` but `environments` array is empty
- **When** target branch is resolved
- **Then** falls back to `cicd.git.targetBranch` with a warning

**Test Cases**:
1. **Integration (SKILL behavioral)**:
   - Scenario A: `env-promotion` + 2 environments → PR targets `"develop"`
   - Scenario B: `trunk` strategy → PR targets `"main"`
   - Scenario C: `env-promotion` + empty environments → fallback to `git.targetBranch` + warning
   - **Coverage Target**: AC-US4-03 fully covered

**Implementation**:
1. Open `plugins/specweave/skills/pr/SKILL.md`
2. Expand Step 2 (Determine Target Branch) with the env-promotion logic (already partially written in T-007)
3. Confirm the expanded step reads:
   ```
   - If release.strategy == "env-promotion" AND environments[0] exists: targetBranch = environments[0].branch
   - If release.strategy == "env-promotion" AND environments is empty: warn + fall back to git.targetBranch
   - Else: targetBranch = git.targetBranch (default "main")
   ```
4. Confirm `--base {targetBranch}` in the `gh pr create` call uses the resolved value

---

### T-014: Write integration tests for full PR-based config and metadata round-trip (P2)

**User Story**: US-004
**Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US3-03, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** a full config with `pushStrategy: "pr-based"`, `git.branchPrefix: "feat/"`, `release.strategy: "env-promotion"`, and 3-item `environments`
- **When** the config loader parses it
- **Then** all fields are accessible and correctly typed
- **Given** a `PrRef` is added to an increment via `addPrRef`
- **When** `getPrRefs` is called
- **Then** the returned array exactly matches the stored refs (round-trip fidelity)
- **Given** a minimal config with no `pushStrategy`
- **When** loaded
- **Then** `pushStrategy` is `"direct"` (backward-compatible default)

**Test Cases**:
1. **Integration**: `src/core/cicd/pr-workflow.integration.test.ts`
   - `testFullPrBasedConfig()`: Parse full config JSON → assert `pushStrategy`, `git`, `release`, `environments` all correct
   - `testMetadataPrRefsRoundTrip()`: `addPrRef` then `getPrRefs` → values match input exactly
   - `testDefaultDirectStrategy()`: Minimal config → `pushStrategy == "direct"`, `git.branchPrefix == "sw/"`
   - `testEnvPromotionTargetResolution()`: `release.strategy == "env-promotion"` + 2 environments → first branch is lowest env
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/core/cicd/pr-workflow.integration.test.ts`
2. Test 1: Construct full config JSON string, call `loadFromConfigFile()` equivalent, assert all fields
3. Test 2: Use a temp directory with `MetadataManager`; call `addPrRef` with a known `PrRef`; call `getPrRefs`; assert deep equality
4. Test 3: Load minimal `{}` config; assert `pushStrategy == "direct"` and `git.branchPrefix == "sw/"`
5. Test 4: Config with `env-promotion` + 2 environments; assert `environments[0].branch` is the correct lowest-env target
6. Run `npx vitest run src/core/cicd/pr-workflow.integration.test.ts`
