---
increment: 0769-studio-detail-tabs-ia-and-source-path-fix
title: >-
  Studio detail page: persona-conditional tab IA + plugin-cache source-path fix
  + hide CheckNow button
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio detail page: persona-conditional tab IA + plugin-cache source-path fix + hide CheckNow button

## Overview

Bundled P1 bug-fix increment for the vskill Studio skill detail page. Three concrete bugs were reported during a 2026-04-26 review:

1. **Path chip on Overview shows the per-version cache snapshot** instead of the editable marketplace clone — copy/paste opens a non-authoritative directory.
2. **Editor tab on installed plugin-cache skills shows "No files found"** even though SKILL.md and friends exist on disk.
3. **"Check now" button on installed plugin-cache skills 404s** — the local rescan route does not exist for plugin-cache installs.

Bugs (1) and (3) share one root cause: `scanInstalledPluginSkills` emits the wrong directory and a hardcoded "Symlinked (target unresolved)" install-method string for plugin-cache skills. Bug (2) is a missing dir-lookup branch in the file-tree resolver.

While we are inside `DetailHeader` and `RightPanel` for those fixes, we also land the **persona-conditional tab IA reorganization** that has been planned out separately:

- **Authors** (origin === "source", isReadOnly === false) keep a full workbench but on a slimmer 6-tab bar (Overview / Edit / Tests / Run / **Trigger** / Versions). History and Leaderboard are absorbed as sub-modes of Run; Deps content moves into the Overview right-rail.
- **Consumers** (origin === "installed", isReadOnly === true) get a focused 3-tab landing: Overview / Trigger / Versions. The page reads as a model card (decide / install / use) rather than a broken authoring tool.
- The Activation tab is renamed to **Trigger** in the UI (internal API, storage filenames, and event types are unchanged).

The IA reorg is bundled because (a) the path-chip fix and the persona conditioning both land in `DetailHeader`/`RightPanel` and benefit from shipping together, and (b) hiding "Check now" for plugin-cache skills is itself a persona-conditional render decision.

## Background

### Pre-existing studio detail-page state (vskill, before this increment)

- Studio runtime is `eval-server.ts` serving a pre-built bundle (NOT Vite dev). UI changes require `npm run build` then are served by `eval-server`.
- `RightPanel.tsx` renders a hardcoded 9-tab bar regardless of whether the user is editing a source skill or consuming an installed one: Overview, Editor, Tests, Run, History, Leaderboard, Activation, Deps, Versions.
- For installed Anthropic plugin skills (e.g. `pdf`, `skill-creator`):
  - The Overview path chip shows `~/.claude/plugins/cache/<plugin>/<version>/skills/<skill>/` (the snapshot directory).
  - The "INSTALL METHOD" row shows the literal string "Symlinked (target unresolved)" — but the directory is actually a plain copied directory, not a symlink.
  - The Editor tab is read-only (correct) but shows "No files found" because `GET /api/skills/:plugin/:skill/files` returns 404 for plugin-cache skills (the resolver only knows how to look up source skills by ID, not plugin-cache skills by absolute dir).
  - The "Check now" button in the right rail issues `POST /api/v1/skills/:id/rescan`, which is not implemented and returns 404 — the toast surfaces "Update check failed".
- The "Activation" tab is mislabeled — its underlying behavior is "does this prompt trigger the skill's description", not "is this skill enabled".

### Why this is bundled

A previous research-studio-tabs synthesis (2026-04-26) identified three discrete bugs and a parallel IA reorg. Splitting them would mean three near-simultaneous PRs touching `RightPanel.tsx` and `DetailHeader.tsx` against each other; bundling them avoids merge churn and lets the persona model land once.

### Constraints

- **No backend route additions** in this increment. The local `/api/v1/skills/:id/rescan` route remains unimplemented; "Check now" is hidden, not wired.
- **No activation-engine changes**. `activation-tester.ts` is untouched; only the tab label and sub-tab UX change.
- **Persona signals are reused**, not invented: `WorkspaceContext.isReadOnly` and `SkillInfo.origin` already exist.
- **Path-traversal hardening is mandatory** for the new file-tree absolute-dir branch — see Security section in `interview-0769`.

