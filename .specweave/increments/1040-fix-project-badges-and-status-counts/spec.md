# 1040 Fix project badges and status counts

## Problem

Anton's screenshot shows EasyChamp sidebar 3, Waiting on you 0, summary 3 working and Working group 5. Source at `bc3fabf56778cb4fe90a64e485bc8ada97e2695d` uses different populations: sidebar includes coordinators and nested descendants across project members; pane counts visible workers. Groups roll busy descendants into idle parents but the summary does not. Offline hosts can yield a false all-clear. Failed and limited runs become attention without proof of a user action. The screenshot does not identify the historical three counted threads.

## Scope

In: shared action classification and scoped aggregation; desktop/web sidebar, project attention view, groups, header chips, global overview, coordinator/worker/subagent rollups, remote worker cards and notification eligibility; freshness, filters, pagination, regression tests and headless captures.

Out: notification transport/settings owned by 1036, navigation restoration owned by 1037, iOS implementation owned by the existing iOS lane, held 1011, merge/release/installed acceptance owned by Complete screenshot sessions. iOS consumes this contract and matched logical-project/host snapshots.

## Acceptance Criteria

- [ ] AC-01: A source-backed audit inventories count/status surfaces, populations, identities and freshness, and explains the screenshot without inventing historical live identities.
- [ ] AC-02: Attention counts distinct visible root conversations with current user actions. Coordinator attention is explicitly visible; descendants roll into their root once, with actionable descendant links. Ordinary waits, unread changes, auto-recovering errors and usage resets do not count.
- [ ] AC-03: Sidebar, project attention header and unfiltered attention view agree for the same logical project, host scope and snapshot. Summary and Working group share descendant rollup. Different metrics are explicitly labeled; filtering/paging never silently changes totals.
- [ ] AC-04: Missing, cached, synchronizing, offline or unauthorized members cannot become authoritative zero/all-clear. Known partial counts and stale observations are labeled. Reconnect replaces observations without duplicate counts.
- [ ] AC-05: Answer, dismiss, resolve, resume, retry, archive, delete, supersede and reopen invalidate stale actions. Identity includes environment/project/thread/request or run generation. Cycles, missing ancestors, native/projected child aliases and remote follower aliases never double count.
- [ ] AC-06: User-action notification eligibility shares badge reason/liveness and revalidates before delivery. Completion/unread notification history stays separately labeled. Preserve 1036 ownership.
- [ ] AC-07: Integrated tests reproduce 3 directly active plus 2 descendant-active worker roots as 5 working, with zero user actions and no attention badge. Cover coordinator-only requests, sibling children, sign-in, failure/limit recovery, identical IDs on different hosts, partial load, disconnect, filters and pagination, with desktop/narrow headless captures.
- [ ] AC-08: An app-bound writer delivers a reviewed PR and exact-head checks without bypassing repository registration. Source, merge, release and installed acceptance have separate receipts.

## Approach

Introduce a pure shared attention classifier over normalized observations, then a client-runtime scoped project aggregate. Each decision carries reason, action target, request/run identity, observed revision and freshness. Reuse pending-runtime-request classification, explicit project membership, lineage and shell freshness. Lifecycle, activity and attention stay independent. Consumers render this aggregate instead of counting arrays or interpreting runtime strings independently.

Current coordinator plus visible project workers form conversation roots. Descendants fold into the root; project attention explicitly exposes the coordinator and actionable children. Working counts worker roots with own or descendant active work, while coordinator activity is separately labeled. Reports are legacy evidence, not proof of current user-only action; a current blocker must identify the user's action and expire when progress supersedes it. Held user messages expose Resume/discard, count once, and are never automatically resumed by this work.

Completeness is per member/environment: empty, cached, synchronizing, live. Global bootstrap is insufficient. Unknown-only gets an unavailable indicator; known actions with unknown members get a partial qualifier. Authentication can be an action when the user must act, but unreachable retry is availability. Deduplicate only authoritative identities, never titles or Git remotes.

