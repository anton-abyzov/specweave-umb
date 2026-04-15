# Implementation Plan: Skill Version Management — Phase 2

## Overview

Extend vskill's version lifecycle across three layers: **CLI** (enhanced `versions`, new `pin`/`unpin`), **eval-server** (proxy routes to platform API, SSE update stream), and **Studio UI** (VersionHistory panel, UpdatesPanel page, reusable ChangelogViewer). The platform API already provides cursor-paginated version lists, full content retrieval, and LCS-based diff — this plan proxies those through the eval-server so Studio never calls the platform directly.

## Architecture

### System Context

```
┌─────────┐      ┌─────────────┐      ┌──────────────────┐
│ vskill  │      │ eval-server │      │ vskill-platform  │
│   CLI   │─────▶│  (proxy)    │─────▶│  (read-only API) │
└─────────┘      └──────┬──────┘      └──────────────────┘
                        │ SSE / JSON
                 ┌──────▼──────┐
                 │  Studio UI  │
                 │ (React SPA) │
                 └─────────────┘
```

### Component Inventory

| # | Component | Location | Purpose |
|---|-----------|----------|---------|
| C1 | `versions.ts` enhancement | `src/commands/versions.ts` | Add installed marker, diffSummary column, `--diff` flag |
| C2 | `pin.ts` (new) | `src/commands/pin.ts` | `vskill pin <skill> [version]` / `vskill unpin <skill>` |
| C3 | Lockfile extension | `src/lockfile/types.ts` | Add `pinnedVersion?: string` to `SkillLockEntry` |
| C4 | Version proxy routes | `src/eval-server/api-routes.ts` | Proxy platform version/diff APIs through eval-server |
| C5 | Update SSE endpoint | `src/eval-server/api-routes.ts` | Stream batch update progress via SSE |
| C6 | `VersionHistoryPanel.tsx` | `src/eval-ui/src/pages/workspace/` | New workspace tab showing version timeline + diffs |
| C7 | `UpdatesPanel.tsx` | `src/eval-ui/src/pages/` | Full-page batch update UI with select-all, per-skill progress |
| C8 | `ChangelogViewer.tsx` | `src/eval-ui/src/components/` | Reusable diff viewer (unified diff rendering) |

---

## Data Model Changes

### C3: Lockfile Extension — `SkillLockEntry`

```typescript
// src/lockfile/types.ts — extend existing interface
export interface SkillLockEntry {
  version: string;
  sha: string;
  tier: string;
  installedAt: string;
  source: string;
  marketplace?: string;
  pluginDir?: boolean;
  scope?: "user" | "project";
  installedPath?: string;
  files?: string[];
  pinnedVersion?: string; // NEW — when set, update skips this skill
}
```

**Decision**: Single `pinnedVersion` field rather than a `pinned: boolean` flag because it records *which* version was intentionally pinned. This lets `vskill outdated` show "pinned at 1.2.0" instead of just "pinned", and enables future "pin to latest" semantics.

### Studio Types Extension — `SkillInfo`

```typescript
// src/eval-ui/src/types.ts — extend existing interface
export interface SkillInfo {
  // ... existing fields ...
  updateAvailable?: boolean;
  currentVersion?: string;
  latestVersion?: string;
  pinnedVersion?: string; // NEW — display pin badge in SkillCard
}
```

### New Types — Version & Diff

```typescript
// src/eval-ui/src/types.ts — new types
export interface VersionEntry {
  version: string;
  certTier: string;
  certScore?: number;
  diffSummary: string | null;
  createdAt: string;
  isInstalled?: boolean; // derived client-side from lockfile version
}

export interface VersionDiff {
  from: string;
  to: string;
  diffSummary: string;
  contentDiff: string; // unified diff format
}

export interface VersionDetail {
  version: string;
  content: string; // full SKILL.md
  certTier: string;
  certScore?: number;
  createdAt: string;
}

export interface BatchUpdateProgress {
  skill: string;
  status: "pending" | "updating" | "scanning" | "installing" | "done" | "error" | "skipped";
  fromVersion?: string;
  toVersion?: string;
  scanScore?: number;
  scanVerdict?: string;
  error?: string;
}
```

