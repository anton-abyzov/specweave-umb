# Implementation Plan: Studio install button: scope clarity + installed-state awareness

## Overview

Two-surface change to the vskill studio:

1. **Server (eval-server, Node http)**: add a single read-only route `GET /api/studio/install-state?skill=<publisher>/<slug>` that reports per-scope (project, user) install state for a single skill, plus the list of agent tools detected on the host. Reuses existing primitives — does not introduce new file-system scanners or schema migrations.
2. **Client (eval-ui, React)**: narrow the existing 3-button scope picker (Project | User | Global) to 2 buttons (Project | User), drive each button's enabled state from the new endpoint, and re-fetch on the existing-but-unconsumed `studio:skill-installed` CustomEvent so post-install state updates without a manual reload.

The vskill CLI is unchanged. The legacy `--global` flag stays for power users; the studio UI's "User" button just maps to it transparently.

## Architecture

### Components

- **`src/eval-server/install-state-routes.ts`** (new): express-style route handler registered with the existing `Router` API. Single GET handler `/api/studio/install-state`. Localhost-only guard. Composes data from `detectInstalledAgents()` + the existing `/api/skills` row-builder logic.
- **`src/eval-server/eval-server.ts`** (~line 99): one-line registration call `registerInstallStateRoutes(router, root)` next to `registerInstallSkillRoutes`. No other server changes.
- **`src/eval-ui/src/api.ts`** (~line 268): typed wrapper `getSkillInstallState(name): Promise<InstallStateResponse>` that fetches the new endpoint and parses the response. Mirrors the existing `getSkills` pattern.
- **`src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx`** (lines 95-141, 215, 246, 752-807, 813-834): narrow `InstallScope` type, drop "global" branches, add `installState` state slot, parallelize the install-state fetch with metadata + versions, listen for `studio:skill-installed` to re-fetch.

### Data Model — `InstallStateResponse` (new shared type)

```ts
// src/eval-server/install-state-routes.ts (exported)
// src/eval-ui/src/types/install-state.ts (mirror) — co-located with other shared UI types

export interface DetectedAgentTool {
  id: string;            // agent registry id, e.g. "claude-code"
  displayName: string;   // human label, e.g. "Claude Code"
  localDir: string;      // project-relative, e.g. ".claude/skills"
  globalDir: string;     // tilde path, e.g. "~/.claude/skills"
}

export interface InstallStateForScope {
  installed: boolean;
  installedAgentTools: string[];   // dedup'd agent ids; empty when installed=false
  version: string | null;          // currentVersion from vskill.lock; null if missing
}

export interface InstallStateResponse {
  skill: string;                                  // echoed from query
  detectedAgentTools: DetectedAgentTool[];        // ~14 typical, all detected on host
  scopes: {
    project: InstallStateForScope;
    user: InstallStateForScope;
  };
}
```

### API Contract — `GET /api/studio/install-state`

Request:
- Query param `skill`: required, must match `SAFE_NAME` regex (mirrors install-skill-routes.ts:29).

