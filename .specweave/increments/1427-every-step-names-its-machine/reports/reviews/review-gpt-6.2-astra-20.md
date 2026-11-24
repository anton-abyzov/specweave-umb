<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=bfdd47cbc290206fe7f000c0eb6aa051215c4cfd at=2026-11-20T00:52:54.997Z -->
# Review: 1427 T-05 coordinator-message receiver, round 5
Verdict: fix first

Reviewer context: fresh cross-family static review of `anton-abyzov/specwithcode#757`. The reviewed range is `a230a04ee9a5d2d9e23fef98ba3c3e2a664d50d1` to `bfdd47cbc290206fe7f000c0eb6aa051215c4cfd`, including `ae38e6229`, `bbef8b2c6`, `b7a8d3ebe` and `bfdd47cbc`. Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at the latter commit. The verdict covers receiver authority, not release readiness or completion of the increment.

The device-bound path now checks the same approval as the HTTP route. Three other cases still let a message reach the coordinator or start after its authority ends. All three apply to new messages at the reviewed head.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 929-932 | Session renewal extends an already admitted message past its credential's signed expiry. | 10/10 |
| 2 | 🟠 HIGH | `apps/server/src/orchestration-v2/Orchestrator.ts` | 6161-6169, 13646-13659 | The deadline is checked before asynchronous start preparation, not at durable admission. | 10/10 |
| 3 | 🟠 HIGH | `apps/server/src/orchestration-v2/RunExecutionService.ts` | 1588-1605, 1644-1660 | A not-yet-offered start-only message can enter the ordinary queue behind a live turn. | 9/10 |

## Route-to-flush parity

The PR table is correct about most ingress checks, but not about expiry equivalence or the point where start becomes irrevocable. It also omits the HTTP method, URL parse and installed-receiver checks. Those three do not grant continuing authority. In the table below, `H` is `apps/server/src/handoff/handoffRoute.ts`, `R` is `apps/server/src/project/CoordinatorMessageReceiver.ts`, `A` is `apps/server/src/auth/EnvironmentAuth.ts`, and `O` is `apps/server/src/orchestration-v2/Orchestrator.ts`.

| Route check at reviewed head | Receiver or start evidence | Assessment |
|---|---|---|
| Update hold, `H:131-140` | No receiver recheck; `O:13737-13752` independently admits commands through the update gate. | Agree: availability, not sender authority. |
| POST, valid URL, known path, receiver installed, `H:125-127,142-144,164-165,319-326` | No deferred HTTP request. | Agree that path need not repeat; same for the three omitted routing prerequisites. |
| Credential present, valid signature, live session and expiry, `H:167-169`, `A:1579-1588` | `R:886-894,929-932`; `A:1348-1352`; `apps/server/src/auth/SessionStore.ts:1070-1117,1368-1392`. | Signature verification belongs to ingress. Flush checks the original session ID, current row and expiry, even for connected sessions. It loses the original signed expiry (finding 1). |
| Subject is `mcp-client` and caller is a coordinator, `A:1589-1590`, `R:431-438` | `R:886-892` requires the same session ID and the sender's coordinator principal. | Agree by continuity of session identity, not a second literal subject comparison. |
| Bearer/DPoP method and request proof, `A:1591-1593,1600-1610` | No request at flush; signed device facts are retained separately. | Agree: proof of possession is request-specific and not repeatable. |
| Coordinator bearer over Connect, `A:1594-1598` | No transport at flush. | Agree: transport restriction applies when the credential is presented. |
| Device approval, `A:1616-1637`, `H:329-331` | `R:675-680,895-902`; `A:1777-1778`; `apps/server/src/auth/mcpClientDevice.ts:17-25,32-40`. | Agree for the admitted binding. The production gate checks the same device key **and** approval; see below. |
| Kept grant, `H:172-176` | `R:425-438,446-466,491-498,923-927`. | Agree: read without creating a grant and require the admitted policy stamp. |
| Missing grant, `H:177-186` | `R:448-457,499-501,913-928`. | Agree: absent policy or read failure cannot authorize delivery. |
| Revoked or timed-out grant, `H:188-200` | `R:459-466,502-508,929-932`; `apps/server/src/fleet/WorkGrants.ts:234-250`; `O:6161-6169`. | Correct grant source and inclusive expiry check, but not at commit (finding 2). |
| Team-rule reach, `H:202-209` | `H:330`; `R:676-678,904-912`. | Agree: same decision using current rules and the admitted sender fingerprint. |
| Runtime ceiling, `H:210-215` | `R:1027-1048` does not set a runtime or model; `O:6170,6968-6976` uses the destination thread. | Agree: this is not a request to execute under the sender's runtime. |
| Declared and actual HTTP body size, `H:217-238` | Bounded on receipt; there is no HTTP body at flush. | Agree: no repeat needed. |
| Wire decode, `H:319-324` | `R:595-619` validates the message; `apps/server/src/project/CoordinatorMessageStore.ts:60-63,109-115` decodes stored records. | Agree: no deferred wire decode needed. Store decoding checks record shape; it does not rerun every semantic input limit. |
| Operate scope, `H:328` | `R:516-522,673,918` intersects admission and current session scope for the kind. | Agree: read-only may send a finding or reply, not a problem or request. |
| Inside `deliver`: project, grant coverage, membership, capability and kind, `R:584-594` | `R:491-530,913-927`; `apps/server/src/project/LinkedPeerRoute.ts:129-151`. | Agree: same authorization function, current linked non-personal project, exact membership stamp, and admitted capability advertisement. No new capability negotiation is claimed. |

