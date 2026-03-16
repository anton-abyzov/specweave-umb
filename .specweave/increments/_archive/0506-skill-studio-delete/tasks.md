---
increment: 0506-skill-studio-delete
by_user_story:
  US-001:
    - T-001
    - T-002
    - T-003
    - T-004
---

# Tasks: Skill Studio -- Add Delete Skill Functionality

## User Story: US-001 - Delete a Source Skill

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09
**Tasks**: 4 total, 4 completed

---

### T-001: Add DELETE /api/skills/:plugin/:skill server endpoint

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a request to `DELETE /api/skills/:plugin/:skill`
- **When** the skill directory exists and has `origin: "source"`
- **Then** the directory is removed recursively and `{ ok: true }` is returned with HTTP 200
- **When** the skill has `origin: "installed"`
- **Then** returns HTTP 403 with `{ error: "Cannot delete installed (read-only) skill" }` and nothing is removed
- **When** the skill directory does not exist
- **Then** returns HTTP 404 with `{ error: "Skill directory not found" }`

**Test Cases**:
1. **Unit**: `src/eval-server/__tests__/api-routes-delete.test.ts`
   - `deleteSkill_sourceOrigin_removes_dir_returns_ok()`: creates temp dir with source layout, calls handler, asserts dir gone and `{ ok: true }`
   - `deleteSkill_installedOrigin_returns_403()`: creates temp dir classified as installed, asserts 403 and dir still present
   - `deleteSkill_missingDir_returns_404()`: calls handler with non-existent path, asserts 404
   - `deleteSkill_rmSyncThrows_returns_500()`: mock `rmSync` to throw, assert 500 error body
   - **Coverage Target**: 90%

**Implementation**:
1. Add `rmSync` to existing `node:fs` import in `src/eval-server/api-routes.ts`
2. Add `import { classifyOrigin } from "../eval/skill-scanner.js"` (already imported via `scanSkills` — check if `classifyOrigin` is re-exported or add direct import)
3. Add `router.delete("/api/skills/:plugin/:skill", ...)` handler after the GET handler for the same route
4. Handler body: `resolveSkillDir(root, plugin, skill)` → `existsSync` check (404) → `classifyOrigin` check (403) → `rmSync(dir, { recursive: true, force: true })` → `{ ok: true }`
5. Run `npx vitest run src/eval-server/__tests__/api-routes-delete.test.ts`

---

### T-002: Add `api.deleteSkill()` client method

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `api` object in `src/eval-ui/src/api.ts`
- **When** `api.deleteSkill("myplugin", "myskill")` is called
- **Then** `fetch` is called with `DELETE /api/skills/myplugin/myskill` and the resolved value is returned

