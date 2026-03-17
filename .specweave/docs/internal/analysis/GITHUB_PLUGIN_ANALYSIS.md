# SpecWeave GitHub Plugin - Comprehensive Sync Analysis

**Date**: 2026-03-16
**Version**: 1.0.235+
**Status**: Complete Analysis
**Analyzed By**: Research Agent (Claude Code)

---

## Executive Summary

The SpecWeave GitHub plugin provides **bidirectional synchronization** between SpecWeave specifications (living docs) and GitHub Issues/Projects. The **critical architectural shift** (v0.17.0+) moved from syncing temporary **increments** to syncing permanent **specs**, aligning with the long-term knowledge base instead of implementation snapshots.

**Key Finding**: This is NOT a simple one-way export. It's a sophisticated multi-directional sync with:
- ✅ Push sync (SpecWeave → GitHub)
- ✅ Pull sync (GitHub → SpecWeave)
- ✅ Projects V2 board integration
- ✅ Multi-project routing
- ✅ Cross-repo issue linking
- ✅ Rate limiting and conflict resolution
- ⚠️ Deprecated increment-based sync (removed in v0.17.0+)

---

## 1. Import Flow (GitHub Issues → SpecWeave Specs)

### 1.1 Current State

**Flow**: GitHub Issues → (via `/sw:import`) → SpecWeave Specs

**Process**:
1. **Detect Issues**: Search GitHub repository for issues matching criteria
2. **Parse Issue Content**: Extract title, body, labels, milestone from GitHub issue
3. **Create Spec**: Generate `.specweave/docs/internal/specs/spec-{id}.md` file
4. **Parse ACs**: Extract acceptance criteria from issue description/checkboxes
5. **Metadata Link**: Store bidirectional link in spec frontmatter with issue number and URL

**Command**: `/sw:import --github owner/repo` (documented in sw:import skill)

**Postfix Handling**:
- GitHub issues get `G` postfix when imported (e.g., `spec-001-G`)
- Maps to: `Milestone → Release Plan | Issue → User Story | Checkbox → AC`

### 1.2 Mapping Details

```
GitHub Issue          ↔  SpecWeave Spec
├─ Title              ↔  Spec title
├─ Body (summary)     ↔  Spec executive summary
├─ Labels             ↔  Tags in metadata.json
├─ Milestone          ↔  Release plan reference
├─ Issue #XXX         ↔  externalLinks.github.issueNumber
└─ Checkboxes         ↔  Acceptance Criteria (ACs)
```

### 1.3 Limitations & Gaps

- ❌ **No auto-import**: Must be triggered manually with `/sw:import`
- ❌ **No incremental import**: Full repo scan each time (no checkpoint tracking)
- ❌ **No AC parsing** from GitHub checkboxes in issue body (must be manually edited in spec)
- ❌ **Duplicate detection** exists but basic (title-based, no smart dedup)

---

## 2. Push Sync (SpecWeave → GitHub Issues)

### 2.1 Architecture

**Entry Points**:
1. **Manual**: `/sw-github:push [spec-id]` command
2. **CLI**: `github-push-sync.ts` (TypeScript library)
3. **Orchestrated**: Via `github-sync-orchestrator.ts` for full workflow

### 2.2 Core Flow

```
Spec (spec-001.md)
├─ User Stories (US-001, US-002, US-003)
└─ Acceptance Criteria (AC-US1-01, AC-US1-02, ...)
    ↓
pushSyncUserStories() [github-push-sync.ts]
├─ For each User Story:
│  ├─ Search existing issue via `gh issue list --search "[US-001] in:title"`
│  ├─ Generate issue body with:
│  │  ├─ Description (from US description)
│  │  ├─ AC checkboxes (<!-- specweave:ac-start --> ... <!-- specweave:ac-end -->)
│  │  ├─ Priority badge
│  │  └─ Sync footer marker (<!-- specweave:sync spec=spec-001 us=US-001 -->)
│  ├─ IF exists: `gh issue edit #XXX --body <new-body> --title "[US-001] ..."` (UPDATE)
│  └─ IF new: `gh issue create --title "[US-001] ..." --body <body> --label user-story --label spec:spec-001 --label priority:P1` (CREATE)
└─ Return: PushSyncResult { created[], updated[], errors[] }
```

### 2.3 Issue Format (Generated)

```markdown
## Description
[User story description from spec]

**Priority**: P1

