# Implementation Plan: Skill Studio — Delete authored skills (OS trash + Undo)

## Overview

Two-layer change with strict reuse of existing primitives.

**Backend** (vskill eval-server, `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:1742-1768`):
- Keep the existing plugin-guard logic (returns 403 when `classifyOrigin(skillDir, root) === "installed"`).
- Replace `rmSync(skillDir, { recursive: true, force: true })` with `await trash([skillDir])`.
- Preserve current 404 behavior when the skill folder no longer exists.
- Wrap the `trash` call in a try/catch and surface failures as 500 with `{ error: <classified message> }`.

**Frontend** (vskill eval-ui):
1. **`ConfirmDialog` component** (new, minimal, accessible) replaces `window.confirm()` in `DetailHeader.tsx` and is opened by the new `delete` context-menu action.
2. **`usePendingDeletion` hook** (new) owns the 10s buffer:
   - `enqueueDelete(skill)` — start a timer; on fire, calls `api.deleteSkill(plugin, skill)` and emits a result event.
   - `cancelDelete(skillKey)` — clear the timer; no API call made.
   - `flushPending()` — fire all pending immediately (used in `beforeunload`).
   - Internal map: `Map<skillKey, { timeoutId, skill }>`.
3. **`ContextMenu`** (`components/ContextMenu.tsx:21-29`) gains a `delete` action with conditional `disabled` + tooltip when `scopeV2 === "available-plugin"`.
4. **`useContextMenuState`** (`hooks/useContextMenuState.ts:56-94`) wires the delete action: opens ConfirmDialog → on confirm, optimistically remove from `StudioContext.skills`, enqueue deletion, show toast with Undo action.
5. **`DetailHeader`** trash button (`components/DetailHeader.tsx:380-408`) calls the same dispatcher (no more `window.confirm()`).

## Architecture

### Components

- **`ConfirmDialog`** — accessible `role="alertdialog"` with focus trap, Escape cancels, default focus on Cancel.
- **`usePendingDeletion`** — owns the 10s buffer. Map<skillKey, { timeoutId, skill }>. Fires `api.deleteSkill` on timer or on `flushPending()`.
- **`StudioContext.optimisticRemove` / `optimisticRestore`** — local state mutators added to the existing context to support optimistic UI.

### Data Model

No persistence. All state is in-memory (`StudioContext`) plus the OS trash on the filesystem.

### API Contracts

- `DELETE /api/skills/:plugin/:skill` — existing route. Behavior change only: `rmSync` → `trash`. Plugin guard preserved.

## Technology Stack

- **Backend**: Node.js (vskill eval-server, ESM), `trash` npm package (>= v9, MIT, no native deps).
- **Frontend**: React 19, Vitest + React Testing Library, custom ToastProvider.

**Architecture Decisions**:
- **OS trash over custom trash dir**: User explicitly preferred. Platform-native UX, eliminates restore endpoint + Recently-Deleted view + sidecar metadata. Trade-off: no in-app restore (user opens OS Trash app). Mitigated by 10s Undo buffer.
- **Optimistic UI + buffered API call**: Undo cancels the *pending API call* (no backend restore needed). Trade-off: row briefly disappears before the actual move. Acceptable — user perceives instant feedback, and disk state matches UI state once buffer flushes.
- **`trash` package over native `child_process` calls**: Cross-platform out of the box. Maintained by sindresorhus, widely used. Trade-off: extra dep (~small).

## Component diagram

```
ContextMenu (delete action)
        │
        ▼
useContextMenuState (dispatch)
        │
        ▼
ConfirmDialog ──► (cancel) end
        │
       (confirm)
        │
        ▼
StudioContext.optimisticRemove(skillKey)
        │
        ▼
usePendingDeletion.enqueueDelete(skill)
        │
        ├──(undo within 10s)──► cancelDelete → StudioContext.restore(skill)
        │
        └──(timer fires)──────► api.deleteSkill(plugin, skill)
                                      │
                                      ├──(ok)──► (no-op, list already updated)
                                      │
                                      └──(err)─► restore + error toast (Retry)
```

## Implementation Phases

### Phase 1: Backend — TDD
- T-001: RED — backend unit tests for DELETE handler.
- T-002: GREEN — add `trash` dep + replace `rmSync`.

### Phase 2: Frontend hooks — TDD
- T-003: RED — `usePendingDeletion` tests.
- T-004: GREEN — implement `usePendingDeletion`.

### Phase 3: Frontend UI — TDD
- T-005: RED — ContextMenu delete-action tests.
- T-006: GREEN — wire `delete` action.
- T-007: GREEN — ConfirmDialog component.
- T-008: GREEN — DetailHeader migrates off `window.confirm()`.
- T-009: GREEN — wire optimistic remove + Undo toast.
- T-010: REFACTOR — extract platform-trash-name helper if duplicated.

### Phase 4: Verification
- T-011: Run all tests (`npm test -- --run`).
- T-012: Manual smoke on macOS.
- T-013: Document Windows VM check (defer if not covered).

## Reuse — do not reinvent

- `ToastProvider` + `Toast.action: { label, onInvoke }` — already supports Undo / Retry buttons.
- `useOptimisticAction` pattern (`hooks/useOptimisticAction.ts:48-119`).
- `classifyOrigin` (`src/eval/skill-scanner.ts:189-201`) — backend discriminator unchanged.
- `useSkillUpdates` SSE stream — list invalidation across tabs.
- `api.deleteSkill(plugin, skill)` (`api.ts:425-426`) — signature unchanged.

## Testing Strategy

- **Backend**: Vitest unit tests with `vi.mock("trash")` so we don't actually hit the OS trash in CI.
- **Frontend**: Vitest + React Testing Library; `vi.useFakeTimers()` for the 10s buffer test.
- **Manual smoke**: macOS dev environment — author a skill, delete, wait, verify in `~/.Trash`.

## Technical Challenges

### Challenge 1: 10s buffer + tab close
**Solution**: `beforeunload` listener calls `flushPending()` synchronously with `keepalive: true` fetches.
**Risk**: Browser may still kill the request mid-flight on aggressive close; the skill already exists optimistically removed from UI. Worst case: user sees the skill restored on next reload, which is recoverable.

### Challenge 2: Cross-volume trash on Linux
**Solution**: `trash` package handles XDG copy-fallback internally. We add a test that mocks a cross-volume rejection to ensure 500 + restore happens.

### Challenge 3: ESM dynamic import of `trash`
**Solution**: Use `await (await import("trash")).default([skillDir])` so we can mock it cleanly with `vi.mock("trash", () => ({ default: vi.fn() }))`.

## Files touched

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill/package.json` | Add `trash` dep |
| `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (~line 1742-1768) | Swap `rmSync` for `trash`; keep guard |
| `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes-delete.test.ts` (new) | Backend unit tests |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ContextMenu.tsx` | Add `delete` action |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ConfirmDialog.tsx` (new) | Accessible dialog |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx` (~line 380-408) | Replace `window.confirm()` |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/usePendingDeletion.ts` (new) | 10s buffer hook |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useContextMenuState.ts` (~line 56-94) | Wire delete dispatcher |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/usePendingDeletion.test.ts` (new) | Hook tests |
| `repositories/anton-abyzov/vskill/src/eval-ui/src/__tests__/ContextMenu.delete.test.tsx` (new) | Menu state tests |
