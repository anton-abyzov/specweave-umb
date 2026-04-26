# 0767 — Plan

## Files touched (vskill repo)

1. `src/eval-ui/src/components/PluginActionMenu.tsx` — replace `window.confirm()` with `<ConfirmDialog>`, dispatch `studio:toast` on success/failure.
2. `src/eval-ui/src/components/PluginActionMenu.test.tsx` (new) — RTL test for dialog flow.
3. `src/eval-server/plugin-cli-routes.ts` — uninstall handler: when CLI fails with "not found in installed plugins", call new `removeOrphanPluginCache(name)` helper and return ok:true on success.
4. `src/eval-server/plugin-orphan-cleanup.ts` (new) — pure helper: list orphan cache dirs for a plugin name + remove them (path-traversal safe).
5. `src/eval-server/plugin-orphan-cleanup.test.ts` (new) — unit tests using a tmp dir as cache root.

## Approach

### Frontend (PluginActionMenu)

- Add local state `confirmOpen: boolean`.
- Click "Uninstall" menu item → set `confirmOpen=true`. Don't call API yet.
- Render `<ConfirmDialog>` (destructive) with onCancel → close dialog + close menu, onConfirm → call API.
- After API resolves:
  - ok:true → dispatch `window.dispatchEvent(new CustomEvent("studio:toast", { detail: { message: "Uninstalled <name>", severity: "success" }}))`, swrMutate skills, triggerPluginsRefresh, onAfterAction, close menu.
  - ok:false → dispatch toast severity "error" with body.error, keep inline error for menu.

### Backend (plugin-orphan-cleanup)

```
function listOrphanCacheDirs(pluginName: string, cacheRoot: string): string[]
  - readdirSync(cacheRoot) → marketplace dirs
  - for each, check if cacheRoot/<marketplace>/<pluginName> exists and is a dir
  - resolve and verify path stays under cacheRoot
  - return list

function removeOrphanCacheDirs(paths: string[]): { removed: string[], failed: string[] }
  - rmSync(p, { recursive: true, force: true })
  - collect failures separately
```

Uninstall route:
- After `claude plugin uninstall` fails AND stderr matches `/not found in installed plugins/i`:
  - Strip `@marketplace` from `name` if present (cache dirs use bare name)
  - Call `listOrphanCacheDirs(name, ~/.claude/plugins/cache)`
  - If non-empty → remove all → respond `{ ok: true, fallback: "orphan-cache-removed", removed }`
  - Else → fall through to original `buildClaudeCliFailureResponse(result)`

## Risks

- **rmSync on wrong path** — guarded by `path.resolve(target).startsWith(cacheRoot + sep)` check.
- **claude CLI changes wording** — match tolerantly: `/not found in installed plugins/i` OR exit 1 + fallback path exists.
- **vskill bundle staleness** — the `vskill studio` runtime serves a pre-built bundle; rebuild via `npm run build:eval-ui` and `npm run build:eval-server` before testing.

## Test strategy

- Unit: orphan-cleanup helper with tmp dir scaffold (Vitest).
- Integration: route handler test calling a mocked `runClaudePlugin`.
- Component: PluginActionMenu — click Uninstall → confirm appears → click Confirm → fetch called → toast event dispatched.
- Manual: Live verification in browser via preview tools — the orphan `skill-creator` cache should disappear after Uninstall.
