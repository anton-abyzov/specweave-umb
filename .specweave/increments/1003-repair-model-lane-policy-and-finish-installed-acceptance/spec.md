# Repair model lane policy and finish installed acceptance

## Problem
0999 shipped model lanes but its closure proved staging rather than installation. Review also found that lanes bypass minimumTier and can retain an explicitly avoided baseline.

## Scope
Repair lane eligibility and fail closed when no permissible lane or baseline can run. Preserve explicit pins. Merge and release the repair, then verify the installed Mac and real complex/routine routing with exhausted-provider skipping.

## Acceptance Criteria
- [ ] AC-01: Lane selection respects minimumTier, including learned preferences and unknown model tiers.
- [ ] AC-02: Matching avoid rules cannot leak through baseline or Auto fallback; no permissible model yields an explicit model_unavailable response before dispatch.
- [ ] AC-03: Repair PR passes CI and merges; signed and notarized release is published and installed on this Mac; installed complex/routine routing and exhausted-provider skip have receipts.

## Approach
Reuse tierRank/modelTier for lane eligibility. Keep the lane decision authoritative when configured. Validate its baseline before retaining it. Exercise shared router and MCP launch path, then use the documented signed macOS release and managed update flow.

## Decisions
### Defaulted
- If every permitted model is unavailable, refuse the launch rather than override an avoid rule or tier floor.
- Keep 0999 historical records; this follow-up supplies its missing acceptance.
### Open
- none

## Tasks
### T-01 Repair and test lane policy
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/model-lane-policy/packages/shared/src/modelLanes.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-lane-policy/packages/shared/src/modelLanes.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-lane-policy/apps/server/src/project/TaskRouting.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-lane-policy/apps/server/src/mcp/OrchestratorMcpTaskRouting.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/model-lane-policy/apps/server/src/mcp/OrchestratorMcpService.ts | Test: focused modelLanes and OrchestratorMcpTaskRouting tests, production server build

### T-02 Merge, release, and verify installed routing
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/model-lanes-20261022/installed-acceptance | Test: CI terminal success, notarized release gate, installed version readbacks and routing receipts

### T-03 Verify and close 1003
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1003-repair-model-lane-policy-and-finish-installed-acceptance | Test: specweave verify and fresh-context review
