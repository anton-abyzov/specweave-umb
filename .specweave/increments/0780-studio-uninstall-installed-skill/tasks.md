# Tasks: Studio Uninstall Button for Installed Skills

## Phase 1 — Server endpoint (US-003)

### T-001: RED+GREEN — POST /api/skills/:plugin/:skill/uninstall happy path
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given a project root with vskill.lock containing `skills.greet-anton` and a real `.claude/skills/greet-anton/SKILL.md`, When POST /api/skills/greet-anton/greet-anton/uninstall, Then the lockfile entry is removed AND the skill dir is trashed AND response is `{ ok: true, removedFromLockfile: true, trashedDir: <path> }`.
**File**: `src/eval-server/__tests__/api-skill-uninstall.test.ts` (new) + `src/eval-server/api-routes.ts`.

### T-002: RED+GREEN — idempotent edge cases
**User Story**: US-003 | **AC**: AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed
**Test Plan**: Three table-driven cases — (a) lockfile entry exists, disk dir missing → ok with trashedDir=null; (b) disk dir exists, no lockfile entry → ok with removedFromLockfile=false; (c) neither → 404 `{ code: "not-installed" }`.
**File**: same as T-001.

### T-003: GREEN — path-traversal guard
**User Story**: US-003 | **AC**: AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given `:skill = "../../../../etc/passwd"` (URL-encoded), the handler returns 400 `{ code: "invalid-skill-name" }` BEFORE touching the filesystem. Verify via mocked `trash`/`existsSync` — never called.
**File**: same as T-001.

## Phase 2 — Client API + UI

### T-004: RED+GREEN — api.uninstallSkill
**User Story**: US-001, US-002 | **AC**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Mock fetch to return `{ ok: true, removedFromLockfile: true, trashedDir: "/tmp/x" }`. Assert `api.uninstallSkill("plugin", "skill")` resolves to that shape.
**File**: `src/eval-ui/src/__tests__/api-uninstall.test.ts` (new) + `src/eval-ui/src/api.ts`.

### T-005: RED — DetailHeader Uninstall button visibility
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test Plan**: Three render cases — (a) origin=installed + trackedForUpdates=true → button visible; (b) origin=installed + trackedForUpdates=false (plugin-bundled) → button absent; (c) origin=source → button absent (existing Delete still renders).
**File**: `src/eval-ui/src/components/__tests__/DetailHeader-uninstall.test.tsx` (new).

### T-006: GREEN — render Uninstall button + dispatch event
**User Story**: US-001 | **AC**: AC-US1-01..03 | **Status**: [x] completed
**Test Plan**: T-005 passes. Click dispatches `studio:request-uninstall` with `{ skill }`.
**File**: `src/eval-ui/src/components/DetailHeader.tsx`.

### T-007: GREEN — App.tsx listener wires uninstall to ConfirmDialog + usePendingDeletion
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**: With usePendingDeletion mocked, dispatching `studio:request-uninstall` opens the ConfirmDialog with the uninstall body copy; confirming schedules via the buffer; canceling within 10s does not call api.uninstallSkill.
**File**: `src/eval-ui/src/App.tsx` + extend the existing `pending-deletion` test if straightforward, else focused App-level event test.

## Phase 3 — Verify + sync

### T-008: Run vitest sweep
**User Story**: cross-cutting | **Status**: [x] completed
**Test Plan**: All new + touched suites green. tsc clean.

### T-009: Sync living docs
**User Story**: cross-cutting | **Status**: [x] completed
**Test Plan**: `specweave sync-living-docs 0780-studio-uninstall-installed-skill` exits 0.
