# Display accepted skips in plan criteria

## Problem
The strict SpecWeave plan reader rejects the new accept-skip event from SpecWeave PR #2175, breaking the plan before 0922 can receive its explicitly authorized waiver. The criteria UI has no way to distinguish accepted waivers from verification or unresolved requirements.

## Scope
In: accept-skip compatibility in both app readers, read-only first-complete waiver fold matching CLI head 015bf42a3b417ac19f80e20ec695517ef4b23980, optional acceptance and waiver wire fields, criteria presentation and focused fixtures. Out: CLI/ledger changes, real 0922 writes, invented closed-as-is states, #899 status changes, deployment or restart. The 0922 backfill stays held until this reader is merged and installed.

## Acceptance Criteria
- [ ] AC-01: A ledger with accept-skip remains readable without changing task ownership, evidence, or counts, and without creating an AC task card.
- [ ] AC-02: First complete record per case-insensitive AC/check wins; incomplete/duplicate records do not waive additional requirements. All provenance fields survive.
- [ ] AC-03: Criteria expose CLI-compatible acceptance and waivers. Mixed/accepted-skip ACs never count as verified; unfinished sibling tasks stay open with their waiver evidence visible.
- [ ] AC-04: The UI shows Skipped (accepted) or a mixed label plus named check, reason, acceptor/date and authorization. Ordinary skips and unobserved AC-02 remain distinct.
- [ ] AC-05: Headless light/dark desktop and narrow captures prove the real criteria component and counts; reader, fold, contract and UI regressions pass.
- [ ] AC-06: Exact-head CI and merged/installed reader acceptance are verified before releasing the 0922 backfill hold.

## Approach
Recognize accept-skip as a non-task event in the strict external-plan reader. Extend the existing offline ledger fold with the published waiver fields and ordering; preserve task behavior. Feed acceptance and waiver data into ThreadIncrementProgress without another store. Keep existing wire state values compatible, carrying optional acceptance/waivers separately. Render mixed and accepted skips without verified icons; unresolved task state takes precedence in the presentation. No markdown checkbox or failed-receipt rewriting.

## Decisions
### Asked
- none
### Defaulted
- D-01 Separate app PR and increment from 1095/#899; same worker and safe checkout, no extra executor.
- D-02 Malformed waiver events grant nothing and never become task events. Strict validation of other ledger events is unchanged.
- D-03 Existing verified receipts stay stored; waiver-bearing ACs cannot acquire a verified presentation solely from overall verify.ok.
### Open
- none

## Tasks

### T-01 Read and present accepted-skip evidence
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/server/src/project/plan/SpecWeavePlanReader.ts, apps/server/src/project/ProjectPlanService.test.ts, apps/server/src/mods/SpecweaveProgress.ts, apps/server/src/mods/SpecweaveProgress.test.ts, apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgress.test.ts, packages/contracts/src/threadIncrementProgress.ts, apps/web/src/components/chat/ThreadPlanCriteria.tsx, apps/web/src/components/chat/ThreadPlanCriteria.test.tsx | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/server && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectPlanService.test.ts src/mods/SpecweaveProgress.test.ts src/project/ThreadIncrementProgress.test.ts

### T-02 Verify source and headless presentation
- AC: AC-05 | Files: apps/web/tests/plan-progress/main.tsx, docs/studio/plan-progress.md, .specweave/increments/1097-display-accepted-skips-in-plan-criteria/reports/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/web && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run --project unit src/components/chat/ThreadPlanCriteria.test.tsx

### T-03 Verify and close 1097
- AC: AC-06 | Files: .specweave/increments/1097-display-accepted-skips-in-plan-criteria/reports/ | Test: Installed reader/version and named synthetic waiver presentation receipt after guarded merge/release; no real backfill before that receipt.


### T-04 Preserve accepted skips on taskless increments
- AC: AC-01, AC-03 | Files: apps/server/src/project/ThreadIncrementProgress.ts, apps/server/src/project/ThreadIncrementProgress.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1095-worker-child-reports/apps/server && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node ../../node_modules/vite-plus/bin/vp test run src/project/ThreadIncrementProgress.test.ts

Verify and close 1097 after exact-head CI and installed acceptance.
