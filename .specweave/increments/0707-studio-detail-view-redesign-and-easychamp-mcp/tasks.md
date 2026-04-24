# Tasks — 0707 Skill Studio Detail View Redesign + EasyChamp MCP

## Task Notation

- `[T-NN]` task ID · `[P]` parallelizable · `[ ]` / `[x]` status · `**Satisfies ACs**:` AC-ID linkage · `**Owner**:` agent · `**Test Plan**:` BDD Given/When/Then

Tasks are partitioned by agent. All tasks across agents can run in parallel — file ownership is disjoint.

---

## Workstream A — studio-frontend (vskill/src/eval-ui/)

### T-001: Port MetricCard into eval-ui
**Satisfies ACs**: AC-US2-06 · **Owner**: studio-frontend · **Status**: [x] completed

Copy `vskill-platform/src/app/components/MetricCard.tsx` to `vskill/src/eval-ui/src/components/MetricCard.tsx`. Preserve CSS-variable usage. No new props beyond the existing ones.

**Test Plan**:
- Given the ported MetricCard is rendered with `{ label: "Tests", value: "12", onClick: fn }`
- When the card is clicked
- Then `onClick` is invoked exactly once and the card has role="button" + tabIndex=0

---

### T-002: VersionBadge component
**Satisfies ACs**: AC-US1-05, AC-US3-04 · **Owner**: studio-frontend · **Status**: [x] completed

Create `vskill/src/eval-ui/src/components/VersionBadge.tsx` — inline-flex chip, tabular-nums, `1px solid var(--border)`, `var(--bg-subtle)` bg, `0.75rem` font.

**Test Plan**:
- Given `<VersionBadge version="1.2.3" />`
- When rendered
- Then the text "v1.2.3" is visible with `font-variant-numeric: tabular-nums` and border style matches the design token

---

### T-003: AuthorLink component
**Satisfies ACs**: AC-US3-01 · **Owner**: studio-frontend · **Status**: [x] completed

Create `vskill/src/eval-ui/src/components/AuthorLink.tsx`. Parse `skill.repoUrl` to extract owner; render `<a href="https://github.com/{owner}" target="_blank" rel="noopener noreferrer">` when parseable; else render `<CopyButton value={author} />`.

**Test Plan**:
- Given a skill with `author="Anton Abyzov"` and `repoUrl="https://github.com/anton-abyzov/vskill"`
- When AuthorLink is rendered
- Then the anchor has `href="https://github.com/anton-abyzov"` and `target="_blank"` and `rel="noopener noreferrer"`
- Given a skill with `author="Anton"` and no repoUrl
- When AuthorLink is rendered
- Then a CopyButton with `value="Anton"` is rendered and no anchor is present

---

### T-004: SourceFileLink component
**Satisfies ACs**: AC-US3-02 · **Owner**: studio-frontend · **Status**: [x] completed

Create `vskill/src/eval-ui/src/components/SourceFileLink.tsx`. Strip any existing `/tree/...` or `/blob/...` suffix from `repoUrl`, then append `/blob/HEAD/{skillPath}`. Render as `<a>` with `↗` Unicode. When `repoUrl` absent, render `<CopyButton value={absolutePath} />`.

**Test Plan**:
- Given `repoUrl="https://github.com/anton-abyzov/vskill/tree/main"` and `skillPath="plugins/easychamp/skills/tournament-manager"`
- When SourceFileLink renders
- Then href is `https://github.com/anton-abyzov/vskill/blob/HEAD/plugins/easychamp/skills/tournament-manager` and text ends with `↗`

---

### T-005: BenchmarkInfoPopover component
**Satisfies ACs**: AC-US2-04 · **Owner**: studio-frontend · **Status**: [x] completed

Create `vskill/src/eval-ui/src/components/BenchmarkInfoPopover.tsx`. Trigger is an ℹ button; popover shows the explanation text with inline Tests/Run tab-navigation links. Escape dismisses.

**Test Plan**:
- Given the popover is rendered
- When the ℹ button is clicked
- Then the explanation text is visible AND clicking "Tests" inside the popover navigates to the Tests tab

---

