# Tasks: 0698-studio-multiproject-anthropic-scopes

**TDD enforcement**: RED → GREEN → REFACTOR. Every task must have failing tests BEFORE implementation.
**Stack**: Vitest 3 (unit/integration), Playwright (E2E), @testing-library/react (UI components).

---

### T-001: Scope union + group/source derivation + API wire normalizer
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-05, AC-US3-06 | **Status**: [x]
**Test Plan**:
- Given legacy scope `"own"` arrives from server → When normalizeSkillScope runs → Then returns `"authoring-project"`
- Given legacy scope `"installed"` arrives from server → When normalizeSkillScope runs → Then returns `"available-project"`
- Given legacy scope `"global"` arrives from server → When normalizeSkillScope runs → Then returns `"available-personal"`
- Given new scope `"available-plugin"` arrives from server → When normalizeSkillScope runs → Then returns `"available-plugin"` unchanged
- Given scope `"available-project"` → When group/source derived → Then group=`"available"`, source=`"project"`
- Given `SkillScope` union is imported → When code references `"enterprise"` → Then TypeScript compile error
- Given SkillInfo with scope `"authoring-plugin"` → When group/source accessed → Then group=`"authoring"`, source=`"plugin"`
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts`, `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/api-provenance.test.ts`
**Effort**: 3h

---

### T-002: Scanner refactor — emit 5-scope strings + precedence within AVAILABLE
**User Story**: US-003, US-007 | **AC**: AC-US3-01, AC-US3-02, AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [x]
**Test Plan**:
- Given project-root skill exists → When scanAvailableSkills runs → Then emits scope=`"available-project"`, group=`"available"`, source=`"project"`, precedenceRank=2
- Given personal skill exists → When scanAvailableSkills runs → Then emits scope=`"available-personal"`, group=`"available"`, source=`"personal"`, precedenceRank=1
- Given same skill name in both project + personal → When precedence pass runs → Then project entry gets shadowedBy=`"available-personal"`, personal entry shadowedBy=null
- Given available-plugin skill with same name as project skill → When precedence pass runs → Then plugin entry precedenceRank=-1, never gets shadowedBy
- Given AUTHORING skill with same name as AVAILABLE skill → When scanAvailableSkills runs → Then AUTHORING row has no shadowedBy
- Given old `scanSkillsTriScope` called → When compat re-export used → Then returns translated scope values (deprecated path still works for 0688 overlap)
**Files**: `repositories/anton-abyzov/vskill/src/eval/skill-scanner.ts`, `repositories/anton-abyzov/vskill/src/eval/__tests__/api-skills-scope.test.ts`
**Effort**: 4h

---

### T-003: Standalone authoring scanner
**User Story**: US-006 | **AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05 | **Status**: [x]
**Test Plan**:
- Given `<root>/skills/my-skill/SKILL.md` exists with no plugin manifest ancestor → When scanStandaloneSkills runs → Then emits SkillInfo with scope=`"authoring-project"`
- Given `<root>/my-plugin/.claude-plugin/plugin.json` exists AND `<root>/my-plugin/skills/foo/SKILL.md` exists → When scanStandaloneSkills runs → Then `foo` is NOT returned (plugin-source ancestor detected)
- Given `<root>/skills/` directory is empty → When scanStandaloneSkills runs → Then returns `[]` without error
- Given activeAgent=`"cursor"` → When scanStandaloneSkills runs → Then still returns skills (cross-agent behavior)
- Given `<root>/skills/deep/nested/SKILL.md` (non-standard path) → When scanStandaloneSkills runs → Then only top-level `<root>/skills/<name>/SKILL.md` is picked up, nested is not
**Files**: `repositories/anton-abyzov/vskill/src/eval/standalone-skill-scanner.ts`, `repositories/anton-abyzov/vskill/src/eval/__tests__/standalone-skill-scanner.test.ts`, `repositories/anton-abyzov/vskill/src/eval/__fixtures__/authoring-project/`
**Effort**: 3h

---

### T-004: Installed plugins scanner (CC)
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x]
**Test Plan**:
- Given fixture `plugin-cache/specweave/sw/1.0.0/skills/increment/SKILL.md` → When scanInstalledPluginSkills runs with agentId=`"claude-code"` → Then emits SkillInfo with scope=`"available-plugin"`, pluginName=`"sw"`, pluginMarketplace=`"specweave"`, pluginVersion=`"1.0.0"`, pluginNamespace=`"sw:increment"`, precedenceRank=-1
- Given agentId=`"cursor"` → When scanInstalledPluginSkills runs → Then returns `[]`
- Given plugin has two versions `1.0.0` and `1.1.0` in cache → When scanner runs → Then only emits skills from `1.1.0` (highest semver wins)
- Given fixture with 2 marketplaces × 2 plugins × multiple skills → When scanner runs → Then correctly groups by plugin name and marketplace
- Given `~/.claude/plugins/cache/` directory does not exist → When scanInstalledPluginSkills runs → Then returns `[]` without throwing
- Given plugin manifest `plugin.json` absent in version dir → When scanner runs → Then skills still emitted with available metadata
**Files**: `repositories/anton-abyzov/vskill/src/eval/plugin-scanner.ts`, `repositories/anton-abyzov/vskill/src/eval/__tests__/plugin-scanner.test.ts`, `repositories/anton-abyzov/vskill/src/eval/__fixtures__/plugin-cache/`
**Effort**: 4h

---

### T-005: Authored plugins scanner (CC)
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [x]
**Test Plan**:
- Given `<root>/my-plugin/.claude-plugin/plugin.json` + `<root>/my-plugin/skills/greeter/SKILL.md` → When scanAuthoredPluginSkills runs with agentId=`"claude-code"` → Then emits SkillInfo with scope=`"authoring-plugin"`, pluginName=`"my-plugin"`, pluginManifestPath=`<abs-path-to-plugin.json>`
- Given agentId=`"cursor"` → When scanAuthoredPluginSkills runs → Then returns `[]`
- Given `<root>/node_modules/vendored-plugin/.claude-plugin/plugin.json` → When scanner runs → Then this manifest is excluded
- Given `<root>` project has plugin at depth 5+ → When scanner runs (default depth 4) → Then plugin at depth 5 is NOT picked up
- Given plugin source has no `skills/` sibling dir → When scanner runs → Then no skills emitted for that manifest (no error)
- Given fixture project with 1 standalone skill + 1 plugin source → When scanAuthoredPluginSkills runs → Then only plugin skills emitted; standalone not double-counted
**Files**: `repositories/anton-abyzov/vskill/src/eval/plugin-scanner.ts`, `repositories/anton-abyzov/vskill/src/eval/__tests__/plugin-scanner.test.ts`, `repositories/anton-abyzov/vskill/src/eval/__fixtures__/authoring-project/`
**Effort**: 4h

---

### T-006: localStorage scope-rename migration shim
**User Story**: US-003 | **AC**: AC-US3-04 | **Status**: [x]
**Test Plan**:
- Given localStorage has `vskill-sidebar-claude-code-own-collapsed=true` → When runScopeRenameMigration runs → Then key renamed to `vskill-sidebar-claude-code-authoring-project-collapsed=true`, old key removed
- Given localStorage has `vskill-sidebar-cursor-installed-collapsed=false` → When runScopeRenameMigration runs → Then renamed to `vskill-sidebar-cursor-available-project-collapsed=false`
- Given localStorage has `vskill-sidebar-claude-code-global-collapsed=true` → When runScopeRenameMigration runs → Then renamed to `vskill-sidebar-claude-code-available-personal-collapsed=true`
- Given migration flag `vskill.migrations.scope-rename.v1=done` already set → When runScopeRenameMigration runs again → Then no keys are touched (idempotent)
- Given no legacy keys present → When runScopeRenameMigration runs → Then flag is set to `"done"`, no errors
- Given migration called from `main.tsx` before `createRoot()` → When app mounts → Then all legacy collapse-state is preserved under new keys
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/lib/scope-migration.ts`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/scope-migration.test.ts`, `repositories/anton-abyzov/vskill/src/eval-ui/src/main.tsx`
**Effort**: 2h

---

### T-007: UI scope rename ripple + strings.ts labels
**User Story**: US-003 | **AC**: AC-US3-03, AC-US3-06 | **Status**: [x]
**Test Plan**:
- Given `strings.ts` imported → When label for `"available"` scope read → Then returns `"Available"` (not `"Installed"`, `"Own"`, or `"Global"`)
- Given all scope labels in `strings.ts` → When enumerated → Then no occurrences of `"Own"`, `"Installed"`, `"Global"`, `"Enterprise"`, `"Drafts"` exist in exports
- Given Sidebar.tsx rendered with new scopes → When snapshot taken → Then no legacy scope strings appear in rendered output
- Given ScopeSection.tsx scope prop typed → When `"enterprise"` passed → Then TypeScript compile error
- Given strings.ts scope labels → When checking user-visible strings → Then exactly: `"Available"`, `"Authoring"`, `"Project"`, `"Personal"`, `"Plugins"`, `"Skills"`
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/strings.ts`, `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ScopeSection.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/Sidebar.allScopes.test.tsx`
**Effort**: 3h