---

## API Contracts

### C4: Eval-Server Proxy Routes

These routes proxy to the vskill-platform REST API. The eval-server reads the lockfile to resolve full skill names and adds the `isInstalled` marker.

| Method | Path | Proxied To | Purpose |
|--------|------|-----------|---------|
| `GET` | `/api/skills/:plugin/:skill/versions` | `GET /api/v1/skills/{owner}/{repo}/{skill}/versions` | List versions with cursor pagination |
| `GET` | `/api/skills/:plugin/:skill/versions/:version` | `GET /api/v1/skills/{owner}/{repo}/{skill}/versions/{version}` | Get full SKILL.md content for a version |
| `GET` | `/api/skills/:plugin/:skill/versions/diff?from=X&to=Y` | `GET /api/v1/skills/{owner}/{repo}/{skill}/versions?from=X&to=Y` | Get unified diff between two versions |

**Name Resolution**: The eval-server resolves `plugin/skill` to `owner/repo/skill` using the lockfile source field, matching the pattern already used in `versions.ts:resolveFullName()`.

**Response enrichment**: The versions-list response adds `isInstalled: true` to the entry matching the lockfile's current version.

### C5: Batch Update SSE Endpoint

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/skills/batch-update` | Start batch update, return SSE stream |

**Request body**:
```json
{
  "skills": ["skill-creator", "architect"],  // empty = all outdated
  "force": false  // skip scan failures
}
```

**SSE events** (same pattern as `sweep-routes.ts`):
```
event: progress
data: {"skill":"architect","status":"updating","fromVersion":"1.0.0","toVersion":"1.1.0"}

event: progress
data: {"skill":"architect","status":"scanning","scanScore":95,"scanVerdict":"PASS"}

event: progress
data: {"skill":"architect","status":"done","fromVersion":"1.0.0","toVersion":"1.1.0"}

event: done
data: {"updated":2,"failed":0,"skipped":1}
```

**Implementation**: Reuse the `initSSE`, `sendSSE`, `sendSSEDone` helpers from `sse-helpers.ts`. Internally calls the same update pipeline as `updateCommand` (fetchFromSource → SHA check → scan → install → lockfile write) but streams progress per skill.

---

## Component Design

### C1: Enhanced `versions` Command

**File**: `src/commands/versions.ts` (currently 68 lines)

Changes:
1. **Installed marker**: Read lockfile, compare `entry.version` to each version row. Mark with `→` or `*` in the table.
2. **diffSummary column**: Add a 4th column showing the `diffSummary` field from the API (already returned by `getVersions()`).
3. **`--diff` flag**: New option `vskill versions <skill> --diff [from] [to]`. Calls `getVersionDiff()` (new client function) and prints unified diff to stdout with ANSI colors.
4. **`--json` flag**: Raw JSON output for scripting.

```
$ vskill versions architect
Versions for anthropics/skills/architect

  Version   Tier        Date         Changes
→ 2.3.0     CERTIFIED   04/10/2026   Added multi-repo support
  2.2.1     CERTIFIED   03/28/2026   Fixed prompt injection edge case
  2.2.0     VERIFIED    03/15/2026   New ADR template engine
```

**API addition** (`src/api/client.ts`):
```typescript
export async function getVersionDiff(
  name: string,
  from: string,
  to: string,
): Promise<{ from: string; to: string; diffSummary: string; contentDiff: string }> {
  return apiRequest(`${skillApiPath(name)}/versions?from=${from}&to=${to}`);
}
```

### C2: Pin/Unpin Command

**File**: `src/commands/pin.ts` (new, ~80 lines)

```
vskill pin <skill> [version]    # Pin to installed version (default) or specific version
vskill unpin <skill>            # Remove pin
```

**Logic**:
1. Read lockfile, find skill entry
2. If version specified, validate it exists via `getVersions()`
3. Set `entry.pinnedVersion = version || entry.version`
4. Write lockfile

**Integration with `update.ts`**: Add guard at top of per-skill loop:
```typescript
if (entry.pinnedVersion) {
  console.log(dim(`${name}: pinned at ${entry.pinnedVersion} — skipping`));
  continue;
}
```

**Integration with `outdated.ts`**: Show pinned skills with distinct formatting:
```
Skill         Installed   Latest    Bump    Tier       Pin
architect     2.2.0       2.3.0     minor   CERTIFIED  📌 2.2.0
```

**Commander registration** (`src/index.ts`):
```typescript
program
  .command("pin <skill> [version]")
  .description("Pin a skill to prevent automatic updates")
  .action(async (skill, version) => { /* ... */ });

