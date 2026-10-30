# 1106 Investigate concise mode noise

## Problem
October 27, 2026 screenshots show Concise in coordinator and worker headers while commands, narration, worker previews and empty assistant chrome consume the conversation. The label describes project reply style independently of timeline detail. Determine intended semantics before fixing verified causes.

## Scope
In: reply style versus display semantics; persistence and provider/fallback audit; grouping; worker previews; empty assistant rendering; focused regressions and headless proof. Out: provider accounts, paid turns, publishing, restarts, reviving the cancelled thread, taking over 1011 acceptance.

## Acceptance Criteria
- [ ] AC-01: A source-backed report distinguishes reply style and display detail, records persistence/provider/fallback behavior and reproduces screenshot causes with real components.
- [ ] AC-02: Worker and coordinator controls disclose effective display level and reply style without implying Concise replies hide activity.
- [ ] AC-03: Results-only display suppresses routine narration, successful command rows and routine worker preview text while preserving full activity, meaningful failures, approvals, questions and results.
- [ ] AC-04: Empty settled assistant output creates no blank bodies, copy controls or attribution-only sections; attachments and errors remain accessible.
- [ ] AC-05: Focused regressions, headless light/dark captures, production web build and fresh review validate changes with installed acceptance reported separately.

- [ ] AC-06: Headless real-timeline reproduction checks streamed and steered messages, width/zoom changes, disclosure changes and hidden-to-visible transitions for non-overlapping mounted rows after layout settles.
- [ ] AC-07: After those transitions, wheel/keyboard scroll, pointer hit targets and text input remain usable; only deliberate reader upward input pauses live follow, with no restart or native interaction.
- [ ] AC-08: Installed version/source comparison and ownership checks distinguish the original screenshot cause from local 1106 changes, and the final report states proven causes versus unproven limits.

## Approach
Audit TimelineDetailMenu, timelineDetail, responseStyle, MessagesTimeline logic/rendering, runtime policy/settings and adapters. Read 1011/1068 history and coordinate with active 1011 owner before overlapping edits. Work in `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/fix-1106-concise-noise` on `fix/1106-concise-noise`, based on app origin/main `6aab213a6fb801e39a6f3df608ccc9cf503e22dd`. Add failing focused cases before repairs. Real-component synthetic fixtures use no live store/provider sessions. Record independent review and distinguish fixture from installed proof.

## Decisions
### Asked
- Anton directly accepted the reviewed PR959 UI at exact `5152e55ac9df121d731ad7cf9fd0a06a1cd9aad6`.
- Anton explicitly answered "Allow this one-time exception" for PR959 whole-file coverage: 30.76% lines against the unchanged 60% threshold. Retain the failed full-scope evidence; no configuration, scope or test weakening. Additional evidence is 93.5% changed-line coverage and 100% new timing integration coverage. This exception applies only to this reviewed candidate; CI, release and installed verification remain separate. Evidence: `~/.specwithcode/m4/evidence/worktree-audit-20261028-late/concise/manual-ui-acceptance-record.json`.
### Defaulted
- Preserve independent project reply style and client display settings; disclose both rather than silently change saved preferences.
- Keep meaningful errors, approvals, questions and full activity accessible. Routine worker preview text can collapse in Results only.
- Cancelled concise thread is history only; 1011 retains installed acceptance ownership.
### Open
- None. Record exact repairs after reproductions.

## Tasks
### T-01 Audit semantics and reproduce screenshot noise
- AC: AC-01 | Files: reports/investigation.md | Test: node ../../node_modules/vite-plus/bin/vp test run src/components/chat/MessagesTimeline.logic.test.ts src/components/studio/RelayedMessage.test.tsx src/components/chat/TimelineDetailMenu.test.tsx (from app worktree apps/web; initial failures retained in reports/investigation.md)

