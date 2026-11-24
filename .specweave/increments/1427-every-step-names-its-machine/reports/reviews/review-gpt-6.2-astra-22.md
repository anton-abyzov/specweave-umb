<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=8975949d86d289bf17e81b29e933ab0234933d9d at=2026-11-20T01:16:38.069Z -->
# Review: 1427 in-app toast machine colour
Verdict: fix first
Reviewer context: fresh session, read-only review of `8975949d86d289bf17e81b29e933ab0234933d9d`. No tests run.

## [high] `apps/web/src/components/ThreadNotificationCoordinator.tsx:619` can name a different machine from Open thread

With the window and thread environment on M5 and execution handed off to linux-mini, lines 583-591 select linux-mini for the suffix. Open thread passes M5's `environmentId` at lines 735-739. The title therefore says “Input needed on linux-mini” where it should have no suffix. Derive the toast identity and fallback label from the click destination.

The test at `apps/web/src/components/ThreadNotificationCoordinator.test.tsx:942` requires `env-1`, not the window's `env-2`, but does not separate execution from dispatch. Cover a handoff and compare the title with the click target, including the local no-suffix case.

Nicknames render as React text (`apps/web/src/studio/actionMachine.tsx:108`); desktop notifications still receive strings. I agree with leaving iOS unchanged: `apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift:240` supplies the session label, line 1382 passes the chat target, and `apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Sessions.swift:721` dispatches on `target.environmentId`.
