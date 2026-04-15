---
increment: 0666-skill-version-lifecycle
title: >-
  Skill Version Management - Phase 2: Version History, Changelogs, Batch Update
  UI
type: feature
priority: P1
status: completed
created: 2026-04-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Version Management - Phase 2: Version History, Changelogs, Batch Update UI

## Problem Statement

Phase 1 (0664) gave users awareness of outdated skills — `vskill outdated`, post-install hints, and Studio badges. But users still cannot: browse version history, see what changed between versions, pin skills to avoid unwanted updates, or batch-update from Studio. The `vskill versions` command shows a bare table without indicating which version is installed. There is no way to compare versions or trigger updates from the Studio UI.

## Goals

- Let users browse full version history with changelogs and diffs from both CLI and Studio
- Provide version pinning to lock skills at a specific version, excluding them from outdated checks and updates
- Enable batch updates from the Studio UI with per-skill control and real-time progress
- Enhance the `vskill versions` command with installed markers, diff summaries, and a --diff flag

## Dependencies

- **0664-skill-version-awareness** (completed) — `vskill outdated`, check-updates API, Studio badges, post-install hints
- **Platform APIs** (deployed, read-only):
  - `GET /api/v1/skills/{o}/{r}/{s}/versions` — cursor-based pagination, returns `diffSummary`
  - `GET /api/v1/skills/{o}/{r}/{s}/versions/{version}` — full version content
  - `GET /api/v1/skills/{o}/{r}/{s}/versions?from=X&to=Y` — unified diff + `diffSummary`
  - `POST /api/v1/skills/check-updates` — batch update check

## User Stories

### US-001: Enhanced `vskill versions` Command (P1)
**Project**: vskill

**As a** skill user
**I want** `vskill versions <skill>` to show which version I have installed, summarize changes per version, and optionally show a full diff
**So that** I can understand what changed across versions without leaving the terminal

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill is installed at version `1.0.0`, when running `vskill versions <skill>`, then the table includes columns `Version | Tier | Date | Installed | Changes` and the row for `1.0.0` shows a `►` marker in the Installed column
- [x] **AC-US1-02**: Given the platform API returns `diffSummary` per version, when running `vskill versions <skill>`, then the Changes column displays the truncated `diffSummary` (max 60 chars, ellipsis if longer)
- [x] **AC-US1-03**: Given a skill is installed at version `1.0.0` and latest is `1.2.0`, when running `vskill versions <skill> --diff`, then a unified diff between `1.0.0` and `1.2.0` is printed to stdout using the platform `?from=1.0.0&to=1.2.0` endpoint
- [x] **AC-US1-04**: Given `--diff` is used with `--from <v1> --to <v2>` flags, when running the command, then the diff between the two specified versions is shown instead of installed-to-latest
- [x] **AC-US1-05**: Given the skill is not installed (not in lockfile), when running `vskill versions <skill>`, then no Installed marker is shown and `--diff` without `--from/--to` prints a warning: `Skill not installed. Use --from and --to to compare specific versions.`
- [x] **AC-US1-06**: Given `--json` flag is used, when running `vskill versions <skill> --json`, then the full versions array with `diffSummary` and `installed: boolean` fields is output as JSON

---

### US-002: Version Pinning (P1)
**Project**: vskill

**As a** skill user
**I want** to pin a skill to its current version so it is excluded from outdated checks and update operations
**So that** I can lock known-good versions and avoid unintended changes

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a skill `owner/repo/skill` is installed, when running `vskill pin owner/repo/skill`, then the `SkillLockEntry` for that skill gains `"pinned": true` and a success message is printed: `Pinned owner/repo/skill at 1.0.0`
- [x] **AC-US2-02**: Given a skill is pinned, when running `vskill unpin owner/repo/skill`, then the `pinned` field is removed from the `SkillLockEntry` and a success message is printed: `Unpinned owner/repo/skill`
- [x] **AC-US2-03**: Given a skill is pinned and a newer version exists, when running `vskill outdated`, then the pinned skill appears in the table with a `📌` indicator in a Pin column and is excluded from the outdated count summary
- [x] **AC-US2-04**: Given a skill is pinned, when running `vskill update` (all) or `vskill update owner/repo/skill`, then the pinned skill is silently skipped and a dim message is printed: `Skipped owner/repo/skill (pinned at 1.0.0)`
- [x] **AC-US2-05**: Given a skill is pinned, when running `vskill update owner/repo/skill --force`, then the pin is ignored and the skill is updated to the latest version (pin remains set)
- [x] **AC-US2-06**: Given a skill name that is not in the lockfile, when running `vskill pin <name>`, then it prints an error: `Skill <name> is not installed` and exits with code 1
- [x] **AC-US2-07**: Given `vskill outdated --json` is invoked, when pinned skills are present, then each pinned skill in the output includes `"pinned": true`

