# SpecWeave Import → Work → Sync → Close Lifecycle Analysis

**Research Date**: 2026-03-16
**Scope**: Complete import flow, living docs integration, and external sync architecture
**Status**: Comprehensive analysis of import coordinator, item converter, living docs engine, and sync hooks

---

## Executive Summary

SpecWeave implements a **three-phase external tool integration lifecycle**:

1. **IMPORT PHASE** (User runs `/sw:import`)
   - Import worker fetches items from GitHub/JIRA/ADO
   - Item converter transforms them into living docs (`.specweave/docs/internal/specs/`)
   - Creates read-only spec references with external metadata (marked with 'E' suffix)
   - **Does NOT create increments** — only living docs for reference

2. **WORK PHASE** (User runs `/sw:do`, `/sw:increment`)
   - Developer can create new internal increments (normal flow)
   - Or implement existing external specs (ref-based flow)
   - Hook chain fires on task completion → syncs to external tools
   - Living docs updated via spec-to-living-docs-sync

3. **SYNC PHASE** (Automatic + manual)
   - **Content sync**: SpecWeave → External (specs, ACs push outward)
   - **Status sync**: External → SpecWeave (closure/state pulled inward)
   - **Permission gates**: Three-tier permission model controls what syncs

4. **CLOSURE PHASE** (User runs `/sw:done`)
   - Quality gates executed (grill, judge-llm, tests)
   - External items closed if Gate 3 enabled
   - All specs mark complete

---

## Part 1: Import Flow Architecture

### Import Coordinator (`src/importers/import-coordinator.ts`)

**Purpose**: Orchestrate multi-platform imports with progress tracking and aggregation.

**Key Features**:
- **Multi-repo GitHub support**: Import from multiple repos in single operation
- **Multi-project JIRA**: Import from multiple JIRA projects with board mappings
- **Multi-project ADO**: Import from multiple projects with area path mappings
- **Rate limiting**: Integrated RateLimiter prevents API quota exhaustion
- **Sync metadata tracking**: Updates sync metadata after import (when enabled)

**Configuration Structure**:
```typescript
interface CoordinatorConfig {
  // Single repo (backward compatible)
  github?: { owner, repo, token };

  // Multi-repo (preferred)
  githubRepositories?: RepoConfig[];

  // JIRA with project mappings
  jira?: {
    host: string;
    projectMappings?: Array<{
      projectKey: string;
      boardMappings: Array<{ boardId, boardName, specweaveFolder }>;
    }>;
  };

  // ADO with project mappings
  ado?: {
    orgUrl: string;
    projectMappings?: Array<{
      projectName: string;
      areaMappings: Array<{ areaPath, specweaveFolder }>;
    }>;
  };

  // Common options
  importConfig?: ImportConfig;
  enableRateLimiting?: boolean;
  enableSyncMetadata?: boolean;
  onProgressEnhanced?: (info: ProgressInfo) => void;
}
```

**Multi-Platform Importer Mapping**:
```
Single Platform Mode (backward compatible):
  importers.set('github', GitHubImporter)
  importers.set('jira', JiraImporter)
  importers.set('ado', ADOImporter)

Multi-Repo Mode (new):
  githubRepoImporters.set('github:owner/repo', GitHubImporter)
  jiraProjectImporters.set('jira:projectKey', JiraImporter)
  adoProjectImporters.set('ado:projectName', ADOImporter)
```

**Result Structure**:
```typescript
interface CoordinatorResult {
  results: ImportResult[];        // Per-platform results
  totalCount: number;             // Total items imported
  allItems: ExternalItem[];       // All items aggregated
  errors: Record<string, string[]>;
  platforms: ('github' | 'jira' | 'ado')[];
}
```

### Import Worker (`src/cli/workers/import-worker.ts`)

**Purpose**: Background worker that runs import in detached process, survives terminal close.

**Architecture**:
1. Spawned as child process by CLI command
2. Reads job config from `.specweave/state/jobs/{jobId}/config.json`
3. Updates progress atomically to `.specweave/state/background-jobs.json`
4. Logs to worker-specific log file
5. Writes result summary on completion

**Key Phases**:
```
1. INITIALIZATION
   ├── Load job configuration
   ├── Write PID file (with exclusive lock)
   ├── Setup signal handlers (SIGTERM, SIGINT)
   └── Dynamically import heavy modules

2. IMPORT EXECUTION
   ├── Initialize import coordinator
   ├── Setup progress callbacks
   ├── Execute coordinator.importAll()
   └── Log per-platform and per-repo breakdown

3. LIVING DOCS CONVERSION (CRITICAL)
   ├── Group items by external container
   ├── Initialize ItemConverter per project
   ├── Convert items to User Stories
   ├── Save to .specweave/docs/internal/specs/
   └── Log created feature folders

4. COMPLETION
   ├── Write result.json
   ├── Mark job complete
   └── Exit cleanly
```

