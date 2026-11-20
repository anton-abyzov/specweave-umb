<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=91cdba369d9fb2efff5da76bf962b69f602a1e71 at=2026-11-20T00:10:29.431Z -->
# Review: 1427 window labels, two-file delta
Verdict: ship

Reviewer context: independent static review of `f0a0030ca75456b71501a396fc12832b8fcfe141` to `91cdba369d9fb2efff5da76bf962b69f602a1e71`. No build or tests run.

`resolveThreadExecution` resolves the owner, runner and runner label before branching on state. `apps/web/src/studio/threadLocation.ts:61` builds the same label for running, unknown and fenced threads. Last-seen time affects only the unknown-state description. `apps/web/src/studio/machineLabels.ts:114` consumes only the IDs and label, so omitting state and time cannot change the suffix. Separately, the new truthiness guards treat empty strings as absent, unlike the old nullish defaults; this is not a change for populated machine IDs and labels.

`apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx:532` wraps the same fixture map in a readable Effect atom. The nickname lookup still reads through the application registry at `apps/web/src/studio/machineNickname.ts:102`; the fixture neither intercepts that read nor catches its errors. No fail-open finding.
