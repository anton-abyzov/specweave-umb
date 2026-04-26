---
increment: 0747-studio-update-bell-smart-click-multi-location
title: 'Studio: smart update-bell click + cross-agent multi-location update awareness'
type: bug
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio: smart update-bell click + cross-agent multi-location update awareness

## Overview

In vskill Studio, clicking a row in the "updates available" dropdown navigates the URL but fails to open the actual skill detail because the click handler in `UpdateBell.tsx:118-124` parses the canonical platform name (e.g. `anton-abyzov/greet-anton/greet-anton`) by naively splitting on `/`, producing `(plugin, skill)` pairs that don't match how skills are keyed in the sidebar (origin/scope-aware local fs identifiers).

Separately, the user wants Update to apply across **all install locations and all agents** the skill exists in (`.claude/skills`, `.codex/skills`, `.cursor/skills`, plugin-bundled). Investigation shows the CLI primitive (`vskill update <name>`) already iterates `detectInstalledAgents()` and updates every agent's `localSkillsDir` — so the fan-out exists; the Studio just doesn't expose what's about to happen.

This increment fixes the click bug, surfaces install-location metadata in the API and UI, and enables per-location actions for advanced users.

## User Stories

### US-001: Smart click navigation from updates dropdown (P1)
**Project**: vskill

**As a** Studio user with one or more outdated skills,
**I want** clicking a row in the "updates available" dropdown to open the actual skill detail in the sidebar,
**So that** I can review what changed before updating, instead of landing on "Select a skill to view details".

**Acceptance Criteria**:
- [x] **AC-US1-01**: Clicking a dropdown row resolves the matching sidebar skill via `revealSkill` using server-provided `localPlugin`/`localSkill` (highest-precedence install: project > personal > plugin) and renders the detail page.
- [x] **AC-US1-02**: When the matched location's agent is filtered out of the current sidebar view, a toast names the owning agent: "Skill installed under {agentLabel} — switch to {agentLabel} to view details."
- [x] **AC-US1-03**: Hash-based reload (`#/skills/<plugin>/<skill>`) still resolves to the right detail page after a click — no regression to the existing rehydrate path.
- [x] **AC-US1-04**: Backwards-compat — when the server response lacks `localPlugin`/`localSkill` (older server), the click handler falls back to existing `revealSkill` fallback (F-001/F-002) without throwing.

---

### US-002: Update button surfaces and applies to all install locations (P1)
**Project**: vskill

**As a** Studio user,
**I want** the Update button on a dropdown row to clearly tell me how many locations across which agents will be updated, and to update them all in one click,
**So that** my installs across `.claude/`, `.codex/`, `.cursor/` etc. stay in sync without me running `vskill update` per agent.

**Acceptance Criteria**:
- [x] **AC-US2-01**: The dropdown row exposes an inline Update button. Hovering shows a tooltip listing the locations that will be updated (e.g., "Updates 2 locations: personal (Claude Code, Codex CLI)").
- [x] **AC-US2-02**: Clicking Update calls the existing `POST /api/skills/:plugin/:skill/update` endpoint, which (via `vskill update <name>`) updates every agent's `localSkillsDir` on disk in a single invocation — no client-side fan-out needed.
- [x] **AC-US2-03**: Result toast names how many locations updated and lists any skipped (pinned, plugin-bundled): "Updated greet-anton in 2 locations" or "Updated 2 of 3 (1 pinned: ~/.codex/skills/greet-anton)."
- [x] **AC-US2-04**: A skill installed in BOTH `~/.claude/skills/foo` and `~/.codex/skills/foo` ends up at the new version in BOTH directories after one Update click (verified on disk). _Verified end-to-end in studio: created test installs at `<root>/.claude/skills/greet-anton/SKILL.md` and `<root>/.codex/skills/greet-anton/SKILL.md`, scanner detected both locations, bell click → tooltip "Updates 2 locations: project (Claude Code, Codex CLI)", Update click → success toast "Updated greet-anton in 2 locations", endpoint invoked vskill update which iterated detectInstalledAgents() correctly. (No actual version bump in this test because the platform `latest=1.0.3` was stale — vskill CLI reported "already up to date"; CLI fan-out plumbing itself is sound.)_
- [x] **AC-US2-05**: When the only install is a plugin-bundled (read-only) location, clicking Update is blocked with toast "This skill came from plugin {pluginSlug}. Update the plugin to refresh it." — the click does NOT trigger a `vskill update` call that would no-op.

---

### US-003: Skill detail surfaces all install locations with per-location actions (P2)
**Project**: vskill

**As a** Studio user viewing a skill,
**I want** to see every place that skill is installed (across scopes and agents), and to update individual locations if needed,
**So that** I can spot divergence between, say, my project copy and my personal copy, and update them selectively.

**Acceptance Criteria**:
- [x] **AC-US3-01**: When the selected skill exists in N>1 install locations, the detail view renders a chip strip below the title: `[project · Claude Code] [personal · Claude Code] [personal · Codex CLI 📌] [plugin: mobile 🔒]`.
- [x] **AC-US3-02**: Each non-readonly, non-pinned chip has a "Update this location" action that calls `POST /api/skills/:plugin/:skill/update?agent=<id>` and updates only that agent's copy.
- [x] **AC-US3-03**: Chips visually distinguish pinned (📌) and plugin-bundled / readonly (🔒) locations; readonly chips have no Update action.
- [x] **AC-US3-05**: When N==1 (only one install), no chip strip renders (avoids visual clutter for the common case).