---

### US-003: Eval-Server Version & Update Routes (P1)
**Project**: vskill

**As a** Studio frontend
**I want** eval-server endpoints that proxy version history, diffs, and trigger skill updates with progress streaming
**So that** Studio can display version data and perform updates without direct platform API access

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `GET /api/skills/:plugin/:skill/versions` is called, when the eval-server processes it, then it proxies the request to the platform `GET /api/v1/skills/{o}/{r}/{s}/versions` API, enriches each version with `installed: boolean` by checking the lockfile, and returns the result as JSON
- [x] **AC-US3-02**: Given `GET /api/skills/:plugin/:skill/versions/diff?from=X&to=Y` is called, when the eval-server processes it, then it proxies to the platform `?from=X&to=Y` endpoint and returns the unified diff + `diffSummary`
- [x] **AC-US3-03**: Given `POST /api/skills/:plugin/:skill/update` is called, when the eval-server processes it, then it initiates `vskill update <plugin>/<skill>` as a child process, streams progress via SSE events (`progress`, `done`, `error`), and the SSE connection uses the existing `initSSE`/`sendSSE`/`sendSSEDone` helpers
- [x] **AC-US3-04**: Given `POST /api/skills/update-batch` is called with body `{"skills": ["owner/repo/skill1", "owner/repo/skill2"]}`, when the eval-server processes it, then it updates skills sequentially, streaming per-skill SSE events: `{event: "skill:start", skill}`, `{event: "skill:done", skill, version}`, `{event: "skill:error", skill, error}`, and a final `{event: "batch:done", results}`
- [x] **AC-US3-05**: Given the platform API is unreachable during a versions proxy request, when the eval-server handles the error, then it returns HTTP 502 with `{"error": "Platform API unavailable"}`
- [x] **AC-US3-06**: Given a batch update is in progress, when a second `POST /api/skills/update-batch` arrives, then it returns HTTP 409 with `{"error": "Update already in progress"}`

---

### US-004: Studio Updates Panel (P1)
**Project**: vskill

**As a** Studio user
**I want** a dedicated Updates panel where I can see all outdated skills and update them individually or in batch
**So that** I can manage skill updates from the browser without switching to the terminal

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the Studio is loaded, when navigating to `#/updates` (via a new "Updates" entry in the left panel nav), then the Updates Panel renders showing a list of outdated skills fetched from `GET /api/skills/updates`
- [x] **AC-US4-02**: Given the Updates Panel is displayed, when outdated skills are present, then each row shows: skill name, installed version, latest version, version bump type (patch/minor/major), diff summary, and an "Update" button
- [x] **AC-US4-03**: Given the Updates Panel has outdated skills, when the user clicks "Update All", then a `POST /api/skills/update-batch` request is sent with all non-pinned skill names and a progress section appears showing per-skill status (pending → updating → done/error) via SSE events
- [x] **AC-US4-04**: Given an individual "Update" button is clicked, when the update starts, then the button changes to a spinner, SSE events stream progress, and on completion the row shows a green checkmark with the new version
- [x] **AC-US4-05**: Given a skill in the Updates Panel is pinned, when the panel renders, then the skill row shows a pin icon, the "Update" button is disabled with tooltip "Pinned — unpin from CLI to update", and it is excluded from "Update All"
- [x] **AC-US4-06**: Given all skills are up to date (or no skills installed), when the Updates Panel renders, then it shows an empty state: "All skills are up to date" with a refresh button
- [x] **AC-US4-07**: Given a batch update is in progress, when a skill update fails, then its row shows a red error indicator with the error message and remaining skills continue updating
- [x] **AC-US4-08**: Given a batch update completes, when all skills finish, then the panel refreshes the outdated list automatically and shows a summary toast: "Updated N skills, M failed"

