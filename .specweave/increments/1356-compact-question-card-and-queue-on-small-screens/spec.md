# Compact question card and queue on small screens

## Problem

On a 14-inch MacBook (1512x945), in the narrow thread side panel and in short windows, the queue block and an ask_user question card stacked above the composer cover almost the whole thread body. Each option shows a multi-line description, the queue shows a paragraph ("Steer now is unavailable: ...") and the card runs off the bottom. Measured before the change in the fixture: the stack took 47% of the panel at 1512x945, 56% in a 480 px side panel and 62% at 700 px tall, leaving 140 px of thread visible.

## Scope

In: the SpecWithCode web/desktop thread composer stack (`apps/web`): question card, queue block, Jump to latest placement, a headless fixture and web tests. Out: the native iOS app, whose question card is a transcript row without options and is not stacked over the thread; the coordinator page card keeps its per-question fold (it gets the compact options from the shared component).

## Acceptance Criteria

- [x] AC-01: The question card scrolls inside a height tied to the thread panel (about 40% for card plus queue), so the stack stays at or under 45% of the panel at 1512x945, 480 px wide and 700 px tall.
- [x] AC-02: Options show one line each (label, Recommended badge, clipped description) and open to the full description on hover, keyboard focus or the details toggle, without picking the option.
- [x] AC-03: The card folds to "Question: ... · N options" and the fold is remembered per thread across reloads; other threads keep their own.
- [x] AC-04: The queue starts folded to one line; the steer note is a short muted hint ("Can't steer now", full reason in its tooltip) and only shows when some row could be steered.
- [x] AC-05: Jump to latest never overlaps the cards (found by `data-jump-to-latest`, not its label).
- [x] AC-06: Verified headless in light and dark at 1512x945, 480x945, 1512x700 and 480x700, with before and after screenshots.

## Approach

`ComposerBanner.Scroll` and the card's scroll area size from `--chat-panel-height`, which ChatView publishes from its overlay's parent with the same ResizeObserver that measures the composer. `ComposerPendingUserInputPanel` gains compact rows, a folded summary and a `collapseKey` (environment and thread) stored in local storage by `questionCardCollapse.ts`. `QueuedRunsControl` folds by default (opens while a row is edited) and replaces the steer paragraph with a header hint. The pill measurement moved to `measureScrollToEndClearance` in `composerFooterLayout.ts`, shared by ChatView and the fixture. A keyboard-opened row folds only after a press completes, so a click never lands on a row that moved.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A folded card stays folded for later questions in the same thread (the summary names the new question) → per-thread boolean.
- D-02 Hover opens a row after 180 ms; keyboard focus opens it only for `:focus-visible`.
### Open
- none

## Tasks

### T-01 Compact card, queue and pill placement
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/web/src/components/chat/ComposerPendingUserInputPanel.tsx, apps/web/src/components/chat/QueuedRunsControl.tsx, apps/web/src/components/chat/questionCardCollapse.ts, apps/web/src/components/chat/ComposerBanner.tsx, apps/web/src/components/composerFooterLayout.ts, apps/web/src/components/ChatView.tsx | Test: vp test run of the QueuedRunsControl, ComposerPendingUserInputPanel and composerFooterLayout suites

### T-02 Headless fixture and screenshots
- AC: AC-06 | Files: apps/web/tests/compact-stack/ | Test: node apps/web/tests/compact-stack/verify.mjs /absolute/report-dir
