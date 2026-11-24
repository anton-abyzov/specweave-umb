# Concise transcripts fold tool rows the same on web, desktop and iOS

## Problem

On November 7, 2026 the user saw a running thread on the iPhone (Duo layout) list a full `Ran cd /Users/... && ls ...` row and four separate "Use tool" rows while the desktop header said "Replies: Concise · Folded steps". They expected Concise to keep tool runs and thinking out of the conversation on every client.

Cause, from source at `anton-abyzov/specwithcode` `3fa12bc408`:

- "Replies: Concise" is the agent's reply style (`responseStyle`, an instruction to the model). It never changed what the transcript shows. What the transcript shows is the second half of that label, the timeline detail: Results only, Folded steps (default) or Everything.
- The phone keeps its own detail level in UserDefaults (`TimelineDetail.stored()`), default Folded steps.
- On iOS, Folded steps returned the running turn unfolded (`if active, detail == .normal { return segment }` in `apps/ios/SWCKit/Sources/SWCSync/TimelineDetail.swift`): every command, tool call and thought of the turn in progress was its own row. Web and desktop fold the running turn's tool calls into one live row and settled tool groups into one summary row each, so the three clients disagreed.
- iOS titles any tool without a hand-written name "Use tool" (`ToolPresentation.swift`), so four different MCP calls read as four identical rows.

## Scope

In: one written rule for what each detail level shows, shared conformance cases in `packages/shared`, the iOS fold of running and waiting turns, readable iOS titles for unnamed tools, web and desktop checked against the same cases, before/after screenshots. Out: merging reply style and timeline detail into one setting; syncing the phone's detail level with the desktop's; changing Everything.

## Acceptance Criteria

- [ ] AC-01: The rule is written once in `docs/transcript-detail.md` and encoded as cases in `packages/shared/src/transcriptDetail.cases.json`; both the web timeline tests and the iOS folding tests run every case.
- [ ] AC-02: In Folded steps, a running turn shows your message, the agent's in-between notes, approvals, questions and failed steps; each run of consecutive thinking, tool, command and agent steps is one fold row, the latest one live ("Working · Ran 1 command · 4 tool calls" with a spinner), opened by tap or click.
- [ ] AC-03: In Results only, a running turn shows only the latest note and one live row; failures appear as a count on the row; thinking never shows, even opened.
- [ ] AC-04: Settled turns keep today's behaviour on all clients: one "Worked" fold before the final reply; Everything shows every row.
- [ ] AC-05: iOS names a tool without a hand-written title from its own name (`mcp__studio-code__chrome_screenshot` reads "Chrome screenshot"), never "Use tool".
- [ ] AC-06: Before and after screenshots of a running turn with a command and four MCP calls exist for web (headless), desktop renderer (headless) and iOS, saved to files.

## Approach

1. `docs/transcript-detail.md`: the rule, as a table of row kind by level and turn state.
2. `packages/shared/src/transcriptDetail.cases.json`: abstract rows (`user`, `note`, `reply`, `thinking`, `command`, `tool`, `failed`, `approval`) with the expected visible sequence per level and running state.
3. iOS `TranscriptFolding.fold`: replace the unfolded running-turn branch with step-group folding; group ids `fold:<first step id>`; failed tools break a group in Folded steps. `ToolPresentation` falls back to a humanised tool name.
4. iOS test loads the shared JSON by path; web test maps the same cases to `TimelineEntry` and runs `deriveMessagesTimelineRows`.
5. Web/desktop: no behaviour change expected; fix any case the web test fails.

Rejected:

- Make reply style Concise force Results only. It overrides a choice the user made (their header shows Folded steps) and couples model instructions to display.
- Hide all tool rows in Folded steps, even when opened. Loses the audit trail that Folded steps exists to offer.
- Sync the desktop's detail level to the phone. Per-device choice is deliberate (a phone wants less); the fix is that each level means the same thing everywhere.
- A shared TypeScript fold function. Swift cannot import it; shared JSON cases plus a written rule is what both languages can check.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 reply style and timeline detail stay separate settings → default (reversible).
- D-02 the phone keeps its own detail level → default.
### Open
- none

## Tasks

### T-01 Write the rule and shared cases
- AC: AC-01 | Files: docs/transcript-detail.md, packages/shared/src/transcriptDetail.cases.json | Test: test -f docs/transcript-detail.md

### T-02 Fold running and waiting turns on iOS
- AC: AC-02, AC-03, AC-04 | Files: apps/ios/SWCKit/Sources/SWCSync/TimelineDetail.swift, apps/ios/SWCKit/Tests/SWCSyncTests/TranscriptFoldingTests.swift | Test: swift test --filter TranscriptFolding (apps/ios/SWCKit)

### T-03 Readable iOS tool titles
- AC: AC-05 | Files: apps/ios/SWCKit/Sources/SWCSync/ToolPresentation.swift | Test: swift test --filter ToolPresentation

### T-04 Web and desktop run the shared cases
- AC: AC-01, AC-04 | Files: apps/web/src/components/chat/transcriptDetailCases.test.ts | Test: pnpm --filter @specweave-studio/web exec vitest run src/components/chat/transcriptDetailCases.test.ts

### T-05 Before and after screenshots
- AC: AC-06 | Files: apps/web/tests/live-activity/main.tsx | Test: ls ~/.specwithcode/ministorm/evidence/1148

### T-06 Verify and close 1262
- AC: AC-01 | Files: none | Test: specweave verify 1262
