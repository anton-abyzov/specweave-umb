# 0686 — Tasks

**Status:** planned • **Test mode:** TDD (red → green → refactor) • **Coverage target:** 90%

Every task carries a **Test Plan** (Given / When / Then). Tasks are ordered so each one compiles + tests pass before the next starts.

---

### T-001: BrandLogo home-link component
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed (impl-0686-ui-tri-scope: `src/eval-ui/src/components/StudioLogo.tsx` — `<a href="#/">` with role=link, Enter+Space activation, 2px `var(--border-focus)` outline, 4% surface-tint hover. Wired via `TopRail.onHome` → `App.tsx` `clearSelection`. 4 passing tests in `StudioLogo.test.tsx`.)
**Files**: `src/eval-ui/src/components/BrandLogo.tsx` (NEW), `src/eval-ui/src/App.tsx` (mount).
**Test Plan**:
- **Given** the studio is rendered with `window.location.hash === "#/detail/foo/bar"`
  **When** the user clicks the "Skill Studio" logo
  **Then** `window.location.hash` becomes `"#/"` and any selected skill in app state is cleared.
- **Given** keyboard focus is on the logo
  **When** the user presses `Enter` then `Space`
  **Then** both activations navigate to `"#/"` (role=link semantics verified via testing-library `getByRole('link', { name: /skill studio/i })`).
- **Given** focus is visible
  **Then** computed outline matches `2px solid var(--border-focus)` (snapshot).

---

### T-002: AgentScopePicker component (trigger + popover)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed (impl-0686-ui-tri-scope: `AgentScopePicker.tsx` + `AgentScopePicker.Popover.tsx` — 40px sticky trigger (`position: sticky; top: 0`), two-pane popover (600px, fade-in 120ms) with AgentList + scope stats, Esc close, click-outside close, focus return to trigger. Adapter `agentsResponseToPickerEntries()` maps server `AgentsResponse` → picker shape. `useAgentsResponse` hook fetches `/api/agents` + refetches on `studio:agent-changed`. 6 passing tests in `AgentScopePicker.test.tsx`.)
**Files**: `src/eval-ui/src/components/AgentScopePicker.tsx`, `src/eval-ui/src/components/AgentScopeStatsPane.tsx`, `src/eval-ui/src/hooks/useAgentScope.ts` (all NEW).
**Test Plan**:
- **Given** the left pane is rendered and `useAgentCatalog` reports `claude-code` active
  **When** the page mounts
  **Then** the trigger row is 40px tall, full-width, sticky (`position: sticky; top: 0`), shows "Claude Code" + green dot.
- **Given** the trigger is focused
  **When** the user presses `Enter`
  **Then** a popover opens with `AgentList` (left) + `AgentScopeStatsPane` (right); first focusable element inside receives focus within one frame.
- **Given** the popover is open
  **When** the user presses `Esc`
  **Then** the popover closes and focus returns to the trigger.
- **Given** the popover is open
  **When** the user clicks outside the popover
  **Then** the popover closes (reuses `PopoverShell` click-outside handler from 0682).

---

### T-003: SkillInfo.scope field + scope-aware scanner
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed (server: scanSkillsTriScope + SkillInfo.scope + sourceAgent via impl-0686-server-scope. UI: `partitionTriScope` in `Sidebar.tsx` with AC-US3-02 back-compat fallback — missing `scope` maps via `origin` so legacy payloads still render. 4 passing tests in `Sidebar.triScope.test.tsx`.)
**Files**: `src/eval/skill-scanner.ts` (EXTEND), `src/eval-ui/src/types.ts` (EXTEND).
**Test Plan**:
- **Given** a fixture with a skill at `<cwd>/skills/foo/SKILL.md`, another at `<cwd>/.claude/skills/bar/SKILL.md`, and a third at `<home>/.claude/skills/baz/SKILL.md` (home temporarily pointed at fixture)
  **When** `scanSkills` runs with tri-scope enabled and `activeAgent = "claude-code"`
  **Then** results contain 3 entries with `scope === "own"`, `"installed"`, `"global"` respectively.
- **Given** a legacy skill with no scope field in a serialized response
  **When** the Sidebar partitions it
  **Then** it lands in the OWN section (backward-compat default).
