# SpecWeave Core Sync Engine - Comprehensive Analysis

## Executive Summary

The SpecWeave sync engine is a **multi-tier orchestration system** that integrates increment lifecycle (spec planning → task execution → closure) with external tools (GitHub, JIRA, Azure DevOps). The architecture consists of:

1. **Type System** (`sync-profile.ts`, `sync-config.ts`, `sync-settings.ts`) - Configuration and permission models
2. **Lifecycle Hooks** (`LifecycleHookDispatcher.ts`) - Event-driven sync triggers at increment milestones
3. **Core Infrastructure** (Config Manager, Progress Tracker, Lock Manager) - State management
4. **Living Docs Sync** - Converts increments to markdown specs in `.specweave/docs/internal/specs/`
5. **External Sync** (GitHub, JIRA, ADO plugins) - Bidirectional sync with external tools
6. **CLI Commands** - User-facing sync operations (`sync-progress`, `sync-status`, `sync-health`)

---

## Complete Sync Lifecycle

### Phase 1: Increment Creation → Planning

```
/sw:increment "Feature X"
    ↓
create-increment.ts (creates metadata.json, spec.md, plan.md, tasks.md)
    ↓
LifecycleHookDispatcher.onIncrementPlanned()
    ├→ hooks.post_increment_planning.sync_living_docs
    │   ├→ LivingDocsSync.syncIncrement(incrementId)
    │   │   ├→ FeatureIDManager (allocates FS-XXX)
    │   │   ├→ Parse spec.md (extract user stories, ACs)
    │   │   ├→ Write .specweave/docs/internal/specs/{project}/FS-XXX/
    │   │   ├→ Write user story files (us-*.md)
    │   │   └→ Chain: GitHubFeatureSync (plugin-level) creates GH issue
    │   └→ Result: Living docs structure created
    │
    └→ hooks.post_increment_planning.auto_create_github_issue
        └→ Now handled by GitHubFeatureSync (plugin)
```

**Key Files:**
- `src/cli/commands/create-increment.ts` - Increment creation
- `src/core/hooks/LifecycleHookDispatcher.ts:onIncrementPlanned()` - Hook dispatch
- `src/core/living-docs/living-docs-sync.ts` - Living docs generation
- `src/core/living-docs/feature-id-manager.ts` - FS-XXX allocation

**Config Key:** `config.json → hooks.post_increment_planning.sync_living_docs`

---

### Phase 2: Task Completion

```
Task marked complete in tasks.md
    ↓
sync-task.ts (or auto via hook)
    ↓
LifecycleHookDispatcher.onTaskCompleted()
    ├→ ACGate.shouldSyncExternal() [checks if this AC now satisfied]
    │   └→ Only sync if NEW AC transitioned from unchecked to satisfied
    │
    ├→ hooks.post_task_completion.sync_tasks_md
    │   └→ LivingDocsSync.syncIncrement(incrementId)
    │       ├→ Sync tasks.md → spec.md ACs
    │       ├→ Update us-*.md files (checkbox status)
    │       ├→ Chain: GitHubFeatureSync updates GH issue checkboxes
    │       └→ [Optional] External sync via JIRA/ADO plugins
    │
    └→ hooks.post_task_completion.external_tracker_sync
        └→ Fallback: If external_tracker_sync enabled but sync_tasks_md not,
           run LivingDocsSync anyway to chain external sync
```

**Key Files:**
- `src/cli/commands/sync-task.ts` - Task completion sync
- `src/core/sync/ac-gate.ts` - AC transition detection
- `src/core/hooks/LifecycleHookDispatcher.ts:onTaskCompleted()` - Task hook
- `src/core/living-docs/living-docs-sync.ts` - Updated spec sync

**Config Keys:**
- `config.json → hooks.post_task_completion.sync_tasks_md`
- `config.json → hooks.post_task_completion.external_tracker_sync`

---

