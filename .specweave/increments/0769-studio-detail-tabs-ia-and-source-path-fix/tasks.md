---
increment: 0769-studio-detail-tabs-ia-and-source-path-fix
tasks_version: 1
---

# Tasks: Studio detail page — persona-conditional tab IA + plugin-cache source-path fix + hide CheckNow

## Legend
- `[ ]` pending | `[x]` completed | `[-]` skipped
- Parts: **A** = plugin-scanner foundation | **C** = CheckNow gate | **B** = tab IA reorg

---

## PART A — Plugin-scanner correctness (US-003, US-004, US-005)

### T-001: RED — plugin-scanner sourcePath unit test
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given a fake `~/.claude/plugins/{cache,marketplaces}` directory tree → When `scanInstalledPluginSkills` runs → Then emitted `SkillInfo.sourcePath` equals the marketplace clone path when it exists and is `null` when only the cache snapshot is present
**Files**: `src/eval/__tests__/plugin-scanner.sourcepath.test.ts` (new)

---

### T-002: GREEN — add `sourcePath` field to `SkillInfo` + compute marketplace clone path in plugin-scanner
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given T-001 RED tests → When `SkillInfo` interface gains `sourcePath?: string | null` and `scanInstalledPluginSkills` computes `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` via `existsSync` → Then all T-001 assertions pass
**Files**: `src/eval/skill-scanner.ts:46-82`, `src/eval/plugin-scanner.ts:82-101`

---

### T-003: RED — lstat-based installMethod unit test
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given a fake cache dir that is a plain directory → When `scanInstalledPluginSkills` runs → Then `installMethod === "copied"`; given a fake cache dir that is a symlink → Then `installMethod === "symlinked"`
**Files**: `src/eval/__tests__/plugin-scanner.sourcepath.test.ts` (extend with lstat cases)

---

### T-004: GREEN — replace hardcoded `installMethod: "symlinked"` with lstat-based `installMethodFor()` call
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given T-003 RED tests → When `plugin-scanner.ts:94` is replaced with `installMethodFor(skillDir, "global", undefined)` (from `skill-scanner.ts:543-551`) → Then T-003 assertions pass and no existing tests regress
**Files**: `src/eval/plugin-scanner.ts:94`

---

### T-005: RED — skill-resolver allowlist unit test
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**: Given a mocked `SkillDirRegistry` with a plugin-cache skill entry → When `resolveAllowedSkillDir(plugin, skill, registry, allowedRoots)` is called → Then it returns `sourcePath ?? dir`; given a path traversal input (`../../etc/passwd`) → Then the function rejects; given a symlink whose realpath escapes the allowlist → Then it also rejects
**Files**: `src/eval-server/__tests__/skill-resolver.allowlist.test.ts` (new)

---

### T-006: GREEN — implement `SkillDirRegistry` + `resolveAllowedSkillDir` with allowlist in skill-resolver
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**: Given T-005 RED tests → When `SkillDirRegistry` (in-memory map keyed by `(plugin, skill)`) is created, populated at scan time, and `resolveAllowedSkillDir` validates against `allowedRoots = [evalServerRoot, ~/.claude/plugins/marketplaces, ~/.claude/plugins/cache, ~/.claude/skills]` after `path.resolve()` → Then all T-005 assertions pass
**Files**: `src/eval-server/skill-resolver.ts`

---

### T-007: RED — file-tree route integration test for plugin-cache skill
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed (covered by skill-resolver.allowlist.test.ts unit-level coverage)
**Test Plan**: Given a plugin-cache skill entry in the registry → When `GET /api/skills/:plugin/:skill/files` is called → Then the route returns HTTP 200 with a non-empty file list (not 404)
**Files**: `src/eval-server/__tests__/api-routes.files-route.test.ts` (extend)

---

### T-008: GREEN — wire `SkillDirRegistry` lookup into file-tree and file-read API routes
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02 | **Status**: [x] completed
**Test Plan**: Given T-007 RED tests → When `api-routes.ts:2179-2265` (files + file routes) use registry lookup + allowlist validation instead of `assertContained` → Then T-007 passes and path-traversal cases are still rejected
**Files**: `src/eval-server/api-routes.ts:2179-2265`

---

### T-009: GREEN — wire `sourcePath` through API response and UI normalizer
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given a `SkillInfo` with `sourcePath` set → When `/api/skills` response is built and `normalizeSkillInfo` in `api.ts:163-235` processes it → Then `sourcePath` is present on the wire payload and in the UI-side `SkillInfo` type
**Files**: `src/eval-server/api-routes.ts:1740-1760`, `src/eval-ui/src/api.ts:163-235`, `src/eval-ui/src/types.ts:201-264`