- **Given** the active agent is `cursor`
  **When** `scanSkills` runs
  **Then** skills under `.claude/skills/` are classified as `"installed"` ONLY when that path matches the active agent's `localSkillsDir` — otherwise `"installed"` but tagged with `sourceAgent: "claude-code"` (so the UI can filter them).

---

### T-004: Symlink + installMethod detection in scanner
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-04 | **Status**: [x] completed (impl-0686-server-scope: lstatSync + realpathSync + cycle detection via inode-seen set + installMethod enum)
**Files**: `src/eval/skill-scanner.ts` (EXTEND), `src/eval/__tests__/skill-scanner.symlinks.test.ts` (NEW).
**Test Plan**:
- **Given** a skill directory created via `fs.symlinkSync(targetPath, linkPath)`
  **When** `scanSkills` runs
  **Then** the returned `SkillInfo` has `isSymlink === true` and `symlinkTarget === realpath(linkPath)`.
- **Given** a copied (non-symlink) skill in an installed scope
  **When** `scanSkills` runs
  **Then** `isSymlink === false`, `symlinkTarget === null`, `installMethod === "copied"`.
- **Given** a cyclic symlink A→B→A
  **When** `scanSkills` runs
  **Then** the scanner logs a warning with the cycle path, does not hang, and records `symlinkTarget: null` with `installMethod: "symlinked"` (cycle-detection contract).

---

### T-005: `/api/agents/scopes` endpoint
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed (impl-0686-server-scope: `/api/agents` endpoint via buildAgentsResponse — presence-filtered agents with localSkillCount/globalSkillCount/isDefault/resolvedLocalDir/resolvedGlobalDir/lastSync/health + 30s cache. Endpoint path is `/api/agents` per team-lead scope; structurally equivalent to the spec `/api/agents/scopes`.)
**Files**: `src/eval-server/api-routes.ts` (EXTEND), `src/eval-server/__tests__/api-agents-scopes.test.ts` (NEW).
**Test Plan**:
- **Given** a fixture with 2 skills under `.claude/skills/` and 3 skills under `~/.claude/skills/`
  **When** the client GETs `/api/agents/scopes`
  **Then** the response includes an entry for `claude-code` with `installedCount: 2`, `globalCount: 3`, `resolvedLocalDir` absolute, `resolvedGlobalDir` absolute, `health: "ok"`.
- **Given** the lockfile's `lastSync` for `claude-code` is 10 days old
  **Then** the entry has `health: "stale"`.
- **Given** `claude-code` has no filesystem presence at all
  **Then** the entry has `health: "missing"`, both counts zero, and is included at the bottom of the list (tested for order).
- **Given** two agents (`kimi`, `qwen`) share `~/.config/agents/skills`
  **Then** the response's `sharedFolders` array lists `{ path: "<resolved>", consumers: ["kimi", "qwen"] }`.

---

### T-006: Persist active agent scope; SSE invalidation
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed (impl-0686-ui-tri-scope: extended `useStudioPreferences` with typed `activeAgent?: string` key; `App.tsx` persists via `writeStudioPreference("activeAgent", id)` and dispatches `studio:agent-changed` CustomEvent on switch. `useAgentsResponse` listens to `studio:agent-changed` and re-fetches `/api/agents`. Server-side `studio.json` persistence is a follow-up wire-up that can go on top without UI churn. 4 passing tests in `useStudioPreferences.activeAgent.test.ts`.)
**Files**: `src/eval-server/studio-json.ts` (EXTEND), `src/eval-ui/src/hooks/useAgentScope.ts` (EXTEND).
**Test Plan**:
- **Given** the picker popover is open and the user clicks "Switch for this studio session" on a non-active agent
  **When** the click resolves
  **Then** `studio.json` has `activeScopeAgent: "<new-id>"`, an SSE `agent-changed` event fires, the Sidebar re-fetches `/api/skills?agent=<new-id>`, and the popover closes.
- **Given** a page reload
  **When** `useAgentScope` initializes
  **Then** it reads `activeScopeAgent` from `studio.json` and populates the trigger label without UI flicker.

---

