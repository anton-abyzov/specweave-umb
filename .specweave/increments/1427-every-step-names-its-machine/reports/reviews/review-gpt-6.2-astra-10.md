<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=5acf4ba92346fc4b919b5eccc87b996ad6b53ed6 at=2026-11-20T00:11:58.578Z -->
# Review: 1427 T-05 coordinator-message receiver, security delta
Verdict: fix first

Reviewer context: fresh cross-family static review of `anton-abyzov/specwithcode#757`. Base: `7bb49a60625a8f22abe0942426ee584442ac3668`. Head: `5acf4ba92346fc4b919b5eccc87b996ad6b53ed6`. Source citations identify Git objects at that head in `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`. No checkout, clone, install, build or test run. Test citations describe assertions, not execution results.

**The cancel race fails open.** A send-time check permits admission to the receiver, not an unconditional future turn. A turn that starts *before* revocation may continue. A queued turn that starts *after* revocation was never authorized to start. Recording it as delivered prevents a duplicate; it does not change that ordering.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | `apps/server/src/orchestration-v2/Orchestrator.ts` | 1917–1952, 2353–2381 | The queue can start a receiver turn after revocation, before withdrawal succeeds. | 10/10 |
| 2 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 825–853, 856–906 | Deferred delivery can pass after the admitting machine loses reach or its grant expires during a flush. | 9/10 |
| 3 | 🟡 MEDIUM | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 301–310, 724–731, 847–852 | A different project copy on the same machine can supply the membership stamp used to authorize delivery after rejoin. | 9/10 |

## [high] `apps/server/src/orchestration-v2/Orchestrator.ts:1917–1952` starts queued work without checking the sender

The receiver checks for a busy or usage-limited destination, but dispatch can still return `queued`. Enqueue, saving the run ID and cancellation are separate operations. The consumer checks the destination and starts the already-framed message; cancellation cannot withdraw a run that has left the queue. An uncertain dispatch outcome is worse: the run can be persisted before the projection read fails, leaving no returned ID for withdrawal. Ordinary messages and digests use this path. See `apps/server/src/project/CoordinatorMessageReceiver.ts:740–747,934–992`, `apps/server/src/orchestration-v2/ThreadManagementService.ts:608–629,644–665` and `apps/server/src/orchestration-v2/Orchestrator.ts:2353–2381,9608–9614`. The test at `apps/server/src/project/CoordinatorMessageReceiver.test.ts:979–991` accepts a queued run that starts; it checks for duplicates, not live authority.

**Required property (AC-12/13, D-01/D-03):** Either dispatch starts an authorized turn now without ever publishing an independently runnable queue item, or the consumer checks the admission identity and rebuilds the frame at start. Best-effort withdrawal guarantees neither.

## [high] `apps/server/src/project/CoordinatorMessageReceiver.ts:825–853` does not repeat the full route authorization

An unexpired session with operate permission is necessary for an actionable message, but not sufficient. The HTTP route enforces the machine-reach rule; the rule can forbid cross-machine work without revoking the session. Flush checks the session and work policy but not that reach rule. Even an immediate-start send can therefore wake the receiver for a peer that the route would now refuse. Local dispatch checks the receiver's runtime and model policy, not the sender's reach. See `apps/server/src/handoff/handoffRoute.ts:202–209,325–330`, `apps/server/src/teamRules/TeamRulesReach.ts:36–54,62–75` and `apps/server/src/orchestration-v2/Orchestrator.ts:4734–4752`.

Two limits of the recheck matter. First, flush samples `now` once for all groups. A later group can pass a deadline that expired during the pass (`apps/server/src/project/CoordinatorMessageReceiver.ts:394–405,828–845,856–899`). Second, looking up a session row does not itself revalidate a device-bound approval (`apps/server/src/auth/EnvironmentAuth.ts:1599–1624`, `apps/server/src/auth/SessionStore.ts:1378–1392`, `apps/server/src/fleet/ConnectDeviceTrust.ts:835–847`). The independently enforceable reach rule suffices for the finding. Use the same non-mutating authorization decision and current time at the point of use.

