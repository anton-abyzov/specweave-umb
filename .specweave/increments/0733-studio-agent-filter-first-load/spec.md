---
increment: 0733-studio-agent-filter-first-load
title: "Studio: agent filter must apply on first load"
type: bug
priority: P1
status: planned
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio: agent filter must apply on first load

## Overview

On a fresh `vskill studio` session — where the user has never explicitly clicked the AgentScopePicker — the picker shows the server-suggested agent (Claude Code in this codebase) but the skill list fetched by StudioContext is unfiltered. The sidebar renders 108 skills with `.agent/`, `.agents/`, `.aider/`, `.codex/`, `.cursor/`, `.gemini/`, `.kiro/`, `.openclaw/`, `.pi/`, `.windsurf/` buckets visible — none of which belong to the visibly-selected agent.

Confirmed with a live curl against the running studio in this workspace:

| Request                                       | Skills returned | Distinct sourceAgent values                                                                    |
| --------------------------------------------- | --------------: | ---------------------------------------------------------------------------------------------- |
| `GET /api/skills` (no `?agent=`)              |             108 | claude-code, antigravity, aider, codex, cursor, gemini-cli, kiro-cli, openclaw, pi, windsurf, opencode |
| `GET /api/skills?agent=claude-code`           |              65 | claude-code only                                                                               |

So the backend filter works in isolation; the failure is the *combination* of frontend never sending `?agent=` AND the backend dropping the filter when it isn't sent.

Three cooperating defects in `repositories/anton-abyzov/vskill`:

1. **Server (api-routes.ts:1611-1701)** — handler resolves `activeAgent` (defaulting to "claude-code") and uses it to *scan*, but the filter call at line 1699-1701 passes `rawAgent` (the un-defaulted query param). When `?agent=` is omitted, `rawAgent` is `undefined` and `filterSkillsByScopeAndAgent` short-circuits, returning all skills.
2. **Frontend hydration (App.tsx:140-145)** — when no persisted `activeAgent` exists, App.tsx falls back to `agentsResponse.response?.suggested` and calls `setActiveAgentIdState(...)` only. It does not call `writeStudioPreference("activeAgent", ...)` and does not dispatch `studio:agent-changed`.
3. **Frontend StudioContext (StudioContext.tsx:181-200)** — initial state reads `vskill.studio.prefs.activeAgent` from localStorage and stays `null` if missing. It only updates via the `studio:agent-changed` event, which (because of bug #2) never fires on first load. So `loadSkills` calls `api.getSkills(undefined)` and the request goes out without `?agent=`.

## User Stories

### US-001: Skills sidebar matches the picker on first load (P1)
**Project**: vskill

**As a** vskill studio user opening a fresh project
**I want** the skill list to be filtered to the agent shown in the picker
**So that** I'm not confused by skills owned by agents I'm not using (`.aider/`, `.cursor/`, `.gemini/`, etc.)

**Acceptance Criteria**:
- [x] **AC-US1-01**: With localStorage cleared and `agentsResponse.suggested = "claude-code"`, the very first `/api/skills` request issued by StudioContext contains `?agent=claude-code` (no other value, not omitted).
- [x] **AC-US1-02**: After hydration, `localStorage["vskill.studio.prefs"].activeAgent === "claude-code"` (the fallback persisted, not just held in React state).
- [x] **AC-US1-03**: After hydration, the `studio:agent-changed` event fires exactly once with `detail.agentId === "claude-code"`, and any listener attached before the dispatch receives it.
- [x] **AC-US1-04**: When `localStorage` already has `activeAgent` set to a real value, the suggested-fallback path does NOT overwrite it.

### US-002: Server filter is enforced even when frontend forgets the query param (P1)
**Project**: vskill

**As a** vskill studio backend operator
**I want** `/api/skills` to filter by the same agent it scans for, even when no `?agent=` query param is passed
**So that** scan/filter mismatch can never leak skills from other agents into the response (defense in depth)

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/skills` (no `?agent=`) returns the SAME skill set as `GET /api/skills?agent=<resolvedDefaultAgent>` — i.e., the response is filtered by the agent the server resolved for scanning, not by the raw param.
- [x] **AC-US2-02**: Every skill in the no-param response satisfies `scope === "own" || sourceAgent === resolvedDefaultAgent`.
- [x] **AC-US2-03**: When `?agent=cursor` is explicitly sent, only skills with `sourceAgent === "cursor"` (plus `scope === "own"`) come back — no regression from existing behavior.
- [x] **AC-US2-04**: An invalid `?scope=` value (e.g. `?scope=garbage`) returns `[]` — no regression.

### US-003: StudioContext stays in sync with App.tsx without prop drilling (P2)
**Project**: vskill

**As a** vskill studio engineer
**I want** StudioContext and App.tsx to read the same effective `activeAgent` from the same source
**So that** future changes can't reintroduce the "picker shows X, fetches with Y" divergence

**Acceptance Criteria**:
- [x] **AC-US3-01**: StudioContext, when it cannot read `activeAgent` from localStorage, falls back to the server-suggested agent from `/api/agents` before issuing its first `/api/skills` request.
- [x] **AC-US3-02**: A unit test asserts that `loadSkills` is called with a non-null `agent` filter even when localStorage starts empty.
- [x] **AC-US3-03**: The `studio:agent-changed` event remains the runtime update path; the suggested-fallback only applies when localStorage is empty AND the event has not yet fired.

## Functional Requirements

### FR-001: Filter parity between scan and response
The `/api/skills` handler MUST resolve `activeAgent` once (raw param OR suggested default) and use that same value for BOTH the global scope scan AND the post-enrichment filter call. There must be no code path where the scan uses one agent value and the filter uses another.

### FR-002: Persisted-state symmetry
The "fall back to suggested" hydration in App.tsx MUST go through the same persistence path as an explicit picker click — `writeStudioPreference` + `dispatchEvent("studio:agent-changed")` — so that any other observer reading `vskill.studio.prefs` sees the same effective value.

### FR-003: Single source of truth on first load
StudioContext MUST NOT fetch skills with a `null`/`undefined` agent on first load when an effective value can be derived. If localStorage is empty, it must wait for or trigger the suggested-fallback before issuing its first fetch.

## Success Criteria

- `GET /api/skills` and `GET /api/skills?agent=<suggested>` return byte-identical JSON when run against the same workspace state.
- On a fresh session in `specweave-umb` with picker showing "Claude Code", the sidebar shows ≤65 skills (no `.aider/`, `.cursor/`, `.gemini/`, etc. buckets) — matching the curl output for `?agent=claude-code`.
- All three bug-specific Vitest tests fail before the fix and pass after.

## Out of Scope

- Reworking the AgentScopePicker UI itself.
- Changing how skills are scanned (`.aider/skills/*` etc. continue to be discovered as `installed` skills with `sourceAgent` populated — that's correct).
- Adding a "show all agents" mode (deliberately filtered out as not needed for this fix).
- Multi-project / workspace-routing changes.

## Dependencies

- Existing `filterSkillsByScopeAndAgent` helper at api-routes.ts:362 (no signature change).
- Existing `writeStudioPreference` / `getStudioPreference` in `useStudioPreferences.ts` (no API change).
- Existing `studio:agent-changed` CustomEvent contract (`detail.agentId: string`) — preserved.
- Existing `/api/agents` endpoint (used as the source for `suggested`).
