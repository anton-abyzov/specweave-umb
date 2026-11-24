<!-- specweave review: reviewer=gpt-6.2-astra model=gpt-6.2-astra family=openai author=unknown depth=standard repo=repositories/anton-abyzov/specwithcode base=8ad73fe68f10f3d4afcfd76b3a6948ca4944a0f8 head=8bafacd234e48461d2dd070028082a9c1150e68e at=2026-11-20T00:23:34.929Z -->
# Review: 1427 T-01, machine names in prompts and hints
Verdict: ship

Reviewer context: independent static review of `anton-abyzov/specwithcode#766`, from `1e6523111a7a4cdab30d7e0712576cc909487240` to `8bafacd234e48461d2dd070028082a9c1150e68e`. No checkout, build or test run.

The prior prompt finding is resolved. Nickname and joined-name fallback remain raw at lookup (`apps/server/src/fleet/machineNames.ts:49`). Local and fleet placement names, coordinator text and worker text all pass through `fenceLine` before interpolation (`apps/server/src/project/ProjectWorkspaceService.ts:176`, `:198`, `:211`); chat and bare-project workers reuse the same renderer. The clock fences only the label (`apps/server/src/project/currentTimeLine.ts:20`), leaving the prefix recognized by the memory fence (`apps/server/src/project/promptFence.ts:23`). The assertions inspect rendered roles, placement text and clock text for mentions and tags, then pass the rendered clock back through the memory fence (`apps/server/src/project/ProjectWorkspaceService.test.ts:925`, `apps/server/src/project/currentTimeLine.test.ts:41`).

The hint now identifies the responding server, falling back to “this machine” only when its label is unavailable. The test asserts “was not found on studio-host.” (`apps/server/src/mcp/threadNotFoundHint.ts:38`, `apps/server/src/mcp/threadNotFoundHint.test.ts:139`). The delta changes no grant predicate and introduces no identifiable real host, person's name or private path.

## [low] `apps/server/src/fleet/RemoteWorkers.test.ts:812` no longer checks which machine acts

The new regex removes the literal machine names, but swapping the responding machine and the target would still pass. Assert the ordered phrase using two distinct neutral fixture labels. This is a coverage regression, not a defect in the current message.
