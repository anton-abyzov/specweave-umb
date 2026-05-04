# Tasks: Studio Reveal in Editor action

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started · `[x]`: Completed
- Tests precede implementation per project TDD policy.

## Phase 1: Server foundations (TDD)

### T-001: Write `resolve-editor.ts` failing tests
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed

**File**: `src/eval-server/utils/__tests__/resolve-editor.test.ts`

**Test Plan** (Given/When/Then):
- **TC-001**: Given `env.VISUAL = "code --reuse-window"` and target `{ dir: "/d", file: "SKILL.md" }` → When `resolveEditorCommand(target, env, "darwin", () => false)` → Then returns `{ command: "code", args: ["--reuse-window", "/d/SKILL.md"] }`.
- **TC-002**: Given `env.EDITOR = "vim"`, no `VISUAL` → returns `{ command: "vim", args: ["/d/SKILL.md"] }`.
- **TC-003**: Given empty env, `which("code") === true` → returns `{ command: "code", args: ["/d/SKILL.md"] }`.
- **TC-004**: Given empty env, `which("code") === false`, `which("cursor") === true` → returns `{ command: "cursor", args: ["/d/SKILL.md"] }`.
- **TC-005**: Given empty env, `which` always false, platform `"darwin"` → returns `{ command: "open", args: ["/d/SKILL.md"] }`.
- **TC-006**: Same with platform `"linux"` → returns `{ command: "xdg-open", args: ["/d/SKILL.md"] }`.
- **TC-007**: Same with platform `"win32"` → returns `{ command: "cmd", args: ["/c", "start", "", "/d/SKILL.md"] }`.
- **TC-008**: Target without `file` → final argv path === target.dir (no SKILL.md suffix).
- **TC-009**: All resolution rungs fail (e.g. unsupported platform with empty env, which always false) → throws `NoEditorError`.

### T-002: Implement `resolve-editor.ts` to make T-001 green
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed

**File**: `src/eval-server/utils/resolve-editor.ts`

**Implementation Details**:
- Export `EditorTarget`, `EditorLaunch`, `NoEditorError`.
- `resolveEditorCommand(target, env = process.env, platform = process.platform, which = defaultWhich): EditorLaunch`.
- Walk the resolution ladder; first match wins; throw `NoEditorError` if all rungs fail.
- `defaultWhich(cmd)` uses `execFileSync("command", ["-v", cmd], { stdio: "ignore" })` on POSIX and `execFileSync("where", [cmd], …)` on win32; cached in a `Map<string, boolean>`.

### T-003: Write `reveal-in-editor.test.ts` failing tests
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-05, AC-US2-01, AC-US2-02, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**File**: `src/eval-server/__tests__/reveal-in-editor.test.ts`

