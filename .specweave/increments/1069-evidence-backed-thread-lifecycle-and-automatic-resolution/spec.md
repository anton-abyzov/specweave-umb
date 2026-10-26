# 1069 Evidence-backed thread lifecycle and automatic resolution

## Problem
Runtime Idle says no turn is executing; it does not say whether the requested job is finished. Owners report long-lived unresolved work across EasyChamp and SpecWeave. Native child rows and ancestor-derived classifications inflate the apparent root backlog. Current source automatically resolves only from observed merged PR readiness and eligible thread state; it does not establish delivery acceptance for non-code work or deployment obligations.

## Scope
In: owner-provided complete inventories and freshness (consumed only; individual adjudication and recovery remain exclusively with the completion-sweep owner), runtime/config audit, durable evidence-backed lifecycle reasons, automatic resolution and reopening, truthful status presentation, focused regression and headless evidence.
Out: underlying task recovery, bulk resolution, archives, Stop release, auth changes, notification/iOS implementation, release-owner takeover. Preserve the 1011 hold. Existing completion owner merges reviewed source and release owner deploys; installed evidence is a separate gate.

## Acceptance Criteria
- [ ] AC-01: Audit distinguishes visible roots from native children, lists complete local pagination and explicit unknown federation coverage for both projects, and records installed version and effective configuration with freshness.
- [ ] AC-02: Automatic code completion requires current-scope evidence of Git push, PR merge, deployment and verification, with no outstanding required action. Research/no-code completion requires the actual answer/artifact delivered and verified against requested scope, with code gates explicitly N/A and a rationale. Terminal turns, age, CI, merged PRs, checkboxes or a claim of done alone never prove delivery.
- [ ] AC-03: Pending requests, outstanding agent work, external waits, user-only decisions, nested activity, Stop/auth holds and unknown remote state have distinct auditable reasons; agent-settleable waits are not user blockers.
- [ ] AC-04: Resolution preserves history and Stop; newer requests or reopened obligations invalidate old acceptance atomically and reopen work without racing pending/nested work.
- [ ] AC-05: Reload/restart and filtered/paginated views preserve lifecycle classification and explicit missing or disconnected evidence.
- [ ] AC-06: Focused tests and wide/narrow headless screenshots demonstrate completion/reopening and every protected state; exact-head review and CI are recorded separately from installed acceptance.

- [ ] AC-07: The supplied 1006 ENOSPC final-message/status mismatch displays an owned operational wait, never generic Idle or user-blocked; historical 162 MiB is not treated as current disk evidence. Remaining HTTP500 project_mutation_failed, compatibility and installed acceptance stay unresolved.
- [ ] AC-08: Structured reasons persist through reload/restart, supersede stale reasons only on verified recovery, and agree across grouping/filter/pagination. Operational recovery never auto-resumes explicit Stop. Auth/provider/limit failures, pending release/review fixes, active descendants and unknown remote state are covered.
- [ ] AC-09: Missing evidence, partial delivery, stale evidence and newly reopened acceptance cannot resolve work across transitions or restart. User-blocked requires Anton's output; deployment, dependency and resource waits carry reasons and owners.

## Approach
First reconcile owner inventories and inspect current lifecycle contracts, projection candidates, settlement service, orchestrator guards and presentation. Define the smallest durable evidence contract before implementation; do not derive acceptance from final-text heuristics. Extend existing commands/events and settlement locking rather than a second sweeper. Keep runtime status separate from delivery disposition. Use isolated synthetic state for tests. Coordinate shared presentation files before edits and retain existing owner boundaries.