Responses:
- `200 OK` + `InstallStateResponse` JSON for a valid skill name (whether or not it's installed).
- `400` `{ "error": "invalid skill identifier" }` if `skill` is missing or fails regex.
- `403` `{ "error": "localhost-only endpoint" }` if `req.socket.remoteAddress` is not loopback.
- `500` only on unexpected internal errors (the row builder is designed to handle "skill not found" silently — those return `installed: false` per scope).

Caching:
- No `Cache-Control` headers — eval-server already returns no-store for studio routes by default.
- In-process: detected-agents result is memoized per process for 60s (parallel to `detectAuthoredSourceLink` memo at api-routes.ts:936-943) since FS detection is the same regardless of skill name.

## Technology Stack

- **Language/Framework**: TypeScript (existing project — Node http server + React eval-ui).
- **Libraries**: existing — no new dependencies.
- **Tools**: Vitest (unit + integration), existing fetch mock pattern from SkillDetailPanel.test.tsx.

**Architecture Decisions**:

- **D1: New endpoint vs extending `/api/skills`** — chose new endpoint. `/api/skills` is 712 KB across 540 rows on the test machine; reshaping it (adding `installScope` per row) would force every consumer (Sidebar, RightPanel, UpdateBell, StudioContext) to handle the new field even though only SkillDetailPanel needs the per-scope split. A dedicated endpoint also lets us filter to one skill server-side (vs all 540 rows over the wire to compute one panel's state).
- **D2: Reuse `detectInstalledAgents()` vs new detector** — chose reuse. The user explicitly opted for "current detected behavior" (AskUserQuestion answer A). detectInstalledAgents already implements the two-tier check (CLI binary OR globalSkillsDir presence) with the right edge-cases (skips generic parent dirs).
- **D3: Disabled button vs hidden button for installed state** — chose disabled. A11y wins: the radiogroup keeps its full set of options visible to screen readers, the "Installed ✓" copy explains why the user can't pick it, and the user can still see at-a-glance which scopes have the skill. Hidden buttons would create a layout shift between "not installed" and "installed" panels.
- **D4: Plain HTML `title=` tooltips vs Radix Tooltip** — chose plain `title=`. The existing scope buttons already use plain `title=` (SkillDetailPanel.tsx:789). Adding a tooltip library for one feature would inflate the bundle and break the established pattern. The tooltip strings are short enough that native browser tooltips render fine.
- **D5: Re-fetch trigger on install success** — chose listening for the existing `studio:skill-installed` CustomEvent (SkillDetailPanel.tsx:454-456). It's already broadcast but had no listener (per the explore agent's report). Wiring it now closes the gap with zero new event-bus surface area.
- **D6: Backwards-compat for `studio:skill-installed` payload** — keep the `scope` field typed as `"project" | "user" | "global"` even though the UI now emits only "project" or "user". Any external listener that filters on scope==="global" continues to compile. Internal listeners only need to handle the two values the UI emits.

## Implementation Strategy

### Phase 1 (Server)
1. Create `src/eval-server/install-state-routes.ts` with the route handler. Reuse the existing `Router` API surface (from `router.ts`).
2. Add `registerInstallStateRoutes(router, root)` call in `eval-server.ts` next to `registerInstallSkillRoutes`.
3. Write unit/integration tests in `src/eval-server/__tests__/install-state-routes.test.ts` covering all 5 endpoint ACs (US-002 AC-01..AC-05 + US-003 AC-02). Tests fail initially → implementation makes them pass.

### Phase 2 (Client API)
1. Add `getSkillInstallState(name)` to `src/eval-ui/src/api.ts`.
2. Add type re-exports.

### Phase 3 (Client UI)
1. Narrow `InstallScope` type and `scopeFlag` mapping (SkillDetailPanel.tsx lines 99, 101-104).
2. Reduce scope picker `.map()` array from 3 → 2 entries (line 767). Update label/description branches.
3. Add `installState` state slot. Add third Promise.all entry for fetch (line 246).
4. Render disabled state for buttons whose scope reports `installed: true`.
5. Add `studio:skill-installed` CustomEvent listener that re-fetches install-state. Cleanup on unmount.
6. Disable primary Install CTA when selected scope is installed; tooltip explains.
7. Extend tests in `SkillDetailPanel.test.tsx` covering all 6 client ACs (US-001 AC-01..AC-06 + US-002 AC-06..AC-09 + US-003 AC-04).

### Phase 4 (Verification)
1. Build: `npm run build` from `repositories/anton-abyzov/vskill/`.
2. Restart studio against local bundle (kill PID 75337, start fresh).
3. Server smoke: `curl localhost:3114/api/studio/install-state?skill=gitroomhq/postiz-agent/postiz | jq` — verify `scopes.user.installed: true`, `version: "2.0.12"`, `installedAgentTools: ["claude-code"]`.
4. UI smoke via Claude_Preview MCP: search "postiz" → click → verify disabled User button, enabled Project button, tooltips, no Global button.
5. Test suite: `npx vitest run` for both new + extended test files.
6. Sanity sweep: full vitest run to catch any unintended downstream breakage.

## Critical files to modify

| Path | Change |
|------|--------|
| `repositories/anton-abyzov/vskill/src/eval-server/install-state-routes.ts` | NEW — endpoint + handler |
| `repositories/anton-abyzov/vskill/src/eval-server/eval-server.ts` (line ~99) | Register the new route alongside `registerInstallSkillRoutes` |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (lines 1896-1976) | Reuse existing row-builder logic — no changes; if needed, extract a helper for install-state-routes |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx` (lines 95-141, 215, 246, 752-807, 813-834) | Narrow `InstallScope`, drop Global branches, fetch install-state, disabled-state rendering, refresh-after-install |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/api.ts` (~line 268) | Add `getSkillInstallState(name)` typed wrapper |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/install-state-routes.test.ts` | NEW — endpoint tests |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/__tests__/SkillDetailPanel.test.tsx` | Extend — installed-state UX tests, no-Global assertion |

## Reused functions / utilities (no reinvention)

- `detectInstalledAgents()` — `src/agents/agents-registry.ts:853` — for `detectedAgentTools`.
- `scanSkillsTriScope` + `enrichAndComputePrecedence` — `src/eval-server/api-routes.ts:1896-1976` — for installed-row queries.
- Lockfile reader — `src/lockfile/lockfile.ts` — for `currentVersion`.
- `studio:skill-installed` CustomEvent — `SkillDetailPanel.tsx:454` — already fires on success; just add a listener.
- `Router` + localhost guard pattern — `src/eval-server/install-skill-routes.ts:49` — for the new route.
- `SAFE_NAME` regex pattern — `src/eval-server/install-skill-routes.ts:29` — for query param validation.

## Risks + mitigations

- **`/api/skills` row builder is heavy** — won't be a problem because the new endpoint filters to one skill before partitioning. If the row builder still walks the full FS tree, we extract a `findInstalledRowsForSkill(name)` helper that early-exits.
- **Two installs at the same scope across different agent tools** — handled by `installedAgentTools[]` returning the deduped list.
- **Race: install completes after panel unmounts** — listener cleanup on unmount per existing `useEffect` return pattern (already used in the panel for the back-button focus management at line 222-231).
- **Test fixtures for FS** — reuse existing mock pattern from `SkillDetailPanel.test.tsx` rather than introducing real-FS scaffolding.
- **Vskill is currently running as `npx vskill@1.0.15`** — the running process has the OLD code. Verification step #2 explicitly restarts the studio against the locally-built `dist/bin.js` so the user sees the new behavior end-to-end.

## ADRs

No new ADR for this increment — the architectural pattern (new studio-only route + thin client wrapper + state-machine narrowing) is well-established in the codebase. Reused decisions:

- Studio routes are localhost-only by default (existing pattern from install-skill-routes, install-engine-routes).
- Per-skill data freshness via the existing `studio:skill-installed` event (no new event-bus).
- Plain HTML `title=` tooltips for short explanations (existing scope-button pattern at SkillDetailPanel.tsx:789).
