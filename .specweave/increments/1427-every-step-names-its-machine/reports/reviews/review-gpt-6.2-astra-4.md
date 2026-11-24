<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=b88be681aa383840f73b4afbca6e09cca627b7d6 at=2026-11-19T23:13:32.040Z -->
# Review: 1427 T-05 coordinator-message receiver
Verdict: fix first

Reviewer context: fresh cross-model review of `anton-abyzov/specwithcode#757` by `gpt-6.2-astra`. Base: `6cf17f9577c89451df95824ccfde708480b8b8a8`. Reviewed head: `b88be681aa383840f73b4afbca6e09cca627b7d6`. Scope: the 10 changed files and the existing authentication, project-link and queue paths they call. Source review only: no checkout, build or tests. No code under review was changed.

Source citations below are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode` and name lines at the reviewed head, not the current checkout.

The HTTP route authenticates the sending machine. The permission it checked is not preserved through deferred delivery. The receiver can also confuse two messages, admit a reference outside the project, and persist more data than it can safely read back.

| # | Severity | File | Lines | Vulnerability | Confidence |
|---|----------|------|-------|---------------|------------|
| 1 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 505–565 | A queued message can reach the agent after its authority ends | 10/10 |
| 2 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 106–110, 293–299 | The actionable-kind gate does not establish permission to run work | 10/10 |
| 3 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 303–316, 353–387, 492–564 | Sender-chosen keys can change another message's contents or delivery state | 10/10 |
| 4 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageStore.ts` | 101–125, 145–169 | The durable inbox has no hard capacity or read-before-parse byte limit | 10/10 |
| 5 | 🟠 HIGH | `apps/server/src/project/CoordinatorMessageReceiver.ts` | 139–150, 278–292 | A valid machine ID vouches for a thread that need not belong to the project | 10/10 |

## [high] Delivery rechecks revocation, not the authority that admitted the row

`apps/server/src/project/CoordinatorMessageReceiver.ts:524–549` looks up the current policy by peer environment and tests `revoked`. It does not repeat `linkedCopyFor`, project scope, or the permission required for the stored kind. Unlinking changes the logical project while retaining the local project ID (`apps/server/src/project/ProjectLink.ts:889–905`). A message admitted before that unlink can still start a turn afterward. The same applies to a project removed from a listed grant. An explicit revocation or expiry that still makes the policy revoked at flush is caught; a revoke followed by a new approval is not proof of uninterrupted authority.

There is a second delivery boundary: when the coordinator is busy, enqueueing succeeds and marks the row delivered before the agent reads it (`apps/server/src/project/CoordinatorMessageReceiver.ts:505–512,549–565`). Rechecking only at the end of the 45-second settle window would leave this gap open.

**Fix:** Bind each row to the admitted project, memberships and approval instance. Use a lookup that cannot create authority. Revalidate live scope, kind, membership, non-personal project and negotiated capability before dispatch and at queue consumption. Keep a refused row visible without passing its text to the agent. A receiver turn that legitimately started before revocation need not be interrupted.

## [high] A sign-in allowlist is not permission to run work

`apps/server/src/project/CoordinatorMessageReceiver.ts:106–110,293–299` equates read-only with `accounts.kind === "none"`. The contracts also permit `listed` with no instances (`packages/contracts/src/studioFleet.ts:394–405`), for which the account policy allows no instance (`apps/server/src/fleet/workGrantPolicy.ts:271–283`). Such a policy passes the receiver's `problem`/`request` test despite permitting no sign-in. The receiver test at `apps/server/src/project/CoordinatorMessageReceiver.test.ts:389–400` exercises only `none`.

This also fails for an authenticated coordinator credential with read-only access. The OAuth flow binds the coordinator principal separately from its access level (`apps/server/src/auth/McpOAuth.ts:494–512,530–549,613–623`). Authentication reports `read-only` when the credential lacks operate scope (`apps/server/src/auth/EnvironmentAuth.ts:1566–1624`), but the route does not require that scope for an actionable message (`apps/server/src/handoff/handoffRoute.ts:163–179,201–206,223–227`). A read-only coordinator credential paired with a broader account policy therefore passes the kind check. This does not apply to an anonymous caller or an ordinary client without a coordinator principal.

**Fix:** Carry the authenticated operate permission separately from the runtime ceiling. Require it and an effective work-capable policy for actionable kinds, not a particular spelling of the account policy. Recheck the resulting kind on merge and delivery; keep `finding` and valid `reply` available to a read-only peer.

## [high] Message IDs and merge keys lose the identity of their owner

`apps/server/src/project/CoordinatorMessageReceiver.ts:492–499,515–529,542–564` groups ordinary rows by sender-supplied message ID, checks the first row, and applies its delivered or revoked state to incoming rows selected by ID. Independent peers can legitimately supply the same ID. Only one message is framed, but the other peer's message can be marked delivered or revoked. Cross-thread command receipt checks occur too late to protect these rows.

The retry and reply lookups omit the project. Merge checks the local project but not the original kind or reply target, and retains the old kind and an omitted step (`apps/server/src/project/CoordinatorMessageReceiver.ts:303–316,353–387`). Thus a nominally informational update can replace the content of an actionable row without being authorized as that kind.