## Decisions
### Asked
- D-10: 1070 ships its dependency seam behind a server-side default-off flag after exact-head SHIP and green CI. Only 1069/#708 may activate it with integrated acceptance checks; unrelated releases remain unblocked.
- D-08: 1070 owns concurrent changes to ProjectionStore.ts, Orchestrator.ts, DeferredThreadResolution.ts and thread MCP handlers/tools. Sequence 1069 shared persistence changes after its merge; coordinate receipt contracts before editing overlapping files.
- D-09: Increment collision resolved by the completion owner via CLI: this increment remains 1069; subscription recovery is 1071.
- D-05: Completion evidence follows `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1040-fix-project-badges-and-status-counts/completion-evidence-contract.md`. Code gates are push, merge, deployment and requested-scope verification; no-code gates require delivered verified answer/artifact with explicit code-gate N/A rationale.
- D-06: Completion-sweep owner exclusively adjudicates every individual idle thread and performs recovery/resolution. This lane consumes those receipts and implements product correctness.
- D-07: Disk/network/tool availability are operational waits with owners; only Anton-dependent output is user-blocked. Verified recovery supersedes stale reasons without releasing Stop.
- D-01: Same-writer branch switch in existing worktree approved; untracked generated cache remains untouched and excluded from commits.
### Defaulted
- D-02: Missing acceptance is unknown, not proof of unfinished work or permission to resolve.
- D-03: Answer-only requests may complete when their actual requested outcome is satisfied; no artifact requirement is invented.
- D-04: Owner inventory reason labels are triage until their per-root evidence is reconciled.
### Open
- None. Dependency #706 merged as 62dde36aaf7b9e0329f979e4c6ba1935599e7571; shared integration is released to this lane. Independent policy contract uses current request ID, run ID and acceptance revision, owner-attributed reasons, timestamped evidence references and explicit code/no-code gate applicability. Legacy missing evidence fails closed. Owner adjudication is the evidence producer; provider final text is never acceptance.

## Tasks

### T-01 Audit current lifecycle and owner inventories
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040/idle-lifecycle-audit.md | Test: owner receipt reconciliation with source paths, installed/config readbacks and completeness accounting

### T-02 Define and implement evidence-backed lifecycle contract
- AC: AC-02, AC-03, AC-04, AC-07, AC-08, AC-09 | Files: packages/contracts/src/threadLifecycleEvidence.ts, packages/contracts/src/threadLifecycleEvidence.test.ts, packages/shared/src/threadLifecycleEvidence.ts, packages/shared/src/threadLifecycleEvidence.test.ts, packages/contracts/src/orchestrationV2.ts, apps/server/src/orchestration-v2/ThreadSettlementService.ts, apps/server/src/orchestration-v2/ThreadResolutionPolicy.ts, apps/server/src/orchestration-v2/ThreadAutomaticResolutionGuard.ts, apps/server/src/orchestration-v2/ProjectionStore.ts | Test: focused lifecycle public-command and settlement tests; finalize exact command/event files after audit before claim

### T-03 Present lifecycle reasons and verify persistence
- AC: AC-03, AC-05, AC-07, AC-08 | Files: finalize owned presentation and projection test paths after T-01 before claim | Test: focused lifecycle presentation tests plus reload/restart and pagination fixtures

### T-05 Integrate the existing settlement command seam
- AC: AC-02, AC-04, AC-09 | Files: apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/ThreadLifecycleAcceptance.ts, apps/server/src/orchestration-v2/ThreadLifecycleAcceptance.test.ts, apps/server/src/orchestration-v2/Orchestrator.control-reads.test.ts, packages/shared/package.json | Test: exact-run accepted/missing/stale/partial/reopened evidence at deferred finish and automatic settlement, persisted projection roundtrip and recovery

### T-06 Preserve automatic settlement and watch behavior under missing evidence
- AC: AC-02, AC-09 | Files: apps/server/src/orchestration-v2/runtimeLayer.test.ts | Test: existing runtime lifecycle and PR watch integration tests assert automatic refusal without acceptance while explicit settlement remains available

### T-04 Verify and close 1069
- AC: AC-06, AC-07, AC-08, AC-09 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040/idle-lifecycle-verification.md | Test: exact supplied final-message/status mismatch; structured persistence across reload/restart; verified recovery and stale-reason supersession; grouping/filter/pagination agreement; preserved unfinished acceptance; missing/partial/stale/reopened evidence transitions; focused regressions, production builds, headless wide/narrow captures, exact-head CI, specweave verify 1069, fresh-context review, specweave complete 1069; retain installed gate if acceptance is unavailable
