# Plan — 0850 Studio install feedback + install-state aware modal

## Files to add

- `src/eval-server/remove-skill-routes.ts` — new `POST /api/studio/remove-skill` route.
- `src/eval-ui/src/api/remove.ts` — frontend client for the new route.

## Files to edit

- `src/eval-server/eval-server.ts` — register the new route.
- `src/eval-server/install-skill-routes.ts` — add `console.log("[install] …")` before/after each multi-install job.
- `src/eval-ui/src/components/InstallTargetsModal.tsx` — scope-aware path renderer, persistent done phase, per-row install-state badges + Remove link, install-state fetch on mount.
- `src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx` — `handleInstallModalSuccess` stops auto-closing on success (let the modal own the close UX).

## Algorithm

1. **Path renderer.** Compute `displayedPath` = `scope === "project" ? agent.resolvedLocalDir : agent.resolvedGlobalDir` and feed into `TierSection`. Tier-3 keeps `pathOverride="Copy to clipboard"`.
2. **Install-state.** On modal mount, fetch `/api/studio/install-state?skill=<full id>`. For each agent row, derive status:
   - `not-installed`: scope state shows installed = false OR agent id not in `installedAgentTools`.
   - `installed-current`: installed + version === target version.
   - `update-available`: installed + version < target.
   - `newer-installed`: installed + version > target.
3. **Remove.** Already-installed rows show a tiny inline button that POSTs `/api/studio/remove-skill` with that single agent id, then updates the row to `not-installed` and removes the lockfile entry server-side.
4. **Done phase persistence.** Remove the `if (exportedCount === 0) { setInstallModalOpen(false); onClose(); }` short-circuit. Modal stays mounted in `phase: "done"`, footer shows "Done" button which closes.
5. **Server logging.** Add `console.log("[install] start", {...})` and `console.log("[install] result", {...})` at the start and end of every multi-install job so terminal users have a trace.

## Backend (remove-skill-routes.ts)

```ts
POST /api/studio/remove-skill
Body: { skill: string, agentIds: string[], scope: "project" | "user" }
→ 200 { removed: [{agentId, path}], errors: [{agentId, message}], skipped: [{agentId, reason}] }
```

For each agent:
- Resolve install dir via `agents-registry` (`localSkillsDir` or `globalSkillsDir`).
- Build `<dir>/<lastSegment(skill)>` path.
- `fs.rmSync(p, { recursive: true, force: true })`.
- Remove agent from lockfile `agents` list if no other skill references it. Drop `skills[<name>]` entry when this was the last install of the skill in this scope.

## Testing

Unit:
- `remove-skill-routes.test.ts`: localhost guard, SAFE_NAME/SAFE_AGENT_ID validation, per-agent removed/skipped/error rows, lockfile mutation.
- `InstallTargetsModal.test.tsx`: scope-aware path rendering (project vs user), install-state badge variants, done-phase persistence, Remove link interaction.

E2E:
- `install-then-verify.spec.ts`: install appstore to claude-code at project scope, verify `<cwd>/.claude/skills/appstore/SKILL.md` exists, modal shows the path and stays in done phase.
- `install-then-remove.spec.ts`: install then remove via the modal, verify path is gone and badge flips to "Not installed".

## Rollout

- No migrations.
- Bump vskill version on release.
- No desktop sidecar protocol changes — desktop picks up the fix automatically via the bundled JS.