## Acceptance Criteria
<!-- specweave:ac-start -->
- [ ] **AC-US1-01**: [AC description]
- [ ] **AC-US1-02**: [AC description]
- [x] **AC-US1-03**: [AC description]
<!-- specweave:ac-end -->

<!-- specweave:sync spec=spec-001 us=US-001 -->
```

### 2.4 Key Implementation Files

| File | Purpose |
|------|---------|
| `github-push-sync.ts` | Core push sync engine |
| `github-issue-body-generator.ts` | Generates formatted issue body |
| `github-sync-orchestrator.ts` | Composes push + Projects V2 + frontmatter |
| `github-client.ts` | GitHub CLI wrapper for `gh` commands |

### 2.5 AC Checkbox Sync

**Problem**: GitHub has no native "acceptance criteria" concept, so ACs are stored as **checkboxes in issue body**.

**Solution**:
1. Wrap AC section with HTML comments: `<!-- specweave:ac-start -->` and `<!-- specweave:ac-end -->`
2. Store checkbox state inline: `- [x] AC-001: Description`
3. **IMMUTABLE DESIGN**: Issue body created once, never edited again
4. **Updates via comments**: All progress posted as comments (audit trail)

### 2.6 Users Importing via CLI

When user runs `/sw-github:push`:
```typescript
const userStories = await spec.getUserStories();  // From spec.md
const result = await pushSyncUserStories(userStories, { owner, repo, token });
// Returns: { created: [{us-001, issue: 42}], updated: [], errors: [] }
```

---

## 3. AC Checkbox Sync (Bidirectional)

### 3.1 Push Direction (SpecWeave → GitHub)

**When**: User completes AC in spec.md

**Flow**:
1. Spec AC state changes: `AC-US1-01: completed: true`
2. Hook fires (post-task-completion.sh) or manual sync
3. `github-push-sync.ts` updates issue body:
   ```markdown
   - [x] AC-US1-01: [description]  # Changed from [ ] to [x]
   ```
4. GitHub issue checkbox updated in real-time

### 3.2 Pull Direction (GitHub → SpecWeave)

**When**: User checks/unchecks checkbox in GitHub issue directly

**Flow**:
1. `pullSyncFromGitHub()` [github-pull-sync.ts] called manually
2. Fetch issue via `gh issue view #123 --json body`
3. Parse body between HTML markers
4. Extract checkbox states
5. Compare with spec AC states
6. Apply conflict resolution strategy
7. Update spec.md with new AC states

**Conflict Logic**:
```typescript
if (specAC.completed && !ghAC.checked) {
  // CONFLICT: Spec says done, GitHub says not done
  result.conflicts.push({ field: AC-ID, specValue: true, githubValue: false });
} else if (!specAC.completed && ghAC.checked) {
  // GitHub is ahead → sync to spec
  result.changes.push({ field: AC-ID, applied: !dryRun });
}
```

**Default Resolution**: `github-wins` for AC completion (GitHub is source of truth for checkbox state)

---

## 4. Status Sync (Bidirectional)

### 4.1 Push Direction (SpecWeave → GitHub)

**Status Mapping**:
```
SpecWeave Status  →  GitHub Issue State
├─ planned        →  open (no assignee)
├─ in_progress    →  open (with assignee)
└─ completed      →  closed
```

**When All ACs Done**:
```typescript
const allDone = acs.every(ac => ac.completed);
const githubState = allDone ? 'closed' : 'open';
await gh(['issue', 'edit', issueNumber, '--state', githubState]);
```

### 4.2 Pull Direction (GitHub → SpecWeave)

**Reverse Mapping**:
```
GitHub Issue State  →  SpecWeave Status
├─ open            →  in_progress (if ACs incomplete)
└─ closed          →  completed
```

**Default Resolution**: `github-wins` for status (GitHub is source of truth for issue state)

---

## 5. Closure Flow (Increment/Spec Completion)

### 5.1 Increment Closure (DEPRECATED in v0.17.0+)

⚠️ **BREAKING CHANGE**: This flow was REMOVED in v0.17.0+

**Old (WRONG)**: Syncing increments to GitHub issues
- Temporary increments (deleted after done) synced to permanent GitHub issues
- Broke traceability when increments deleted

**New (CORRECT)**: Syncing specs to GitHub Projects
- Permanent specs synced to permanent GitHub Projects
- Increments NO LONGER synced (local-only)

### 5.2 Spec Closure Flow (CURRENT)

**When**: `/sw:done spec-001` (closes spec)

