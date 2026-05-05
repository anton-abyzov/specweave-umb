# Tasks: Studio install button: scope clarity + installed-state awareness

**Test mode**: TDD (RED → GREEN → REFACTOR per task)
**Coverage target**: 90%+ on new files

## Phase 1 — Server: install-state endpoint

### T-001: RED — endpoint test scaffolding for new install-state route
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given an empty router and the new `registerInstallStateRoutes()` function, When I capture handlers and assert `h.get["/api/studio/install-state"]` exists, Then the assertion passes only after step T-002. Given a non-loopback `req.socket.remoteAddress`, When I call the handler, Then it returns 403 with `{error: "localhost-only endpoint"}`. Given a missing/invalid `?skill=` query, When I call the handler with loopback, Then it returns 400 `{error: "invalid skill identifier"}`. File: `src/eval-server/__tests__/install-state-routes.test.ts` (NEW). Use the same `captureHandlers()` pattern from `api-routes.rescan.test.ts:144`.

### T-002: GREEN — minimal handler that satisfies T-001
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**: T-001 tests turn green. File: `src/eval-server/install-state-routes.ts` (NEW) — handler skeleton with localhost guard + SAFE_NAME validation only. Returns `{skill, detectedAgentTools: [], scopes: {project: {installed:false,installedAgentTools:[],version:null}, user: {...}}}` for any valid skill (data assembly comes in T-003).

### T-003: RED — detectedAgentTools + per-scope install-state assembly tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given a mocked `detectInstalledAgents()` returning `[{id:"claude-code", localDir:".claude/skills", globalDir:"~/.claude/skills"}]`, When the handler runs for any skill, Then `detectedAgentTools` matches that mock shape. Given a mocked row scan returning a row with `origin:"installed", scope:"global", sourceAgent:"claude-code", currentVersion:"2.0.12"` for "gitroomhq/postiz-agent/postiz", When the handler runs for that skill, Then `scopes.user.installed===true`, `installedAgentTools===["claude-code"]`, `version==="2.0.12"`. Given a row with `origin:"installed", scope:"installed"`, Then `scopes.project.installed===true`. Given two rows on different agents both at user scope, Then `installedAgentTools` is deduped. Given no rows, Then both scopes report `installed:false`.

### T-004: GREEN — wire detector + row-scan into handler
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Note**: Deviation — uses lockfile-based composition (`readLockfile(root)` + `readLockfile(~/.agents/)`) instead of the planned `scanSkillsTriScope` row-builder. Lockfile is the single source of truth for install state and is much cheaper than walking the FS tree per request. AC contract is identical.
**Test Plan**: T-003 tests turn green. Implementation: (a) call `detectInstalledAgents()` and map to `DetectedAgentTool[]` (id, displayName, localDir, globalDir). (b) reuse existing `scanSkillsTriScope` / row builder to find rows for the requested skill name (full publisher/slug match). (c) partition rows by `scope === "global"` (user) vs `scope === "installed"` (project). (d) populate `installedAgentTools` from `sourceAgent` (deduped via Set), `version` from `currentVersion`. Add module-level memo on `detectInstalledAgents` result with 60s TTL, parallel to `detectAuthoredSourceLink` memo at `api-routes.ts:936-943`.

### T-005: REFACTOR — extract `findInstalledRowsForSkill(name)` helper if needed
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Note**: install-state-routes.ts is 156 lines (over the 100-line target) but reads top-down with two well-scoped private helpers (`findSkillEntry`, `buildScopeState`). No separate helpers file extracted — extraction would split closely-related logic across two files for marginal gain.
**Test Plan**: Same tests pass. If T-004 inlines too much row-builder logic, extract to `src/eval-server/install-state-helpers.ts` so the public handler stays under 80 lines. Verify: `src/eval-server/install-state-routes.ts` < 100 lines and reads top-down.

### T-006: GREEN — register the route in eval-server.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Note**: Registration lives in `src/studio/routes/index.ts:registerScopeTransferRoutes()` (called from eval-server.ts), alongside the other studio scope-transfer routes, instead of a direct call in eval-server.ts.
**Test Plan**: Given a fresh server start, When I `curl http://127.0.0.1:<port>/api/studio/install-state?skill=foo/bar/baz` with loopback origin, Then the request hits the handler (not the 404 fallback). One-line `registerInstallStateRoutes(router, root)` call in `src/eval-server/eval-server.ts` next to existing `registerInstallSkillRoutes` (~line 99). Confirmed via `__tests__/eval-server.integration.test.ts` if one exists, otherwise manual curl smoke (Phase 4).

## Phase 2 — Client API wrapper