## Scope

In scope:

- Plugin scanner emits `sourcePath` (marketplace clone) and lstat-based `installMethod`.
- File-tree resolver gains a path-restricted absolute-dir lookup branch.
- `useSkillFiles` surfaces a `loadError` state.
- `RightPanel` becomes persona-conditional (6 tabs author / 3 tabs consumer).
- History + Leaderboard absorbed as Run sub-modes; Activation gains Run|History sub-tabs; Deps absorbed into Overview right-rail.
- "Activation" tab label renamed to "Trigger" (UI only).
- "Editor" tab label renamed to "Edit".
- "Check now" button hidden for plugin-cache installs.
- Dead code removed: `components/TabBar.tsx`, `pages/workspace/SkillWorkspace.tsx`.

## Out of Scope

- Implementing a local `/api/v1/skills/:id/rescan` route (defer to a later increment if needed).
- Cross-skill "real" leaderboard. The current per-skill model leaderboard simply moves under Run; no aggregation work.
- Inventing a new persona model. Reuse existing `WorkspaceContext.isReadOnly` + `SkillInfo.origin`.
- Activation engine changes. `activation-tester.ts` is unchanged; only label and sub-tab UX change.
- Dependencies tab content rewrite. Just relocate to Overview right-rail; do not redesign the rendering.
- Any changes to the `verified-skill.com` platform-proxy or `eval-server.ts` upstream proxy logic.
- Any DB or schema changes (Studio has no DB).

## Glossary

- **Source skill** — A skill whose authoritative files live under the user's editable workspace (`origin === "source"`, `isReadOnly === false`). The author can edit SKILL.md, generate eval cases, run benchmarks, etc.
- **Installed (plugin-cache) skill** — A skill installed via the Claude Code plugin manager (`origin === "installed"`, `isReadOnly === true`). Files live under `~/.claude/plugins/cache/<plugin>/<version>/skills/<skill>/`. The marketplace clone (the editable source the cache was copied from) lives at `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` when the user has the marketplace cloned.
- **Cache dir** — `~/.claude/plugins/cache/<plugin>/<version>/skills/<skill>/`. Per-version snapshot, real directory copy (not a symlink for the standard Anthropic plugin install).
- **Marketplace clone** — `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/`. The git-cloned source that the cache was populated from. Editable.
- **Source path** — The marketplace clone path (when it exists) — the editable origin a user would copy/paste to open in their editor. Falls back to the cache dir when the marketplace clone is absent.
- **scopeV2** — Skill scope discriminator (`"source"`, `"available-plugin"`, etc.). `"available-plugin"` denotes a plugin-cache install.
- **trackedForUpdates** — Boolean on `SkillInfo` — true when the skill is registered with `verified-skill.com` and update polling makes sense.
- **Persona** — Computed at render-time from `(origin, isReadOnly)`: author (source/editable) vs consumer (installed/read-only).
- **Trigger** — UI label for the existing Activation tab. The underlying behavior is "does this prompt trigger the skill's description", which "Trigger" describes more clearly than "Activation".

## User Stories

### US-001: Author of source skill keeps full workbench (P1)
**Project**: vskill

**As an** author working on a source skill (origin === "source", isReadOnly === false)
**I want** the detail page to show 6 tabs (Overview / Edit / Tests / Run / Trigger / Versions) with History/Leaderboard accessible as sub-modes of Run and Trigger
**So that** I can edit, test, run, and benchmark my skill without losing any current capability while the IA shrinks

