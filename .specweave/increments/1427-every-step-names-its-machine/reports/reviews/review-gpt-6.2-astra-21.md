<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=db9e99cc5a216c62913e2b6ae5ffc57a2792c5c0 at=2026-11-20T00:54:21.728Z -->
# Review: 1427 T-05 coordinator-message receiver, round 5
Verdict: fix first

Reviewer context: fresh cross-family static review of `anton-abyzov/specwithcode#757`. The reviewed range is `a230a04ee9a5d2d9e23fef98ba3c3e2a664d50d1` through `db9e99cc5a216c62913e2b6ae5ffc57a2792c5c0`. Source citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` at that head. This verdict covers receiver authority for T-05, not the rest of the increment.

**The device fix stands.** The fast-forward `bfdd47cbc` → `865176ab9` → `db9e99cc5` changes only the receiver and its delta test. If a row has no recorded device facts, the receiver now refuses it rather than treating it as an unbound credential. The new test asserts zero sends and a refused row. Neither commit changes the credential-expiry calculation, the durable commit, or provider-busy recovery. The three blockers below apply to new messages at this head.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 930-934 | Session renewal can extend a pending message past the presenting credential's signed expiry. | 10/10 |
| 2 | 🟠 HIGH | `apps/server/src/orchestration-v2/Orchestrator.ts` | 6161-6169, 13646-13659 | A deadline can pass between the locked clock check and the durable message commit. | 10/10 |
| 3 | 🟠 HIGH | `apps/server/src/orchestration-v2/RunExecutionService.ts` | 1588-1605, 1644-1660 | Provider-busy recovery can queue a not-yet-offered start-only message behind a live turn. | 9/10 |

## Route-to-flush parity

The revised PR table correctly includes the URL parse and installed-receiver checks. The HTTP `POST` constraint is implicit. None of those three is continuing sender authority. The material discrepancies are which expiry is checked, when the check occurs, and whether a start can be deferred after dispatch.

In the citations below, `H` is `apps/server/src/handoff/handoffRoute.ts`, `R` is `apps/server/src/project/CoordinatorMessageReceiver.ts`, `A` is `apps/server/src/auth/EnvironmentAuth.ts`, and `O` is `apps/server/src/orchestration-v2/Orchestrator.ts`.

| Route check | Flush or start at reviewed head | Assessment |
|---|---|---|
| Update hold, `H:131-140` | No receiver recheck; `O:13737-13752` independently gates dispatch. | Agree: availability, not sender authority. |
| POST, URL parse and known path, `H:125-127,142-144` | No deferred HTTP request. | Agree: none needs repeating. |
| Receiver installed, `H:164-165,319-326` | Flush runs inside that service. | Agree: no repeat needed. |
| Credential, signature, live session and expiry, `H:167-169`, `A:1579-1588` | `R:886-894,930-934`; `A:1348-1352`; `apps/server/src/auth/SessionStore.ts:1070-1131,1368-1392`. | Signature verification is admission-only. The session lookup excludes revoked rows; principal revocation sets their tombstones (`apps/server/src/persistence/AuthSessions.ts:328-339,438-445`). Flush explicitly rejects an expired connected session. Its mutable expiry is not necessarily the signed expiry (finding 1). |
| MCP subject and coordinator identity, `A:1589-1590`, `R:431-438` | `R:886-892` checks the same session ID and the sender's coordinator principal. | Agree by continuity of identity, not a second literal subject comparison. |
| Bearer/DPoP method and request proof, `A:1591-1593,1600-1610` | No request proof at flush; device facts are handled separately. | Agree: request-specific proof is not repeatable. |
| Coordinator bearer over Connect, `A:1594-1598` | No transport at flush. | Agree: applies only where the credential is presented. |
| Device approval, `A:1616-1637`, `H:329-331` | `R:675-680,895-903`; `A:1777-1778`; `apps/server/src/auth/mcpClientDevice.ts:17-25,32-40`. | Agree for the admitted binding. The method is read-only and refuses missing evidence; see below. The helper ends at line 40, not 41. |
| Kept grant, `H:172-176` | `R:425-438,446-466,491-498,924-929` | Agree: read without creating a grant and require the admitted policy stamp. |
| Missing grant, `H:177-186` | `R:448-457,499-501,914-929` | Agree: absent policy or a failed policy read cannot authorize delivery. |
| Revoked or timed-out grant, `H:188-200` | `R:459-466,502-508,930-934`; `apps/server/src/fleet/WorkGrants.ts:234-250`; `O:6161-6169`. | Correct grant source and inclusive expiry comparison, but not a commit-time guarantee (finding 2). |
| Team-rule reach, `H:202-209` | `H:330`; `R:676-678,905-913` | Agree: current rules, same reach decision and admitted fingerprint. |
| Runtime ceiling, `H:210-215` | `R:1028-1049` sets neither runtime nor model; `O:6170,6968-6976` uses the destination thread. | Agree: the turn is not run under the sender's runtime. |
| HTTP body size, `H:217-238` | Declared and actual request length are bounded at ingress. | Agree: no deferred HTTP body to measure. |
| Wire decode, `H:319-324` | `R:595-619` validates the message; `apps/server/src/project/CoordinatorMessageStore.ts:60-63,109-115` decodes stored records. | Agree: no wire re-decode needed. Store decoding enforces record shape, not every semantic input limit. |
| Operate scope, `H:328` | `R:516-522,673,919` intersects admitted and current operate authority. | Agree: read-only may send a finding or reply, not a problem or request. |
| `deliver` authorization, `R:584-594` | `R:491-530,914-929`; `apps/server/src/project/LinkedPeerRoute.ts:129-151`. | Agree: same authorization function, current linked non-personal project, grant coverage, exact membership stamp, admitted capability advertisement and kind. No later capability negotiation is claimed. |

`R:964` checks each **row**, not once per group. The first clock reading is shared by the group. `R:1007-1018` checks each selected row again after the destination and reference lookups. A failed row suppresses the entire prepared send. Every passing row contributes to the minimum deadline; a non-finite result suppresses the send.

## [high] `apps/server/src/project/CoordinatorMessageReceiver.ts:930-934` loses the admitting credential's expiry

The route rejects the presented token at its signed `exp`. Verification returns that expiry, but neither the authenticated MCP result nor the admission stores it (`apps/server/src/auth/SessionStore.ts:1084-1097,1117-1131`; `A:1627-1638`; `R:671-681`). Renewal accepts the matching coordinator principal and updates `expires_at` on the **same session ID** (`apps/server/src/auth/SessionStore.ts:1189-1227`; `apps/server/src/persistence/AuthSessions.ts:403-417`). A held message can pass both flush checks after the credential that sent it would fail at ingress.

Keep the verified expiry with the admitted message revision. Bound the start by the earliest of that immutable expiry, the current session expiry and the kept grant end. A new merged revision should keep its own admission.

## [high] `apps/server/src/orchestration-v2/Orchestrator.ts:6161-6169` checks before commit

The PR's lock ordering is correct: `dispatchWithoutPermissionGate` takes the thread lock, `dispatchWithReceiptEffect` calls `dispatchOnce`, and `dispatchMessage` checks the orchestrator's own clock (`O:13710-13735,13451,12846,5851,6161-6169`). Equality refuses without a queue entry or rejection receipt (`O:13562-13575`). With no deadline this branch does nothing, and a caller-supplied deadline cannot authorize an otherwise forbidden dispatch.

But runtime-policy resolution and checkpoint preparation run **after** the comparison (`O:6965-6989`). The planned run is `starting`, with `startedAt: null` (`O:6990-7004`). `commitCommand` then persists the message and start effect without checking a deadline (`O:13646-13659`). Expiry during that work does not prevent the message becoming durable on the coordinator thread. Enforce the bound at durable admission before recording the message, start effect or success receipt.

## [high] `apps/server/src/orchestration-v2/RunExecutionService.ts:1588-1605,1644-1660` requeues a new start-only message

Initial dispatch refuses a busy or usage-held thread rather than enqueueing (`O:6476-6493`). But the durable provider-start request carries only `runId`, losing both restrictions (`O:7213-7221,8157-8163`). That effect can wait behind earlier pending or running work on the thread (`apps/server/src/orchestration-v2/EffectOutbox.ts:380-425`). `sendToThread` can report `started` from the projected run before the provider has accepted the prompt (`apps/server/src/orchestration-v2/ThreadManagementService.ts:629-653,660-675`).

Provider-busy recovery checks live ownership (`apps/server/src/orchestration-v2/ProviderTurnStartService.ts:332-345,1870-1872`). If another live run owns the previous turn, the code explicitly says no prompt was offered, sets this run back to `queued` at position 1 and clears its start time. The ordinary queue reactor then calls `startNextQueuedRun`, not the receiver's authorization check (`O:13789-13804`). Authority can end while the message waits behind the other turn.

Preserve the start-only restriction until the first provider offer. A deferred or provider-busy start must not become an ordinary queued turn; a later attempt needs fresh receiver authority. This concerns a new send at the reviewed head, not pre-upgrade state or an already-running turn continuing after revocation.

## Device approval and prior confirmations

- **Missing device facts:** `R:895-903` now distinguishes “not recorded” from “verified credential with no binding.” A missing field or method returns false without calling trust; an error or refusal does not authorize delivery. `apps/server/src/project/CoordinatorMessageReceiver.delta.test.ts:434-447` omits the field and asserts both zero sends and a refused row. Production still records an explicit facts object for a genuinely unbound credential (`A:1637`).
- **Bound device:** Production uses verified claims, not the request body (`A:1616-1637`; `H:325-332`). The read-only MCP path does not create an approval. `apps/server/src/fleet/ConnectDeviceTrust.ts:162-183,835-847,892-901` requires a single stored entry to match **both key and approval** and refuses an unreadable list for bound credentials. Another device's approval does not satisfy it. For a thumbprint with no signed binding, the existing turned-away-key check returns false on non-OK storage (`apps/server/src/fleet/ConnectDeviceTrust.ts:881-901`). That matches the HTTP route but is not a blanket fail-closed storage guarantee.
- **Reach, membership and revision guard:** Reach is re-evaluated. `R:342-355,816-828,924-929` requires one sender copy, matches both link identities and the local coordinator's project. `R:711-725,850-869,971,1021-1026,1066-1075` ties delivery to the sent IDs and revisions. A newer merge is not acknowledged by an older send.
- **Accepted window:** None of the blockers depends solely on a revocation during the wait for the thread lock. The initial start-only refusal still stands; it does not prevent deferred provider delivery after dispatch.

## Verification, file sizes and public fixtures

Reviewed `ae38e6229`, `bbef8b2c6`, `b7a8d3ebe`, `bfdd47cbc`, `865176ab9` and `db9e99cc5` using fetched objects. The final two commits add 15 test lines and add three/remove two receiver lines. No checkout, install, build or test run. `git diff --check` was clean. There was no increment verification report. The live PR head matched `db9e99cc5a216c62913e2b6ae5ffc57a2792c5c0`; the server and typecheck gates were still running when inspected.

The existing start-only tests assert busy refusal, an untouched held queue, and exact deadline equality (`apps/server/src/orchestration-v2/StartOnlyDispatch.test.ts:120-137,140-178,181-196`). Their effect worker is disabled (`:33-45`), so they do not exercise provider-busy recovery. The receiver tests cover selection of grant/session bounds, revocation during lookup, removal, missing facts, and a failed device check (`apps/server/src/project/CoordinatorMessageReceiver.delta.test.ts:362-401,404-460`). The trust-helper tests check the facts sent to trust and the handling of refusal/failure (`apps/server/src/auth/mcpClientDevice.test.ts:20-46`).

Eleven of 14 delta files are under 1,500 lines, including `R` (1,118) and its delta test (460). No file crossed the threshold. Two oversized files grew by more than a few lines: `apps/server/src/auth/EnvironmentAuth.ts:314-318`, 1,888 → 1,904 (+16), and `apps/server/src/orchestration-v2/Orchestrator.ts:6161-6169,13571-13573`, 14,323 → 14,334 (+11). `packages/contracts/src/orchestrationV2.ts:3515-3516` grew by two, 4,525 → 4,527. File size does not block this authority verdict.

No added person's name, private filesystem path or identifying hostname was found. The public fixture uses the permitted `M5` and `linux-mini` and generic `build-host` and `studio-host` (`apps/server/src/project/CoordinatorMessageReceiver.testkit.ts:32-49`).