**Critical Phase - Living Docs Conversion** (lines 273-319):
```typescript
// CRITICAL: Convert imported items to living docs
// Without this, items are fetched but NOT saved to specs folder!
if (result.totalCount > 0 && result.allItems.length > 0) {
  const specsDir = path.join(projectPath, '.specweave', 'docs', 'internal', 'specs');

  // Group items by source
  const groups = groupItemsByExternalContainer(result.allItems, projectPath);

  for (const group of groups) {
    const converter = new ItemConverter({
      specsDir,
      projectRoot: projectPath,
      enableFeatureAllocation: true,
      projectId: group.projectId,
      externalContainer: group.externalContainer,
      // ... callbacks
    });

    const convertedStories = await converter.convertItems(items);
    totalConverted += convertedStories.length;
  }
}
```

**Progress Tracking**:
- Atomic updates prevent race conditions when multiple resume attempts
- Tracks current count, total estimate, platform, percentage, rate
- Logs milestone updates every 100 items, on page changes, or on completion

### Item Converter (`src/importers/item-converter.ts`)

**Purpose**: Transform external items (GitHub/JIRA/ADO) into SpecWeave living docs.

**Key Constraint**:
> **Does NOT create increments** — only living docs. Increments are created separately via `/sw:increment`.

**Data Flow**:
```
External Items → ItemConverter → Living Docs FS
  (GitHub Issues)                (.specweave/docs/internal/specs/)
  (JIRA Stories)                 ├── project-id/
  (ADO Work Items)               │   ├── feature-folder/
                                 │   │   ├── FEATURE.md
                                 │   │   └── us-001-name.md
                                 │   └── feature-folder-2/
```

**Converted Structure**:
```typescript
interface ConvertedUserStory {
  id: string;              // US-001E (E = external)
  title: string;
  description: string;
  acceptanceCriteria: string[];
  priority?: string;       // P0-P4
  status: string;          // open, in-progress, completed
  externalId: string;      // GitHub/JIRA/ADO ID
  externalUrl: string;     // Link back to source
  sourceRepo?: string;     // For GitHub items
}
```

**Feature Allocation**:
- Creates folder structure: `{specsDir}/{projectId}/{feature-folder}/{us-files}`
- Feature folders group related user stories
- Auto-archival for old items (configurable via `autoArchiveAfterDays`)
- Collision detection prevents duplicate US IDs

**External Metadata Frontmatter**:
```yaml
---
title: "Login Form"
external_id: "github-issue-42"
external_url: "https://github.com/org/repo/issues/42"
external_platform: "github"
external_type: "issue"
external_status: "open"
origin: "imported"
imported_at: "2026-03-16T10:00:00Z"
---
```

**Hierarchy Mapping** (from `item-converter/hierarchy-mapper.ts`):

| Platform | Level 1 | Level 2 | Level 3 |
|----------|---------|---------|---------|
| GitHub | Milestone | Issue | Checkbox |
| JIRA | Epic | Story | Sub-task |
| ADO | Feature | User Story | Task |

**SpecWeave Maps To**:
- Feature Level (FS-XXX) ← Epic/Feature
- User Story Level (US-XXX) ← Story/Issue/UserStory
- Task Level (T-XXX) ← Sub-task/Task/Checkbox

---

## Part 2: Living Docs Engine

### Architecture Overview

**Location**: `src/living-docs/` and `src/core/living-docs/`

**Key Components**:

1. **FSIdAllocator** (`fs-id-allocator.ts`)
   - Manages file system IDs for feature folders (FS-001, FS-002, etc.)
   - Handles external work item allocation
   - Prevents ID collisions

2. **EpicIdAllocator** (`epic-id-allocator.ts`)
   - Allocates user story IDs (US-001, US-002, etc.)
   - Tracks allocations across feature folders
   - Handles external epic items

3. **IDRegistry** (`id-registry.ts`)
   - Central registry for all IDs
   - Ensures uniqueness across project
   - Resolves ID collisions

4. **EnterpriseAnalyzer** (`enterprise-analyzer.ts`)
   - Analyzes multi-level hierarchy structures
   - Maps teams to folder structures
   - Detects organizational patterns