### Phase 3: AC/Checkbox Sync to External Tools

```
LivingDocsSync chains to GitHubFeatureSync (plugin)
    ↓
sync-progress.ts (explicit manual command)
    ├→ Step 1: Sync ACs (tasks.md → spec.md)
    ├→ Step 2: Sync to living docs (LivingDocsSync)
    ├→ Step 3: Detect external tool config (GitHub/JIRA/ADO)
    ├→ Step 4: Auto-create external issues if missing
    │   ├→ autoCreateExternalIssue(projectRoot, incrementId, provider)
    │   ├→ Check metadata.json for existing issue
    │   └→ If missing → create and link
    │
    └→ Step 5: Sync AC checkboxes to external tools
        ├→ GitHub: GitHubACCheckboxSync.syncACCheckboxesToGitHub()
        │   ├→ Find/create issue from metadata.github.issue
        │   ├→ Update issue body with AC checkboxes
        │   └→ [Optional] Add progress comment
        │
        ├→ JIRA: syncACProgressToProviders() (v1.0.357)
        │   ├→ Map user stories to JIRA issues
        │   ├→ Update issue description with ACs
        │   └→ [Optional] Auto-transition on completion
        │
        └→ ADO: syncACProgressToProviders() (v1.0.357)
            ├→ Map user stories to ADO work items
            ├→ Update work item description
            └→ [Optional] Auto-transition on completion
```

**Key Files:**
- `src/cli/commands/sync-progress.ts` - Main sync command (5-step pipeline)
- `src/sync/external-issue-auto-creator.ts` - External issue creation
- `plugins/specweave-github/lib/github-ac-checkbox-sync.ts` - GitHub checkbox sync
- `src/core/ac-progress-sync.ts` - JIRA/ADO AC progress

**Permissions:**
- `config.json → sync.settings.canUpsertInternalItems` - Create external issues
- `config.json → sync.settings.canUpdateExternalItems` - Update external issues
- `config.json → sync.settings.canUpdateStatus` - Update status only

---

### Phase 4: Increment Closure

```
/sw:done incrementId
    ↓
completeIncrement() + LifecycleHookDispatcher.onIncrementDone()
    ├→ hooks.post_increment_done.update_living_docs_first
    │   └→ LivingDocsSync.syncIncrement() [if enabled]
    │
    ├→ hooks.post_increment_done.sync_to_github_project
    │   └→ GitHub Projects V2 board sync (if configured)
    │
    ├→ hooks.post_increment_done.close_github_issue
    │   └→ SyncCoordinator.syncIncrementClosure()
    │       ├→ Close GitHub issue (via GH plugin)
    │       ├→ Close JIRA issue (if configured)
    │       └→ Close ADO work item (if configured)
    │
    └→ Archive increment
        └→ Move to .specweave/increments/_archive/
```

**Key Files:**
- `src/core/increment/status-commands.ts` - completeIncrement()
- `src/core/hooks/LifecycleHookDispatcher.ts:onIncrementDone()` - Closure hooks
- `src/sync/sync-coordinator.ts` - Multi-provider closure

**Config Keys:**
- `config.json → hooks.post_increment_done.update_living_docs_first`
- `config.json → hooks.post_increment_done.sync_to_github_project`
- `config.json → hooks.post_increment_done.close_github_issue`
- `config.json → sync.settings.autoSyncOnCompletion` - Global on/off (default: true)

---

## Type System & Configuration

### 1. Sync Profiles (`sync-profile.ts`)

**Multi-tier architecture:**

