---
increment: 0666-skill-version-lifecycle
title: "Skill Version Management - Phase 2: Version History, Changelogs, Batch Update UI"
generated: 2026-04-14
test_mode: TDD
---

# Tasks: Skill Version Management — Phase 2

## Domain Split
- **CLI** (T-001–T-008): Lockfile extension, API client, `versions`, `pin/unpin`, `update`, `outdated`
- **Eval-Server** (T-009–T-012): Proxy routes, single-skill SSE, batch SSE
- **Studio UI** (T-013–T-024): Types, utilities, components, panels, navigation

---

## US-001: Enhanced `vskill versions` Command

### T-001: Lockfile Extension — Add `pinnedVersion` Field
**User Story**: US-001 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-04
**Status**: [x] completed
**Test**: Given an existing `skills.lock` without a `pinnedVersion` field → When `readLockfile()` parses it → Then `SkillLockEntry.pinnedVersion` is `undefined` (no error); and writing an entry with `pinnedVersion: "1.0.0"` round-trips correctly through `writeLockfile()`

**Details**:
- Extend `SkillLockEntry` in `src/lockfile/types.ts` with `pinnedVersion?: string`
- No schema migration needed — additive change, old files parse as-is
- Unit test: old lockfile (no field) parses without error; new lockfile preserves value

---

### T-002: API Client — `getVersionDiff()` Function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed
**Test**: Given skill `anthropics/skills/architect` with `from=1.0.0` and `to=2.0.0` → When `getVersionDiff("architect", "1.0.0", "2.0.0")` is called → Then an HTTP request hits `${skillApiPath}/versions?from=1.0.0&to=2.0.0` and the response is parsed into `{ from, to, diffSummary, contentDiff }`

**Details**:
- Add `getVersionDiff(name, from, to)` to `src/api/client.ts`
- Follow existing `apiRequest` pattern with `AbortController` timeout
- Unit test with `vi.mock` on `fetch`: verify URL construction and response shape

---

### T-003: `versions` Command — Installed Marker + `diffSummary` Column
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed
**Test**: Given `architect` is installed at `1.0.0` (lockfile present) and `getVersions()` returns entries with `diffSummary` → When running `vskill versions architect` → Then the table includes a `►` marker in the Installed column for `1.0.0` and the Changes column shows `diffSummary` truncated to 60 chars with `…`

**Details**:
- Modify `src/commands/versions.ts` to read lockfile and compare entry version
- Add `Changes` column; truncate at 60 chars + `…`
- If skill not in lockfile: no marker shown (AC-US1-05 behaviour)
- Unit test: mock lockfile and `getVersions()`, assert table row content

---

### T-004: `versions` Command — `--diff` and `--from`/`--to` Flags
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed
**Test**: Given `architect` installed at `1.0.0` and latest `2.0.0` → When `vskill versions architect --diff` → Then `getVersionDiff("architect","1.0.0","2.0.0")` is called and unified diff is printed with ANSI green/red; when `--from 1.0.0 --to 2.0.0` provided, those versions are used; when skill not installed and `--from`/`--to` absent, then warning printed and exits cleanly

**Details**:
- Add `--diff` flag and optional `--from <v1> --to <v2>` to `versions.ts`
- Default: installed→latest; with `--from`/`--to`: specified range
- Not installed without `--from`/`--to`: print `Skill not installed. Use --from and --to to compare specific versions.`
- Unit test: three scenarios (default diff, explicit range, not-installed warning)

---

### T-005: `versions` Command — `--json` Flag
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06
**Status**: [x] completed
**Test**: Given `architect` installed at `1.0.0` → When `vskill versions architect --json` → Then stdout is valid JSON: an array where each object has `version`, `diffSummary`, and `installed: boolean`; `installed: true` appears only on the lockfile-matched entry

**Details**:
- Add `--json` flag to `versions.ts`; when set, `JSON.stringify` the enriched array and print then exit
- Unit test: parse stdout JSON, assert field presence and `installed` boolean accuracy

---

## US-002: Version Pinning

