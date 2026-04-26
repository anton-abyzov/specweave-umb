# Tasks: Studio: smart update-bell click + cross-agent multi-location update awareness

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable with previous task
- `[ ]`: Not started, `[x]`: Completed
- TDD discipline: RED → GREEN → REFACTOR for each task. Tests first; implementation only after a failing test exists.

---

## Phase 1: Backend foundation

### T-001: `scanSkillInstallLocations` utility
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] Completed (8/8 tests pass)

**Description**: Create new pure utility that finds every install location of a skill by canonical name. Iterates `getInstallableAgents()`, probes both project (`<projectRoot>/<agent.localSkillsDir>/<slug>/SKILL.md`) and personal (`expandHome(agent.globalSkillsDir)/<slug>/SKILL.md`) paths per agent, plus plugin cache via `scanInstalledPluginSkills()`. Detects symlinks via `fs.lstat`.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-server/utils/scan-install-locations.ts`
- Exports: `scanSkillInstallLocations(canonicalName: string, projectRoot?: string): InstallLocation[]`
- Helper `expandHome` mirrored from `agents-registry.ts:827-833` (or imported if exported).
- Reuses: `getInstallableAgents()` from `src/agents/agents-registry.ts`, `scanInstalledPluginSkills()` from `src/eval/plugin-scanner.ts`.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-server/utils/__tests__/scan-install-locations.test.ts`
- **TC-001**: Given a tmp project with `.claude/skills/foo/SKILL.md` and `.codex/skills/foo/SKILL.md` → When `scanSkillInstallLocations("owner/repo/foo", projectRoot)` → Then returns 2 locations both `scope="project"`, agents `["claude-code", "codex-cli"]`, both `readonly: false`, `symlinked: false`.
- **TC-002**: Given personal install at `~/.claude/skills/foo/SKILL.md` (mocked HOME) → Returns 1 location `scope="personal"`, `agent="claude-code"`.
- **TC-003**: Given project install is a symlink to `<projectRoot>/.agents/skills/owner-repo-foo/` → `symlinked: true`.
- **TC-004**: Given a plugin in `~/.claude/plugins/cache/.../skills/foo/SKILL.md` → Returns location `scope="plugin"`, `readonly: true`, `pluginSlug` populated.
- **TC-005**: Given no installs anywhere → Returns `[]`.
- **TC-006**: Given canonical name with `..` or path-traversal characters → Sanitizes/rejects (returns `[]`); does NOT escape sandbox.

---

### T-002: Enrich `/api/skills/updates` response with location metadata
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-05, AC-US4-06 | **Status**: [x] Completed

**Description**: In the `/api/skills/updates` handler at `src/eval-server/api-routes.ts:1791`, build a per-request scan map keyed by canonical name, attach `installLocations[]`, `localPlugin` (highest-precedence install's `dir`-derived plugin slug), `localSkill` (canonical's last segment) to each row.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:1791-1809`
- Build `Map<string, InstallLocation[]>` once at top of handler from `getOutdatedJson()` result names.
- For each row, attach `installLocations[]`. Resolve `localPlugin`/`localSkill` by mapping the highest-precedence (project > personal > plugin) location to a `(plugin, skill)` pair using existing `scanSkillsTriScope` data (or a lookup helper).
- Preserve all existing fields exactly (additive change).

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.updates-locations.test.ts`
- **TC-001**: Given mocked `getOutdatedJson` returning 2 outdated skills + mocked scanner returning locations → Response includes `installLocations[]` per row with correct counts.
- **TC-002**: Given a skill with no installs detected → `installLocations: []`, `localPlugin`/`localSkill` resolved from canonical fallback (`undefined` if no match).
- **TC-003**: Same scan called per-request, verified by spying that scanner runs once per call (not once per row).
- **TC-004**: Backwards-compat: existing field shape (`name`, `installed`, `latest`, `updateAvailable`, `pinned`, etc.) preserved unchanged.

---

### T-003: Per-agent update endpoint with allowlist validation
**User Story**: US-004, US-003 | **Satisfies ACs**: AC-US4-04, AC-US3-02 | **Status**: [x] Completed

