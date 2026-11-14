# Reports stay in SpecWithCode: no provider artifact links in replies

## Problem

On November 13, 2026 a SpecWithCode worker ("Finish parallel Claude desktop sessions", Opus 5.5 on M4) ended its Blockers paragraph with `[Before the move to the M5](https://claude.ai/artifact/KMQWxSYB5N7EAJ9Fez58iT)`. The reply showed Claude's asterisk favicon and a blue link that opens claude.ai in the browser, private to the Claude account that made it. Anton: "Why do we have links in our response to the artifacts of Claude Code? ... we must have our own reports created and artifacts."

Why it happens, at each layer:

- Agents copy provider links. The worker read a Claude desktop session's transcript; that session had published its report to claude.ai. Nothing in SpecWithCode's runtime instructions says where a document lives, so the worker passed the URL through.
- Claude sessions in SpecWithCode can publish provider-hosted pages themselves. Claude Code's native `Artifact` tool and the claude.ai Docs connector (`mcp__claude_ai_Claude_Docs__*`) are both attached; the connector's instructions call a claude.ai doc "the default for any document ... report". The app even lists those pages on the thread shelf as "Published to claude.ai" (`apps/web/src/nativeArtifacts.ts`, 1.0.77).
- The renderer treats them as ordinary links: `ChatMarkdown.tsx` `MarkdownLinkFavicon` fetches the host favicon, so a claude.ai link looks like a first-class, branded document.
- There is no tool to bring an outside document in: `saveThreadReport` (`apps/server/src/project/ThreadReports.ts`) only saves a thread's own reply.

## Scope

In:

- A reports rule in the runtime instructions every provider receives.
- SpecWithCode Claude sessions cannot publish provider-hosted documents (native `Artifact`, claude.ai Docs write tools); read tools stay so imports work.
- A `studio_report_save` MCP tool that saves Markdown as a SpecWithCode report in the right increment, with quiet provenance for imports.
- An outside-document chip for provider-hosted links that still reach a reply.
- Importing the "Before the move to the M5" document as the live proof.

Out:

- Rewriting messages already stored.
- Removing the existing "Published to claude.ai" shelf entries of old threads (they stay readable as references).
- HTML imports (pages stay `html_render`), iOS and Android renderers, a hosted share link.

## Acceptance Criteria