---

### US-005: Studio Version History Tab (P2)
**Project**: vskill

**As a** Studio user viewing a skill's detail workspace
**I want** a Version History tab showing a timeline of all published versions with cert badges and the ability to diff any two versions
**So that** I can understand the evolution of a skill and review changes before updating

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given a skill is selected in Studio, when navigating to the workspace, then a new "Versions" tab appears (alongside Editor, Tests, Run, Activation, History, Deps, Leaderboard) and is accessible via `Ctrl+8` keyboard shortcut
- [x] **AC-US5-02**: Given the Versions tab is active, when it renders, then it shows a vertical timeline of versions fetched from `GET /api/skills/:plugin/:skill/versions` with each entry displaying: version number, cert tier badge (color-coded: gold=CERTIFIED, blue=VERIFIED, gray=COMMUNITY), publish date, and truncated diff summary
- [x] **AC-US5-03**: Given the timeline is rendered, when the currently installed version appears, then it has a distinct visual marker (filled dot + "installed" label) differentiating it from other versions
- [x] **AC-US5-04**: Given two versions in the timeline, when the user clicks a version entry, then it selects that version; when a second version is clicked (or the "Compare" button is clicked), then the Changelog Viewer (US-006) opens showing the diff between the two selected versions
- [x] **AC-US5-05**: Given the installed version is not the latest, when the Versions tab loads, then a prominent "View changes since installed" link auto-selects installed→latest diff in the Changelog Viewer
- [x] **AC-US5-06**: Given the platform API returns paginated results, when the user scrolls to the bottom of the timeline, then the next page of versions is loaded (cursor-based pagination)

---

### US-006: Studio Changelog Viewer Component (P2)
**Project**: vskill

**As a** Studio user
**I want** a diff viewer that shows changes between two skill versions in unified or side-by-side format with color coding
**So that** I can quickly understand what was added, changed, or removed between versions

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the Changelog Viewer receives a diff payload from `GET /api/skills/:plugin/:skill/versions/diff?from=X&to=Y`, when it renders, then it displays the unified diff with green highlighting for additions, red for deletions, and gray for context lines
- [x] **AC-US6-02**: Given the Changelog Viewer is displayed, when the user toggles the "Side-by-side" switch, then the view changes from unified diff to a two-column side-by-side comparison with synchronized scrolling
- [x] **AC-US6-03**: Given the Changelog Viewer is open, when the diff header is rendered, then it shows: from-version, to-version, cert tier badges for each, and the `diffSummary` text as a human-readable changelog above the raw diff
- [x] **AC-US6-04**: Given the Changelog Viewer is used from the Updates Panel (US-004), when a user clicks "View changes" on an outdated skill, then the Changelog Viewer opens in a modal/drawer showing the diff between installed and latest versions
- [x] **AC-US6-05**: Given the Changelog Viewer is used from the Version History tab (US-005), when the user selects two versions, then the Changelog Viewer renders inline below the timeline (not a modal)
- [x] **AC-US6-06**: Given the diff endpoint returns an error, when the Changelog Viewer handles it, then it shows a fallback message: "Unable to load diff. Try again." with a retry button

## Functional Requirements

### FR-001: Lockfile Schema Extension
The `SkillLockEntry` interface gains an optional `pinned?: boolean` field. All existing lockfile operations remain unchanged. The `vskill pin`/`unpin` commands are the only writers of this field.

### FR-002: Platform API Proxying
The eval-server proxies platform version/diff APIs rather than re-implementing them. It enriches responses with local state (installed marker from lockfile) before returning to the Studio frontend.

