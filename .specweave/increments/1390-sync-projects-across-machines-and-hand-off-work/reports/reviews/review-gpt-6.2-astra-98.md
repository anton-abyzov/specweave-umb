<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=515522ce45fb7f8594dc5bb888faa52f4d9d7576 at=2026-11-19T19:46:03.007Z -->
# Review: 1390 T-13 Bring back one handed-off thread
Verdict: ship
Reviewer context: fresh session; web delta from `092cd291c`, Git objects only.

1. Closed. `apps/web/src/components/handoff/bringBack.logic.ts:77-91` returns the pinned source or no destination. Ordinary Hand off still calls its original picker at `apps/web/src/components/handoff/HandOffThreadDialog.tsx:414-421`.
2. Closed for the client. `apps/web/src/components/handoff/BringBack.tsx:34-35` detects sign-in on either shell. `apps/web/src/components/handoff/HandOffThreadDialog.tsx:412-413,468-485` observes the live wait and rereads the same scoped thread before submitting its ID and resolved destination.

No fail-open regression found. The server-side interruption check is outside this review.