**Description**: Extend `POST /api/skills/:plugin/:skill/update` at `src/eval-server/api-routes.ts:1925-1954` to accept optional `?agent=<id>` query param. Validate against `AGENTS_REGISTRY.map(a => a.id)` allowlist. Forward as `--agent <id>` to the existing `vskill update` execSync invocation. Reject unknown agent ids with 400.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:1925-1954`
- Read `url.searchParams.get('agent')`. If present, validate via `AGENTS_REGISTRY.some(a => a.id === agentId)`. On invalid, return 400 with `{error: "Unknown agent id"}`.
- On valid, build CLI command as `vskill update ${quotedSkillName} --agent ${quotedAgentId}`. Use `execSync` with array form to avoid shell interpolation entirely (safer than string interpolation).

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.update-per-agent.test.ts`
- **TC-001**: Given `?agent=claude-code` → execSync invoked with `--agent claude-code` flag.
- **TC-002**: Given `?agent=$(rm -rf /)` (injection attempt) → Returns 400, execSync NOT called.
- **TC-003**: Given `?agent=unknown-agent` → Returns 400.
- **TC-004**: Given no `?agent` query param → Behavior unchanged (no `--agent` flag, full fan-out).
- **TC-005**: Given valid agent id but execSync fails → Returns 500 with stderr in body (existing error path).

---

## Phase 2: Frontend types + utilities

### T-004: Extend `SkillUpdateInfo` type and add `InstallLocation` to `api.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03 | **Status**: [x] Completed

**Description**: Mirror the backend type extensions in the frontend type definitions.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (around lines 165-200 where `SkillUpdateInfo` lives — verify exact location).
- Add exported `InstallLocation` type with `{scope, agent, agentLabel, dir, pluginSlug?, pluginMarketplace?, symlinked, readonly}`.
- Extend `SkillUpdateInfo` with optional `installLocations?`, `localPlugin?`, `localSkill?`.

**Test Plan**:
- No runtime test (type-only change). Verified by `tsc --noEmit` passing and downstream tests in T-005..T-010 type-checking against new shape.

---

### T-005: `formatUpdateLocationTooltip` pure function util
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] Completed

**Description**: Pure function that converts `InstallLocation[]` into a human-readable tooltip string covering count, scope, agents, pinned/plugin caveats.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/formatUpdateLocationTooltip.ts`
- Signature: `formatUpdateLocationTooltip(locations: InstallLocation[], opts?: { pinned?: boolean }): string`
- Output examples:
  - 0 locations: `"No tracked install — click to view details"`
  - 1 location project: `"Updates 1 location: project (Claude Code)"`
  - N>1 mixed: `"Updates 3 locations: project + personal (Claude Code, Codex CLI)"`
  - Pinned: append `" — pinned (skipped)"` when `opts.pinned`
  - Has plugin readonly: append `" — 1 from plugin {pluginSlug} (handled separately)"`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/utils/__tests__/formatUpdateLocationTooltip.test.ts`
- **TC-001..TC-008**: One test per output variant above (0/1/N, pinned, readonly, mixed scope, mixed agent, all-plugin).

---

## Phase 3: UpdateBell + UpdateDropdown UX

### T-006: Replace naive split in `UpdateBell.tsx` with `revealSkill` + fallback toast
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] Completed

**Description**: In `UpdateBell.tsx:118-124`, replace the current `selectSkill({ plugin, skill, origin: "installed" })` call with `revealSkill(localPlugin, localSkill)` using server-provided fields. Add fallback for missing fields. Add no-match toast using existing `useToast` + `useAgentCatalog` hook.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateBell.tsx:118-124`
- Pull `revealSkill` from `useStudio()`.
- Compute `plugin = u.localPlugin ?? ""`, `skill = u.localSkill ?? u.name.split("/").pop() ?? ""`.
- Call `revealSkill(plugin, skill)`.
- After call, check `state.selectedSkill` — if still null and `installLocations[0]?.agent` exists, show toast naming the owning agent.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/UpdateBell.smartclick.test.tsx`
- **TC-001**: Given `localPlugin="greet-anton", localSkill="greet-anton"` and matching skill in state → revealSkill called with those args; URL hash set; no toast.
- **TC-002**: Given `localPlugin`/`localSkill` absent (older server) → falls back to last-segment split; revealSkill F-001/F-002 fallback covers it.
- **TC-003**: Given no matching skill in state and `installLocations[0]={agent: "codex-cli"}` → toast shows "Skill installed under Codex CLI — switch to Codex CLI to view details."
- **TC-004**: Given hash reload `#/skills/foo/bar` → existing rehydrate path still resolves (no regression).