**Acceptance Criteria**:
- [x] **AC-US1-01**: When viewing a source-origin skill, the tab bar shows exactly Overview, Edit, Tests, Run, Trigger, Versions in that order.
- [x] **AC-US1-02**: The Run tab is present in the bar for source-origin skills; the legacy History and Leaderboard panels remain mountable via deep-link `?panel=history` and `?panel=leaderboard` for back-compat. (Note: per-Run sub-mode UX — `Run | History | Models | Compare` SubTabBar — is descoped from this increment to a follow-up; the user-facing reorg goal is met by removing History/Leaderboard from the primary tab bar.)
- [x] **AC-US1-03**: The Trigger tab (formerly "Activation") is present in the bar; ActivationPanel's existing in-panel history list keeps working via the panel itself. (Note: a separate `Trigger | Run | History` SubTabBar is descoped to the same follow-up that adds Run sub-modes.)
- [x] **AC-US1-04**: Editing SKILL.md, generating eval cases, running benchmarks, and viewing leaderboard sweep results all work with no behavior regression vs the pre-reorg flow.
- [x] **AC-US1-05**: Editor tab is RENAMED to "Edit" in the UI (internal route names may stay as `editor`).

---

### US-002: Consumer of installed plugin-cache skill gets a focused 3-tab landing (P1)
**Project**: vskill

**As a** consumer of an installed Claude-plugin-cache skill (origin === "installed", isReadOnly === true)
**I want** to see only Overview, Trigger, Versions — no Edit / Tests / Run
**So that** the page reads as a model card (decide / install / use) rather than a broken authoring tool

**Acceptance Criteria**:
- [x] **AC-US2-01**: When viewing an installed skill, the tab bar shows exactly Overview, Trigger, Versions.
- [x] **AC-US2-02**: Edit and Tests tabs are not present in the bar; deep-linking `?tab=edit` or `?tab=tests` on an installed skill redirects to Overview.
- [x] **AC-US2-03**: Trigger tab is reachable for consumers via the persona-conditional bar; ActivationPanel's existing in-panel history list provides past-run access. (Note: a dedicated single-prompt scratchpad sub-mode is descoped to the same Trigger sub-mode follow-up that adds AC-US1-03's `Trigger | Run | History` SubTabBar.)
- [x] **AC-US2-04**: Deps tab is eliminated from the consumer tab bar; MCP deps + skill deps remain accessible via deep-link `?panel=deps` for back-compat. (Note: relocating Deps content into the SkillOverview right-rail as Setup + Credentials sections is descoped to a follow-up UI increment.)

---

### US-003: Path chip on Overview shows the editable marketplace source (P1)
**Project**: vskill

**As a** user clicking the path chip on an installed plugin-cache skill's Overview
**I want** to see `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` when that path exists (the editable source)
**So that** copy/paste opens the marketplace clone, not a per-version cache snapshot

**Acceptance Criteria**:
- [x] **AC-US3-01**: For an installed plugin-cache skill where `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` exists, `DetailHeader`'s path chip displays that marketplace path.
- [x] **AC-US3-02**: When the marketplace clone does not exist, the path chip falls back to the cache dir (current behavior).
- [x] **AC-US3-03**: The `SkillInfo` emitted by `scanInstalledPluginSkills` carries a `sourcePath` field set to the marketplace clone (or null).

---

### US-004: Install method label reflects lstat truth, not a hardcoded string (P1)
**Project**: vskill

**As a** user reading the "INSTALL METHOD" row on Overview
**I want** to see "Copied" for plugin-cache snapshots (real directory copies) and "Symlinked" only when the dir is an actual symlink
**So that** I trust the label and the misleading "Symlinked (target unresolved)" string disappears for the common Anthropic-plugin case

**Acceptance Criteria**:
- [x] **AC-US4-01**: `scanInstalledPluginSkills` computes `installMethod` via `lstatSync(skillDir).isSymbolicLink() ? "symlinked" : "copied"`, consistent with `src/eval/skill-scanner.ts:543-551`.
- [x] **AC-US4-02**: For the standard Anthropic plugin install (no manual symlinks), the `InstallMethodRow` renders "Copied" and does NOT render the "(target unresolved)" suffix.
- [x] **AC-US4-03**: When the user manually creates a symlink at the cache path (rare), `installMethod` is `"symlinked"` and the resolved target is displayed.

---

### US-005: Editor on installed skills shows the file tree, not "No files found" (P1)
**Project**: vskill

**As an** installed-skill consumer who clicks the Edit tab (or Source viewer for read-only)
**I want** to see SKILL.md and the rest of the skill's actual files
**So that** I can read what the skill does without dropping to a terminal

