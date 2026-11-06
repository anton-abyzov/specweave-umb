# 1235 Recent review phase3 Team Rules repairs

## Problem
Campaign review proved delayed automatic approvals bypass newly tightened folder/machine rules, companion export silently drops Claude launch pins, and failed records export leaves its reader open. Findings and deterministic baseline receipts are in ~/.specwithcode/m4/evidence/recent-features-review-20261103/team-rules-followup.md.

## Scope
In: isolated stacked repair candidate based on PR1237 head450a6346bd4c2301b1753b1f6dbed94e54aa40f1, regression tests, local validation and draft PR targeting feat/team-rules-phase-3. Out: merging into the owner's branch/main, releasing/installing, changing live policies/accounts/DB, completing increment1186, duplicating main retry PR1336.

## Acceptance Criteria
- [ ] AC-01: A delayed automatic accept stops when current thread mode, live pending prompt or applicable machine/folder rules no longer permit it; ordinary retries remain valid.
- [ ] AC-02: Export explicitly reports unsupported Claude binary/argument pins while preserving supported environment mapping.
- [ ] AC-03: Export closes its reader if output creation or writing fails, preserving exclusive private output semantics.
- [ ] AC-04: The frozen candidate has owning tests, server build/typecheck evidence, fresh independent review and a draft stacked PR; owner review/manual acceptance are explicitly separate.

## Approach
Use authorized dedicated worktree /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/review-team-rules-phase3 on codex/review-team-rules-phase3. Repo-prefixed Files below identify canonical ownership; all product edits execute in this isolated checkout only. Keep1186 owner claude@antons-macbook-m4max/session34bfb7a1-5b3e-4acb-90df-017381a92f4c intact. Add fresh checks at every automatic attempt, extend unsupported pin notice, and close lazy reader in outer finally. Regression fixtures use synthetic in-memory policies and throwaway DBs only. User authorized candidate preparation; do not claim implementation ownership of the underlying1186 feature. Main retry PR1336 is independently owned by product lead; reconcile overlap at owner integration.

## Decisions
### Defaulted
- Draft stacked PR preserves the owner's acceptance/merge decision. No authorization to alter live policies or perform manual auth acceptance.
- Managed worktree API rejected nested repository sourceRoot; use explicitly approved Git worktree under configured root, normal pnpm install, no shared node_modules symlink.
### Open
- none for candidate preparation.

## Tasks

### T-01 Repair the three verified findings with owning regressions
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/FullAccessApprovals.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/FullAccessApprovals.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/teamRules/companion.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/teamRules/companion.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/teamRules/TeamRulesRecords.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/teamRules/TeamRulesRecords.test.ts | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/specwithcode-dev/review-team-rules-phase3 && /Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node node_modules/vite-plus/bin/vp test run apps/server/src/orchestration-v2/FullAccessApprovals.test.ts apps/server/src/teamRules/companion.test.ts apps/server/src/teamRules/TeamRulesRecords.test.ts

### T-02 Verify and close1235 candidate preparation
- AC: AC-04 | Files: .specweave/increments/1235-recent-review-phase3-team-rules-repairs/reports/candidate.md | Test: python3 /Users/antonabyzov/.specwithcode/m4/evidence/recent-features-review-20261103/team-rules-followup-probe/verify-candidate.py