## Decisions

### Defaulted

- Badge unit: root conversations needing action, not request count, agents, activity or unread messages.
- Scope: explicit linked logical project; selected-machine filtering is labeled and does not redefine global totals or move work.
- Archived/deleted items do not ask for attention. Resolved suppresses old report/failure state; new authoritative unresolved requests reopen attention.
- Failure, usage limit, stall and background work remain operational status unless a current user-only action exists. Operational notifications can remain separately labeled.
- Unknown is never zero. Partial observations carry qualifiers.
- iOS owner implements parity; this lane edits no iOS files.

### Open

- None. Supported app binding verified for mcp:c3913578-5bdd-4b1f-9b42-45f5c93e09e5, native Codex gpt-6-astra, branch fix/1040-project-attention-counts. Notification implementation remains exclusively with 1036.

## Tasks

### T-01 Audit surfaces and specify contract
- AC: AC-01 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040/audit.md, /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040/review.html | Test: validate source inventory, screenshot observations and regression matrix

### T-02 Implement shared attention and scoped rollups
- AC: AC-02, AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/packages/shared/src/projectAttention.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/packages/shared/src/projectAttention.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/packages/client-runtime/src/state/projectAttention.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/packages/client-runtime/src/state/projectAttention.test.ts | Test: vp test run packages/shared/src/projectAttention.test.ts packages/client-runtime/src/state/projectAttention.test.ts

### T-03 Integrate count surfaces and unknown states
- AC: AC-02, AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/components/studio/shell/StudioSidebar.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/components/studio/shell/SidebarProjectList.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/components/studio/shell/ThreadsPane.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/projectWorkspaceModel.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/shellModel.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/overviewModel.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/remoteWorkerCards.ts | Test: vp test run apps/web/src/studio/projectWorkspaceModel.test.ts apps/web/src/studio/shellModel.test.ts apps/web/src/studio/overviewModel.test.ts apps/web/src/studio/remoteWorkerCards.test.ts

### T-04 Share notification eligibility contract with 1036
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040/notification-contract.md | Test: document shared classifier API and lifecycle evidence for 1036; obtain owner integration evidence without editing notification components

### T-05 Verify integrated state transitions and screenshots
- AC: AC-03, AC-04, AC-05, AC-06, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/tests/project-workspace/attention-check.mjs, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/tests/project-workspace/attention-fixture.tsx, /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040 | Test: integrated headless fixture and web build/typecheck; headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never, HTML open never; save desktop and narrow captures

### T-06 Verify and close 1040
- AC: AC-08 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1040-fix-project-badges-and-status-counts/ledger.jsonl, /Users/antonabyzov/.specwithcode/m4/evidence/project-attention-1040/review.md | Test: specweave verify 1040; fresh-context review; exact-head PR checks; specweave complete 1040

Implementation paths identify the approved source for planning, not permission to edit the shared checkout. Replace them with the app-managed worktree paths before claiming implementation tasks.

### T-07 Package exports and observation adapter
- AC: AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/packages/shared/package.json, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/packages/client-runtime/package.json, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/useProjectAttention.ts | Test: focused aggregate tests and web production build

### T-08 Update behavioral contracts and integrated fixture wiring
- AC: AC-03, AC-04, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/projectWorkspaceModel.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/shellModel.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/overviewModel.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/remoteWorkerCards.test.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/tests/project-workspace/serve.mjs, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/tests/project-workspace/mocks.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/tests/project-workspace/fixture.tsx | Test: focused surface tests and integrated headless fixture

### T-09 Preserve global overview availability and metric labels
- AC: AC-03, AC-04 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/components/studio/StudioOverview.tsx | Test: web typecheck/build and focused overview tests

### T-10 Reconcile remote follower coverage
- AC: AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/studio/fleet.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1040-project-attention-counts/apps/web/src/components/studio/RemoteWorkerCards.tsx | Test: aggregate alias/unknown tests, web typecheck and headless partial scenario