**Test Cases**:
1. **Unit**: `src/eval-ui/src/api.test.ts` (extend existing file)
   - `deleteSkill_calls_DELETE_with_correct_url()`: mock fetch to return `{ ok: true, json: async () => ({ ok: true }) }`, call `api.deleteSkill("p", "s")`, assert `fetch` called with `"/api/skills/p/s"` and `{ method: "DELETE" }`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/eval-ui/src/api.ts`
2. Add after `deleteHistoryEntry`:
   ```ts
   deleteSkill(plugin: string, skill: string): Promise<{ ok: boolean }> {
     return fetchJson(`/api/skills/${plugin}/${skill}`, { method: "DELETE" });
   },
   ```
3. Run `npx vitest run src/eval-ui/src/api.test.ts`

---

### T-003: Add delete button with confirmation to DetailHeader

**User Story**: US-001
**Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US1-08, AC-US1-09
**Status**: [x] completed

**Test Plan**:
- **Given** `DetailHeader` rendered with `isReadOnly: false` and `onDelete` prop
- **When** the component renders
- **Then** a trash-icon button is visible
- **Given** `isReadOnly: true`
- **Then** the trash button is not rendered
- **Given** `isRunning` is true (a case has status "running")
- **Then** the trash button is disabled
- **When** the trash button is clicked and `window.confirm` returns true
- **Then** `onDelete` is called
- **When** `window.confirm` returns false (cancel)
- **Then** `onDelete` is NOT called

**Test Cases**:
1. **Unit**: `src/eval-ui/src/components/__tests__/DetailHeader.test.tsx`
   - `showsDeleteButton_whenSourceSkill()`: render with `isReadOnly=false`, assert button present
   - `hidesDeleteButton_whenReadOnly()`: render with `isReadOnly=true`, assert button absent
   - `disablesDeleteButton_whenRunning()`: render with a running case state, assert button disabled
   - `callsOnDelete_whenConfirmed()`: mock `window.confirm` → true, click button, assert `onDelete` called once
   - `doesNotCallOnDelete_whenCanceled()`: mock `window.confirm` → false, click button, assert `onDelete` not called
   - **Coverage Target**: 90%

**Implementation**:
1. Add `onDelete?: () => void` to the `Props` interface in `src/eval-ui/src/components/DetailHeader.tsx`
2. Destructure `onDelete` from props
3. Add trash-icon button in the right `<div>` (before stats pills), conditional on `!isReadOnly`:
   ```tsx
   {!isReadOnly && (
     <button
       disabled={isRunning}
       onClick={() => {
         if (window.confirm(`Delete skill "${skill}"? This cannot be undone.`)) {
           onDelete?.();
         }
       }}
       title="Delete skill"
       style={{ background: "none", border: "none", cursor: isRunning ? "not-allowed" : "pointer", color: "var(--text-tertiary)", padding: "4px" }}
     >
       <TrashIcon />
     </button>
   )}
   ```
4. Add `TrashIcon` inline SVG component (16x16 trash can)
5. Run `npx vitest run src/eval-ui/src/components/__tests__/DetailHeader.test.tsx`

---

### T-004: Wire onDelete in SkillWorkspaceInner and pass through RightPanel

**User Story**: US-001
**Satisfies ACs**: AC-US1-07
**Status**: [x] completed

**Test Plan**:
- **Given** a source skill is selected and the user confirms deletion
- **When** `onDelete` fires in `DetailHeader`
- **Then** `api.deleteSkill(plugin, skill)` is called, followed by `refreshSkills()` and `clearSelection()` from `useStudio()`
- **Then** the workspace is no longer shown (selection cleared)

**Test Cases**:
1. **Unit**: `src/eval-ui/src/pages/workspace/__tests__/SkillWorkspace.delete.test.tsx`
   - `handleDelete_callsApiThenRefreshesAndClears()`: mock `api.deleteSkill` → resolves, mock `useStudio` hooks, trigger delete, assert call order: `api.deleteSkill` → `refreshSkills` → `clearSelection`
   - `handleDelete_apiError_doesNotClearSelection()`: mock `api.deleteSkill` → rejects, assert `clearSelection` NOT called (error surfaced to console)
   - **Coverage Target**: 85%

**Implementation**:
1. In `src/eval-ui/src/pages/workspace/SkillWorkspace.tsx`, add import for `api` and `useStudio`
2. Inside `SkillWorkspaceInner`, pull `refreshSkills` and `clearSelection` from `useStudio()`
3. Define `handleDelete`:
   ```ts
   const handleDelete = useCallback(async () => {
     try {
       await api.deleteSkill(plugin, skill);
       refreshSkills();
       clearSelection();
     } catch (err) {
       console.error("Failed to delete skill:", err);
     }
   }, [plugin, skill, refreshSkills, clearSelection]);
   ```
4. Pass `onDelete={handleDelete}` to `<DetailHeader ... />`
5. Verify `StudioContext` exports `clearSelection` (check `StudioContext.tsx`); if not, add it
6. No changes needed in `RightPanel.tsx` — `SkillWorkspaceInner` is already rendered inside `WorkspaceProvider` which has access to `useStudio` context
7. Run `npx vitest run` from `repositories/anton-abyzov/vskill/`
