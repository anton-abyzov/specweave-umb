# Tasks: Studio First-Launch Onboarding Polish

## Phase 1 — CLI onboarding (US-001)

### T-001: RED — onboarding skips when claude binary present
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given Claude Code installed (mock `detectClaudeBinary` → true) and no provider env vars, When `firstRunOnboarding(io)` runs, Then it returns `{ action: "skip" }` AND `io.stdout.write` was never called.
**File**: `src/__tests__/first-run-onboarding-claude-detect.test.ts` (new).

### T-002: GREEN — implement detectClaudeBinary + early-skip branch
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given the failing test from T-001, When `detectClaudeBinary()` is added (uses `spawnSync` with 250 ms timeout, win32 → `where`, posix → `which`) AND called before `anyProviderConfigured`, Then T-001 passes AND a parallel test that simulates timeout → false also passes.
**File**: `src/first-run-onboarding.ts`.

### T-003: RED+GREEN — softened wording in the prompt and decline path
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given no claude binary AND no keys, When the prompt fires, Then the printed message does NOT contain "needs"; contains "Claude Code"; contains "optional"; AND the decline message contains BOTH "claude" AND "vskill keys set anthropic".
**File**: `src/first-run-onboarding.ts` + test in `src/__tests__/first-run-onboarding-wording.test.ts`.

## Phase 2 — Server pluginSkillCount (US-002)

### T-004: RED — buildAgentsResponse emits pluginSkillCount
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given a fixture root with `~/.claude/plugins/cache/foo/skills/skill-a/SKILL.md`, When `buildAgentsResponse({ root, home })` runs, Then the `claude-code` entry has `pluginSkillCount: 1` AND any non-claude-code entry has `pluginSkillCount: 0`.
**File**: `src/eval-server/__tests__/api-agents-plugin-count.test.ts` (new).

### T-005: GREEN — populate pluginSkillCount in api-routes.ts
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-05 | **Status**: [x] completed
**Test Plan**: T-004 passes after extending `AgentScopeEntry` and adding the single `scanInstalledPluginSkills({ agentId: "claude-code" }).length` lookup before the per-agent loop.
**File**: `src/eval-server/api-routes.ts`.

## Phase 3 — UI badge + popover (US-002)

### T-006: RED — adapter forwards pluginSkillCount onto PickerAgentEntry
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given a server response with `agents[0].pluginSkillCount = 81`, When `agentsResponseToPickerEntries(response)` runs, Then the returned entry has `pluginCount: 81`. Missing-field fixture defaults to `pluginCount: 0`.
**File**: `src/eval-ui/src/components/__tests__/AgentScopePicker-adapter.test.tsx` (new or extend existing).

### T-007: GREEN — adapter + interface change
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: T-006 passes after updating `PickerAgentEntry` interface and the `agentsResponseToPickerEntries` map.
**File**: `src/eval-ui/src/components/AgentScopePicker.tsx`.

### T-008: RED — trigger renders triple format with tooltip
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given an active agent with installedCount=0, globalCount=13, pluginCount=81, When AgentScopePicker renders, Then the trigger button text contains "(0 · 13 · 81)" AND the button's `title` attribute is "project · personal · plugins".
**File**: `src/eval-ui/src/components/__tests__/AgentScopePicker-trigger.test.tsx` (new).

### T-009: GREEN — trigger render update
**User Story**: US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: T-008 passes after editing `AgentScopePicker.tsx:177-186`.
**File**: `src/eval-ui/src/components/AgentScopePicker.tsx`.

### T-010: RED+GREEN — popover stats grid Plugins row
**User Story**: US-002 | **AC**: AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given the popover open for an agent with pluginCount=81, When the detail pane renders, Then a row labeled "Plugins" exists with value "81" between "Global" and "Last sync".
**File**: `src/eval-ui/src/components/AgentScopePicker.Popover.tsx` + a focused test or extend existing popover suite + new string `strings.scopePicker.statsPlugins = "Plugins"`.

## Phase 4 — RightPanel onboarding empty state (US-003)