### T-006: `pin` / `unpin` Commands (new `pin.ts`)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-06
**Status**: [x] completed
**Test**: Given `architect` installed at `1.0.0` → When `vskill pin architect` → Then `lock.skills["architect"].pinnedVersion === "1.0.0"` and `Pinned architect at 1.0.0` printed; when `vskill unpin architect` → Then `pinnedVersion` is removed from lockfile and `Unpinned architect` printed; when `vskill pin nonexistent` → Then exits code 1 with `Skill nonexistent is not installed`

**Details**:
- Create `src/commands/pin.ts` (~80 lines) with `pinCommand(skill, version?)` and `unpinCommand(skill)`
- Register in `src/index.ts`: `program.command("pin <skill> [version]")` and `program.command("unpin <skill>")`
- If `version` specified: call `getVersions()` to validate existence before writing
- Unit tests: pin writes correct lockfile, unpin removes field, error on missing skill

---

### T-007: `update.ts` — Skip Pinned Skills + `--force` Override
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05
**Status**: [x] completed
**Test**: Given `architect` has `pinnedVersion: "1.0.0"` in lockfile → When `vskill update` → Then `architect` is skipped with dim log `architect: pinned at 1.0.0 — skipping`; when `vskill update architect --force` → Then the pin is ignored, update pipeline runs, and `pinnedVersion` remains set after completion

**Details**:
- Add guard at top of per-skill loop in `src/commands/update.ts`: if `entry.pinnedVersion && !force` → log + continue
- `--force` flag bypasses pin check (one-time override, pin not cleared)
- Unit test: mock pinned lockfile entry, assert skip log; assert force flag bypasses guard

---

### T-008: `outdated.ts` — Pin Status Display + `--json` Enrichment
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-07
**Status**: [x] completed
**Test**: Given `architect` has `pinnedVersion: "1.0.0"` and latest is `2.0.0` → When `vskill outdated` → Then table shows `architect` with `📌 1.0.0` in a Pin column and count summary excludes pinned skills; when `vskill outdated --json`, then each pinned skill's JSON object includes `"pinned": true`

**Details**:
- Modify `src/commands/outdated.ts` to read `pinnedVersion` from lockfile
- Add `Pin` column: `📌 <version>` when pinned; empty otherwise
- Exclude pinned skills from the "N skills outdated" summary count
- `--json`: add `pinned: true` on pinned entries
- Unit test: assert table row formatting and `--json` field inclusion

---

## US-003: Eval-Server Version & Update Routes

### T-009: Eval-Server Versions Proxy Route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed
**Test**: Given `GET /api/skills/myPlugin/architect/versions` → When eval-server handles it → Then it resolves `myPlugin/architect` to `owner/repo/architect` via lockfile `source`, proxies to platform `GET /api/v1/skills/owner/repo/architect/versions`, enriches the matching version entry with `isInstalled: true`, and returns JSON; given platform unreachable, then HTTP 502 with `{"error":"Platform API unavailable"}`

**Details**:
- Add route in `src/eval-server/api-routes.ts`: `GET /api/skills/:plugin/:skill/versions`
- Name resolution via `parseSource()` / `resolveFullName()` using lockfile `source` field
- Enrich: set `isInstalled: true` on entry matching lockfile `version`
- 502 on platform error with JSON body
- Integration test: mock platform fetch, verify enrichment and 502 path

---

### T-010: Eval-Server Diff Proxy Route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] completed
**Test**: Given `GET /api/skills/myPlugin/architect/versions/diff?from=1.0.0&to=2.0.0` → When processed → Then proxied to platform `GET /api/v1/skills/owner/repo/architect/versions?from=1.0.0&to=2.0.0` and `{ from, to, diffSummary, contentDiff }` returned unchanged; given missing `from` or `to` params, then HTTP 400

**Details**:
- Add route: `GET /api/skills/:plugin/:skill/versions/diff`
- Validate `from` and `to` query params (400 if absent)
- Forward to platform, pass response through
- Integration test: mock platform fetch, assert upstream URL and response pass-through; assert 400 on missing params

---

### T-011: Eval-Server Single-Skill Update SSE Endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03
**Status**: [x] completed
**Test**: Given `POST /api/skills/myPlugin/architect/update` → When processed → Then `initSSE(res)` called, update pipeline runs, SSE events `{event:"progress",data:{status:"updating"}}` → `{event:"progress",data:{status:"done"}}` → `{event:"done"}` emitted; given update fails, then `{event:"error",data:{error:"..."}}` followed by `{event:"done"}`