```typescript
SyncProfiles {
  defaultProfile: string;  // Fallback for increments without explicit profile
  profiles: {
    "github-main": SyncProfile {
      provider: 'github';
      strategy: 'intelligent' | 'custom';

      config: GitHubConfig {
        owner: string;
        repos?: string[];           // Multi-repo: auto-classify stories
        masterRepo?: string;        // Master+nested pattern
        projectV2Number?: number;   // GitHub Projects V2 (NEW v1.0.235)
        customQuery?: string;       // Power users: raw GraphQL
        hierarchyMapping?: HierarchyMappingConfig;
      };

      timeRange: {
        default: '1W' | '2W' | '1M' | '3M' | '6M' | '1Y' | 'ALL';
        max: TimeRangePreset;
      };
      rateLimits?: RateLimitConfig;
    }
  }
}
```

**Hierarchy Mapping (v0.30.6+):**

Flexible mapping for 3/4/5-level hierarchies:

```typescript
HierarchyMappingConfig {
  epicLevelTypes: string[];      // [Optional] Top strategic (e.g., ["Capability"])
  featureLevelTypes: string[];   // [Required] Feature containers (e.g., ["Epic", "Feature"])
  userStoryTypes?: string[];     // [Optional] Defaults to standard types
  taskTypes?: string[];          // [Optional] Defaults to ["Task", "Sub-task"]
}
```

**Examples:**
- **ADO Scrum (3 levels):** Epic → PBI → Task
  ```json
  { "epicLevelTypes": [], "featureLevelTypes": ["Epic"] }
  ```

- **ADO SAFe (5 levels):** Capability → Epic → Feature → Story → Task
  ```json
  { "epicLevelTypes": ["Capability"], "featureLevelTypes": ["Epic", "Feature"] }
  ```

- **JIRA (3 levels):** Epic → Story → Sub-task
  ```json
  { "epicLevelTypes": [], "featureLevelTypes": ["Epic", "Feature"] }
  ```

---

### 2. Sync Settings (`sync-settings.ts`)

**Three independent permission flags (v0.24.0+):**

```typescript
SyncSettings {
  canUpsertInternalItems: boolean;   // Q1: Create/update internal work items in external tools
  canUpdateExternalItems: boolean;   // Q2: Update externally-created items
  canUpdateStatus: boolean;           // Q3: Update status field only
}
```

**Permission Flows:**

| Flow | canUpsert | canUpdate | canStatus | Outcome |
|------|-----------|-----------|-----------|---------|
| **Internal → External** | true | - | - | Create GH issue, JIRA issue, ADO item from increment |
| **External → SpecWeave** | false | true | - | Read-only: external items stay as living docs, no automatic creation |
| **Status Only** | - | - | true | Both flows: update status field when ACs complete |
| **Read-Only** | false | false | false | No sync (manual management) |
| **Bidirectional** | true | true | true | Full two-way sync |

---

### 3. Sync Config Validation (`sync-config-validator.ts`)

**Immutable architectural rules:**

1. `incrementToLivingDocs` MUST be `'one-way'` (ALWAYS)
2. `autoIncrementCreation` MUST be `false` (FORBIDDEN)
3. All permissions enabled = full sync mode (⚠️ warning: conflict risk)

---

## Core Infrastructure

### Config Management (`config-manager.ts`)

- **Load:** `.specweave/config.json` with auto-migration
- **Merge:** User config + defaults
- **Watch:** Single-project detection and auto-upgrade to multi-project
- **Validation:** Via sync-config-validator
- **Error Handling:** JSON parse errors handled, missing config returns defaults

**Key Methods:**
- `read()` - Async load with migration
- `readSync()` - Synchronous load
- `write()` - Persist to disk (called after migration)

---

### Progress Tracking (`progress-tracker.ts`)

**Real-time progress reporting during bulk imports:**

- **ASCII Progress Bar:** 30-character visual indicator
- **ETA Calculation:** Linear extrapolation from elapsed time
- **Item Status Tracking:** pending → success | error
- **Configurable Update Frequency:** Batch updates to reduce output spam

**Used by:** Import operations, large sync jobs

---

### Lifecycle Hook Dispatcher (`LifecycleHookDispatcher.ts`)

**Four lifecycle hooks:**