### FR-003: SSE Update Progress
Skill updates triggered from Studio stream progress via Server-Sent Events using the existing `sse-helpers.ts` infrastructure. Batch updates process skills sequentially to avoid concurrent lockfile writes, streaming per-skill events.

### FR-004: Reusable Changelog Viewer
The Changelog Viewer is a standalone React component that accepts a diff payload and renders it. It is used in two contexts: inline in Version History tab and as a modal/drawer in the Updates Panel. The component does not fetch data itself — the parent provides the diff payload.

## Non-Functional Requirements

- **Performance**: Version history proxy responds in under 300ms (p95) for standard payloads. Diff endpoint under 500ms.
- **Reliability**: Batch update failures are isolated per-skill — one failure does not abort remaining updates.
- **Concurrency**: Only one batch update can run at a time (eval-server enforces via 409 response).
- **Backwards Compatibility**: `SkillLockEntry` extension is additive — old lockfiles without `pinned` field work without migration.
- **Accessibility**: Updates Panel and Version History tab support keyboard navigation and screen readers.

## Out of Scope

- Automatic background update checks / auto-update without user action
- Semver range constraints for pinning (e.g., `^1.2.0`, `~2.1`) — exact pin only
- Breaking change detection between versions
- `vskill rollback <skill> <version>` command
- Push notifications for new versions
- `vskill update --interactive` TUI checklist
- Platform API modifications (all APIs are read-only, already deployed)

## Edge Cases

- **Pinned + force update**: `--force` overrides pin for a single update, pin remains set afterward
- **Skill not in registry**: Local/GitHub-direct skills without registry entries show "No version history available" in Studio; CLI skips them in `--diff`
- **Concurrent lockfile writes**: Batch update processes skills sequentially to avoid write conflicts with the lockfile
- **Empty version history**: Skills with only one published version show the timeline with a single entry; diff is unavailable
- **Network failure mid-batch**: Per-skill SSE error events report the failure; remaining skills continue; summary includes failure count
- **Pinned skill in outdated --json**: Included in output with `"pinned": true` so consumers can filter if needed

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Platform version API slow for skills with many versions | 0.3 | 3 | 0.9 | Cursor pagination, fetch first page only in timeline |
| SSE connection drops during batch update | 0.2 | 5 | 1.0 | Client-side reconnect logic; eval-server completes update regardless of SSE state |
| Diff payload too large for inline rendering | 0.2 | 3 | 0.6 | Truncate at 500 lines with "Show full diff" expansion |
| Concurrent batch update requests from multiple tabs | 0.3 | 4 | 1.2 | 409 conflict response with clear error message in UI |

## Technical Notes

### Existing Patterns (from codebase)
- **CLI commands**: Commander.js with dynamic imports — `program.command("pin").action(async () => { ... })`
- **Lockfile ops**: `readLockfile()`, `writeLockfile()`, `addSkillToLock()` in `src/lockfile/lockfile.ts`
- **Eval-server routes**: `registerRoutes(router, root)` in `src/eval-server/api-routes.ts`
- **SSE helpers**: `initSSE()`, `sendSSE()`, `sendSSEDone()`, `withHeartbeat()` in `src/eval-server/sse-helpers.ts`
- **API client**: `getVersions()`, `checkUpdates()` in `src/api/client.ts`
- **Studio tabs**: `PanelId` union type in `SkillWorkspace.tsx` — extend with `"versions"`
- **Studio context**: `StudioContext.tsx` manages global state + update merging

### Architecture Decisions
- Eval-server proxies platform APIs (no direct browser→platform calls) to keep platform URLs internal
- Batch updates are sequential (not parallel) to avoid lockfile race conditions
- Changelog Viewer is a dumb component — data fetching is the parent's responsibility
- Pin/unpin are CLI-only operations; Studio displays pin state but cannot change it (keeps lockfile as CLI-owned)

## Success Metrics

- 30% of CLI users who run `vskill outdated` also use `vskill versions --diff` within 60 days
- 15% of Studio users visit the Updates Panel within 30 days of release
- Average batch update from Studio covers 3+ skills (validates batch value)
- Version pinning used by 10% of active CLI users within 60 days
