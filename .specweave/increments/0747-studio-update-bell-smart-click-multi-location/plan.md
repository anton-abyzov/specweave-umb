# Implementation Plan: Studio: smart update-bell click + cross-agent multi-location update awareness

## Overview

Two-layer change in `repositories/anton-abyzov/vskill/`:

1. **Backend (Node eval-server)**: new `scanSkillInstallLocations` utility that iterates `AGENTS_REGISTRY` to find every agent dir holding a given skill (project + personal scope) plus plugin-cache scan; enriches `/api/skills/updates` response with `installLocations[]` + resolved `localPlugin`/`localSkill`; extends single-skill update endpoint to accept `?agent=<id>` (allowlist-validated, forwarded as `--agent <id>` CLI flag).

2. **Frontend (React eval-ui)**: replace naive split in `UpdateBell` with `revealSkill(localPlugin, localSkill)`; add inline `<UpdateAction>` button + native HTML tooltip per dropdown row using new `formatUpdateLocationTooltip` util; render `InstallLocationChips` strip in `SkillDetailPage` when N>1 locations.

The CLI primitive `vskill update <name>` already iterates `detectInstalledAgents()` and updates every agent's `localSkillsDir` — so the cross-agent fan-out exists and is reused as-is.

## Architecture

### Components

**Backend (new)**:
- `src/eval-server/utils/scan-install-locations.ts` — pure function `scanSkillInstallLocations(canonicalName, projectRoot?): InstallLocation[]`. Iterates `getInstallableAgents()`, probes both `<projectRoot>/<agent.localSkillsDir>/<slug>/SKILL.md` (project) and `expandHome(agent.globalSkillsDir)/<slug>/SKILL.md` (personal). Calls `scanInstalledPluginSkills()` for plugin-bundled copies. `fs.lstat` detects symlinks pointing to canonical `.agents/skills/<name>/`.

**Backend (modified)**:
- `src/eval-server/api-routes.ts:1791-1809` (`/api/skills/updates`) — call scanner once per request (per-request memoization), attach `installLocations[]`, `localPlugin`, `localSkill` per row.
- `src/eval-server/api-routes.ts:1925-1954` (`POST /api/skills/:plugin/:skill/update`) — accept `?agent=<id>` query param, validate against `AGENTS_REGISTRY`, forward as `--agent <id>` to `vskill update`.
- `src/commands/outdated.ts:53-110` (`getOutdatedJson`) — optionally surface install location data so the API handler doesn't need to re-scan (or keep scanner separate; decided in T-002 based on coupling).

**Frontend (new)**:
- `src/eval-ui/src/components/InstallLocationChips.tsx` — chip strip below skill detail title. Renders `[scope · agentLabel]` per location with optional 📌 (pinned) / 🔒 (readonly) icons. Per-chip "Update this location" affordance for non-readonly, non-pinned chips.
- `src/eval-ui/src/utils/formatUpdateLocationTooltip.ts` — pure formatter `formatUpdateLocationTooltip(locations: InstallLocation[]): string`.

**Frontend (modified)**:
- `src/eval-ui/src/api.ts` — extend `SkillUpdateInfo` with `installLocations?: InstallLocation[]`, `localPlugin?: string`, `localSkill?: string`. Add new `InstallLocation` exported type.
- `src/eval-ui/src/components/UpdateBell.tsx:118-124` — call `revealSkill(localPlugin ?? "", localSkill ?? lastSegment)` instead of `selectSkill`. Add no-match fallback toast using `useToast` + `useAgentCatalog`.
- `src/eval-ui/src/components/UpdateDropdown.tsx` — add inline `<UpdateAction>` per row with `title=` tooltip via the formatter.
- `src/eval-ui/src/components/UpdateAction.tsx` — accept optional `agentId` prop; when set, call update endpoint with `?agent=<id>`.
- `src/eval-ui/src/pages/SkillDetailPage.tsx:30-62` — render `<InstallLocationChips>` when `locations.length > 1`.

### Data Model

```ts
// Added to src/eval-ui/src/api.ts (and mirrored on backend)
export type InstallLocation = {
  scope: "project" | "personal" | "plugin";
  agent: string;            // AgentDefinition.id (e.g. "claude-code")
  agentLabel: string;       // e.g. "Claude Code"
  dir: string;              // absolute path to skill folder
  pluginSlug?: string;      // when scope === "plugin"
  pluginMarketplace?: string;
  symlinked: boolean;       // true when this is a symlink to canonical
  readonly: boolean;        // true for plugin-bundled
};

export type SkillUpdateInfo = {
  // existing fields:
  name: string;
  installed: string;
  latest: string | null;
  updateAvailable: boolean;
  pinned?: boolean;
  pinnedVersion?: string;
  trackedForUpdates?: boolean;
  // NEW (optional, additive):
  installLocations?: InstallLocation[];
  localPlugin?: string;
  localSkill?: string;
};
```

### API Contracts

- `GET /api/skills/updates` — response shape extended (additive). Existing fields unchanged. Cross-agent scan runs once per request.
- `POST /api/skills/:plugin/:skill/update?agent=<id>` — same endpoint, new optional query param. Without `?agent`, behavior unchanged (full cross-agent fan-out via CLI). With valid `?agent=<id>` from `AGENTS_REGISTRY`, forwards as `--agent <id>`.

## Technology Stack

- **Language/Framework**: TypeScript (Node eval-server, React eval-ui), Vitest, Playwright.
- **Libraries**: no new deps. Reuses native `fs`, existing `useToast`, existing `revealSkill`, native HTML `title=` tooltips.
- **Tools**: existing vskill CLI (`vskill update`).

**Architecture Decisions**:

- **ADR-0747-01 — Reuse CLI fan-out instead of TS reimplementation**: `vskill update <name>` already iterates `detectInstalledAgents()` and updates every agent's `localSkillsDir`. We reuse this primitive rather than reimplementing fan-out in TypeScript. Trade-off: slightly less control over per-location error reporting (current CLI returns one stdout dump), but zero risk of behavior divergence between CLI and Studio. Deferred per-location result parsing until measured need.

- **ADR-0747-02 — Use `revealSkill`, not `selectSkill`, for bell-click navigation**: `revealSkill` already implements F-001 (no-plugin guard) and F-002 (non-plugin-source fallback) for matching skills in state. Calling it from the bell click reuses the proven matching logic instead of duplicating it. Trade-off: requires server to provide `localPlugin`/`localSkill` for accurate matching; backwards-compat handled via fallback path.

- **ADR-0747-03 — Pin remains global per skill, not per-location**: Lockfile schema currently has one `pinnedVersion` per skill name. Per-location pinning would require schema redesign. Out of scope for this increment; UI surfaces the global pin once per chip but does not allow per-location pin/unpin. Tracked as future follow-up.

- **ADR-0747-04 — Plugin-bundled skills are read-only from the bell flow**: Updating a plugin-bundled skill requires updating the plugin (different mechanism). The bell Update button blocks with informative toast for plugin-only skills; chip in detail view shows 🔒 with no Update affordance. No auto-trigger of plugin update.

- **ADR-0747-05 — Allowlist validation on `?agent=<id>`**: Before interpolating into the execSync command, validate against `AGENTS_REGISTRY` ids. Prevents shell injection via crafted query params.

- **ADR-0747-06 — Native HTML tooltips, not Radix/Floating UI**: Studio already uses `title=` attributes throughout (per `SymlinkChip.tsx`, `VersionBadge.tsx`, `ProvenanceChip.tsx`). Stay consistent; avoid adding a tooltip library for one feature.

## Implementation Phases

### Phase 1: Backend foundation (T-001 → T-003)
- T-001: `scanSkillInstallLocations` utility + tests (RED→GREEN→REFACTOR).
- T-002: Enrich `/api/skills/updates` response with location metadata.
- T-003: Extend single-skill update endpoint with `?agent=<id>` query param + allowlist validation.

### Phase 2: Frontend types + utilities (T-004 → T-005)
- T-004: Extend `SkillUpdateInfo` type and add `InstallLocation` to `api.ts`.
- T-005: `formatUpdateLocationTooltip` pure-function util + tests.

### Phase 3: UpdateBell + UpdateDropdown UX (T-006 → T-007)
- T-006: Replace naive split in `UpdateBell.tsx` with `revealSkill(localPlugin, localSkill)` + no-match fallback toast.
- T-007: Add inline `<UpdateAction>` button + tooltip to `UpdateDropdown.tsx` rows.

### Phase 4: Detail view chips (T-008 → T-010)
- T-008: `InstallLocationChips` component + tests.
- T-009: Integrate chips into `SkillDetailPage.tsx`.
- T-010: Per-chip "Update this location" wiring + plugin-readonly handling.

## Testing Strategy

Strict TDD per `.specweave/config.json` (`testing.defaultTestMode: "TDD"`, enforcement varies):

- **Unit tests** (Vitest): scanner with fixtured fs, tooltip formatter (pure), backwards-compat fallback in UpdateBell.
- **Component tests** (Vitest + Testing Library): UpdateBell click → revealSkill mock; UpdateDropdown row Update button + tooltip; InstallLocationChips render conditions; SkillDetailPage with N=1 vs N>1.
- **Integration tests** (Vitest): `/api/skills/updates` response shape with mocked fs scan; update endpoint `?agent=<id>` parameter forwarding.
- **E2E test** (Playwright): full flow — install greet-anton in two agent dirs → click bell row → detail loads → click Update → toast confirms 2 locations updated → verify on disk.

Coverage target: 90% lines (per increment frontmatter).

## Technical Challenges

### Challenge 1: Symlink detection across mixed install methods
**Solution**: Use `fs.lstat` (not `fs.stat`) per location to detect symlinks. Mark `symlinked: true` when the target resolves under `.agents/skills/<canonical-name>/`. UI can then show the symlink icon (using existing `SymlinkChip` patterns) so users understand "updating this also updates other symlinked locations".
**Risk**: Edge case where the symlink is broken (target deleted) — `lstat` succeeds but `stat` fails. Treat as still-listed (the SKILL.md inode resolution failed, but the symlink entry counts as an install location).

### Challenge 2: Backwards compatibility with older eval-servers
**Solution**: Frontend treats `installLocations` and `localPlugin`/`localSkill` as optional. When absent, falls back to existing behavior (naive split + revealSkill fallback). Tooltip in that case shows generic "Update this skill" without location count.
**Risk**: User sees inconsistent UX between updated and stale eval-servers. Mitigated by version-bump notice on next vskill release.

### Challenge 3: Allowlist for `?agent=<id>` to prevent injection
**Solution**: Hard validation against `AGENTS_REGISTRY.map(a => a.id)` before any execSync interpolation. Reject with 400 for unknown ids. Same pattern used elsewhere in the API for skill-name validation.
**Risk**: New agents added to AGENTS_REGISTRY without UI awareness — handled by the existing detection pipeline; agent must be in registry to appear in scan results, so allowlist is consistent by construction.

### Challenge 4: Per-request memoization of scan
**Solution**: Build a `Map<canonicalName, InstallLocation[]>` once at the top of the `/api/skills/updates` handler, reuse for all rows. No cross-request caching to avoid stale data after install/uninstall.
**Risk**: 60+ stat calls per scan can be slow on cold cache. Acceptable per performance budget (sub-50ms warm); if measured-hot, lift into existing skills cache (deferred).
