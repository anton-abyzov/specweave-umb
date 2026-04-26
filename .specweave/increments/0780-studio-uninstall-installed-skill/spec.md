---
increment: 0780-studio-uninstall-installed-skill
title: "Studio Uninstall Button for Installed Skills"
type: bug
priority: P2
status: active
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Uninstall Button for Installed Skills

## Overview

Studio currently has a "Delete" trash button on the DetailHeader that works for **source-authored** skills (origin="source"), routing through `DELETE /api/skills/:plugin/:skill` → OS trash. For **installed** skills (origin="installed", brought in via `vskill install`), the button is hidden because the read-only gate (`!isReadOnly`) excludes them. The user has no UI path to uninstall — only the CLI `vskill uninstall` works. This increment adds an "Uninstall" button on the read-only banner / DetailHeader for installed, lockfile-tracked skills.

**Out of scope**: changing the source-skill delete flow (already works), bulk uninstall, plugin-bundled skill removal (handled via the existing PluginActionMenu).

## User Stories

### US-001: Uninstall button visible on installed lockfile-tracked skills
**Project**: vskill

**As a** user viewing an installed skill in the studio
**I want** an Uninstall button on the detail header
**So that** I can remove the skill without dropping to the CLI

**Acceptance Criteria**:
- [x] **AC-US1-01**: When the selected skill has `origin === "installed"` AND `trackedForUpdates === true` (lockfile entry exists), the DetailHeader renders an "Uninstall" button.
- [x] **AC-US1-02**: When the selected skill is **plugin-bundled** (`origin === "installed"` AND `trackedForUpdates === false`), the Uninstall button is NOT rendered. The existing read-only banner stays unchanged.
- [x] **AC-US1-03**: When the selected skill is source-authored (`origin === "source"`), the Uninstall button is NOT rendered. The existing source "Delete" button continues to work.

### US-002: Uninstall flow with confirm + optimistic hide
**Project**: vskill

**As a** user clicking the Uninstall button
**I want** a confirmation dialog and a brief undo window
**So that** I don't accidentally lose a skill I configured

**Acceptance Criteria**:
- [x] **AC-US2-01**: Click → ConfirmDialog opens. Body reads "Uninstall &lt;skill&gt;? It will be sent to your &lt;Trash&gt; and the lockfile entry will be removed. You can re-install with `vskill install &lt;source&gt;`."
- [x] **AC-US2-02**: Confirm → optimistic hide via the existing `usePendingDeletion` machinery (10s undo). Cancel → no API call.
- [x] **AC-US2-03**: After 10s expires (or on user opt-in to delete sooner), `POST /api/skills/:plugin/:skill/uninstall` fires. On 200, the skill is gone from the sidebar permanently. On error, the optimistic hide reverses and a toast surfaces the failure.
- [x] **AC-US2-04**: Undo within the 10s window cancels the pending POST entirely — the skill stays installed.

### US-003: Server endpoint
**Project**: vskill

**As an** eval-server
**I want** to expose POST /api/skills/:plugin/:skill/uninstall
**So that** the studio can remove an installed skill safely

**Acceptance Criteria**:
- [x] **AC-US3-01**: `POST /api/skills/:plugin/:skill/uninstall` reads `vskill.lock` from the project root, removes the entry whose key matches `:skill`, and writes the file back. Returns `{ ok: true, removedFromLockfile: boolean, trashedDir: string | null }`.
- [x] **AC-US3-02**: After the lockfile update, the on-disk skill directory is routed through the `trash` package (same pattern as the existing `DELETE /api/skills/:plugin/:skill`). Symlinks installed by other agents (e.g. `.cursor/skills/<name>`) are also removed.
- [x] **AC-US3-03**: When the skill is in the lockfile but the on-disk directory is already missing → `removedFromLockfile: true`, `trashedDir: null`, status 200 (idempotent).
- [x] **AC-US3-04**: When the on-disk directory exists but no lockfile entry (side-loaded) → trash the dir, `removedFromLockfile: false`, status 200.
- [x] **AC-US3-05**: When neither the lockfile entry NOR the disk directory exist → 404 with `{ code: "not-installed" }`.
- [x] **AC-US3-06**: Path-traversal hardening: the resolved skill directory MUST be inside the project root (validated via `path.resolve()` + `startsWith()`).

## Non-Functional Requirements

- **Reversibility**: Uninstall routes to OS trash, NOT a hard `rm -rf`. The user can recover from Trash / Recycle Bin / XDG.
- **Cross-platform**: `trash` package handles macOS / Linux / Windows.
- **Performance**: O(1) lockfile read+write + one `trash()` call.
- **Accessibility**: Button has a clear `aria-label`, the ConfirmDialog is keyboard-accessible (existing infra).

## Out of Scope

- Source-skill delete flow (already works).
- Bulk uninstall.
- Plugin-bundled skill uninstall (PluginActionMenu owns that).
- Hard `rm -rf` mode (trash is intentional).

## References

- `src/eval-server/api-routes.ts:2648-2651` — existing trash flow for source skills
- `src/eval-ui/src/components/DetailHeader.tsx:399-435` — existing Delete button + dispatch
- `src/eval-ui/src/App.tsx:321+` — ConfirmDialog + pendingDeletion event listeners
- `src/eval-ui/src/hooks/usePendingDeletion.ts` — 10s undo buffer
- `vskill.lock` — JSON shape: `{ skills: { [name]: { version, sha, ... } } }`
