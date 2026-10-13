# 0905 Studio readable output formatting

## Problem
Usage errors expose raw ISO timestamps in banners and chat. Human-facing prose should consistently show readable dates and structured lists/tables without corrupting source data.

## Scope
Web/desktop display dates in errors, assistant Markdown and structured output; shared provider response guidance; focused regression, coverage, build and headless visual evidence. Preserve transport/storage timestamps, source copying, code, URLs, identifiers and raw diagnostic payloads. October 13 follow-up authorizes compact coordinator messages and release after coordination with the existing 1.0.8 owner; preserve that frozen release and its live install window.

## Acceptance Criteria
- [ ] AC-01: Valid ISO dates in display prose use readable calendar dates and local time with explicit timezone, respecting the 12/24-hour preference. Date-only values retain their calendar date; invalid and ambiguous values are never guessed.
- [ ] AC-02: Assistant paragraphs, lists and tables display dates consistently while code, links, paths, source/copy content, list structure and table alignment remain intact. Tables remain accessible and fit narrow viewports through contained scrolling.
- [ ] AC-03: All providers receive common output guidance covering readable dates, timezone, lists, tables, numbers, units, currencies and unknown data without changing exact machine output.
- [ ] AC-04: Focused regression tests, scoped coverage, relevant production builds, independent review and explicit headless desktop/mobile visual checks pass. Manual UI acceptance is recorded separately before closure.
- [ ] AC-05: Long coordinator user and worker messages show a compact preview with keyboard-accessible expand/collapse and exact full-message copy. Short requests and assistant results remain readable in full; attachments, links and stored content are preserved.

## Approach
Base Studio origin/main 2a66d765a in isolated owned worktrees; existing provider-usability work does not own these files. SpecWeave 3.0.14 equals npm stable; Jev unavailable (no key). Read project hub, current owners and test isolation ADR. Existing Markdown supports GFM lists and tables: retain it, extracting touched logic from oversized files before adding behavior. Pure Intl date formatter runs at presentation boundaries, never storage. Markdown transformation skips literal/code/link material and preserves raw date metadata for copying. Prompts reinforce readable output without guessing timezone/currency. Browser tests headless:true; PWDEBUG=0 and PLAYWRIGHT_HTML_OPEN=never. Node22 runtime with scoped Node24 build tooling only if required.

## Tasks

### T-01 Format display dates and error surfaces
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/lib/displayDates.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/lib/displayDates.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ThreadErrorBanner.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ThreadErrorBanner.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/FailureDetail.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/FailureDetail.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/UsageLimitRecoveryBanner.tsx | Test: focused display-date and error renderer regressions

### T-02 Format Markdown dates and preserve structured output
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/markdown-display-dates.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/markdown-display-dates.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/ChatMarkdown.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/MarkdownTable.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/ChatMarkdown.output.test.tsx | Test: focused Markdown output and existing copy/list regressions

### T-03 Establish shared provider output instructions
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/provider/RuntimeInstructions.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provider/RuntimeInstructions.test.ts | Test: focused runtime and provider instruction regressions

### T-04 Verify integrated formatting
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/web/tests/output-formatting/, repositories/anton-abyzov/specweave-studio/scripts/studio-verify/output-formatting.mjs, .specweave/increments/0905-studio-readable-output-formatting/reports/ | Test: focused coverage, production builds, headless desktop/mobile output checks and independent review

### T-05 Cover coordinator replies, plans and expanded reasoning
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspace.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ProposedPlanCard.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/V2ItemInspector.tsx | Test: focused project workspace and shared Markdown regressions plus production web build

### T-06 Make long coordinator requests readable
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/CoordinatorConversation.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectMessageBody.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectMessageBody.test.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspace.tsx | Test: focused ProjectMessageBody and ProjectWorkspace regression tests

### T-07 Verify and prepare readability release
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/web/tests/output-formatting/, repositories/anton-abyzov/specweave-studio/scripts/studio-verify/output-formatting.mjs, .specweave/increments/0905-studio-readable-output-formatting/reports/ | Test: production builds, scoped coverage and headless desktop/mobile verification including expand/collapse and exact copy

### T-08 Integrate completed changes and release the successor
- AC: AC-04, AC-05 | Files: repositories/anton-abyzov/specweave-studio/.gitignore, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspace.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/CoordinatorConversation.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/MessagesTimeline.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ThreadAutomationsPanel.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/, repositories/anton-abyzov/specweave-studio/scripts/studio-google/verify.mjs, repositories/anton-abyzov/specweave-studio/apps/desktop/package.json, repositories/anton-abyzov/specweave-studio/apps/server/package.json, repositories/anton-abyzov/specweave-studio/apps/web/package.json, repositories/anton-abyzov/specweave-studio/packages/contracts/package.json, repositories/anton-abyzov/specweave-studio/scripts/studio-projects/release-version.test.mjs, .specweave/increments/0905-studio-readable-output-formatting/reports/ | Test: integrated focused regressions, web/server and release builds, compiled Google gate, source/asset publication and installed-version readback after release-owner handover

## Manual UI acceptance
Anton approved the linked compact-message layout on October 13, 2026 and explicitly authorized coordinating the release. Preserve 0904 ownership of frozen 1.0.8; stage the successor in this checkout and publish/install only after the owner handover. 0901 confirmed completed next-batch commits 55272cd0a and 1ec4388ae; its existing owners retain real Google account verification and navigation acceptance.

## Updated browser authorization
On October 13, 2026 Anton granted standing permission for visible browser use when needed for an authorized task, superseding older headless-only copies. Routine tests remain preferably headless. The evidence in this increment was captured headlessly; no visible-browser approval is needed for future authorized follow-up.

### Release source reconciliation — October 13
The shared Studio history was truncated while this lane was interrupted. Original candidate `4b9b94a7a359092f81a13ed311d71b79f4ac3613` maps to current `51c49ab4603c17c87362e9700cd242b24ed83e2e`; both have tree `3f70ed237cfd885acee20cec16afaac9e64a306a`. An independent paired-DAG audit found identical trees for all 1,020 retained commits. Original artifacts and receipts remain preserved. A fresh signed build and runtime package were made and audited against the current source; the update plan admits the actual installed pre-rewrite source IDs for 1.0.7 and 1.0.8.

PR 164 merged normally as `34826e95eea37bf5979452773e6f5c75d6803556`. The frozen release source is its ancestor; the only additional merge-tree change is the previously merged documentation explaining pre-rewrite installed source IDs. T-07 evidence checks the successful fresh build, 512 focused test results, scoped unit coverage, four headless visual cases, and the compiled Google client/navigation gate. Earlier test receipts retain their original source attribution, with exact tree equivalence recorded separately. Publication and installed readback remain T-08.