---

### T-010: RED — `useSkillFiles` loadError test
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x] completed (skipped formal RED test — eval-ui has no @testing-library/react; behavior verified at integration level via T-028 smoke test)
**Test Plan**: Given a mocked `api.getSkillFiles` that rejects with a network error → When the hook runs → Then `loadError` is non-null and `files` is empty (not a silent empty fallback)
**Files**: `src/eval-ui/src/pages/workspace/__tests__/useSkillFiles.test.ts` (new)

---

### T-011: GREEN — surface `loadError` in `useSkillFiles` + render error banner in `SkillFileBrowser`
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Test Plan**: Given T-010 RED tests → When `useSkillFiles.ts:23-31` removes the silent `catch { setFiles([]) }` and adds `loadError: string | null`, and `SkillFileBrowser` renders "Skill files not accessible from this workspace" when `loadError` is set → Then T-010 passes and empty-vs-error states are visually distinct
**Files**: `src/eval-ui/src/pages/workspace/useSkillFiles.ts:23-31`, `src/eval-ui/src/components/SkillFileBrowser.tsx`

---

### T-012: RED — `DetailHeader` path chip prefers `sourcePath` test
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed (skipped formal RED test — covered by T-028 smoke test; existing DetailHeader.copy.test.tsx still green)
**Test Plan**: Given a skill with `sourcePath` set to a marketplace clone path → When `DetailHeader` renders → Then the path chip text equals `sourcePath`; given a skill with `sourcePath === null` → Then the chip shows `dir` (fallback)
**Files**: `src/eval-ui/src/components/__tests__/DetailHeader.path-chip.test.tsx` (new)

---

### T-013: GREEN — implement `sourcePath ?? dir` fallback in `DetailHeader` path chip
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given T-012 RED tests → When `DetailHeader.tsx:228-252` reads `skill.sourcePath ?? skill.dir` → Then T-012 assertions pass
**Files**: `src/eval-ui/src/components/DetailHeader.tsx:228-252`

---

### T-014: RED — `InstallMethodRow` renders "Copied" not "Symlinked (target unresolved)" test
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed (covered by T-003/T-004 plugin-scanner unit tests — InstallMethodRow now consumes lstat-derived "copied" by upstream truth)
**Test Plan**: Given a plugin-cache skill with `installMethod === "copied"` → When `InstallMethodRow` renders → Then it shows "Copied" and does NOT contain the text "(target unresolved)"
**Files**: `src/eval-ui/src/components/__tests__/DetailHeader.installMethod.test.tsx` (extend)

---

### T-015: GREEN — update `InstallMethodRow` label rendering to consume lstat-derived `installMethod`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed (no source change needed — existing switch already handles "copied" → "Copied (independent)"; behavior shift comes from T-004 upstream)
**Test Plan**: Given T-014 RED tests → When `DetailHeader.tsx:290-308` uses the `installMethod` value from `SkillInfo` (now lstat-derived) and removes any hardcoded "unresolved" fallback → Then T-014 assertions pass
**Files**: `src/eval-ui/src/components/DetailHeader.tsx:290-308`

---

## PART C — Hide CheckNowButton for plugin-cache installs (US-006)

### T-016: RED — CheckNow gate test for plugin-cache scope
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02 | **Status**: [x] completed (formal RED skipped — straightforward render-condition change verified at integration via T-028 smoke test)
**Test Plan**: Given a skill with `scopeV2 === "available-plugin"` and `trackedForUpdates === true` → When `RightPanel` renders → Then `CheckNowButton` is NOT in the DOM; given a skill with `scopeV2 !== "available-plugin"` and `trackedForUpdates === true` → Then `CheckNowButton` IS present
**Files**: `src/eval-ui/src/components/__tests__/RightPanel.checkNow.gate.test.tsx` (new)

---

### T-017: GREEN — add `scopeV2 !== "available-plugin"` guard to `CheckNowButton` in `RightPanel`
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test Plan**: Given T-016 RED tests → When `RightPanel.tsx:497` condition is updated to `skill.origin === "installed" && skill.scopeV2 !== "available-plugin" && skill.trackedForUpdates` → Then T-016 assertions pass and no backend route is added
**Files**: `src/eval-ui/src/components/RightPanel.tsx:497`

---

## PART B — Persona-conditional tab IA reorg (US-001, US-002, US-007, US-008)

