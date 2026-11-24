# Decision cards: reply in chat with attachments, no lost messages

## Problem

When an agent or subagent asks a question through `ask_user`, the thread shows a decision card (lettered options, "reply in chat"). The user reported on October 20, 2026 that while a card is showing, attaching images to a chat reply does not work, and that messages sometimes disappear when a subagent's question card appears. A free answer must be a full chat message: text, pasted or attached images and files, sent to the asking thread and kept in the timeline.

## Scope

In: the composer while a decision card is pending (`apps/web/src/components/chat/ComposerPendingUserInputPanel.tsx` and the composer around it), the "reply in chat" path, attachments (paste, drag, picker) on that reply, delivery of the reply as the answer, and the timeline when a card from a delegated child thread appears or resolves in the parent.

Out: redesigning the card; new question types.

## Acceptance Criteria

- [ ] AC-01: While a decision card is pending, the composer stays usable: the user can type, paste an image, drop a file or use the attach button, and the attachments show as chips before sending.
- [ ] AC-02: Sending from the composer while a card is pending delivers the text and every attachment as the answer to that question (the asking agent receives the images), and the card resolves showing "Answered in chat".
- [ ] AC-03: "Reply in chat" focuses the composer without clearing an existing draft or its attachments.
- [ ] AC-04: A card raised by a delegated subagent or child thread never hides, replaces or drops messages already in the parent timeline or the user's unsent draft; reproduce the reported loss first and record its cause.
- [ ] AC-05: Answering by option and answering in chat both survive a reload and a service restart (no answer lost, no duplicate).
- [ ] AC-06: Tests: component tests for AC-01..AC-03, a reducer or projection test for AC-04, and a headless browser recording of a card answered in chat with an attached image, light and dark.

## Tasks

### T-01 Reproduce and find the causes
- AC: AC-01, AC-04 | Files: none | Test: headless repro recording, cause written in the lane report

### T-02 Composer and reply in chat with attachments
- AC: AC-01, AC-02, AC-03 | Files: ComposerPendingUserInputPanel.tsx, composer, answer RPC | Test: component and server tests

### T-03 Child-thread cards keep the parent timeline
- AC: AC-04, AC-05 | Files: timeline projection, pending request handling | Test: projection test, restart test

### T-04 Evidence
- AC: AC-06 | Files: apps/web tests | Test: headless Playwright, light and dark

### T-05 Verify and close 0977
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
