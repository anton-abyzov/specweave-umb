---
increment: 0793-vskill-studio-plugin-authoring-paths
title: 'vskill Studio: First-class plugin authoring paths'
type: bug
priority: P2
status: completed
created: 2026-04-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill Studio — First-class plugin authoring paths

## Overview

vskill Studio's discovery logic is correct: when a folder contains `.claude-plugin/plugin.json` plus `<folder>/skills/<skill>/SKILL.md`, the skills correctly nest under AUTHORING > PLUGINS via `scopeV2: "authoring-plugin"`. The user-visible bug is that **no first-class authoring path produces a plugin.json**:

- `vskill skill new` and the `skill-builder` skill emit only `SKILL.md`.
- Studio's Create-Skill modal `mode: "new-plugin"` is buried behind a modal toggle.
- `claude plugin` CLI has no `new`/`create`/`init` subcommand.

The user's URL `localhost:3109/#/skills/hi-anton/hi-there` already nests skills under their parent dir as the "owner" segment, but the sidebar contradicts that by flattening `authoring-project` skills. Result: a folder like `~/Projects/TestLab/hi-anton/` with three skills appears as 3 flat AUTHORING > SKILLS entries with AUTHORING > PLUGINS empty.

This increment adds four additive lanes:

- **Lane A** — `vskill plugin new <name> [--with-skill <s>]` CLI.
- **Lane B1** — Sidebar groups `authoring-project` skills under their parent dir when 2+ siblings exist.
- **Lane B2** — `POST /api/authoring/convert-to-plugin` endpoint + Studio "Convert to plugin" CTA.
- **Lane C** — `skill-builder` SKILL.md gains a "plugin authoring" section.
- **Lane D** — Create-Skill modal copy/order: "Plugin (multi-skill)" becomes a peer top-level mode.

Schema validation is delegated to `claude plugin validate <path>` so vskill never duplicates Claude Code's plugin schema.

## User Stories

### US-001: Scaffold a plugin from the CLI (P1)
**Project**: vskill

**As a** vskill user authoring multiple related skills
**I want** a single CLI command that scaffolds a plugin folder with manifest and (optionally) a first skill
**So that** I don't have to hand-write `plugin.json` or know which mode in the Studio modal to pick

**Acceptance Criteria**:
- [x] **AC-US1-01**: `vskill plugin new my-plugin` creates `my-plugin/.claude-plugin/plugin.json` with valid schema (name, description, author).
- [x] **AC-US1-02**: `vskill plugin new my-plugin --with-skill greet` additionally scaffolds `my-plugin/skills/greet/SKILL.md` using the existing skill-emitter helper.
- [x] **AC-US1-03**: `vskill plugin new my-plugin --description "..."` writes the description into the manifest.
- [x] **AC-US1-04**: After scaffolding, the command runs `claude plugin validate my-plugin` (when `claude` is on PATH); on validator failure, the manifest is unlinked and the validator's stderr is printed.
- [x] **AC-US1-05**: Re-running `vskill plugin new my-plugin` against an existing plugin folder fails with a clear error and does not overwrite the manifest.
- [x] **AC-US1-06**: Invalid kebab-case names (`MyPlugin`, `my plugin`, `my_plugin`) are rejected before any filesystem write.

---

### US-002: See standalone skills grouped under their parent folder in the sidebar (P1)
**Project**: vskill

**As a** Studio user with a folder of skills that don't (yet) have a manifest
**I want** the sidebar to show those skills grouped under the folder name, not flattened
**So that** the sidebar matches the URL's existing `<folder>/<skill>` ownership and I can see at a glance which skills belong together

**Acceptance Criteria**:
- [x] **AC-US2-01**: When 2+ `authoring-project` skills share the same `plugin` (parent dir) field, the sidebar renders a collapsible group header for that dir with the skills nested underneath (matching `PluginTreeGroup` styling).
- [x] **AC-US2-02**: The group header shows a small "Not a plugin yet" pill plus a "Convert →" link.
- [x] **AC-US2-03**: A folder with exactly one skill renders flat (no spurious group of 1).
- [x] **AC-US2-04**: Existing AUTHORING > PLUGINS section (real plugins with manifests) is unchanged.
- [x] **AC-US2-05**: The skill detail panel and URL routing are unchanged — only the sidebar grouping changes.

---

### US-003: Promote a folder of standalone skills into a plugin from Studio (P1)
**Project**: vskill

**As a** Studio user
**I want** a one-click action that writes `.claude-plugin/plugin.json` into a candidate folder and turns it into a real plugin
**So that** I don't have to drop to the terminal or hand-write JSON

