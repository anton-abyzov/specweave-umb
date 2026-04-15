---
increment: 0666-skill-version-lifecycle
title: "Skill Version Management - Phase 2: Version History, Changelogs, Batch Update UI"
generated: 2026-04-14
source: auto-generated
version: "1.0"
status: active
---

# Quality Rubric: Skill Version Management — Phase 2

> Review and customize criteria below before implementation begins.
> Change severity, add/remove criteria, adjust thresholds as needed.

---

## Category 1: US-001 — Enhanced `vskill versions` Command

### R-001: Installed version marker in table [blocking]
- **Source**: AC-US1-01
- **Evaluator**: sw:grill
- **Verify**: `vskill versions <skill>` table shows `►` in Installed column for the currently installed version, column headers include `Version | Tier | Date | Installed | Changes`
- **Threshold**: Marker appears for installed version; absent when skill not in lockfile
- **Result**: [ ] PENDING

### R-002: diffSummary column truncation [blocking]
- **Source**: AC-US1-02
- **Evaluator**: sw:grill
- **Verify**: Changes column shows `diffSummary` from platform API, truncated to 60 chars with `…` ellipsis
- **Threshold**: Truncation at exactly 60 chars; no truncation when <= 60 chars
- **Result**: [ ] PENDING

### R-003: `--diff` flag shows unified diff installed→latest [blocking]
- **Source**: AC-US1-03
- **Evaluator**: sw:grill
- **Verify**: `vskill versions <skill> --diff` calls `getVersionDiff(installed, latest)` and prints ANSI-colored unified diff to stdout
- **Threshold**: Correct version pair used; ANSI colors present; diff content matches API response
- **Result**: [ ] PENDING

### R-004: `--from`/`--to` overrides default diff range [blocking]
- **Source**: AC-US1-04
- **Evaluator**: sw:grill
- **Verify**: `vskill versions <skill> --diff --from 1.0 --to 2.0` uses specified versions regardless of installed version
- **Threshold**: `getVersionDiff` called with exactly the specified versions
- **Result**: [ ] PENDING

### R-005: Skill not installed warning for `--diff` [blocking]
- **Source**: AC-US1-05
- **Evaluator**: sw:grill
- **Verify**: When skill not in lockfile and `--from`/`--to` absent, warning message printed and process exits without error
- **Threshold**: Exact message: `Skill not installed. Use --from and --to to compare specific versions.`
- **Result**: [ ] PENDING

### R-006: `--json` output format with `installed` boolean [blocking]
- **Source**: AC-US1-06
- **Evaluator**: sw:grill
- **Verify**: `vskill versions <skill> --json` outputs valid JSON array with `version`, `diffSummary`, and `installed: boolean` per entry
- **Threshold**: Valid JSON; `installed: true` on exactly one entry (the lockfile version); all other fields present
- **Result**: [ ] PENDING

---

## Category 2: US-002 — Version Pinning

### R-007: `vskill pin` writes pinnedVersion to lockfile [blocking]
- **Source**: AC-US2-01
- **Evaluator**: sw:grill
- **Verify**: After `vskill pin owner/repo/skill`, `SkillLockEntry.pinnedVersion === installedVersion`; success message printed
- **Threshold**: Lockfile correctly written; message matches `Pinned owner/repo/skill at <version>`
- **Result**: [ ] PENDING

### R-008: `vskill unpin` removes pinnedVersion from lockfile [blocking]
- **Source**: AC-US2-02
- **Evaluator**: sw:grill
- **Verify**: After `vskill unpin owner/repo/skill`, `pinnedVersion` field is absent from `SkillLockEntry`; success message printed
- **Threshold**: Lockfile written without `pinnedVersion`; message matches `Unpinned owner/repo/skill`
- **Result**: [ ] PENDING

### R-009: Pinned skill shown with 📌 in `outdated` table [blocking]
- **Source**: AC-US2-03
- **Evaluator**: sw:grill
- **Verify**: `vskill outdated` shows pinned skills with `📌 <pinnedVersion>` in Pin column; count summary excludes pinned skills
- **Threshold**: Pin column populated; summary count accurate (excludes pinned)
- **Result**: [ ] PENDING

### R-010: Pinned skill skipped during `vskill update` [blocking]
- **Source**: AC-US2-04
- **Evaluator**: sw:grill
- **Verify**: `vskill update` skips skills with `pinnedVersion` set; dim skip message logged per skipped skill
- **Threshold**: No update pipeline runs for pinned skill; message matches `Skipped <name> (pinned at <version>)`
- **Result**: [ ] PENDING

