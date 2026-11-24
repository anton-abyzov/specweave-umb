# Coordinator context continuity across model switches

## Problem
The supplied screenshot shows the ol project coordinator on m3 using Muse Wonder 1.0 claiming a launched workflow exists inside the coordinator, without a worker link, and asking for context the user expects it to retain. The earlier provider/model and actual switch sequence are not yet verified.

## Scope
In: trace provider/model handoff and retained history, inspect ownership discovery and worker references, reproduce demonstrated gaps, implement regression fixes, independent review and delivery verification, coordinate deployment with the release owner. Out: unrelated provider changes, recreating retired checkouts, forced updates on busy machines.

## Acceptance Criteria
- [ ] AC-01: Document intended and actual handoff behavior with code and incident evidence; distinguish verified causes from uncertainty.
- [ ] AC-02: Regression tests demonstrate that model/provider switches preserve or make recoverable coordinator history and worker identity for the proven failure paths.
- [ ] AC-03: Fixes pass required checks and independent review at the shipped revision.
- [ ] AC-04: Release owner deploys the reviewed fix; independent verifier records installed version and current-scope delivery.

## Approach
Inspect the attachment, project knowledge, live ownership and approved app checkout. Trace coordinator session selection, provider handoff construction, history retrieval and worker inventory. Compare bounded transcript replay, structured coordinator handoff and on-demand history retrieval before selecting the smallest supported fix. Add focused regression tests, run required checks through the isolated checks runner, review and deploy through existing release coordination.

## Decisions
### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Treat prior-provider wording as uncertain; inspect recorded runs.
- D-02: Preserve bounded context with explicit recovery paths rather than unbounded transcript injection.
- D-03: Preserve existing checkout ownership and release dispatcher.
### Open
- none

## Tasks
### T-01 Research incident and compare fixes
- AC: AC-01 | Files: app handoff/session/history modules (locate during investigation), investigation report | Test: evidence-backed incident and code-path review
### T-02 Fix demonstrated continuity gaps
- AC: AC-02 | Files: identified app modules and focused regression tests | Test: focused regression suite for reproduced paths
### T-03 Review and validate
- AC: AC-03 | Files: review evidence | Test: required isolated checks and independent exact-head review
### T-04 Deploy and verify delivery
- AC: AC-04 | Files: delivery evidence | Test: release CI, installed-version readback and independent scope verification

## Investigation dependencies and next step

- November 17, 2026: original m3/ol history unavailable; release-owner send failed exactly: "m4 is unavailable right now." This limits incident attribution and release dispatch, not source investigation.
- Read-only verification source: /srv/specwithcode/minisforum/verify/specwithcode at 913843375e6cd690b7f3e3c3f3f0b7106894d85f. It contains an unrelated modified ProjectWorkspaceSettings test; leave untouched.
- Compared current upstream source at cb61c42bf4032f504cb4bb119fb61d5f3b0ad7cf using individual GitHub file reads. Pure-function reproduction proves thread_created/subagent/dynamic_tool identities disappear while an assistant launch claim survives and omittedItems remains zero; running children are excluded from pendingChildResults. No attribution to the original incident yet.
- Evidence: /srv/specwithcode/minisforum/evidence/1354-context-continuity/reproduction.json and /srv/specwithcode/minisforum/evidence/1354-context-continuity/reproduce.cjs.
- Next implementation dependency: coordinator to assign an approved local app checkout. Existing clean candidate /srv/specwithcode/minisforum/worktrees/env-worktree-setting belongs historically to Environment tab worktrees banner; do not repurpose without ownership handback. The canonical app checkout is absent. No new clone or shell worktree has been created.
- After checkout assignment: preserve compact worker lifecycle identities and answered questions in bounded handoff, align production history SQL with projection, add tests for provider switch and recovery pointers, then independent review, release-owner deployment, and independent delivery verification. All remain pending.

## Implementation checkpoint

- November 17, 2026: previous owner explicitly released /srv/specwithcode/minisforum/worktrees/env-worktree-setting. Reused in place, branch fix/1354-coordinator-context; no clone/worktree created.
- PR https://github.com/anton-abyzov/specwithcode/pull/521, head a82734d5cac876f00a009f0798ccc5fe36ef8523. Changes: ContextHandoffBudget.ts, ProjectionStore.ts and focused tests under apps/server/src/orchestration-v2 in that checkout. Compact worker facts, tool receipt pointers, prior question text, worker-prioritized bounded selection and qualified coverage counts. No inventory expansion.
- 100 focused tests passed, including production SQLite and provider-switch suites. Server build passed. Evidence /srv/specwithcode/minisforum/evidence/1354-context-continuity/focused-tests.log and /srv/specwithcode/minisforum/evidence/1354-context-continuity/server-build.log.
- checks copy refused with exit 2 due to existing apps/web/src/components/studio/ProjectWorkspaceSettings.test.tsx modification in the shared verification copy. It was left untouched. Full local typecheck has not run. Required CI and independent review remain pending, then release dispatch and independent installed delivery verification. Original incident attribution is still unverified.
- Independent review dispatch refused: no cross-family reviewer can run locally (Claude usage full; Devin Claude billing unknown). Nothing was started; no same-family substitute requested. PR watcher also returned "Could not change whether the pull request is watched." Coordinator must arrange reviewer availability and supported CI watch; do not merge without review/readiness gates.

## Monitoring diagnosis