1. **`onIncrementPlanned()`** → post_increment_planning
   - sync_living_docs
   - auto_create_github_issue

2. **`onTaskCompleted()`** → post_task_completion
   - sync_tasks_md
   - external_tracker_sync
   - [AC Gate filter applied]

3. **`onIncrementDone()`** → post_increment_done
   - update_living_docs_first
   - sync_to_github_project
   - close_github_issue

**Dispatch Properties:**
- ✅ **Non-blocking:** All async, fire-and-forget (except onIncrementDone)
- ✅ **Error-isolated:** Catch + log, never crash
- ✅ **Test-aware:** Skipped when `VITEST` env var set (can bypass with `_bypassTestGuard`)
- ✅ **Configurable:** Each hook can be independently enabled/disabled

---

## Living Docs Sync Pipeline

### Architecture

```
increment spec.md (plan phase)
    ↓
LivingDocsSync.syncIncrement()
    ├→ Parse spec.md (extract title, user stories, ACs)
    ├→ FeatureIDManager.getFeatureIdForIncrement()
    │   ├→ Greenfield: Allocate new FS-XXX
    │   └→ Brownfield: Detect from external link
    │
    ├→ Generate .specweave/docs/internal/specs/{project}/FS-XXX/
    │   ├→ FEATURE.md (title, description, status)
    │   ├→ us-XXXX.md (for each user story)
    │   └→ README.md [optional]
    │
    └→ [CHAIN] GitHubFeatureSync (plugin)
        ├→ Create GitHub issue for FS-XXX
        ├→ Link to milestone
        └→ Update on subsequent syncs
```

**Key Files:**
- `src/core/living-docs/feature-id-manager.ts` - Feature ID allocation
- `src/core/living-docs/sync-helpers/generators.ts` - Markdown generation
- `plugins/specweave-github/lib/github-feature-sync.ts` - GitHub integration (plugin)

**Project Detection Priority:**
1. `multiProject.activeProject` (config)
2. Git remote (GitHub repo name, if detectable)
3. "default" (fallback)

---

## External Sync Orchestration

### Strategy: Intelligent vs. Custom

**Intelligent (default):**
- User stories auto-classified to projects based on content
- Works with 1 project (backward compat) or N projects
- Recommended for 90% of users

**Custom:**
- Raw query syntax: JQL (JIRA), GraphQL (GitHub), WIQL (ADO)
- For power users with complex filtering
- e.g., `"project IN (FE, BE) AND labels IN (sprint-42)"`

### Per-Provider Pattern

**GitHub:**
- Single repo: `owner` + `repo`
- Multiple repos: `owner` + `repos[]` (intelligent auto-classify)
- Master+nested: `masterRepo` + `repos[]` (epics in master, stories in nested)
- Projects V2: `projectV2Enabled` + `projectV2Number` + status field mapping

**JIRA:**
- Single project: `domain` + `projectKey`
- Multiple projects: `domain` + `projects[]` (intelligent)
- Board-based teams (v0.29.0): `boardMapping` (single JIRA project, multiple boards → SpecWeave projects)
- Custom: `domain` + `customQuery` (raw JQL)

**ADO:**
- Single project: `organization` + `project`
- Multiple projects: `organization` + `projects[]`
- Area paths: `organization` + `project` + `areaPaths[]` (team-based)
- Area path mapping (v0.29.0): `areaPathMapping` (single project, area paths → SpecWeave projects)
- Custom: `organization` + `customQuery` (raw WIQL)

---

## CLI Sync Commands

### 1. `sync-progress` (5-step pipeline)

**Purpose:** Complete progress sync from tasks → external tools

**Steps:**
1. Sync ACs (tasks.md → spec.md)
2. Sync to living docs
3. Detect external tool config
4. Auto-create external issues if missing
5. Sync AC checkboxes to external tools