### R-011: `--force` overrides pin during update [blocking]
- **Source**: AC-US2-05
- **Evaluator**: sw:grill
- **Verify**: `vskill update <skill> --force` runs full update pipeline despite `pinnedVersion`; pin remains set after update
- **Threshold**: Update completes; `pinnedVersion` unchanged in lockfile after `--force` update
- **Result**: [ ] PENDING

### R-012: Error when pinning uninstalled skill [blocking]
- **Source**: AC-US2-06
- **Evaluator**: sw:grill
- **Verify**: `vskill pin <unknown>` prints error and exits with code 1
- **Threshold**: Exact message: `Skill <name> is not installed`; exit code 1
- **Result**: [ ] PENDING

### R-013: Pinned field in `outdated --json` output [blocking]
- **Source**: AC-US2-07
- **Evaluator**: sw:grill
- **Verify**: `vskill outdated --json` output includes `"pinned": true` for each pinned skill entry
- **Threshold**: `pinned` field present and `true` on all pinned entries; absent on non-pinned entries
- **Result**: [ ] PENDING

---

## Category 3: US-003 — Eval-Server Routes

### R-014: Versions proxy enriches with `isInstalled` [blocking]
- **Source**: AC-US3-01
- **Evaluator**: sw:grill
- **Verify**: `GET /api/skills/:plugin/:skill/versions` proxies to platform and adds `isInstalled: true` on the lockfile-matched version entry
- **Threshold**: Exactly one entry marked `isInstalled: true`; all other entries lack the field or have `false`
- **Result**: [ ] PENDING

### R-015: Diff proxy returns unified diff payload [blocking]
- **Source**: AC-US3-02
- **Evaluator**: sw:grill
- **Verify**: `GET /api/skills/:plugin/:skill/versions/diff?from=X&to=Y` returns `{ from, to, diffSummary, contentDiff }` proxied from platform
- **Threshold**: All four fields present; `from`/`to` match query params; 400 returned when params absent
- **Result**: [ ] PENDING

### R-016: Single-skill update SSE event sequence [blocking]
- **Source**: AC-US3-03
- **Evaluator**: sw:grill
- **Verify**: `POST /api/skills/:plugin/:skill/update` emits SSE events: `progress(updating)` → `progress(done)` → `done`; error path emits `error` event
- **Threshold**: Event sequence in correct order; SSE headers correct; connection closes after `done`
- **Result**: [ ] PENDING

### R-017: Batch update SSE per-skill events and `batch:done` [blocking]
- **Source**: AC-US3-04
- **Evaluator**: sw:grill
- **Verify**: `POST /api/skills/batch-update` emits `skill:start`, `skill:done`/`skill:error` for each skill, then `batch:done` with summary counts
- **Threshold**: Event per skill in order; `batch:done.updated + failed + skipped` = total skills submitted
- **Result**: [ ] PENDING

### R-018: 502 on platform API unreachable [blocking]
- **Source**: AC-US3-05
- **Evaluator**: sw:grill
- **Verify**: When platform API returns error or times out, eval-server returns HTTP 502 with `{"error":"Platform API unavailable"}`
- **Threshold**: HTTP status 502; exact JSON body
- **Result**: [ ] PENDING

### R-019: 409 when batch update already in progress [blocking]
- **Source**: AC-US3-06
- **Evaluator**: sw:grill
- **Verify**: Second `POST /api/skills/batch-update` while first is running returns HTTP 409 with `{"error":"Update already in progress"}`
- **Threshold**: HTTP status 409; exact JSON body; first batch continues unaffected
- **Result**: [ ] PENDING

---

## Category 4: US-004 — Studio Updates Panel

### R-020: Updates Panel accessible via nav [blocking]
- **Source**: AC-US4-01
- **Evaluator**: sw:grill
- **Verify**: `#/updates` or `?view=updates` renders UpdatesPanel with outdated skills fetched from API; "Updates" nav entry present in sidebar
- **Threshold**: Route renders panel; outdated skills list populated on mount
- **Result**: [ ] PENDING

### R-021: Outdated skill row shows all required fields [blocking]
- **Source**: AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: Each row in UpdatesPanel shows: skill name, installed version, latest version, bump type (patch/minor/major), diff summary, "Update" button
- **Threshold**: All 6 fields present per row; bump type correctly classified
- **Result**: [ ] PENDING