program
  .command("unpin <skill>")
  .description("Remove version pin from a skill")
  .action(async (skill) => { /* ... */ });
```

### C6: VersionHistoryPanel (Workspace Tab)

**File**: `src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx`

This is a new tab in the skill workspace, added to the "Insights" group alongside History, Leaderboard, and Deps.

**UI layout**:
```
┌──────────────────────────────────────────────────────┐
│ Version History                          [Pin badge] │
│                                                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Timeline (vertical)                              │ │
│ │ ● 2.3.0 CERTIFIED  04/10  +Added multi-repo...  │ │
│ │ │                                         [Diff] │ │
│ │ ● 2.2.1 CERTIFIED  03/28  Fixed prompt inj...   │ │
│ │ │                                         [Diff] │ │
│ │ → 2.2.0 VERIFIED   03/15  ← installed           │ │
│ │ │                                         [Diff] │ │
│ │ ● 2.1.0 VERIFIED   03/01  Initial release       │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │ ChangelogViewer (expanded on [Diff] click)       │ │
│ │ From 2.2.0 → 2.3.0           +12 -3             │ │
│ │ ┌────────────────────────────────────────┐       │ │
│ │ │  unified diff with syntax highlighting │       │ │
│ │ └────────────────────────────────────────┘       │ │
│ └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

**State management**: Uses `useSWR` for version list fetching (same pattern as HistoryPanel). The diff is loaded lazily when user clicks [Diff] — no preloading.

**Integration points**:
- Extend `PanelId` type: `"editor" | "tests" | "run" | "activation" | "history" | "leaderboard" | "deps" | "versions"`
- Add to `VALID_PANELS` array in `SkillWorkspace.tsx`
- Add to `TAB_GROUPS` in `TabBar.tsx` under "Insights" group
- Add keyboard shortcut `Ctrl+8`

### C7: UpdatesPanel (Full Page)

**File**: `src/eval-ui/src/pages/UpdatesPanel.tsx`

This is NOT a workspace panel — it's a top-level page accessible via a prominent button in the sidebar when updates are available (extending the existing `mergeUpdatesIntoSkills` pattern).