- [ ] AC-01: Every provider's runtime instructions say that documents an agent makes or cites live in SpecWithCode: saved as reports (`studio_report_save`, or a Markdown file in the increment's `reports/`) and linked by local path, never published to or linked as a provider-hosted page; a document another tool made is imported first with its source recorded. The instructions stay within their length cap.
- [ ] AC-02: A SpecWithCode Claude session has Claude Code's `Artifact` tool and the claude.ai Docs connector's write tools (`batch`, `update`, `create`, `delete`) in `disallowedTools`; its read tools are not disallowed, and a caller's own disallowed tools are kept.
- [ ] AC-03: `studio_report_save` saves Markdown into the calling thread's project: the named increment's `reports/`, else the thread's increment, else `.specweave/reports/threads/`. The file has frontmatter `title`, `thread`, `increment`, `savedAt`, and for an import `source` and `original`. Saving the same text again returns the same file. It refuses an empty or over-512-KiB body, a non-https original, an unknown increment and a project without `.specweave`, and returns the absolute path and a ready Markdown link.
- [ ] AC-04: In a reply, a link to a provider-hosted page (claude.ai artifacts, docs, chats and shares; ChatGPT and Codex shares, canvases and tasks; Gemini shares; Cursor agents; Devin sessions) renders as an outside-document chip: a document glyph, its label and a muted "outside · Claude" tag, never the provider favicon. Its tip says where it lives and who can open it; clicking offers "Save to this project" (drafts the import request into this thread's composer), "Open in Claude" and "Copy link". Every other link renders as before. Light and dark.
- [ ] AC-05: "Before the move to the M5" is saved as a SpecWithCode report under `.specweave/reports/threads/` with its claude.ai origin in the frontmatter, opens in the app's document viewer, and the M5 thread has the local link.

## Approach

UX chosen (see Decisions): one home for documents, the project's reports. A reply links the saved file, which opens in the app's own document viewer (property table, outline rail, clickable local links) and lists on the Artifacts shelf and in the Library, for every provider and machine. Provenance is a frontmatter property (Source, Original), not a logo in the reply.

1. `apps/server/src/provider/RuntimeInstructions.ts`: add one reports line to `STUDIO_PRESENTATION_INSTRUCTIONS` (both response styles, every provider, Pi through its extension). Keep under the test's cap.
2. `apps/server/src/provider/ClaudeWorkflowPolicy.ts`: always merge `CLAUDE_PROVIDER_HOSTED_DOCUMENT_TOOLS` into `disallowedTools`. Exact names, not the server prefix, so the connector's `read`, `query`, `export` and `guide` remain for imports.
3. `apps/server/src/project/ThreadReports.ts`: new `saveReport` takes `title`, `increment` and `provenance` options, merges the text's own flat front matter into one block, and returns the saved file; `saveThreadReport` wraps it. `ThreadReportService.saveForThread` scopes it to the calling thread's project. New toolkit `apps/server/src/mcp/toolkits/report/` (`tools.ts`, `handlers.ts`) registered in `McpHttpServer.ts`, presented in `packages/shared/src/studioMcpToolPresentation.ts` and `packages/client-runtime/src/studioToolSummary.ts` ("Saved a report"). Writes as the caller (`Access.writes`), scoped to the calling thread's project.
4. `apps/web/src/providerHostedDocument.ts` recognizes provider-hosted pages by host and path (only document, chat, share, task and session paths; `claude.ai/chrome` and other product pages stay ordinary links). `ChatMarkdown.tsx`'s anchor renders `OutsideDocumentLink` for them before the generic external link. The menu uses the app's `Menu` primitive so it works in the browser client too; "Save to this project" uses `useComposerDraftStore.setPrompt` on the thread's composer and is hidden where there is no thread.
5. Live proof: read the claude.ai doc with the connector's read tool, save it with the new tool's code path (no increment, so `.specweave/reports/threads/`), link it to the M5 thread.

Rejected: rewriting provider links server-side (the app cannot read a private claude.ai page; only the agent's connector can); dropping the link entirely (loses the only copy); disallowing the whole claude.ai Docs server (blocks imports); a Settings switch to allow publishing (no one asked; reversible later).

Risks: a user who explicitly wants a claude.ai artifact now gets a refusal from the tool; they can still publish from Claude desktop. Claude Docs tool names may change; the list is exact and tested, and unknown future write tools fall back to the prompt rule.

## Decisions

### Asked
- none (Anton's direction in the request: our own reports, our viewer, quiet provenance, no outbound provider links)
### Defaulted (change any before sw-do)
- D-01 Outside links that still arrive keep a way to the original (menu "Open in Claude") but never as the primary click → chip plus menu (reversible).
- D-02 Publishing to provider-hosted pages is off in SpecWithCode Claude sessions with no setting → disallowedTools (reversible).
- D-03 Imports are Markdown only; HTML pages stay `html_render` → (reversible).
### Open
- none

## Tasks

### T-01 Reports rule in every provider's runtime instructions
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/RuntimeInstructions.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/RuntimeInstructions.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/provider/RuntimeInstructions.test.ts src/provider/CodexDeveloperInstructions.test.ts

### T-02 Claude sessions cannot publish provider-hosted documents
- AC: AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/ClaudeWorkflowPolicy.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/provider/ClaudeWorkflowPolicy.test.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/provider/ClaudeWorkflowPolicy.test.ts

### T-03 studio_report_save saves and imports reports
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadReports.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadReports.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ThreadReportService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/report/tools.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/report/handlers.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/report/handlers.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/studioMcpToolPresentation.ts, repositories/anton-abyzov/specwithcode-dev/packages/client-runtime/src/studioToolSummary.ts | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ThreadReports.test.ts src/mcp/toolkits/report/handlers.test.ts

### T-04 Outside-document chip for provider-hosted links
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/providerHostedDocument.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/providerHostedDocument.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/OutsideDocumentLink.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/OutsideDocumentLink.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatMarkdown.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/ChatMarkdown.test.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/studio/shell/shell.css, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/outside-document/, repositories/anton-abyzov/specwithcode-dev/scripts/studio-verify/outside-document.mjs | Test: cd repositories/anton-abyzov/specwithcode-dev/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/providerHostedDocument.test.ts src/components/chat/OutsideDocumentLink.test.tsx src/components/ChatMarkdown.test.tsx

### T-05 Import "Before the move to the M5" as the live proof
- AC: AC-05 | Files: .specweave/reports/threads/, .specweave/increments/1320-reports-stay-in-specwithcode-no-provider-artifact-links-in-replies/reports/ | Test: grep -l 'original: "https://claude.ai/artifact/KMQWxSYB5N7EAJ9Fez58iT"' .specweave/reports/threads/*.md

### T-06 Verify and close 1320
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: .specweave/increments/1320-reports-stay-in-specwithcode-no-provider-artifact-links-in-replies/reports/ | Test: specweave verify 1320-reports-stay-in-specwithcode-no-provider-artifact-links-in-replies