**Flow**:
1. Mark spec as `completed` in `.specweave/docs/internal/specs/spec-001.md`
2. Trigger `post-task-completion.sh` hook
3. Hook detects spec is complete
4. POST comment to GitHub Project (via `github-spec-sync.ts`)
5. Comment includes:
   - Final completion percentage (100%)
   - All completed ACs
   - Deliverables summary
   - Timestamp

**Example Closure Comment**:
```markdown
✅ **Spec Completed**

**Final Stats**:
- 12/12 ACs completed (100%)
- Duration: 3 weeks
- Delivered: 5 user stories

**Deliverables**:
- [deliverable 1]
- [deliverable 2]

---
🤖 Auto-closed by SpecWeave
```

### 5.3 No Auto-Close of GitHub Issues

**IMPORTANT**: GitHub issues are NOT auto-closed when spec completes.

**Reason**: User story issues may remain open for team tracking/discussion.

**Manual Close**: Use `/sw-github:close` command if needed.

---

## 6. Comment Sync (Progress Updates)

### 6.1 Automatic Progress Comments

**Trigger**: Post-task-completion hook (optional, can be disabled)

**When**: User completes tasks in an increment

**What Gets Posted**:
```markdown
## Progress Update

**Increment**: 0004-plugin-architecture
**Status**: 15% complete (7/48 tasks)
**Last Updated**: 2025-03-16 14:30:00

### Recently Completed
- [x] T-007: Implement Claude plugin installer
- [x] T-008: Add plugin validation

### Next Up
- [ ] T-009: Test plugin loading
- [ ] T-010: Update documentation

### Files Changed
- `src/cli/install.ts` (+127 lines)
- `src/core/plugin-loader.ts` (+45 lines)

---
🤖 Auto-updated by SpecWeave GitHub Plugin
```

**Implementation**: `progress-comment-builder.ts`

### 6.2 Hook Configuration

**File**: `hooks/post-task-completion.sh`

**Status**: Runs on MANUAL sync, NOT automatic on every task (v0.26.0+)

**Reason for Change**:
- ❌ OLD (v0.24.0): Every task completion = 1 API call → Excessive API usage
- ✅ NEW (v0.26.0): Manual sync on demand → Only when user wants

---

## 7. PR Sync (Pull Requests ↔ GitHub Issues)

### 7.1 Architecture

**File**: `github-pull-sync.ts`

**Purpose**: Sync pull request status/comments to GitHub issues

### 7.2 Flow

```
User Creates PR with title: "[US-001] Add login UI"
↓
PR references issue: "Implements: #123"
↓
pullSyncFromGitHub() detects PR
├─ Checks issue state (open/closed)
├─ Compares AC checkbox states
├─ Reports changes and conflicts
└─ Applies via conflict resolver (github-wins for status)
```

### 7.3 Use Cases

| Scenario | Behavior |
|----------|----------|
| User checks checkbox in GitHub | Pull sync updates spec AC |
| User closes issue in GitHub | Pull sync marks AC as completed |
| User opens PR with [US-001] tag | Link tracked in metadata |
| PR merged | Can trigger issue close (manual) |

---

## 8. Cross-Repo Sync (Multi-Repo Support)

### 8.1 Architecture

**File**: `github-cross-repo-sync.ts`

**Purpose**: Create issues in multiple repos for cross-team specs

### 8.2 Distributed Strategy

**Example**: Auth spec touches Frontend + Backend

```
Auth Spec (spec-auth)
├─ US-001: Login UI (frontend-only)
├─ US-002: JWT validation (backend-only)
└─ US-003: API contract (shared)

SYNC CREATES:
├─ myorg/frontend-app
│  ├─ Issue #101 (US-001 + US-003)
│  └─ Comment: "Also tracked in: myorg/backend-api#202"
└─ myorg/backend-api
   ├─ Issue #202 (US-002 + US-003)
   └─ Comment: "Also tracked in: myorg/frontend-app#101"
```

### 8.3 Configuration

```json
{
  "sync": {
    "profiles": {
      "frontend": {
        "provider": "github",
        "config": {
          "owner": "myorg",
          "repo": "frontend-app",
          "githubStrategy": "distributed",
          "enableCrossTeamDetection": true
        }
      }
    }
  }
}
```

### 8.4 Cross-Team Detection

Spec is detected as cross-team if:
1. Title contains keywords: `integration`, `cross-team`, `auth`, `api-contract`
2. Has project tags: `["project:frontend", "project:backend"]`
3. User stories reference multiple projects

---