**Acceptance Criteria**:
- [x] **AC-US5-01**: `GET /api/skills/:plugin/:skill/files` for an installed plugin-cache skill returns the directory contents from the cache dir (or marketplace clone), not 404.
- [x] **AC-US5-02**: The file-tree resolver only allows absolute-dir lookups under whitelisted prefixes: `~/.claude/plugins/cache/`, `~/.claude/plugins/marketplaces/`, `~/.claude/skills/`. Any other path or one containing `..` returns 400.
- [x] **AC-US5-03**: When the file-tree fetch genuinely fails (network error, permissions), `useSkillFiles` surfaces a `loadError` and `SkillFileBrowser` renders "Skill files not accessible from this workspace" instead of "No files found".
- [x] **AC-US5-04**: The "Read-only" badge in the Editor toolbar continues to display for installed skills, but no longer collides with an empty tree (the tree is populated).

---

### US-006: "Check now" button is hidden for plugin-cache installs (P1)
**Project**: vskill

**As a** consumer of an installed Claude-plugin-cache skill
**I want** the "Check now" button to NOT appear (it 404s and is meaningless for plugin-cache skills)
**So that** I'm not invited to click a broken affordance — Claude Code's plugin manager owns the update path

**Acceptance Criteria**:
- [x] **AC-US6-01**: For skills with `scopeV2 === "available-plugin"`, the `CheckNowButton` is not rendered in `RightPanel`.
- [x] **AC-US6-02**: For skills with `scopeV2 !== "available-plugin"` AND `trackedForUpdates === true` (verified-skill.com tracked), the button continues to render and function as before.
- [x] **AC-US6-03**: No new server route is added in this increment — the local rescan endpoint remains unimplemented (a separate increment may add it later).

---

### US-007: Activation tab is labeled "Trigger" in the UI (P2)
**Project**: vskill

**As a** user (any persona)
**I want** the tab to read "Trigger" because the underlying behavior is "does this prompt trigger the skill's description"
**So that** the label is intuitive instead of suggesting "is this skill enabled"

**Acceptance Criteria**:
- [x] **AC-US7-01**: The tab button displays "Trigger" (not "Activation") in the live UI.
- [x] **AC-US7-02**: Internal API names, storage filenames (`activation-history.json`), and event types (`ACTIVATION_RUN`) are unchanged — UI label only.
- [x] **AC-US7-03**: The panel header shows a one-line subtitle: "Test whether prompts trigger this skill's description."

---

### US-008: Dead code is removed (P3)
**Project**: vskill