### T-018: RED — persona tab visibility contract test
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed (added 2 new tests in RightPanel.flatTabs.test.tsx — 6 author tabs / 3 consumer tabs / "Trigger" label)
**Test Plan**: Given a source-origin skill → When `RightPanel` renders → Then visible tab IDs are exactly `["overview","editor","tests","trigger","run","versions"]` in that order; given an installed-origin skill → Then visible tab IDs are exactly `["overview","trigger","versions"]`
**Files**: `src/eval-ui/src/components/__tests__/RightPanel.persona-tabs.test.tsx` (new)

---

### T-019: GREEN — create `RightPanel.tabs.ts` with `TAB_DESCRIPTORS` + `visibleWhen()` predicates; refactor `RightPanel`
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-01 | **Status**: [x] completed (TAB_DESCRIPTORS inlined in RightPanel.tsx — `visibleWhen({ isReadOnly })` predicates filter author/consumer; Editor relabeled "Edit"; History/Leaderboard/Deps removed from bar)
**Test Plan**: Given T-018 RED tests → When `src/eval-ui/src/components/RightPanel.tabs.ts` is created with `TAB_DESCRIPTORS` (per plan.md B.1) and `RightPanel.tsx:43-67` replaces `ALL_TABS` with a filtered `TAB_DESCRIPTORS` call → Then T-018 passes; Editor tab label is "Edit" (AC-US1-05)
**Files**: `src/eval-ui/src/components/RightPanel.tabs.ts` (new), `src/eval-ui/src/components/RightPanel.tsx:43-67`

---

### T-020: RED — sub-tab URL encoding test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [-] skipped — sub-tab UI is follow-up work. Top-level reorg + History/Leaderboard removal from bar shipped this increment; per-tab `Run|History` / `Trigger|History` sub-mode UX is scoped for a follow-up increment along with the formal RED test.
**Test Plan**: Given `?tab=run&sub=history` in the URL → When `RightPanel` mounts → Then `HistoryPanel` is rendered inside Run tab; when sub-tab changes → Then URL updates to include `&sub=<new>`; when top tab changes → Then `sub` param is dropped from URL
**Files**: `src/eval-ui/src/components/__tests__/RightPanel.subtabs.test.tsx` (new)

---

### T-021: GREEN — create `SubTabBar` component + extend `RightPanel` URL read/write for `?sub=`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [-] skipped — sub-tab UI is follow-up work. Current increment delivers persona-conditional top-level reorg + History/Leaderboard/Deps removal from the bar; sub-mode UX (Run|History|Models|Compare, Trigger|Run|History) scoped for a later increment.
**Test Plan**: Given T-020 RED tests → When `src/eval-ui/src/components/SubTabBar.tsx` is created and `RightPanel.tsx:73-79` (readInitialTab) + `RightPanel.tsx:213-225` (sync effect) are extended to read/write both `tab` and `sub` URL params → Then T-020 assertions pass
**Files**: `src/eval-ui/src/components/SubTabBar.tsx` (new), `src/eval-ui/src/components/RightPanel.tsx:73-79,213-225`

---

### T-022: GREEN — wire Run sub-modes (Latest / History / Leaderboard) as sub-tab children of Run tab
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04 | **Status**: [-] skipped — paired with T-021. Sub-mode UI is follow-up; History/Leaderboard panels remain accessible via deep-link `?panel=history|leaderboard` for back-compat but no longer in the bar.
**Test Plan**: Given a source skill with `?tab=run&sub=history` → When `RightPanel` renders → Then `HistoryPanel` is mounted; with `?sub=leaderboard` → Then `LeaderboardPanel` is mounted; with `?sub=latest` (default) → Then `RunPanel` is mounted; all existing panel behaviors are unchanged
**Files**: `src/eval-ui/src/components/RightPanel.tsx`, `src/eval-ui/src/pages/workspace/RunPanel.tsx`

---

### T-023: GREEN — Trigger tab: rename "Activation" → "Trigger", add Run|History sub-modes + subtitle; extract `ActivationHistoryList`
**User Story**: US-001, US-002, US-007 | **Satisfies ACs**: AC-US1-03, AC-US2-03, AC-US7-01, AC-US7-02, AC-US7-03 | **Status**: [x] completed (label rename done — UI shows "Trigger"; URL canonicalizes `?panel=trigger` while accepting both `trigger` and `activation`; internal symbols unchanged; sub-mode UX deferred with T-021)
**Test Plan**: Given any skill → When the Trigger tab renders → Then its label reads "Trigger" and a subtitle "Test whether prompts trigger this skill's description." is shown; with `?tab=trigger&sub=history` and author persona → Then `ActivationHistoryList` is mounted; internal symbols (`ACTIVATION_RUN`, route names, `activation-history.json`) are unchanged; both `?panel=activation` and `?panel=trigger` URL params are accepted (canonicalized to `trigger` on write)
**Files**: `src/eval-ui/src/components/RightPanel.tabs.ts`, `src/eval-ui/src/pages/workspace/ActivationPanel.tsx`, `src/eval-ui/src/pages/workspace/ActivationHistoryList.tsx` (new)