### T-02 Clarify controls and fix verified timeline noise
- AC: AC-02, AC-03, AC-04 | Files: apps/web/src/components/chat/TimelineDetailMenu.tsx, apps/web/src/components/chat/TimelineDetailMenu.test.tsx, apps/web/src/components/chat/MessagesTimeline.logic.ts, apps/web/src/components/chat/MessagesTimeline.logic.test.ts, apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/chat/MessagesTimeline.test.tsx, apps/web/src/components/studio/RelayedMessage.tsx, apps/web/src/components/studio/RelayedMessage.test.tsx | Test: node ../../node_modules/vite-plus/bin/vp test run src/components/chat/TimelineDetailMenu.test.tsx src/components/chat/MessagesTimeline.logic.test.ts src/components/studio/RelayedMessage.test.tsx src/components/chat/MessagesTimeline.test.tsx src/timelineDetail.test.ts (from app worktree apps/web)

### T-03 Document reply and display behavior
- AC: AC-01, AC-02 | Files: docs/studio/operator-guide.md | Test: git diff --check; fresh review matches documentation to source and regressions

### T-04 Verify and close 1106
- AC: AC-05 | Files: apps/web/tests/activity-diffs/, reports/validation.md, reports/review.md | Test: node node_modules/vite-plus/bin/vp build --config apps/web/tests/activity-diffs/vite.config.ts; native headless preview fixture; node ../../node_modules/vite-plus/bin/vp build (from apps/web); specweave verify 1106 with explicit scoped commands


## Overlap follow-up, October 27, 2026

User reports overlapping long steer, assistant and tool rows plus temporarily blocked scrolling/input, recovering after slight movement. Installed app and CLI currently report 1.0.105. Local d5c1283c07 has not been installed. Check measured row geometry and hit targets, rather than treating this as cosmetic. Prior scroll thread is completed and read as history only; 1011 owner now completed, steer-only coordination was rejected without starting a turn. Preserve all existing runs/drafts and worktrees. Continue in the same isolated app worktree.

### T-05 Reproduce overlap and blocked interaction
- AC: AC-06, AC-07, AC-08 | Files: apps/web/tests/activity-diffs/main.tsx, apps/web/tests/activity-diffs/mocks.tsx, apps/web/tests/activity-diffs/vite.config.ts, reports/overlap-investigation.md | Test: synthetic real timeline under streamed/steered content, pane/zoom/reveal/disclosure transitions; record DOM geometry, scroll and hit-test evidence in native headless preview

### T-06 Fix verified row layout or interaction invalidation
- AC: AC-06, AC-07 | Files: apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/chat/MessagesTimeline.test.tsx, apps/web/src/components/chat/timelineLayout.ts, apps/web/src/components/chat/timelineLayout.test.ts | Test: focused regression suites and headless reproduction before/after; preserve readerScroll policy

### T-08 Keep measured web rows and positions in the same layout transaction
- AC: AC-06, AC-07 | Files: patches/@legendapp__list@3.3.5.patch, pnpm-lock.yaml, pnpm-workspace.yaml, scripts/legend-list-row-layout.test.ts | Test: actual patched web bundle regressions; real headless row geometry and interaction matrix on first paint and settled frames; existing timeline scroll anchoring regressions

### T-09 Retain the headless overlap and interaction prevention check
- AC: AC-06, AC-07 | Files: apps/web/tests/activity-diffs/overlap-check.mjs, docs/studio/operator-guide.md | Test: retained wrapper syntax check; execute the same in-page matrix through native headless preview with file-backed screenshots/action trace; wrapper keeps nonzero failure exit and Playwright trace capture for CI; documentation matches synchronous web measurement behavior

### T-07 Verify and close 1106
- AC: AC-08 | Files: reports/overlap-validation.md, reports/overlap-review.md | Test: focused production web build, geometry and interaction matrix, fresh-context review, specweave verify 1106 and complete