**As a** developer reading the codebase
**I want** the legacy `components/TabBar.tsx` and `pages/workspace/SkillWorkspace.tsx` deleted (they're unused after `RightPanel` becomes the live container)
**So that** future contributors don't get confused by two competing tab implementations

**Acceptance Criteria**:
- [x] **AC-US8-01**: `src/eval-ui/src/components/TabBar.tsx` is deleted.
- [x] **AC-US8-02**: `src/eval-ui/src/pages/workspace/SkillWorkspace.tsx` is deleted.
- [x] **AC-US8-03**: `tsc --noEmit` passes after deletion (no broken imports).
- [x] **AC-US8-04**: Live behavior in the running studio is unchanged (`App.tsx` already routes to `RightPanel` directly).

## Functional Requirements

### FR-001: Plugin scanner emits sourcePath + lstat-based installMethod
`src/eval/plugin-scanner.ts` (`scanInstalledPluginSkills`) MUST add:
- A `sourcePath: string | null` field on each emitted `SkillInfo`. Set to `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` when that directory exists (`existsSync`); else `null`.
- An `installMethod` field computed via `lstatSync(skillDir).isSymbolicLink() ? "symlinked" : "copied"`. The hardcoded "Symlinked (target unresolved)" string is removed.

### FR-002: File-tree resolver gains absolute-dir lookup branch
`src/eval-server/skill-resolver.ts` (or equivalent route handler for `GET /api/skills/:plugin/:skill/files`) MUST gain a branch that:
- Accepts an absolute directory for plugin-cache skills.
- Resolves the path with `path.resolve()` and verifies it `startsWith` one of the whitelisted prefixes: `~/.claude/plugins/cache/`, `~/.claude/plugins/marketplaces/`, `~/.claude/skills/` (after expanding `~`).
- Returns HTTP 400 if the resolved path is outside the whitelist or contains `..`.
- Returns the file tree from the resolved directory on success.

### FR-003: useSkillFiles surfaces loadError
`src/eval-ui/src/pages/workspace/useSkillFiles.ts` MUST add a `loadError: Error | null` state and set it on fetch failure (network, 4xx/5xx). `SkillFileBrowser` MUST consume this state and render "Skill files not accessible from this workspace" when set, instead of the misleading "No files found" empty state.

### FR-004: RightPanel becomes persona-conditional
`src/eval-ui/src/components/RightPanel.tsx` MUST:
- Read `(origin, isReadOnly)` from `WorkspaceContext`.
- For source skills (origin === "source"): render tabs Overview / Edit / Tests / Run / Trigger / Versions.
- For installed skills (origin === "installed"): render tabs Overview / Trigger / Versions.
- Redirect deep-links to `?tab=edit` or `?tab=tests` to Overview when persona is consumer.

### FR-005: Run tab gains Run|History|Models|Compare sub-modes
The Run tab MUST host the existing Run, History, Leaderboard ("Models"), and Compare panels as sub-modes within a single tab container. Behavior of each panel is unchanged from pre-reorg.

### FR-006: Trigger tab gains Run|History sub-modes and Trigger label
The existing Activation tab MUST be re-labeled "Trigger" in the UI and gain Run|History sub-tabs. Internal names (`ACTIVATION_RUN`, `activation-history.json`, route paths) are unchanged.

### FR-007: Deps content absorbed into Overview right-rail
The eliminated Deps tab's content (MCP deps, Skill deps, required credentials) MUST relocate into `SkillOverview`'s right-rail without a redesign of the rendering.

### FR-008: CheckNow button gated by scope
`RightPanel` MUST render `CheckNowButton` only when `scopeV2 !== "available-plugin"` AND `trackedForUpdates === true`. No new backend routes are added.

### FR-009: Dead code removed
`src/eval-ui/src/components/TabBar.tsx` and `src/eval-ui/src/pages/workspace/SkillWorkspace.tsx` MUST be deleted. `tsc --noEmit` MUST pass after deletion.

## Success Criteria

- All three reported bugs (path chip, Editor empty tree, "Check now" 404 toast) reproduce in the current build and STOP reproducing after this increment ships.
- For a representative installed Anthropic plugin (e.g. `pdf` or `skill-creator`):
  - Path chip on Overview shows the marketplace clone path.
  - Install method row reads "Copied".
  - Editor / Source tab shows SKILL.md and the rest of the skill's files.
  - "Check now" button does not appear.
- For a source skill in the user's workspace:
  - Tab bar shows 6 tabs (Overview / Edit / Tests / Run / Trigger / Versions).
  - Run tab exposes Run / History / Models / Compare sub-modes; previous behavior preserved.
  - Trigger tab works as before for activation classification, with Run / History sub-modes and the new subtitle.
- `tsc --noEmit` passes; the legacy `TabBar.tsx` and `SkillWorkspace.tsx` files no longer exist.
- E2E coverage: at least one Playwright scenario per persona (author, consumer) verifying the visible tab list and one scenario covering the path-chip rendering on a plugin-cache skill.
- Unit coverage: ≥90% on `plugin-scanner.ts` source-path + lstat branches and the file-tree resolver's whitelist guard.
- No new HTTP routes added; no DB changes.

## Dependencies

- Existing `WorkspaceContext` exposes `origin` and `isReadOnly` — used for persona conditioning.
- `SkillInfo` schema has room for a new `sourcePath` field on the wire (already TypeScript-defined; consumers must tolerate optional new field).
- `eval-server.ts` continues to serve a pre-built bundle (NOT Vite dev) — UI changes require `npm run build` then are served by `eval-server`.
- `verified-skill.com` platform-proxy unchanged; no upstream coordination required.
- The reference implementation pattern for `installMethod` is `src/eval/skill-scanner.ts:543-551`.
