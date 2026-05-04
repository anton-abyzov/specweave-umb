# Tasks: 0823 — Studio installed-skill read-only Source view + comprehensive origin resolver + rescan endpoint

**TDD discipline mandatory**: each implementation task is paired with a RED test task that must fail before the GREEN task lands. Refactor opportunistically.

---

## Phase 1 — Backend foundation: Origin Resolver

### T-001: Origin resolver — RED tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-10 | **Status**: [x] completed
**Test Plan**: Given a temp project root with a known `vskill.lock` at cwd containing `nanobanana → github:foo/nanobanana-skill` AND a `~/.agents/vskill.lock` containing the same entry mapped differently, When `resolveSkillOrigin("nanobanana", ".claude", root)` runs, Then the project lockfile entry wins (precedence). Cover all 5 tiers with separate cases. Use temp dirs for isolation.

### T-002: Origin resolver — GREEN implementation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-10 | **Status**: [x] completed
**Test Plan**: T-001 tests pass. Implement `src/eval-server/origin-resolver.ts` with `resolveSkillOrigin(skill, plugin, root)` walking the five-tier chain. Include `ANTHROPIC_SKILL_REGISTRY` const map.

### T-003: skill-name-resolver delegation — RED test [DESCOPED]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: ORIGINALLY: tests for skill-name-resolver delegating to origin-resolver. DESCOPED during implementation (see spec.md AC-US2-03): the legacy `resolveSkillApiName` is left untouched (its 35 existing tests still pass) and the NEW callsites in `/versions`, `/versions/diff`, `/rescan` consult `resolveSkillOrigin` directly with a legacy fallback. The buildSkillApiPath helper in api-routes.ts (added per code-review F-001 iteration 2) centralizes the call pattern.

### T-004: skill-name-resolver delegation — GREEN [DESCOPED]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: ORIGINALLY: refactor `skill-name-resolver.ts` to call `resolveSkillOrigin()`. DESCOPED — see T-003. The api-routes.ts callsites use the new resolver; existing tests for skill-name-resolver remain green without modification.

---

## Phase 2 — Backend: /versions envelope + Rescan endpoint

### T-005: /versions envelope adds trackedForUpdates + provider — RED
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Test Plan**: Given an HTTP request to `/api/skills/.claude/nanobanana/versions`, When the response is a registered skill with platform versions, Then envelope contains `trackedForUpdates: true` AND `provider: "vskill"` AND original `versions/count/source` fields are unchanged.

### T-006: /versions envelope — GREEN
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Test Plan**: T-005 passes. Extract `fetchUpstreamVersions(skill, plugin, root)` helper. Extend envelope in api-routes.ts.

### T-007: Rescan endpoint — RED tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given POST `/api/v1/skills/.claude%2Fnanobanana/rescan` with valid slug, Then returns 200 with `{jobId: <uuid>}`. Given POST with `--malicious` slug, Then returns 400. Given two concurrent POSTs, Then each returns its own jobId. Mock `fetch` to verified-skill.com.

### T-008: Rescan endpoint — GREEN
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-06 | **Status**: [x] completed
**Test Plan**: T-007 passes. Add route after the SSE update route in api-routes.ts. Reuse `isSafeSkillName`, `resolveSkillOrigin`, `fetchUpstreamVersions`.

### T-009: Rescan SSE bridge — RED
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-05, AC-US3-07 | **Status**: [x] completed
**Test Plan**: Given a subscriber attached to dataEventBus listening for `skill.updated`, When rescan completes successfully, Then the bus emits an event with `{plugin, skill, versions}` payload. When rescan called on a no-upstream skill, Then bus still emits with `versions: []`.

### T-010: Rescan SSE bridge — GREEN
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-05, AC-US3-07 | **Status**: [x] completed
**Test Plan**: T-009 passes. Confirm `skill.updated` is in `DataEventType` union (add if missing). Verify the bus reaches the SSE stream consumed by `useSkillUpdates`. If `platform-proxy.ts:248` bypasses the bus, unify both paths.

---

## Phase 3 — Frontend: Source tab UI (BIGGEST piece)

### T-011: api.ts client methods — RED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given mocked `/api/skills/:plugin/:skill/files` and `/file?path=...`, When `api.listSkillFiles(plugin, skill)` and `api.getSkillFile(plugin, skill, path)` are called, Then they parse responses correctly and surface errors via thrown `Error`.

### T-012: api.ts client methods — GREEN
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: T-011 passes. Add the two methods to `src/eval-ui/src/api.ts`.

### T-013: SourceFileTree — RED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-07 | **Status**: [x] completed
**Test Plan**: Given `files=[SKILL.md, references/foo.md, scripts/bar.sh]`, When tree renders, Then the user sees a collapsible folder structure. When user presses ArrowDown twice and Enter, Then `onSelect` fires with the third visible item. When user presses Escape, Then focus moves to the parent tab bar.

### T-014: SourceFileTree — GREEN
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-07 | **Status**: [x] completed
**Test Plan**: T-013 passes. Implement `src/eval-ui/src/components/SourceFileTree.tsx`.