**Flags:**
- `--dry-run` - Simulate without changes
- `--no-create` - Skip auto-issue creation
- `--no-github` / `--no-jira` / `--no-ado` - Skip provider
- `--force` - Force living docs sync
- `--reconcile` - Clean up stale/duplicate milestones (GitHub only)

**Output:** Comprehensive progress report with warnings/errors

---

### 2. `sync-status`

**Purpose:** Show sync health (retry queue, circuit breakers, rate limits)

**Outputs:**
- Retry queue: pending / failed counts
- Circuit breaker states per provider (closed / open / half-open)
- Rate limit status (remaining %, threshold)
- Recent errors (last 24h)
- Overall health: ✅ or ⚠️

**Exit Codes:**
- 0: Healthy
- 1: Issues detected (open circuit, pending retries)

---

### 3. `sync-health`

**Purpose:** Validate external integrations (credentials, permissions, access)

**Checks:**
- GitHub: Token validity, repo access, rate limits
- JIRA: Domain/auth, project access, permissions
- ADO: Organization access, project/team visibility

**Output:** Per-provider health + overall status

**Exit Codes:**
- 0: All pass
- 1: One or more fail
- 2: No providers configured

---

### 4. Other Sync Commands

- **`sync-task`:** Mark task complete + trigger hooks
- **`sync-gaps`:** Detect spec-to-code discrepancies
- **`sync-living-docs`:** Manual living docs sync trigger
- **`sync-retry`:** Retry failed sync operations
- **`sync-scheduled`:** Scheduler for recurring syncs
- **`sync-setup`:** Interactive setup wizard (GitHub/JIRA/ADO)

---

## Key Architectural Decisions

### 1. One-Way Increment → Living Docs

**Why immutable:**
- Increments are the source of truth
- Living docs are derived artifacts
- Prevents conflicting bidirectional writes

**Exception:** External items can be imported as living docs ONLY (no auto-increment creation)

---

### 2. Three-Permission Model

**Why separate permissions:**
- `canUpsertInternalItems`: Asymmetric trust (allow create only for internal)
- `canUpdateExternalItems`: Sync risk control (stricter than status-only)
- `canUpdateStatus`: Lightweight status updates without full sync overhead

**All default to true** (full sync works out of the box) but can be disabled for safety.

---

### 3. AC Gate Filter

**Purpose:** Prevent external noise from partial task completion

- Only sync when NEW AC transitions from unchecked → satisfied
- Avoids spamming external tool on every minor task change
- Reduces notification fatigue

---

### 4. Async Hook Pattern

**Why non-blocking:**
- Hooks fire after task marked complete, don't block UX
- Failures isolated + logged, never crash user workflow
- Allows independent plugin execution (GitHub plugin separate from JIRA)

**Exception:** `onIncrementDone` is awaited (closure is critical, must wait for sync)

---

## Missing Features & Gaps

### 1. Error Handling Gaps

**Issue:** Silent failures in progress tracking
```typescript
// File: sync-progress.ts:755
console.warn(`❌ Failed to check existing GitHub issue: ${error}`);
// Returns false instead of throwing — hides real errors
```
**Risk:** Duplicate issues created if issue exists but check fails

---

### 2. Race Conditions in Multi-User Environments

**Issue:** No lock mechanism for concurrent sync
- Task A marks complete → triggers living docs sync
- Task B marks complete simultaneously → same increment
- **Result:** Living docs write conflict, data loss

**Mitigated by:** LockManager exists but not always used
```typescript
// File: living-docs-sync.ts:148
// TOCTOU mitigation - check active folder BEFORE sync work.
// Not truly atomic (fs.access + later reads are separate syscalls)
```

---

### 3. Incomplete AC Progress Mapping

**Issue:** v1.0.358+ auto-maps unmapped user stories, but:
- Only maps at sync time (not during increment creation)
- No UI to show unmapped user stories
- Silent default mapping (user might not know)

---

### 4. Missing Retry Logic for Transient Failures