### R-022: "Update All" triggers batch SSE and shows progress [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: "Update All" sends `POST /api/skills/batch-update` with non-pinned skills; progress section shows per-skill status via SSE
- **Threshold**: Pinned skills excluded from batch payload; all selected skills appear in progress section
- **Result**: [ ] PENDING

### R-023: Individual "Update" button shows real-time progress [blocking]
- **Source**: AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: Clicking "Update" on a skill row changes button to spinner; on SSE `done` event row shows green checkmark with new version
- **Threshold**: Button state transitions: enabled → spinner → checkmark; version displayed updates to latest
- **Result**: [ ] PENDING

### R-024: Pinned skill row disabled in Updates Panel [blocking]
- **Source**: AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: Pinned skill shows pin icon; "Update" button disabled with tooltip `Pinned — unpin from CLI to update`; excluded from "Update All" selection
- **Threshold**: `disabled` attribute on button; tooltip text exact match; checkbox absent or unchecked for pinned
- **Result**: [ ] PENDING

### R-025: Empty state when all skills up to date [blocking]
- **Source**: AC-US4-06
- **Evaluator**: sw:grill
- **Verify**: When no outdated skills, panel shows "All skills are up to date" with refresh button
- **Threshold**: Exact empty state message; refresh button re-fetches outdated list
- **Result**: [ ] PENDING

### R-026: Failed skill shows error; batch continues [blocking]
- **Source**: AC-US4-07
- **Evaluator**: sw:grill
- **Verify**: When one skill emits `skill:error` SSE, its row shows red error indicator with message; remaining skills continue updating
- **Threshold**: Error indicator per failed skill; other skills not blocked
- **Result**: [ ] PENDING

### R-027: Post-batch list refresh and summary toast [blocking]
- **Source**: AC-US4-08
- **Evaluator**: sw:grill
- **Verify**: After `batch:done` SSE, outdated list refreshes automatically and toast shows "Updated N skills, M failed"
- **Threshold**: List reflects post-update state; toast counts match SSE summary
- **Result**: [ ] PENDING

---

## Category 5: US-005 — Studio Version History Tab

### R-028: Versions tab exists and keyboard shortcut works [blocking]
- **Source**: AC-US5-01
- **Evaluator**: sw:grill
- **Verify**: "Versions" tab appears in workspace tab bar alongside other tabs; `Ctrl+8` activates it
- **Threshold**: Tab rendered in "Insights" group; keyboard shortcut fires panel switch
- **Result**: [ ] PENDING

### R-029: Version timeline renders with cert badges [blocking]
- **Source**: AC-US5-02
- **Evaluator**: sw:grill
- **Verify**: Timeline shows each version with: version number, cert tier badge (gold/blue/gray), publish date, truncated diff summary
- **Threshold**: All four fields per entry; badge color matches tier (CERTIFIED=gold, VERIFIED=blue, COMMUNITY=gray)
- **Result**: [ ] PENDING

### R-030: Installed version has distinct visual marker [blocking]
- **Source**: AC-US5-03
- **Evaluator**: sw:grill
- **Verify**: The installed version entry in timeline shows filled dot + "installed" label distinct from other entries
- **Threshold**: Marker visible; only one entry marked; matches `isInstalled: true` from API
- **Result**: [ ] PENDING

### R-031: Two-click diff selection opens ChangelogViewer inline [blocking]
- **Source**: AC-US5-04
- **Evaluator**: sw:grill
- **Verify**: Clicking first version selects it; clicking second (or "Compare") opens ChangelogViewer inline below timeline with correct diff loaded
- **Threshold**: `getVersionDiff` called with correct version pair; ChangelogViewer renders inline (not modal)
- **Result**: [ ] PENDING

### R-032: Auto-select installed→latest link when behind [blocking]
- **Source**: AC-US5-05
- **Evaluator**: sw:grill
- **Verify**: When installed version ≠ latest, "View changes since installed" link appears; clicking auto-opens ChangelogViewer with installed→latest diff
- **Threshold**: Link visible only when installed ≠ latest; diff loaded for correct pair on click
- **Result**: [ ] PENDING

### R-033: Infinite scroll loads next page of versions [blocking]
- **Source**: AC-US5-06
- **Evaluator**: sw:grill
- **Verify**: When user scrolls to bottom of timeline, next page is fetched using cursor from previous response
- **Threshold**: API called with correct cursor param; new entries appended (not replaced)
- **Result**: [ ] PENDING

---

## Category 6: US-006 — Studio Changelog Viewer