### T-011: RED — EmptyState gains "empty-project" variant
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given `<EmptyState variant="empty-project" />`, When rendered inside a StudioProvider stub, Then the heading text equals "No skills installed for this project yet.", AND there are exactly two buttons named "Browse marketplaces" and "Create new skill". Clicking Browse dispatches a `studio:open-marketplace` `CustomEvent`. Clicking Create calls `setMode("create")` on the provider.
**File**: `src/eval-ui/src/components/__tests__/EmptyState-empty-project.test.tsx` (new).

### T-012: GREEN — implement variant + RightPanel branching
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: T-011 passes; AND a RightPanel render test with `state.skills` containing 13 personal skills and 0 project skills (filtering by `scopeV2 === "available-project"`) AND `selectedSkill === null` renders the new variant. With ≥1 project skill it renders the "no-selection" copy unchanged.
**File**: `src/eval-ui/src/components/EmptyState.tsx` + `RightPanel.tsx:205-213`.

## Phase 5 — Create-skill flow hardening (US-004)

### T-013: RED — server emits structured 409 payload
**User Story**: US-004 | **AC**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given a skill that already exists, When `POST /api/skills/create` returns 409, Then the JSON body contains `{ code: "skill-already-exists", plugin: "<plugin>", skill: "<name>", error: "..." }`.
**File**: `src/eval-server/__tests__/skill-create-409-payload.test.ts` (new or extend).

### T-014: GREEN — extend 409 payload
**User Story**: US-004 | **AC**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: T-013 passes after editing `skill-create-routes.ts:1202`.
**File**: `src/eval-server/skill-create-routes.ts`.

### T-015: RED — client treats 409 as recoverable navigation
**User Story**: US-004 | **AC**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given `api.createSkill` rejecting with `{ code: "skill-already-exists", plugin, skill }`, When `handleCreate` runs, Then `onCreated(plugin, skill)` is called AND `error` state remains null AND `info` state is set to a non-empty string mentioning "already existed".
**File**: `src/eval-ui/src/hooks/__tests__/useCreateSkill-409.test.ts` (new).

### T-016: GREEN — wire fetchJson 409 path through useCreateSkill
**User Story**: US-004 | **AC**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: T-015 passes. `fetchJson` already throws on non-2xx; we either catch and re-classify in `handleCreate` or expose a 409-aware variant.
**File**: `src/eval-ui/src/hooks/useCreateSkill.ts` + `src/eval-ui/src/api.ts` if needed.

### T-017: RED — RightPanel.onCreated awaits refreshSkills before selecting
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: Given a successful create, When the onCreated handler runs, Then `refreshSkills` resolves BEFORE `selectSkill` fires (assert via mock call ordering with promise sequencing). After selection, the right pane renders the new skill's overview, not the empty state.
**File**: `src/eval-ui/src/components/__tests__/RightPanel-create-flow.test.tsx` (new).

### T-018: GREEN — make onCreated async and await refreshSkills
**User Story**: US-004 | **AC**: AC-US4-01 | **Status**: [x] completed
**Test Plan**: T-017 passes after editing `RightPanel.tsx:194-198`.
**File**: `src/eval-ui/src/components/RightPanel.tsx`.

### T-019: RED+GREEN — double-click guard regression test
**User Story**: US-004 | **AC**: AC-US4-03 | **Status**: [x] completed
**Test Plan**: Given the Create button rendered with `creating === false`, When two `click` events fire within 10 ms, Then `api.createSkill` is invoked exactly once.
**File**: extend `useCreateSkill` test suite or component test.

## Phase 6 — GitHub bootstrap hint (US-005)

### T-022: RED — github-status endpoint returns the three-status contract
**User Story**: US-005 | **AC**: AC-US5-01 | **Status**: [x] completed
**Test Plan**: Three table-driven cases — (a) project with no `.git` → `{ hasGit: false, githubOrigin: null, status: "no-git" }`; (b) project with `.git` and `origin = git@github.com:foo/bar.git` → `{ hasGit: true, githubOrigin: "https://github.com/foo/bar", status: "github" }`; (c) project with `.git` but origin = gitlab.com → `{ ..., status: "non-github" }`.
**File**: `src/eval-server/__tests__/api-project-github-status.test.ts` (new).

### T-023: GREEN — implement /api/project/github-status
**User Story**: US-005 | **AC**: AC-US5-01 | **Status**: [x] completed
**Test Plan**: T-022 passes. Reuses `parseGithubRemote` + the parent-walking `.git` locator already in api-routes.ts.
**File**: `src/eval-server/api-routes.ts`.

