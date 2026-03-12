# Implementation Plan: Skill Studio Delete Skill

## Overview

Add a delete-skill feature across three layers: a DELETE endpoint on the eval server, a client API method, and a delete button with confirmation in the DetailHeader UI component. The implementation reuses existing infrastructure (`resolveSkillDir`, `classifyOrigin`, `rmSync`, `useStudio` context) with no new dependencies. Approximately 80 lines of new code across 5 files.

## Architecture

### Component Boundaries

```
DetailHeader.tsx                    api.ts                     api-routes.ts
 [Delete button]  ──onClick──>  api.deleteSkill()  ──DELETE──>  DELETE /api/skills/:p/:s
   + confirm()                                                    resolveSkillDir()
   + isRunning guard                                              classifyOrigin() → 403
   + isReadOnly guard                                             existsSync() → 404
                                                                  rmSync({ recursive, force })
                                                                  → { ok: true }
```

### Data Flow

1. User clicks trash icon in DetailHeader (visible only when `!isReadOnly`)
2. Browser `window.confirm()` dialog asks "Delete skill {name}? This cannot be undone."
3. On confirm: `api.deleteSkill(plugin, skill)` sends `DELETE /api/skills/:plugin/:skill`
4. Server resolves path via `resolveSkillDir()`, checks origin via `classifyOrigin()`, validates existence, removes directory
5. On success: `refreshSkills()` + `clearSelection()` via StudioContext

### API Contract

```
DELETE /api/skills/:plugin/:skill

Response 200: { "ok": true }
Response 403: { "error": "Cannot delete installed (read-only) skill" }
Response 404: { "error": "Skill directory not found" }
Response 500: { "error": "<message>" }
```

## Technology Stack

No new dependencies. Uses existing:
- **Server**: `rmSync` from `node:fs` (cross-platform, recursive), `classifyOrigin` from `skill-scanner.ts`, `resolveSkillDir` from `skill-resolver.ts`
- **Client**: `fetchJson` wrapper already in `api.ts`
- **UI**: React, `useStudio` + `useWorkspace` hooks, `window.confirm()` for confirmation

**Architecture Decisions**:
- **`window.confirm()` over custom modal**: Spec explicitly states "simple confirm/cancel is sufficient" and custom modal is out of scope. Zero additional UI code. Can upgrade later if needed.
- **`rmSync` over `rm`**: Synchronous deletion is simpler and the operation is fast (skill directories are small). Avoids async error handling complexity for negligible performance difference. `{ recursive: true, force: true }` handles nested files and missing-path edge cases cross-platform.
- **Origin check on server, not just client**: Defense-in-depth. The UI hides the button for installed skills, but the server independently rejects deletion of installed skills via `classifyOrigin()`. Prevents API-level misuse.
- **No ADR needed**: This is a straightforward CRUD addition following existing patterns. No new architectural decisions, no trade-offs with lasting implications.

## Implementation Phases

### Phase 1: Server Endpoint (~25 lines in api-routes.ts)

Add `router.delete("/api/skills/:plugin/:skill", ...)` handler:
1. Import `rmSync` (add to existing `node:fs` import) and `classifyOrigin` (from `skill-scanner.ts`)
2. Resolve skill directory via `resolveSkillDir(root, params.plugin, params.skill)`
3. Check `existsSync(skillDir)` -- return 404 if missing
4. Check `classifyOrigin(skillDir, root)` -- return 403 if "installed"
5. Call `rmSync(skillDir, { recursive: true, force: true })`
6. Return `{ ok: true }`

Place the handler after the existing `GET /api/skills/:plugin/:skill` route for readability.

### Phase 2: Client API Method (~5 lines in api.ts)

Add `deleteSkill(plugin, skill)` to the `api` object:
```
deleteSkill(plugin: string, skill: string): Promise<{ ok: boolean }> {
  return fetchJson(`/api/skills/${plugin}/${skill}`, { method: "DELETE" });
}
```

### Phase 3: UI Delete Button (~50 lines in DetailHeader.tsx)

1. Add `onDelete` callback prop to `DetailHeader` Props interface
2. Add trash icon button between the breadcrumb area and the stats pills
3. Button visibility: only when `!isReadOnly`
4. Button disabled state: when `isRunning` is true
5. onClick: `window.confirm("Delete skill \"${skill}\"? This cannot be undone.")` -- if confirmed, call `onDelete()`
6. In `SkillWorkspaceInner` (caller): wire `onDelete` to call `api.deleteSkill()`, then `refreshSkills()` + `clearSelection()` from `useStudio()`

### Props Threading

`DetailHeader` receives `onDelete` from `SkillWorkspaceInner`. The delete handler in `SkillWorkspaceInner` calls the API then uses `useStudio()` context methods. This keeps DetailHeader a pure presentational component.

## Testing Strategy

- **Server unit tests**: 4 tests covering 200/403/404/500 responses using temp directories with real fs operations (matches existing test patterns in the codebase -- see `benchmark.test.ts`, `benchmark-history.test.ts`)
- **Client API test**: Verify `deleteSkill` calls `DELETE` with correct URL (mock fetch)
- **UI test**: Verify button visibility (source vs installed), disabled state during runs, confirm dialog interaction, and post-delete state cleanup

## Technical Challenges

### Challenge 1: Path Traversal Safety
**Solution**: `resolveSkillDir()` already constrains resolution to known layout patterns under `root`. The resolved path always starts from `root` and only matches specific directory structures. No user-supplied path segments reach the filesystem directly.
**Risk**: Low. Existing pattern is battle-tested across all other skill endpoints.

### Challenge 2: Race Condition During Benchmark
**Solution**: The UI disables the delete button when `isRunning` is true (any case has status "running" or "queued"). Server-side, `rmSync` will fail if files are locked by another process, but on all major OSes, file reads don't hold locks that block deletion. The semaphore system (`getSkillSemaphore`) could be extended if needed, but the UI guard is sufficient for V1.
**Risk**: Minimal. The UI guard prevents the primary race condition.