**Details**:
- Add route: `POST /api/skills/:plugin/:skill/update`
- Use `initSSE`, `sendSSE`, `sendSSEDone` from `src/eval-server/sse-helpers.ts`
- Extract per-skill update pipeline with progress callback (reuse from `updateCommand`)
- Integration test: assert SSE event sequence for success and error cases

---

### T-012: Eval-Server Batch Update SSE + 409 Conflict Guard
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04, AC-US3-06
**Status**: [x] completed
**Test**: Given `POST /api/skills/batch-update` with body `{"skills":["architect","pm"]}` → When processed → Then skills updated sequentially with `skill:start`, `skill:done`/`skill:error` SSE events per skill and final `batch:done` with `{updated, failed, skipped}`; given a second POST while first is in progress, then HTTP 409 with `{"error":"Update already in progress"}`

**Details**:
- Add route: `POST /api/skills/batch-update`
- Module-level `batchUpdateInProgress: boolean` flag for 409 enforcement
- Sequential processing (not parallel) to avoid lockfile race conditions
- Per-skill events: `skill:start`, `skill:done` / `skill:error`; final `batch:done`
- Integration test: mock update pipeline, assert SSE sequence and 409 path

---

## US-004: Studio Updates Panel

### T-013: Studio Type Extensions
**User Story**: US-004, US-005, US-006 | **Satisfies ACs**: AC-US4-02, AC-US5-02, AC-US6-01
**Status**: [x] completed
**Test**: Given `src/eval-ui/src/types.ts` is extended → When TypeScript compiles (`tsc --noEmit`) → Then no type errors; `VersionEntry`, `VersionDiff`, `VersionDetail`, `BatchUpdateProgress` are exported; `SkillInfo.pinnedVersion` is optional string

**Details**:
- Add to `src/eval-ui/src/types.ts`:
  - `VersionEntry { version, certTier, certScore?, diffSummary, createdAt, isInstalled? }`
  - `VersionDiff { from, to, diffSummary, contentDiff }`
  - `VersionDetail { version, content, certTier, certScore?, createdAt }`
  - `BatchUpdateProgress { skill, status: "pending"|"updating"|"scanning"|"installing"|"done"|"error"|"skipped", fromVersion?, toVersion?, scanScore?, scanVerdict?, error? }`
  - Extend `SkillInfo` with `pinnedVersion?: string`
- Unit test: TypeScript compilation check

---

### T-014: `parseUnifiedDiff` Utility
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01
**Status**: [x] completed
**Test**: Given a standard unified diff string with `@@` hunks, `+` additions, `-` deletions, and context lines → When `parseUnifiedDiff(diffStr)` is called → Then it returns `DiffLine[]` with correct `type` values (`"add"`, `"remove"`, `"context"`, `"header"`) and content without leading `+`/`-`

**Details**:
- Create `src/eval-ui/src/utils/parseUnifiedDiff.ts`
- Parse `@@` hunk headers, `+` lines (add), `-` lines (remove), space lines (context)
- Return `DiffLine[]` compatible with the `ChangelogViewer` rendering table
- Unit tests: empty diff, single hunk, multi-hunk, lines with special chars

---

### T-015: `ChangelogViewer` Base Component
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-06
**Status**: [x] completed
**Test**: Given `<ChangelogViewer contentDiff={unifiedDiffStr} fromLabel="1.0.0" toLabel="2.0.0" diffSummary="Added X" />` → Then addition lines have green background, deletion lines red, context lines gray; header shows `from 1.0.0 → to 2.0.0` with `diffSummary` above the diff; given empty `contentDiff`, then "Unable to load diff. Try again." with retry button shown

**Details**:
- Create `src/eval-ui/src/components/ChangelogViewer.tsx`
- Extract diff rendering table from `ImproveDiffView` in `HistoryPanel.tsx` (lines ~417–593)
- Props: `{ contentDiff: string; fromLabel: string; toLabel: string; diffSummary?: string; maxHeight?: number; collapsible?: boolean }`
- Uses `parseUnifiedDiff()` from T-014
- Replace `ImproveDiffView`'s inline table with `<ChangelogViewer />` (refactor, no behaviour change)
- Unit tests: green/red/gray rendering, header display, error/empty state, retry callback

