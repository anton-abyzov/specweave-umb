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