**Test Plan**:
- **TC-101**: Given valid `{ plugin: "p", skill: "s", file: "SKILL.md" }` and `scanSkillInstallLocations` returns one project install with dir `/r/p/skills/s` containing `SKILL.md` → When handler runs with mocked `resolveEditorCommand` and `spawn` → Then `sendJson` called with status 200 and `{ ok: true, command, args }` where args includes `/r/p/skills/s/SKILL.md`.
- **TC-102**: Body without `file` → spawn target = dir → 200.
- **TC-103**: `scanSkillInstallLocations` returns `[]` → 404 `{ error: "skill_not_found" }`.
- **TC-104**: `file: "../etc/passwd"` → 400 `{ error: "invalid_file" }`.
- **TC-105**: `file: "sub/dir/x"` (contains `/`) → 400 `{ error: "invalid_file" }`.
- **TC-106**: Body missing `plugin` → 400 `{ error: "invalid_body" }`.
- **TC-107**: Body missing `skill` → 400 `{ error: "invalid_body" }`.
- **TC-108**: `file: "MISSING.md"` (clean basename, doesn't exist) → 404 `{ error: "file_not_found" }`.
- **TC-109**: `resolveEditorCommand` throws `NoEditorError` → 500 `{ error: "no_editor" }`.
- **TC-110**: `spawn` emits `ENOENT` → 500 `{ error: "spawn_failed" }`.
- **TC-111**: When multiple install scopes exist, the project-scope dir is chosen (precedence test).

### T-004: Implement POST `/api/skills/reveal-in-editor` route
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: same as T-003 | **Status**: [x] completed

**File**: `src/eval-server/api-routes.ts`

**Implementation Details**:
- Register route inside `registerRoutes`. Body via `await readBody(req)`.
- Validate `plugin: string` (allow `""` for personal scope) and `skill: non-empty string`.
- Resolve dir via `scanSkillInstallLocations(canonical, root)` where `canonical = plugin ? \`${plugin}/${skill}\` : skill`. Pick highest-precedence install.
- If `file` present: reject if it contains `/`, `\`, or any segment equal to `..` or `""`. Then `existsSync(join(dir, file))`.
- Compute target; call `resolveEditorCommand`; launch via `spawn(cmd, args, { detached: true, stdio: "ignore" })` (argv array, no shell). Wrap in a Promise that resolves on `spawn` event and rejects on `error`. Call `child.unref()` on success.
- All error returns use `sendJson(res, { error: <code> }, status, req)`.

## Phase 2: UI wiring

### T-005: Add `api.revealInEditor` to `eval-ui/src/api.ts`
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [x] completed

**Implementation Details**:
- New method on the exported `api` object.
- Signature: `revealInEditor(plugin: string, skill: string, file?: string): Promise<{ ok: true; command: string; args: string[] }>`.
- Body construction: omit `file` from JSON when undefined.
- Reuses `fetchJson` (throws `ApiError` on non-2xx).

### T-006: Update `useContextMenuState.ts` router
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Implementation Details**:
- Replace the collapsed `case "open" | "reveal" | "edit":` block with three branches.
- `reveal` and `edit` → `api.revealInEditor(skill.plugin, skill.skill, "SKILL.md")`.
- `open` → `api.revealInEditor(skill.plugin, skill.skill)`.
- On success → dispatch `studio:toast` with `{ message: strings.toasts.openingInEditor, severity: "info" }`.
- On `ApiError` 404 (`skill_not_found` or `file_not_found`) → `skillNotFound` (error).
- On `ApiError` 500 with body.error === `no_editor` → `noEditor` (error).
- Anything else → `openFailed` (error).
- Handler returns `Promise<void>` (uniformly async) so tests can await; production callers (`ContextMenu.onAction` typed as `() => void | Promise<void>`) `void` the result. This is the resolution of the simplify-vs-grill divergence: keep the type honest rather than exposing a `void | Promise<void>` union.

### T-007: Update `eval-ui/src/strings.ts`
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Implementation Details**:
- Remove `actions.editPlaceholder`.
- Add to existing `toasts` group: `openingInEditor`, `noEditor`, `openFailed`, `skillNotFound` (copy per spec AC text).

## Phase 3: Test extension + regression

### T-008: Extend `useContextMenuState` tests for un-collapsed branches
**User Story**: US-001, US-002, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US4-01, AC-US4-02, AC-US4-03 | **Status**: [x] completed

**File**: `src/eval-ui/src/hooks/__tests__/useContextMenuState.test.ts` (or co-located test).

**Test Plan**:
- **TC-201**: `handleContextMenuAction("reveal", skill)` → `fetch` called once with URL `/api/skills/reveal-in-editor`, method `POST`, body JSON `{ plugin, skill, file: "SKILL.md" }`.
- **TC-202**: `handleContextMenuAction("edit", skill)` → same body as TC-201.
- **TC-203**: `handleContextMenuAction("open", skill)` → body `{ plugin, skill }` (no `file`).
- **TC-204**: 200 `{ ok: true }` → `studio:toast` event with message containing the localized "Opening in editor" copy.
- **TC-205**: 500 `{ error: "no_editor" }` → toast contains "No editor".
- **TC-206**: 404 → toast for skill-not-found.
- **TC-207**: `fetch` rejects (network) → `openFailed` toast.
- **TC-208**: Regression — `strings.actions.editPlaceholder` is `undefined`; the literal "0675" does not appear anywhere in `strings.ts`.

### T-009: Run full vitest suite, address any regressions
**Status**: [x] completed

**Command**: `cd repositories/anton-abyzov/vskill && npx vitest run`

### T-010: Manual smoke per spec verification section
**Status**: [x] completed

Steps from spec:
1. `npm run dev` in vskill.
2. Right-click source skill → Reveal in Editor → editor opens SKILL.md.
3. Right-click → Open → editor opens folder.
4. Right-click installed skill → same behaviors.
5. Tamper test: POST malicious `file: "../../etc/passwd"` via devtools → server replies 400.