Verified follow-up direction: the existing web virtualizer delays position recalculation until another animation frame while its MVCP anchor lock is active. Pane narrowing plus live text changes reproduces updated measured heights with stale downstream positions in the first frame. Test the dependency's own web path rather than introducing a second app-level size cache. Native variants stay unchanged. T-06 is unnecessary if the library repair resolves the reproduction. Longer interaction blocking remains unproven and must be tested/reported separately.

Scaling refinement: keep fractional layout border-box units consistent across synchronous reads and ResizeObserver. The final source acceptance uses native headless preview; standalone Playwright wrapper execution and native Electron zoom are explicitly unverified.


## Internal receipt follow-up, October 28, 2026

Installed app 1.0.109 still uses old relay/default and coordinator empty-turn rendering. Prior local 1106 commits were never pushed or installed. Current screenshot contains three internal worker receipts followed by empty coordinator acknowledgements. Preserve reply-style and detail settings independently; make non-verbose internal receipts compact in both shared relay consumers, retaining candidate questions/decisions/actionable failures inline and the entire original behind disclosure/Find/copy. Do not change the user's mode. This is presentation only; 1130 stays proposal-only and 1095 retains attention/blocker classification. Both owners are completed, and steer-only 1130 coordination returned thread_not_sendable without resuming it. No release dispatch, external session mutation or Stop release.

- [ ] AC-09: The screenshot receipt sequence folds without hash/log/path previews or metadata-only blank chrome in coordinator and worker views under non-verbose detail. Verbose and disclosure/Find retain complete original text/activity.
- [ ] AC-10: User prompts, candidate questions/decisions, actionable failures, attachments, thread cards and active output remain accessible; no classification or lifecycle changes overlap 1130/1095.
- [ ] AC-11: Current source/installed/owner inventory, red-green regressions, real-component headless evidence, exact-head fresh review, CI and PR delivery are recorded separately from installation.

### T-10 Compact shared internal receipt presentation
- AC: AC-09, AC-10 | Files: apps/web/src/components/studio/RelayedMessage.tsx, apps/web/src/components/studio/RelayedMessage.test.tsx, apps/web/src/studio/workerMessagePresentation.ts, apps/web/src/studio/workerMessagePresentation.test.ts | Test: focused relay and presentation tests for the screenshot sequence, both source directions, disclosure, Find and candidate attention

### T-11 Remove metadata-only coordinator chrome through a shared content predicate
- AC: AC-09, AC-10 | Files: apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/ProjectWorkspace.test.tsx, apps/web/src/components/chat/MessagesTimeline.logic.ts, apps/web/src/components/chat/MessagesTimeline.logic.test.ts, apps/web/src/studio/messagePresentation.ts, apps/web/src/studio/messagePresentation.test.ts | Test: coordinator and worker empty-turn parity, preserve activity access, attachments, cards and active messages

### T-12 Reproduce and deliver current receipt sequence
- AC: AC-11 | Files: apps/web/tests/activity-diffs/, apps/web/tests/project-workspace/, apps/web/tests/agent-messages/internalReceipts.ts, apps/web/tests/agent-messages/internal-receipts-check.mjs, docs/studio/operator-guide.md, reports/internal-receipts-investigation.md, reports/internal-receipts-validation.md | Test: headless native preview real components in both views at 390/1280 light/dark, focused production build; push own branch and open PR; CI checks

### T-13 Verify and close 1106
- AC: AC-11 | Files: reports/internal-receipts-review.md | Test: current scoped verify, fresh-context exact-head review, complete; installed acceptance remains explicit proof limit


## Explicit timing and 0957 follow-up, October 28, 2026

The header chip receives only shell.latestRun.startedAt/completedAt. It shows the newest presented run's wall-clock span, floored to minutes, or current UTC minute minus start while unfinished. It is not cumulative active work; waits inside a turn count, gaps between completed turns do not. No current active timing/header owner was found in the project title/catalog and file history; old machine-header and timer fixes are merged. 1130 is now running on finite assignment versus durable goal/lifecycle. Steer-only scope coordination delivered; 1106 will not resolve workers or change attention classification.