### T-006: SkillOverview component (the compact metric grid)
**Satisfies ACs**: AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05 · **Owner**: studio-frontend · **Status**: [x] completed

Create `vskill/src/eval-ui/src/components/SkillOverview.tsx`. Layout: sticky header (skill name, VersionBadge, TierBadge, install-method chip, byline with AuthorLink + SourceFileLink + category + date) followed by the 8-card responsive metric grid (Benchmark, Tests, Activations, Last run, MCP deps, Skill deps, Size, Last modified). CSS `grid-template-columns: repeat(auto-fit, minmax(180px, 1fr))`, gap `0.75rem`. Cards are clickable when they have a corresponding tab.

**Test Plan**:
- Given a skill with 3 test cases, 5 activations, a passing benchmark, 1 MCP dep, 2 skill deps
- When SkillOverview renders
- Then 8 cards are visible in the grid and the Tests card shows "3" and clicking it fires the tab-navigation callback with `"tests"`

---

### T-007: Refactor RightPanel to flat 9-tab layout
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 · **Owner**: studio-frontend · **Status**: [x] completed

Modify `vskill/src/eval-ui/src/components/RightPanel.tsx`: replace the 2-tab (`Overview|Versions`) structure with a 9-tab TabBar (`Overview|Editor|Tests|Run|Activation|History|Leaderboard|Deps|Versions`) driven by `PanelId`. Remove the nested `SkillWorkspaceInner` mount; instead, each tab renders its delegated component directly. Preserve URL hash handling (`?panel=tests`) by hoisting the `useHashPanel` hook to this level.

**Test Plan**:
- Given RightPanel renders with a selected skill
- When the user clicks the "Tests" tab
- Then the Tests component mounts AND the URL hash updates to `#/skills/.../tests` (or equivalent)
- Given the page loads with `?panel=activation` in the URL
- When RightPanel mounts
- Then the Activation tab is active by default

---

### T-008: Integrate redesigned header in DetailHeader
**Satisfies ACs**: AC-US3-03 · **Owner**: studio-frontend · **Status**: [x] completed

Modify `vskill/src/eval-ui/src/components/DetailHeader.tsx` to slot in `<VersionBadge />`, `<AuthorLink />`, `<SourceFileLink />`. Remove the current plain-text version and author rendering.

**Test Plan**:
- Given DetailHeader renders for a skill with repoUrl and version
- When rendered
- Then VersionBadge + AuthorLink (anchor) + SourceFileLink are all present; the old plain version text is gone

---

### T-009: Version badges in sidebar + test runs + activation log
**Satisfies ACs**: AC-US3-04 · **Owner**: studio-frontend · **Status**: [x] completed

Add `<VersionBadge />` to: (a) sidebar skill rows in `LeftPanel.tsx`, (b) each test-run result card in `TestsTab`, (c) each activation-log row in `ActivationTab` / `HistoryTab`.

**Test Plan**:
- Given the sidebar lists 3 skills with versions "1.0.0", "2.1.3", "0.1.0"
- When LeftPanel renders
- Then each row shows its matching VersionBadge

---

### T-010: api.ts type annotations for new envelopes
**Satisfies ACs**: AC-US4-05 · **Owner**: studio-frontend · **Status**: [x] completed

Update type annotations in `vskill/src/eval-ui/src/api.ts` to match the new `{data, exists, count}` envelope shapes for versions, evals, activation-history. Adjust `getSkillVersions`, `getSkillEvals`, `getActivationHistory` return types.

**Test Plan**: TypeScript compile must succeed after backend agent B ships the new envelopes.

---

### T-011: E2E — tabs visible without scrolling at 1440x900
**Satisfies ACs**: AC-US1-02 · **Owner**: studio-frontend · **Status**: [x] completed

Playwright test `e2e/studio-detail-tabs.spec.ts`: open a skill, assert all 9 tab buttons have `getBoundingClientRect().bottom < window.innerHeight` at 1440x900.

---

### T-012: E2E — responsive breakpoints
**Satisfies ACs**: AC-US2-02 · **Owner**: studio-frontend · **Status**: [x] completed

Playwright test: for viewports 480, 768, 1024, 1440, render overview and assert no metric card `scrollWidth > clientWidth`.