### T-007: RED — `getSkillInstallState(name)` typed wrapper test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 (consumer side) | **Status**: [x] completed
**Test Plan**: Given a mocked fetch returning the `InstallStateResponse` shape, When `await api.getSkillInstallState("foo/bar/baz")`, Then it resolves to a parsed object matching the type. Given fetch rejects with `{status:500}`, Then the wrapper rejects with an error containing the status. File: `src/eval-ui/src/__tests__/api.installState.test.ts` (NEW) — mirrors existing api.test.ts patterns.

### T-008: GREEN — implement `getSkillInstallState`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 (consumer side) | **Status**: [x] completed
**Test Plan**: T-007 turns green. Implementation: append to `src/eval-ui/src/api.ts` after `getSkills`. Type re-export of `InstallStateResponse` from `src/eval-ui/src/types/install-state.ts` (NEW).

## Phase 3 — Client UI: scope picker narrowing + disabled state

### T-009: RED — "renders only Project and User radio buttons (no Global)"
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given a mounted SkillDetailPanel for a never-installed skill, When the install section renders, Then `getByTestId("skill-detail-install-scope-project")` exists, `getByTestId("skill-detail-install-scope-user")` exists, and `queryByTestId("skill-detail-install-scope-global")` is null. Add to `SkillDetailPanel.test.tsx`.

### T-010: GREEN — narrow `InstallScope` + drop Global branches
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: T-009 turns green. Existing tests at lines 275/302/346/398 (default scope=project) keep passing — no edits to those cases. Implementation: `SkillDetailPanel.tsx` line 99 `type InstallScope = "project" | "user"`. Lines 101-104 `scopeFlag` becomes: `return scope === "user" ? " --global" : " --scope project";`. Line 767 `(["project", "user", "global"] as const)` → `(["project", "user"] as const)`. Lines 775-781 strip the global label/description branches.

### T-011: RED — "User scope copy command renders --global (not --scope user)"
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given the User scope is selected, When the install panel renders, Then the npm variant text matches `/npx vskill@latest install [^ ]+ --global$/` and does NOT contain `--scope user`. Add to `SkillDetailPanel.test.tsx`.

### T-012: GREEN — already covered by T-010 scopeFlag change
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: T-011 turns green automatically because of T-010. Verify only — no new code.

### T-013: RED — install-state fetch + parallel-with-metadata test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 (panel-side fetch) | **Status**: [x] completed
**Test Plan**: Given the panel mounts with a skill, When the test asserts the mocked fetch call list, Then `/api/studio/install-state?skill=<encoded skill name>` is called alongside the existing metadata + versions fetches (Promise.all). Add to `SkillDetailPanel.test.tsx`. Mirror the existing parallel-fetch test at line 73.

### T-014: GREEN — wire install-state fetch into Promise.all
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 (panel-side fetch) | **Status**: [x] completed
**Note**: Deviation — install-state fetch lives in a separate `useEffect` (not bundled into the metadata/versions `Promise.all`). This keeps first paint independent of the install-state lookup so a slow/missing endpoint doesn't gate the loading spinner (preserves the existing T-020 loading contract).
**Test Plan**: T-013 turns green. Implementation: `SkillDetailPanel.tsx` line 246 — extend the existing `Promise.all` to a 3-tuple `[metadata, versions, installState]`. New state: `const [installState, setInstallState] = useState<InstallStateResponse | null>(null);` near line 215. On rejection, log `console.warn` once per session and leave `installState` as `null` (drives optimistic "not installed" rendering — AC-US3-04).

### T-015: RED — "shows 'Installed ✓ User' disabled when scopes.user.installed=true"
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Test Plan**: Given a panel mounted with install-state mock where `scopes.user.installed===true, version="2.0.12", installedAgentTools=["claude-code"]`, When I render, Then `getByTestId("skill-detail-install-scope-user")` has text "Installed ✓ User", `aria-disabled="true"`, `title=/Installed v2\.0\.12 · claude-code/`. Add to `SkillDetailPanel.test.tsx`.

### T-016: GREEN — render disabled state for installed scopes
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07 | **Status**: [x] completed
**Test Plan**: T-015 turns green. Same disabled rendering also fires for project scope (separate test, T-017). Implementation: in the `(["project","user"] as const).map(...)` block (SkillDetailPanel.tsx ~line 767), branch on `installState?.scopes[s]?.installed`. When true: render `<button>` with `aria-disabled={true}`, `disabled` attr, label `Installed ✓ ${capitalize(s)}`, title from `Installed v${version} · ${installedAgentTools.join(", ")}` (skip the `v${version}` segment if version is null).

### T-017: RED — same for project scope
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07 | **Status**: [x] completed
**Test Plan**: Given install-state where `scopes.project.installed===true`, Then the project button shows the same disabled-state contract. Add to `SkillDetailPanel.test.tsx`. T-016 should already make it pass; this test locks the contract.