5. **SmartDocOrganizer** (`smart-doc-organizer.ts`)
   - Auto-organizes imported docs into feature folders
   - Intelligent grouping by epic, board, or area path
   - Handles 2-level structures (team-based organization)

### Living Docs Folder Structure

```
.specweave/docs/internal/specs/
├── project-id/                          # Project (normalized)
│   ├── FS-001-feature-name/            # Feature folder
│   │   ├── FEATURE.md                  # Feature-level spec
│   │   ├── us-001-login.md             # User Story 1
│   │   ├── us-002-signup.md            # User Story 2
│   │   └── us-003-password-reset.md    # User Story 3
│   └── FS-002-dashboard/
│       ├── FEATURE.md
│       └── us-004-main-dashboard.md
├── project-id-2/
│   └── FS-003-reporting/
│       ├── FEATURE.md
│       └── us-005-export-reports.md
```

**Single vs. Two-Level Structures**:

**1-Level** (Simple):
```
.specweave/docs/internal/specs/
├── my-project/
│   ├── FS-001/
│   │   ├── FEATURE.md
│   │   └── us-001-*.md
```
Use when: Single team, simple organization

**2-Level** (Team-Based):
```
.specweave/docs/internal/specs/
├── my-project/
│   ├── frontend-team/
│   │   ├── FS-001/
│   │   └── FS-002/
│   ├── backend-team/
│   │   ├── FS-003/
│   │   └── FS-004/
```
Use when: Multiple teams, JIRA boards, or ADO area paths

### Spec to Living Docs Sync (`src/sync/spec-to-living-docs-sync.ts`)

**Purpose**: The critical missing link that syncs AC checkbox states and task completion from increment `spec.md` to living docs US files.

**Data Flow**:
```
Task Completion
    ↓
tasks.md updated
    ↓
Hook fires: post-task-completion
    ↓
spec.md ACs updated
    ↓
SpecToLivingDocsSync.sync()
    ↓
Living docs US files updated
    ↓
External sync picks up changes
    ↓
GitHub/JIRA/ADO updated
```

**Algorithm**:
1. Read `spec.md` from increment folder
2. Parse AC states (checked/unchecked)
3. Find all referenced US files in living docs
4. Update AC checkboxes in living docs
5. Sync status changes back to external tools

**Key Methods**:
```typescript
async sync(): Promise<SpecToLivingDocsSyncResult>
  ├── Parse spec.md
  ├── Extract AC states
  ├── Find living docs US files
  ├── For each US file:
  │   ├── Load file
  │   ├── Update ACs matching spec
  │   ├── Check for status changes
  │   └── Write if changed
  └── Return result with metadata
```

---

## Part 3: Hooks System

### Hook Architecture (`src/hooks/`)

**Files**:
- `platform.ts`: Cross-platform utilities (Windows/macOS/Linux)
- `processor.ts`: Main hook execution pipeline
- `hooks-status.ts`: Diagnostic tools
- `command-bridge.mjs`: Bridge to external commands

**Execution Points**:

| Hook | Trigger | Purpose |
|------|---------|---------|
| `post-increment-planning` | After `/sw:increment` | Create external issue from spec |
| `post-task-completion` | After task marked complete | Sync to external tools |
| `post-increment-done` | After `/sw:done` | Close external items |
| `session-start` | CLI session begins | Setup sync environment |
| `scheduler-startup` | Background scheduler starts | Resume pending syncs |

**Hook Processor Pipeline** (`src/hooks/processor.ts`):
```typescript
async processHook(hookName: string, context: HookContext) {
  1. Check if hook enabled in config
  2. Load hook configuration
  3. Validate permissions (sync gates)
  4. Setup hook context (paths, credentials)
  5. Execute hook with callbacks
  6. Update metadata with results
  7. Handle errors and retry logic
}
```

### Permission Gates System

**Three-Tier Gate Model** (from docs):

```
Every sync operation passes through permission gates:

Gate 1: canUpsertInternalItems
  ├── Can create/update items that originated in SpecWeave?
  └── Example: Push US-001 to create JIRA story

Gate 2: canUpdateExternalItems
  ├── Can update items that were imported from external?
  └── Example: Update GitHub issue that was imported as external ref

Gate 3: canUpdateStatus
  ├── Can change status fields in external tools?
  └── Example: Close JIRA issue when increment completes
```

**Default State**: All gates OFF (safe mode)

**Configuration**:
```json
{
  "sync": {
    "permissions": {
      "canUpsertInternalItems": false,    // OFF by default
      "canUpdateExternalItems": false,    // OFF by default
      "canUpdateStatus": false            // OFF by default
    }
  }
}
```

---

## Part 4: External Increment Lifecycle

