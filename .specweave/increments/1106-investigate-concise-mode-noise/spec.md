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
- None. Investigation and verified repairs are authorized.
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