Defaulted presentation: compact current status or explicit Last turn elapsed. A keyboard/touch-accessible timing disclosure explains start-to-finish wall-clock meaning and recorded-turn cumulative elapsed from available valid spans only. Gaps/background watches outside turns are excluded, overlap is counted once, and waits inside a span are explicitly included. Loaded/partial history and unknown timing are disclosed; no active-work estimate, provider-session age or invented lifetime total. Reuse current activity-run selector and existing run-health/background-work signals, with no telemetry/schema/DB changes. The same component/helper applies to coordinator and worker thread pages; compact coordinator Overview keeps its existing status surface.

- [ ] AC-12: The header distinguishes latest/current turn elapsed from cumulative recorded elapsed, updates for follow-ups/steers/resume, and never silently labels idle/watch duration active work.
- [ ] AC-13: Recorded totals use available valid unique spans, exclude between-turn gaps and unstarted/invalid/unknown ends, handle overlaps/partial history, and preserve current queued/waiting/stopped status without extrapolating settled turns.
- [ ] AC-14: The 0957 mobile Connect carry-forward and repetitive no-action receipts fold in non-verbose relay presentation while legitimate user results/questions remain visible; lifecycle ownership remains with 1130.

### T-14 Clarify latest and recorded timing
- AC: AC-12, AC-13 | Files: apps/web/src/components/chat/ThreadMetaRow.tsx, apps/web/src/components/chat/ThreadMetaRow.test.tsx, apps/web/src/components/chat/threadTiming.ts, apps/web/src/components/chat/threadTiming.test.ts, apps/web/src/components/ChatView.tsx, docs/studio/operator-guide.md, reports/timing-investigation.md | Test: focused timing, metadata and existing execution selector regressions for multiple messages/turns, active/queued/waits/resume/missing timestamps and disclosure accessibility

### T-15 Regress 0957 no-action carry-forward receipts
- AC: AC-14 | Files: apps/web/src/studio/workerMessagePresentation.ts, apps/web/src/studio/workerMessagePresentation.test.ts, apps/web/tests/agent-messages/internalReceipts.ts, apps/web/src/components/studio/RelayedMessage.test.tsx, apps/web/src/studio/messagePresentation.test.ts, reports/internal-receipts-investigation.md | Test: exact 0957-style receipts fold; user-action and user-result preservation cases pass; coordinate 1130, no lifecycle edits

### T-16 Verify and close 1106
- AC: AC-12, AC-13, AC-14 | Files: apps/web/tests/thread-machine/, apps/web/tests/chat-density/, reports/timing-validation.md, reports/timing-review.md | Test: headless real metadata component across coordinator/worker, live/settled/waits/multiple follow-ups, relevant production build, exact-head CI/PR959, current scoped verify, fresh-context review and complete

### T-17 Preserve exact provenance for the reviewed LegendList patch update
- AC: AC-05, AC-11 | Files: scripts/studio-toolchain/preservation-audit.mjs, scripts/studio-toolchain/preservation-audit.test.mjs, scripts/studio-toolchain/reviewed-lock-changes.json | Test: preservation audit regressions including unchanged registry integrity, exact same-package patch replacement and negative controls; fresh independent review of the original patch and pinned record

The current-main merge exposed an omitted provenance record for the existing T-08 patch (commit c43122baf030e06e39eea71e3eb8b72e47982776). Permit only a reviewed replacement of the same existing patched package key, with exact before/after hashes and required patch bytes; keep the digest-pinned closed set and all registry protections. No source patch or test assertion is weakened to accommodate the audit.