---

### T-016: `ChangelogViewer` Side-by-Side Toggle + Dual Render Context
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02, AC-US6-04, AC-US6-05
**Status**: [x] completed
**Test**: Given `ChangelogViewer` is rendered → When "Side-by-side" toggle clicked → Then view switches to two-column layout with synchronized scrolling; given `renderContext="modal"` prop → Then rendered in a modal/drawer wrapper; given `renderContext="inline"` → Then rendered without modal chrome

**Details**:
- Add `sideBy side` toggle state (default: unified)
- Side-by-side: two scrollable columns, `onScroll` synchronized via `ref`s
- Add `renderContext?: "modal" | "inline"` prop controlling wrapper element
- Unit test: toggle state change, scroll sync, modal vs inline wrapper class

---

### T-017: Studio API Client Extensions
**User Story**: US-004, US-005 | **Satisfies ACs**: AC-US4-01, AC-US5-02
**Status**: [x] completed
**Test**: Given Studio API client is extended → When `api.getSkillVersions("myPlugin","architect")` called → Then fetch hits `/api/skills/myPlugin/architect/versions`; when `api.getVersionDiff("myPlugin","architect","1.0.0","2.0.0")` called → Then `/api/skills/myPlugin/architect/versions/diff?from=1.0.0&to=2.0.0`; when `api.startBatchUpdate(["architect","pm"])` called → Then `POST /api/skills/batch-update` with correct body and returns `EventSource`

**Details**:
- Add to Studio API client (`src/eval-ui/src/api.ts` or equivalent):
  - `getSkillVersions(plugin, skill): Promise<VersionEntry[]>`
  - `getVersionDiff(plugin, skill, from, to): Promise<VersionDiff>`
  - `startBatchUpdate(skills: string[]): EventSource`
  - `startSkillUpdate(plugin, skill): EventSource`
- Unit tests with mocked `fetch`: assert URL, method, body for each function

---

### T-018: UpdatesPanel — Layout, Outdated List, Pin Display, Empty State
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05, AC-US4-06
**Status**: [x] completed
**Test**: Given Studio navigates to `?view=updates` with 2 outdated skills (one pinned) → When `UpdatesPanel` renders → Then list shows name, installed→latest versions, bump type badge, diff summary, and "Update" button per row; pinned skill shows pin icon and disabled "Update" button with tooltip `Pinned — unpin from CLI to update`; given 0 outdated skills → Then "All skills are up to date" empty state with refresh button shown

**Details**:
- Create `src/eval-ui/src/pages/UpdatesPanel.tsx`
- Fetch outdated skills via `api.getSkillUpdates()` on mount
- Row: checkbox, name, installed→latest, bump badge, diff summary, "Update" + "View Changes" buttons
- Pinned row: pin icon, disabled "Update" with tooltip, excluded from "Update All" selection
- Empty state: text + re-fetch button
- Unit test: render with mixed skill list, assert pin row behaviour and empty state

---

### T-019: UpdatesPanel — Batch Update SSE Integration + Summary Toast
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04, AC-US4-07, AC-US4-08
**Status**: [x] completed
**Test**: Given 2 updatable skills and user clicks "Update All" → When `POST /api/skills/batch-update` streams SSE events → Then "Update All" shows loading state and each skill row transitions `pending → updating → done`; given `skill:error` for one skill → Then its row shows red error while remaining skills continue; given `batch:done` → Then list refreshes and toast shows "Updated N skills, M failed"

**Details**:
- `EventSource` connection to `/api/skills/batch-update` on "Update All" click
- Per-skill progress state map: `{ [skill]: BatchUpdateProgress }`
- Individual "Update" button: button → spinner → green checkmark via `api.startSkillUpdate()`
- On `batch:done`: re-fetch outdated list + show toast notification
- Unit test: simulate SSE events, assert component state transitions

---

### T-020: Navigation Sidebar — Updates Entry + Route
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] completed
**Test**: Given Studio loads with 3 outdated skills → When sidebar renders → Then "Updates" nav entry appears with yellow badge showing `3`; when clicked, URL changes to `?view=updates` and `UpdatesPanel` renders; given 0 outdated skills → Then badge is hidden