**Issue:** Rate limit or network timeout → silently logged, not retried
- Retry queue exists (`SyncRetryQueue`) but not integrated into all commands
- Manual retry needed: `sync-retry` command (user must remember)

---

### 5. Circuit Breaker Not Fully Integrated

**Issue:** Circuit breaker registry exists (`CircuitBreakerRegistry`) but:
- Not hooked into sync-progress command
- Status shown in `sync-status` but commands ignore it
- Could sync to broken provider, get error, then retry (wasting quota)

---

### 6. No Distributed Routing for Multi-Repo + Multi-Project

**Issue:** When project ID is ambiguous:
- GitHub: Falls back to global config (v1.0.348)
- JIRA/ADO: Manual resolution needed

**Partial fix:** `resolveSyncTarget()` handles some cases, but:
- Not integrated into all commands
- No user-facing routing config

---

### 7. Dead Code: Deprecated Functions

**Identified:**
- `SyncCoordinator.createGitHubIssuesForUserStories()` (marked deprecated, v0348)
- Legacy `isSimpleStrategy()` (aliased, kept for backward compat)
- Old `SyncSettings` migration (syncDirection → three-part permissions)

---

### 8. Missing Test Coverage for Sync Chains

**Issue:** Test files exist but coverage gaps:
- ✅ `sync-progress.test.ts` - Tests parseArgs, provider detection
- ✅ `sync-health.test.ts` - Integration health checks
- ❌ No tests for living-docs-sync → github-feature-sync chain
- ❌ No tests for AC gate + external sync orchestration
- ❌ No multi-provider chaos tests (GitHub fails, JIRA succeeds, etc.)

---

### 9. Unclear Permission Semantics for Import

**Issue:** `canUpdateExternalItems=false` but importing external items still happens
- External items imported as living docs ONLY (not increments)
- But what if user later marks an imported task as complete?
- Spec says: "NO automatic creation of increments for external items"
- **Actual:** No enforcement mechanism; relies on user behavior

---

### 10. Platform Suffix ID System (Incomplete)

**Issue:** v1.0.233+ introduced platform-specific IDs (FS-042G for GitHub)
- System exists: `parseId()`, `SUFFIX_MAP`, `PLATFORM_MAP`
- **But:** Not used in AC sync operations
- Living docs still use generic FS-XXX (no suffix)
- External sync uses generic metadata (externalLinks.github.issues, no suffix in key)

**Result:** Can't distinguish which platform "FS-042" lives on without metadata

---

## Single vs. Multi-Repo Sync

### Patterns Supported

**Greenfield (Single Repo):**
- Config: `sync.github.owner` + `sync.github.repo`
- Sync: All increments → single repo

**Brownfield (Multi-Repo + Multi-Project):**
- Config: `sync.github.owner` + `sync.github.repos[]`
- Sync: Auto-classify user stories to repos
- **Smart routing:** `resolveSyncTarget()` detects project from spec frontmatter

**Master + Nested (Enterprise):**
- Config: `sync.github.masterRepo` + `sync.github.repos[]`
- Pattern: Epics in master, stories in nested repos
- **Challenge:** Cross-linking (must maintain issue references)

### Known Issues

1. **Auto-classification confidence:** Default 0.3 (30%) — easy to miss
2. **No fallback routing:** If classification fails, uses default profile
3. **Distributed ADO/JIRA:** Requires manual `areaPathMapping` / `boardMapping` setup

---

## Hook Execution Order & Dependencies

### Task Completion Flow