---

## Workstream B — studio-backend (vskill/src/eval-server/)

### T-020: Router pattern audit + fix for dash-containing slugs
**Satisfies ACs**: AC-US4-06 · **Owner**: studio-backend · **Status**: [x] completed

Audit `vskill/src/eval-server/router.ts` for `:plugin` / `:skill` param extraction. Ensure pattern uses `[^/]+` (not `\w+`). Add test.

**Test Plan**:
- Given routes registered for `/api/skills/:plugin/:skill/*`
- When a request to `/api/skills/google-workspace/gws/versions` arrives
- Then `req.params.plugin === "google-workspace"` and `req.params.skill === "gws"`

---

### T-021: Harden /versions — git-safe fallback
**Satisfies ACs**: AC-US4-01 · **Owner**: studio-backend · **Status**: [x] completed

Modify the `/versions` handler (around line 1338 of `api-routes.ts`). Wrap `execSync("git log ...")` in try/catch; on failure return `200 { versions: [], count: 0, source: "none" }` with `X-Skill-VCS: unavailable` header.

**Test Plan**:
- Given a skill dir NOT inside a git repo
- When GET `/api/skills/plugin/skill/versions` is called
- Then status is 200, body is `{ versions: [], count: 0, source: "none" }`, response header `X-Skill-VCS: unavailable` is present

---

### T-022: Harden /benchmark/latest — 200 null default
**Satisfies ACs**: AC-US4-02 · **Owner**: studio-backend · **Status**: [x] completed

Ensure `/benchmark/latest` handler (line ~2397) returns `200 null` when no benchmark exists. Wrap file-not-found in graceful fallback. Confirm dash-slug plugins reach the handler (depends on T-020).

**Test Plan**:
- Given `google-workspace/gws` has no benchmark record
- When GET `/api/skills/google-workspace/gws/benchmark/latest` is called
- Then status is 200 and body is `null`

---

### T-023: Harden /evals — distinguish missing vs malformed
**Satisfies ACs**: AC-US4-03 · **Owner**: studio-backend · **Status**: [x] completed

Modify the `/evals` handler (line ~1661). Detect missing `evals.yaml` → `200 { tasks: [], exists: false }`. Detect malformed YAML or schema-validation error → `422 { error: details }`. Valid → `200 { tasks, exists: true }`.

**Test Plan**:
- Given a skill without `evals.yaml`
- When GET `/evals` is called
- Then status 200 and body `{ tasks: [], exists: false }`
- Given a skill with a malformed `evals.yaml`
- When GET `/evals` is called
- Then status 422 with validation details
- Given a skill with a valid `evals.yaml` containing 3 tasks
- When GET `/evals` is called
- Then status 200 and `tasks.length === 3` and `exists === true`

---

### T-024: Harden /activation-history — 200 empty for never-activated
**Satisfies ACs**: AC-US4-04 · **Owner**: studio-backend · **Status**: [x] completed

Modify the `/activation-history` handler (line ~2540). When the log file doesn't exist, return `200 { runs: [], count: 0 }`. Preserve 500 only for actual I/O errors (non-ENOENT).

**Test Plan**:
- Given a skill that has never been activated (no history log)
- When GET `/activation-history` is called
- Then status 200 and body `{ runs: [], count: 0 }`

---

### T-025: Envelope consistency sweep + api.ts type handoff
**Satisfies ACs**: AC-US4-05 · **Owner**: studio-backend · **Status**: [x] completed

Review all 4 endpoints to ensure envelope shape consistency. Document the envelope shape in a short comment block at the top of each handler so the frontend agent can cross-reference when updating `api.ts`.

---

### T-026: Integration tests for non-git fixture skills
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 · **Owner**: studio-backend · **Status**: [x] completed

Vitest integration suite at `vskill/src/eval-server/__tests__/fixture-endpoints.test.ts`. Uses a tmp dir fixture skill NOT inside a git repo; exercises all 4 endpoints and asserts the happy-empty envelopes.

---

## Workstream C — studio-fixture (plugins + mcp-detector)