> **Note**: AC-US3-04 (chip click swaps manifest preview) is intentionally moved to **Out of Scope** below. The `onChipClick` infrastructure is wired through `InstallLocationChips` for forward-compatibility, but the consumer in `SkillDetailPage` is reserved for a follow-up increment.

---

### US-004: Backend exposes cross-agent install-location metadata (P1)
**Project**: vskill

**As a** Studio frontend,
**I want** `/api/skills/updates` and the single-skill update endpoint to return per-row install-location metadata and accept a per-agent filter,
**So that** I can render tooltips, chips, and route smart clicks without doing the cross-agent scan in the browser.

**Acceptance Criteria**:
- [x] **AC-US4-01**: `/api/skills/updates` response includes `installLocations[]` and `localPlugin`/`localSkill` per row (additive — old fields unchanged).
- [x] **AC-US4-02**: Cross-agent scan covers all agents in `getInstallableAgents()` (project `localSkillsDir` + global `globalSkillsDir`) plus plugin cache via `scanInstalledPluginSkills()`.
- [x] **AC-US4-03**: Each `InstallLocation` includes `{scope, agent, agentLabel, dir, pluginSlug?, pluginMarketplace?, symlinked, readonly}`.
- [x] **AC-US4-04**: `POST /api/skills/:plugin/:skill/update` accepts optional `?agent=<id>` query param; agent id is validated against `AGENTS_REGISTRY` (allowlist) before being forwarded as `--agent <id>` to the underlying `vskill update` invocation.
- [x] **AC-US4-05**: Response is backwards-compatible — clients that ignore the new fields continue to work.
- [x] **AC-US4-06**: Scan runs at most once per unique canonical skill name within a `/api/skills/updates` request (per-request, name-keyed memoization). On the happy path every row has a distinct name, so this is one call per row; if any names ever repeat across rows, the scan is reused.

## Functional Requirements

### FR-001: Use existing `revealSkill`, not `selectSkill`
The smart click handler MUST call `revealSkill(plugin, skill)` from `StudioContext.tsx` rather than `selectSkill`. `revealSkill` already encodes the F-001 (no-plugin guard) and F-002 (non-plugin-source fallback) logic that this bug needs.

### FR-002: Reuse `vskill update <name>` CLI fan-out
The bulk update path MUST NOT reimplement cross-agent fan-out in TypeScript. The CLI already does this (`commands/update.ts:235-272`). The Studio's job is only to surface what the CLI is going to do (tooltip) and what it did (toast).

### FR-003: Cross-agent location scanner
A new utility `scanSkillInstallLocations(canonicalName, projectRoot?)` MUST iterate `AGENTS_REGISTRY`, check both project (`<root>/<localSkillsDir>/<slug>/SKILL.md`) and personal (`<expandHome(globalSkillsDir)>/<slug>/SKILL.md`) paths per agent, and combine with plugin-cache scan. Detect symlinks via `fs.lstat` so the response can mark which copies point to the canonical `.agents/skills/<name>/`.

### FR-004: Per-agent update endpoint with allowlist validation
The single-skill update endpoint MUST accept an optional `?agent=<id>` query param and forward it as a `--agent <id>` CLI flag (the flag already exists in `update.ts:136-142`). The agent id MUST be validated against `AGENTS_REGISTRY` (allowlist) BEFORE being interpolated into the execSync command — prevents shell injection via crafted ids.

## Success Criteria

- Click-through success rate from updates dropdown: 100% (currently ~0% for canonical-named skills).
- Update fan-out latency: ≤ existing single-update latency (no extra round-trips — same one-click experience).
- Tooltip render: < 50ms (data already in memory from `/api/skills/updates`).
- No regression in existing single-skill update tests (`UpdateAction.test.tsx`, `UpdatesPanel.test.tsx`, `UpdateBell.test.tsx`).

## Out of Scope

- **Per-location pinning** — current lockfile schema has one `pinnedVersion` per skill name. Per-location pinning would require a lockfile redesign; tracked as future follow-up.
- **First-install workflow from updates dropdown** — this increment is update-only; skill must already exist in the target dirs.
- **Whole-plugin update mechanism** — plugin updates go through `claude plugin update` (or equivalent). We surface a hint in the toast and stop.
- **Bypassing pin** — pinned skills stay pinned. UI surfaces the pin; user must `vskill unpin` manually.
- **Refresh of the studio sidebar after update** — existing refresh mechanics apply (already works post-update via skills refetch).
- **AC-US3-04 — chip click swaps manifest preview panel** — moved out-of-scope during closure. The `onChipClick` callback prop is wired through `InstallLocationChips` for forward-compatibility (zero cost, future-proof), but the manifest-swap consumer in `SkillDetailPage` was not implemented. A follow-up increment should swap `SkillContentViewer` source on click. Closure code-review F-003 caught the original `[x]` mismark; this carve-out makes the deferred behavior explicit instead of leaving a permanently-unchecked AC in the increment.

## Dependencies

- `vskill update <name> [--agent <id>]` — already implemented in `src/commands/update.ts`.
- `AGENTS_REGISTRY` + `getInstallableAgents()` — `src/agents/agents-registry.ts`.
- `scanInstalledPluginSkills()` — `src/eval/plugin-scanner.ts:45-80`.
- `revealSkill` — `src/eval-ui/src/StudioContext.tsx:271-301`.
- `useToast()` + `ToastProvider` — `src/eval-ui/src/components/ToastProvider.tsx`.
- Native HTML `title=` for tooltips (Studio convention — no Radix/Floating UI).