### External Increment Naming Convention

**Suffix**: `E` appended to IDs indicates external origin

```
Internal:  FS-001, US-001, T-001
External:  FS-001E, US-001E, T-001E
```

**Metadata Differentiation**:
```yaml
# Internal increment metadata
{
  "type": "internal",
  "origin": "created",
  "status": "active"
}

# External increment metadata
{
  "type": "external_reference",
  "origin": "imported",
  "status": "active",
  "externalRef": {
    "platform": "github",
    "id": "42",
    "url": "https://github.com/org/repo/issues/42",
    "syncedAt": "2026-03-16T10:00:00Z"
  }
}
```

### Complete Lifecycle: Import → Work → Sync → Close

#### Phase 1: Import (User runs `/sw:import`)

```
1. CLI validates credentials
2. Spawns ImportWorker background process
3. ImportWorker executes:
   a. Fetch items from GitHub/JIRA/ADO
   b. Update progress atomically
   c. Group by source container
   d. Convert to living docs
   e. Create .specweave/docs/internal/specs/ files
   f. Store external metadata in frontmatter
4. Return aggregated results
5. CLI polls job status via job manager
```

**Outcome**:
- Living docs created (read-only references)
- No increments created yet
- External metadata stored for sync

#### Phase 2: Work (User runs `/sw:do` or `/sw:increment`)

**Case A: Internal Increment** (User runs `/sw:increment "feature"`)
```
1. `/sw:increment` → PM + Architect plan feature
2. Create increment: .specweave/increments/0001-feature/
   ├── spec.md (internal, no external ref)
   ├── plan.md
   └── tasks.md
3. User runs `/sw:do`
4. Implement tasks
5. On each task completion:
   a. Hook fires: post-task-completion
   b. Update spec.md ACs
   c. Trigger SpecToLivingDocsSync
   d. Living docs updated
   e. External sync reads changes
   f. Gate 1 check: canUpsertInternalItems
   g. Create/update external items if Gate 1 enabled
```

**Case B: External Spec Reference** (User implements imported spec)
```
1. `/sw:import` fetches external items
2. Living docs created: FS-001E/us-001-name.md
3. User creates new increment referencing external spec:
   `/sw:increment --from-external FS-001E`
4. Increment spec.md includes external_ref frontmatter
5. On task completion:
   a. Hook fires: post-task-completion
   b. Detect this is external reference (E suffix)
   c. Gate 2 check: canUpdateExternalItems
   d. Update status in external tool if Gate 2 enabled
```

#### Phase 3: Sync (Automatic + manual)

**Content Sync** (SpecWeave → External):
```
Triggers:
  ├── After /sw:increment (new spec)
  ├── After spec.md edit (detect changes)
  └── Manual: /sw:sync-progress

Process:
  1. Load spec from .specweave/docs/internal/specs/ or increment spec.md
  2. Detect what changed:
     ├── Title change
     ├── Description change
     └── User story count change
  3. Gate 1 check: canUpsertInternalItems
  4. If changes detected:
     ├── Create new issue (if not linked)
     ├── Update title/description in external tool
     ├── Sync user stories and ACs
     └── Store external ID in frontmatter
  5. Update metadata.json with external link

What syncs:
  ✓ Title
  ✓ Description
  ✓ User Stories
  ✓ Acceptance Criteria

What does NOT sync:
  ✗ State/Status (Open/Closed)
  ✗ Progress percentage
  ✗ Assignees
  ✗ Labels (except initial 'specweave')
```

**Status Sync** (External → SpecWeave):
```
Triggers:
  ├── After task completion
  ├── Manual: /sw:sync-progress --from-external
  └── Scheduled: hourly check

Process:
  1. Query external tool for item status
  2. Check if item was imported (has externalRef)
  3. Gate 2 check: canUpdateExternalItems
  4. If closed in external:
     ├── Mark task completed in local
     ├── Update living docs
     └── Close increment if all tasks done
  5. No reverse: Completing locally does NOT close external

What syncs:
  ✓ State (Open/Closed/Done)
  ✓ Progress percentage

What does NOT sync back:
  ✗ Content (always SpecWeave truth)
  ✗ Assignments
```

**Commit Sync** (SpecWeave → External):
```
Triggers:
  ├── After task completion (detects new commits)
  ├── Manual: /sw:sync-progress

Process:
  1. Detect new commits since last sync
  2. Group by AC-IDs (via AC-US#-## format)
  3. Build commit summary per user story
  4. Gate 1 check: canUpsertInternalItems
  5. Post comment to external item:
     └─ ### US-001: Login
        **Commits**:
        - abc123f: Add AuthService
        - def456g: Add login endpoint
        **PR**: #789

Data linked:
  ├── Task.md references AC-US#-##
  ├── Commits include AC-ID in message
  ├── Sync extracts AC-IDs
  └── Groups commits under user story
```

