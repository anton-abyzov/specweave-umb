# Tasks: Skill Studio click-to-switch project folders

**Increment**: 0863-studio-folder-switch | **Project**: vskill
**Repo**: repositories/anton-abyzov/vskill

---

### T-001: ActiveRootStore
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given a store created with root A → When `getRoot()` → Then returns A.
- Given a store at A → When `setRoot(B)` → Then `getRoot()` returns B.
- Given workspace.json with active project C → When `reload(workspaceDir)` → Then `getRoot()` returns C's path.

Create `src/eval-server/active-root-store.ts` exporting `ActiveRootStore` +
`createActiveRootStore(initialRoot)`. In-memory holder; `reload` reuses `resolveActiveRoot`.

---

### T-002: Thread getRoot through all root-consuming route registrations (load-bearing)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US4-03 | **Status**: [x] completed
**Test Plan**:
- Given the server registered with `getRoot` backed by a store at A → When `store.setRoot(B)` then `GET /api/skills` → Then the response lists B's skills, not A's.
- Given an improve/sweep job started while root=A → When root switches to B mid-job → Then the job continues against A (root snapshot at start).
- Regression: existing route unit tests still pass.

Convert `registerRoutes` + `registerImproveRoutes`, `registerModelCompareRoutes`,
`registerSkillCreateRoutes`, `registerSweepRoutes`, `registerIntegrationRoutes`,
`registerAuthoringRoutes`, `registerPluginCliRoutes`, `registerGitRoutes`,
`registerScopeTransferRoutes` (+ its 5 install/remove/detect children) from `root: string` to
`getRoot: () => string`; add `const root = getRoot();` at the top of each handler. Snapshot root at
start of long-lived jobs. Audit `agentPresenceCache`/any per-root module caches include root in key.

---

### T-003: POST /api/workspace/active applies the new root (+ 409 guard)
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-03, AC-US1-05, AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**:
- Given projects A,B registered → When `POST /api/workspace/active {id:B}` → Then 200 `{ok,activeProjectId:B,root,skillCount}` and next `GET /api/skills` returns B's skills.
- Given B's path is an empty dir → Then 200 with `skillCount:0` (not an error).
- Given B's path deleted/unreadable → Then 409 `{ok:false,error,fallbackCommand}` AND the store still serves A.
- Given switch → Then studio token + bound port are unchanged.

Inject `rootStore` + scan helper into `makeWorkspaceHandlers`; after `setActiveProject`, statSync
guard → `setRoot` → immediate re-scan for `skillCount`.

---

### T-004: ProjectPicker click = switch (remove default modal)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given the dropdown open → When clicking a non-active row → Then `onSwitch(id)` fires and no cd-command modal appears.
- Given clicking the active row → Then the dropdown closes (no-op).

Edit `ProjectPicker.tsx:236-246` to call `onSwitch(p.id)`; remove the default `setSwitchHint`. Keep
modal markup for the error path only.

---

### T-005: Reload UX state machine
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**:
- Given a switch starts → Then the target row shows active immediately (optimistic) with a "Switching…" spinner and the picker is disabled.
- Given skills are refetching → Then the prior content + existing loading state remain (no layout collapse) until the new skills arrive.
- Given the switch resolves → Then a toast "Switched to {name} — {N} skills" appears and auto-dismisses.
- Given a double-click → Then only one switch executes.
- `switchProject` resolves after the re-root POST applies + reports skillCount; `studio:project-changed` then drives the in-place skill-list + agent-badge refetch.

Optimistic active-row flip + inline Spinner in `ProjectPicker.handleSwitch`; disabled-while-switching;
`studio:toast` success event; `studio:project-changed` event wired to `StudioContext.loadSkills` +
`useAgentsResponse` so the sidebar list AND the agent scope badge refetch in place (no page reload).

---

### T-006: Error-only fallback modal
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test Plan**:
- Given `POST /api/workspace/active` returns 409 → Then the cd-command modal opens showing `fallbackCommand` from the response body.
- Given a successful switch → Then the modal never appears.

Wire the kept modal markup to the switch-failure branch only; source the command from `fallbackCommand`.

---

### T-007: "Open folder…" — native dialog (desktop) + path entry (npx)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**:
- Given `isTauriHost` true → When "Open folder…" → Then a native directory picker opens; choosing a folder registers it and switches to it.
- Given browser/npx → When "Open folder…" → Then the absolute-path entry shows; a valid path registers + switches.
- Given a folder is added → Then the app switches to it automatically.

Use `@tauri-apps/plugin-dialog` `open({directory:true})` gated on `isTauriHost`; fall back to the
existing path-entry input. After `addProject`, call `switchProject`.

---

### T-008: Tests + live preview verification
**User Story**: US-001..US-004 | **Satisfies ACs**: all | **Status**: [x] completed
**Test Plan**:
- Unit (Vitest): ActiveRootStore; `POST /api/workspace/active` re-root + 409; ProjectPicker click calls onSwitch.
- E2E (Playwright): dropdown → switch → skill grid changes; 409 → error modal; empty folder → empty state.
- Live: build, launch `vskill studio` with ≥2 registered projects, drive via preview MCP tools
  (open dropdown → click another project → snapshot shows that project's skills, no cd-modal →
  screenshot proof). Confirm switch-back + bad-folder behavior.

Run `npx vitest run` + `npx playwright test` (relevant specs) — all green before closure.