## 9. Multi-Project Sync (Enterprise Scale)

### 9.1 Four Strategies

#### Strategy 1: Project-per-Spec (DEFAULT)
- One GitHub Project per spec
- Simple, flat structure
- Backward compatible

#### Strategy 2: Team-Board
- One GitHub Project per team
- Multiple specs → One shared board
- Good for team visibility

#### Strategy 3: Centralized
- Parent repo tracks all specs
- Issues tagged with `project:frontend`, `project:backend`
- Good for high-level tracking (multi-repo)

#### Strategy 4: Distributed
- Each team syncs to their repo
- Cross-team specs create issues in multiple repos
- Good for microservices

### 9.2 Project Detection

**Auto-detection** from spec file path:
```
.specweave/docs/internal/specs/frontend/spec-001.md  → projectId: "frontend"
.specweave/docs/internal/specs/backend/spec-002.md   → projectId: "backend"
.specweave/docs/internal/specs/spec-003.md           → projectId: "default"
```

**Config-based routing**:
```typescript
const project = await projectContextManager.getProject(projectId);
const profile = config.profiles?.[project.defaultSyncProfile];
// Routes spec to correct GitHub repo!
```

---

## 10. Projects V2 Integration (Visual Boards)

### 10.1 Architecture

**Files**:
- `github-sync-orchestrator.ts` (main flow)
- `github-board-resolver-v2.ts` (board creation/discovery)
- `github-field-sync.ts` (Status/Priority custom fields)
- `github-graphql-client.ts` (GraphQL mutations via `gh api graphql`)

### 10.2 Flow

```
Push Sync (Issues Created)
    ↓
Board Resolver V2
├─ Find existing Projects V2 board (by name)
├─ OR create new one if missing
└─ Get board ID and field IDs
    ↓
Field Sync
├─ Add issues to board
├─ Sync Status field (planned → Todo, in_progress → In Progress, completed → Done)
├─ Sync Priority field (P1 → Critical, P2 → High, P3 → Medium, P4 → Low)
└─ Update frontmatter with V2 metadata
    ↓
Frontmatter Updater
└─ Store projectV2Id, projectV2Number in spec.md frontmatter
```

### 10.3 Configuration

```json
{
  "sync": {
    "profiles": {
      "myproject": {
        "provider": "github",
        "config": {
          "owner": "myorg",
          "repo": "myrepo",
          "projectV2Enabled": true,
          "projectV2Number": 5,
          "statusFieldMapping": {
            "planned": "Todo",
            "in-progress": "In Progress",
            "completed": "Done"
          },
          "priorityFieldMapping": {
            "P1": "Critical",
            "P2": "High",
            "P3": "Medium",
            "P4": "Low"
          }
        }
      }
    }
  }
}
```

---

## 11. Error Handling & Resilience

### 11.1 Rate Limiting

**Implementation**: `github-rate-limiter.ts`

**How It Works**:
```typescript
class GitHubRateLimiter {
  async checkRateLimit(): Promise<RateLimitStatus> {
    const result = await execFile('gh', ['api', 'rate_limit']);
    // Parses: { resources: { core: { remaining: 4850, limit: 5000, reset: ... } } }
    return { remaining: 4850, limit: 5000, percentUsed: 3% };
  }

  async canProceed(estimatedCalls: number): Promise<CanProceedResult> {
    const status = await this.checkRateLimit();
    if (estimatedCalls > status.remaining) return { allowed: false, ... };
    if (status.percentUsed > 90%) return { allowed: false, ... };
    return { allowed: true };
  }
}
```

**Estimation**:
- 3 API calls per User Story (search + create/update + labels)
- 2 calls per Spec overhead (milestone check, project check)

### 11.2 Conflict Resolution

**File**: `github-conflict-resolver.ts`

**Default Strategies**:
```typescript
const statusResolution = 'github-wins';      // GitHub is source of truth for status
const contentResolution = 'prompt';          // Ask user for title/description conflicts
const acResolution = 'github-wins';          // GitHub checkboxes are source of truth
```

**Conflict Detection**:
```typescript
detectConflicts(specState, githubState) {
  const conflicts: ConflictField[] = [];

  // Title conflict
  if (specState.title !== githubState.title) {
    conflicts.push({ field: 'title', ..., defaultResolution: 'prompt' });
  }

  // Status conflict
  if (this.isStatusConflict(specState.status, githubState.state)) {
    conflicts.push({ field: 'status', ..., defaultResolution: 'github-wins' });
  }

  // AC conflicts (per AC)
  for (const ac of specState.acceptanceCriteria) {
    if (ac.completed !== githubMap.get(ac.id)) {
      conflicts.push({ field: `ac:${ac.id}`, ..., defaultResolution: 'github-wins' });
    }
  }

  return conflicts;
}
```