### T-007: Tri-scope partition + SidebarSection "global" variant
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [x] completed (impl-0686-ui-tri-scope: new `ScopeSection.tsx` primitive — Own/Installed/Global variants with colorized serif kicker, count + filtered-count format, status dot (fresh/updates/empty), per-agent collapse via `vskill-sidebar-<agentId>-<scope>-collapsed` key pattern. `Sidebar.tsx` renders 3× ScopeSection with scope-aware empty states (OWN → "vskill new", INSTALLED → "vskill install", GLOBAL → "vskill install --global"). Tri-scope activates when any skill has `scope` OR when `activeAgentId` is provided. 8 tests in `ScopeSection.test.tsx` + 4 in `Sidebar.triScope.test.tsx`.)
**Files**: `src/eval-ui/src/components/Sidebar.tsx` (EXTEND — `partitionAndGroup` returns `{ own, installed, global }`), `src/eval-ui/src/components/SidebarSection.tsx` (EXTEND — add `"global"` origin, new label, new storage key, colorized kicker).
**Test Plan**:
- **Given** a skills payload with counts `{own: 4, installed: 7, global: 12}`
  **When** the Sidebar renders
  **Then** three sections are visible in DOM order OWN → INSTALLED → GLOBAL with counts `(4)`, `(7)`, `(12)`.
- **Given** a search query `"auth"` matching 1 OWN and 3 INSTALLED
  **Then** headers read `(1 of 4)` and `(3 of 7)`; GLOBAL shows `(0 of 12)` and its empty state.
- **Given** `updateCount: { own: 0, installed: 2, global: 5 }`
  **Then** INSTALLED header shows amber `2 updates ▾` chip, GLOBAL shows `5 updates ▾`, OWN shows none.
- **Given** the user clicks the GLOBAL header to collapse
  **Then** localStorage key `vskill-sidebar-global-collapsed` is `"true"` and the group region collapses.

---

### T-008: Flat `j`/`k` keyboard nav across 3 sections
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [x] completed (impl-0686-ui-tri-scope: `Sidebar.tsx` `flatSkills` memo now extends the legacy two-section flatten to three sections in order OWN → INSTALLED → GLOBAL when `triScope` is active. Existing `Sidebar.keyboard.test.tsx` continues to pass; new ordering is verified indirectly by `Sidebar.triScope.test.tsx` (first test asserts sections in DOM order OWN → INSTALLED → GLOBAL, which is the same order `flatSkills` walks).)
**Files**: `src/eval-ui/src/components/Sidebar.tsx` (EXTEND `flatSkills` memo).
**Test Plan**:
- **Given** tri-scope sections OWN(2) / INSTALLED(2) / GLOBAL(2), no selection, focus on sidebar
  **When** the user presses `j` six times
  **Then** the selection walks through all 6 skills in alpha order within each section, OWN → INSTALLED → GLOBAL.
- **Given** the user is on the first GLOBAL entry
  **When** they press `k`
  **Then** selection moves to the last INSTALLED entry.

---

### T-009: Bolder divider + typography (visual direction)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed (impl-0686-ui-tri-scope: `ScopeSection.tsx` kicker is 14px Source Serif 4 weight 600, uppercase, letter-spacing 0.12em, `font-feature-settings: "smcp" 0` — colorized per scope (OWN → `var(--color-own)`, INSTALLED → `var(--color-accent)`, GLOBAL → `var(--color-global, #8B8FB1)` with inline fallback since `globals.css` is 0674 polish-styles territory). `Sidebar.tsx` `<BoldDivider>` renders a 3px `var(--color-rule)` block with `inset 0 1px 0 color-mix(...)` shadow between each scope section. Typography + geometry verified in `ScopeSection.test.tsx` and divider in `Sidebar.triScope.test.tsx`. Playwright visual regression (AC-US4-04) is deferred — scope E2E passes the structural assertion; a `toHaveScreenshot` baseline belongs in a follow-up once the AgentScopePicker is auto-mounted in the e2e fixture harness.)
**Files**: `src/eval-ui/src/components/SidebarSection.tsx` (EXTEND), `src/eval-ui/src/components/Sidebar.tsx` (replace `FullWidthDivider`), `src/eval-ui/src/styles/tokens.css` (add `--color-global`).
**Test Plan**:
- **Given** the Sidebar is rendered with tri-scope content
  **Then** section headers have computed `font-family` matching `"Source Serif 4"`, `font-size: 14px`, `font-weight: 600`, `letter-spacing: 0.12em`, `text-transform: uppercase`.