**Fix:** Give each row a receiver-owned identity. Namespace external keys by authenticated peer, direction and project. Use the same identity for retries, reply targets, orchestration commands and state transitions. Merge only compatible kinds and reply targets, and mark only the specific revision actually delivered.

## [high] A wake rate limit does not bound persistent storage

On a paused project, distinct findings are held. After six, each further distinct finding gets its own folded row (`apps/server/src/project/CoordinatorMessageReceiver.ts:388–425,532–540`). Neither the 24-hour hold window nor seven-day retention bounds how many rows may accumulate in that period. `apps/server/src/project/CoordinatorMessageStore.ts:35–37,65–70,101–125,145–169` accepts an uncapped array and reads the whole file before decoding it. The 1 MiB HTTP body limit and 32-ID per-merge limit do not bound the allocation required on the next store read.

**Fix:** Enforce both a row and a byte budget before writing, including pending and folded entries. Bound digest contents and reject or compact overflow. Check the persisted byte limit on the read handle before decoding. The store pathname itself is fixed under the app's `stateDir`; this finding is not path traversal.

## [high] Thread-reference admission proves the machine, not the thread

`apps/server/src/project/CoordinatorMessageReceiver.ts:278–292` validates the referenced environment against project membership but not the thread's ownership. A member machine can host threads for several projects. A reference naming that machine and a different project's thread is admitted and rendered as a suggested read (`apps/server/src/project/CoordinatorMessageReceiver.ts:139–150`). This breaks the requested reference boundary even if a subsequent tool refuses the read. No automatic read or data disclosure is asserted.

**Fix:** Bind thread references to the exact logical project and verify ownership at the authoritative machine. Omit or reject a reference whose ownership cannot be established; repeat the check on dereference. The user-step machine must also be a member.

## Boundaries checked

- **Authentication and body order:** `apps/server/src/handoff/handoffRoute.ts:147–151,163–229,310–316` authenticates and performs the initial grant checks before reading this body. The caller environment is derived from the authenticated grant, not the JSON. `apps/server/src/fleet/WorkGrants.ts:343–366,424–454,508–524` can initialize a missing policy for a live coordinator credential; it cannot create the underlying approval for an unpaired caller. The route therefore does not prove a policy row already existed. Require a non-creating lookup if a missing policy must refuse. Project and kind checks follow bounded decoding because those fields are in the body. The existing pre-refusal read for `takeover` is not used by the new route.
- **Project kind:** `apps/server/src/server.ts:836–845,1138` installs the receiver service globally. `apps/server/src/project/LinkedPeerRoute.ts:129–150`, not layer registration, refuses a personal project at admission. This does not substitute for checking the target again at delivery.
- **Capability:** A request without the sender's v1 advertisement is refused. The local handler implements v1 and advertises it in the success response. This is not a sender-side preflight or evidence that bilateral capability is revalidated at consumption.
- **Turn identity and direct steering:** `apps/server/src/project/CoordinatorMessageReceiver.ts:466–480` requests queued delivery as an agent notification. It supplies no sender model, work origin, steering command or answer IDs. `apps/server/src/orchestration-v2/Orchestrator.ts:6160,6202–6212,6255–6288` uses the destination thread's model selection; the active-turn steering exception is for delegated completions. The notification is stored with conversation role `user` **and** `createdBy: agent`; it is not a human-authored forward (`apps/server/src/orchestration-v2/Notification.ts:244–266`; `apps/server/src/mcp/OrchestratorMcpService.ts:1661–1669,4614–4634`).
- **Pending input and holds:** A blocking run queues the notification; the dispatch does not release older held rows. With no blocking run, a message-mode question can remain open while the receiver starts its own turn. Starting that turn does not answer, approve, dismiss or close the card (`apps/server/src/orchestration-v2/Orchestrator.ts:6459–6477,6586–6598,6792–6808,13239–13244`; `apps/server/src/orchestration-v2/blockingRuntimeRequest.ts:33–49`).
- **Other paths and file writes:** No broadened existing peer route or sender-controlled store pathname was found. The receiver uses a fixed file and temporary-file rename under `stateDir` (`apps/server/src/project/CoordinatorMessageStore.ts:35,145–169`). Ref text is not used as a receiver write path. The existing `studio_thread_send` denial for an active linked receiver-owned coordinator is unchanged. Earlier compatibility exceptions in `apps/server/src/mcp/workGrantAccess.ts:283–311` prevent claiming that denial is universal.

## Follow-ups, not additional blockers

- Persist trusted `peerMessage` metadata through `apps/server/src/orchestration-v2/ThreadManagementService.ts:608–622` so later UI and reply restrictions need not infer provenance from text. This receiver review does not certify future sender-tool, UI or phone-notification behavior.
- `apps/server/src/project/CoordinatorMessageReceiver.ts:436–479` falls back when a local member is absent and uses the resolved shell's project ID. Require the exact authorized project and its live coordinator binding before enqueue. A mismatched shell was not established on a normal admission path.
