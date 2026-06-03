# Plan: 0869 Hook wiring audit + recurrence guard

## Deliverables
1. **Audit report** (`reports/hook-wiring-audit-2026-06-03.md`) — done: full 10-hook table, root cause `0f81519b1`, connected places, per-hook fix plan, grade 40/100.
2. **Recurrence guard test** — `src/core/hooks/handlers/hook-wiring-parity.test.ts`.

## Guard test design
Single source of truth = the plugin `hooks.json` (call-sites) vs the router `HANDLERS` map (dispatch).

```
invoked   = every `specweave hook X` name parsed from plugins/specweave/hooks/hooks.json
registered = keys of HANDLERS in src/core/hooks/handlers/hook-router.ts (parsed from source text)
KNOWN_UNROUTED = { session-start, post-tool-use, post-tool-use-analytics, stop-reflect, stop-auto, stop-sync }  // dead since 0f81519b1, tracked for restoration

assert: invoked ⊆ registered ∪ KNOWN_UNROUTED        // no NEW silent-dead hook
assert: KNOWN_UNROUTED ⊆ invoked                      // no stale allowlist entry
assert: {user-prompt-submit, pre-tool-use, pre-compact, stop} ⊆ registered  // the live 4 can't regress
```

Parse `registered` by reading hook-router.ts source and matching `'<key>':` inside the HANDLERS
object (avoids importing TS-with-deps into the test). Parse `invoked` from hooks.json JSON.

### TDD
- **RED**: write the test asserting `invoked ⊆ registered` with KNOWN_UNROUTED **empty** → fails listing the 6 dead hooks (proves the test detects the real bug).
- **GREEN**: populate KNOWN_UNROUTED with the 6 → passes; add the stale-entry + live-4 assertions.
- **REFACTOR**: none.

## When a hook is restored later
The follow-up increment registers the handler (adds the key to HANDLERS) AND removes that name
from `KNOWN_UNROUTED` — the stale-entry assertion forces them to stay in sync.

## Files
- `src/core/hooks/handlers/hook-wiring-parity.test.ts` (new)

## Out of scope
- Handler restoration (follow-up). Republish/refresh to clear cache drift.