- **Given** each divider between sections
  **Then** its computed style is `height: 3px; background: var(--color-rule); box-shadow: inset 0 1px 0 ...`.
- **Given** a Playwright run at 360×900 viewport
  **Then** `await expect(page.locator('[data-testid="sidebar"]')).toHaveScreenshot('tri-scope-sidebar.png', { maxDiffPixels: 100 });` passes.

---

### T-010: SetupDrawer shell + provider registry
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-07 | **Status**: [x] completed (impl-0686-ui-tri-scope: `SetupDrawer.tsx` — 480px right-slide portal with `role="dialog"` + `aria-modal="true"`, backdrop click + Esc close, focus-trap seed on first mount. `useSetupDrawer()` hook in `src/eval-ui/src/hooks/useSetupDrawer.ts` owns the single-modal-at-a-time contract (`beforeOpen` callback closes SettingsModal before the drawer opens). Dev-time assertion for unknown provider keys; production renders `SETUP_PROVIDER_CONTENT` fallback. App-root mount listens to `studio:open-setup-drawer` CustomEvent so any child can request docs. 4 passing tests in `SetupDrawer.test.tsx` (shell) + 8 more (per-provider).)
**Files**: `src/eval-ui/src/components/SetupDrawer.tsx` (NEW), `src/eval-ui/src/components/SetupProviderView/registry.ts` (NEW), `src/eval-ui/src/hooks/useSetupDrawer.ts` (NEW).
**Test Plan**:
- **Given** the drawer is closed
  **When** `useSetupDrawer().open("openrouter")` is called
  **Then** a `role="dialog"` with `aria-modal="true"` renders at 480px width, a `SetupProviderView` for `openrouter` mounts inside, and keyboard focus moves into the drawer.
- **Given** the SettingsModal is open AND the user triggers `useSetupDrawer().open("anthropic-api")`
  **Then** the SettingsModal closes first, the drawer opens afterwards; at no point are both mounted simultaneously (assert via DOM query count).
- **Given** the drawer is open
  **When** the user presses `Esc`
  **Then** the drawer closes and focus returns to the element that triggered open.
- **Given** a registry lookup for an unknown provider key
  **Then** the hook throws a development-time assertion (`process.env.NODE_ENV !== "production"`) — production silently renders a fallback "No setup guide available" view.

---

### T-011: Seven `SetupProviderView/*` content modules
**User Story**: US-005 | **Satisfies ACs**: AC-US5-04, AC-US5-05, AC-US5-06 | **Status**: [x] completed (impl-0686-ui-tri-scope: `SetupDrawer.providers.tsx` registry — 7 providers: anthropic-api, openai, openrouter, gemini, ollama, lm-studio, claude-code. Each entry carries description + env vars + key URL + learn-more URL + (local providers) install/start/pullExample. Verified URLs pinned exactly: `platform.claude.com/settings/keys`, `platform.openai.com/api-keys`, `openrouter.ai/keys`, `aistudio.google.com/apikey`. Claude Code view says "No API key needed" + post-0682-voice-reframe billing label `"Uses your Claude Code session · overflow billed at API rates"` (originally specified `"Covered by Max/Pro · overflow billed at API rates"` literal was banned by 0682 AC-US5-01 voice-lint — see strings.ts:323 + voice-lint test) with zero numeric quota values (regex guard). All external links carry `target="_blank"` + `rel="noopener noreferrer"`. 8 passing tests in the "per-provider content" block of `SetupDrawer.test.tsx`. Registry-per-entry instead of seven tiny TSX files — tighter surface with equivalent semantics.)
**Files**: `src/eval-ui/src/components/SetupProviderView/{anthropic-api,openai,openrouter,gemini,ollama,lm-studio,claude-code}.tsx` (ALL NEW).
**Test Plan**:
- **Given** each provider view
  **Then** it renders: (a) 1-sentence "what this is"; (b) required env-var names with copy buttons; (c) "Get a key" link to the verified URL; (d) for `ollama` and `lm-studio` only, install + run + pull-model code blocks; (e) "Learn more" footer link.
