# Implementation Plan: Studio Uninstall Button for Installed Skills

## Design

### Part A — Server: `POST /api/skills/:plugin/:skill/uninstall` (US-003)

New route in `src/eval-server/api-routes.ts`. Reuses three existing primitives:
1. The `trash` npm package import already used at line 2650.
2. Path-traversal guard pattern (`path.resolve()` + `startsWith()`).
3. Lockfile read/write helpers from `src/lockfile/lockfile.ts`.

Handler steps:
1. Validate `:skill` matches the kebab-case regex (same one used by skill-create).
2. Compute `targetDir = join(root, ".claude/skills", skillName)`.
3. Resolve absolute path; assert `startsWith(rootResolved)`.
4. Read `vskill.lock`; if `skills[skillName]` exists, delete it; write back. Track `removedFromLockfile`.
5. If `targetDir` exists, `await trash([targetDir])`. Track `trashedDir`.
6. If neither lockfile entry nor disk dir → 404 `{ code: "not-installed" }`.
7. Return `{ ok: true, removedFromLockfile, trashedDir }`.

### Part B — Client: api.uninstallSkill + DetailHeader button (US-001, US-002)

`src/eval-ui/src/api.ts` gains `uninstallSkill(plugin, skill)`.

`src/eval-ui/src/components/DetailHeader.tsx` — render a NEW "Uninstall" button gated on `isReadOnly && skill.trackedForUpdates`. Click dispatches a new `studio:request-uninstall` CustomEvent with `{ skill }`.

`src/eval-ui/src/App.tsx` — add a listener for `studio:request-uninstall` that opens `ConfirmDialog` with uninstall-specific copy. On confirm, schedule via the existing `usePendingDeletion` buffer; the buffer's run callback branches: source-authored → `api.deleteSkill` (existing); installed-tracked → `api.uninstallSkill` (new).

### Part C — Confirmation copy + Undo

ConfirmDialog body: "Uninstall &lt;skill&gt;? It will be sent to your &lt;Trash&gt; and the lockfile entry will be removed."

Undo: standard 10s window from `usePendingDeletion`.

## Rationale

- **Why not extend `DELETE /api/skills/:plugin/:skill`?** That endpoint's contract is "trash the source skill files." Adding lockfile semantics overloads it. A dedicated `/uninstall` keeps install/uninstall symmetric.
- **Why route through OS trash and not `rm -rf`?** Reversibility. 10s in-app undo + OS trash recovery = two layers of safety.
- **Why hide the button for plugin-bundled skills?** Their uninstall path is owned by `PluginActionMenu` (uninstall the *plugin*).
- **Why `trackedForUpdates` as the discriminator?** Already differentiates lockfile-tracked vs plugin-bundled in the existing `SkillInfo`.

## ADRs

No new ADRs. Respects 0722 OS-trash + undo, CORS-free architecture, existing `trackedForUpdates` semantics.