**UI layout**:
```
┌──────────────────────────────────────────────────────┐
│ Available Updates (3)                                │
│                                                      │
│ [✓] Select All                [Update Selected (3)]  │
│                                                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │ [✓] architect    2.2.0 → 2.3.0  minor  CERTIFIED│ │
│ │     +Added multi-repo support, new ADR templates │ │
│ │                                    [View Changes]│ │
│ ├──────────────────────────────────────────────────┤ │
│ │ [✓] skill-creator 1.0.0 → 1.1.0 minor VERIFIED │ │
│ │     +New eval generation, improved prompts       │ │
│ │                                    [View Changes]│ │
│ ├──────────────────────────────────────────────────┤ │
│ │ [ ] debug         0.9.0 → 1.0.0 major VERIFIED  │ │
│ │     📌 Pinned at 0.9.0                           │ │
│ └──────────────────────────────────────────────────┘ │
│                                                      │
│ ┌──────────────────────────────────────────────────┐ │
│ │ Progress (during update)                         │ │
│ │ ● architect: Scanning... (95/100 PASS)           │ │
│ │ ○ skill-creator: Pending                         │ │
│ │ ✓ pm: Updated 1.0.0 → 1.1.0                     │ │
│ └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

**State**: Local component state — no need for workspace context since this operates across all skills. Uses SSE via `EventSource` to `/api/skills/batch-update` for real-time progress.

**Routing**: Add route in `App.tsx` — e.g., `?view=updates`. Sidebar button with yellow badge count when `updateCount > 0`.

### C8: ChangelogViewer (Reusable Component)

**File**: `src/eval-ui/src/components/ChangelogViewer.tsx`

Extracted from the existing `ImproveDiffView` in `HistoryPanel.tsx` (lines 417-593). That component already implements:
- Dual line numbers (old/new)
- Color-coded gutter (+/- indicators)
- Added/removed line highlighting
- Stats header (+N, -N)

**Refactoring plan**:
1. Extract the diff rendering table into `ChangelogViewer` with props: `{ diff: string; fromLabel: string; toLabel: string; maxHeight?: number }`
2. The component parses unified diff format (from platform API) into `DiffLine[]` using the existing `computeDiff` utility in `src/eval-ui/src/utils/diff.ts`
3. Replace `ImproveDiffView`'s inline table with `<ChangelogViewer />`
4. Reuse in `VersionHistoryPanel` and `UpdatesPanel`'s "View Changes" expandable

**Props interface**:
```typescript
interface ChangelogViewerProps {
  contentDiff: string;      // unified diff string from API
  fromLabel: string;        // e.g., "2.2.0"
  toLabel: string;          // e.g., "2.3.0"
  diffSummary?: string;     // human-readable summary line
  maxHeight?: number;       // default 480px
  collapsible?: boolean;    // default false
}
```

---

## Data Flow

### Version History Flow (VersionHistoryPanel)

```
VersionHistoryPanel
  │
  ├─ useSWR("/api/skills/:plugin/:skill/versions")
  │   └─ eval-server GET handler
  │       ├─ resolveFullName(plugin, skill) → "owner/repo/skill"
  │       ├─ fetch(platform `/api/v1/skills/{owner}/{repo}/{skill}/versions`)
  │       ├─ readLockfile() → mark isInstalled on matching version
  │       └─ return enriched list
  │
  └─ onClick [Diff] → fetch("/api/skills/:plugin/:skill/versions/diff?from=X&to=Y")
      └─ eval-server GET handler
          ├─ resolveFullName
          ├─ fetch(platform `/api/v1/skills/{owner}/{repo}/{skill}/versions?from=X&to=Y`)
          └─ return { from, to, diffSummary, contentDiff }
              └─ <ChangelogViewer contentDiff={...} />
```

### Batch Update Flow (UpdatesPanel)

```
UpdatesPanel
  │
  ├─ Mount: api.getSkillUpdates() → show outdated list
  │   └─ (existing route — /api/skills/updates via execSync)
  │
  ├─ User selects skills, clicks "Update Selected"
  │   └─ POST /api/skills/batch-update { skills: [...] }
  │       └─ eval-server SSE handler
  │           ├─ For each skill:
  │           │   ├─ sendSSE("progress", {skill, status: "updating"})
  │           │   ├─ fetchFromSource() → content
  │           │   ├─ SHA check → skip if unchanged
  │           │   ├─ sendSSE("progress", {skill, status: "scanning"})
  │           │   ├─ runTier1Scan() → score, verdict
  │           │   ├─ sendSSE("progress", {skill, status: "installing"})
  │           │   ├─ installSymlink() + lockfile update
  │           │   └─ sendSSE("progress", {skill, status: "done"})
  │           └─ sendSSEDone({updated, failed, skipped})
  │
  └─ On completion: refresh skill list
```

### Pin/Unpin Flow (CLI)

```
vskill pin architect 2.2.0
  │
  ├─ readLockfile()
  ├─ Validate: lock.skills["architect"] exists
  ├─ Optional: getVersions("architect") → validate version exists
  ├─ lock.skills["architect"].pinnedVersion = "2.2.0"
  └─ writeLockfile(lock)

vskill update
  │
  ├─ For each skill in lockfile:
  │   ├─ if (entry.pinnedVersion) → skip, log "pinned at X"
  │   └─ else → normal update pipeline