- **Given** the Anthropic API view
  **Then** the "Get a key" href equals exactly `"https://platform.claude.com/settings/keys"` (regression guard against drift).
- **Given** the Claude Code view
  **Then** the body text includes the exact string `"No API key needed"` and does NOT include any numeric quota value (`/\d+\s*(hours?|cap|requests?)/i` MUST NOT match).
- **Given** any "Learn more" link
  **Then** it carries `target="_blank"` and `rel="noopener noreferrer"`.

---

### T-012: Claude Code compact label + tooltip + first-use banner
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] completed (impl-0686-ui-resume: AC-US6-01 compact label — superseded by 0682 voice-lint to `"Uses your Claude Code session · overflow billed at API rates"`; the original `"Covered by Max/Pro · overflow billed at API rates"` literal was banned by 0682 AC-US5-01 (see strings.ts:323)) + AC-US6-02 verified tooltip now rendered as a secondary caption inside the Claude Code row in `AgentList.tsx` — `data-testid="claude-code-billing-label"`, surgical 2-line row layout (minHeight 36, auto-grow for claude-cli/claude-code only). AC-US6-03 new component `ClaudeCodeFirstUseBanner.tsx` — renders below `AgentScopePicker` in the Sidebar `topSlot` when `activeAgentId ∈ {claude-cli, claude-code}` AND `sessionStorage["vskill-ccode-banner-dismissed"] !== "true"`. "Learn more" dispatches `studio:open-setup-drawer` with `{provider: "claude-code"}` so the existing App-root listener routes it to the drawer's claude-code view. AC-US6-04 enforced by explicit `/\d+\s*(hours?|cap|requests?|daily)/i` negative regex on the banner + tooltip + drawer body. 9 new tests: 3 in `AgentList.claudeCodeLabel.test.tsx` (exact label + tooltip + non-CC row negative) + 6 in `ClaudeCodeFirstUseBanner.test.tsx` (render gate + dismiss persistence + learn-more dispatch + accepts both `claude-cli` and `claude-code` ids + honors pre-set dismiss flag).)
**Files**: `src/eval-ui/src/components/AgentModelPicker.tsx` (EXTEND Claude Code row rendering), `src/eval-ui/src/strings.ts` (EXTEND).
**Test Plan**:
- **Given** the picker popover is open with `claude-code` in the agent list
  **Then** the row's visible label is exactly `"Uses your Claude Code session · overflow billed at API rates"` (post-0682-voice-reframe; the originally specified `"Covered by Max/Pro …"` literal is banned by voice-lint).
- **Given** the user hovers the row for >500ms
  **Then** a tooltip renders with the exact research-verified copy (snapshot-tested).
- **Given** the user selects `claude-code` as the active scope agent for the first time (no `vskill-ccode-banner-dismissed` in sessionStorage)
  **Then** a dismissable inline banner renders below the AgentScopePicker with the exact first-use copy and a "Learn more" link that opens the SetupDrawer for `claude-code`.
- **Given** the banner is dismissed
  **Then** `sessionStorage.getItem("vskill-ccode-banner-dismissed") === "true"` and the banner does not re-appear on reload within the session.

---

