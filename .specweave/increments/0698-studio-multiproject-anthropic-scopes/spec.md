---
increment: 0698-studio-multiproject-anthropic-scopes
title: "Skill Studio: multi-project + Anthropic-aligned scopes + plugin visibility (Available/Authoring)"
type: feature
priority: P1
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio — multi-project + Anthropic-aligned scopes + plugin visibility (Available/Authoring)

## Overview

Phase 1 of the Skill Studio redesign. Reorganizes the sidebar around the user's real mental model — **AVAILABLE** (skills Claude can invoke now) vs **AUTHORING** (skills I am writing) — each split by source channel (Project / Personal / Plugins). Introduces a multi-project workspace with a top-left `ProjectPicker` pill and a ⌘P command palette. Replaces the invented `own/installed/global` tri-scope with a 5-value `SkillScope` union that maps 1:1 to [Anthropic's skills docs](https://code.claude.com/docs/en/skills) and [plugins docs](https://code.claude.com/docs/en/plugins). Adds two new scanners: one walks `~/.claude/plugins/cache/` for installed plugin skills (AVAILABLE > Plugins), the other walks the active project for `.claude-plugin/plugin.json` manifests to surface plugin sources under development (AUTHORING > Plugins). Drops Drafts, Enterprise, and the footer project-path statusbar.

Full design reference: `/Users/antonabyzov/.claude/plans/eventual-dazzling-dahl.md`.

## Background & Problem

- **Single-project limitation**: `eval-server` requires `root` at boot. Users with multiple projects must restart Skill Studio to switch context. No in-app switcher exists.
- **Invented vocabulary**: `OWN / INSTALLED / GLOBAL` labels don't appear in Anthropic's docs. Users (and downstream tooling) have to translate mentally on every interaction. Increment 0688 is 85% done on these old strings and must be allowed to land without blocking.
- **Two concepts collapsed into one**: the current sidebar conflates "skills Claude can use right now" with "skills I am writing". A skill under development and a skill already installed in `~/.claude/skills/` look the same on disk from the sidebar's perspective, but are not the same in the user's head.
- **Plugin skills invisible**: skills distributed via Claude Code plugins (`~/.claude/plugins/cache/<marketplace>/<plugin>/skills/`) don't show up anywhere in Skill Studio. Neither do plugin sources being authored inside a project (`<project>/<plugin>/.claude-plugin/plugin.json`).
- **Redundant statusbar**: with a ProjectPicker pill in the top-left header, the footer project-path display duplicates information.

## User Stories

### US-001: Multi-project workspace management (P1)
**Project**: vskill

**As a** Skill Studio user with multiple local projects
**I want** to add, switch between, and remove projects from a persistent workspace without restarting
**So that** I can work across my project portfolio in one session and preserve the active selection between runs

**Acceptance Criteria**:
- [ ] **AC-US1-01**: A `ProjectPicker` pill renders in the top-left of `StudioLayout`; clicking it opens a popover listing all registered projects with name, absolute path (monospace), and a deterministic OKLCH color dot hashed from the path.
- [ ] **AC-US1-02**: The popover has an "Add project" affordance that accepts a directory path (via `showDirectoryPicker()` where supported, with a text-input fallback for Safari/Firefox) and appends a new `ProjectConfig` to `~/.vskill/workspace.json`.
- [ ] **AC-US1-03**: Selecting a project in the popover sets it as active, persists `activeProjectId` + `lastActiveAt` to `~/.vskill/workspace.json`, and invalidates the React Query `["skills"]` cache so the sidebar repopulates from the new project without a reload.
- [ ] **AC-US1-04**: A "Remove" affordance on each project row deletes it from `~/.vskill/workspace.json`; removing the active project clears `activeProjectId` and the UI renders an empty-state prompt.
- [ ] **AC-US1-05**: Keyboard shortcut ⌘P (Cmd+P on macOS, Ctrl+P elsewhere) opens `ProjectCommandPalette` with fuzzy filter over name + path, arrow-key navigation, and Enter to switch. Browser print dialog is suppressed via `preventDefault` only when focus is inside the Skill Studio DOM subtree.
- [ ] **AC-US1-06**: On load, `loadWorkspace` validates each `ProjectConfig.path` with `existsSync`; stale projects render in a muted style in the picker with a visible "Remove" affordance and are not selectable as active.
- [ ] **AC-US1-07**: Passing `--root <path>` on the CLI when `~/.vskill/workspace.json` does not exist auto-seeds the workspace with that project as the active entry, preserving CLI parity with the single-project behavior.

---

### US-002: Two-category sidebar organization (P1)
**Project**: vskill

**As a** skill author switching between reviewing installed skills and editing in-progress skills
**I want** the sidebar to show two top-level groups — AVAILABLE (skills Claude can invoke now) and AUTHORING (skills I am writing) — each with nested source sub-sections
**So that** I can tell at a glance whether a skill is live versus in-development, and know exactly where on disk it lives

**Acceptance Criteria**:
- [ ] **AC-US2-01**: The sidebar renders two non-collapsible small-caps `GroupHeader` rows — `AVAILABLE (N)` and `AUTHORING (M)` — where N and M are the totals of their nested sub-sections and are always displayed even when zero.
- [ ] **AC-US2-02**: Under AVAILABLE, three collapsible sub-sections render in order: `Project (p)`, `Personal (q)`, `Plugins (r)`. The Plugins sub-section is only rendered when the active agent is Claude Code.
- [ ] **AC-US2-03**: Under AUTHORING, two collapsible sub-sections render in order: `Skills (s)`, `Plugins (t)`. The Plugins sub-section is only rendered when the active agent is Claude Code.
- [ ] **AC-US2-04**: Each sub-section count reflects the number of skills assigned to that `SkillScope` for the active project; empty sub-sections still render with `(0)` rather than being hidden.
- [ ] **AC-US2-05**: Within AVAILABLE > Plugins and AUTHORING > Plugins, skills nest under their parent plugin: a collapsible `pluginName (x)` row parents its member skills. The `PluginGroup` component is reused for both locations.
- [ ] **AC-US2-06**: Per-sub-section collapse state persists in `localStorage` keyed by `vskill-sidebar-<agentId>-<scope>-collapsed`.
- [ ] **AC-US2-07**: Snapshot tests cover two agent scenarios (Claude Code vs Cursor) and assert that the Plugins sub-sections are present for Claude Code and absent otherwise.

---

### US-003: Anthropic-aligned scope vocabulary (P1)
**Project**: vskill

**As a** user reading Anthropic's official skills and plugins documentation while using Skill Studio
**I want** the in-app scope labels and internal identifiers to match the vocabulary in those docs 1:1
**So that** I don't have to mentally translate and can trust that what the docs describe is what the UI shows

**Acceptance Criteria**:
- [x] **AC-US3-01**: `SkillScope` in `src/eval-ui/src/types.ts` is defined as the union `"available-project" | "available-personal" | "available-plugin" | "authoring-project" | "authoring-plugin"`; no other scope literals exist in production code paths.
- [x] **AC-US3-02**: `SkillInfo` exposes derived `group: "available" | "authoring"` and `source: "project" | "personal" | "plugin"` computed as `scope.split("-")[0]` and `scope.split("-")[1]`; invalid combinations (e.g. `authoring-personal`) are never emitted by any scanner.
- [ ] **AC-US3-03**: User-visible labels in `src/eval-ui/src/strings.ts` are exactly: `available="Available"`, `authoring="Authoring"`, `project="Project"`, `personal="Personal"`, `plugin="Plugins"`, `skills="Skills"`. No occurrences of `Own`, `Installed`, `Global`, `Enterprise`, or `Drafts` remain in user-facing strings.
- [ ] **AC-US3-04**: A one-shot `scope-migration.ts` shim invoked synchronously from `main.tsx` before `createRoot()` rewrites legacy `localStorage` keys:
  - `vskill-sidebar-<agentId>-own-collapsed` → `vskill-sidebar-<agentId>-authoring-project-collapsed`
  - `vskill-sidebar-<agentId>-installed-collapsed` → `vskill-sidebar-<agentId>-available-project-collapsed`
  - `vskill-sidebar-<agentId>-global-collapsed` → `vskill-sidebar-<agentId>-available-personal-collapsed`
  Migration is idempotent, guarded by the flag `vskill.migrations.scope-rename.v1=done`, and has unit coverage for all three mappings plus the re-run case.
- [x] **AC-US3-05**: An API-boundary normalizer in `src/eval-ui/src/api.ts` accepts legacy `own/installed/global` strings from the server and translates them to the new 5-scope union for the duration of the 0688 overlap window, so 0688 can land on old names without blocking this increment. Contract tests in `api-provenance.test.ts` assert legacy-in → new-out for all three legacy values.
- [x] **AC-US3-06**: Enterprise as a concept is removed — no code path emits an Enterprise scope, no UI surface references it, and no test fixture asserts it.

---

### US-004: Plugin visibility under AVAILABLE (Claude Code only) (P1)
**Project**: vskill

**As a** Claude Code user with installed plugin skills
**I want** a read-only view of plugin skills under AVAILABLE > Plugins, nested by plugin name
**So that** I can see everything Claude can invoke right now, including `plugin:skill` namespaced skills

**Acceptance Criteria**:
- [ ] **AC-US4-01**: A new `scanInstalledPluginSkills(home)` function in `src/eval/plugin-scanner.ts` walks `<home>/.claude/plugins/cache/<marketplace>/<plugin>/skills/<skill>/SKILL.md` and emits one `SkillInfo` per SKILL.md with `scope="available-plugin"`, `pluginName=<plugin>`, `pluginMarketplace=<marketplace>`, and `pluginNamespace="<plugin>:<skill>"`.
- [ ] **AC-US4-02**: The scanner is a no-op (returns `[]`) when the active agent is not Claude Code.
- [ ] **AC-US4-03**: AVAILABLE > Plugins renders the returned skills as a tree — collapsible parent rows per `pluginName`, with member skills nested under each — using the shared `PluginGroup` component.
- [ ] **AC-US4-04**: Each nested skill row displays the `pluginNamespace` label (e.g. `anthropic-skills:pdf`) in `font-mono`.
- [ ] **AC-US4-05**: Fixture-based tests under `src/eval/__tests__/` exercise a sample `plugin-cache/` tree containing at least two marketplaces, three plugins, and five skills; assertions cover plugin-name grouping, namespace formatting, and non-CC no-op.

---

### US-005: Plugin-source authoring visibility (Claude Code only) (P1)
**Project**: vskill

**As a** plugin author developing Claude Code plugins inside my project
**I want** AUTHORING > Plugins to show every `.claude-plugin/plugin.json` manifest I am working on, with its in-development skills nested underneath
**So that** I can edit and iterate on plugin-bundled skills from the same sidebar that shows installed skills

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A new `scanAuthoredPluginSkills(projectRoot)` function in `src/eval/plugin-scanner.ts` globs `<projectRoot>/**/.claude-plugin/plugin.json` (excluding `node_modules`, `.git`, `dist`, `build`, `.specweave/cache`) with a default depth of 4, and for each manifest scans the sibling `skills/` directory.
- [ ] **AC-US5-02**: Each discovered skill is emitted with `scope="authoring-plugin"`, `pluginName=<directory name containing .claude-plugin>`, and `pluginManifestPath=<absolute path to plugin.json>`.
- [ ] **AC-US5-03**: The scanner is a no-op (returns `[]`) when the active agent is not Claude Code.
- [ ] **AC-US5-04**: AUTHORING > Plugins renders the returned skills grouped by plugin name using the shared `PluginGroup` component (same visual treatment as AVAILABLE > Plugins).
- [ ] **AC-US5-05**: Plugin-source detection excludes plugins that happen to be vendored under excluded paths; fixture tests verify that a `plugin.json` under `node_modules/` is never returned.

---

### US-006: Standalone authoring skills (P1)
**Project**: vskill

**As a** skill author writing skills that are not bundled in a plugin
**I want** AUTHORING > Skills to list every standalone skill I have under `<project>/skills/<skill>/SKILL.md`
**So that** I can see in-development skills that live in version control but aren't yet installed to `.claude/skills/` or `~/.claude/skills/`

**Acceptance Criteria**:
- [ ] **AC-US6-01**: A new `scanStandaloneSkills(projectRoot)` function in `src/eval/standalone-skill-scanner.ts` walks `<projectRoot>/skills/<skill>/SKILL.md` and emits one `SkillInfo` per SKILL.md with `scope="authoring-project"`.
- [ ] **AC-US6-02**: The scanner **skips** any SKILL.md whose ancestors contain a `.claude-plugin/plugin.json`; those skills are the responsibility of `scanAuthoredPluginSkills` and must not be double-counted.
- [ ] **AC-US6-03**: AUTHORING > Skills renders the returned skills as a flat list (no plugin nesting), counts always shown including `(0)`.
- [ ] **AC-US6-04**: The scanner runs regardless of active agent (standalone skills are cross-agent-friendly).
- [ ] **AC-US6-05**: Fixture tests cover: (a) a standalone skill outside any plugin source is included; (b) a SKILL.md nested inside a plugin source is excluded; (c) an empty `<root>/skills/` returns `[]` without error.

---

### US-007: Shadowing indication within AVAILABLE (P2)
**Project**: vskill

**As a** user who has the same skill name in multiple AVAILABLE sources
**I want** a visible precedence indicator that tells me which copy Claude actually invokes
**So that** I can reason about override behavior without diffing the filesystem

**Acceptance Criteria**:
- [ ] **AC-US7-01**: `scanSkills*` results within AVAILABLE are post-processed to compute `precedenceRank` — `personal=1`, `project=2` (lower wins); `available-plugin` rows set `precedenceRank=-1` (orthogonal, namespaced, never shadows non-plugin skills).
- [ ] **AC-US7-02**: When two AVAILABLE rows share the same skill name across `available-project` and `available-personal`, the higher-rank row sets `shadowedBy=<losing-scope>` on the shadowed row; the winning row has `shadowedBy=null`.
- [ ] **AC-US7-03**: Shadowed rows in the sidebar render an inline pill with the text `shadowed → <winning-source>` (provisional copy, finalized during T2); winning rows render no pill.
- [ ] **AC-US7-04**: Plugin skills are never marked as shadowed or shadowing against non-plugin skills — they live in their own namespace via `pluginNamespace` and don't collide by bare name.
- [ ] **AC-US7-05**: Shadowing logic is scoped to AVAILABLE only; AUTHORING rows never emit `shadowedBy`.

---

### US-008: Statusbar cleanup (P2)
**Project**: vskill

**As a** user with the `ProjectPicker` pill in the top-left header
**I want** the footer statusbar to stop duplicating the project path
**So that** the project identity is displayed in exactly one place and the statusbar can carry useful real-time state instead

**Acceptance Criteria**:
- [ ] **AC-US8-01**: `src/eval-ui/src/components/StatusBar.tsx` no longer renders the project-path display in its footer.
- [ ] **AC-US8-02**: `ProjectPicker` is mounted once, in the top-left of `StudioLayout`, as the single source of project identity in the UI.
- [ ] **AC-US8-03**: Snapshot tests for `StatusBar.tsx` and `StudioLayout.tsx` reflect the new layout; the absence of the footer path is asserted, not incidental.

## Functional Requirements

### FR-001: Workspace persistence schema
`~/.vskill/workspace.json` follows the `WorkspaceConfig` interface (`version: 1`, `activeProjectId`, `projects[]`). Atomic writes (temp-file + rename) avoid partial-state corruption. Deleting the file reverts Skill Studio to legacy single-project behavior when `--root` is provided.

### FR-002: Optional `EvalServerOptions.root`
`src/eval-server/eval-server.ts` resolves the effective `root` per request from `workspace.activeProjectId`. When no workspace exists and no `--root` is passed, endpoints return a zero-project empty-state payload rather than throwing.

### FR-003: Workspace REST endpoints
- `GET /api/workspace` — returns current `WorkspaceConfig`.
- `POST /api/workspace/projects` — adds a `ProjectConfig` (path validated, `id` computed from path hash, color dot derived deterministically).
- `DELETE /api/workspace/projects/:id` — removes a project; clears `activeProjectId` if it was the active one.
- `POST /api/workspace/active` — sets `activeProjectId`, updates `lastActiveAt`.

Contract tests in `api-workspace.test.ts` assert 400 on malformed payloads and 404 on missing ids.

### FR-004: Scanner aggregation
`skill-scanner.ts` orchestrates the source-specific scanners per active project:
- `scanInstalledSkills` (project + personal roots) → `available-project` / `available-personal`
- `scanInstalledPluginSkills(home)` → `available-plugin` (CC only)
- `scanStandaloneSkills(projectRoot)` → `authoring-project`
- `scanAuthoredPluginSkills(projectRoot)` → `authoring-plugin` (CC only)

Results are unioned, precedence-ranked (AVAILABLE only), and returned as a single `SkillInfo[]`.

### FR-005: Deterministic project color dot
`ProjectConfig.colorDot` is an OKLCH string computed deterministically from the absolute path hash — same path always produces the same color across machines and sessions, and stored only for UI convenience (not treated as authoritative).

### FR-006: Styling discipline
All new UI reuses Tailwind v4 tokens already in the codebase. No new color palette, no new typography scale, no new fonts. Paths and plugin namespaces render in `font-mono`. Group headers use the existing small-caps utility. Density preserved via `text-sm` + `leading-tight`.

## Success Criteria

- **Scope rename lands cleanly alongside 0688**: 0688 merges on legacy scope names unchanged; this increment rebases on top; normalizer removed one release after 0688 closes.
- **Multi-project switch is sub-second**: switching active project triggers a single React Query invalidation; the sidebar repopulates from the new scan result in under 1 second on a 500-skill workspace.
- **Zero regressions in non-CC agents**: Cursor, Windsurf, and other agents see exactly two AVAILABLE sub-sections (Project/Personal, Plugins absent) and one AUTHORING sub-section (Skills); snapshot tests pin this.
- **Migration is silent**: 100% of existing users with legacy `localStorage` scope keys see collapse state preserved on first load after upgrade; the migration flag ensures no second-run rewrite.
- **Plugin visibility is accurate**: for a test home with known plugin-cache contents, every installed plugin skill appears under AVAILABLE > Plugins; every authored plugin source in the active project appears under AUTHORING > Plugins.
- **Coverage**: unit ≥95% on new scanners and migration shim; integration ≥90% on workspace endpoints; Playwright E2E covers add-project → switch-project → sidebar-repopulates without cross-project contamination.

## Out of Scope

- **Filesystem auto-scan for projects** — phase 1 is manual add only; auto-discovery is phase 2+.
- **Bulk / workspace edit mode across projects** — no cross-project batch operations in this increment.
- **Enterprise scope** — removed entirely; no compat path, no UI hook, no test fixture.
- **Plugin install / uninstall affordances** — AVAILABLE > Plugins is strictly read-only in phase 1.
- **Manifest editor and "package & publish" wizard** — AUTHORING > Plugins only surfaces *visibility* of plugin sources, no editing flows.
- **Non-Claude-Code plugin formats** — only the Claude Code plugin spec (`.claude-plugin/plugin.json` + `skills/`) is recognized.
- **`.vskill-meta.json` sidecar migration** — deferred.
- **Drafts category** — explicitly dropped; AUTHORING is the home for in-development skills.

## Dependencies

- **0688-studio-skill-scope-transfer** (85% done, concurrent): operates on legacy `own/installed/global` strings. The API normalizer in `src/eval-ui/src/api.ts` translates at the server boundary during the overlap window so 0688 lands on old names and this increment rebases on top. No blocking relationship; the normalizer is removed one release after 0688 closes.
- **Claude Code plugin cache layout**: assumes `~/.claude/plugins/cache/<marketplace>/<plugin>/skills/<skill>/SKILL.md`. Verify against a real cache before T4 implementation; fixture tests pin the layout so future Claude Code changes are caught.
- **Anthropic docs vocabulary**: [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) and [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) are the source of truth for user-visible labels.
- **vskill CLI `--root` flag**: preserved for single-project users; auto-seeds workspace when none exists.

## Risks

| Risk | Mitigation |
|---|---|
| 0688-studio-skill-scope-transfer uses legacy scope strings | API normalizer in `api.ts` translates legacy → new at the boundary for one release; 0688 lands unblocked, this increment rebases on top. |
| Plugin source detection picks up `node_modules/**` or vendored deps | Glob excludes `node_modules`, `.git`, `dist`, `build`, `.specweave/cache`; fixture tests pin the exclusion. |
| Claude Code plugin cache layout assumption drifts | Verify against a real `~/.claude/plugins/cache/` before T4; fixtures mirror the real layout. |
| `showDirectoryPicker()` missing in Safari/Firefox | Text-path input fallback in `ProjectPicker` empty state. |
| `localStorage` migration races React mount | Synchronous call before `createRoot()` in `main.tsx`. |
| User deletes a project folder out-of-band | `loadWorkspace` validates each path; stale projects render muted with a "Remove" affordance. |
| Two-tier sidebar adds visual hierarchy users must learn | `GroupHeader` is visually quiet (small-caps, muted color); collapsible pattern reused within; fully reversible by removing the wrapper. |
| AUTHORING > Plugins false positives on a plugin source vendored as a dependency | Glob is depth-limited (default 4) and walks only the active project root; `node_modules` excluded. |
