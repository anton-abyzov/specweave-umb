---
increment: 0863-studio-folder-switch
title: "Skill Studio click-to-switch project folders"
type: feature
priority: P1
status: planned
created: 2026-05-31
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio click-to-switch project folders

## Overview

In Skill Studio, clicking a project in the top-left `ProjectPicker` dropdown does not switch
folders — it pops a modal instructing the user to quit and relaunch from a terminal
(`cd "{path}" && npx vskill@latest studio`). This makes multi-project work unusable from the app.

The scan root is captured **once at boot** (`eval-server.ts:85`) and frozen into every route
handler's closure, so even though `POST /api/workspace/active` already updates
`~/.vskill/workspace.json`, the running server keeps serving the original folder's skills. The
entire frontend switch pipeline (`useWorkspace.switchProject` → POST active → invalidate SWR
caches) already exists but is bypassed because the backend never re-roots.

This increment makes the running eval-server **re-root in place** when the active project changes,
re-enables the `ProjectPicker` to switch on click, adds a polished reload experience, and lets the
user open **any** folder (native dialog on desktop, path entry in npx). One code path works
identically in `npx vskill studio` (single process) and the desktop Tauri app, because the desktop
app's sidecar *is* this eval-server.

**Non-goals (deferred):** desktop sidecar respawn / "Reload from disk" hard-reset hatch. Option A
(runtime re-root) makes a restart unnecessary, so it is out of scope.

---

### US-001: Switch project by clicking the dropdown
**Project**: vskill

**As a** Skill Studio user
**I want** to click a project in the top-left dropdown and have the app switch to that folder
**So that** I can work across projects without quitting and relaunching from a terminal

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new `ActiveRootStore` (`getRoot`/`setRoot`/`reload`) holds the current scan root in memory, seeded at boot from the boot-resolved root.
- [x] **AC-US1-02**: All root-consuming route registrations read the root from `getRoot()` per request instead of a boot-captured constant, so the scan root can change without a process restart.
- [x] **AC-US1-03**: `POST /api/workspace/active` updates `ActiveRootStore` after persisting the active project, so a subsequent `GET /api/skills` scans the newly active folder.
- [x] **AC-US1-04**: Clicking a non-active project row in `ProjectPicker` calls `onSwitch(id)` (the existing wired pipeline) instead of showing the relaunch modal.
- [x] **AC-US1-05**: After switching, the skill list, agent list, and workspace state reflect the new project; the studio token and port are unchanged (same process).
- [x] **AC-US1-06**: Switching works identically whether served by `npx vskill studio` or the desktop Tauri sidecar (one HTTP code path, no mode branching on the happy path).

---

### US-002: Reload feedback while switching
**Project**: vskill

**As a** Skill Studio user
**I want** clear, immediate feedback when a switch is in progress
**So that** I trust the app is loading the new folder and don't double-click or assume it hung

**Acceptance Criteria**:
- [x] **AC-US2-01**: On click, the target row optimistically shows as active and the previous active row de-emphasizes before the round trip completes.
- [x] **AC-US2-02**: While skills refetch, the skill area keeps the prior content and the sidebar's existing loading state (no layout collapse or empty flash) until the new folder's skills arrive.
- [x] **AC-US2-03**: On success, a subtle auto-dismissing toast shows "Switched to {name} — {N} skills" using the `skillCount` from the switch response.
- [x] **AC-US2-04**: The picker is disabled (no re-entrant switches) while a switch is in flight; rapid double-clicks resolve to a single switch.
- [x] **AC-US2-05**: `switchProject` resolves only after the new skills have been refetched, so callers can transition UI state deterministically.

---

### US-003: Open any folder (not just registered ones)
**Project**: vskill

**As a** Skill Studio user
**I want** to browse to and open any folder on disk from the dropdown
**So that** I can switch to a project I haven't registered yet without using a terminal

**Acceptance Criteria**:
- [x] **AC-US3-01**: In the desktop app (`isTauriHost`), "Open folder…" launches a native directory picker; the chosen absolute path is registered and switched to.
- [x] **AC-US3-02**: In npx/browser mode, "Open folder…" presents the existing absolute-path entry (reliable fallback) which validates and registers the path.
- [x] **AC-US3-03**: After adding a folder, the app immediately switches to it (no extra click), reusing the US-001/US-002 switch+reload flow.

---

### US-004: Robust switching under failure & edge cases
**Project**: vskill

**As a** Skill Studio user
**I want** switching to fail safely and informatively
**So that** a bad folder or an in-flight job never corrupts my session

**Acceptance Criteria**:
- [x] **AC-US4-01**: Switching to a folder with no skills succeeds and shows an empty state ("No skills found in {name}"), not an error.
- [x] **AC-US4-02**: If the target path is missing/unreadable, `POST /api/workspace/active` returns `409 { ok:false, error, fallbackCommand }`, the server keeps serving the previous root, and the UI shows the (now error-only) cd-command modal.
- [x] **AC-US4-03**: Long-lived jobs (improve/sweep/eval) snapshot the root at job start, so a switch does not retarget a job already running.
- [x] **AC-US4-04**: No regression: launching with `--root <path>` or via `~/.vskill/workspace.json` resolves the same initial root as before.