- Watch failure reproduced with explicit repository/number/threadId. Source mismatch: apps/server/src/mcp/toolkits/pullRequests/handlers.ts permits coordinator-owned workers, but apps/server/src/orchestration-v2/Orchestrator.ts rejects all relationshipToParent=subagent threads in thread.pull-request.watch. No watcher code change folded into this scope.
- checks copy exit 2 is the intentional dirty guard in apps/server/src/cli/verificationCopy.ts. Existing diff is a formatting-only line wrap in ProjectWorkspaceSettings.test.tsx. It remains unchanged. No alternate per-thread checks clone or bypass created. Full CI typecheck/server checks are running, preserving validation without altering that edit.
- Supported scheduler fallback will wake this worker on CI failure or completion and disable itself after its first delivery. Review routing remains coordinator-owned; no duplicate review dispatched.
- CI on a82734d5 found TS2322 in the new fixture: ProviderDriverKind requires a branded value. Fixed via ProviderDriverKind.make("codex") in commit 095bab6a; production SQLite and memory tests pass again. Existing reviewer must review the new head. Diagnostic artifacts: /srv/specwithcode/minisforum/evidence/1354-context-continuity/typecheck-a82734d5/apps__server.log.
- Release route confirmed: scripts/release/request-release.sh --by can run locally from any machine and joins the single GitHub Release macOS queue. Use after review/CI/merge; no need to alter fleet grants or force updates. Installed outcome verification still required.
- Independent review at 095bab6a: fix first, two high selection-budget regressions and one low coverage gap. Fixes preserve conversation anchors; worker metadata enables deduplication and an eight-reference cap, tool refs follow prose. Interrupted tool-only recovery integration test verifies checkpoint preface and no duplicate history. Response /srv/specwithcode/minisforum/evidence/1354-context-continuity/review-response.md. Coordinator will dispatch fresh review; no prior reviewer restarted.

- Round 2 fix pushed as `6382a0967f6216be6869aeac32cc4c1f20b8efed`: priority-only eight-worker cap, spare-budget worker selection before tools, explicit omitted worker count and recovery route carried through delivery. 107 focused tests pass across final runs; server build passes. Response: `/srv/work/github/specweave-umb/.specweave/increments/1354-coordinator-context-continuity-across-model-switches/reports/round2-response.md`. Next: coordinator fresh independent review, required CI, verification-copy owner handback, then authorized release and installed behavior verification. No merge/deploy yet.

Verification-copy ownership resolved: the prior owner confirmed the formatting edit was byte-identical to pushed/merged PR 467 commit `a2096285`, saved it as `/srv/specwithcode/minisforum/worktrees/pr467-verify-copy-fmt-backup.patch`, and restored it himself. This worker did not remove the edit. Supported checks copy succeeded and the clean verification copy now holds `23657666cdd2c3dcf37722784e08fd36e847edfb`; server typecheck is running through the heavy-check gate.

Server typecheck gate completed with exit 0 at `23657666cdd2c3dcf37722784e08fd36e847edfb`, through supported checks copy/run. Evidence: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/typecheck-23657666.log`. Required remote CI and independent review remain pending before merge, release and installed verification.

- Round 3 independent Claude Opus 5.5 verdict SHIP at `23657666cdd2c3dcf37722784e08fd36e847edfb` recorded with `npx --yes specweave@3.1.24 review 1354 --record ... --model claude-opus-5-5 --family claude --head 23657666cdd2c3dcf37722784e08fd36e847edfb`; `satisfiesPolicy: true`. Record: `/srv/work/github/specweave-umb/.specweave/increments/1354-coordinator-context-continuity-across-model-switches/reports/reviews/review-claude-opus-5-5-3.md`. Nonblocking lows retained: omission count can overstate across multiple handoffs; older prose can precede workers beyond priority eight. Base query-plan provenance run passes at `cb61c42bf4032f504cb4bb119fb61d5f3b0ad7cf`; head comparison running in the same supported copy/toolchain. Required CI remains pending; do not infer the reviewer failure is preexisting. Deployment and independent delivery verification still pending.

Query-plan provenance comparison completed: `ProjectionStore.slowQueries.test.ts` passes on both base `cb61c42bf4032f504cb4bb119fb61d5f3b0ad7cf` and reviewed head `23657666cdd2c3dcf37722784e08fd36e847edfb`, using the same supported verification copy, Node 22.20.0, checks copy/run and focused command. Evidence: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/base-query-plan.log` and `/srv/specwithcode/minisforum/evidence/1354-context-continuity/head-query-plan.log`. The reviewer failure is not reproduced in the supported production toolchain; its exact environmental cause remains unverified. No claim that it fails on base. Required CI still gates merge.

CI server 1/3 failed at reviewed head on a timing assertion, not the missing-index assertion: `AssertionError: expected 54.75375800000256 to be below 50`. Log: `/srv/specwithcode/minisforum/evidence/1354-context-continuity/ci-server1-23657666.log`. With focused base/head comparisons both passing under Node 22, requested one unchanged-head retry via `gh run rerun 44033331395 --job 133870426584`. No threshold change or gate bypass. Required CI still pending; repeated failure requires further diagnosis.

- PR 521 merged as `bed940f7e58fa16db6ed86cd85d03418dabef759` after reviewed-head CI passed. Documented single release queue requested run `44036253156`. Receipt and pending installed/independent delivery obligations: `/srv/work/github/specweave-umb/.specweave/increments/1354-coordinator-context-continuity-across-model-switches/reports/release-progress.md`.