```

---

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions per vskill convention)
- **CLI**: Commander.js (existing pattern)
- **Server**: Raw Node.js HTTP with custom `Router` class (existing pattern)
- **UI**: React 18 + Tailwind CSS + inline styles with CSS variables (existing design system)
- **Data fetching**: Custom `useSWR` hook + `useOnDataEvent` for real-time invalidation (existing pattern)
- **SSE**: `initSSE`/`sendSSE`/`sendSSEDone` helpers (existing in `sse-helpers.ts`)
- **Platform API client**: `fetch` with timeout via `AbortController` (existing pattern in `client.ts`)

---

## Architecture Decisions

### AD-1: Eval-Server as Proxy (Not Direct Platform Calls)

**Decision**: Studio components call eval-server, which proxies to platform API.

**Rationale**:
- Consistent with existing `/api/skills/updates` route pattern
- Eval-server can enrich responses (add `isInstalled` from lockfile)
- No CORS issues — Studio and eval-server are same origin
- Platform API credentials/base URL managed in one place (server-side)
- Enables caching at proxy layer (avoid hammering platform on rapid tab switches)

**Alternative rejected**: Direct platform API calls from Studio. Would require CORS config, duplicate auth, and couldn't enrich with local lockfile state.

### AD-2: Batch Update via SSE (Not Polling)

**Decision**: Use SSE streaming for batch update progress.

**Rationale**:
- Matches existing sweep-routes.ts SSE pattern (proven, well-tested helpers)
- Real-time progress without polling overhead
- Clean error handling per-skill (errors don't abort the batch)
- Existing `ProgressLog` component already handles SSE event rendering

**Alternative rejected**: WebSocket. Overkill for one-way server→client progress. SSE is simpler and already proven in the codebase.

### AD-3: VersionHistory as Workspace Panel (Not Standalone Page)

**Decision**: Version history is a workspace tab, updates is a standalone page.

**Rationale**:
- Version history is per-skill context — belongs in workspace alongside History, Leaderboard, Deps
- Batch updates span all skills — doesn't belong in per-skill workspace
- Follows existing UI patterns: per-skill tabs vs. global pages

### AD-4: Pin Field on Lockfile Entry (Not Separate Config)

**Decision**: Store `pinnedVersion` directly on `SkillLockEntry`.

**Rationale**:
- Pin state is per-skill — natural fit on the entry
- Lockfile is already the source of truth for installed skill state
- No new config file needed
- `vskill outdated --json` already reads lockfile — pin info flows naturally

**Alternative rejected**: Separate `.vskill-pins.json` file. Unnecessary indirection — the lockfile is the right place.

### AD-5: Reuse Existing Diff Rendering (Extract, Don't Rewrite)

**Decision**: Extract `ChangelogViewer` from `ImproveDiffView` in `HistoryPanel.tsx`.

**Rationale**:
- `ImproveDiffView` already implements exactly the diff UI we need (dual line numbers, color coding, gutter markers)
- DRY — avoid duplicate diff rendering code
- The existing `computeDiff` utility handles line-level diffing
- For platform diffs (already unified format), parse the unified diff into `DiffLine[]` array

---

## Implementation Phases

### Phase 1: Foundation (Data Model + CLI)

**Dependencies**: None (pure CLI/lockfile work)

1. **Lockfile extension** — add `pinnedVersion?: string` to `SkillLockEntry`
2. **`pin.ts` command** — implement pin/unpin with lockfile write
3. **Commander registration** — add `pin` and `unpin` to `index.ts`
4. **`update.ts` guard** — skip pinned skills
5. **`outdated.ts` display** — show pin status in table
6. **`versions.ts` enhancement** — installed marker, diffSummary column, `--diff` flag
7. **`client.ts` addition** — `getVersionDiff()` function

### Phase 2: Server Layer (Eval-Server Proxy + SSE)

**Dependencies**: Phase 1 (lockfile types)

1. **Version proxy routes** — GET versions list, detail, diff in `api-routes.ts`
2. **Name resolution helper** — reuse `resolveFullName` pattern for eval-server
3. **Batch update SSE endpoint** — POST `/api/skills/batch-update`
4. **Pin info in `/api/skills/updates`** — extend response with pinnedVersion
5. **Pin/unpin REST endpoints** — POST `/api/skills/:plugin/:skill/pin` and DELETE for Studio UI

### Phase 3: Studio UI Components

**Dependencies**: Phase 2 (server routes available)

1. **ChangelogViewer extraction** — extract from ImproveDiffView, make reusable
2. **API client extensions** — add version/diff/batchUpdate methods to `api.ts`
3. **Type extensions** — add VersionEntry, VersionDiff, BatchUpdateProgress to `types.ts`
4. **VersionHistoryPanel** — new workspace tab with timeline + lazy diff loading
5. **Workspace integration** — extend PanelId, VALID_PANELS, TAB_GROUPS, keyboard shortcuts
6. **UpdatesPanel** — full page with batch update SSE progress
7. **SkillCard pin badge** — show pin icon alongside update badge
8. **Navigation** — sidebar updates button with badge count, route in App.tsx

---

## Testing Strategy

### Unit Tests (Vitest)
- `pin.ts`: pin/unpin writes correct lockfile, validates version exists
- `update.ts`: skips pinned skills, logs message
- `outdated.ts`: pinned skills shown with distinct formatting
- `versions.ts`: installed marker, diffSummary rendering, --diff output
- `ChangelogViewer.test.tsx`: renders diff lines, handles empty diff, respects maxHeight
- `VersionHistoryPanel.test.tsx`: renders version timeline, loads diff on click
- `UpdatesPanel.test.tsx`: renders outdated list, handles batch update SSE events

### Integration Tests (Vitest)
- Eval-server proxy routes: mock platform API, verify response enrichment
- Batch update SSE: verify event stream format, error handling per skill
- Pin/unpin REST endpoints: verify lockfile mutation

### E2E Tests (Playwright)
- Navigate to Versions tab in workspace, verify timeline renders
- Click diff button, verify ChangelogViewer expands
- Navigate to Updates page, select skills, trigger batch update
- Pin a skill via UI, verify it appears as pinned in outdated list

---

## Technical Challenges

### Challenge 1: Platform API Name Resolution

**Problem**: Studio operates on `plugin/skill` pairs (filesystem-based), but platform API needs `owner/repo/skill` (hierarchical names).

**Solution**: Reuse the `resolveFullName()` pattern from `versions.ts` and `outdated.ts`. The eval-server reads the lockfile's `source` field, parses it with `parseSource()`, and constructs the hierarchical name. Falls back to the raw name if source parsing fails.

**Risk**: Skills installed from local paths or non-GitHub sources won't have hierarchical names. Mitigation: return 404 for version routes when name can't be resolved — the UI hides the Versions tab for non-registry skills.

### Challenge 2: Batch Update in Server Context

**Problem**: The existing `updateCommand` runs as a CLI process with direct filesystem access. The eval-server needs to run the same pipeline but stream progress via SSE.

**Solution**: Extract the per-skill update pipeline from `updateCommand` into a shared function that accepts a progress callback. The CLI calls it with `console.log`, the eval-server calls it with `sendSSE`. This avoids duplicating the fetchFromSource → scan → install → lockfile pipeline.

**Risk**: Concurrent updates could corrupt the lockfile. Mitigation: Use the existing `getSkillSemaphore()` pattern from `concurrency.ts` to serialize updates.

### Challenge 3: ChangelogViewer Dual Input Formats

**Problem**: `ImproveDiffView` uses `computeDiff(original, improved)` which takes two strings. Platform API returns a pre-computed unified diff string.

**Solution**: `ChangelogViewer` accepts `contentDiff: string` (unified diff format) and parses it into `DiffLine[]` with a new `parseUnifiedDiff()` utility. The existing `computeDiff` is used when both full texts are available (e.g., ImproveDiffView). Both paths produce the same `DiffLine[]` array for rendering.

---

## Out of Scope

- Version rollback (installing a specific older version) — future Phase 3
- Automatic update scheduling (cron-based) — no demand signal yet
- Platform API authentication — currently public read-only endpoints
- Version comparison across different skills — single-skill scope only
