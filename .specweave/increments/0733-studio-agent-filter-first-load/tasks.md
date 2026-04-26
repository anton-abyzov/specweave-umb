# Tasks: Studio: agent filter must apply on first load

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started — `[x]`: Completed
- TDD strict: every implementation task has a paired RED-test task that must fail before implementation lands.

## Phase 1 — RED (write failing tests first)

### T-001: RED — server filter parity test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x]
**File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-skills-route.test.ts` (NEW)
**Test Plan (BDD)**:
- **Given** a fixture workspace root with skills owned by `claude-code`, `aider`, `cursor` (mixed `own`/`installed` scopes), and the eval-server router mounted with that root, and the AGENTS_REGISTRY default resolution returns `claude-code`
- **When** the test issues `GET /api/skills` with NO query params AND `GET /api/skills?agent=claude-code`
- **Then** the two responses are deeply equal AND every row in the no-param response satisfies `scope === "own" || sourceAgent === "claude-code"`
- **Then** `GET /api/skills?agent=cursor` returns only rows where `sourceAgent === "cursor"` (plus `own`-scope rows) — regression guard for AC-US2-03
- **Then** `GET /api/skills?scope=garbage` returns `[]` — regression guard for AC-US2-04
**Verification**: `npx vitest run src/eval-server/__tests__/api-skills-route.test.ts` — must FAIL before T-005 lands.

### T-002: RED — StudioContext first-load fetch test
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01, AC-US3-02 | **Status**: [x]
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/StudioContext.first-load.test.tsx` (NEW)
**Test Plan (BDD)**:
- **Given** localStorage is empty and `fetch` is mocked: `/api/agents` → `{ suggested: "claude-code", agents: [...] }`, `/api/skills?agent=claude-code` → `[]`
- **When** `<StudioProvider>` is mounted
- **Then** within `waitFor`, `fetch` is called with a URL that includes `agent=claude-code`
- **And** `fetch` is NEVER called with `/api/skills` lacking `?agent=`
- **Given** localStorage starts with `{"activeAgent":"cursor"}`
- **When** mounted
- **Then** `fetch('/api/skills?agent=cursor')` is called and `/api/agents` is NOT called (warm-start path)
**Verification**: `npx vitest run src/eval-ui/src/__tests__/StudioContext.first-load.test.tsx` — must FAIL before T-006 lands.

### T-003: RED — App suggested-fallback persistence test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x]
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/App.suggested-fallback.test.tsx` (NEW)
**Test Plan (BDD)**:
- **Given** localStorage is empty and `useAgentsResponse` is mocked to return `{ suggested: "claude-code" }`, with a `studio:agent-changed` listener attached BEFORE mount
- **When** `<App />` is mounted
- **Then** localStorage `vskill.studio.prefs` contains `{"activeAgent":"claude-code", ...}` AND the listener received exactly ONE event with `detail.agentId === "claude-code"`
- **Given** localStorage already contains `{"activeAgent":"opencode"}`
- **When** `<App />` is mounted with the same suggested mock
- **Then** localStorage is unchanged (`opencode`) AND the listener received ZERO events from hydration
**Verification**: `npx vitest run src/eval-ui/src/__tests__/App.suggested-fallback.test.tsx` — must FAIL before T-007 lands.

### T-004: RED — verify all three RED tests fail for the right reasons
**Status**: [x]
**Verification**: Run `npx vitest run` in vskill repo, confirm T-001/T-002/T-003 each fail with assertion messages that point to the specific bug (filter no-op, missing ?agent=, missing localStorage write). No syntax errors, no missing-mock errors.

## Phase 2 — GREEN (implement the fix)

### T-005: Server — filter uses resolved agent
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x]
**File**: `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (line 1699-1701)
**Change**: `agent: rawAgent` → `agent: activeAgent` in the `filterSkillsByScopeAndAgent` call.
**Verification**: T-001 passes. Re-run the existing scope-filter unit test (`api-skills-scope.test.ts`) — must remain green.

### T-006: StudioContext — bootstrap from /api/agents when localStorage empty
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x]
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/StudioContext.tsx`
**Change**:
- Add `bootstrapDone` state, initial `false`.
- On mount: if localStorage `activeAgent` is set, set `bootstrapDone = true` immediately.
- Else fetch `/api/agents`, on response set `activeAgent = response.suggested ?? "claude-code"` and `bootstrapDone = true`.
- Gate `loadSkills` `useEffect`: `if (!bootstrapDone) return;` at the top.
**Verification**: T-002 passes. No new console errors in the existing `StudioContext.*.test.tsx` files.

### T-007: App.tsx — suggested-fallback routes through handleActiveAgentChange
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x]
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (lines 140-145)
**Change**: Replace `setActiveAgentIdState(agentsResponse.response.suggested);` with `handleActiveAgentChange(agentsResponse.response.suggested);`.
**Verification**: T-003 passes. No new errors in existing `App.*.test.tsx` files.

### T-008: Build the eval-ui bundle
**Status**: [x]
**Command**: `(cd repositories/anton-abyzov/vskill/src/eval-ui && npm run build)`
**Verification**: Build succeeds, dist/ updated. Per project memory `project_vskill_studio_runtime.md`, `vskill studio` serves this pre-built bundle.

## Phase 3 — REFACTOR + verify

### T-009: Run full Vitest suite for vskill
**Status**: [x]
**Command**: `(cd repositories/anton-abyzov/vskill && npx vitest run)`
**Verification**: All tests green, no flakes. T-001/T-002/T-003 specifically green. No previously-green test newly red.

### T-010: Live API parity check (curl)
**Status**: [x]
**Verification**: After restarting `vskill studio` (to pick up the rebuilt bundle):
- `curl -s http://localhost:3113/api/skills | jq 'length'`
- `curl -s 'http://localhost:3113/api/skills?agent=claude-code' | jq 'length'`
- The two counts must be EQUAL (in `specweave-umb` workspace, both should be 65).
- `curl -s http://localhost:3113/api/skills | jq '[.[] | .sourceAgent] | unique'` — must be `["claude-code"]` (or `[null, "claude-code"]` if any `own`-scope rows have null).

### T-011: Sub-agent verification — server contract
**Status**: [x]
**Action**: Spawn an Explore sub-agent to verify the server response invariants from a fresh inspection (independent of my edits) — see prompt in Phase 4.

### T-012: Sub-agent verification — frontend contract
**Status**: [x]
**Action**: Spawn an Explore sub-agent to verify the StudioContext + App.tsx changes don't introduce hidden races or duplicate fetches — see prompt in Phase 4.

## Phase 4 — Closure

### T-013: CHANGELOG entry
**Status**: [x]
**File**: `repositories/anton-abyzov/vskill/CHANGELOG.md`
**Entry**: One line under "### Fixed" for the next unreleased version: "Studio: skill list now filters by the picker-selected agent on first load (previously surfaced 108 skills from `.aider/`, `.cursor/`, etc. when picker showed Claude Code)."

### T-014: Sync living docs + GitHub issue update
**Status**: [x]
**Command**: `specweave sync-living-docs 0733-studio-agent-filter-first-load`
