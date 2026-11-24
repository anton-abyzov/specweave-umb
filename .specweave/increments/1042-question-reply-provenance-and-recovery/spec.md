# 1042 Question replies: chat first, clear authorship, no dead ends

## Problem

Follow-up to 0977 (closed October 21, 2026, PR specwithcode-dev#514, merge 6728899d06). On October 23, 2026 Anton answered a coordinator ask_user request ("App binding") through the Coordinator requests dialog and found the flow confusing:

1. **Two ways in, one unclear.** The dialog (Your answer, Attach to answer, Send answer, Close review) duplicates the chat reply. Anton expects paste and attach to work in the chat composer and sees no reason for the dialog unless it covers a real recovery case.
2. **Ambiguous authorship.** Answering echoed the coordinator-authored question into the conversation as if Anton had said it, so he could not tell whether the request was genuine or his own words.
3. **Stale and dead states.** The dialog kept old answer text, and a request that failed or was already settled could leave a state with no way forward.

Screenshot: `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-b59ed0c4-24a2-45e7-b91c-d7cef659f828.png`.

## Scope

In: coordinator and thread composers while a question request is pending (paste, drop, attach, send); sender provenance of question and answer messages in thread and coordinator timelines; answered/expired request settlement in cards, badges and the dialog; draft and attachment survival across send failures; deciding whether the Coordinator requests dialog stays, as recovery only, based on its real recovery semantics; small-window, keyboard and screen-reader use; tests and file-backed headless proof.

Out: approval semantics and grants (no bypass, no removal); model controls in the composer toolbar (1041 T-05 owns them); fallback and model-lane policy; merge, release and restart (sole integration and release owner: Complete screenshot sessions).

## Acceptance Criteria

- [x] AC-01: With a question request pending, the chat composer of the thread and of the project coordinator is the primary answer path: typed text, pasted and dropped images and the attach button all work, chips show, and send delivers text and files to the agent as the answer.
- [x] AC-02: Every message in a question exchange shows its real sender: the question reads as the agent's (coordinator or worker named), the answer as the user's, and no user-authored bubble contains agent-authored question text.
- [x] AC-03: An answered, expired or withdrawn request settles everywhere (card, badge, dialog, composer hint) within one projection update, and a stale request shows why it cannot be answered plus a way forward instead of a dead control.
- [x] AC-04: A failed send keeps the draft text and attachments, shows the exact error next to the composer, and retry delivers once with no duplicate answer.
- [x] AC-05: The Coordinator requests dialog is kept only for the recovery cases research proves it serves (named in Decisions); in those it carries no stale draft, uses the same draft and attachment path as chat, and never shows a second, divergent answer box. Approvals and plan reviews keep their current semantics.
- [x] AC-06: The flows work at 360 px wide and 200% zoom, by keyboard alone (focus order, Escape, Enter) and with a screen reader (labelled controls, live status for send and settle).
- [x] AC-07: Unit and component tests cover AC-01 to AC-05, and a headless fixture (headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never) records interaction and visual proof in light and dark at 360 and 1280 px to `/Users/antonabyzov/Projects/github/studio-research-notes/question-reply-provenance-2026-10-23/`.

## Approach

Research (Fable 5.1, origin/main `2e95e09ae3`): `/Users/antonabyzov/Projects/github/studio-research-notes/question-reply-provenance-2026-10-23/research/findings.md`. Causes C1 to C9 there.

1. Chat first: the coordinator page derives its pending question from the coordinator projection, shows `ComposerPendingUserInputPanel` above `CoordinatorComposer`, and routes a send while a question waits through `planQuestionChatReply` and `respondToThreadUserInput({ answeredInChat: true })` with the draft's uploaded attachments (C1).
2. Explicit sender: the stored `async-answer:` user message holds only the user's words (answers labelled by question header when there are several), never the agent's question text. The coordinator conversation folds a dialog answer into a `DecisionCard` row like `session-logic.ts` does and keeps a chat reply as the user's bubble. Cards and the dialog name who asked: the coordinator or the worker thread (C2, C3).
3. Settle everywhere: one derived pending question drives notice, chip, composer panel and dialog. "Runtime request ... is resolved." on a retry counts as settled when the projection shows the answer; otherwise the exact server string shows beside the composer (C6).
4. Failure-safe drafts: the draft text and uploaded attachments stay on failure, the error shows next to the composer, and a stable commandId per request and draft revision makes a replay idempotent (C4, C6).
5. Recovery-only dialog: approvals and plan review are unchanged. For questions the dialog shows "Answer in chat" (closes it, focuses the coordinator composer) whenever the composer can answer, and an answer box bound to the same coordinator draft only when the composer is blocked or has no model (case F). Initial focus goes to the first actionable control. The held-queue entry no longer opens an empty dialog (C5, C7, C8, C9).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Direct chat reply is primary; the dialog survives only as optional recovery for pending requests (Anton, October 23, 2026).
- D-02 Main implementation runs on native Claude Code Opus 5.5 with ultracode effort; the hardest research runs on Claude Fable 5.1. No silent model substitution (Anton, October 23, 2026).
- D-03 The app repository is written only through its registered binding (repository `dbc4018e-bea3-46a1-826e-dd6ee149c9c7`) via `studio_thread_launch` workspaceStrategy; no ad-hoc checkout.
- D-04 Shared composer files are coordinated with the 1041 owner: this increment does not touch the toolbar model controls.
- D-05 The Coordinator requests dialog keeps an answer box for exactly one recovery case: the coordinator composer cannot send (blocked or no model). Every other question offers "Answer in chat" (AC-05).
- D-06 Gaps the fresh-context closing review found on #662's accepted head `6616a312e` (AC-04 thread placement, AC-06 live status, Approach 3 landed-answer rule) ship as a separate stacked delta on `fix/question-reply-1042-close-gaps`, never on the accepted head.
### Open
- none

## Tasks

### T-01 Research: actual request and reply behavior
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/question-reply-provenance-2026-10-23/research/findings.md | Test: findings file exists with file:line citations, reproduced behaviors and a keep/drop verdict for the dialog

### T-02 Chat composer answers with files in thread and coordinator
- AC: AC-01, AC-04 | Files: apps/web/src/components/chat, apps/web/src/studio, apps/web/src/components/ChatView.tsx | Test: vp test run apps/web/src/components/chat apps/web/src/studio

### T-03 Sender provenance for questions and answers
- AC: AC-02 | Files: apps/server/src/orchestration-v2, apps/web/src/session-logic.ts, apps/web/src/studio | Test: vp test run apps/server/src/orchestration-v2/Orchestrator.questionAnswers.test.ts apps/web/src/session-logic.test.ts

### T-04 Settle answered and stale requests; recovery-only dialog
- AC: AC-03, AC-05 | Files: apps/web/src/components/studio, apps/web/src/components/chat | Test: vp test run apps/web/src/components/studio apps/web/src/components/chat

### T-05 Small windows, keyboard and screen reader; headless proof
- AC: AC-06, AC-07 | Files: apps/web/tests/question-reply, /Users/antonabyzov/Projects/github/studio-research-notes/question-reply-provenance-2026-10-23 | Test: headless fixture light/dark 360/1280 px and 200% zoom; headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never

### T-06 PR with exact-head CI and review, handed to the integration owner
- AC: AC-07 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/question-reply-provenance-2026-10-23/pr.md | Test: gh pr checks on the exact head; fresh-context review verdict; no merge or release from this lane

### T-08 Close-review gaps: live status, thread answer errors beside the composer, landed-answer rule
- AC: AC-03, AC-04, AC-06 | Files: apps/web/src/components/ChatView.tsx, apps/web/src/components/chat, apps/web/src/components/studio, apps/web/src/studio, apps/server/src/orchestration-v2/ContextHandoffService.test.ts, apps/web/tests/question-reply, apps/web/tests/decision-card-reply | Test: vp test run apps/web/src/components/chat apps/web/src/studio apps/web/src/components/studio; headless question-reply fixture with live-status and Tab-order checks; headless decision-card-reply fixture with the thread answer error against the composer at 900 and 360 px; stacked PR with exact-head CI and fresh-context review

### T-07 Verify and close 1042
- AC: AC-07 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1042-question-reply-provenance-and-recovery/ledger.jsonl | Test: specweave verify 1042; fresh-context review; specweave complete 1042

Implementation paths are relative to the app repository and are replaced with the bound worktree path before tasks are claimed.