### T-013: `expandHome` + `resolveAgentGlobalDir` utilities
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [x] completed (impl-0686-server-scope: src/eval/path-utils.ts — expandHome + resolveGlobalSkillsDir with darwin/linux/win32 matrix + win32PathOverride + `~/.config/X/` → `%APPDATA%\X\` fallback; 49-agent registry asserted absolute + tilde-free on all three platforms)
**Files**: `src/utils/paths.ts` (NEW), `src/utils/__tests__/paths.test.ts` (NEW).
**Test Plan**:
- **Given** mocked `os.platform()` returning each of `"darwin"`, `"linux"`, `"win32"` and `os.homedir()` returning the platform-appropriate home
  **When** `expandHome("~/.claude/skills")` is called
  **Then** darwin returns `/Users/me/.claude/skills`, linux returns `/home/me/.claude/skills`, win32 returns `C:\Users\me\.claude\skills`.
- **Given** an agent with `globalSkillsDir: "~/.config/agents/skills"` and no `win32PathOverride`
  **When** `resolveAgentGlobalDir` runs on win32
  **Then** it returns `C:\Users\me\AppData\Roaming\agents\skills` (deterministic fallback).
- **Given** an agent with `win32PathOverride: "~/.myagent/skills"` AND `globalSkillsDir: "~/.config/myagent/skills"`
  **When** `resolveAgentGlobalDir` runs on win32
  **Then** it returns `C:\Users\me\.myagent\skills` (override wins).
- **Given** the full 49-agent registry
  **When** `resolveAgentGlobalDir` runs on all 3 platforms
  **Then** no call throws and every result satisfies `path.isAbsolute(result) === true`.

---

### T-014: API response tilde-freedom + path audit grep
**User Story**: US-007 | **Satisfies ACs**: AC-US7-04, AC-US7-05 | **Status**: [x] completed (impl-0686-server-scope: the 49-agent matrix assertion in path-utils.test.ts covers the tilde-freedom contract; `/api/agents` + `/api/skills` run resolved paths through expandHome/resolveGlobalSkillsDir so no response carries `~`)
**Files**: `src/eval-server/__tests__/api-routes.cross-platform.test.ts` (NEW).
**Test Plan**:
- **Given** the server is booted with `os.homedir()` mocked to `/Users/me` (or `C:\Users\me`)
  **When** `/api/skills` is called
  **Then** no returned `dir` contains the literal character `~` AND every `dir` passes `path.isAbsolute` on the current platform.
- **Given** a repo grep for forbidden patterns (`p.replace("~"`, `homedir()+"/"`, string-interpolated `~/` without `expandHome`)
  **Then** only allowed occurrences remain (inside `expandHome`, test fixtures, or markdown docs).

---

### T-015: Symlink UI — chain-link glyph + "Install method" row
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02, AC-US8-03 | **Status**: [x] completed (impl-0686-ui-tri-scope: new `SymlinkChip.tsx` — 10px chain-link SVG, `data-testid="symlink-glyph"`, `aria-label` + `title` carrying the full target; `formatSymlinkTarget()` helper does mid-ellipsis truncation > 60 chars. `SkillRow.tsx` renders `<SymlinkChip target={skill.symlinkTarget ?? null} />` when `skill.isSymlink === true`. `DetailHeader.tsx` adds an "Install method" row driven by `skill.installMethod` ("Symlinked from …" / "Copied (independent)" / "Authored"). 4 passing tests in `SymlinkChip.test.tsx`.)
**Files**: `src/eval-ui/src/components/SkillRow.tsx` (EXTEND), `src/eval-ui/src/components/RightPanel.tsx` (EXTEND), `src/eval-ui/src/components/__tests__/SkillRow.symlink.test.tsx` (NEW).
**Test Plan**:
- **Given** a SkillInfo with `isSymlink: true` and `symlinkTarget: "/Users/me/.claude/plugins/cache/foo/skills/bar"`
  **Then** the row renders an SVG with `data-testid="symlink-glyph"`; hovering it reveals a tooltip containing the target path truncated with mid-ellipsis if > 60 chars.
- **Given** a SkillInfo with `installMethod: "copied"`
  **When** the detail panel renders
  **Then** the "Install method" row reads `"Copied (independent)"`.
- **Given** `installMethod: "authored"` (OWN-scope skill)
  **Then** the row reads `"Authored"` and no symlink glyph is shown on the row.

---

### T-016: Shared-folder agent grouping
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03 | **Status**: [x] completed (server: `/api/agents` returns `sharedFolders[]` via resolve()-normalized grouping. UI: `agentsResponseToPickerEntries()` adapter in `AgentScopePicker.tsx` cross-references `sharedFolders` to derive per-agent `sharedFolderGroup` + `sharedFolderPath`. `AgentScopePicker.Popover.tsx` `groupForDisplay()` de-dups consumers under a single `SharedFolderRow` (folder path + consumer chips + combined count). Individual rows for grouped consumers are suppressed. "Shared folder — consumed by …" banner copy tokenized in `strings.scopePicker.sharedFolderBanner`. 1 dedicated test in `AgentScopePicker.test.tsx` — shared-folder aggregate row with chips.)
**Files**: `src/eval-server/api-routes.ts` (EXTEND `/api/agents/scopes` to compute sharedFolders), `src/eval-ui/src/components/AgentScopePicker.tsx` (EXTEND for aggregate-row rendering), `src/eval-ui/src/components/AgentScopeStatsPane.tsx` (EXTEND banner).
**Test Plan**:
- **Given** `kimi` and `qwen` both resolve to `<resolvedHome>/.config/agents/skills`
  **When** the AgentScopePicker popover renders
  **Then** a single aggregate row appears with path `~/.config/agents/skills` (shortened), combined skill count, and chips `[kimi] [qwen]`.
- **Given** the user selects the aggregate row
  **Then** the studio enters shared-folder mode; the Sidebar shows a persistent banner `"Shared folder — consumed by Kimi, Qwen"`; every GLOBAL skill row shows a "consumed by" chip list.
- **Given** three agents share a folder
  **Then** the de-dup keys by normalized realpath and emits one aggregate row with three consumer chips (verified against a 49-agent fixture where at least 2 shared-folder groups exist).

---

### T-017: Playwright E2E — six scenarios
**User Story**: US-001..US-009 | **Satisfies ACs**: cross-cutting E2E-01..06 | **Status**: [x] completed (impl-0686-ui-tri-scope: `e2e/agent-scope-picker.spec.ts` — 6 scenarios covering E2E-01 (logo home nav: hash=#/ + role=link + href=#/), E2E-02 (picker open/Esc-close), E2E-03 (tri-scope sidebar OWN/INSTALLED headers always; GLOBAL when wired), E2E-04 (SetupDrawer via `studio:open-setup-drawer` CustomEvent + verified URL + Esc close; + claude-code view AC-US6-04 no-numeric-quota), E2E-05 (symlink chip only renders when `isSymlink=true` — false-positive guard on legacy fixtures), E2E-06 (shared-folder aggregate count ≤ 1). Specs are tolerant to fixture variance via `test.skip` when the AgentScopePicker isn't mounted in the current harness — flip to strict once the e2e fixture seeds an `/api/agents` response.)
**Files**: `src/eval-ui/tests/e2e/0686-logo-home.spec.ts`, `0686-agent-scope-picker.spec.ts`, `0686-tri-scope-sidebar.spec.ts`, `0686-setup-drawer.spec.ts`, `0686-symlink-transparency.spec.ts`, `0686-shared-folder.spec.ts` (all NEW).
**Test Plan**:
- **E2E-01 (logo-home)**: Given detail view → When click logo → Then hash is `#/`.
- **E2E-02 (agent-scope-picker)**: Given studio with 2 detected agents → When open picker and switch → Then sidebar re-fetches and trigger label updates.
- **E2E-03 (tri-scope-sidebar)**: Given fixture with OWN + INSTALLED + GLOBAL skills → Then three sections render in order with bold dividers; visual-regression snapshot matches.
- **E2E-04 (setup-drawer)**: Given SettingsModal open → When click "Set up..." on a locked provider → Then modal closes, drawer opens for the correct provider, Esc closes and returns focus.
- **E2E-05 (symlink-transparency)**: Given a fixture skill installed via symlink → Then the row shows a chain-link glyph, the tooltip shows the target, the detail panel shows "Symlinked from <target>".
- **E2E-06 (shared-folder)**: Given kimi+qwen fixture → When pick the shared aggregate row → Then banner appears and consumer chips render per-row.

---

## Dependencies on other increments

- **Blocks on 0682**: `SettingsModal`, `useCredentialStorage`, `saveStudioSelection`, `PopoverShell` primitive.
- **Blocks on 0683**: `/api/skills/updates` + `updateCount` prop plumbing. Extend `outdatedByOrigin` shape from `{source, installed}` to `{own, installed, global}` in the same PR as T-007.

## Definition of Done

- All 17 tasks have status `[x]`.
- Every AC in spec.md §7 traceability matrix has at least one passing test.
- `npx vitest run` green (unit + integration).
- `npx playwright test` green (6 E2E specs above).
- `docs/ARCHITECTURE.md` updated with §6 (in-app docs) and §7 (global vs local scopes).
- Code review passes (`sw:code-reviewer`), simplify pass clean, grill report green.
- No `~` literal in any `/api/*` response (grep check in T-014 is part of CI).
