<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=9c7f3d50631c117060ded003fcd2460d5b50914c at=2026-11-19T20:48:11.010Z -->
# Review: 1390 handoff plan RPC, fix round 1
Verdict: fix first

Reviewer context: fresh session. Git object delta `6dd1443b8f480a175302ea20a5933a110dec7488` to `9c7f3d50631c117060ded003fcd2460d5b50914c`. No build or tests run, as requested. Citations are relative to `/Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specwithcode`.

## 1. [high] Project denial: not closed for mixed versions

The updated peer returns null evidence before inspecting tracks or sign-ins at `apps/server/src/handoff/handoffPlan.ts:205-214`. But the pre-fix peer can return both a project grant failure and account evidence (old head, same file, lines 205-208 and 287-290). The current source preserves both at `apps/server/src/handoff/handoffPlan.ts:364-368`. `apps/server/src/handoff/handoffPlanRead.ts:426-436` copies that denied evidence into the picker, exposing provider name, account relationship and percentage. Suppress evidence on a grant refusal at the source, too. Cover a compatible peer response carrying both fields.

## 2. Measured-only submission: closed

`apps/web/src/components/handoff/HandOffMachineDialog.tsx:591-596,623-634,705` keeps display-only plans separate from measured responses for the chosen destination. Both the form and button wait for readiness (lines 271-280 and 442-447); submission intersects the selected rows with the measured movable IDs (lines 776-794). Neither client rows nor an unmeasured cached response can authorize a submit.

## 3. [medium] Automatic destination: not closed for mixed readings

`apps/server/src/handoff/handoffPlanRead.ts:427-435` keeps the first result for each provider display name. If two threads resolve to the same provider label, a fresh different-account result followed by a same-account or stale result leaves only `automatic: true`. `apps/web/src/components/handoff/handOffMachinePlan.ts:100-107` then qualifies the machine for preselection. Compute eligibility across all relevant checks before deduplicating display lines. Preselection alone does not move a thread; this is not the blocker.

## 4. [low] Other regression: excess selected folder work silently stays

`apps/web/src/components/handoff/handOffMachineRows.ts:152-168` allows up to 100 selected rows. With 21 eligible folder rows selected, `apps/web/src/components/handoff/HandOffMachineDialog.tsx:788-794` sends only the first 20 (`packages/contracts/src/handoffTransfer.ts:317`). The 21st stays without a selection-limit warning. Enforce the folder cap at selection time or identify which rows will stay. This is fail-closed.