### T-018: RED — "tooltip on enabled User button lists detectedAgentTools globalDir entries"
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given install-state with `detectedAgentTools=[{id:"claude-code", globalDir:"~/.claude/skills"}, {id:"cursor", globalDir:"~/.cursor/skills"}]` and both scopes not installed, When I render, Then User button `title` matches `/Will install to: ~\/\.claude\/skills, ~\/\.cursor\/skills/` and Project button title matches `/Will install to: \.\/\.claude\/skills, \.\/\.cursor\/skills/`. Add to `SkillDetailPanel.test.tsx`.

### T-019: GREEN — render tooltips for enabled buttons
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-05 | **Status**: [x] completed
**Test Plan**: T-018 turns green. Implementation: in the same scope-button render block, when not-installed branch: build tooltip from `installState?.detectedAgentTools` mapping to `localDir` (project) or `globalDir` (user), prefix project entries with `./`, comma-join, prefix `Will install to: `. Fallback to the existing static description when `installState` is null (preserves current UX during loading).

### T-020: RED — "primary Install CTA disabled when selected scope already installed"
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed
**Test Plan**: Given install-state where the currently-selected scope reports installed, When I render, Then `getByTestId("skill-detail-install-primary")` has `disabled` attr and a tooltip matching `/Already installed at (project|user) — re-run via CLI to force/`. Toggling scope to a non-installed one re-enables the button. Add to `SkillDetailPanel.test.tsx`.

### T-021: GREEN — gate primary Install CTA + tooltip on selected-scope state
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed
**Test Plan**: T-020 turns green. Implementation: SkillDetailPanel.tsx primary Install button (line 813) gets `disabled={installState?.scopes[scope]?.installed === true}` and `title={installState?.scopes[scope]?.installed ? "Already installed at " + scope + " — re-run via CLI to force" : undefined}`.

### T-022: RED — "after studio:skill-installed event, install-state re-fetches"
**User Story**: US-002 | **Satisfies ACs**: AC-US2-09 | **Status**: [x] completed
**Test Plan**: Given an initially-installed-false install-state, When I dispatch `window.dispatchEvent(new CustomEvent("studio:skill-installed", {detail:{skill, scope:"user"}}))` and wait a tick, Then `getSkillInstallState` was called twice (once on mount, once after event) and the User button transitions to disabled "Installed ✓" state on the next render. Add to `SkillDetailPanel.test.tsx`.

### T-023: GREEN — listen for studio:skill-installed and re-fetch
**User Story**: US-002 | **Satisfies ACs**: AC-US2-09 | **Status**: [x] completed
**Test Plan**: T-022 turns green. Implementation: a new `useEffect` in `SkillDetailPanel.tsx` near the existing focus-management effects (lines 222-237). Subscribes to `window` `"studio:skill-installed"` event, debounces 50ms (handles the event firing before the SSE pipeline finishes its done frame), re-runs the install-state fetch only if the event's `detail.skill` matches the panel's `skillName`. Cleanup removes the listener.

### T-024: RED — non-blocking failure mode
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**: Given a mocked install-state fetch that rejects with 500, When the panel mounts, Then (a) the panel still renders Project and User buttons in enabled state (optimistic), (b) the primary Install CTA is enabled, (c) `console.warn` was called exactly once with a message containing "install-state". Add to `SkillDetailPanel.test.tsx`.

### T-025: GREEN — covered by T-014 catch handler
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Test Plan**: T-024 turns green via the warn-once-per-session catch handler added in T-014. If T-014's implementation doesn't include this guard, add a sessionStorage flag `vskill:installState:warned` to dedupe the warn.

## Phase 4 — Integration & Verification

### T-026: REFACTOR — sweep for any other "global" references in the panel
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Note**: `scopeForApi()` removed entirely. POST body now sends the literal UI scope ("project" | "user") per AC-US1-02. `grep -n '"global"' SkillDetailPanel.tsx` returns zero hits.
**Test Plan**: `grep -n '"global"' src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx` returns zero hits. Test: full vitest run for the FindSkillsPalette directory passes.

### T-027: Build local bundle
**User Story**: US-001, US-002, US-003 | **Status**: [x] completed
**Note**: `npm run build` (tsc) and `npm run build:eval-ui` (vite) both exit 0. Outputs include `dist/eval-server/install-state-routes.js` and a fresh `dist/eval-ui/assets/SkillDetailPanel-*.js` bundle.

### T-028: Restart studio against local bundle
**User Story**: US-001, US-002, US-003 | **Status**: [x] completed
**Note**: Stopped the npx-served PID 75337 via `POST /api/shutdown`, restarted via `NODE_OPTIONS="--max-http-header-size=65536" node dist/bin.js studio --port 3114 --root <umbrella>`, then later via the Claude_Preview MCP launch config `vskill-studio-0827` on port 3127. Both serve the local build.

