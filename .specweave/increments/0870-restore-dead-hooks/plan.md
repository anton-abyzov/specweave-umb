# Plan: 0870 Restore dead hooks

## Restore the 5 (US-001)
Copy the recovered handlers from `/tmp/dead-hooks/` back to `src/core/hooks/handlers/`:
`session-start.ts`, `post-tool-use.ts`, `post-tool-use-analytics.ts`, `stop-reflect.ts`, `stop-sync.ts`
(verify they still compile against current `types.ts`/`utils.ts`; adjust imports if drifted).
Add each key to `HANDLERS` in `hook-router.ts`. Routed test per hook via `hookRouter('<name>', stdin)`.

## Rewrite stop-auto (US-002) — the centerpiece
The recovered `stop-auto.ts` is a non-blocking stub. Keep its scaffold (session detection via
`auto-mode.json` per-session/global, staleness via `auto.maxSessionAge`, active-increment scan)
but add the BLOCKING decision the `/sw:auto` SKILL.md requires:

```
not auto-active | inactive | stale            -> reset .stop-auto-turns; { decision:'approve' }
turns > auto.maxTurns (default 20)            -> clear counter; { decision:'approve' }  // safety stop
all tasks complete AND all ACs satisfied      -> clear counter; { decision:'block', reason:'...all_complete_needs_closure... run sw:done --auto <id>' }
otherwise (pending tasks/ACs)                 -> increment counter; { decision:'block', reason:'<P> tasks / <A> ACs remain in <id>. Run sw:do. Goal: <userGoal>' }
any throw                                     -> { decision:'approve' }
```
- Counts: prefer `parseTasksWithUSLinks` + `calculateProgressFromTasksFile` (and AC parse from spec.md) over naive regex.
- Counter file: `.specweave/state/.stop-auto-turns` (matches the cleanup list in `auto.ts`/`session-lifecycle.ts`).
- `incrementIds` come from `auto-mode.json.incrementIds`; fall back to active-increment scan.

## Guard sync (US-003)
Remove all 6 from `KNOWN_UNROUTED` in `hook-wiring-parity.test.ts` → it must end EMPTY and still pass.

## TDD order
Per hook: RED routed test → GREEN register/restore → run. Do stop-auto last (most tests).
Then `npx vitest run src/core/hooks` (full green) + `npm run build`.

## Files
- restore 5 + rewrite 1 in `src/core/hooks/handlers/`
- `hook-router.ts` (HANDLERS +6)
- new `*.test.ts` routed tests (or extend existing)
- `hook-wiring-parity.test.ts` (empty KNOWN_UNROUTED)
- `package.json` patch bump

## Ship
Republish (Anton's OK) → `specweave refresh-plugins` to clear installed-cache drift.
