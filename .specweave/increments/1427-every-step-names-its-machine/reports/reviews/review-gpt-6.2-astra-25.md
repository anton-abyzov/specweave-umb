<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=037ad649ff9ff764e99b288a5a77a1abcb4538ba at=2026-11-20T01:47:38.592Z -->
# Review: 1427 toast click destination
Verdict: ship
Reviewer context: fresh session; read-only delta review at `037ad649ff9ff764e99b288a5a77a1abcb4538ba`. No tests run.

The previous blocker is fixed. `apps/web/src/components/ThreadNotificationCoordinator.tsx:581` resolves the suffix from the same `environmentId` that Open thread passes at line 731. The fallback label belongs to that environment; `apps/web/src/studio/actionMachine.tsx:33` suppresses the suffix for the window's own environment.

The regression at `apps/web/src/components/ThreadNotificationCoordinator.test.tsx:965` clicks Open thread and checks the remote label and local unsuffixed title with a conflicting execution label. It models label disagreement, not a divergent execution ID: the existing case at line 754 expects no toast for a copy running elsewhere.

The shared helper diff changes only a comment, so the cards from `anton-abyzov/specwithcode#756` are unchanged. The badge diff only adds a hook mock to its test.