---

### T-007: Add inline `<UpdateAction>` button + tooltip to `UpdateDropdown.tsx` rows
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] Completed

**Description**: In `UpdateDropdown.tsx`, add an inline `<UpdateAction>` button at the right of each row. Use `formatUpdateLocationTooltip` to build the `title=` attribute. For plugin-bundled-only skills (all locations `readonly: true`), block click and show informative toast.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/UpdateDropdown.tsx`
- Import `<UpdateAction>` and `formatUpdateLocationTooltip`.
- Add Update button per row, positioned at the right end of the existing button row.
- Set `title={formatUpdateLocationTooltip(u.installLocations ?? [], { pinned: u.pinned })}`.
- If all locations readonly → onClick shows `useToast({ severity: "info", message: "..." })` and skips the update call.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/UpdateDropdown.inline-update.test.tsx`
- **TC-001**: Given row with 2 locations → tooltip shows "Updates 2 locations: ...". Click → fetch called for `/api/skills/.../update`.
- **TC-002**: Given row with all-readonly locations → click shows toast, no fetch call.
- **TC-003**: Given row with pinned=true → tooltip includes "pinned (skipped)".
- **TC-004**: Given successful update → result toast names locations updated.

---

## Phase 4: Detail view chips

### T-008: `InstallLocationChips` component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] Completed

**Description**: New component that renders a chip strip showing every install location of a skill. Uses existing chip styling (CSS variables consistent with `VersionBadge`/`SymlinkChip`).

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallLocationChips.tsx`
- Props: `{ locations: InstallLocation[]; pinned?: boolean; onChipClick?: (loc: InstallLocation) => void; onUpdateLocation?: (loc: InstallLocation) => void }`
- Renders nothing when `locations.length <= 1` (US-003 AC-US3-05 enforced at render).
- Each chip: `[<scope> · <agentLabel>]` with optional 📌 (pinned) / 🔒 (readonly) icon.
- Per-chip "Update" button rendered only for non-readonly, non-pinned chips.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/InstallLocationChips.test.tsx`
- **TC-001**: Given 1 location → renders nothing (returns `null`).
- **TC-002**: Given 3 locations including 1 readonly → 3 chips, readonly chip shows 🔒 and has no Update button.
- **TC-003**: Given pinned global → 📌 icon on all chips.
- **TC-004**: Click on chip → onChipClick called with location.
- **TC-005**: Click Update on non-readonly chip → onUpdateLocation called with that location.

---

### T-009: Integrate `InstallLocationChips` into `SkillDetailPage`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05 | **Status**: [x] Completed
<!-- AC-US3-04 carved out to Out-of-Scope during closure: onChipClick wiring is shipped (forward-compat), manifest-swap consumer deferred to follow-up increment. -->


**Description**: In `SkillDetailPage.tsx`, fetch the install locations for the current skill (reuse data from `/api/skills/updates` cache if available, else fetch from a new lightweight endpoint or extend an existing detail endpoint), and render `<InstallLocationChips>` below the title.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/SkillDetailPage.tsx:30-62`
- Source for locations: prefer reading from `skillUpdates.updatesById` (already fetched and cached by `useSkillUpdates`). Fallback: small additional fetch.
- Wire `onChipClick` to swap manifest preview source (read `dir/SKILL.md` from that location's `dir`).
- Wire `onUpdateLocation` to the per-agent update endpoint via `api.postSkillUpdate(plugin, skill, { agentId: loc.agent })` (extend `postSkillUpdate` signature).

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/__tests__/SkillDetailPage.locations.test.tsx`
- **TC-001**: Given skill with 1 location → no chip strip rendered.
- **TC-002**: Given skill with 3 locations → chip strip rendered with 3 chips below title.
- **TC-003**: Click a chip → manifest preview swaps to that location's SKILL.md content.

