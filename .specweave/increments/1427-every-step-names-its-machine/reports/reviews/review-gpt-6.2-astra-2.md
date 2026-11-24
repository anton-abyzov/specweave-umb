<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=6f87dcfc613fc684841381918d73b523b3281a6a at=2026-11-19T22:47:26.300Z -->
# Review: 1427 T-03 action surfaces, anton-abyzov/specwithcode#756
Verdict: fix first

Reviewer context: fresh session, GPT-6.2 Astra. Reviewed `33a53f50ed5a817071d513f1e77531394441384b` to `6f87dcfc613fc684841381918d73b523b3281a6a` from Git objects. No checkout, build or tests. Citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

## [high] The machine named on an actionable control can differ from its destination

After a handoff from A to B, A's source thread records B as its execution machine (`apps/server/src/handoff/handoffFence.ts:184-195`). In a window on A viewing that source, the web action label therefore names B (`apps/web/src/components/ChatView.tsx:5130-5138`). But an expired-sign-in button uses that label while invoking the original callback (`apps/web/src/components/chat/ThreadErrorBanner.tsx:198-205`): “Sign in again on B” opens **A's** provider settings. The callback takes the failed instance to the route's `environmentId`, not B (`apps/web/src/components/ChatView.tsx:10523-10535`, `:6944-6949`). The provider status banner has the same mismatch (`:15777-15782`). Opening setup does not itself sign anyone in.

The same split is consequential for consent. The access panel receives A as its RPC destination and B as its display machine (`apps/web/src/components/ChatView.tsx:15500-15507`). If a request on A is still answerable, “Always allow on B” sends a machine-scope answer to A (`apps/web/src/components/chat/AccessRequestCard.tsx:150-154`, `:317-335`); the receiving server persists it in its own machine grant list (`apps/server/src/access/AccessRequests.ts:173-191`). A rejected or expired request does not create a grant. No handler was rerouted by this diff; the regression is that the new wording promises a different destination from the one the handler uses.

Derive the label from the exact environment bound to each callback. Do not silently redirect an existing request or provider instance to another host. Add an integration case where the window, serving environment and execution machine are not all the same; assert the displayed machine against the dispatched environment.

## Follow-ups

- **[medium] Name fallback:** Even a surface intended to name B can print A when B has no nickname or execution label: the fallback passed for B is the active environment A's label (`apps/web/src/components/ChatView.tsx:3332-3333`, `:5130-5135`). Use a fallback label only when it belongs to the selected ID.
- **[medium] iOS attribution:** The approval row uses the current session label (`apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift:240`), which comes from the controller environment, not the shell's execution machine (`apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift:446-463`). This can name the source on a handed-off thread. Access cards prefer the app subject's host where present (`apps/ios/SWCKit/Sources/SWCFeatures/Support/Mapping.swift:140`).
- **[low] Colour:** The in-app toast receives a plain string rather than a coloured machine name (`apps/web/src/components/ThreadNotificationCoordinator.tsx:691-699`, `apps/web/src/studio/actionMachine.tsx:95-98`). Unlike an OS notification, the in-app surface can render the colour.

## Access and denial

No grant-decision change or denial leak found in the server diff. The nickname or descriptor label is added to the card subject only. The app key still comes from the app label, `isAllowed` still takes the thread ID and subject key, and the denied result contains status and `asked`, not host metadata or app contents (`apps/server/src/access/accessGate.ts:80-96`, `:115-127`, `:178-199`). Approval, access-answer, notification and recovery callbacks retain their original targets.
