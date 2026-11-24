# 1032 Finish threads and audit fallback

## Problem
An EasyChamp thread automatically moved from exhausted Claude and Copilot providers to Devin, although the user did not intend to authorize a new paid provider. The previous worker was interrupted with unverified edits. Thread completion labels also conceal unfinished acceptance and nested work.

## Scope
In: recover existing edits; audit actual routing and execution evidence; prevent unapproved automatic selection of registry agents with unknown billing; inventory project threads across explicit bindings; route unfinished authorized work through existing owners.
Out: new spend, credentials, provider enablement, cancelled work revival, duplicate cleanup, merges or release owned by Complete screenshot sessions.

## Acceptance Criteria
- [ ] AC-01: Incident receipt distinguishes configured fallback policy, actual provider/model selection, and execution evidence without claiming backend identity from a label.
- [ ] AC-02: Automatic same-model, any-ready and coordinator fallback cannot select unknown-billing registry agents unless explicitly named in existing configuration; Copilot and explicit selections retain their behavior, covered by focused regression tests.
- [ ] AC-03: Paginated inventory accounts for local threads, nested work and explicit remote bindings, records unknown remote state, and routes actionable unfinished work to its existing owner without duplicating active assignments.

- [ ] AC-04: Disabled providers remain excluded from automatic same-model, named-order, default and coordinator fallback regardless of billing metadata; live no-Devin containment is read back separately from source tests.
- [ ] AC-05: A limit-fallback continuation keeps its way home when another message steers into or replays its run; the idle thread returns to its pre-limit model once that provider has room, covered by a steer/replay regression. Explicit user pins are never moved.
- [ ] AC-06: A coordinator on an unnamed unknown-billing fallback (Devin) does not stay there under wait, ask or switch; a fallback the person named still may. Covered by the 1039 three-policy reproduction as regression tests.
- [ ] AC-07: A limit fallback that serves the same model through the same driver keeps the thread's selected options (effort), on a stopped run and on a pre-switch; other drivers still get their own defaults (1039 medium finding).

## Approach
Reuse the interrupted worker's isolated checkout `/Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing`, branch `fix/fallback-unknown-billing-agents`. Review its two retained edits before extending them. Use public selector tests and a production server build. Keep sanitized incident and sweep receipts in `/Users/antonabyzov/.specwithcode/m4/evidence/completion-sweep-20261023`. Read live state only through supported tools or `specweave-studio db query`.

## Decisions
### Asked
- User requires this continuation on GPT-6 Astra or Claude Code Opus 5.5. Settings 1031 retains Claude Code Ultra Code specifically.
### Defaulted
- Preserve explicit provider configuration; block implicit selection of unknown-billing registry agents. Do not change live provider settings.
- Source fix acceptance and installed release acceptance remain separate; existing release owner controls integration and rollout.
- October 23 follow-up (coordinator and user): the 1032 successor owns the way-back and unknown-billing stay repairs in the retained checkout on a new branch from origin/main; candidate freeze stays on hold; the section 4 pin warning is separate; no automatic repinning.
### Open
- none

## Tasks

### T-01 Recover and repair fallback policy
- AC: AC-01, AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/README.md, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/CHANGELOG.md, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/docs/studio/getting-started.md, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/packages/shared/src/providerFallback.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/packages/shared/src/providerFallback.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/provider/Drivers/AcpRegistryDriver.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/provider/Drivers/AcpRegistryDriver.test.ts, /Users/antonabyzov/.specwithcode/m4/evidence/completion-sweep-20261023/incident | Test: focused providerFallback tests and production server build

### T-02 Reconcile threads and route remaining work
- AC: AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/completion-sweep-20261023/astra-inventory, /Users/antonabyzov/.specwithcode/m4/evidence/completion-sweep-20261023/receipt.md | Test: paginated tool inventory and exact owner continuation readbacks

### T-04 Reconcile explicit provider exclusion and live containment
- AC: AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/packages/shared/src/providerFallback.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/docs/studio/getting-started.md, /Users/antonabyzov/.specwithcode/m4/evidence/completion-sweep-20261023/live-enforcement.md | Test: focused providerFallback tests and supported live provider/readback receipts

### T-05 Repair Copilot identity fixtures exposed by full CI
- AC: AC-02 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.limitReply.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.unopenable.test.ts | Test: both failing suites plus providerFallback and existing worker regressions

### T-06 Keep the way home across a steer or replay
- AC: AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/providerOpenFailure.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.wayBackSteer.test.ts | Test: steer/replay regression plus existing ProviderFallbackWorker suites

### T-07 Refuse staying on an unnamed unknown-billing fallback
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/packages/shared/src/providerFallback.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/packages/shared/src/providerFallback.test.ts | Test: 1039 three-policy cases and providerFallback suite

### T-08 Keep effort on a same-driver fallback
- AC: AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/packages/shared/src/providerFallback.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/fallback-unknown-billing/apps/server/src/orchestration-v2/ProviderFallbackWorker.wayBackSteer.test.ts | Test: worker sweep dispatch keeps effort on a second Claude account

### T-03 Verify and close 1032
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1032-finish-threads-and-audit-fallback | Test: specweave verify 1032, fresh-context review, specweave complete 1032