**Details**:
- Add "Updates" entry to Studio left-nav (follow existing nav item pattern)
- Badge: yellow, shows `updateCount` from `StudioContext` when > 0
- Add `?view=updates` route in `App.tsx` rendering `<UpdatesPanel />`
- Extend `StudioContext` to expose `updateCount` (derived from existing `mergeUpdatesIntoSkills`)
- Unit test: badge count display, routing assertion

---

## US-005: Studio Version History Tab

### T-021: VersionHistoryPanel — Timeline Rendering + Pagination
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-06
**Status**: [x] completed
**Test**: Given a skill is selected and Versions tab is active → When `VersionHistoryPanel` renders → Then vertical timeline lists version entries with version number, cert tier badge (gold/blue/gray), publish date, and truncated diff summary; installed entry has filled dot + "installed" label; given user scrolls to bottom → Then next page fetched via cursor pagination

**Details**:
- Create `src/eval-ui/src/pages/workspace/VersionHistoryPanel.tsx`
- Use `useSWR` with cursor pagination for `GET /api/skills/:plugin/:skill/versions`
- Cert tier colour: gold = CERTIFIED, blue = VERIFIED, gray = COMMUNITY
- Installed marker: `isInstalled: true` → filled dot + "installed" label
- Infinite scroll via `IntersectionObserver` at sentinel element
- Unit test: timeline entries rendering, installed marker, pagination trigger

---

### T-022: VersionHistoryPanel — Diff Interaction + Auto-Select Installed→Latest
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05
**Status**: [x] completed
**Test**: Given Versions tab active → When user clicks a version entry → Then it is selected (highlighted); when user clicks a second entry → Then `ChangelogViewer` expands inline below the timeline with diff loaded from `api.getVersionDiff`; given installed ≠ latest → When tab loads → Then "View changes since installed" link appears and clicking auto-opens ChangelogViewer with installed→latest diff

**Details**:
- Two-click selection model: first click = `selectedA`, second click = `selectedB` → triggers diff fetch
- "Compare" button appears after first selection
- On diff: `<ChangelogViewer renderContext="inline" />` below timeline
- Auto-select: if installed version ≠ latest → render link; on click set versions and fetch diff
- Unit test: selection state machine, diff fetch trigger, auto-link visibility

---

### T-023: Workspace Tab Integration — PanelId, TabBar, `Ctrl+8`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Status**: [x] completed
**Test**: Given `SkillWorkspace` renders → When `PanelId` is extended with `"versions"` → Then TypeScript compiles without error; Versions tab appears in "Insights" group in `TabBar`; when user presses `Ctrl+8` → Then Versions tab becomes active

**Details**:
- Extend `PanelId` union type in `SkillWorkspace.tsx` with `"versions"`
- Add to `VALID_PANELS` array
- Add to `TAB_GROUPS` under "Insights" group in `TabBar.tsx`
- Register `Ctrl+8` keyboard shortcut (follow existing `Ctrl+1..7` pattern)
- Render `<VersionHistoryPanel />` when `activePanel === "versions"`
- Unit test: keyboard shortcut fires panel switch, tab appears in correct group

---

## US-006: Changelog Viewer — Additional Wiring

### T-024: SkillCard Pin Badge + Verify Dual ChangelogViewer Context
**User Story**: US-006 | **Satisfies ACs**: AC-US6-04, AC-US6-05
**Status**: [x] completed
**Test**: Given `SkillInfo.pinnedVersion = "1.0.0"` → When `SkillCard` renders → Then a `📌` pin badge appears alongside any update badge; given no `pinnedVersion` → Then no pin badge shown; given UpdatesPanel "View changes" clicked → Then `<ChangelogViewer renderContext="modal" />` opens correctly; given Version History diff triggered → Then `<ChangelogViewer renderContext="inline" />` renders below timeline

**Details**:
- Modify `SkillCard.tsx`: read `skillInfo.pinnedVersion`, render pin icon in top-right when set
- Pin badge co-exists with update dot if both present
- Wire UpdatesPanel "View changes" button → modal ChangelogViewer (T-016 provides modal support)
- Wire VersionHistoryPanel diff trigger → inline ChangelogViewer (T-022 provides inline rendering)
- Unit test: SkillCard with/without `pinnedVersion`, badge presence; integration: modal and inline paths
