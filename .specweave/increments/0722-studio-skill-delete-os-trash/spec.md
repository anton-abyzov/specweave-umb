---
increment: 0722-studio-skill-delete-os-trash
title: "Skill Studio: Delete authored skills (OS trash + Undo)"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio — Delete authored skills (OS trash + Undo)

## Overview

The Skill Studio (vskill eval-ui) currently has no UI affordance to delete a skill. Users who experiment with the "+ New Skill" flow accumulate dead skills they cannot remove without dropping to the filesystem.

This increment adds a safe, simple delete flow:

- User-owned skills (Authoring + user-owned Available) get a Delete action.
- Plugin-installed skills stay read-only — the menu item shows disabled with an explanatory tooltip.
- Deletes go to the **OS trash** (macOS Trash / Windows Recycle Bin / Linux XDG) via the `trash` npm package — no custom in-app trash dir.
- A 10-second **Undo toast** buffers the backend call so accidental deletes never reach the OS trash.

Why OS trash over a custom recycle bin: the user explicitly preferred it. It's the platform's standard, the user already knows how to use it, and it eliminates a whole subsystem (custom trash dir, restore endpoints, "Recently Deleted" view).

## User Stories

### US-001: Delete a user-owned skill from the Studio (P1)
**Project**: vskill

**As a** Skill Studio user
**I want** to delete a skill I own directly from the sidebar
**So that** I can clean up authoring scratch and personal skills without dropping to the shell.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Right-clicking a skill where `scopeV2 ∈ { available-project, available-personal, authoring-project, authoring-plugin }` shows an enabled `Delete` menu item.
- [x] **AC-US1-02**: Selecting Delete opens a `ConfirmDialog` titled `Delete "<skill-name>"?` with body text naming the OS trash as the destination, focus on the Cancel button by default, Escape cancels.
- [x] **AC-US1-03**: Confirming the dialog optimistically removes the skill row from the sidebar list immediately and shows a toast `Deleted <skill-name>` with an `Undo` action and a 10-second auto-dismiss.
- [x] **AC-US1-04**: After the 10-second window elapses, the backend `DELETE /api/skills/:plugin/:skill` is invoked exactly once and the skill folder is moved to the OS trash (verified by absence on disk + presence in `~/.Trash` on macOS).
- [x] **AC-US1-05**: If the backend call fails, the row is restored to the list and the toast switches to an error variant `Couldn't delete: <reason>` with a `Retry` action.
- [x] **AC-US1-06**: Clicking the trash icon in `DetailHeader` triggers the same flow (no `window.confirm()`).

---

### US-002: Undo a delete before it commits (P1)
**Project**: vskill

**As a** Skill Studio user
**I want** a brief window to undo a delete I just confirmed
**So that** an accidental click never destroys a skill I needed.

**Acceptance Criteria**:
- [x] **AC-US2-01**: The toast shown after delete confirmation has a clearly labeled `Undo` action button.
- [x] **AC-US2-02**: Clicking `Undo` before the 10s timer fires cancels the pending backend call (no DELETE request issued) and restores the skill row to the sidebar list.
- [x] **AC-US2-03**: The skill folder remains untouched on disk after Undo.
- [x] **AC-US2-04**: Closing the browser tab while a delete is pending flushes pending deletes via `beforeunload` so the OS trash receives the skill (no silent data loss in the limbo state).

---

### US-003: Plugin skills cannot be deleted (P1)
**Project**: vskill

**As a** Skill Studio user with plugin-installed skills
**I want** the Delete option to be visibly unavailable for plugin skills, with a clear explanation
**So that** I never accidentally delete plugin-managed content and I understand why I can't.

**Acceptance Criteria**:
- [x] **AC-US3-01**: For skills with `scopeV2 === "available-plugin"`, the context menu shows `Delete` rendered as **disabled** (grayed out, not clickable, `aria-disabled="true"`).
- [x] **AC-US3-02**: Hovering / focusing the disabled `Delete` item shows a tooltip with text `Plugin skills are managed by their owning plugin — uninstall the plugin to remove.`
- [x] **AC-US3-03**: The backend continues to reject DELETE for plugin/installed-origin skills with HTTP 403 (defense-in-depth — request never originates from the UI for these).

---

### US-004: User understands where deleted skills go (P2)
**Project**: vskill

**As a** new Skill Studio user
**I want** clear notification of where deleted skills land
**So that** I know how to recover a skill if needed.

**Acceptance Criteria**:
- [x] **AC-US4-01**: The `ConfirmDialog` body explicitly names the platform's trash: `system Trash` (macOS), `Recycle Bin` (Windows), or `Trash` (Linux), adapted via `navigator.platform`.
- [x] **AC-US4-02**: The first delete in a session shows an additional toast subline `Sent to your system Trash. Open Trash to restore.` Subsequent deletes in the same session omit the subline.

---

### US-005: Cross-platform behavior (P2)
**Project**: vskill

**As a** Skill Studio user on any supported OS
**I want** the delete to behave correctly on macOS, Windows, and Linux
**So that** the feature works consistently across my workstations.

**Acceptance Criteria**:
- [x] **AC-US5-01**: Backend uses the `trash` npm package (>= v9, MIT, no native deps) so deletion routes to the OS-native trash on all three platforms.
- [x] **AC-US5-02**: `trash` rejection (e.g., volume crossing on Linux without copy-fallback, permission denied) surfaces as HTTP 500 with `{ error: <classified message> }` and the frontend restores the row + shows error toast.

## Success Criteria

- 100% of context-menu interactions on `available-plugin` skills render Delete disabled (verified by component test).
- Zero `rmSync` calls remain in the DELETE handler (verified by grep + test).
- Manual smoke on macOS confirms the deleted skill folder appears in `~/.Trash` after the 10s window.

## Out of Scope

- Custom in-app "Recently Deleted" / restore UI — OS trash covers this.
- Bulk / multi-select delete.
- Empty-trash UI — the OS handles that.
- Per-project trash directories.

## Dependencies

- `trash` npm package (sindresorhus, MIT) — added to `repositories/anton-abyzov/vskill/package.json`.
- Existing `classifyOrigin()` plugin discriminator in `src/eval/skill-scanner.ts`.
- Existing `ToastProvider` action API and `useOptimisticAction` rollback pattern.