#### Phase 4: Closure (User runs `/sw:done`)

```
1. Quality gates execute:
   ├── All tasks completed?
   ├── Tests passing?
   ├── Living docs updated?
   ├── Coverage > threshold?
   └── Grill report generated?

2. On success:
   a. Gate 3 check: canUpdateStatus
   b. If Gate 3 enabled:
      ├── Close external issues
      ├── Update JIRA to "Done"
      └── Set ADO to "Closed"
   c. Mark increment complete
   d. Archive increment metadata

3. Metadata updated:
   {
     "status": "completed",
     "completedAt": "2026-03-16T15:00:00Z",
     "externalItems": [
       {
         "platform": "github",
         "id": 456,
         "status": "closed"
       }
     ]
   }
```

---

## Part 5: Multi-Repo and Single-Repo Architecture

### Single-Repo Configuration

**Setup**:
```json
{
  "sync": {
    "providers": {
      "github": {
        "enabled": true,
        "owner": "my-org",
        "repo": "my-app"
      }
    }
  }
}
```

**Import Config** (single source):
```typescript
const coordinator = new ImportCoordinator({
  github: { owner: 'my-org', repo: 'my-app' },
  importConfig: { timeRangeMonths: 6, includeClosed: false }
});
```

**Living Docs Structure**:
```
.specweave/docs/internal/specs/
├── my-app/                       # Project ID from repo
│   ├── FS-001-feature/
│   │   ├── FEATURE.md
│   │   └── us-001-*.md
```

### Multi-Repo Configuration

**Setup** (new approach):
```json
{
  "sync": {
    "providers": {
      "github": {
        "enabled": true,
        "repositories": [
          { "owner": "my-org", "repo": "frontend" },
          { "owner": "my-org", "repo": "backend" },
          { "owner": "my-org", "repo": "mobile" }
        ]
      }
    }
  }
}
```

**Import Config** (multi-source):
```typescript
const coordinator = new ImportCoordinator({
  githubRepositories: [
    { owner: 'my-org', repo: 'frontend' },
    { owner: 'my-org', repo: 'backend' },
    { owner: 'my-org', repo: 'mobile' }
  ],
  importConfig: { timeRangeMonths: 6, includeClosed: false }
});
```

**Living Docs Structure**:
```
.specweave/docs/internal/specs/
├── frontend/                     # Project ID from repo name
│   ├── FS-001-feature/
│   │   ├── FEATURE.md
│   │   └── us-001-*.md
├── backend/
│   ├── FS-002-api/
│   │   └── ...
├── mobile/
│   ├── FS-003-app/
│   │   └── ...
```

### Umbrella Repo Support

**Umbrella Structure**:
```
specweave-umb/                    # Main umbrella
├── repositories/
│   └── anton-abyzov/
│       ├── specweave/            # Plugin source
│       ├── vskill/               # Skill CLI
│       ├── vskill-platform/      # Next.js app
│       └── [other-repos]/
├── .specweave/                   # Umbrella root
│   └── docs/internal/specs/
```

**Key Difference**:
- Each child repo CAN have `.specweave/` but shouldn't (cleanup done 2026-03-15)
- Umbrella root is source of truth for specs
- Multi-repo sync routes to child repos via path resolution

**Resolved Path Logic**:
```typescript
// Resolve effective root
effectiveRoot = resolveEffectiveRoot(currentDir)
  ├── Check current dir for .specweave/
  ├── Check parent dirs for .specweave/
  └── Return first match (umbrella or child)

// For umbrella with child repos:
specsPath = path.join(effectiveRoot, 'docs/internal/specs/child-repo-name/')
```

---

## Part 6: Documentation Gaps & Discrepancies

### Gap 1: Import Doesn't Create Increments

**Documented**: "Import creates living docs"
**Reality**: Import ONLY creates living docs, never increments
**Impact**: Users must separately run `/sw:increment` to create working increments
**Missing Doc**: Clear statement that import ≠ increment creation

### Gap 2: External Suffix Convention Undocumented

