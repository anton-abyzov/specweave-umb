# Reports show once with their own title

## Problem

The user sees a worker's answers as duplicated messages. Thread [How MCP and Connect work] stores one final message per turn, with no second copy in `studio_thread_read` and none repeated at the coordinator level. What repeats is the display: a follow-up that merely mentions "the same report" turned 369-word and 362-word answers into report cards, and each card fell back to the thread's name as its title, so identical-looking cards stacked turn after turn. Where a title came from the report's first line, the card summary and the reader's lead repeated those same words under it.

## Scope

In: the shared report rule and title, card summary, reader document. Out: the coordinator's relay, saved report files, the 600-word and heading thresholds, the phone, which has no report card and shows the message text once.

## Acceptance Criteria

- [ ] AC-01: A reply of 150 to 600 words with no heading, after a message that mentions a report, shows as plain text with no card; a requested reply with a heading still shows as a card.
- [ ] AC-02: A report opening with a bolded sentence of 41 to 90 characters takes that sentence as its title, so such cards do not all carry the thread's name. A shorter bold opening such as `**No.**` reads as a label and keeps the thread's name.
- [ ] AC-03: Words used as the title do not repeat in the card summary or the reader's lead.
- [ ] AC-04: The rule works from the message text alone, so every provider, web, desktop and threads loaded from history behave the same.
- [ ] AC-05: Before and after headless screenshots rendered from the real thread's text are saved to files.

## Approach

Change `shouldCollapseReport`, `reportTitle` and `reportSummary` in `packages/shared/src/threadReport.ts`, add `reportBodyAfterTitle`, and use it in `reportDocument` in `packages/shared/src/reportDocument.ts`. Rejected: deduplicating timeline items, since no duplicate item exists; dropping the card altogether, since long documents still read better in the reader.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 A requested reply needs a heading to become a card; a reply past 600 words or 80 lines stays a card without one.
- D-02 A line is removed from the body only when its raw text equals the title, plus a lone `# ` first block, which the reader always showed as the title (#1217).
### Open
- none

## Tasks

### T-01 Report rule, title and repeated words
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/shared/src/threadReport.ts, packages/shared/src/reportDocument.ts, apps/web/src/components/chat/MessagesTimeline.test.tsx, apps/web/src/components/chat/longReport.test.ts, packages/shared/src/threadReport.test.ts | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/threadReport.test.ts packages/shared/src/reportDocument.test.ts apps/web/src/components/chat/longReport.test.ts apps/web/src/components/chat/MessagesTimeline.test.tsx apps/web/src/components/chat/ReportArtifact.test.tsx

### T-02 Before and after screenshots
- AC: AC-05 | Files: none | Test: headless render saved under ~/.specwithcode/m4/evidence/report-duplicate/

### T-03 Merge and hand to the release dispatcher
- AC: AC-04 | Files: none | Test: required checks on the exact head
