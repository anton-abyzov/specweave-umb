# Tasks: Skill Studio — Delete authored skills (OS trash + Undo)

> Order is RED → GREEN → REFACTOR. No implementation before failing test.

## Phase 1: Backend (TDD)

### T-001: RED — backend unit tests for DELETE handler
**User Story**: US-001, US-003, US-005 | **Satisfies ACs**: AC-US1-04, AC-US3-03, AC-US5-01, AC-US5-02 | **Status**: [x]

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes-delete.test.ts`
- **TC-001 — plugin guard**: Given a skill with `origin === "installed"`, When DELETE arrives, Then response is 403 and the mocked `trash` is NOT called.
- **TC-002 — happy path**: Given a skill with `origin === "source"`, When DELETE arrives, Then `trash` is called once with the resolved absolute skill dir, response is `{ ok: true }`.
- **TC-003 — missing folder**: Given a non-existent skill path, When DELETE arrives, Then response is 404.
- **TC-004 — trash failure**: Given `trash` throws, When DELETE arrives, Then response is 500 with `{ error }`.

**Status**: [x] Done

### T-002: GREEN — add `trash` dep + replace `rmSync` in DELETE handler
**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-04, AC-US5-01 | **Status**: [x]

**Implementation Details**:
- Add `"trash": "^9"` to `repositories/anton-abyzov/vskill/package.json` dependencies.
- In `src/eval-server/api-routes.ts` DELETE handler, replace `rmSync(skillDir, { recursive: true, force: true })` with `await (await import("trash")).default([skillDir])`.
- Add try/catch → 500 with classified error.
- T-001 tests must pass.

**Status**: [x] Done

## Phase 2: Frontend hooks (TDD)

### T-003: RED — `usePendingDeletion` hook tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x]

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/usePendingDeletion.test.ts`
- **TC-001 — cancel within window**: Given an enqueued delete, When `cancelDelete` is called within 10s, Then `api.deleteSkill` is NOT called.
- **TC-002 — fire after window**: Given an enqueued delete, When 10s elapses without cancel, Then `api.deleteSkill` is called exactly once with the right `(plugin, skill)`.
- **TC-003 — flush all pending**: Given two deletes enqueued at different times, When `flushPending` is called, Then both fire immediately and the internal map is empty.
- **TC-004 — failure event**: Given a delete that resolves with `{ ok: false, error }`, When the timer fires, Then the hook emits a failure event so the caller can roll back.

**Status**: [x] Done

### T-004: GREEN — implement `usePendingDeletion`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x]

**Implementation Details**:
- Create `hooks/usePendingDeletion.ts`. API per plan.md.
- Internal map keyed by `${plugin}/${skill}`.
- `useEffect` registers `beforeunload` → `flushPending()`.
- T-003 tests must pass.

**Status**: [x] Done

## Phase 3: Frontend UI

### T-005: RED — ContextMenu delete-action tests
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01, AC-US3-02 | **Status**: [x]

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ContextMenu.delete.test.tsx`
- **TC-001 — plugin disabled**: Given a skill with `scopeV2 === "available-plugin"`, When ContextMenu renders, Then the `Delete` item has `aria-disabled="true"` and shows the plugin tooltip on hover/focus.
- **TC-002 — personal enabled**: Given a skill with `scopeV2 === "available-personal"`, When ContextMenu renders, Then `Delete` is enabled and click invokes the delete handler.
- **TC-003 — authoring enabled**: Given a skill with `scopeV2 === "authoring-project"`, When ContextMenu renders, Then `Delete` is enabled.

**Status**: [x] Done

### T-006: GREEN — wire `delete` action into ContextMenu + dispatcher
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US3-01, AC-US3-02 | **Status**: [x]

**Implementation Details**:
- Extend `ContextMenu.tsx` actions union with `"delete"` (label `Delete`, destructive style).
- Conditional `disabled: true` + tooltip when `scopeV2 === "available-plugin"`.
- In `useContextMenuState.ts`, route `delete` action to a new `requestDelete(skill)` dispatcher that opens ConfirmDialog.
- T-005 tests must pass.

**Status**: [x] Done

### T-007: GREEN — ConfirmDialog component
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-02, AC-US4-01 | **Status**: [x]

**Implementation Details**:
- Create `components/ConfirmDialog.tsx`: title, body, Cancel (default focus) + destructive action button.
- Escape cancels, Enter on focused destructive button confirms.
- Body text adapts per platform: macOS → "system Trash", Win → "Recycle Bin", else → "Trash".
- Accessibility: `role="alertdialog"`, `aria-labelledby`, focus trap, restore focus on close.

**Status**: [x] Done

### T-008: GREEN — DetailHeader migrates off `window.confirm()`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [x]

**Implementation Details**:
- Replace `window.confirm(...)` in `components/DetailHeader.tsx` (~line 384) with the new ConfirmDialog flow via the same dispatcher used by the context menu.

**Status**: [x] Done

### T-009: GREEN — wire optimistic remove + Undo toast
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-03, AC-US1-05, AC-US2-01, AC-US4-02 | **Status**: [x]

**Implementation Details**:
- On confirm: optimistically remove the skill from `StudioContext.skills`.
- Show toast `Deleted <skill-name>` with `action: { label: "Undo", onInvoke: ... }`, `durationMs: 10_000`.
- First-of-session: prepend `"Sent to your system Trash. Open Trash to restore."` subline (track `useRef<boolean>` flag in App-level provider).
- On Undo: cancel pending, restore via `optimisticRestore(skill)`.
- On timer-fire failure: restore + error toast with Retry action.

**Status**: [x] Done

### T-010: REFACTOR — extract platform-trash-name helper
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x]

**Implementation Details**:
- If duplication appears between ConfirmDialog body and the first-of-session toast subline, extract a `getTrashLabel()` helper into `lib/platform.ts`.

**Status**: [x] Done

## Phase 4: Verification

### T-011: Run all tests
**Status**: [x] Done
- `cd repositories/anton-abyzov/vskill && npm test -- --run`
- All new tests pass; existing tests remain green.
- Verified 2026-04-25: 21 tests across 4 files green (api-routes-skill-delete, delete-endpoint, ContextMenu.delete, usePendingDeletion).

### T-012: Manual smoke (macOS)
**User Story**: US-001, US-002, US-005 | **Satisfies ACs**: AC-US1-04, AC-US2-03, AC-US5-01 | **Status**: [x]
- Start the studio: `cd repositories/anton-abyzov/vskill && npm run dev:eval-ui`.
- Author a throwaway skill via `+ New Skill` flow.
- Right-click → Delete → Confirm → click Undo → verify row returns and folder still on disk.
- Right-click → Delete → Confirm → wait 11s → verify folder is gone from disk and present in `~/.Trash`.
- Right-click a plugin skill (PLUGINS section) → verify Delete is grayed with tooltip.

### T-013: Document Windows VM check (defer)
**Status**: [x] Deferred — documented as follow-up
- A Windows Recycle Bin smoke test is intentionally deferred to a follow-up — `trash@^9` is widely used and platform-tested upstream, and the cross-platform contract is enforced via mocking in `api-routes-skill-delete.test.ts`. Track a follow-up if Windows verification is required before release.