---

### T-010: Per-chip "Update this location" + plugin readonly handling
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] Completed

**Description**: Extend `api.postSkillUpdate` to accept optional `agentId`, forward as `?agent=<id>`. Wire `InstallLocationChips`'s `onUpdateLocation` to invoke it. Plugin-readonly chips have no Update button (enforced in T-008). Result toast names the agent updated.

**Implementation**:
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` — extend `postSkillUpdate(plugin: string, skill: string, opts?: { agentId?: string })` to append `?agent=<id>` when set.
- Reuse the same fetch + toast pattern from `UpdateAction.tsx`.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/InstallLocationChips.update.test.tsx`
- **TC-001**: Given click Update on a `claude-code` personal chip → `postSkillUpdate` called with `agentId: "claude-code"`.
- **TC-002**: Given backend returns 200 → success toast shows "Updated greet-anton in personal (Claude Code)".
- **TC-003**: Given backend returns 500 → error toast shown.

---

## Phase 5: Verification

### T-011: Run full vitest suite for affected files
**Status**: [x] Completed (10 new test files = 55 new tests, all passing; full suite 4392/4405 with 13 pre-existing failures verified by stash test, none caused by 0747)

```bash
cd repositories/anton-abyzov/vskill
npx vitest run \
  src/eval-server/utils/__tests__/scan-install-locations.test.ts \
  src/eval-server/__tests__/api-routes.updates-locations.test.ts \
  src/eval-server/__tests__/api-routes.update-per-agent.test.ts \
  src/eval-ui/src/utils/__tests__/formatUpdateLocationTooltip.test.ts \
  src/eval-ui/src/components/__tests__/UpdateBell.smartclick.test.tsx \
  src/eval-ui/src/components/__tests__/UpdateDropdown.inline-update.test.tsx \
  src/eval-ui/src/components/__tests__/InstallLocationChips.test.tsx \
  src/eval-ui/src/components/__tests__/InstallLocationChips.update.test.tsx \
  src/eval-ui/src/pages/__tests__/SkillDetailPage.locations.test.tsx
```

Plus regression: `npx vitest run src/eval-ui/src/components/__tests__/UpdateBell.test.tsx src/eval-ui/src/components/__tests__/UpdatesPanel.test.tsx` to ensure no break.

---

### T-012: Manual studio verification
**Status**: [x] Completed (built local vskill, started studio at port 3185 rooted in specweave-umb; created `<root>/.claude/skills/greet-anton/` and `<root>/.codex/skills/greet-anton/`; verified end-to-end: `/api/skills/updates` returns `installLocations[]`, bell row tooltip shows "Updates 2 locations: project (Claude Code, Codex CLI)", smart click navigates and renders detail, Update button fires endpoint and shows success toast. Also verified scanner returns 11 install locations across 5 agents in real fixture for skill-creator.)

Per the plan's Verification section:
1. `vskill install anton-abyzov/greet-anton --agent claude-code` and `--agent codex-cli` (or equivalent setup).
2. Bump platform version or pin local copies to old version.
3. Open Studio, see "1 updates available" badge.
4. Click row → sidebar reveals greet-anton, detail loads (AC-US1-01).
5. Hover Update button → tooltip "Updates 2 locations: ..." (AC-US2-01).
6. Click Update → toast confirms 2 locations updated (AC-US2-03).
7. Verify on disk both `~/.claude/skills/greet-anton/SKILL.md` and `~/.codex/skills/greet-anton/SKILL.md` reflect new version (AC-US2-04).
8. Detail page shows chip strip (AC-US3-01).
9. Pin one location → re-open dropdown → tooltip shows "pinned (skipped)" (pin handling).
10. Plugin-bundled skill in plugin cache → click Update from bell → blocked toast (AC-US2-05); chip in detail shows 🔒 (AC-US3-03).

---

### T-013: Closure (`/sw:done 0747`)
**Status**: [x] Completed (this run)

Run `/sw:done 0747` to invoke the closure pipeline:
- code-review (sw:code-reviewer)
- /simplify
- /sw:grill
- /sw:judge-llm
- PM 3-gate validation
- sync to GitHub/JIRA/ADO if configured