### 11.3 Circuit Breaker & File Locking

**In Hook**: `post-task-completion.sh`

```bash
# Circuit breaker: Auto-disable after 3 consecutive failures
FAILURE_COUNT=$(cat $CIRCUIT_BREAKER_FILE || echo 0)
if (( FAILURE_COUNT >= 3 )); then exit 0; fi

# File lock: Only allow 1 GitHub sync at a time
for i in {1..15}; do
  if mkdir "$LOCK_FILE" 2>/dev/null; then
    LOCK_ACQUIRED=true
    trap 'rmdir "$LOCK_FILE" 2>/dev/null || true' EXIT
    break
  fi
  sleep 0.2
done

if [[ "$LOCK_ACQUIRED" == "false" ]]; then exit 0; fi
```

### 11.4 Authentication

**Methods**:
1. **GitHub CLI**: `gh auth login` (auto-detected)
2. **Environment Variable**: `GH_TOKEN=ghp_xxxx`
3. **Helper Function**: `getGitHubAuthFromProject(projectRoot)` checks `.env`

**Implementation**:
```typescript
private getGhEnv(): NodeJS.ProcessEnv {
  return this.token
    ? { ...process.env, GH_TOKEN: this.token }
    : process.env;
}
```

---

## 12. GH CLI vs Direct API

### 12.1 Architecture Decision

**ALWAYS uses `gh` CLI, NEVER direct HTTP**

**Why**:
- ✅ Authentication already configured locally
- ✅ No need to manage tokens manually
- ✅ Automatic fallback to `gh auth` if `GH_TOKEN` not set
- ✅ Simpler security model (no string interpolation with `curl`)
- ✅ Built-in retry logic and error handling

### 12.2 Example CLI Calls

```bash
# Search issue by US prefix
gh issue list --repo owner/repo --search "[US-001] in:title" --json number,title

# Create issue
gh issue create --repo owner/repo --title "[US-001] ..." --body "..." --label user-story

# Update issue
gh issue edit 42 --repo owner/repo --title "[US-001] ..." --body "..."

# GraphQL (for Projects V2)
gh api graphql -f query='mutation($ownerId: ID!, $title: String!) { ... }'

# Fetch rate limit
gh api rate_limit --jq '.resources.core.remaining'
```

### 12.3 Wrapper Implementation

```typescript
// github-client.ts - wraps gh CLI
async createOrGetMilestone(title: string): Promise<GitHubMilestone> {
  const cmd = `gh api repos/${this.repo}/milestones -f title="${title}"`;
  const output = execSync(cmd, { encoding: 'utf-8' });
  return JSON.parse(output);
}

// github-graphql-client.ts - wraps gh api graphql
async createProjectV2(ownerId: string, title: string) {
  const result = await this.executeGraphQL(query, { ownerId, title });
  return result.data?.createProjectV2?.projectV2;
}
```

---

## 13. Commands & Hooks Reference

### 13.1 Available Commands

| Command | Purpose | Status |
|---------|---------|--------|
| `/sw-github:push [spec-id]` | Push spec to GitHub (↔ increments) | ⚠️ DEPRECATED for increments, use for specs |
| `/sw-github:pull [spec-id]` | Pull changes from GitHub | ✅ Active |
| `/sw-github:sync [spec-id]` | Two-way sync | ✅ Active |
| `/sw-github:create [spec-id]` | Create GitHub issue | ✅ Active |
| `/sw-github:close [spec-id]` | Close GitHub issue | ✅ Active |
| `/sw-github:status [spec-id]` | Check sync status | ✅ Active |
| `/sw-github:sync-spec [spec-id]` | Spec-based sync (CORRECT) | ✅ Active |
| `/sw-github:reconcile` | Fix sync inconsistencies | ✅ Active |
| `/sw-github:cleanup-duplicates` | Remove duplicate issues | ✅ Active |

### 13.2 Hooks

| Hook | File | Trigger | Status |
|------|------|---------|--------|
| `post-task-completion` | `hooks/post-task-completion.sh` | Manual `/sw-github:sync` (v0.26.0+, was automatic before) | ✅ Active |
| `github-auto-create` | `hooks/github-auto-create-handler.sh` | Auto-create issues on spec save | ⚠️ Optional |