### T-030: Scaffold easychamp/tournament-manager fixture
**Satisfies ACs**: AC-US5-01 · **Owner**: studio-fixture · **Status**: [x] completed

Create `vskill/plugins/easychamp/skills/tournament-manager/` with:
- `SKILL.md` — frontmatter with `mcp-deps: [easychamp]`, version `0.1.0`, author `Anton Abyzov`, homepage `https://easychamp.com`, tags. Body uses `easychamp_generate_league`, `easychamp_generate_tournament`, `easychamp_generate_bracket`, `easychamp_create_schedule`, `easychamp_enter_results`.
- `references/schemas.md` — tool input/output schemas reference.
- `evals/evals.yaml` — 5 smoke tasks, one per tool, runnable in demo mode.

**Test Plan**:
- Given the fixture exists
- When the Skill Studio lists skills
- Then `easychamp/tournament-manager` appears in the sidebar with version `0.1.0`

---

### T-031: Register EasyChamp in MCP Registry
**Satisfies ACs**: AC-US5-02 · **Owner**: studio-fixture · **Status**: [x] completed

Add EasyChamp entry to the registry in `vskill/src/eval/mcp-detector.ts` (lines 25-80). Shape matches the existing entries with `prefixes: ["easychamp_"]`, `url`, `transport: "stdio"`, `configSnippet` wiring `npx -y easychamp-mcp` + `EASYCHAMP_API_KEY`.

**Test Plan**:
- Given a SKILL.md that uses `easychamp_generate_league`
- When `detectMcpDependencies(content)` runs
- Then `EasyChamp` is in the returned dependency list with the correct configSnippet

---

### T-032: Unit test — detector picks up easychamp_ prefix
**Satisfies ACs**: AC-US5-05 · **Owner**: studio-fixture · **Status**: [x] completed

Extend `vskill/src/eval/mcp-detector.test.ts` with a case that uses `easychamp_generate_league` in the body; assert `EasyChamp` is detected.

---

### T-033: E2E — Deps tab shows EasyChamp with Copy config
**Satisfies ACs**: AC-US5-03, AC-US5-04 · **Owner**: studio-fixture · **Status**: [x] completed

Playwright test: navigate to `easychamp/tournament-manager`, open Deps tab, assert EasyChamp row + tools list visible, click Copy config, read clipboard, parse JSON, assert shape matches spec.

---

## Workstream D — easychamp-mcp (new repo)

### T-040: Scaffold repo + package.json
**Satisfies ACs**: AC-US6-01 · **Owner**: easychamp-mcp · **Status**: [x] completed

Initialize `repositories/anton-abyzov/easychamp-mcp/` with `package.json` (name `easychamp-mcp`, `bin` pointing to `dist/index.js`, dependencies: `@modelcontextprotocol/sdk`, `zod`, `undici`; devDeps: `typescript`, `vitest`, `@types/node`), `tsconfig.json` (ESM, `moduleResolution: nodenext`, `outDir: dist`), `.gitignore`, `.env.example`.

**Test Plan**: `npm install && npm run build` succeeds.

---

### T-041: Stdio entry + server.ts tool registration
**Satisfies ACs**: AC-US6-03 · **Owner**: easychamp-mcp · **Status**: [x] completed

Create `src/index.ts` with shebang (`#!/usr/bin/env node`) and stdio boot. `src/server.ts` registers all 5 tools with the `McpServer` from `@modelcontextprotocol/sdk`.

**Test Plan**:
- Given the built binary is launched in a child process
- When an MCP `ListTools` request is sent over stdio
- Then the response lists all 5 tools with their input schemas

---

### T-042: generate_league tool
**Satisfies ACs**: AC-US6-02, AC-US6-05, AC-US6-06 · **Owner**: easychamp-mcp · **Status**: [x] completed

Create `src/tools/generate-league.ts` with Zod input schema `{ name, sport, teamCount, format }`, mode routing (live/demo/no-auth), structured error for no-auth case.

**Test Plan**:
- Given `EASYCHAMP_DEMO=1` and no API key
- When `generate_league({ name: "Summer League", sport: "basketball", teamCount: 8, format: "single_elim" })` is called
- Then the response shape matches `{ leagueId, name, sport, teams: string[] }` with `teams.length === 8`
- Given no API key and no demo
- When the tool is called
- Then the response is a structured error including the `https://easychamp.com/account/api-keys` link

