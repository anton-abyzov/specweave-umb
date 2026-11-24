<!-- specweave review: reviewer=claude-opus-5-5 model=claude-opus-5-5 family=claude author=openai depth=standard repo=repositories/anton-abyzov/specwithcode base=021ac0536cafcd09a8ce2de0206822483954b41c head=9bc9b82cef5f96bc1e192128ef9defb9c6e188ed at=2026-11-20T05:13:32.063Z -->
I've read the diff and both Settings callers, and the main finding is drafted. Two Sonnet checkers are now trying to refute it and looking for regressions. I'll report when they finish.

Verdict: ship

SHA: `9bc9b82cef5f96bc1e192128ef9defb9c6e188ed` (against `021ac0536cafcd09a8ce2de0206822483954b41c`)

The fix works for a machine that has only a Connect address. A relay route, whether it is the preferred or the alternate route, now counts as saved there, so the stray Connect and Connect machine buttons go away. I found no regressions. Two Sonnet checkers tried to refute this and got the same result.

**Findings**

1. **Medium: the fix does nothing when a tailnet address and a Connect URL coexist** (`apps/web/src/studio/fleetAutoConnect.ts:112-117` and `:156`).
   - When the machine has a `.ts.net` address, a relay route is matched against `connectUrl`. But `fleetMachineSaved` only compares `machine.url`, which is the tailnet address, and no other code compares saved origins to `connectUrl`. So that branch can never match.
   - What the user sees: if the Windows machine advertises a tailnet address and this browser saved it only over Connect, Settings still shows Online with Connect and Connect machine buttons. That happens in v1.0.398 and still happens after this commit. The buttons only add a tailnet route behind the relay, which already ranks ahead of tailnet (`routes.ts:117-124`).
   - All three new tests use a `spec-weave.com` address only, so this case is untested.
   - Smallest fix: in `fleetMachineSaved`, also treat the machine as saved when its `connectUrl` origin is in the saved set. Auto-connect doesn't pass fleet machines, so it would still add the tailnet route on its own. If keeping the button is intended, drop the tailnet branch instead and add a test that says so.

2. **Low, not a regression: auto-connect still treats a Connect-only machine saved over relay as unsaved** (`apps/web/src/components/AutoConnectPrivateMachines.tsx:64` and `apps/web/src/studio/machineChecking.ts:113`).
   - Neither file passes `snapshot?.machines`, so `fleetMachinesAwaitingReach` counts that machine as unsaved, while Settings now calls it saved. Both checkers found nothing new the user sees from this, because v1.0.398 behaved the same way.
   - Fix if wanted: pass `snapshot?.machines` at both call sites.

**Cases checked and fine**
- **Direct host moved:** the old origin stays saved and the new tailnet address still reads as unsaved, so Connect adds the new route as before.
- **Identity mismatch:** the status comes from the session, the same as a saved direct route.
- **Expired credential:** it reads as saved, the same as direct routes did before.
- **Rejected credential:** a `reapprovalRequired` rejection gives an empty set, so Approve again still appears.
- **Another environment:** a relay route with a different environment ID is dropped (`:129`).
- **Older fleet records with no `connectUrl`:** the lookup finds no address and skips the route; nothing breaks.
- **Duplicate IDs in the fleet list:** the last record wins, which is harmless.
- **Memo dependencies** in `usePrimaryFleet` are correct.
- **Original sources unchanged:** session status, privileges (`canPair` and the scope it checks) and auto-connect still come from where they did before.

**Not verified:** I didn't run any tests, so the 133 passing tests are Codex's report, not mine. I also didn't check whether the real Windows machine advertises a `.ts.net` address. If it does, finding 1 is the bug you reported and the verdict becomes fix first.
