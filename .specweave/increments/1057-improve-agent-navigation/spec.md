# Improve agent navigation

## Problem

A thread's agent popover (the bot chip in the thread header, `SubagentsChip`) lists workflows first, then subagents in spawn order, with no grouping, no filter and no keyboard model beyond Tab. On the 1041 design thread (October 24, 2026) it held 5 workflows and 55 subagents. The two Working agents were the last two rows, under about 58 Done and Stopped rows, so the person had to scroll to the bottom of a 420px list to find live work. The header said "2 working" without linking to them.

Anton: "Working agents or the most relevant ones should be at the top, I believe. Think about how to make navigation the best from the UI/UX perspective."

Constraints from earlier decisions:

- Rows must not move under the reader because of background updates (`sidebar-chats-no-jumping`, PR #443). Only the person's own action reorders a list.
- Only the reader's own input pauses follow behaviour (`follow-latest-reader-intent`, PR #481).
- "Working" must be true. A stale running flag is not liveness. 1053 (core recovery) adds `subagentExecutionStatus` with `unknown` for unreachable machines and settles stranded children. `threadRunHealth` on main already classifies a quiet run as `stalled`.

Evidence: screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-bcbf0101-8894-4999-a7e7-28dded9f8613.png`; source `apps/web/src/components/studio/shell/SubagentsChip.tsx` and `apps/web/src/studio/threadSubagents.ts` at `origin/main`.

## Scope

In: ordering, grouping, header summary, filter, keyboard and screen reader model, selection retention and in-place updates for the thread agent popover; narrow-width layout. Mockups and this spec are the review deliverable; code waits for approval and for 1053 to merge.

Out: the sidebar and the project Threads pane order (already stable, unchanged); server liveness and settlement (1053 owns them); the read-only peek itself; iOS (a follow-up that reuses the same pure ordering function).

## Proposed behaviour

The order is computed when the popover opens, from one pure function, and sorts only on immutable timestamps inside a group:

| Group (shown only when non-empty) | Who belongs | Order inside | Default |
|---|---|---|---|
| Needs you | active and blocked on the person (approval, answer, sign-in) | oldest request first | open |
| Working | running or starting, and `threadRunHealth` not stalled | newest started first | open |
| Quiet or unreachable | running with no activity past the stall threshold, or `unknown` (machine unreachable) | newest started first | open, muted |
| New results | finished, failed or interrupted since the person last opened this popover on this thread | failed first, then newest finished | open |
| Earlier | every other finished row | newest finished first | folded ("Show 48 earlier"), unless the filter is active |

- Nested rows stay under their parent. A parent with live children ranks by its most urgent descendant and shows "2 of 6 working". A workflow is one row whose agents nest under it when lineage links them.
- Group placement is fixed while the popover is open. A row that changes state updates its dot, label and timer in place. New rows and group changes collect in a pill at the top ("2 updates, Show"); the person applies them. A row entering Needs you shows a separate "1 needs you" pill that jumps to it.
- The header turns into filters: "2 working", "1 needs you", "3 new" are buttons that filter the list; a text filter (title, prompt, model) appears above 12 rows; `/` focuses it.
- Selection: the last opened row's key is kept per thread. Reopening the popover focuses and scrolls to it (or to the first Needs you row if one is new). Returning from a peek restores focus to that row.
- Keyboard: one Tab stop for the list (roving tabindex), Up/Down, Home/End, Enter or Right opens the peek, Left goes to the parent row, typing letters jumps by title, Escape clears the filter and then closes. Groups are `role="group"` with headings; state changes go through one polite live region, throttled to one announcement every 5 seconds.
- Narrow widths (under 480px): the popover becomes a bottom sheet, titles wrap to two lines, model and timer move to the second line.
- The chip keeps the total count; its dot uses the warning tone when anything needs the person and the working tone otherwise.

## Acceptance Criteria

- [ ] AC-01: With the 1041 fixture (5 workflows, 55 subagents, 2 working), opening the popover shows both Working rows in the first viewport without scrolling, and Earlier is folded behind "Show N earlier".
- [ ] AC-02: Group membership follows truthful status: a running row whose `threadRunHealth` is stalled, or whose status is `unknown`, appears under Quiet or unreachable and is not counted in "N working"; a row blocked on the person appears under Needs you and is not counted working.
- [ ] AC-03: While the popover is open, 30 background updates (status changes, new rows, timers) cause 0 row reorders and 0 scroll-position changes; state changes render in place and new rows or group moves surface only through the updates pill, which applies them on press.
- [ ] AC-04: The last opened row is focused and scrolled into view when the popover reopens and when the person returns from its peek, including after rows were added above it.
- [ ] AC-05: The list is reachable and fully operable by keyboard alone (one Tab stop, arrows, Home/End, Enter, Left to parent, type-ahead, `/`, Escape), and axe reports no violations for the open popover in both themes.
- [ ] AC-06: Header filters and the text filter narrow the list; with a filter active, Earlier unfolds and matching rows keep their group headings.
- [ ] AC-07: Nested subagents and workflow agents render under their parent; a parent ranks by its most urgent descendant and shows "N of M working".
- [ ] AC-08: At 375px wide the list opens as a bottom sheet with no horizontal overflow and long titles wrap to two lines.
- [ ] AC-09: Fresh-context review passes, and the before/after headless captures are saved under the increment's `evidence/` folder.

## Approach

1. `apps/web/src/studio/subagentNavigation.ts` (new): `orderSubagentEntries(entries, { lastSeenAt, nowMs })` returns groups with nested rows. Pure, no React, reused by iOS later. Inputs are 1053's `SubagentEntry.status` and `threadRunHealth`; sort keys are `startedAt`, `completedAt` and request time only. `updatedAt` is used only to detect quiet runs, never to sort.
2. `apps/web/src/components/studio/shell/SubagentsChip.tsx`: snapshot the order on open (`useState` initialised from the ordering, plus a pending diff), render groups, pills, header filters, text filter, roving focus and the live region. Persist `lastSeenAt` and the last opened row key per thread in client storage keyed by `environmentId:threadId`.
3. `apps/web/src/components/studio/shell/panes.css`: group headings, pills, sheet layout under 480px, focus ring.
4. Headless fixture `apps/web/tests/subagent-navigation/` (the existing `subagent-handoff-continuity` fixture pattern): the 1041 data set, a 30-update replay that counts reorders and scroll changes, keyboard script, axe, 375px capture.

Rejected: live re-sorting while open (breaks the no-jumping rule and loses the reader's place); sorting by last activity (`updatedAt` changes on every event and would reshuffle constantly); hiding finished rows entirely (results that still need review would disappear); a separate "Agents" page (more navigation for a list that is usually short).

Risks: 1053 changes the same three files and must merge first; the stall threshold comes from `threadRunHealth` and can mislabel a long silent command, so Quiet stays a visible group rather than being hidden.

## Decisions

### Asked
- none (proposal awaits Anton's review)
### Defaulted (change any before sw-do)
- D-01 Group order Needs you, Working, Quiet or unreachable, New results, Earlier (reversible).
- D-02 Freeze order while open; changes arrive through the updates pill rather than auto-applying (reversible; alternative: auto-apply after 3 seconds without pointer or keyboard input).
- D-03 Inside Working, newest started first, so the agent just asked for is on top (reversible; alternative: longest running first).
- D-04 "New results" means finished since this person last opened the popover on this thread, stored per device (reversible).
### Open
- none

## Tasks

### T-01 Review proposal and mockups with Anton
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1057-improve-agent-navigation/mockups/agent-navigation.html, .specweave/increments/1057-improve-agent-navigation/reports/recommendation.md | Test: test -s .specweave/increments/1057-improve-agent-navigation/mockups/agent-navigation.html

### T-02 Pure ordering function with truthful groups
- AC: AC-01, AC-02, AC-07 | Files: apps/web/src/studio/subagentNavigation.ts, apps/web/src/studio/subagentNavigation.test.ts (app repo, after 1053 merges) | Test: npx vp test run apps/web/src/studio/subagentNavigation.test.ts

### T-03 Stable popover: snapshot order, in-place updates, pills, selection retention
- AC: AC-03, AC-04 | Files: apps/web/src/components/studio/shell/SubagentsChip.tsx, apps/web/src/components/studio/shell/SubagentsChip.test.tsx | Test: npx vp test run apps/web/src/components/studio/shell/SubagentsChip.test.tsx

### T-04 Filters, keyboard model, live region, narrow sheet
- AC: AC-05, AC-06, AC-08 | Files: apps/web/src/components/studio/shell/SubagentsChip.tsx, apps/web/src/components/studio/shell/panes.css | Test: npx vp test run apps/web/src/components/studio/shell/SubagentsChip.test.tsx

### T-05 Headless fixture: reorder count, keyboard, axe, 375px
- AC: AC-01, AC-03, AC-05, AC-08 | Files: apps/web/tests/subagent-navigation/ | Test: PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node apps/web/tests/subagent-navigation/verify.mjs

### T-06 Verify and close 1057
- AC: AC-09 | Files: .specweave/increments/1057-improve-agent-navigation/reports/review.md | Test: specweave verify 1057-improve-agent-navigation