```
Task marked [x] in tasks.md
    ↓
sync-task.ts dispatches onTaskCompleted()
    ↓
[1] ACGate.shouldSyncExternal()?
    ├→ true: proceed
    └→ false: skip external sync (for partial ACs)
    ↓
[2] sync_tasks_md hook?
    ├→ true: LivingDocsSync.syncIncrement() [ALWAYS RUNS]
    │   ├→ Updates spec.md ACs
    │   ├→ Updates us-*.md files
    │   └→ [CHAINS] GitHubFeatureSync updates GH issue
    └→ false: proceed
    ↓
[3] external_tracker_sync hook?
    ├→ true AND sync_tasks_md already ran: use LivingDocsSync result
    ├→ true AND sync_tasks_md didn't run: call LivingDocsSync anyway
    └→ false: skip
    ↓
[4] Post-sync operations (if external_tracker_sync):
    ├→ syncACProgressToProviders() [JIRA/ADO status transitions]
    └→ [CHAINS] Plugin-level sync for GitHub
```

**Critical:** If EITHER hook enabled, LivingDocsSync runs. Can't disable it entirely without disabling both hooks.

---

### Increment Done Flow

```
/sw:done incrementId
    ↓
[1] autoSyncOnCompletion check (config.sync.settings, default true)
    ├→ false: skip all hooks
    └→ true: proceed
    ↓
[2] update_living_docs_first?
    ├→ true: LivingDocsSync.syncIncrement()
    └→ false: skip
    ↓
[3] sync_to_github_project?
    ├→ true: GitHub Projects V2 board sync (if configured)
    └→ false: skip
    ↓
[4] close_github_issue?
    ├→ true: SyncCoordinator.syncIncrementClosure()
    │   ├→ Close GH issue
    │   ├→ Close JIRA issue
    │   └→ Close ADO work item
    └→ false: skip (manual closure)
    ↓
[5] Archive increment
    └→ .specweave/increments/_archive/
```

**Note:** Hooks run SEQUENTIALLY (not parallel) — GitHub closure might fail, blocking JIRA/ADO

---

## Test Coverage & Validation

### Existing Tests

- ✅ `sync-progress.test.ts` - 100+ test cases (helper functions)
- ✅ `sync-health.test.ts` - Integration health checks
- ✅ `sync-status.test.ts` - Status display
- ✅ `sync-gaps.test.ts` - Discrepancy detection
- ✅ CLI integration tests

### Coverage Gaps

1. **Living Docs → External Chain**
   - No e2e tests for LivingDocsSync → GitHubFeatureSync → issue creation
   - Manual verification only

2. **Multi-Provider Orchestration**
   - No chaos tests: GitHub fails, JIRA succeeds
   - No interleaved sync tests: concurrent tasks in same increment

3. **AC Gate Logic**
   - Tested in isolation, not end-to-end with hooks

4. **Retry + Circuit Breaker**
   - Modules exist but not integrated into sync-progress command
   - No tests for transient failure recovery

5. **Distributed Routing**
   - `resolveSyncTarget()` has unit tests
   - No integration tests with real multi-repo setups

---

## Recommendations

### High Priority

1. **Add integration tests for living-docs-sync → external-sync chain**
   - Verify GH issue creation from increment spec
   - Test JIRA/ADO follow-up

2. **Integrate circuit breaker + retry queue into sync-progress**
   - Check circuit state before external sync
   - Automatic retry for transient failures

3. **Implement atomic living docs sync**
   - Add file locking or transaction semantics
   - Prevent partial writes on failure

4. **Add user visibility for unmapped user stories**
   - Show unmapped stories in `/sw:progress` output
   - Suggest mappings for auto-fix

### Medium Priority

5. **Implement proper error propagation in progress tracking**
   - Bubble up real errors instead of silent failures
   - Add error details to metadata for debugging

6. **Add chaos tests for multi-provider sync**
   - Simulate GitHub failure → JIRA succeeds scenario
   - Verify partial success handling

7. **Deprecate/remove dead code**
   - Deprecated SyncCoordinator methods
   - Legacy sync direction migration (v0.24.0)

8. **Document platform suffix IDs in implementation**
   - Align living docs / external sync on FS-042G naming
   - Or remove suffix system if not fully utilized

### Low Priority

