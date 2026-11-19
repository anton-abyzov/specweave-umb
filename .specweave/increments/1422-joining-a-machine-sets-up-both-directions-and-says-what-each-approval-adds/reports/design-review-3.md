# Design review 3: 1422 one-way join

Reviewer: Codex GPT-6.2 Sol, effort high, on M5 (Muse Wonderful out until November 23, 2026). November 19, 2026, 10:07 PM UTC. Read the spec after round 5 (`d17f931761`, `1ab33e2544`, `99ca1474ae`) and app `origin/main`. Thread: studio://thread/644195cc-3df8-418f-9708-3cd5ff059725/mcp%3Abf2606a2-0ce5-4a5b-8857-a2f954f39a8a

Verdict: Design: fix first. D-03 fix first, D-01 fix first, D-02/D-06 fix first.

## Baseline checked by the owner thread at app `origin/main` `0ec9cd966`

- Device approval gates only Connect and phone-link sessions: `gatedDevice` returns null for every other subject (`apps/server/src/fleet/ConnectDeviceTrust.ts:162-182`). A management key (`fleet-invitation`, coordinator principal) is never asked for a device code.
- The websocket ticket needs only an authenticated session, no scope (`apps/server/src/auth/http.ts:650-663`).
- The pairing route needs `access:write` and accepts a coordinator session (`apps/server/src/auth/http.ts:712-740`), so a management key can mint a pairing code that lets a window in with no device approval.
- So today every join already gives the joined machine app-level reach into the new machine through its management key, with no device code.

## Findings, sorted by kind

Kinds: **New** = exposure the design itself adds (blocks); **Promise** = shipped exposure the design promised to close but does not yet; **Regression** = the design would break a working flow.

| Severity | Finding | Kind |
|---|---|---|
| Critical | Workers-only access: the management session of a reverse tie still carries standard app scopes, is exempt from device approval and can mint a websocket ticket; tickets carry no scope, so a rollback restores the row's known scopes. Fix: endpoint allowlist for workers-only sessions and no ticket. (`ConnectDeviceTrust.ts:162`, `auth/http.ts:650`, `SessionStore.ts:1350`) | Promise (today's management key already does this) |
| High | First spend: destination and ticket checks compare fields in an unsigned line envelope; a different invitation can match them and reserve the approval. Fix: verify the issuer's binding before reservation and at redeem. (`studioFleetJoin.ts:150`, `:366`) | Promise (today's code approves a full device, which can hand over any line) |
| High | Cap and renewal: MCP approval drops scopes and renewal needs exactly two scopes with an exact row match, so the marker can be lost at issuance or break renewal. (`McpOAuth.ts:494`, `SessionStore.ts:1165`, `FleetWorkerGrants.ts:317`) | Promise for the cap; Regression risk for renewal |
| High | Vouch generation: a grant can expire before the sweep records Stop. Fix: check `endsAt` at authorization, bump on expiry, never reuse a generation after record loss or rollback. (`WorkGrants.ts:227`, `:711`) | New (the vouch is new access) |
| High | Remove: a failed remote worker revoke can be followed by management revoke and local deletion, losing the credential needed to retry; the lease bounds stale vouch access to 24 hours. (`studioFleetJoin.ts:628`) | New for the vouch; the offline delay is the owner's lease question |
| High | Automatic open: a loaded snapshot can be stale and saved-route reconciliation has its own registration path. Fix: gate every automatic mint on current policy. (`W/studio/fleet.ts:79`, `W/cloud/ConnectRouteReconciler.tsx:131`) | Promise (today the window opens it automatically anyway) |
| Medium | Rollback: a marked pairing row breaks the old build's whole pairing list until it expires. (`AuthSessions.ts:609`, `AuthPairingLinks.ts:362`, `:401`) | Regression |

Closed from round 2: concurrency barrier before reservation, unrelated phone requests stay visible, key binding before mint in the threat table.

AC-05, AC-06 and AC-10: do not hold as designed under answer A (reviewer).