### T-024: RED — PublishStatusRow renders correct content per status
**User Story**: US-005 | **AC**: AC-US5-02, AC-US5-04 | **Status**: [x] completed
**Test Plan**: Three render cases mirroring server statuses. `github` renders a green "Publish-ready" badge AND the PublishButton. `non-github` renders an amber badge + the `gh remote add origin ...` line + Copy button. `no-git` renders an amber badge + a code block with `gh repo create <basename> --public --source=. --remote=origin --push` + Copy button.
**File**: `src/eval-ui/src/components/__tests__/PublishStatusRow.test.tsx` (new).

### T-025: GREEN — implement PublishStatusRow + Copy + SWR hook
**User Story**: US-005 | **AC**: AC-US5-02, AC-US5-03, AC-US5-05 | **Status**: [x] completed
**Test Plan**: T-024 passes. Clicking Copy invokes `navigator.clipboard.writeText` with the displayed command. SWR cache key `project-github-status` is shared (one fetch hydrates the row). Editor's PublishButton is untouched (`AC-US5-04`).
**File**: `src/eval-ui/src/components/PublishStatusRow.tsx` (new) + `src/eval-ui/src/components/SkillOverview.tsx` (mount the row) + `src/eval-ui/src/hooks/useGitHubStatus.ts` (new SWR hook).

## Phase 7 — Sidebar GitHub-not-connected indicator (US-006)

### T-026: RED — sidebar Project section header shows cloud-off icon when status≠github
**User Story**: US-006 | **AC**: AC-US6-01, AC-US6-02 | **Status**: [x] completed
**Test Plan**: Given `useGitHubStatus()` returns `status: "no-git"`, When the Sidebar renders, Then the AVAILABLE > PROJECT NamedScopeSection header has a `data-testid="sidebar-github-not-connected"` icon with role/aria-label. Given `status: "github"`, the icon is NOT in the DOM.
**File**: `src/eval-ui/src/components/__tests__/Sidebar-github-indicator.test.tsx` (new).

### T-027: GREEN — implement sidebar indicator slot + click handler
**User Story**: US-006 | **AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04 | **Status**: [x] completed
**Test Plan**: T-026 passes. Click handler test: clicking the icon when a skill is selected dispatches a custom event (or sets `activeDetailTab='overview'`) AND attempts a scrollIntoView on the row ref (mock the ref). Tooltip test: hovering shows a `title` containing "gh repo create".
**File**: `src/eval-ui/src/components/Sidebar.tsx` + `src/eval-ui/src/components/NamedScopeSection.tsx` (extend to accept a header right-slot).

### T-028: RED+GREEN — dismiss persists across sidebar + overview row
**User Story**: US-005, US-006 | **AC**: AC-US6-05 | **Status**: [x] completed
**Test Plan**: Given the dismiss button on the Overview row clicked, When the localStorage key `vskill-github-hint-dismissed-<projectRoot>` is set, Then the sidebar icon is removed on next render. Given the localStorage key set on initial mount, Then the icon is never rendered.
**File**: extend the two suites above + a small shared util `getDismissedProjects()` if reuse is cleaner.

## Phase 8 — Verify

### T-020: Run full vitest sweep on touched files
**User Story**: cross-cutting | **Status**: [x] completed
**Test Plan**: `npx vitest run src/__tests__/first-run-onboarding-* src/eval-server/__tests__/api-agents-plugin-count.test.ts src/eval-server/__tests__/skill-create-409-payload.test.ts src/eval-ui/src/components/__tests__/AgentScopePicker* src/eval-ui/src/components/__tests__/EmptyState-empty-project.test.tsx src/eval-ui/src/components/__tests__/RightPanel-create-flow.test.tsx src/eval-ui/src/hooks/__tests__/useCreateSkill-409.test.ts` — all green.

### T-021: Sync living docs
**User Story**: cross-cutting | **Status**: [x] completed
**Test Plan**: `specweave sync-living-docs 0772-studio-first-launch-onboarding-polish` exits 0 and produces / updates the spec under `.specweave/docs/internal/specs/`.