---

### T-008: GroupHeader component
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x]
**Test Plan**:
- Given `<GroupHeader name="AVAILABLE" count={47} />` rendered → When snapshot taken → Then shows small-caps `"AVAILABLE"` text and `(47)` count
- Given count=0 → When GroupHeader rendered → Then `(0)` is displayed (not hidden)
- Given GroupHeader rendered → When clicked → Then nothing collapses (non-collapsible)
- Given GroupHeader with count → When snapshot taken → Then output matches stored snapshot (regression guard)
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/GroupHeader.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/GroupHeader.test.tsx`
**Effort**: 2h

---

### T-009: Two-tier Sidebar layout
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06, AC-US2-07 | **Status**: [x]
**Test Plan**:
- Given agent=`"claude-code"` and skills from all 5 scopes → When Sidebar renders → Then AVAILABLE umbrella has 3 sub-sections (Project, Personal, Plugins), AUTHORING umbrella has 2 sub-sections (Skills, Plugins)
- Given agent=`"cursor"` → When Sidebar renders → Then AVAILABLE has only Project + Personal (no Plugins), AUTHORING has only Skills (no Plugins)
- Given sub-sections with 0 skills → When Sidebar renders → Then each still renders with `(0)` count visible
- Given collapse state toggled for `available-project` scope → When key set in localStorage → Then key matches pattern `vskill-sidebar-<agentId>-available-project-collapsed`
- Given Sidebar rendered with CC agent → When snapshot taken → Then output matches stored CC-agent snapshot
- Given Sidebar rendered with Cursor agent → When snapshot taken → Then output matches stored non-CC snapshot (Plugins sub-sections absent)
- Given AVAILABLE > Plugins sub-section → When skills exist → Then Plugins sub-section is rendered only when agentIsCC
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/Sidebar.layout.test.tsx`
**Effort**: 5h