`R:963` checks **each row** with one clock reading per group. `R:1006-1016` checks each selected row again after destination and reference lookups. A failed row suppresses the entire prepared send. A passing group takes the minimum of all its row deadlines and rejects a non-finite result.

## [high] `apps/server/src/project/CoordinatorMessageReceiver.ts:929-932` loses the admitting credential's expiry

The route rejects the presented token at its signed `exp`. Verification returns that expiry, but neither the authenticated MCP result nor the admission stores it (`apps/server/src/auth/SessionStore.ts:1084-1097,1117-1131`; `A:1627-1638`; `R:671-681`). Renewal explicitly accepts the matching **coordinator** principal and updates `expires_at` on the **same session ID** (`apps/server/src/auth/SessionStore.ts:1189-1227`; `apps/server/src/persistence/AuthSessions.ts:403-417`). A pending message can therefore pass both flushes after the token that sent it would fail at ingress. This does not require a revocation during dispatch.

Keep the verified expiry with the message revision, including when a new admission replaces merged text. Under no circumstances should the calculated deadline exceed that expiry, the current session expiry, or the kept grant end.

## [high] `apps/server/src/orchestration-v2/Orchestrator.ts:6161-6169` checks before commit

The comparison uses the orchestrator's own clock, inside the thread lock. Equality refuses without a queue entry or rejection receipt (`O:13562-13575,13710-13735`). A command without the field follows the old branch; the field itself can only impose a restriction. But runtime-policy resolution and checkpoint preparation still run **after** the comparison (`O:6965-6989`). The run is then planned as `starting`, with `startedAt: null` (`O:6990-7004`). `commitCommand` persists the events and effects without a deadline (`O:13646-13659`). A deadline that passes during that work does not prevent the message becoming durable on the coordinator thread.

Enforce the bound at the durable admission point as well. If it has passed, neither the message, start effect nor success receipt should be committed.

## [high] `apps/server/src/orchestration-v2/RunExecutionService.ts:1588-1605,1644-1660` requeues a new start-only message

Initial dispatch refuses a busy/usage-held thread rather than enqueueing (`O:6476-6493`). But the durable provider-start request carries only `runId`, not `startOnly` or the deadline (`O:7213-7221,8157-8163`). That effect can wait behind earlier pending or running work on the thread (`apps/server/src/orchestration-v2/EffectOutbox.ts:380-425`). `sendToThread` can report `started` from the projected run before the provider has accepted the prompt (`apps/server/src/orchestration-v2/ThreadManagementService.ts:629-653,660-675`).

