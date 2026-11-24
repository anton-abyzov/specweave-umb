# 1033 Keep Aide separate from project chats

## Problem
Aide's prompt routes any product-related question to a project coordinator, even when the user only asks to discuss or review it. The supplied screenshot shows Aide's own routing acknowledgement, not evidence of a shared transcript query. General thread-send tools also allow cross-project agents to inject messages into a personal assistant.

## Scope
In: explicit-request routing guidance and provenance, cross-project message delivery guards, focused server regression coverage, headless separation verification, PR and CI. Out: 0981 singleton/machine isolation, settings 1031, releases and installed acceptance owned by the release lane.

## Acceptance Criteria
- [ ] AC-01: Aide's instructions keep ordinary discussion local and distinguish requested reports from requested project task control; routing requires a quote from a real user message.
- [ ] AC-02: Project agents cannot push text or attachments into Aide through generic thread-send tools; Aide cannot bypass explicit routing through those tools. Same-project messages and on-demand reads remain available.
- [ ] AC-03: Focused tests, server build and headless checks pass with durable evidence; fresh-context review finds no unresolved high or critical issues; PR CI is verified.

## Approach
Preserve the predecessor's seven-file patch, update it against current main, and add a shared message-boundary check at MCP text and attachment entrypoints. Keep access and read semantics unchanged. Quote validation proves provenance, not natural-language intent; prompt guidance handles semantic intent. Verify without provider turns or live database access.

## Decisions
### Defaulted
- On-demand reports are read-only pulls by Aide; project agents never push responses into personal threads.
- Keep existing histories intact. No message deletion or migration.
- Release coordination goes to Complete screenshot sessions; source acceptance is distinct from installed acceptance.
### Open
- None.

## Tasks

### T-01 Preserve and finish explicit-request routing
- AC: AC-01 | Files: apps/server/src/mcp/toolkits/project/route.ts, apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/mcp/toolkits/project/route.integration.test.ts, apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/project/ProjectWorkspaceService.test.ts, apps/server/src/project/projectRouting.ts, apps/server/src/project/projectRouting.test.ts | Test: focused routing and project-context tests

### T-02 Guard personal chat message boundaries
- AC: AC-02 | Files: apps/server/src/mcp/personalChatBoundary.ts, apps/server/src/mcp/personalChatBoundary.test.ts, apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/mcp/OrchestratorMcpService.activity.test.ts, apps/server/src/mcp/toolkits/attachment/handlers.ts, apps/server/src/mcp/toolkits/attachment/tools.ts, apps/server/src/mcp/toolkits/attachment/handlers.test.ts | Test: focused MCP message and attachment tests

### T-04 Close alternate project-write paths found in review
- AC: AC-02 | Files: apps/server/src/mcp/OrchestratorMcpService.ts, apps/server/src/mcp/OrchestratorMcpService.activity.test.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/mcp/toolkits/project/handlers.test.ts, apps/server/src/mcp/toolkits/thread/handlers.ts, apps/server/src/mcp/toolkits/thread/tools.ts, apps/server/src/mcp/personalChatBoundary.test.ts | Test: launch, schedule and queued-message boundary regressions

### T-05 Preserve code-project toolkit compatibility
- AC: AC-02 | Files: apps/server/src/mcp/OrchestratorMcpToolkit.integration.test.ts | Test: full MCP toolkit integration regression with both real fixture projects represented in the mock catalog

### T-06 Guard merge-back across personal boundaries
- AC: AC-02 | Files: apps/server/src/mcp/toolkits/thread/handlers.ts, apps/server/src/mcp/toolkits/thread/handlers.test.ts | Test: real toolkit refuses foreign personal parent/source merges and preserves same-project, code-to-code and external-client merges

### T-03 Verify and close 1033
- AC: AC-03 | Files: scripts/studio-verify/aide-chat-separation.mjs, docs/studio/aide-chat-separation.md, CHANGELOG.md, README.md, AGENTS.md | Test: focused tests, server build, headless separation check, fresh-context review, PR CI