---

### T-010: PluginGroup nested tree refactor
**User Story**: US-002, US-004, US-005 | **AC**: AC-US2-05, AC-US4-03, AC-US4-04, AC-US5-04 | **Status**: [x]
**Test Plan**:
- Given skills from two plugins `sw` and `anthropic-skills` → When PluginGroup renders → Then each plugin name appears as a collapsible parent row with member skills nested inside
- Given plugin row collapsed → When collapse toggled → Then member skills hidden
- Given skill with pluginNamespace=`"anthropic-skills:pdf"` → When rendered inside PluginGroup → Then `"anthropic-skills:pdf"` displays in `font-mono`
- Given PluginGroup used in AVAILABLE > Plugins section → When rendered → Then visual treatment matches AUTHORING > Plugins section (shared component)
- Given PluginGroup snapshot taken for AVAILABLE context → When snapshot compared → Then matches stored snapshot
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/PluginGroup.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/PluginGroup.test.tsx`
**Effort**: 3h

---

### T-011: WorkspaceStore server module
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03, AC-US1-04, AC-US1-06, AC-US1-07 | **Status**: [x]
**Test Plan**:
- Given `~/.vskill/workspace.json` does not exist → When loadWorkspace called → Then returns `{ version: 1, activeProjectId: null, projects: [] }`
- Given valid `workspace.json` on disk → When loadWorkspace called → Then returns parsed WorkspaceConfig with staleProjectIds for paths that no longer existsSync
- Given corrupt JSON in workspace.json (`{`) → When loadWorkspace called → Then returns empty workspace, does not throw, does not delete the file
- Given addProject called with valid absolute path → When workspace saved → Then new ProjectConfig has id=sha1(path).slice(0,12), colorDot starts with `"oklch("`, atomically written via tmp+rename
- Given addProject called with same path twice → When second call made → Then rejects with conflict returning existing id
- Given addProject called with non-absolute or non-directory path → When call made → Then rejects with `"invalid-path"` error
- Given removeProject called on active project id → When workspace saved → Then activeProjectId set to null
- Given setActive called with stale path (existsSync=false) → When call made → Then rejects with `"stale-path"` error
- Given `EvalServerOptions.root` passed with empty workspace → When loadWorkspace + auto-seed called → Then workspace now has one project seeded from root, set as active
**Files**: `repositories/anton-abyzov/vskill/src/eval-server/workspace-store.ts`, `repositories/anton-abyzov/vskill/src/eval-server/__tests__/workspace-store.test.ts`, `repositories/anton-abyzov/vskill/src/eval-server/__tests__/fixtures/workspace/`
**Effort**: 4h

---

### T-012: Workspace REST endpoints
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06 | **Status**: [x]
**Test Plan**:
- Given `GET /api/workspace` with populated workspace → When request made → Then returns `{ workspace, activeProject, staleProjectIds }`
- Given `GET /api/workspace` with empty workspace and no `--root` → When request made → Then returns zero-project empty state (no 4xx)
- Given `POST /api/workspace/projects` with valid `{ path, name }` → When request made → Then returns 201 with `{ project, workspace }`, path validated
- Given `POST /api/workspace/projects` with relative path → When request made → Then returns 400 `{ error: "invalid-path" }`
- Given `POST /api/workspace/projects` with already-registered path → When request made → Then returns 409 `{ error: "already-registered", existingId }`
- Given `DELETE /api/workspace/projects/:id` with valid id → When request made → Then returns 200 with updated workspace
- Given `DELETE /api/workspace/projects/:id` with unknown id → When request made → Then returns 404 `{ error: "not-found", id }`
- Given `POST /api/workspace/active` with valid id → When request made → Then returns 200, updates `lastActiveAt`
- Given `POST /api/workspace/active` with stale path id → When request made → Then returns 400 `{ error: "stale-path" }`
- Given route that needs active root but no project is active → When request made → Then returns 409 `{ error: "no-active-project" }`
**Files**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts`, `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-workspace.test.ts`
**Effort**: 3h

---

### T-013: Optional root derivation + CLI `--root` fallback
**User Story**: US-001 | **AC**: AC-US1-07 | **Status**: [x]
**Test Plan**:
- Given server boots with `--root ./foo` and workspace.json absent → When first request arrives → Then workspace auto-seeded with `foo` as active project, GET /api/workspace returns it
- Given server boots with `--root ./foo` and workspace already has projects → When server starts → Then `--root` is ignored (workspace is source of truth), warning logged
- Given server boots with no `--root` and empty workspace → When `GET /api/skills` requested → Then returns 409 `{ error: "no-active-project" }`
- Given EvalServerOptions.root is now optional (TypeScript type) → When compile → Then no type errors in server bootstrap code
**Files**: `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts`, `repositories/anton-abyzov/vskill/src/eval-server/__tests__/eval-server-root.test.ts`
**Effort**: 3h

---

### T-014: useWorkspace hook
**User Story**: US-001 | **AC**: AC-US1-03, AC-US1-04, AC-US1-06 | **Status**: [x]
**Test Plan**:
- Given GET /api/workspace returns populated response → When useWorkspace hook used → Then `workspace`, `activeProject`, and `staleProjectIds` are accessible
- Given setActive(id) called → When hook runs → Then POSTs to `/api/workspace/active`, then mutates `"workspace"`, `"skills"`, `"agents"` SWR keys
- Given addProject(path) called → When hook runs → Then POSTs to `/api/workspace/projects`, then mutates `"workspace"`
- Given removeProject(id) called → When hook runs → Then DELETEs `/api/workspace/projects/:id`, then mutates `"workspace"` and `"skills"`
- Given loading state → When hook first renders → Then loading=true until response arrives
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useWorkspace.ts`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/useWorkspace.test.tsx`
**Effort**: 3h

---

### T-015: ProjectPicker component + ProjectCommandPalette (⌘P)
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x]
**Test Plan**:
- Given workspace with 2 projects → When ProjectPicker rendered → Then pill shows active project name; clicking opens popover listing both projects with name, path (monospace), and OKLCH color dot
- Given project with stale path → When rendered in popover → Then row is muted, "Remove" affordance visible, row is NOT selectable as active
- Given "Add project" button clicked → When `showDirectoryPicker()` supported → Then directory picker invoked; when NOT supported → Then text-input fallback shown
- Given project row clicked → When setActive called → Then active project switches, SWR cache mutated
- Given project "Remove" button clicked → When removeProject called → Then project removed; if it was active, empty state prompt shown
- Given ProjectCommandPalette opened via ⌘P (focus inside Studio) → When user types → Then fuzzy-filtered list of projects shows; Enter switches active project
- Given ⌘P pressed while focus is OUTSIDE Studio DOM subtree → When key event fires → Then browser Print dialog NOT suppressed (no preventDefault)
- Given ProjectCommandPalette open → When arrow keys pressed → Then selection navigates up/down through filtered list
- Given OKLCH color dot → When computed from same path twice → Then identical color value returned (deterministic hash)
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ProjectPicker.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ProjectCommandPalette.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ProjectPicker.test.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ProjectCommandPalette.test.tsx`
**Effort**: 6h

---

### T-016: StatusBar trim + ProjectPicker mount in StudioLayout
**User Story**: US-008 | **AC**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x]
**Test Plan**:
- Given `StatusBar.tsx` rendered → When snapshot taken → Then no project-path text appears in output
- Given `StudioLayout.tsx` rendered → When snapshot taken → Then `ProjectPicker` is rendered in top-left position, appears exactly once
- Given StatusBar snapshot → When compared to stored snapshot → Then absence of footer path element is asserted explicitly (not incidental)
- Given StudioLayout snapshot → When compared to stored snapshot → Then ProjectPicker is present in header region
**Files**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StatusBar.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StudioLayout.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/StatusBar.test.tsx`, `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/StudioLayout.test.tsx`
**Effort**: 2h

