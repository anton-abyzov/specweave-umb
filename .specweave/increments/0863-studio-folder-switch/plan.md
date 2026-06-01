# Implementation Plan: Skill Studio click-to-switch project folders

## Architecture decision: Option A — runtime re-root, no process restart

The eval-server already scans the filesystem **fresh on every `/api/skills` request** — the scan is
stateless. The only thing frozen is the **root value**, captured at boot as a `const` and closed
over by every route handler. So we don't need to restart anything; we need the root to be a
**mutable lookup** instead of a captured constant.

```
ProjectPicker row click (non-active)
        │  onSwitch(id)
        ▼
useWorkspace.switchProject(id)
        │  POST /api/workspace/active { id }
        ▼
workspace-routes: setActiveProject (persist) → statSync guard → rootStore.setRoot(path) → re-scan
        │  200 { ok, activeProjectId, root, skillCount }   |   409 { ok:false, error, fallbackCommand }
        ▼
invalidate skills/agents/workspace SWR → refetch /api/skills (now scans NEW root) → ready
```

Because the desktop Tauri app loads the same eval-ui from its sidecar (the sidecar *is* this
eval-server), the identical HTTP flow works in desktop and `npx vskill studio`. No mode branch on
the happy path. **This is the "NPM is different" answer:** npx is a single process that cannot
cleanly self-exec with a new CWD — Option A removes the need to.

### Rejected: Option B — restart sidecar with new --root
Impossible in npx (no supervisor to relaunch the process). In desktop it drops the WebView,
re-mints the studio token, reassigns the port, and kills in-flight evals. Kept only as a possible
future desktop-only "Reload from disk" hard-reset hatch — **out of scope here**.

## Components

### 1. `ActiveRootStore` (new — `src/eval-server/active-root-store.ts`)
```ts
export interface ActiveRootStore {
  getRoot(): string;
  setRoot(p: string): void;
  reload(workspaceDir: string): string; // re-derive from workspace.json via resolveActiveRoot
}
export function createActiveRootStore(initialRoot: string): ActiveRootStore
```
In-memory holder. `getRoot()` is a plain field read (no fs per call). Seeded at boot with the
boot-resolved root. `reload` reuses the existing `resolveActiveRoot` logic (exported from
eval-server.ts or duplicated minimally) to re-derive from `~/.vskill/workspace.json`.

### 2. Thread `getRoot` through route registrations (load-bearing)
Convert each root-consuming `registerX(router, root: string, …)` to
`registerX(router, getRoot: () => string, …)`. Inside, add a single `const root = getRoot();` at
the **top of each request handler** so all existing `root` references stay valid and resolve the
live value per request. Functions (all reachable from `startEvalServer`):

| File | Function |
|---|---|
| `api-routes.ts:1498` | `registerRoutes` (owns `/api/skills`, skill detail/install ops) |
| `improve-routes.ts` | `registerImproveRoutes` |
| `model-compare-routes.ts` | `registerModelCompareRoutes` |
| `skill-create-routes.ts` | `registerSkillCreateRoutes` |
| `sweep-routes.ts` | `registerSweepRoutes` |
| `integration-routes.ts` | `registerIntegrationRoutes` |
| `authoring-routes.ts` | `registerAuthoringRoutes` |
| `plugin-cli-routes.ts` | `registerPluginCliRoutes` |
| `git-routes.ts` | `registerGitRoutes` |
| `studio/routes/index.ts:23` | `registerScopeTransferRoutes` → passes `getRoot` to its 5 children: `registerDetectEnginesRoute`, `registerInstallEngineRoutes`, `registerInstallSkillRoutes`, `registerInstallStateRoutes`, `registerRemoveSkillRoutes` |

**Long-lived runners** (improve / sweep / eval jobs): snapshot `getRoot()` into a local at job
**creation**, then use that snapshot for the job's lifetime — a switch mid-run must not retarget it.

### 3. `eval-server.ts` wiring
- `const rootStore = createActiveRootStore(root);`
- Pass `rootStore.getRoot` to every registration above.
- Pass `rootStore` (or a `setActiveRoot` callback) into `registerWorkspaceRoutes`.

### 4. `POST /api/workspace/active` (`workspace-routes.ts:102-122`)
After `setActiveProject` persists: resolve the project's path, `statSync` to confirm it exists and
is a readable directory, `rootStore.setRoot(path)`, run one `scanSkillsTriScope(path,…)` to get
`skillCount`, respond `{ ok:true, activeProjectId, root, skillCount }`. On bad path: do **not**
mutate the store; respond `409 { ok:false, error, fallbackCommand: 'cd "{path}" && npx vskill@latest studio' }`.
Requires injecting `rootStore` + a scan helper into `makeWorkspaceHandlers`.

### 5. Frontend
- **`ProjectPicker.tsx:236-246`** — non-active row click calls `onSwitch(id)`. Delete the default
  `switchHint` assignment; keep the modal markup (`:529-600`) but only open it on switch failure,
  rendering `fallbackCommand` from the 409 body.
- **`useWorkspace.switchProject`** — POST active, then `await` the skills refetch (so the promise
  resolves on `ready`), surface `{ skillCount }` for the toast, and propagate 409 errors.
- **Reload state machine** — `idle → switching → reloading → ready (+error)` driven from
  `ProjectPicker`/`App`: optimistic active-row flip, picker disabled while switching, skeleton
  skill grid (sized to `skillCount` when known), success toast, empty-state when `skillCount===0`.
- **"Open folder…"** — `isTauriHost` → `@tauri-apps/plugin-dialog` `open({ directory:true })` →
  `addProject(absPath)` → switch. Browser/npx → existing absolute-path entry. After add, auto-switch.

## Reuse (do NOT rebuild)
- `~/.vskill/workspace.json` + `workspace-store.ts` (`loadWorkspace`/`addProject`/`setActiveProject`/`projectIdFromPath`)
- `resolveActiveRoot` (`eval-server.ts:231-240`)
- `scanSkillsTriScope` (`eval/skill-scanner.ts`)
- `useWorkspace` + SWR `mutate` cache invalidation; `App.tsx` `onSwitch={switchProject}` wiring
- `isTauriHost` / `useDesktopBridge` for mode detection; `dialog:default` capability

## ADRs
No new ADR required — this completes the 0698 multi-project workspace design (ADR-0698-*). Reference
that ADR; note the runtime-re-root decision in the increment record.

## Risks
- **Blast radius of getRoot threading** — bounded & mechanical (~16 fns, one line per handler). Mitigate
  with unit test asserting `setRoot` changes `/api/skills` output, plus full typecheck + existing route tests.
- **Stale per-root module caches** — e.g. `agentPresenceCache` keyed by root in api-routes. Verify the
  cache key includes root (it does: `rootKey`), so a new root misses the cache and re-scans. Audit during T-002.
- **In-flight jobs** — snapshot root at job start (T-002 sub-task).