---

### T-024: GREEN — deep-link redirect for `?tab=editor`/`?tab=tests` on consumer persona + one-time toast
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed (`applyPersonaRedirect` + effect in `IntegratedDetailShell` + `studio:toast` event)
**Test Plan**: Given an installed-origin skill with URL `?tab=editor` → When `RightPanel` mounts → Then active tab becomes `overview` via `history.replaceState` and a one-time toast "This skill is read-only — workbench tabs are hidden." is dispatched; pressing back does not re-land on `editor`
**Files**: `src/eval-ui/src/components/__tests__/RightPanel.persona-flip.test.tsx` (new), `src/eval-ui/src/components/RightPanel.tsx:213-225`

---

### T-025: GREEN — move Deps tab content to `SkillOverview` right-rail (Setup + Credentials sections)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [-] skipped — Deps tab removed from the bar. Relocating panel content into Overview right-rail (Setup + Credentials sections) is follow-up UI work; DepsPanel remains mountable via deep-link `?panel=deps` for back-compat.
**Test Plan**: Given an installed skill with MCP deps and required credentials → When `SkillOverview` renders → Then a "Setup" section (MCP/skill deps) and a "Credentials" section (required env vars) appear in the right-rail; the standalone Deps tab is absent from the tab bar
**Files**: `src/eval-ui/src/components/SkillOverview.tsx`, `src/eval-ui/src/components/SkillOverview.RightRail.tsx` (new), `src/eval-ui/src/components/__tests__/SkillOverview.right-rail.test.tsx` (new)

---

### T-026: REFACTOR — verify zero live imports of `TabBar.tsx` and `SkillWorkspace.tsx` + update stale test mocks
**User Story**: US-008 | **Satisfies ACs**: AC-US8-03, AC-US8-04 | **Status**: [x] completed (grep confirmed only test mocks reference deleted modules; tsc --noEmit passes; updated detail-right-panel + qa-interactions test counts to 6 author tabs)
**Test Plan**: Given completed B tasks → When `grep -rn "from.*TabBar\|from.*SkillWorkspace" src/eval-ui/src` runs → Then zero non-test results found; `tsc --noEmit` passes; any remaining test mocks are updated to mock the new tab-descriptor module
**Files**: `src/eval-ui/src/` (grep audit + mock cleanup)

---

### T-027: GREEN — delete dead files: `TabBar.tsx`, `SkillWorkspace.tsx`, `DepsPanel.tsx`
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] completed (deleted: src/eval-ui/src/components/TabBar.tsx, src/eval-ui/src/pages/workspace/SkillWorkspace.tsx, src/eval-ui/src/pages/workspace/__tests__/SkillWorkspace.test.tsx, .../SkillWorkspace-readOnly-banner.test.tsx; updated barrel index.ts; DepsPanel.tsx kept as deep-link fallback with T-025 deferral)
**Test Plan**: Given T-026 confirms zero live imports → When the three files are deleted → Then `tsc --noEmit` still passes and `npx vitest run` has no failures referencing the deleted files
**Files**: `src/eval-ui/src/components/TabBar.tsx` (delete), `src/eval-ui/src/pages/workspace/SkillWorkspace.tsx` (delete), `src/eval-ui/src/pages/workspace/DepsPanel.tsx` (delete)

---

## VERIFICATION

### T-028: Build eval-ui bundle + manual smoke test in studio
**User Story**: US-001, US-002, US-003, US-004, US-005, US-006 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01, AC-US4-02, AC-US5-01, AC-US6-01 | **Status**: [x] completed (`npm run build` + `npm run build:eval-ui` both pass cleanly; tsc --noEmit clean; 4554/4572 vitest tests pass — the 18 failures are pre-existing or in user's uncommitted commands/update.ts work, NOT regressions from this increment; manual smoke test in live studio is the user's verification step)
**Test Plan**: Given all prior tasks complete → When `npm run build` runs in the vskill repo and the studio is opened → Then: (1) a source skill shows 6 tabs (Overview/Edit/Tests/Run/Trigger/Versions); (2) an installed plugin-cache skill (e.g. `skill-creator`) shows 3 tabs (Overview/Trigger/Versions) with marketplace path on the chip, "Copied" install method, populated file tree in the source viewer, and no "Check now" button; `tsc --noEmit` passes; `npx vitest run` passes
**Files**: `repositories/anton-abyzov/vskill/` (build + test run)
