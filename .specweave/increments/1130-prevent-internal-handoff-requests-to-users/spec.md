# 1130 Preserve goal obligations and prevent internal handoff requests to users

## Problem

The 0957 recovery worker delivered its R5 repair proposal, which the receiving owner recorded as evidence-only, then an unrelated mobile Connect acceptance carry-forward started a new worker turn. Earlier, a coordinator instruction made Anton relay an internal handoff receipt; the app promoted that request into a Blocked banner after he had already selected the destination. In the disk lane, increment 1131 completed its source milestone while the original goal still required activation, cleanup and dependency growth prevention. Assignment completion, source completion and goal completion are different outcomes.

Evidence: [initial investigation](reports/investigation.md) and [assignment lifecycle](reports/assignment-lifecycle.md).

## Scope

In: shared no-manual-relay and finite-assignment instructions, optional durable goal evidence carried by existing lifecycle receipts, one common settlement guard, inherited obligations across later reports/new runs/reopen, meaningful command/projection regressions, exact-head review and CI. Coordinator explicitly admitted the file set below on October 28, 2026, after 1095 merged. Use existing lifecycle evidence and 1095 status model; no second attention classifier.

Out: 1106 rendering/timing, 1095 attention classification, 1108 worktree retirement, original external sessions/claims, release/install/restart, path removal, automatic resume or Stop release. HOME-DISK alone removes paths; disk owner retains actual delivery/cleanup. No activation of the global 1069 evidence feature flag. No automatic goal inference from prose or a source increment title.

## Acceptance Criteria

- [ ] AC-01: Shared instructions and ask_user guidance prohibit manual internal receipt relays, retain answered destination decisions, distinguish destination consent from ownership release, and ask only actual user-only decisions/actions with the exact limitation explained.
- [ ] AC-02: A finite worker finishes its accepted assignment without declaring its parent's goal complete or inheriting unrelated release/mobile waits. Required gates retain a named accountable owner. Instructions avoid acknowledgment-only turns, broad carry-forward fanout and repeated unchanged checks; raw history and real user requests remain intact.
- [ ] AC-03: An independently recorded goal has stable identity, scope and required obligation IDs. Missing or incomplete goal evidence cannot be replaced by a narrower source receipt or omitted in a later report. Existing legacy receipts remain decodable and do not acquire fabricated obligations/evidence.
- [ ] AC-04: The common settle path refuses a registered goal with pending, invalid or incomplete activation, cleanup or acceptance evidence, including after source completion/merge, a later run, projection reload or explicit reopen. It permits completion when every registered obligation has valid evidence and the existing pending-work/Stop guards permit it. A distinct worker's accepted scoped result does not modify the parent goal.
- [ ] AC-05: Goal updates use existing independent record_delivery reporting, preserve every registered required obligation and accept valid completion evidence rather than create an indefinite hold. No completion action resumes Stop, starts deletion or changes ownership. A pending goal's owner/reason remains available through the existing lifecycle delivery status even if its latest-turn receipt is superseded.
- [ ] AC-06: Focused command/projection/schema/instruction tests, fresh-context review and exact-head CI pass. Installed acceptance is reported separately and stays open until a containing version is admitted by its existing release owner; this lane never dispatches a release/install/restart.

## Approach

Base: fresh main `d754aec47df8ef4d6be823c3b83a506bc3d7fa80`, containing merged PR #899. Isolated checkout: `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130`, branch `fix/goal-completion-1130`. Installed CLI 3.1.14, verified stable 3.1.15 used session-locally; small-fix declaration recorded as explicitly requested, while this increment remains the task authority.

Extend LifecycleReceiptReport with an optional goal containing stable identity/scope/revision and required obligations using existing wait/evidence types. Preserve it if omitted from a later report; reject changed identity, removed requirements or narrowed meaning. Completion of each requirement needs verified evidence for the goal revision. Preserve a registered goal through reopen even when the turn-bound receipt becomes stale. The one existing dispatchThreadMutation settle path checks goal completion, so automatic, deferred, direct and evidence-based settlement share it. The coordinator additionally admitted four readback-seam files: optional threadDetail goal readback and its contract/integration regressions. This lets a fresh independent reporter read stable IDs and update existing requirements without reconstructing history, through the unchanged access filtering. Use pending command evidence when recording a completed goal so a valid update can release the guard in the same transaction. Existing Stop/pending work guards still apply.

Goal evidence is explicitly registered by an independent reporter, not inferred from a merged PR or text. Legacy threads retain current behavior. This bounded patch cannot discover unrecorded goals; shared instructions make registration part of reporting the overall goal. A worker receipt records that worker's scoped output, never copies the parent's obligations onto every dependency thread.