**Acceptance Criteria**:
- [x] **AC-US3-01**: Clicking "Convert →" on the parent-dir group (or the empty-state CTA in AUTHORING > PLUGINS) opens a dialog with the name prefilled to the folder basename. Description is left blank for the user to fill (the dialog accepts an optional `initialDescription` prop for future package.json-based prefill — deferred as a UX polish).
- [x] **AC-US3-02**: Submitting the dialog `POST`s to `/api/authoring/convert-to-plugin` with `{ anchorSkillDir, pluginName, description }` (anchor = absolute path of any skill in the candidate group; the server derives `pluginDir = dirname(dirname(anchorSkillDir))` to keep client-side path math out of the contract).
- [x] **AC-US3-03**: The endpoint writes `<pluginDir>/.claude-plugin/plugin.json` using the same `pluginJsonScaffold()` helper as `mode: "new-plugin"`, then runs `claude plugin validate <pluginDir>`.
- [x] **AC-US3-04**: On validation failure the endpoint deletes the manifest and returns 422 with the validator's stderr; the dialog displays the error and the sidebar is unchanged.
- [x] **AC-US3-05**: On success the frontend re-fetches `/api/skills` and the dir flips from `authoring-project` group to `authoring-plugin` group with skills nested.
- [x] **AC-US3-06**: The endpoint rejects: anchorSkillDir outside the workspace root (400 `anchor-outside-root`), anchorSkillDir whose parent is not `skills/` (400 `invalid-anchor-shape`), manifest already exists at the resolved pluginDir (409), invalid kebab-case pluginName (400), pluginDir without any `skills/*/SKILL.md` (400 `no-skills-to-convert`).

---

### US-004: Plugin authoring is documented in skill-builder (P2)
**Project**: vskill

**As a** future agent invocation of `skill-builder`
**I want** clear guidance on when to scaffold a plugin instead of a standalone skill
**So that** users describing a multi-skill bundle land on the plugin path automatically

**Acceptance Criteria**:
- [x] **AC-US4-01**: `skill-builder/SKILL.md` has a new "Authoring a plugin (multi-skill bundle)" section that documents the three concrete paths (`vskill plugin new`, Studio "new-plugin" mode, "Convert to plugin" CTA).
- [x] **AC-US4-02**: The section includes a heuristic: "if the user describes 2+ related skills under a shared identity, prefer plugin mode over standalone."
- [x] **AC-US4-03**: Skill-builder version in SKILL.md is bumped (1.0.3 → 1.0.4) so vskill-platform shows the update.

---

### US-005: Plugin mode is discoverable in the Create-Skill modal (P2)
**Project**: vskill

**As a** Studio user opening Create Skill
**I want** "Plugin (multi-skill)" to be presented as a peer top-level mode, not buried in a sub-toggle
**So that** I pick it without having to hunt

**Acceptance Criteria**:
- [x] **AC-US5-01**: The Create-Skill modal lists three peer modes: "Standalone skill", "Add to existing plugin", "Plugin (multi-skill)" — in that order.
- [x] **AC-US5-02**: "Plugin (multi-skill)" mode shows a one-line caption: "Creates `<folder>/.claude-plugin/plugin.json` and `<folder>/skills/<first>/SKILL.md`."
- [x] **AC-US5-03**: Existing POST `/api/authoring/create-skill` request bodies are unchanged (mode names: `"standalone" | "existing-plugin" | "new-plugin"`).

## Functional Requirements

### FR-001: `pluginJsonScaffold()` is the single source of truth
The helper in `src/eval-server/authoring-routes.ts:77` is the only writer of `plugin.json` content. Lane A's CLI imports it; Lane B2's endpoint imports it. No duplication.

### FR-002: `claude plugin validate` integration
Both Lane A and Lane B2 invoke `claude plugin validate <path>` as a child process after writing the manifest. If `claude` is not on PATH, validation is soft-skipped with a warning. On non-zero exit, the manifest is removed and the validator's stderr is surfaced to the user.

### FR-003: No regression in discovery / dedupe
Existing precedence in `dedupeByDir()` (`skill-scanner.ts:205`) — `authoring-plugin > authoring-project` — must be preserved. After Lane B2 writes a manifest, the next `/api/skills` fetch must show the affected skills with `scopeV2: "authoring-plugin"`, not duplicated under both scopes.

### FR-004: Sidebar grouping is purely client-side
Lane B1 does NOT change the backend response shape. The grouping happens in `partitionByGroupSource()` over the existing flat `SkillInfo[]`. The skill's `scopeV2` stays `authoring-project` until a manifest is actually written.

## Success Criteria

- A user who runs `vskill plugin new my-plug --with-skill first` ends up with a folder that opens in `vskill studio` showing `my-plug` under AUTHORING > PLUGINS with `first` nested.
- A user with the existing `~/Projects/TestLab/hi-anton/` (no manifest, 3 skills) sees `hi-anton` as a sidebar group with the 3 skills nested AND a "Convert →" CTA. One click + dialog promotes it to a real plugin.
- All existing vitest specs pass; no regression in `0740` dedupe tests.
- `claude plugin validate <path>` succeeds on every plugin scaffolded by either path.

## Out of Scope

- Reorganizing already-installed plugins under `~/.claude/plugins/cache/`.
- Marketplace publishing flows (`marketplace.json` generation/sync).
- Renaming `plugin` field on `SkillInfo` (would touch lockfiles).
- Changing `scopeV2` semantics or dedupe precedence.
- A "demote plugin to standalone" reverse flow.

## Dependencies

- `claude` CLI on PATH for validation (soft dependency — soft-skip if absent).
- Existing `pluginJsonScaffold()` in `src/eval-server/authoring-routes.ts`.
- Existing skill-emitter in `src/core/skill-emitter.ts` (reused by Lane A `--with-skill`).
- Existing `PluginTreeGroup` component for sidebar grouping reuse.
