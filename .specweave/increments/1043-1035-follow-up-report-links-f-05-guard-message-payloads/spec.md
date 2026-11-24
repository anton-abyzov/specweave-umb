# 1043 1035 follow-up: report links, F-05 guard, message payloads

## Problem

Follow-up to 1035 (completed October 23, 2026, PR specwithcode-dev#651, squash `f4ff1b4bc`). Three presentation defects remain on the same surfaces:

1. **F-05 (1039, medium).** `ViewerOverlayRouteGuard` (`apps/web/src/components/ViewerOverlayHost.tsx:312`) closes the focused report only when the pathname changes. A notification for another worker in the same project changes only `?thread=` (and `threadEnvironment`/`checkout`), so the old report stays over the destination. Repro: `/Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1039-adversarial-feature-review/reports/presentation-repro/repro.cjs`, receipt `.../presentation-repro/receipt.json` (`sameProjectNotificationLeavesReportOpen` is non-null).
2. **HTML evidence paths.** Agent HTML reports print evidence as giant inline-code absolute paths (screenshot `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-44c3b3df-ff0a-4dc4-97dc-3c55d65c0920.png`). The iframe bridge honors only http(s) `ui/open-link`, so a local file link cannot open in the app.
3. **Worker payload walls.** In every project's coordinator view, a worker-to-coordinator message renders in full as one block of internal prose: tool objects, repository UUIDs, routing IDs, gates and bare paths (screenshots `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-ed3be36e-5f71-4faf-8f05-56cd310a65a3.png` (specweave) and `/Users/antonabyzov/.specwithcode/m4/userdata/attachments/project-coordinator-1332065e-795b-4f98-91c4-f114917e53f6-b312dc14-1ed4-4993-92d6-dbb4d9f1fedc.png` (EasyChamp)). Concise does not help, and words run together ("exactEXISTINGbackend").

Verified so far: the EasyChamp message's run-together words are already in the sender's own `studio_thread_send` tool-call input (Codex `gpt-6.1-sol`, thread "Complete EasyChamp handoff audit", activity position 2019), so they are generated, not lost in transport or rendering. `CoordinatorConversation.tsx` excludes worker messages from the length fold (`collapsible={... && author !== "Message from a worker"}`), and the report fold needs more than 600 words, 80 lines or 3 headings (`packages/shared/src/threadReport.ts`), so a 1,100-character payload always shows in full. Concise folds only the coordinator's own in-between replies and thinking (`apps/web/src/studio/coordinatorActivity.ts`).

## Scope

In: F-05 route identity guard; labeled evidence links and a guarded file-open bridge for HTML renders; worker-message body presentation in the shared coordinator conversation used by every project; root-cause record for run-together words and uncollapsed payloads; focused tests and headless evidence.

Out: shared Markdown/code styling and language inference (1038); question/answer messages (`async-answer:` ids), question cards and sender provenance (1042); notification eligibility (1036) and counts (1040); held 1011 activity work; EasyChamp business logic or data; rewriting stored messages or historical HTML attachments; merge, release, restart and installed acceptance (Complete screenshot sessions).

## Acceptance Criteria

- [x] AC-01: Explicit navigation that changes the pathname or the project pane's destination (`thread`, `threadEnvironment`, `checkout`) closes the open focused report. Other query preferences, the hash and `restoreThread` do not close it. The 1039 F-05 scenario (same-project notification to another worker) closes the report in a test that drives the real guard.
- [x] AC-02: In newly published HTML reports, explicit anchors whose href is an absolute local path render as compact labeled evidence links with semantic color and hover/focus-visible states, reveal the full path on hover and focus, and copy the exact path. Code strings and plain text are never linkified; http(s) links behave as before.
- [x] AC-03: Activating an evidence link asks the host. The host opens the file in the app only for a request from its own frame, with user activation and frame focus, taking environment and thread from the frame's trusted viewer provenance (never from the payload), through the existing file-open path and its filesystem/grant checks. Forged environment/thread fields, non-path, traversal, control-character or oversized payloads, floods and requests without activation are rejected. The sandbox keeps no `allow-same-origin`.
- [x] AC-04: Worker-to-coordinator messages in every project's coordinator view keep the existing "Sent by" provenance and show a concise verbatim lead. The complete original is one disclosure away, selectable and copyable byte-exact, and the collapsed state says how much is hidden. No text is rewritten. Answer messages, user-authored and routed messages keep their current display. The sentence asking for a decision (a `Blockers:` line, else the first question) stays in the folded view, and conversation find opens a folded message whose hidden part matches.
- [x] AC-05: In the details, code formatting applies only to explicit fences or segments that parse as JSON; JS-object-like text stays prose. Explicit links (Markdown links, `studio://thread` links, thread references the renderer already chips) stay labeled; nothing new is linkified.
- [x] AC-06: `rootcause.md` traces the run-together words and the uncollapsed payload across generation, MCP transport, stored message and renderer with evidence. Any source-side mitigation is minimal and never alters stored or model-visible text.
- [x] AC-07: Headless before/after evidence covers dark and light, 360 and 1280 px, 200% zoom, keyboard-only use and accessible names/states, real navigation and link interactions, and hostile payload rejection. Focused tests, web typecheck and the web production build pass.
- [x] AC-08: A reviewed PR with exact-head CI is delivered to Complete screenshot sessions; installed acceptance stays with that owner; no merge, release or restart from this lane.

## Approach

1. F-05: the guard selects one identity string from the location (pathname plus `thread`, `threadEnvironment`, `checkout`) and closes the active viewer when it changes. Pure helper exported for tests.
2. Evidence links: the publish-time bootstrap marks explicit anchors with absolute local-path hrefs, styles them from the injected theme tokens, adds an accessible full-path reveal and copy control, and posts a separate file-open request; the web host validates source, focus, activation and the path, then calls `openFileInFront` with the frame's own `threadRef`. Exact design follows the Fable bridge-security research (T-01).
3. Worker payloads: a pure presentation helper in a new module (not `projectCoordinatorMessageDisplay.ts`, which 1042 edits) computes the verbatim lead and fold decision; a `WorkerMessageBody` component in the coordinator conversation's worker branch renders lead, disclosure, original and exact copy through the existing renderer. Exact thresholds and never-hide rule follow the Fable payload research (T-01).
4. Evidence: extend the report-experience fixture and add a coordinator-message fixture; headless captures and interaction checks to `/Users/antonabyzov/.specwithcode/m4/evidence/1043-report-links-payloads/`.

Rejected: auto-linkifying code strings or bare paths (unsafe, owned by 1038 styling); rewriting messages with a model summary (semantic change); a new message contract field before research shows the existing data cannot carry the default view.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Base: #651 was squash-merged, so the retained branch was forward-merged with `origin/main` (`ce6670c0f`, tree equal to `2e95e09ae`). No rebase, no new branch.
- D-02 Ownership: 1043 owns the non-answer worker body; 1042 owns `async-answer:` messages, question cards and sender provenance; 1038 owns shared Markdown/code styling. Whoever lands second rebases.
- D-03 Stored HTML reports keep their publish-time bootstrap; new link behavior applies to newly published reports.
- D-04 Main implementation on native Claude Code Opus 5.5 Ultracode; hardest research on Claude Fable 5.1; no substitutes.
- D-05 Worker messages fold above 600 characters or 8 lines, the thread page's thresholds. This supersedes the October 17 rule that a worker's direct answer shows whole: a long answer now opens with its lead and decision sentence. A message whose excerpt would be at least 80% of the text stays whole.
- D-06 Evidence links open from the focused reader only: the inline preview is `inert`, so it cannot take clicks. The file opens in the reader's linked pane with Back. The host accepts one file request per 400 ms.
- D-07 Network (UNC) paths are never evidence links: opening one makes the machine connect and sign in to a host the page chose. In reports published before this change, only same-server links under a filesystem root (`/Users`, `/home`, `/tmp` and similar) open as files, at the same pace.
### Open
- none

## Tasks

### T-01 Research and root cause
- AC: AC-06 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/1043-report-links-payloads/research/bridge-security.md, /Users/antonabyzov/.specwithcode/m4/evidence/1043-report-links-payloads/research/payload-presentation.md, /Users/antonabyzov/.specwithcode/m4/evidence/1043-report-links-payloads/rootcause.md | Test: findings files exist with file:line citations; root cause cites the sender tool-call input, stored text and renderer branch

### T-02 Close the focused report on semantic navigation (F-05)
- AC: AC-01 | Files: apps/web/src/components/ViewerOverlayHost.tsx, apps/web/src/components/ViewerOverlayRouteGuard.test.tsx | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/components/ViewerOverlayRouteGuard.test.tsx

### T-03 Labeled evidence links and guarded file opening in HTML reports
- AC: AC-02, AC-03 | Files: packages/shared/src/htmlRender.ts, packages/shared/src/htmlRender.test.ts, apps/web/src/components/files/BrowserDocumentFrame.tsx, apps/web/src/components/files/BrowserDocumentFrame.bridge.test.tsx, apps/web/src/components/chat/HtmlRenderFrame.tsx, apps/web/src/components/chat/MessagesTimeline.tsx, docs/reports/report-experience.md | Test: node node_modules/vite-plus/bin/vp test run packages/shared/src/htmlRender.test.ts apps/web/src/components/files/BrowserDocumentFrame.bridge.test.tsx

### T-04 Concise worker messages with exact original details
- AC: AC-04, AC-05 | Files: apps/web/src/studio/workerMessagePresentation.ts, apps/web/src/studio/workerMessagePresentation.test.ts, apps/web/src/components/studio/WorkerMessageBody.tsx, apps/web/src/components/studio/CoordinatorConversation.tsx, apps/web/src/components/studio/ProjectWorkspace.test.tsx, apps/web/src/hooks/useCopyToClipboard.ts | Test: node node_modules/vite-plus/bin/vp test run apps/web/src/studio/workerMessagePresentation.test.ts apps/web/src/components/studio/ProjectWorkspace.test.tsx

### T-05 Headless interaction and visual evidence
- AC: AC-07 | Files: apps/web/tests/report-experience/evidence.html, apps/web/tests/report-experience/evidence-check.mjs, apps/web/tests/report-experience/main.tsx, apps/web/tests/report-experience/stubs.ts, apps/web/tests/report-experience/vite.config.ts, apps/web/tests/project-workspace/mocks.tsx, apps/web/tests/project-workspace/worker-message-check.mjs, /Users/antonabyzov/.specwithcode/m4/evidence/1043-report-links-payloads | Test: headless `evidence-check.mjs` and `worker-message-check.mjs` (headless: true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never), web typecheck and web production build

### T-06 PR with exact-head CI and review, handed to the integration owner
- AC: AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/1043-report-links-payloads/delivery.md | Test: gh pr checks on the exact head; fresh-context review verdict; no merge or release from this lane

### T-07 Verify and close 1043
- AC: AC-08 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1043-1035-follow-up-report-links-f-05-guard-message-payloads/spec.md | Test: specweave verify 1043; fresh-context review subagent; specweave complete 1043

Implementation paths are relative to the bound worktree `/Users/antonabyzov/.specwithcode/m4/worktrees/report-experience-1035`.