Reuse lifecycleDeliveryStatus for pending goal owner/reason across superseded run receipts; do not add a classifier or edit presentation files. Surface completion as goal completion only when all registered required evidence passes. Internal unsupported external-session routing remains an operational limitation, never permission to inject input or take over a live writer.

## Decisions

### Asked

- D-01: Anton authorized durable prevention and coordinator admitted the exact files below. No release, install, restart, deletion, stopped-lane wake or overlapping presentation edits.

### Defaulted

- D-02: Optional backwards-compatible registration. Missing legacy evidence stays unknown; no retroactive goal creation or completion claimed.
- D-03: Required obligations cannot disappear by omission or a narrower report. Valid independently recorded evidence discharges them.
- D-04: Existing 1069/1095 seam, no second classifier. Source/assignment completion remains distinct from overall goal completion.

### Open

- None for source implementation. Installed acceptance remains an explicit later gate with the retained release owner.

## Tasks

### T-01 Implement the admitted goal guard and coordination contracts

- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/packages/contracts/src/threadLifecycleEvidence.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/packages/shared/src/threadLifecycleEvidence.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/packages/shared/src/threadLifecycleEvidence.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/orchestration-v2/Orchestrator.goal-completion.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/provider/RuntimeInstructions.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/provider/RuntimeInstructions.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/mcp/toolkits/orchestrator/tools.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/mcp/toolkits/thread/tools.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/packages/contracts/src/orchestratorMcp.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/packages/contracts/src/orchestratorMcp.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/mcp/OrchestratorMcpService.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/threadLifecycleEvidence.test.ts apps/server/src/orchestration-v2/Orchestrator.goal-completion.test.ts apps/server/src/provider/RuntimeInstructions.test.ts

### T-02 Review and deliver exact source

- AC: AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1130-prevent-internal-handoff-requests-to-users/reports/ | Test: relevant lifecycle control and MCP regressions, server production build, fresh-context exact-head review, PR exact-head CI; preserve installed gate

### T-03 Verify and close 1130

- AC: AC-06 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1130-prevent-internal-handoff-requests-to-users/reports/ | Test: installed acceptance through existing release owner when available, specweave verify 1130-prevent-internal-handoff-requests-to-users, fresh-context closure review, specweave complete 1130-prevent-internal-handoff-requests-to-users

Verify and close 1130.

### T-04 Reconcile current main and complete final-head CI
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/orchestration-v2/Orchestrator.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/mcp/OrchestratorMcpService.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/fleet/folderTransfer/apply.test.ts | Test: lifecycle/MCP and folder-transfer journal regressions, relevant server build and final-head applicable CI

October 28: Anton explicitly transferred idle PR961 completion to the worktree-cleanup task. Reconcile current main and diagnose the Windows journal gate without weakening assertions or timeouts. Installed acceptance remains with the release owner. Verify and close1130 after its acceptance gates.

#### T-04 shared baseline repair scope (2026-10-29)

Anton transferred idle PR #961, including its named journal-durability gate. Root assigned the bounded baseline repair after the unchanged 2,000-file Apply/Undo test also exceeded 60 seconds locally. Additional Files: apps/server/src/fleet/folderTransfer/undo.ts, apps/server/src/fleet/folderTransfer/undo.recovery.test.ts. Keep each Undo intent durable before mutation; let completion marks flush with the next intent or final close. Retain every timeout/assertion and verify real crash replay, stash recovery and original-file preservation. Separate implementation commit makes shared provenance reviewable.

Read-only ownership check: retained folder chat mcp:9be8c3bf-32c6-4849-9e99-f1893e0776cd has latest provider turn completed 2026-10-28T18:46:26Z and provider thread idle; its recorded scratch worktree no longer exists. No matching live process was found. This authorizes source/test work only: no live folder copy/Undo, migration-state change or manual acceptance claim. Exact fix requires independent review before merge.

### T-05 Keep storage/handoff regression fixtures portable on Windows
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/worktreesDirectory.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/goal-completion-1130/apps/server/src/handoff/handoffPlacement.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/worktreesDirectory.test.ts apps/server/src/handoff/handoffPlacement.test.ts --maxWorkers=1

October29: root explicitly transferred this bounded fixture repair to attention-usage-codex while fleet-goal-cleanup-codex exclusively implements copyT12. Checkout a9827770 is clean; tests originated in merged PR920, with no open storage/handoff owner found. Windows shard2 passed2113 tests but exposed native-drive resolution of POSIX literals and Git forward-slash output against native backslashes. Exercise explicit POSIX and Windows path adapters; compare native path identity while preserving exact checkout reuse, retained dirty content and no-new-location assertions. No production source or live worktree mutation.