---

### T-017: E2E project switching + docs
**User Story**: US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05, AC-US2-02, AC-US2-03, AC-US2-07, AC-US4-02, AC-US5-03 | **Status**: [x]
**Test Plan**:
- Given two projects with different skill sets → When user switches via ProjectPicker → Then Sidebar repopulates from new project with no cross-contamination between projects
- Given agent=`"claude-code"` + plugins installed in fixture cache → When Skill Studio loads → Then AVAILABLE > Plugins section renders with plugin tree
- Given agent=`"cursor"` → When Skill Studio loads → Then AVAILABLE > Plugins and AUTHORING > Plugins sections are absent
- Given ⌘P keyboard shortcut → When pressed with focus inside Studio → Then ProjectCommandPalette opens with fuzzy filter functional
- Given localStorage with legacy `vskill-sidebar-claude-code-own-collapsed=true` → When app loads fresh tab → Then key renamed to `vskill-sidebar-claude-code-authoring-project-collapsed=true`, migration flag set
- Given fresh install (no `--root`, empty workspace) → When Studio opens → Then empty state "Add project" CTA is shown; after adding a project skills load correctly
- Given project switch → When Sidebar re-renders → Then repopulation completes in under 1 second (performance budget check via Playwright timing)
- Given corrupt workspace.json → When server boots → Then empty workspace returned, file preserved on disk (not deleted)
- Given ADRs reference in plan.md (0698-01, 0698-02, 0698-03) → When docs checked → Then ADR files exist in `.specweave/docs/internal/architecture/adr/`
**Files**: `repositories/anton-abyzov/vskill/e2e/project-switching.spec.ts`, `repositories/anton-abyzov/vskill/e2e/scope-taxonomy.spec.ts`, `repositories/anton-abyzov/vskill/e2e/cmd-palette.spec.ts`, `.specweave/docs/internal/architecture/adr/0698-01-skillscope-five-value-union.md`, `.specweave/docs/internal/architecture/adr/0698-02-workspace-json-user-global.md`, `.specweave/docs/internal/architecture/adr/0698-03-plugin-cache-version-segment.md`
**Effort**: 4h