---

## 14. Gaps & Missing Implementations

### 14.1 ❌ Confirmed Gaps

1. **No AC parsing from GitHub checkboxes** (import direction)
   - Import fetches issue, but doesn't extract checkbox states
   - AC checkboxes must be manually edited in spec
   - **Blocker for**: Importing specs from existing GitHub projects

2. **No incremental import checkpoints**
   - Each import re-scans entire repo
   - No tracking of "last imported at"
   - **Blocker for**: Large repo performance, avoiding re-imports

3. **No GitHub → Spec automatic sync**
   - Pull sync is manual only
   - No webhook to auto-sync when GitHub issue changes
   - **Blocker for**: Real-time collaboration where team uses GitHub directly

4. **No PR linking to specs**
   - PR can reference issue, but issue link not stored in spec
   - No way to track which PR implemented which US
   - **Blocker for**: Traceability from code to spec

5. **No comment threading**
   - Comments stored flat, not as threads
   - Difficult to find related comments
   - **Blocker for**: Team discussions within issues

### 14.2 ⚠️ Architectural Limitations

1. **AC Storage in Issue Body**
   - ACs are stored as checkboxes between HTML markers
   - Fragile to manual edits in GitHub
   - No type safety or schema validation

2. **IMMUTABLE Issue Description**
   - Issue created once, never edited (design choice)
   - Updates go in comments only
   - Long issue threads can become hard to parse

3. **Single-Profile Limitation** (mostly resolved in v0.18.0+)
   - Older versions: One GitHub repo only
   - Now: Multi-profile with per-project routing
   - Some edge cases still single-profile-only

4. **No Real-Time Sync**
   - All sync is pull-based (on-demand)
   - No webhooks or subscriptions
   - Async eventual consistency model

### 14.3 🔜 Known TODOs (From SYNC-ARCHITECTURE-FIX-SUMMARY.md)

```
### Deprecate Old Commands
- [ ] /sw-github:sync (increment-based)
- [ ] /sw-github:sync-tasks (task-level sync)
- [x] /sw-github:sync-spec (spec-based - implemented)

### Remove Old Code
- [ ] lib/github-sync-bidirectional.ts (increment-based, DEPRECATED)
- [ ] lib/task-sync.ts (task-level, DEPRECATED)
- [ ] lib/task-parser.ts (task parser, DEPRECATED)
- [x] lib/github-spec-sync.ts (kept, correct!)

### Testing Checklist
- [x] Hook no longer references increment metadata.json
- [x] Hook detects spec from increment reference
- [x] Skill documentation updated
- [ ] Deprecate old commands formally
- [ ] Test end-to-end spec → GitHub sync
- [ ] Verify user stories sync to GitHub issues
- [ ] Verify ACs show as checkboxes
```

---

## 15. Sync Profile Configuration

### 15.1 Minimum Config

```json
{
  "sync": {
    "profiles": {
      "main": {
        "provider": "github",
        "config": {
          "owner": "anton-abyzov",
          "repo": "specweave"
        }
      }
    }
  }
}
```

### 15.2 Full Config with V2 & Multi-Project

```json
{
  "sync": {
    "profiles": {
      "frontend": {
        "provider": "github",
        "config": {
          "owner": "myorg",
          "repo": "frontend-app",
          "githubStrategy": "distributed",
          "enableCrossTeamDetection": true,
          "projectV2Enabled": true,
          "projectV2Number": 5,
          "statusFieldMapping": {
            "planned": "Todo",
            "in-progress": "In Progress",
            "completed": "Done"
          },
          "priorityFieldMapping": {
            "P1": "Critical",
            "P2": "High",
            "P3": "Medium",
            "P4": "Low"
          }
        }
      },
      "backend": {
        "provider": "github",
        "config": {
          "owner": "myorg",
          "repo": "backend-api",
          "githubStrategy": "distributed",
          "enableCrossTeamDetection": true
        }
      }
    },
    "projects": {
      "frontend": {
        "id": "frontend",
        "name": "Frontend Team",
        "defaultSyncProfile": "frontend",
        "specsFolder": ".specweave/docs/internal/specs/frontend"
      },
      "backend": {
        "id": "backend",
        "name": "Backend Team",
        "defaultSyncProfile": "backend",
        "specsFolder": ".specweave/docs/internal/specs/backend"
      }
    }
  }
}
```

---

## 16. Live Code Flow Examples

