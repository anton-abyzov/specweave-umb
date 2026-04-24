---
increment: 0707-studio-detail-view-redesign-and-easychamp-mcp
title: Skill Studio detail view redesign + MCP showcase + EasyChamp MCP server
type: feature
priority: P1
status: completed
created: 2026-04-24T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio detail view redesign + MCP showcase + EasyChamp MCP server

## Context

The local Skill Studio at `localhost:3162` (served by `vskill/src/eval-server/` using `vskill/src/eval-ui/`) has a UX flaw that hides the main interactions. The Editor / Tests / Run / Activation / History / Leaderboard / Deps tabs are rendered **inside** the Overview tab, after 6 stacked metadata cards, so users must scroll past a tall metadata panel to reach the actions they care about. On top of that, four backend endpoints return 404/502 for perfectly legitimate fixture skills: `/versions` (502 because of an unguarded `execSync("git log ...")`), `/benchmark/latest` (404 due to a router pattern mismatch for plugin slugs with dashes), `/evals` (404 when `evals.yaml` is missing rather than a friendlier empty payload), and `/activation-history` (404 when the history log doesn't exist yet). The Deps tab ships with MCP-dependency rendering, but no fixture skill ever declares an MCP dependency — so the feature is effectively untested in the happy path.

This increment fixes all of the above and ships a real, usable custom MCP — **EasyChamp MCP** — with tools for generating a league, tournament, bracket, schedule, and entering results, authenticated against the EasyChamp platform. The MCP doubles as the real dependency declared by a new showcase fixture skill, so the Deps tab renders an end-to-end example the user can copy into their own Claude config.

## Success Criteria

1. All 9 tabs (Overview..Versions) visible in one flat tab bar on 1440×900 viewport, reachable without scrolling past a header.
2. `/versions`, `/benchmark/latest`, `/evals`, `/activation-history` return 200 with consistent `{data, exists, count}` envelopes for all fixture skills including non-git and dash-slug cases.
3. Benchmark card explains the methodology via an ℹ popover and links to the Tests and Run tabs.
4. Author and source file links are clickable when the skill has a `repoUrl` (open GitHub in new tab) and copy-only when local.
5. Version badge appears in the detail header, sidebar list items, tab area, test-run cards, and activation log.
6. The `easychamp/tournament-manager` fixture renders in the Deps tab with a working "Copy config" action that emits a valid `claude_ai/config.json` snippet.
7. `easychamp-mcp-demo` builds and its 5 tools (generate_league, generate_tournament, generate_bracket, create_schedule, enter_results) respond correctly in demo mode. Real EasyChamp API integration is deferred to a follow-up increment tracked against the canonical `easychamp-mcp` package (already published to npm v0.1.0, Stainless-generated from `anton-abyzov/ec-mcp-server`; the real platform authenticates via Keycloak OIDC, not the API-key flow scaffolded here). The demo repo at `repositories/anton-abyzov/easychamp-mcp/` is marked `private: true` in its package.json to prevent accidental npm publication.
8. Responsive: zero overflow regressions at 480 / 768 / 1024 / 1440 breakpoints.

---

## User Stories

### US-001: Studio detail view — flat tab bar + redesigned header (P1)
**Project**: vskill

**As a** Skill Studio user selecting a skill in the left panel
**I want** Editor / Tests / Run / Activation / History / Leaderboard / Deps / Versions to all be reachable in one flat tab bar alongside Overview — without having to scroll past a tall Overview panel
**So that** I can jump straight to the action I care about and see the skill's most important metadata above the fold

**Acceptance Criteria**:
- [x] **AC-US1-01**: `RightPanel.tsx` renders exactly 9 top-level tabs (Overview, Editor, Tests, Run, Activation, History, Leaderboard, Deps, Versions) driven by the existing `PanelId` union — `SkillWorkspaceInner` is no longer mounted inside Overview.
- [x] **AC-US1-02**: On a 1440×900 viewport, all 9 tab buttons are visible in a single horizontal bar without horizontal scrolling (`TabBar.tsx` group layout preserved).
- [x] **AC-US1-03**: The URL hash contract (`?panel=tests`) still deep-links directly to that tab — verified by an E2E that visits the URL and asserts the Tests tab is active on load.
- [x] **AC-US1-04**: The new `SkillOverview.tsx` component renders the compact header (skill name, version badge, tier badge if present, install-method chip) and the byline row (author, category, source file link, updated date) as a single sticky block above the metric grid.
- [x] **AC-US1-05**: The redesigned header element shows the version badge as a dedicated inline-flex chip, tabular-nums, `border: 1px solid var(--border)`.

---

### US-002: Overview metric grid + benchmark explanation (P1)
**Project**: vskill

**As a** Skill Studio user on a skill's Overview tab
**I want** the key metrics (benchmark, tests, activations, last run, MCP deps, skill deps, size, last modified) displayed in a sleek responsive grid — with the benchmark's methodology explained and linked to the actual tests/evals that produced it
**So that** I can scan skill health at a glance and understand what a benchmark number actually means

**Acceptance Criteria**:
- [x] **AC-US2-01**: The Overview tab renders an 8-card metric grid using CSS `grid-template-columns: repeat(auto-fit, minmax(180px, 1fr))`, gap `0.75rem`, card interior padding `1rem`.
- [x] **AC-US2-02**: At 1440px viewport the grid shows 4 columns; 1024px shows 3; 768px shows 2; 480px shows 1 — verified by Playwright viewport-resize tests with no content clipping.
- [x] **AC-US2-03**: Each metric card that has a dedicated tab is clickable and navigates to that tab (Benchmark→Run, Tests→Tests, Activations→Activation, MCP deps→Deps, Skill deps→Deps).
- [x] **AC-US2-04**: The benchmark card shows a ℹ trigger that opens a popover reading: "Benchmarks are the aggregated score of this skill's evals (`evals.yaml`) run against its tests (`tests/`). Each test case produces a verdict; the benchmark is the mean pass rate." — with inline links to the Tests and Run tabs.
- [x] **AC-US2-05**: Card text uses `word-break: break-word` + `overflow-wrap: anywhere` so long author names and paths do not overflow the grid at 480px.
- [x] **AC-US2-06**: The `MetricCard.tsx` component is ported into `vskill/src/eval-ui/src/components/MetricCard.tsx` reusing the CSS variables from `globals.css` (dark card bg, uppercase mono labels, large value typography).

---

### US-003: Clickable author + source file link everywhere (P1)
**Project**: vskill

**As a** Skill Studio user reviewing a skill
**I want** the author to be a clickable link to their GitHub profile (when the skill has a repo URL) or a copy-to-clipboard chip (when the skill is local-only), and the source file to be a link that opens the file on GitHub — mirroring the Verified Skill platform portal
**So that** I can vet the author and inspect the source without re-deriving URLs by hand

**Acceptance Criteria**:
- [x] **AC-US3-01**: New `AuthorLink.tsx` component renders an `<a target="_blank" rel="noopener noreferrer">` to `https://github.com/{repoOwner}` when `skill.repoUrl` parses; otherwise renders a `CopyButton` with the author string.
- [x] **AC-US3-02**: New `SourceFileLink.tsx` renders `{repoUrl}/blob/HEAD/{skillPath}` with the `↗` affordance when `repoUrl` is present; otherwise renders a `CopyButton` with the absolute local path.
- [x] **AC-US3-03**: Both components are integrated into `DetailHeader.tsx` so they appear in the sticky header row for every skill.
- [x] **AC-US3-04**: Version badge appears as a reusable `VersionBadge.tsx` component used in at least four places: detail header, sidebar list row (`LeftPanel.tsx`), test-run result cards, and activation log rows. *(0707: detail header, SkillRow sidebar, HistoryPanel row, ActivationPanel activation-log row — four surfaces. TestsPanel per-run card deferred; see reports/studio-frontend-followups.md.)*

---

### US-004: Eval-server endpoint hardening (P1)
**Project**: vskill

**As a** Skill Studio user viewing the Versions tab, Benchmark card, Evals tab, or Activation tab
**I want** each of those views to load real data or a clean empty state — never a 404 or 502 — for any fixture skill including non-git skills and plugins with dashes in their slugs
**So that** the Studio feels complete and never surfaces red errors for normal fixture skills

**Acceptance Criteria**:
- [x] **AC-US4-01**: `GET /api/skills/:plugin/:skill/versions` returns `200 { versions: [], count: 0, source: "none" }` with `X-Skill-VCS: unavailable` header when the skill dir is not inside a git repo or the platform is unreachable (no 502).
- [x] **AC-US4-02**: `GET /api/skills/:plugin/:skill/benchmark/latest` returns `200` (benchmark payload or `null`) for all fixture skills including plugins with dashes (`google-workspace`) — verified by integration test against that slug.
- [x] **AC-US4-03**: `GET /api/skills/:plugin/:skill/evals` returns `200 { exists: false, evals: [] }` when `evals.json` is missing, `422` with validation details when malformed, `200 { exists: true, ...EvalsFile }` when valid.
- [x] **AC-US4-04**: `GET /api/skills/:plugin/:skill/activation-history` returns `200 { runs: [], count: 0 }` when the history log doesn't exist, `200 { runs: [...], count }` when it does.
- [x] **AC-US4-05**: All four endpoints follow a consistent envelope shape reflected in `vskill/src/eval-ui/src/api.ts` type annotations (`SkillVersionsEnvelope`, `SkillEvalsEnvelope`, `ActivationHistoryEnvelope`, `BenchmarkLatestEnvelope`).
- [x] **AC-US4-06**: Router pattern (`vskill/src/eval-server/router.ts`) correctly matches plugin slugs containing dashes for all four endpoints — verified by test cases using `google-workspace/gws`.

---

### US-005: EasyChamp MCP showcase fixture skill (P1)
**Project**: vskill

**As a** Skill Studio user who wants to see a real MCP dependency in action
**I want** a fixture skill that declares an MCP dependency and renders it in the Deps tab — with a "Copy config" button that emits a valid Claude config snippet
**So that** the MCP showcase in the Deps tab is not hypothetical — I can copy the snippet into my own Claude setup and run the skill

**Acceptance Criteria**:
- [x] **AC-US5-01**: `vskill/plugins/easychamp/skills/tournament-manager/SKILL.md` exists with a frontmatter block declaring `mcp-deps: [easychamp]`, version `0.1.0`, author `Anton Abyzov`, homepage `https://easychamp.com`, and a body that references the `easychamp_generate_league`, `easychamp_generate_tournament`, `easychamp_generate_bracket`, `easychamp_create_schedule`, and `easychamp_enter_results` tools.
- [x] **AC-US5-02**: `vskill/src/eval/mcp-detector.ts` MCP Registry contains an EasyChamp entry with `prefixes: ["easychamp_"]`, `url: "https://easychamp.com/mcp"`, `transport: "stdio"`, and a `configSnippet` that wires `npx -y easychamp-mcp` with the `EASYCHAMP_API_KEY` env var.
- [x] **AC-US5-03**: Opening the new fixture skill and clicking the Deps tab shows "EasyChamp" under MCP Servers with the `easychamp_*` tool list and a working Copy config button — verified by an E2E.
- [x] **AC-US5-04**: The copied JSON snippet parses as valid JSON and matches the shape `{ "easychamp": { "command": "npx", "args": ["-y", "easychamp-mcp"], "env": { "EASYCHAMP_API_KEY": "${EASYCHAMP_API_KEY}" } } }`.
- [x] **AC-US5-05**: Unit test for `mcp-detector.ts`: given a SKILL.md that uses `easychamp_generate_league`, the detector returns `EasyChamp` in `mcpDependencies`.

---

### US-006: EasyChamp MCP server — demo fixture for the Deps tab (P1)
**Project**: easychamp-mcp

**As a** Skill Studio user clicking the Deps tab on the `easychamp/tournament-manager` fixture skill
**I want** the declared `easychamp` MCP dependency to resolve to a working local demo server (5 tools with Zod schemas, stdio transport, demo mode)
**So that** the Deps-tab showcase is concrete and demonstrable end-to-end — not hypothetical — while the canonical `easychamp-mcp` (already on npm v0.1.0, Keycloak OIDC auth) continues to evolve independently.

> **Scope note (post-verification):** The repo built by this workstream is marked `private: true` with the package name `easychamp-mcp-demo`. It is NOT the canonical MCP that end users install from npm. Real EasyChamp API integration (Keycloak OIDC) is tracked against the canonical `easychamp-mcp` package owned by the EasyChamp platform team and is explicitly out of scope for 0707.

**Acceptance Criteria**:
- [x] **AC-US6-01**: New repo `repositories/anton-abyzov/easychamp-mcp/` scaffolded with `package.json` (now named `easychamp-mcp-demo` + `private: true` per verification — canonical `easychamp-mcp` is already on npm v0.1.0 from `anton-abyzov/ec-mcp-server`), `tsconfig.json`, `src/`, `test/`, `README.md`. *(32/32 unit + integration tests green; `npm pack --dry-run` clean.)*
- [x] **AC-US6-02**: Five tools implemented as separate files under `src/tools/` with Zod input schemas: `generate_league({ name, sport, teamCount, format })`, `generate_tournament({ leagueId, type })`, `generate_bracket({ tournamentId })`, `create_schedule({ tournamentId, startDate, venues? })`, `enter_results({ matchId, homeScore, awayScore, winner })`.
- [x] **AC-US6-03**: Stdio transport entry point `src/index.ts` boots the MCP server via `@modelcontextprotocol/sdk/server/stdio` with a shebang line so it can run as `npx -y easychamp-mcp-demo` (demo-only binary; real MCP remains `npx -y easychamp-mcp`).
- [x] **AC-US6-04**: Auth scaffold: `EASYCHAMP_API_KEY` env var sent as `Authorization: Bearer {key}` to `EASYCHAMP_API_URL` (default `https://api.easychamp.com/v1`). No API key logging. *(Real EasyChamp platform uses Keycloak OIDC, not API-key — this scaffold is deferred and not wired to the canonical MCP.)*
- [x] **AC-US6-05**: Demo mode — if `EASYCHAMP_DEMO=1` and no API key present, tools return mock responses from `src/mocks/demo-responses.ts` matching the declared Zod output schemas.
- [x] **AC-US6-06**: Missing key + no demo mode — each tool returns a structured error with a link to `https://easychamp.com/account/api-keys`; no unhandled exceptions.
- [x] **AC-US6-07**: Unit tests (Vitest) for every tool cover happy path, missing-auth error, and demo-mode response shape; integration test boots the server in a child process, sends `ListTools` + `CallTool`, asserts responses. *(32/32 tests pass.)*
- [x] **AC-US6-08**: README documents the demo binary install (`npx -y easychamp-mcp-demo` for local dev; end users should install the canonical `easychamp-mcp` from npm), env var setup, and each tool with example calls. README explicitly calls out the demo-vs-canonical distinction.
- [x] **AC-US6-09**: `npm run build && npm test` both pass; `npm pack --dry-run` clean. No publish step in this increment (demo is `private: true`).

---

## Functional Requirements

### FR-001: Flat top-level tab bar
Replace the `Overview | Versions` 2-tab layout in `RightPanel.tsx` with a flat 9-tab layout. Overview mounts `SkillOverview.tsx`; other tabs mount what `SkillWorkspaceInner` currently delegates to.

### FR-002: Empty-state-first API envelopes
Every one of the 4 endpoints must prefer a 200 with an empty envelope over a 404/500 when the "cause" is simply that the fixture skill doesn't carry that artifact yet (no git, no benchmark, no evals.yaml, no activation-history log).

### FR-003: MCP Registry extensibility
The EasyChamp entry must be the second entry pattern beyond the existing 9 registry entries in `mcp-detector.ts`, following the same shape so future custom MCPs can be added the same way.

## Non-Functional Requirements

- **Accessibility**: All interactive elements keyboard-navigable (tab, enter). External links use `rel="noopener noreferrer"`. Popovers are dismissible with Escape.
- **Performance**: Overview tab initial render ≤100ms on a 50-skill fixtures workspace. Endpoint P95 latency ≤50ms for empty envelopes. EasyChamp MCP demo-mode tool latency ≤200ms.
- **Security**: `EASYCHAMP_API_KEY` never logged, never returned in tool responses, never written to disk, never committed. Copy-config snippet uses `${EASYCHAMP_API_KEY}` placeholder — no real values in UI-generated JSON.
- **Responsiveness**: Tested at 480 / 768 / 1024 / 1440 breakpoints; no card overflow; long author strings and file paths wrap gracefully.
- **Test coverage**: Unit ≥90%, integration ≥85%, E2E covers every US.
- **No Tailwind**: Must reuse existing CSS variables in `globals.css` and Geist fonts. Zero new icon libraries — Unicode symbols and inline SVG only.

## Out of Scope

- Actually publishing `easychamp-mcp` to npm (build + pack only in this increment).
- OAuth device-code flow for EasyChamp MCP (API-key only for v0.1.0; OAuth scaffold present but disabled).
- Deploying the EasyChamp backend API — this increment assumes the API exists or demo mode suffices.
- Leaderboard tab redesign — the user did not request it, and the existing Leaderboard still works.
- Migrating any other consumers of the deprecated `MetadataTab.tsx` (none expected — it's only used by `RightPanel`).

## Dependencies

- `@modelcontextprotocol/sdk` (npm) — EasyChamp MCP.
- `zod` (npm) — EasyChamp MCP tool input validation.
- Existing CSS variables in `vskill-platform/src/app/globals.css` and Skill Studio equivalents — design tokens.
- Existing components: `TabBar.tsx`, `DetailHeader.tsx`, `RightPanel.tsx`, `MetadataTab.tsx`, `TabGroup.tsx`, `MetricCard.tsx`, `CopyButton.tsx`, `RepoLink.tsx`, `PublisherLink.tsx`.
- Existing eval-server routes in `vskill/src/eval-server/api-routes.ts` (lines 1338, 1661, 2397, 2540).