9. **Add routing visualization**
   - CLI command to show which project/repo each story routes to
   - Help debug auto-classification issues

10. **Performance optimization**
    - Batch external API calls (combine 10 AC updates → 1 API call)
    - Cache rate limit status to avoid redundant checks

---

## Configuration Examples

### Minimal Single-Repo Setup

```json
{
  "sync": {
    "settings": {
      "canUpsertInternalItems": true,
      "canUpdateExternalItems": true,
      "canUpdateStatus": true
    },
    "profiles": {
      "github": {
        "provider": "github",
        "config": {
          "owner": "myorg",
          "repo": "main-repo"
        },
        "timeRange": { "default": "1W", "max": "1Y" }
      }
    },
    "defaultProfile": "github"
  },
  "hooks": {
    "post_increment_planning": {
      "sync_living_docs": true,
      "auto_create_github_issue": true
    },
    "post_task_completion": {
      "sync_tasks_md": true,
      "external_tracker_sync": true
    },
    "post_increment_done": {
      "update_living_docs_first": true,
      "close_github_issue": true
    }
  }
}
```

### Multi-Project JIRA + ADO

```json
{
  "sync": {
    "profiles": {
      "jira": {
        "provider": "jira",
        "config": {
          "domain": "company.atlassian.net",
          "projects": ["FE", "BE", "MOBILE"],
          "intelligentMapping": true,
          "boardMapping": {
            "projectKey": "CORE",
            "boards": [
              { "boardId": 123, "boardName": "Frontend", "specweaveProject": "FE" },
              { "boardId": 456, "boardName": "Backend", "specweaveProject": "BE" }
            ]
          }
        },
        "timeRange": { "default": "2W", "max": "3M" }
      },
      "ado": {
        "provider": "ado",
        "config": {
          "organization": "myorg",
          "project": "MainProduct",
          "areaPathMapping": {
            "project": "MainProduct",
            "mappings": [
              { "areaPath": "MainProduct\\Frontend", "specweaveProject": "FE" },
              { "areaPath": "MainProduct\\Backend", "specweaveProject": "BE" }
            ]
          }
        },
        "timeRange": { "default": "2W", "max": "3M" }
      }
    },
    "defaultProfile": "jira"
  }
}
```

---

## Conclusion

The SpecWeave sync engine is a **well-architected multi-tier system** with:

✅ **Strengths:**
- Clear separation of concerns (types, hooks, living docs, external sync)
- Extensible provider pattern (GitHub, JIRA, ADO)
- Non-blocking hooks prevent UX blocking
- Comprehensive permission model
- Three-part validation (SyncSettings, SyncOrchestrationConfig, SyncConfigValidator)

⚠️ **Weaknesses:**
- Silent failures in error handling
- Race conditions in multi-user scenarios
- Incomplete platform suffix ID system
- Gaps in circuit breaker / retry integration
- Limited test coverage for sync chains

**Risk Level:** Medium
- Single-repo, single-provider setups are stable
- Multi-repo + multi-provider introduces coordination risks
- Recommend test coverage improvements before production deployment

---

## Key Files Reference

| File | Purpose | Key Decision |
|------|---------|--------------|
| `sync-profile.ts` | Provider config types | Multi-tier architecture |
| `sync-settings.ts` | Permission model | Three-part permissions |
| `sync-config.ts` | Orchestration config | Scheduler + permissions + discrepancy |
| `LifecycleHookDispatcher.ts` | Hook dispatch | Non-blocking async pattern |
| `living-docs-sync.ts` | Spec → Markdown | Feature ID allocation + project detection |
| `sync-progress.ts` | 5-step sync pipeline | Explicit sync command (vs. implicit hooks) |
| `sync-coordinator.ts` | Multi-provider closure | Closure metrics + provider routing |
| `sync-target-resolver.ts` | Distributed routing | Spec-based project detection |
| `config-manager.ts` | Config loading | Auto-migration support |
