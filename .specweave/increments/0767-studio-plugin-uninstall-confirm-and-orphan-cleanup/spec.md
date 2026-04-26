---
status: completed
---
# 0767 — Studio plugin uninstall: ConfirmDialog + orphan-cache cleanup

## Problem

User clicks `... > Uninstall` on `skill-creator` (or any plugin) in the Skill Studio sidebar. Two failure modes today:

1. **Ugly confirmation** — uses `window.confirm()` instead of the existing accessible `<ConfirmDialog>` component (already used for skill delete in `App.tsx`).
2. **Silent failure for orphan plugins** — when a plugin only exists in `~/.claude/plugins/cache/<marketplace>/<name>/<hash>/` (with `.orphaned_at` marker) but is NOT in `~/.claude/plugins/installed_plugins.json`:
   - `claude plugin uninstall <name>` returns `Plugin "<name>" not found in installed plugins` (exit 1).
   - Server returns `{ ok: false, error }` with HTTP 200, frontend shows tiny red text inside the dropdown — easy to miss.
   - Cache directory remains, so the scanner (`scanInstalledPluginSkills` in `src/eval/plugin-scanner.ts`) keeps surfacing the plugin on next load.

User-visible: "Uninstall doesn't work."

## User stories

### US-001: Beautiful confirmation dialog

**As a** Skill Studio user
**I want** a polished modal confirmation when I click Uninstall
**So that** I don't get ambushed by a system dialog

- [x] AC-US1-01: Click `... > Uninstall` opens `<ConfirmDialog>` with destructive variant
- [x] AC-US1-02: Title says "Uninstall <plugin-name>?"; body explains it removes the plugin and its skills
- [x] AC-US1-03: Cancel / Esc / overlay click → no API call made; menu closes
- [x] AC-US1-04: Confirm → API call proceeds; the menu and dialog close

### US-002: Successful uninstall feedback

**As a** Skill Studio user
**I want** a clear toast when uninstall succeeds
**So that** I know the action completed

- [x] AC-US2-01: Successful uninstall shows toast `"Uninstalled <plugin>"` (severity: success)
- [x] AC-US2-02: Plugin disappears from sidebar after refresh

### US-003: Orphan-cache cleanup fallback

**As a** Skill Studio user
**I want** orphaned plugin cache directories to be cleaned up automatically
**So that** "ghost" plugins don't keep reappearing

- [x] AC-US3-01: When `claude plugin uninstall` returns non-zero with stderr/stdout containing "not found in installed plugins", the server scans `~/.claude/plugins/cache/*/<name>/` for matching dirs.
- [x] AC-US3-02: If at least one orphan dir exists, the server removes it recursively and returns `{ ok: true, fallback: "orphan-cache-removed", removed: [paths] }`.
- [x] AC-US3-03: If no orphan dir exists either, the server returns `{ ok: false, error: <claude stderr> }` so the original error surfaces.
- [x] AC-US3-04: Cleanup is constrained to paths under `~/.claude/plugins/cache/` — `path.resolve(target).startsWith(cacheRoot + sep)` guard.

### US-004: Visible error feedback on failure

**As a** Skill Studio user
**I want** a toast on uninstall failure
**So that** I see the error even if I closed the menu

- [x] AC-US4-01: When `ok: false`, show toast with severity "error" containing the error message
- [x] AC-US4-02: The dropdown menu also keeps the small inline error for context

## Out of scope

- Disable confirmation (no destructive action, keep the existing one-click Disable)
- Re-architecting the plugin scanner to filter against `installed_plugins.json` (separate concern; orphan cleanup here is reactive, not preventative)