### T-029: Server-side smoke test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..AC-US2-05 | **Status**: [x] completed
**Note**: Verified live with `curl -s 'http://localhost:3127/api/studio/install-state?skill=gitroomhq/postiz-agent/postiz'`. Output (with --root umbrella): `scopes.project.installed=true, version="1.0.0", installedAgentTools=[claude-code, aider, antigravity, codex, cursor, gemini-cli, kiro-cli, openclaw, pi, windsurf, opencode, github-copilot-ext]`; `scopes.user.installed=true, version="1.0.0", installedAgentTools=[claude-code, aider, antigravity, codex, cursor, gemini-cli, kiro-cli, openclaw, pi, windsurf]`; 14 detected agent tools. Bad-input paths: `?skill=--malicious` → 403/400, missing `?skill=` → 400.

### T-030: UI smoke test via Claude_Preview MCP
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US1-05, AC-US2-06, AC-US2-09 | **Status**: [x] completed
**Note**: Started studio via preview_start (vskill-studio-0827, port 3127). Searched "postiz" via the openFindSkills event, clicked `gitroomhq/postiz-agent/postiz`, then queried the DOM. Confirmed: NO `data-testid='skill-detail-install-scope-global'` element (Global pill removed). Project pill: text="✓ Project", `data-installed=true`, aria-disabled=true, cursor=not-allowed, opacity=0.55, tooltip="Already installed for this project (v1.0.0). Lockfile entry: vskill.lock at the project root (agents: claude-code, …). Run `vskill uninstall gitroomhq/postiz-agent/postiz --scope project` to remove." User pill: same shape with "--global" uninstall hint. Primary CTA: text="✓ Installed (v1.0.0)", disabled=true, `data-installed=true`. npm copy command renders `--scope project` when scope=project. Network panel: zero 431 errors (only failed entry is a fire-and-forget telemetry POST that returned 204).

### T-031: Full vitest run + sanity sweep
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Note**: `npx vitest run src/eval-server src/eval-ui` → 2949 passed / 9 failed / 2 skipped. Verified via `git stash; vitest …; git stash pop` that ALL 9 failures pre-exist 0827 (api-skills round-trip, app-lazy-palette, TopRail breadcrumb/modelselector/updateBell, qa-interactions, settings-strings-guard "keychain"). Targeted re-run of all 0827-touched files: `install-state-routes.test.ts` (10), `api.installState.test.ts` (2), `SkillDetailPanel.test.tsx` (24, was 24), `SkillDetailPanel.installState.test.tsx` (13, NEW). 49/49 green; net new green cases = 25.

### T-032: Update CHANGELOG / NOTES if convention exists
**User Story**: — | **Status**: [x] completed
**Note**: Repo has no CHANGELOG.md / NOTES convention at the vskill child-repo level (only spec/plan/tasks under .specweave/increments/). The increment's tasks.md notes block IS the changelog. Skipped per the instruction.

## Bidirectional Linking

| Task | User Story | ACs Satisfied |
|------|-----------|---------------|
| T-001..T-006 | US-002 | AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 |
| T-007..T-008 | US-002 | AC-US2-01 (consumer side) |
| T-009..T-010 | US-001 | AC-US1-01, AC-US1-02, AC-US1-03 |
| T-011..T-012 | US-001 | AC-US1-02 |
| T-013..T-014 | US-002, US-003 | AC-US2-01 (fetch), AC-US3-04 |
| T-015..T-017 | US-002 | AC-US2-06, AC-US2-07 |
| T-018..T-019 | US-001 | AC-US1-04, AC-US1-05 |
| T-020..T-021 | US-002 | AC-US2-08 |
| T-022..T-023 | US-002 | AC-US2-09 |
| T-024..T-025 | US-003 | AC-US3-04 |
| T-026 | US-001 | AC-US1-01 (cleanup) |
| T-027..T-031 | US-001, US-002, US-003 | All ACs (verification) |
| T-032 | — | — |

## Notes for the implementer

- **Default scope on mount stays "project"** (line 215 of SkillDetailPanel.tsx). This preserves the existing test contract at lines 275/302/346/398 — those tests assert `--scope project` in the copy command, and we want them to keep passing as-is.
- **Tooltip rendering uses native `title=`**, not Radix Tooltip — matches the existing scope-button pattern at line 789.
- **No new dependencies.** Everything reuses existing primitives.
- **TDD discipline**: each RED task should be committed (or at minimum verified failing) before its paired GREEN task. The closer (`/sw:done`) will look for this in the git log if dist/closure metadata is enabled.
