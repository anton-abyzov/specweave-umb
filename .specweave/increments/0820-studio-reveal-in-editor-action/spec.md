---
increment: 0820-studio-reveal-in-editor-action
title: Studio Reveal in Editor action
type: bug
priority: P2
status: completed
created: 2026-05-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Reveal in Editor action

## Overview

The Studio sidebar context menu exposes **Open**, **Reveal in Editor**, and **Edit** items, but all three currently show the same stub toast — `"Edit lands with 0675. Open the file in your editor."` — because the underlying server endpoint was never built. The "0675" reference is itself stale (0675 is the unrelated skill-creator detection hotfix).

This increment wires the three actions to a new `POST /api/skills/reveal-in-editor` endpoint that resolves the user's preferred editor (`$VISUAL` → `$EDITOR` → `code` → `cursor` → OS default) and spawns it on the skill's `SKILL.md` (Reveal/Edit) or directory (Open). Failure modes are surfaced via real toast strings; the placeholder is removed.

## User Stories

### US-001: Reveal in Editor opens SKILL.md (P2)
**Project**: vskill

**As a** Studio user
**I want** Reveal in Editor to actually open the skill's SKILL.md in my editor
**So that** I can read or modify it without manually navigating to the file

**Acceptance Criteria**:
- [x] **AC-US1-01**: Right-clicking a skill row and selecting "Reveal in Editor" sends `POST /api/skills/reveal-in-editor` with `{ plugin, skill, file: "SKILL.md" }`.
- [x] **AC-US1-02**: On 200, the UI shows the toast "Opening in editor…" (info).
- [x] **AC-US1-03**: The server resolves the editor in this order — `$VISUAL` → `$EDITOR` → `code` (if on PATH) → `cursor` (if on PATH) → OS default (`open` on darwin, `xdg-open` on linux, `cmd /c start` on win32) — and spawns it detached so the response returns immediately.
- [x] **AC-US1-04**: `$VISUAL="code --reuse-window"` resolves to `command="code"`, `args=["--reuse-window", "<absolute-skill-md-path>"]`.
- [x] **AC-US1-05**: When no editor can be located anywhere, the server returns 500 `{ error: "no_editor" }` and the UI shows the toast "No editor found. Set $VISUAL or $EDITOR, or install code/cursor."

### US-002: Open opens the skill folder (P2)
**Project**: vskill

**As a** Studio user
**I want** the Open menu item to open the skill's folder in my editor
**So that** I can browse all the files in the skill, not just SKILL.md

**Acceptance Criteria**:
- [x] **AC-US2-01**: Right-clicking a skill row and selecting "Open" sends `POST /api/skills/reveal-in-editor` with `{ plugin, skill }` (no `file`).
- [x] **AC-US2-02**: The server spawns the editor on the skill **directory** (not `SKILL.md`) and returns 200.
- [x] **AC-US2-03**: The UI shows "Opening in editor…" on success.
- [x] **AC-US2-04**: For source-origin skills, "Edit" routes through the same flow as "Reveal in Editor" (opens `SKILL.md`).

### US-003: Server is hardened against path-traversal (P2)
**Project**: vskill

**As a** vskill maintainer
**I want** the new endpoint to reject malicious requests
**So that** a localhost-CSRF-style attack cannot use it to launch arbitrary files

**Acceptance Criteria**:
- [x] **AC-US3-01**: The handler **never trusts a client-supplied dir path**. The dir is re-resolved server-side via `scanSkillInstallLocations(canonical, root)`, picking the highest-precedence install (project > personal > plugin). Note: `scanSkillInstallLocations` resolves by skill *slug* (the last `/`-segment) and ignores the plugin namespace at the resolver level. The resolved dir is also basename-guarded server-side (`basename(dir) !== skill` → 404). This is acceptable for a localhost API surface where any installed skill is already enumerable via `GET /api/skills`; tightening the resolver to filter plugin-scope hits by `pluginSlug` is a follow-up if cross-plugin namespacing becomes a real concern.
- [x] **AC-US3-02**: When `(plugin, skill)` does not resolve to any install location, the server returns 404 `{ error: "skill_not_found" }`.
- [x] **AC-US3-03**: When `file` is provided, it is validated as a clean basename — requests containing `/`, `\`, or any `..` segment get 400 `{ error: "invalid_file" }`.
- [x] **AC-US3-04**: When `file` is a clean basename but does not exist on disk, the server returns 404 `{ error: "file_not_found" }`.
- [x] **AC-US3-05**: The editor command is launched via `spawn` with an argv array (no shell) — no shell interpolation. The resolved path is appended as the **last** argv element so `$VISUAL`-supplied flags cannot displace it.

### US-004: Stale placeholder is removed (P2)
**Project**: vskill

**As a** Studio user
**I want** the "Edit lands with 0675…" copy to disappear
**So that** I never see a stale reference to a different increment

**Acceptance Criteria**:
- [x] **AC-US4-01**: `strings.actions.editPlaceholder` is removed from `src/eval-ui/src/strings.ts`.
- [x] **AC-US4-02**: No UI-copy hits for the literal string `"0675"` remain in `src/eval-ui/src/strings.ts` (test files are fine).
- [x] **AC-US4-03**: `strings.toasts` gains four new entries: `openingInEditor`, `noEditor`, `openFailed`, `skillNotFound`.

## Functional Requirements

### FR-001: Editor resolution helper
A new pure module `src/eval-server/utils/resolve-editor.ts` exporting `resolveEditorCommand(target, env, platform, which)` that returns `{ command, args }`. Pure (no I/O on import); accepts `env`, `platform`, and `which` as injected parameters so tests can pin them deterministically.

### FR-002: New endpoint
`POST /api/skills/reveal-in-editor` registered alongside the other skill routes in `src/eval-server/api-routes.ts`, using the existing `readBody` + `sendJson` pattern.

### FR-003: UI API method
`api.revealInEditor(plugin, skill, file?)` added to the `api` object in `src/eval-ui/src/api.ts`, mirroring the `setConfig` pattern (`fetchJson` + `JSON.stringify` body).

### FR-004: Context-menu router wiring
`handleContextMenuAction` in `src/eval-ui/src/hooks/useContextMenuState.ts` splits the collapsed `open|reveal|edit` placeholder into three real branches that call `api.revealInEditor` and dispatch real success/failure toasts.

## Success Criteria

- Right-click → Reveal in Editor on any installed skill opens SKILL.md in the user's editor.
- Right-click → Open opens the skill folder in the user's editor.
- All four failure paths surface a meaningful toast (no silent failures, no stale "0675" copy).
- Path-traversal and arbitrary-file attempts are rejected with 4xx.
- All new code is covered by unit tests; the existing useContextMenuState test gains regression cases for the un-collapsed branches.

## Out of Scope

- Native in-Studio inline editing (the original "Edit lands with 0675" promise) — explicitly deferred.
- Per-user editor preferences UI; honoring `$VISUAL` / `$EDITOR` is sufficient.
- Windows packaging tweaks beyond the `cmd /c start` fallback.
- E2E Playwright run for this increment — covered by manual smoke + unit/integration tests.

## Dependencies

- Reuses `scanSkillInstallLocations` (registry-aware skill-dir resolver with traversal defenses).
- Reuses `readBody` / `sendJson` from `src/eval-server/router.ts`.
- Reuses `fetchJson` / `ApiError` from `src/eval-ui/src/api.ts`.