**Discovered**: External items marked with 'E' suffix (FS-001E, US-001E)
**Documented**: NOT mentioned in any docs
**Impact**: Users don't understand why imported specs show 'E'
**Fix Needed**: Add to [External Tools Overview](#)

### Gap 3: Permission Gates Not Fully Explained

**Documented**: "Three gates exist" (high level)
**Reality**:
- Gate 1: Controls spec creation in external tools
- Gate 2: Controls updates to imported items
- Gate 3: Controls status closure in external tools
- Default: All OFF
- No incremental enablement guide
**Missing**: "Safe Mode Start-Up" guide showing how to enable gates gradually

### Gap 4: Brownfield Support Unclear

**Question**: Can I add sync to an existing project (without import)?
**Answer**: YES — use `/sw:sync-setup` to configure, then `/sw:sync-progress` to push existing specs
**Documented**: Partially in guides
**Missing**: Explicit brownfield workflow (setup → push → maintain)

### Gap 5: Living Docs Conversion Hidden from User

**What Happens**:
1. Import worker fetches items
2. (CRITICAL) Converts to living docs
3. Stores in `.specweave/docs/internal/specs/`

**What's Visible**:
- Job status: "Fetching items..."
- Result: "123 items imported"

**What's Hidden**:
- Conversion phase progress
- Where specs are saved
- Feature folder allocation logic

**Impact**: Users think import is complete when fetch finishes, don't realize conversion happening
**Fix Needed**: Show conversion progress in worker logs

### Gap 6: Spec-to-Living-Docs Sync Not Mentioned in Flow

**Current Docs Flow**:
```
Task Complete → Spec.md Updated → External Sync
```

**Actual Flow**:
```
Task Complete → Spec.md Updated → LIVING DOCS SYNC → External Sync
```

**Missing Component**: `SpecToLivingDocsSync` — the critical link between spec and external
**Impact**: Developers don't understand how AC completion → living docs → external sync chain works

### Gap 7: 2-Level Structure Folder Name Convention

**Question**: What are valid folder names for team/board level?
**Answer**:
- JIRA: Board names (e.g., "Frontend Board", "Backend Board")
- ADO: Area path names (e.g., "frontend-team", "backend-team")
- GitHub: Repo names (for multi-repo)

**Documented**: In JIRA/ADO guides
**Missing**: Unified explanation + folder name validation rules

### Gap 8: Status Sync Direction Confusion

**Documented Statement**: "Bidirectional sync"
**Reality**: Split-source (not true bidirectional):
- Content: SpecWeave → External (one way)
- Status: External → SpecWeave (one way)
- NOT: Same data editable in both places

**Issue**: Term "bidirectional" is misleading
**Fix**: Docs use "split-source" now, but API/configs still say "bidirectional"

---

## Part 7: Sync Hooks Deep Dive

### Hook Execution Chain

**Sequence Diagram**:
```
User Action
    │
    ├─ /sw:increment
    │   └── post-increment-planning hook
    │       ├── Load spec from living docs
    │       ├── Gate 1 check
    │       ├── Create external issue
    │       └── Store external link in spec frontmatter
    │
    ├─ Complete task in /sw:do
    │   └── post-task-completion hook
    │       ├── Update spec.md
    │       ├── Run SpecToLivingDocsSync
    │       ├── Gate 3 check (optional)
    │       └── Update external status (if enabled)
    │
    └─ /sw:done
        └── post-increment-done hook
            ├── Run quality gates
            ├── Gate 3 check
            ├── Close external issues
            └── Archive increment
```

### Hook Configuration

**`.specweave/config.json`**:
```json
{
  "hooks": {
    "enabled": true,
    "timeout": 30000,
    "hooks": {
      "post-increment-planning": {
        "enabled": true,
        "executeOn": ["spec_created", "spec_updated"]
      },
      "post-task-completion": {
        "enabled": true,
        "executeOn": ["task_marked_complete"]
      },
      "post-increment-done": {
        "enabled": true,
        "executeOn": ["increment_closed"]
      }
    }
  }
}
```

### Hook Retry Logic

**On Failure**:
1. First retry after 30s
2. Second retry after 5m
3. Store failure in hook log
4. Don't block user operations
5. User can manually retry with `/sw:sync-progress`

---

## Part 8: Lifecycle Workflow Examples

### Workflow A: Internal Feature → Sync to External

```bash
# 1. Create internal increment
/sw:increment "User authentication feature"
# → spec.md created (no external ref)
# → post-increment-planning hook fires
# → Gate 1 check: canUpsertInternalItems
# → If enabled: GitHub issue #456 created, link stored

# 2. Implement tasks
/sw:do
# → Complete task 1
#   ├─ post-task-completion hook fires
#   ├─ spec.md AC-001 marked complete
#   ├─ SpecToLivingDocsSync runs
#   ├─ living docs US file updated
#   └─ External status synced (if Gate 3 enabled)

# 3. Finish all tasks
/sw:done 0001
# → Quality gates pass
# → post-increment-done hook fires
# → Gate 3 check: canUpdateStatus
# → If enabled: GitHub issue #456 closed
```

### Workflow B: External Feature → Implement Locally

```bash
# 1. Import from external
/sw:import
# → Fetch GitHub issues
# → Convert to living docs: FS-001E/us-001-login.md
# → Store external metadata in frontmatter

# 2. Create local increment for implementation
/sw:increment --from-external FS-001E
# → spec.md includes external_ref metadata
# → tasks.md linked to external US

# 3. Implement
/sw:do
# → Complete tasks
# → post-task-completion hook fires
# → Detect external reference (E suffix)
# → Gate 2 check: canUpdateExternalItems
# → If enabled: Update GitHub issue status

# 4. Close
/sw:done 0042
# → External issue #456 marked complete (if Gate 3 enabled)
```

### Workflow C: Multi-Team Multi-Repo

```bash
# 1. Setup umbrella with multiple repos
specweave init .
# Select: GitHub with repositories: [frontend, backend, mobile]

# 2. Import from all repos
/sw:import
# → Fetches from frontend, backend, mobile
# → Groups by repo
# → Creates living docs:
#   ├─ frontend/FS-001/us-001.md
#   ├─ backend/FS-002/us-001.md
#   └─ mobile/FS-003/us-001.md

# 3. Work on tasks in context
# (Each team works on their increment)
/sw:do 0001  # Frontend feature
/sw:do 0002  # Backend feature
/sw:do 0003  # Mobile feature

# 4. Sync all to external
/sw:sync-progress
# → Updates frontend repo issues
# → Updates backend repo issues
# → Updates mobile repo issues
```

---

## Part 9: Key Architecture Decisions & Trade-offs

### Decision 1: Import ≠ Increment

**Choice**: Import creates only living docs, not increments

**Trade-offs**:
✓ Pro: Separation of concerns (import vs planning)
✓ Pro: Reusable specs across multiple increments
✓ Pro: Can review imported specs before creating increment
✗ Con: Extra step for users (import → increment)
✗ Con: Confusion about what import creates

**Rationale**: Specs are permanent (living docs), increments are temporary (implementation). Don't couple them.

### Decision 2: Split-Source (Not True Bidirectional)

**Choice**: Content SpecWeave→External, Status External→SpecWeave

**Trade-offs**:
✓ Pro: No merge conflicts (different data flows different directions)
✓ Pro: Clear ownership (specs in SpecWeave, workflow in external)
✓ Pro: Single source of truth per data type
✗ Con: Users must edit content in one place only
✗ Con: Can't edit descriptions in both tools

**Rationale**: Prevent data loss from conflicting updates. Specs are developers' domain, workflow is PMs' domain.

### Decision 3: Three Permission Gates

**Choice**: Don't sync by default (safe mode)

**Trade-offs**:
✓ Pro: Safe for beginners (nothing changes in external by accident)
✓ Pro: Fine-grained control per operation
✓ Pro: Can enable incrementally (Gate 1 → test → Gate 3)
✗ Con: Extra configuration step
✗ Con: Users confused why nothing syncs

**Rationale**: External tools are shared. Don't make changes without explicit permission.

### Decision 4: External Items Marked with 'E' Suffix

**Choice**: FS-001E indicates external feature

**Trade-offs**:
✓ Pro: Visually distinct from internal (FS-001 vs FS-001E)
✓ Pro: Can filter/search external specs
✗ Con: Non-standard naming (why 'E'?)
✗ Con: Not documented

**Rationale**: Need to distinguish external refs from internal. Single-character suffix is minimal overhead.

---

## Part 10: Missing Implementation Connections

### Connection Gap 1: Import → Living Docs Conversion

**Flow Implemented**:
1. ImportCoordinator fetches items ✓
2. Returns CoordinatorResult ✓
3. import-worker receives result ✓
4. ItemConverter called (line 294) ✓
5. Specs written to disk ✓

**What's Missing**:
- No progress feedback for conversion phase
- User sees "Import complete" but conversion still running
- No way to distinguish fetch vs conversion in UI

**Fix**: Show conversion progress in CLI output

### Connection Gap 2: Spec.md ↔ Living Docs US File Linking

**Flow Implemented**:
1. Create increment spec.md ✓
2. Parse AC-IDs from spec.md ✓
3. SpecToLivingDocsSync finds US files ✓
4. Updates based on AC-ID match ✓

**What's Missing**:
- No explicit linking (spec.md should reference which US files)
- If US file renamed, linking breaks
- No validation that AC-IDs are unique

**Fix**: Add forward reference in spec.md frontmatter:
```yaml
---
linkedUserStories:
  - .specweave/docs/internal/specs/project/FS-001/us-001-login.md
---
```

### Connection Gap 3: Hook Error Propagation

**Flow Implemented**:
1. Hook fires on task completion ✓
2. Error logged to hook log ✓
3. Error doesn't block task completion ✓

**What's Missing**:
- User doesn't know hook failed
- Sync is incomplete but task shows complete
- No retry mechanism without manual CLI

**Fix**:
- Display hook results in `/sw:progress`
- Add `/sw:sync-retry` command

### Connection Gap 4: External ID Storage

**Flow Implemented**:
1. Create external item (GitHub issue #42) ✓
2. Store external_id in frontmatter ✓
3. Next sync looks up external_id ✓

**What's Missing**:
- No validation that external_id is still valid
- If external item deleted, ID becomes stale
- No cleanup of stale external IDs

**Fix**: Add periodic `external-id-validator` that checks if external items still exist

---

## Part 11: Testing Gaps

### Gap 1: Import Lifecycle Tests

**Current**: Unit tests for ItemConverter exist
**Missing**:
- Integration test: Import → Living Docs complete flow
- Test: External metadata properly stored in frontmatter
- Test: Multi-repo import groups correctly
- Test: Feature folder allocation on collision

### Gap 2: Spec-to-Living-Docs-Sync Tests

**Current**: None found (class defined but no tests)
**Missing**:
- Unit: AC state extraction from spec.md
- Unit: US file discovery by AC-ID
- Integration: spec.md AC update → living docs sync
- Integration: Status changes detected properly

### Gap 3: Hook Chain Tests

**Current**: Some hook tests
**Missing**:
- Integration: Full hook chain (post-task-completion → spec update → living docs sync → external sync)
- Test: Permission gates block correctly
- Test: Hook retries on failure
- Test: Concurrent hook executions don't race

### Gap 4: Multi-Repo Sync Tests

**Current**: None found
**Missing**:
- Test: Multi-repo import separates items correctly
- Test: Multi-repo sync routes to correct repos
- Test: Umbrella root vs child repo paths resolve correctly

---

## Summary of Key Findings

### Architecture Strengths

1. **Clean Separation**: Import (fetch), Living Docs (specs), Increments (implementation) are distinct
2. **Safe Defaults**: Permission gates OFF by default, can enable incrementally
3. **Split-Source Design**: Prevents merge conflicts, clear data ownership
4. **Multi-Platform**: GitHub, JIRA, ADO all supported with consistent hierarchy mapping
5. **Extensible**: ItemConverter, SpecToLivingDocsSync can be extended for new behaviors

### Critical Bottlenecks

1. **Missing Living Docs Conversion Progress**: User doesn't see conversion phase
2. **Undocumented Spec-to-Living-Docs Sync**: Core link in chain is invisible
3. **External Metadata Fragile**: External ID stored in multiple places (frontmatter, metadata.json, external API)
4. **No Validation Loop**: Stale external IDs not detected
5. **Incomplete Hook Error Handling**: Failures don't block but aren't visible

### Documentation Gaps

1. External suffix 'E' convention not explained
2. Import lifecycle vs increment creation confusing
3. Permission gates safe-mode startup guide missing
4. Brownfield workflow (add sync to existing project) unclear
5. Spec-to-Living-Docs-Sync mechanism completely undocumented

### Recommended Improvements

1. **Add Living Docs Conversion Progress**: Show conversion phase in import worker logs
2. **Document External Metadata Model**: Explain where external_id stored and why
3. **Create Integration Test Suite**: Full lifecycle tests for import→work→sync→close
4. **Add Validation Scheduler**: Periodic checks for stale external IDs
5. **Improve Error Visibility**: Show hook results in `/sw:progress`, add retry commands
6. **Document Spec Linking**: Add forward references from spec.md to living docs US files

---

## Conclusion

SpecWeave's import and sync architecture is **sophisticated and well-designed** but has **visibility gaps** that hide critical phases from users:

- **Import worker** fetches items, **then invisibly converts to living docs**
- **Spec-to-living-docs sync** is the **core link** connecting increments to external tools, but **completely undocumented**
- **Permission gates** provide **safe defaults**, but require **explicit enablement** to work
- **Split-source sync** prevents conflicts but requires **understanding distinct data flows**

With better documentation, progress visibility, and integration tests, the architecture would be clearer and more reliable.