### T-015: TextFileViewer + ImageFileViewer + BinaryFilePlaceholder — RED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given a code file content, Then TextFileViewer renders `<pre>` with monospace font and line numbers. Given an image, Then ImageFileViewer renders `<img>` with the correct src. Given binary, Then BinaryFilePlaceholder shows `Binary file — N KB`.

### T-016: TextFileViewer + ImageFileViewer + BinaryFilePlaceholder — GREEN
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: T-015 passes. Three small components in `src/eval-ui/src/components/`.

### T-017: SourcePanel — RED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-08 | **Status**: [x] completed
**Test Plan**: Given mounted `<SourcePanel plugin=".claude" skill="slack-messaging" />`, Then it fetches files, default-selects SKILL.md, and renders SkillContentViewer with the markdown. When user clicks `references/foo.md`, Then the viewer switches to that file rendered as markdown. When user clicks a binary, Then placeholder shows.

### T-018: SourcePanel — GREEN
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-08 | **Status**: [x] completed
**Test Plan**: T-017 passes. Implement `src/eval-ui/src/components/SourcePanel.tsx`.

### T-019: RightPanel Source tab registration — RED
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test Plan**: Given a read-only persona viewing `slack-messaging`, Then the tab bar shows Overview, Source, Tests, Run, History (no Edit). Source comes BEFORE Edit in the descriptor list. Default landing tab for read-only is Source. Default landing tab for author is Overview.

### T-020: RightPanel Source tab registration — GREEN
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test Plan**: T-019 passes. Modify `RightPanel.tsx`: add `source` to `DetailTab`, `ALL_TABS`, `LEGACY_REDIRECTS`, `TAB_DESCRIPTORS` (before `edit`). Mount `<SourcePanel />` in the panel switch. Update `applyPersonaRedirect` for read-only default.

---

## Phase 4 — Frontend: Versions UX clarity + Provider chip

### T-021: ProviderChip — RED
**User Story**: US-002 | **Satisfies ACs**: AC-US2-09 | **Status**: [x] completed
**Test Plan**: Given `<ProviderChip provider="anthropic" />`, Then it renders an "Anthropic" pill with the orange variant. Given "vskill", Then light-blue. Given "local", Then gray.

### T-022: ProviderChip — GREEN
**User Story**: US-002 | **Satisfies ACs**: AC-US2-09 | **Status**: [x] completed
**Test Plan**: T-021 passes. Implement `src/eval-ui/src/components/ProviderChip.tsx`.

### T-023: VersionHistoryPanel UX swap + chip + CheckNow gate — RED
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-07, AC-US2-08, AC-US2-09 | **Status**: [x] completed
**Test Plan**: Given envelope `{source:"none", provider:"local", trackedForUpdates:false}`, When VersionHistoryPanel renders, Then the message reads "No upstream registry — this skill ships without origin metadata, so update tracking is unavailable" AND the CheckNowButton is NOT rendered. Given envelope `{source:"platform", provider:"vskill", trackedForUpdates:true}`, Then versions render with a vskill chip on each row AND CheckNowButton renders. Given envelope with `provider:"anthropic"`, Then chip reads "Anthropic".

### T-024: VersionHistoryPanel UX swap + chip + CheckNow gate — GREEN
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-07, AC-US2-08, AC-US2-09 | **Status**: [x] completed
**Test Plan**: T-023 passes. Modify `VersionHistoryPanel.tsx`.

---

## Phase 5 — E2E + Browser verification

### T-025: Playwright source-tab.spec.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Open Studio → navigate to `#/skills/project/.claude/slack-messaging` → click Source tab → assert SKILL.md body visible AND folder tree present → click a file in the tree → assert content updates.

### T-026: Playwright check-now.spec.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Navigate to a tracked skill (`nanobanana`) → click Versions tab → assert CheckNowButton visible → click it → wait for POST `/rescan` to return 200 (network listener) → assert spinner clears within 30s.

### T-027: Playwright version-tracking.spec.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-07, AC-US2-09 | **Status**: [x] completed
**Test Plan**: For each of (nanobanana = vskill, slack-messaging = anthropic, fake-local-only = local): navigate to its Versions tab, assert provider chip text + envelope-driven message + CheckNow visibility.

### T-028: Build vskill UI bundle + start local studio
**User Story**: US-001/002/003 | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: `npm run build` completes without errors. `node dist/cli/cli.js studio --port 3157` starts cleanly and serves the new bundle.

### T-029: Browser verification with Claude Preview MCP — 8-step flow + screenshots
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: Execute the 8-step flow from plan.md verification section. Capture screenshots at steps 4, 5, 6, 8.

---

## Phase 6 — Closure

### T-030: Sync living docs
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: `specweave sync-living-docs 0823-studio-installed-skill-readonly-and-rescan` exits 0; new spec entries appear under `.specweave/docs/internal/specs/`.

### T-031: Run /sw:done — quality gates + closure
**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed
**Test Plan**: `/sw:done 0823` runs code-review, simplify, grill, judge-llm. All gates clean. Increment metadata.json status flips to `complete`.
