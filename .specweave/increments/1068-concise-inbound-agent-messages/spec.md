# Concise inbound agent messages

## Problem

On October 25, 2026, Anton saw the EasyChamp coordinator in Concise mode filled with one message, "Sent by Quiz product value audit". It was about 40 lines of raw text: absolute paths, words run together and ENOSPC details. The thread beside it showed similar agent-to-agent receipts, cut off by a fade (screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-d0617d9f-25a6-45a0-bf70-22a78454d715.png`).

Causes, checked against source on October 25:
1. **Installed versus source.** The installed 1.0.76 (released October 24, 3:10 PM) predates #661 (`bcf4cd48`, 7:42 PM). So 1043's coordinator fold (`WorkerMessageBody`) is not installed, and the coordinator shows worker messages whole.
2. **Concise is ignored.** Even on main, the coordinator folds worker messages the same way at every detail level (600 characters or 8 lines; a lead of up to 280 characters). Concise promises one line per finished turn, but an agent message still shows several lines of raw excerpt.
3. **The thread page uses the person's clamp.** Messages another agent sent (`createdBy: "agent"`, "Sent by …") use the clamp meant for a person's own prompt (`CollapsibleUserMessageBody`, 11rem with a fade). The shared verbatim excerpt is not used.

The run-together words come from the sender. 1043 decided the app never re-spaces, rewrites or summarizes an agent's text, and that decision stands.

## Scope

In:
- the presentation of messages one agent sends another: worker to coordinator in the coordinator view, and any agent-created message on a thread page;
- the timeline detail levels (Concise, Normal, Verbose);
- historical messages, rendered the same way with no stored-data change;
- headless before and after captures with screenshot-shaped payloads.

Out:
- the person's own prompts, which keep their clamp;
- the coordinator's own replies and reports (`ReportArtifact`, `CollapsibleReport`);
- activity rows and turn cards, which belong to 1011 (#687);
- routing, delivery and stored payloads;
- agent instructions;
- release and installed acceptance, which belong to the release owner. This lane verifies afterward.

## Acceptance Criteria

- [x] AC-01: In Concise, a long agent message (over 280 characters or 3 non-blank lines) shows its sender, a verbatim lead of whole opening sentences (up to 160 characters; a longer first sentence is cut at a space outside links, code and bold, with an ellipsis, and at Normal's 240 characters when no space falls in the second half of the 160), any decision sentence (a question or a `Blockers:` line), its hidden size ("N more characters", as 1043 labels it), "Show full message" and "Copy original". A shorter message shows whole, as does one whose fold would hide under 100 characters or leave 80% showing. A long message with no prose to cut (only JSON or a code fence) shows its top, clipped with a fade, and its whole size.
- [x] AC-02: Normal keeps 1043's fold (600 characters or 8 lines; a lead of up to 280 characters plus the decision sentence), with blank lines no longer counted. Verbose opens every agent message, which can still be folded with "Show less".
- [x] AC-03: On a thread page, a message another agent sent uses the same presentation as AC-01 and AC-02, at the thread's own detail level, below its existing "Sent by" provenance. The person's own prompts keep their clamp.
- [x] AC-04: Nothing is rewritten. The excerpt and the expanded text come from the stored message. "Copy original" copies it byte for byte. Paths, error text and run-together words are unchanged. Find in the conversation opens a folded message that holds a match. Routing notes, provenance chips and links keep working. Historical messages render the same way, and no stored message changes.
- [x] AC-05: Headless captures (headless: true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never) cover a screenshot-shaped payload: about 1,400 characters, run-together words, long absolute paths and an ENOSPC error. They run in the coordinator and on a thread page, in Concise, Normal and Verbose, at a 360 px and a 1280 px window, in light and dark. Before captures use the 1.0.76 behavior; after captures use this branch. Each capture checks the folded height, that no text overflows horizontally, and the exact copy.
- [x] AC-06: Delivery: focused tests, web typecheck and the production build pass. A fresh-context review passes. A PR goes to the PR-resolution owner with exact-head CI. Installed acceptance is confirmed with the release owner on the first release that contains #661 and this change.

## Approach

1. `apps/web/src/studio/workerMessagePresentation.ts`: add an optional `detail` argument. Concise uses a 280-character or 3-line fold and a 160-character lead, Normal keeps today's numbers, and Verbose folds like Normal. It stays pure and verbatim.
2. `apps/web/src/components/studio/WorkerMessageBody.tsx`: add a `detail` prop. Verbose starts open. The rest is unchanged: verbatim excerpt, size, Show full message, Copy original, Find opening.
3. `apps/web/src/components/studio/CoordinatorConversation.tsx`: pass the coordinator's existing `timelineDetail` (a one-line change).
4. `apps/web/src/components/chat/MessagesTimeline.tsx`: in the user-message row, an agent-created message mounts `WorkerMessageBody` with `ctx.timelineDetail`, rendering through the same `UserMessageBody` markdown. The person's prompts keep `CollapsibleUserMessageBody`. The change stays inside the row body; 1011 (#687) is told first.
5. Headless fixture: `apps/web/tests/agent-messages/`, with a vite config, a page mounting the real `WorkerMessageBody` and the timeline row through existing stubs, and a check script.

Rejected:
- re-spacing or summarizing the sender's text, which changes evidence (1043 D-decision);
- agent prose instructions alone, which already exist and are not enforced;
- deleting or rewriting history;
- a CSS line clamp over markdown, which can hide decision sentences and breaks Find.

Risks:
- MessagesTimeline conflicts with #687. Mitigation: a minimal call-site change and a rebase after #687.
- Verbose opening every agent message adds height. That is the Verbose contract.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Follow-up increment, not a reopened 1043 (closed) or 1049 (Files scope, T-09 only) → 1068, owned by the 1043/1049 writer thread.
- D-02 Concise budgets: fold over 280 characters or 3 non-blank lines, lead 160 characters, decision sentence up to 400 characters. Tuned from the screenshot payload at a 360 px window. Revised after the fresh reviews of `57c282f4f2` and `f047ca4fa3`: blank lines do not count, a fold hides at least 100 characters, a near-empty Concise cut takes the whole head when it fits 240 or else cuts at 240, and clipping applies only over the character budget. After the review of `72b8b76174`: bold means a `**` or `__` pair as CommonMark pairs them, so a glob, `**kwargs`, `__dirname` or `2 ** n` never holds a cut back, and no piece starts or ends inside a bold run. After the review of `3ff96f239a`: bold never pairs across list items, table rows, quotes or headings; when bold leaves under half the cut window, the cut falls back to main's, at the cost of one literal `**`, so bold never leaves a lead under half the window.
- D-03 Verbose opens agent messages by default, following "Open every turn, tool call and thought".
### Open
- none

## Tasks

### T-01 Detail-aware presentation
- AC: AC-01, AC-02, AC-04 | Files: apps/web/src/studio/workerMessagePresentation.ts, apps/web/src/studio/workerMessagePresentation.test.ts, apps/web/src/components/studio/WorkerMessageBody.tsx, apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/ProjectWorkspace.test.tsx, apps/web/src/components/studio/ProjectWorkspace.test-fixtures.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/workerMessagePresentation.test.ts apps/web/src/components/studio/ProjectWorkspace.test.tsx

### T-02 Thread page agent messages use the shared presentation
- AC: AC-03, AC-04 | Files: apps/web/src/components/chat/MessagesTimeline.tsx, apps/web/src/components/chat/MessagesTimeline.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/MessagesTimeline.test.tsx apps/web/src/components/chat/UserMessageProvenance.test.tsx

### T-03 Headless before and after captures
- AC: AC-05 | Files: apps/web/tests/agent-messages/index.html, apps/web/tests/agent-messages/main.tsx, apps/web/tests/agent-messages/payloads.ts, apps/web/tests/agent-messages/fixture.css, apps/web/tests/agent-messages/vite.config.ts, apps/web/tests/agent-messages/check.mjs, apps/web/tests/agent-messages/README.md, apps/web/tests/project-workspace/agent-messages-check.mjs, apps/web/tests/project-workspace/mocks.tsx, apps/web/tests/project-workspace/README.md, /Users/antonabyzov/.specwithcode/m4/evidence/1068-concise-agent-messages/ | Test: node apps/web/tests/agent-messages/check.mjs and node apps/web/tests/project-workspace/agent-messages-check.mjs, each with UI_EVIDENCE_DIR set to a new directory. Before captures: the same checks with MEASURE_ONLY=1 against base `204712d71e` (main with #661, without 1068); the installed 1.0.76 before is the screenshot itself.

### T-04 Delivery
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/1068-concise-agent-messages/delivery.md | Test: web typecheck, production build, gh pr checks on the exact head, fresh-context review verdict

### T-05 Verify and close 1068
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: this spec | Test: specweave verify 1068 with focused --cmd lines; fresh-context review subagent; installed acceptance on the release with #661 and this change; specweave complete 1068