### R-034: Unified diff renders with correct color coding [blocking]
- **Source**: AC-US6-01
- **Evaluator**: sw:grill
- **Verify**: ChangelogViewer shows green background for additions, red for deletions, gray for context lines
- **Threshold**: All three colors applied correctly; `parseUnifiedDiff` produces correct `DiffLine[]` input
- **Result**: [ ] PENDING

### R-035: Side-by-side toggle with synchronized scrolling [blocking]
- **Source**: AC-US6-02
- **Evaluator**: sw:grill
- **Verify**: "Side-by-side" toggle switches to two-column layout; scrolling one column scrolls the other in sync
- **Threshold**: Two columns rendered; scroll events synchronized via refs
- **Result**: [ ] PENDING

### R-036: Changelog Viewer header shows version labels and diffSummary [blocking]
- **Source**: AC-US6-03
- **Evaluator**: sw:grill
- **Verify**: Header displays from-version, to-version, cert tier badges for each, and `diffSummary` text above raw diff
- **Threshold**: All header elements present; versions and summary match API response
- **Result**: [ ] PENDING

### R-037: Changelog Viewer opens as modal from Updates Panel [blocking]
- **Source**: AC-US6-04
- **Evaluator**: sw:grill
- **Verify**: "View changes" from UpdatesPanel opens ChangelogViewer in modal/drawer; shows diff between installed and latest
- **Threshold**: Modal wrapper rendered; correct version pair diff loaded
- **Result**: [ ] PENDING

### R-038: Changelog Viewer renders inline from Version History [blocking]
- **Source**: AC-US6-05
- **Evaluator**: sw:grill
- **Verify**: When triggered from Version History tab, ChangelogViewer renders inline below timeline (no modal)
- **Threshold**: No modal chrome; inline placement below timeline
- **Result**: [ ] PENDING

### R-039: Error state with retry button [blocking]
- **Source**: AC-US6-06
- **Evaluator**: sw:grill
- **Verify**: When diff endpoint returns error or empty contentDiff, shows "Unable to load diff. Try again." with retry button
- **Threshold**: Exact message text; retry button triggers re-fetch
- **Result**: [ ] PENDING

---

## Category 7: Infrastructure & Quality

### R-040: Test coverage meets targets [blocking]
- **Source**: NFR
- **Evaluator**: sw:code-reviewer
- **Verify**: Unit test coverage ≥ 95% for CLI commands and utils; integration test coverage ≥ 90% for eval-server routes; E2E tests cover 100% of AC scenarios
- **Threshold**: Coverage report meets targets; no untested branches in critical paths
- **Result**: [ ] PENDING

### R-041: TypeScript compilation clean [blocking]
- **Source**: NFR
- **Evaluator**: sw:code-reviewer
- **Verify**: `tsc --noEmit` passes with zero errors across all modified files in vskill and eval-ui
- **Threshold**: Zero TypeScript errors
- **Result**: [ ] PENDING

### R-042: Lockfile backwards compatibility [blocking]
- **Source**: FR-001
- **Evaluator**: sw:grill
- **Verify**: Existing lockfiles without `pinnedVersion` field continue to work without migration; no runtime errors on old lockfile schema
- **Threshold**: All lockfile operations succeed on old-format files
- **Result**: [ ] PENDING

### R-043: Batch update sequential (no race conditions) [blocking]
- **Source**: FR-003, NFR-Concurrency
- **Evaluator**: sw:grill
- **Verify**: Batch update processes skills sequentially; lockfile writes do not overlap; `batchUpdateInProgress` flag prevents concurrent batches
- **Threshold**: Sequential execution confirmed; 409 prevents concurrent batch
- **Result**: [ ] PENDING

### R-044: Platform API proxy response time [advisory]
- **Source**: NFR-Performance
- **Evaluator**: sw:grill
- **Verify**: Versions proxy endpoint responds in under 300ms p95; diff endpoint under 500ms under normal conditions
- **Threshold**: Response times within NFR bounds in integration tests with mock platform
- **Result**: [ ] PENDING

### R-045: Accessibility — keyboard nav in Updates Panel and Version History [blocking]
- **Source**: NFR-Accessibility
- **Evaluator**: sw:grill
- **Verify**: All interactive elements in UpdatesPanel and VersionHistoryPanel reachable via keyboard; ARIA labels present on icon-only buttons
- **Threshold**: Tab order logical; no keyboard traps; screen reader labels on pin icon and cert badges
- **Result**: [ ] PENDING
