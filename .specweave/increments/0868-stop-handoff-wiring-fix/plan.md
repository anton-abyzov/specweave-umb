# Plan: 0868 Stop-handoff wiring fix

## Approach (decided)

**Option (b): wire `specweave hook stop` into `hooks.json` `Stop[]`.** The Node hook-router
already maps `HANDLERS['stop'] → pre-compact.js#handleStop` (with a comment citing AC-US7-02);
the only break is that the plugin never calls it. Add a 4th command object to the existing
`Stop[]` group, identical in shape to its siblings:

```jsonc
{ "type": "command",
  "command": "bash -c 'command -v specweave &>/dev/null && specweave hook stop || { cat >/dev/null; echo \"{\\\"decision\\\":\\\"approve\\\"}\"; }'",
  "timeout": 15000 }
```

No handler, router, or builder code changes — `handleStop` already self-gates on
`auto-mode.json` and reuses `buildWorkHandoff`.

### Why not option (a)
Folding `handleStop` into `stop-auto` assumes `stop-auto` is a wired handler. It is not:
`HANDLERS` in `hook-router.ts` has only `user-prompt-submit`, `pre-tool-use`, `pre-compact`,
`stop`. `specweave hook stop-auto` falls through to "unknown event type" → safe default
(confirmed by runtime probe). Chaining onto it would be wrong and obscure ownership.

## TDD strategy

The bug is a *false-positive green test* — the fix must make the test exercise the **real
dispatch path**, not the handler in isolation.

1. **RED** — add, in `pre-compact.test.ts` (or a sibling `stop-wiring.test.ts`):
   - a routed test: `hookRouter('stop', JSON.stringify({reason:'auto run paused'}))` against a
     temp SpecWeave repo **with** `auto-mode.json` → asserts a handoff doc was written; and
     **without** → asserts none. (Fails today only if the router map regresses; primarily
     locks the dispatch contract.)
   - a **pin test** parsing `plugins/specweave/hooks/hooks.json` asserting `Stop[]` contains a
     command string matching `specweave hook stop` (word-boundary, not `stop-reflect` etc.).
     **This is the test that fails RED today.**
2. **GREEN** — add the `specweave hook stop` command to `hooks.json` `Stop[]`.
3. **REFACTOR** — none expected; keep the sibling entries byte-identical.

## Verify

- `npx vitest run src/core/hooks/handlers/pre-compact.test.ts` + the new wiring test → green.
- `npm run build` (tsc) so `dist/` reflects source; `hooks.json` is data (no build needed) but
  the package bundles it.
- Manual: `echo '{"reason":"x"}' | node bin/specweave.js hook stop` in a repo with
  `.specweave/state/auto-mode.json` → writes `state/handoff-latest.md`; without → no write.

## Files touched

- `repositories/anton-abyzov/specweave/plugins/specweave/hooks/hooks.json` (Stop[] +1 command)
- `repositories/anton-abyzov/specweave/src/core/hooks/handlers/pre-compact.test.ts` (or new `stop-wiring.test.ts`)

## Out of scope / flagged

- `stop-reflect/stop-auto/stop-sync` not being registered in the Node router is a separate
  defect — note it, do not fix here.

## Ship

After green: rebuild, republish the CLI via the `npm-publish-otp` skill, so the global binary
ships the corrected wiring. Then `/sw:progress-sync` if external trackers are wanted.
