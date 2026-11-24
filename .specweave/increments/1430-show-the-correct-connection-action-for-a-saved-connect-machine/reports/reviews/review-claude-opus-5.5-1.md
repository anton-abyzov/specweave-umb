<!-- specweave review: reviewer=claude-opus-5.5 model=claude-opus-5.5 family=claude author=openai depth=standard repo=repositories/anton-abyzov/specwithcode base=021ac0536cafcd09a8ce2de0206822483954b41c head=e37236bbd9a1e94561611b2034e82a7517f753b1 at=2026-11-20T05:21:30.411Z -->
**Head:** `e37236bbd9a1e94561611b2034e82a7517f753b1`, base `021ac0536cafcd09a8ce2de0206822483954b41c`, repository `anton-abyzov/specwithcode`.

Verdict: ship

I found no material issues. Each requested check holds at this head:

| Check | Result | Where |
|---|---|---|
| Header and details use the same saved check | Both build it from the fleet's machine list. | `StudioFleetConnections.tsx:377-381`, `usePrimaryFleet.ts:36-44` |
| Saved Connect route, preferred or alternate | Recognized when Connect is the main address and when Tailscale is. | `fleetAutoConnect.ts:120-141` |
| Direct-only moved machine | Still offered Connect machine. | `fleetAutoConnect.ts:157-163` |
| Auto-pair | Checks only the main address, so a missing Tailscale route still gets added. | `fleetAutoConnect.ts:200`, `:219` |
| Rejected device, route for another machine | Neither counts as saved. | `fleetAutoConnect.ts:131`, `:138` |
| Live status and authorization | No code reads the saved-route result for Online, Connecting or access. | — |

**Tests:** the three targeted suites passed at this head: 3 files, 100 tests, run directly in the worktree because another 1430 verify run held the shared checks copy. That count is lower than the 134 you mentioned, so the 134 probably included other files. I didn't rerun those.

**Low, not a regression (both behaved the same at base):**

1. `AutoConnectPrivateMachines.tsx:62-68` and `machineChecking.ts:113` don't pass the fleet machines in. On those background paths, a machine connected only through Connect, with no Tailscale address, still looks unsaved. The only effect is an extra fleet refresh every `OFFLINE_RECHECK_MS`; nothing is paired and no button appears. Fix if wanted: pass `snapshot?.machines` at both call sites.
2. A machine that answered as a different machine (identity mismatch) but has a saved Connect route reads as saved. Saved direct routes already worked this way, and the status line still shows the mismatch.