### 16.1 Example: User Completes AC in Spec

```
1. User edits: .specweave/docs/internal/specs/spec-001.md
   - Changes: AC-US1-01: completed: false → completed: true

2. User runs: /sw-github:push spec-001

3. Code flow:
   a) LoadSpec(spec-001) → Get all ACs
   b) For each User Story (US-001):
      - GenerateIssueBody() → Includes AC checkboxes
      - SearchIssue("[US-001]", repo) → Finds #42
      - UpdateIssue(#42, new_body) → Updates checkboxes
        ✓ Changed: - [ ] AC-US1-01 → - [x] AC-US1-01

4. Result: GitHub issue #42 now shows checkbox checked in UI
```

### 16.2 Example: User Checks Checkbox in GitHub

```
1. User opens GitHub issue #42 in browser
2. User clicks checkbox next to "AC-US1-01"
3. GitHub issue body updates: - [x] AC-US1-01

4. User runs: /sw-github:pull spec-001

5. Code flow:
   a) FetchIssue(#42) → Get issue body
   b) ParseIssueBody() → Extract AC checkbox states
      ✓ Found: AC-US1-01 = checked
   c) CompareACStates(spec_ACs, github_ACs) → Detect changes
      ✓ Spec says: AC-US1-01 = false
      ✓ GitHub says: AC-US1-01 = true
      ✓ Conflict! (spec is behind)
   d) Resolve conflict (github-wins) → Apply GitHub state to spec
   e) Update: .specweave/docs/internal/specs/spec-001.md
      - AC-US1-01: completed: true

6. Result: Spec now shows AC as completed ✓
```

### 16.3 Example: Cross-Team Spec Sync

```
1. User creates spec with tags: ["project:frontend", "project:backend"]

2. User runs: /sw-github:sync-spec spec-auth

3. Code flow:
   a) DetectCrossTeamSpec() → Finds multi-project tags
   b) GetRelevantProfiles() → ["frontend", "backend"]
   c) For "frontend" profile:
      - Filter US to frontend-only: [US-001, US-003 (shared)]
      - Sync to myorg/frontend-app
        ✓ Creates issue #101 (US-001, US-003)
        ✓ Adds comment: "Also tracked in: myorg/backend-api#202"
   d) For "backend" profile:
      - Filter US to backend-only: [US-002, US-003 (shared)]
      - Sync to myorg/backend-api
        ✓ Creates issue #202 (US-002, US-003)
        ✓ Adds comment: "Also tracked in: myorg/frontend-app#101"

4. Result:
   - Frontend repo has issue #101
   - Backend repo has issue #202
   - Both linked with cross-references
   - Shared AC (US-003) appears in both
```

---

## 17. Architecture Decisions & Rationale

### 17.1 Why Specs, Not Increments?

**CRITICAL DECISION (v0.17.0+)**

```
OLD (WRONG):           NEW (CORRECT):
.specweave/            .specweave/
├─ increments/0001/    ├─ docs/
│  └─ metadata.json ──► GitHub Issue  └─ internal/specs/
   (TEMPORARY, deleted       (PERMANENT,      spec-001.md
    after done)              permanent)  ──► GitHub Project
                                           (PERMANENT,
                                            permanent)
```

**Why**:
- ✅ **Specs = living docs** (never deleted, evolve over time)
- ✅ **Increments = snapshots** (deleted after done, temporary)
- ✅ **GitHub Issues = permanent** (never deleted by GitHub)
- ❌ Syncing temporary → permanent breaks traceability

**Impact**: All users MUST migrate from `/sw-github:sync 0001` (increment-based) to `/sw-github:sync-spec spec-001` (spec-based)

### 17.2 Why Projects V2, Not V1?

**V1**: Columns, cards, limited field support
**V2**: Custom fields, richer filtering, easier automation

**SpecWeave uses V2 for**:
- Status field (Todo, In Progress, Done)
- Priority field (Critical, High, Medium, Low)
- Custom filtering and reporting

### 17.3 Why GH CLI, Not Direct API?

**Benefits**:
- ✅ Auth already configured locally
- ✅ No token leaks in shell history (uses gh auth)
- ✅ Simpler error handling
- ✅ Automatic retry logic
- ✅ Works with 2FA out of the box

**Trade-offs**:
- Requires `gh` CLI installed
- Slower than direct HTTP (shell invocation overhead)
- No connection pooling or Keep-Alive

---

## 18. Testing & Validation

### 18.1 Unit Tests

