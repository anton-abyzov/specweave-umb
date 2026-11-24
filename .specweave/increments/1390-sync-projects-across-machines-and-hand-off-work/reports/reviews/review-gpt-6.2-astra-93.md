<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=5f8beeefc9293ae65412c120cbc50ccfc6ddb02f at=2026-11-19T19:29:52.175Z -->
# Review: 1390 T-12 handoff selection delta
Verdict: ship
Reviewer context: fresh session; Git objects only, 069f4dad1 to 5f8beeefc9293ae65412c120cbc50ccfc6ddb02f.

Item 1 closed. In `apps/web/src/components/handoff/HandOffMachineDialog.tsx:539-541` the initial ticks are chosen once. In `apps/web/src/components/handoff/handOffMachineRows.ts:158-163` unticking removes only that ID, leaving 99 without selecting row 101.

Item 3 closed. `apps/web/src/components/handoff/handOffMachineRows.ts:179-180` serializes the array as JSON; `apps/web/src/components/handoff/HandOffMachineDialog.tsx:553-566` parses and sends that array. A comma inside an ID remains part of that ID.

No fail-open regression found. `apps/web/src/components/handoff/handOffMachineRows.ts:129-130` excludes staying rows, and line 171 intersects eligible rows with stored ticks. `apps/web/src/components/handoff/HandOffMachineDialog.tsx:680-693` submits only selected IDs with successful preflight.