## [medium] `apps/server/src/project/CoordinatorMessageReceiver.ts:301–310` stamps the first copy on a machine, not necessarily the destination

The stamp now includes a link ID and generation, which fixes the single-copy rejoin. But the stamp lookup selects by environment ID alone, whereas the destination is selected by local project. The membership contract permits different project IDs on the same environment. If the first copy stays linked while the actual destination leaves and rejoins, the first copy's stamp still matches; a message for the previous membership can pass. See `packages/contracts/src/logicalProject.ts:27–39,47–54`, `apps/server/src/project/LinkedPeerRoute.ts:158–165`, `apps/server/src/project/ProjectLink.ts:674–695` and `apps/server/src/project/CoordinatorMessageReceiver.ts:724–731,847–852`. Bind each end to its exact member, or refuse an ambiguous binding. This blocks because it admits old traffic, not because coverage is missing.

## Disposition of the five prior blockers

| Prior blocker | Disposition at this head |
|---|---|
| 1. Queued versus started | **Not fixed on every path.** A known hold stays in the receiver. A queued dispatch is tracked and withdrawal retried, but the consumer can still start it without reauthorization (finding 1). |
| 2. Grant getters create the policy they require | **Fixed on the enabled message path.** Both checks use `peekPolicy`; a missing policy cannot authorize the message. Takeover and linked sync retain their prior `forClient` behavior. When the optional receiver is absent, a rejected message request can still call the settling getter and create a policy; it cannot deliver through that absent receiver. See `apps/server/src/handoff/handoffRoute.ts:164–195,261–265,319–349`, `apps/server/src/fleet/WorkGrants.ts:448–471,516–531,772–782` and `apps/server/src/project/CoordinatorMessageReceiver.ts:373–405,439–447`. |
| 3. Admitting session and operate scope are snapshots | **Fixed at receiver recheck, not at every possible start.** Each row, including a digest member, must match a live admitting session and coordinator. Actionable kinds require both admitted and current operate permission and a work-capable policy. Findings 1 and 2 explain the remaining boundaries. Peer capabilities are still the admission-time advertisement, not a new negotiation (`apps/server/src/project/CoordinatorMessageReceiver.ts:155–168,409–415,591–597,825–853`). |
| 4. Old membership after rejoin | **Fixed for an unambiguous single copy; open for multiple copies on one environment** (finding 3). |
| 5. Departed machine in a step or ref | **Fixed when the frame is built, not after it enters the independent queue.** The current member set filters machine-bound steps and refs; local thread ownership is checked again. Digests contain subjects rather than step or ref instructions. A queued frame is not rebuilt when consumed (finding 1). See `apps/server/src/project/CoordinatorMessageReceiver.ts:259–268,316–329,479–499,915–932`. No file disclosure or phone notification is inferred. |

## Test and revision follow-ups

- **Both fixture changes are present.** The real-file test round-trips `kept-message` as `externalId`, satisfying the eight-character minimum. The merge test keeps kind and dedupe key constant and varies `replyTo` A/B/A: B is distinct; the second A merges. See `apps/server/src/project/CoordinatorMessageReceiver.test.ts:375–382,734–746,831–842` and `packages/contracts/src/coordinatorMessage.ts:34–38`.
- **The delivered revision is guarded only on the immediate path.** Queued reconciliation persists the thread and run IDs, not the exact row IDs and revisions sent. If the old run executes, reconciliation can mark newer merged text or a new digest member delivered even though the run did not contain it. Keep the sent row IDs and revisions with the run. This is a delivery-integrity follow-up, not a separate authority bypass. See `apps/server/src/project/CoordinatorMessageReceiver.ts:637–641,765–780,866–892,974–992`, `apps/server/src/project/CoordinatorMessageStore.ts:91–99` and `apps/server/src/project/CoordinatorMessageReceiver.test.ts:933–945`.

Only the fail-open findings determine the verdict. The receiver delta provides no end-to-end notification evidence under D-02; none is claimed.