### T-18 Repair hosted typecheck findings without a baseline waiver
- AC: AC-11, AC-12, AC-13 | Files: apps/web/src/components/ChatView.tsx, apps/web/src/components/chat/ThreadMetaRow.tsx, apps/web/src/components/chat/threadTiming.ts, apps/web/src/components/chat/threadTiming.test.ts, apps/web/src/studio/messagePresentation.ts, apps/web/src/studio/messagePresentation.test.ts, apps/web/tsconfig.json, scripts/legend-list-row-layout.test.ts | Test: focused timing/presentation/installed LegendList regressions; scoped web+scripts typecheck reports zero new diagnostics; exact-head fresh review and hosted CI.

Hosted PR959 head144738db exposed a real out-of-scope background-task reference in the ChatView render and six additional strict TypeScript/test diagnostics. Use the existing state-owned pending tasks under the same settled-turn predicate, explicitly admit undefined where actual records use it, include the existing shared test fixture in the web composite project, and keep the installed-bundle regression deterministic. No typecheck baseline or assertion/timeout weakening.

### T-19 Retain concise failure counts and verify relay disclosure contracts
- AC: AC-09, AC-10, AC-11 | Files: apps/web/src/components/chat/MessagesTimeline.logic.ts, apps/web/src/components/chat/MessagesTimeline.activityDiffs.test.tsx, apps/web/src/components/studio/ProjectWorkspace.attachments.test.tsx | Test: actual hosted-failing activity-diffs and attachments component suites plus timeline logic; all original failure counts/chips/attribution preserved and relay original text verified after accessible disclosure.

Hosted web shard1 exposed missing turn-level failure counts after concise failures were deliberately left outside the folded routine work. Count all turn failures in the turn summary while keeping their actionable rows visible. Update the old relay test to exercise the new explicit disclosure instead of assuming all internal messages start expanded; retain original text, source navigation and no-send assertions.

### T-20 Exercise the actual timing projection boundary
- AC: AC-12, AC-13 | Files: apps/web/src/components/ChatView.tsx, apps/web/src/components/chat/ProjectedThreadMetaRow.tsx, apps/web/src/components/chat/ProjectedThreadMetaRow.test.tsx | Test: render the real metadata wrapper and real ThreadMetaRow with Effect DateTime server runs; assert last/recorded elapsed, partial-to-complete history, live-to-settled run transitions, missing projection and settled background-work gating; measure the extracted glue coverage, focused typecheck and independent review.

The lead authorized meaningful timing-glue integration without broad ChatView refactoring. Extract only the new projection/history/background adapter into the actual metadata wrapper used by ChatView. Tests must not mock ThreadMetaRow or timing derivation. This is boundary integration, not a claim to mount the entire ChatView. Keep all existing changed production files in the whole-file coverage scope and retain the failed60% gate unless the lead/user explicitly resolves it.

### T-21 Integrate reviewed shared Windows repairs
- AC: AC-05, AC-11 | Files: apps/server/src/fleet/fleetSkills.ts, apps/server/src/fleet/fleetSkills.test.ts, apps/server/src/worktreesDirectory.test.ts, apps/server/src/handoff/handoffPlacement.test.ts, apps/server/src/project/ClaudeSettingsWrite.test.ts, apps/server/src/project/ProjectSkillsActions.test.ts, apps/server/src/project/ProjectSkillsActions.ts, apps/server/src/project/ProjectSkillsActionsCommon.ts, apps/server/src/project/ProjectSkillsActionsRpc.ts, apps/web/src/components/RightPanelTabs.keyboard.test.tsx | Test: exact shared Windows launcher/path regression suites, unchanged concise UI/source blob proof, fresh integration review and exact-head hosted CI.

The lead authorized normal integration of the full reviewed PR991 dependency before its last hosted fleet retry finishes, plus the reviewed PR961 path-fixture delta. Do not duplicate its implementation or weaken tests. Preserve the user's exact5152e55a concise UI acceptance and one-time coverage exception only with byte-identical owned product files; new integration must receive independent review and CI.