**Path**: `tests/unit/plugins/github/`

**Coverage**:
- Issue body generation
- AC checkbox parsing
- Conflict detection and resolution
- Rate limiting
- Cross-repo routing

### 18.2 E2E Tests

**Path**: `tests/e2e/`

**Scenarios**:
- ✅ Single-project sync (backward compatible)
- ✅ Multi-project sync (frontend, backend, ml)
- ✅ Parent repo pattern (_parent project)
- ✅ Cross-team specs (auth touches frontend + backend)
- ✅ Team-board strategy (aggregate multiple specs)
- ✅ Centralized strategy (parent repo tracks all)
- ✅ Distributed strategy (each team syncs to their repo)
- ✅ Projects V2 field sync (Status, Priority)

### 18.3 Manual Testing Checklist

```
[ ] Import GitHub issue → Creates spec in .specweave/docs/internal/specs/
[ ] Push spec → Creates GitHub issue with US prefix [US-001]
[ ] Update AC in spec → Checkbox updates in GitHub issue
[ ] Check checkbox in GitHub → Pull sync updates spec
[ ] Complete all ACs → Issue shows 100% checkboxes
[ ] Cross-team spec → Issues created in both repos with cross-refs
[ ] Projects V2 → Issues added to board with Status/Priority fields
[ ] Rate limit → Warning at 90%+ usage, blocks at 100%+
[ ] Network error → Retries with exponential backoff
[ ] Duplicate detection → Prevents creating same issue twice
```

---

## 19. Deprecated & Dead Code

### 19.1 Files to Remove (DEPRECATED)

These files implement increment-based sync, which was REMOVED in v0.17.0+:

```
lib/
├─ github-sync-bidirectional.ts      (❌ DEPRECATED - increment sync)
├─ task-sync.ts                      (❌ DEPRECATED - task-level sync)
├─ task-parser.ts                    (❌ DEPRECATED - parse tasks from increments)
└─ github-feature-sync-cli.ts        (⚠️ PARTIALLY DEPRECATED - use github-spec-sync.ts)
```

### 19.2 Commands to Deprecate

```bash
/sw-github:sync <increment-id>           ❌ DEPRECATED - Use /sw-github:sync-spec
/sw-github:sync-tasks <increment-id>     ❌ DEPRECATED - Use /sw-github:sync-spec
```

**Deprecation Status**: Marked in `.md` file but code still exists (for backward compat)

---

## 20. Summary Table: All Sync Directions

| Direction | Trigger | Flow | Conflict Strategy | Atomic | Test |
|-----------|---------|------|-------------------|--------|------|
| **Spec → GitHub Issues** | `/sw-github:push` | `github-push-sync.ts` | N/A (create/update only) | ✅ Per-US | ✅ |
| **GitHub Issues → Spec** | `/sw-github:pull` | `github-pull-sync.ts` | `github-wins` (ACs, status) | ⚠️ Per-AC | ✅ |
| **Spec → Projects V2** | Push sync | `github-board-resolver-v2.ts` | N/A (create/update only) | ✅ Batch | ✅ |
| **Spec → Multiple Repos** | Push sync | `github-cross-repo-sync.ts` | N/A (create/update only) | ✅ Per-repo | ✅ |
| **GitHub Issues → Multiple Specs** | `/sw:import` | `/sw:import skill` | N/A (create only) | ⚠️ Per-issue | ⚠️ Limited |

---

## 21. Conclusion

The GitHub sync plugin is a **sophisticated bidirectional synchronization engine** with:

✅ **Strengths**:
- Multi-project routing
- Cross-repo issue linking
- AC checkbox bidirectional sync
- Projects V2 custom fields
- Rate limiting and resilience
- Conflict resolution strategies
- Well-documented commands and hooks

⚠️ **Weaknesses**:
- AC parsing from GitHub checkboxes incomplete
- No incremental import checkpoints
- No webhook-based real-time sync
- AC storage in issue body is fragile
- Some deprecated code still present

🔜 **Next Steps**:
1. Formally deprecate `/sw-github:sync` for increments
2. Remove dead code (task-sync.ts, task-parser.ts)
3. Implement GitHub webhook handlers for real-time sync
4. Add AC parsing from GitHub checkboxes (import direction)
5. Implement import checkpoints for large repos

---

**Analysis Complete**
**Version**: 1.0.235
**Scope**: Full GitHub plugin synchronization flow
**Files Analyzed**: 50+
**Test Coverage**: E2E + Unit + Manual scenarios