---

### T-043: generate_tournament tool
**Satisfies ACs**: AC-US6-02, AC-US6-05, AC-US6-06 · **Owner**: easychamp-mcp · **Status**: [x] completed

Same pattern as T-042 for `generate_tournament({ leagueId, type })`.

**Test Plan**: analogous to T-042.

---

### T-044: generate_bracket tool
**Satisfies ACs**: AC-US6-02, AC-US6-05, AC-US6-06 · **Owner**: easychamp-mcp · **Status**: [x] completed

Same pattern for `generate_bracket({ tournamentId })`. Returns `{ bracketId, rounds: Match[] }`.

**Test Plan**: demo-mode returns a bracket with rounds matching the tournament size.

---

### T-045: create_schedule tool
**Satisfies ACs**: AC-US6-02, AC-US6-05, AC-US6-06 · **Owner**: easychamp-mcp · **Status**: [x] completed

Same pattern for `create_schedule({ tournamentId, startDate, venues? })`. Returns `{ scheduleId, matches: ScheduledMatch[] }`.

**Test Plan**: demo-mode returns matches starting at `startDate`.

---

### T-046: enter_results tool
**Satisfies ACs**: AC-US6-02, AC-US6-05, AC-US6-06 · **Owner**: easychamp-mcp · **Status**: [x] completed

Same pattern for `enter_results({ matchId, homeScore, awayScore, winner })`. Returns `{ matchId, finalized: true }`.

**Test Plan**: demo-mode echoes the inputs in the response.

---

### T-047: auth module + easychamp-client
**Satisfies ACs**: AC-US6-04 · **Owner**: easychamp-mcp · **Status**: [x] completed

Create `src/auth/api-key.ts` reading `EASYCHAMP_API_KEY`; `src/client/easychamp-client.ts` using undici `fetch` with `Authorization: Bearer {key}` and 5s timeout.

**Test Plan**:
- Given `EASYCHAMP_API_KEY=test` is set
- When the client makes a request
- Then the `Authorization` header is `Bearer test`
- Given no API key
- When `apiKey()` is called
- Then it returns `{ missing: true }` — no exception

---

### T-048: Integration test — stdio MCP protocol end-to-end
**Satisfies ACs**: AC-US6-07 · **Owner**: easychamp-mcp · **Status**: [x] completed

`test/server.test.ts`: spawn the server binary as a child process (`EASYCHAMP_DEMO=1`), exchange `ListTools` + `CallTool(generate_league, ...)`, assert the responses.

---

### T-049: README + .env.example
**Satisfies ACs**: AC-US6-08 · **Owner**: easychamp-mcp · **Status**: [x] completed

README documents install (`claude mcp add easychamp` / `npx -y easychamp-mcp`), env setup (`EASYCHAMP_API_KEY`, `EASYCHAMP_API_URL`, `EASYCHAMP_DEMO`), and each tool with example inputs/outputs.

---

### T-050: GitHub Actions CI workflow
**Satisfies ACs**: AC-US6-09 · **Owner**: easychamp-mcp · **Status**: [x] completed

`.github/workflows/test.yml`: Node 20, `npm ci`, `npm test`, `npm run build`.

---

## Closure (team-lead, after all 4 agents COMPLETION)

### T-100: Closure via sw-closer subagent
**Owner**: team-lead → sw-closer

Run `sw:done` on increment 0707: code-review loop, simplify, grill, judge-llm, PM 3-gate validation, sync to GitHub/JIRA/ADO if configured, set status to completed.

---

## Summary

- Workstream A (studio-frontend): 12 tasks (T-001..T-012)
- Workstream B (studio-backend): 7 tasks (T-020..T-026)
- Workstream C (studio-fixture): 4 tasks (T-030..T-033)
- Workstream D (easychamp-mcp): 11 tasks (T-040..T-050)
- Closure: 1 task (T-100)

**Total: 35 tasks across 4 parallel agents — max 12 per agent (under 40-task cap).**