In particular, provider-busy recovery consults live ownership (`apps/server/src/orchestration-v2/ProviderTurnStartService.ts:332-345,1870-1872`). If another live run owns the previous turn, the recovery code explicitly says no prompt was offered, sets this run back to `queued` at position 1 and clears its start time. The ordinary queue reactor then calls `startNextQueuedRun`, not the receiver's authorization check (`O:13789-13804`). A grant can end while the message waits behind that turn. This is a new send at the reviewed head, not a pre-upgrade queue entry or an already-running turn continuing after revocation.

Preserve the start-only restriction until the first provider offer. A deferred or provider-busy start must not become an ordinary queued turn; any later attempt needs fresh receiver authority. The test harness at `apps/server/src/orchestration-v2/StartOnlyDispatch.test.ts:33-45` disables the effect worker and cannot exercise this branch.

## Device approval and round 4 confirmations

- **Bound device:** Production admission derives the facts from verified claims, not the peer body (`A:1616-1637`; `H:325-332`). The receiver normalizes the saved facts, then rejects a missing method, failed effect or non-allowed verdict (`R:895-902`; `apps/server/src/auth/mcpClientDevice.ts:17-25,32-40`). For `mcp-client`, `gatedDevice` returns null, so the recheck does not enqueue a new approval. `apps/server/src/fleet/ConnectDeviceTrust.ts:162-183,835-847,892-901` requires the **same entry** to match both key and approval, and refuses unreadable trust storage for a bound credential. A different approved device does not satisfy it.
- **Limit of that statement:** A thumbprint without a signed binding follows the existing turned-away-key check; non-OK storage there reads as “not turned away” (`apps/server/src/fleet/ConnectDeviceTrust.ts:881-901`). That is ingress parity, not a blanket fail-closed storage guarantee. Production at this head emits an explicit facts object even for an unbound credential. No legacy-row scenario is counted as a blocker.
- **Reach, membership and revision guard:** Reach is re-evaluated. `R:342-355,816-828,923-927` requires one sender copy, matches the two link identities and the local coordinator's project. `R:711-725,850-869,970,1020-1025,1065-1074` binds delivery to the sent IDs and revisions. A newer merge is not acknowledged by an older send.
- **Accepted window:** No finding is based solely on a revoke, device removal or reach change after the final row check while acquiring the thread lock. Findings 2 and 3 concern a time limit passing before durable commit and a prompt deferred beyond that commit. The projection-level busy guard is intact; the end-to-end guarantee that nothing waits behind a turn is not.

## Verification evidence

No checkout, dependency install, build or test run. There was no increment verification report. At initial inspection GitHub identified the requested head: the secrets check had passed and server and typecheck gates were still running. The PR subsequently advanced to `db9e99cc5a216c62913e2b6ae5ffc57a2792c5c0`; that revision and its checks are not part of this verdict.

- `apps/server/src/orchestration-v2/StartOnlyDispatch.test.ts:120-137,140-178,181-196` asserts no queued run on busy, a held queue left held, refusal at the exact deadline with no run, and acceptance one millisecond before a later deadline. The deadline test sets the clock before dispatch, not while another command holds the lock.
- `apps/server/src/project/CoordinatorMessageReceiver.delta.test.ts:362-401,404-445` asserts the session and grant bounds independently, revocation during destination lookup, use of the admitted binding, and zero sends after removal or a device-check error. `apps/server/src/auth/mcpClientDevice.test.ts:20-46` checks which facts reach trust and how refusal and failure map to false. The trust double is not evidence that the underlying trust implementation never writes.

## File size and public fixtures

Eleven of the 14 delta files are below 1,500 lines at head. Three were already over. `apps/server/src/auth/EnvironmentAuth.ts:314-318` grew from 1,888 to 1,904 (+16). `apps/server/src/orchestration-v2/Orchestrator.ts:6161-6169,13571-13573` grew from 14,323 to 14,334 (+11). Both exceed a few lines of growth. `packages/contracts/src/orchestrationV2.ts:3515-3516` grew by only two, from 4,525 to 4,527. No file crossed the threshold. These are size follow-ups, not authority findings.

No added person's name, private filesystem path or identifying hostname was found. The public fixture uses the permitted `M5` and `linux-mini`, plus generic `build-host` and `studio-host` (`apps/server/src/project/CoordinatorMessageReceiver.testkit.ts:32-49`).
