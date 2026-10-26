# Project knowledge with automatic search mode

## Problem

Claude Projects keep project knowledge in context while it fits and switch on their own to a search tool when it approaches the context window, which Anthropic says expands capacity up to ten times. SpecWithCode threads receive only `MEMORY.md` and the names of other memory files. Memory details and the project Library (hub artifacts, reports, increments, docs) reach agents only when an agent goes looking, and large projects such as the umbrella (about 43 MB of markdown under `.specweave`) have no way to retrieve the right passage. The owner asked for the Claude behaviour reimplemented, investigated with REA, so that big projects work automatically (thread "RAG for large projects", 2026-10-17; "pull all the latest changes, consolidate it, and complete the job", 2026-10-20).

## Scope

In: a per-project knowledge index over project memory, hub file artifacts and Library folder text files; the inline/search switching rule with hysteresis; delivery through the project context snapshot; two read-only MCP tools; RPCs and a settings card; deletion and orphan cleanup; the design document. Out: embeddings, per-turn excerpts, uploads and PDF/Office/Drive extraction, per-thread allowances, cross-machine knowledge, and any release (another thread owns releases).

## Acceptance Criteria

- [ ] AC-01: Project memory files except `MEMORY.md`, hub file artifacts with a text extension and `.md/.mdx/.markdown/.txt` files under the four Library folders are indexed; paths stay inside the workspace by real path, symlinks are refused, files over 2 MiB or past 20,000 documents / 64 MiB are left out and counted, and only new or changed documents are re-read.
- [ ] AC-02: A project is inline while its rendered knowledge fits 24,000 characters, switches to search mode above that and back to inline only at or below 19,200; the mode is per project and survives a restart.
- [ ] AC-03: The index is a separate SQLite FTS5 file per project at `<stateDir>/knowledge/v1/<sha256(projectId)>.sqlite`, never `statev2.sqlite`, written in batches of at most 200 chunks, registered with the live-database guard, and rebuilt when missing or damaged.
- [ ] AC-04: Inline mode delivers one fenced, delta-tracked section per document after the shared sections; search mode delivers a catalog without counts, sizes or timestamps; workers are told to search and the coordinator to point workers at knowledge; no file is read inside the receipt transaction.
- [ ] AC-05: Agents call `studio_project_knowledge_search` and `studio_project_knowledge_read`, read-only and bound to their own project; results default to 8, cap at 20, two chunks per document and 16,000 characters of text; reads page at 16,000 characters.
- [ ] AC-06: Project settings, Memory tab, shows a Project knowledge card with the mode, a usage bar, size, index state, what was left out, a search field and Rebuild index for people who may operate the project; older hosts show an update notice.
- [ ] AC-07: Search never passes raw text to MATCH; identifiers such as `AC-01` and increment numbers match as phrases; ranking is bm25 over title, heading and body.
- [ ] AC-08: Deleting a project deletes its index file; a startup sweep removes files whose project no longer exists.
- [ ] AC-09: The design is documented in `docs/studio/project-knowledge.md`, and the change merges to specwithcode-dev main with every required check green.

## Approach

Design: `repositories/anton-abyzov/specweave-studio` is the umbrella name for specwithcode-dev; the change lives on branch `feat/project-knowledge-rag` there. The design document `docs/studio/project-knowledge.md` records the REA findings about Claude Projects (server-owned `kb/stats`, server-defined `project_knowledge_search` tool, capacity bar rules), the budget rule `B = 0.15 × (E − O − P)` behind the 24,000-character allowance, the storage choice (per-project FTS5 file, not `statev2`) with its measurements, and what is deliberately left out. Research inputs are in `reports/research/` (git-ignored).

Server: `apps/server/src/project/knowledge/` holds the chunker, query builder, source scan, index file and the `ProjectKnowledge` service. `ProjectWorkspaceService.contextSnapshot` appends knowledge sections from the service's in-memory view; `ProjectContextDelivery.prepare` waits for readiness outside its transaction. A new `projectKnowledge` MCP toolkit follows `projectMemory`. Contracts gain `projectKnowledge.ts` and three RPCs.

Web: `ProjectKnowledge.tsx` in the Memory tab, a pure model file, settings search row, client-runtime atoms.

Risks: main-thread indexing stalls (bounded by 200-chunk batches and yields); Claude restore hooks may truncate long context (knowledge sections come last); disk use on large projects (caps, one file per project).

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Mode is per project, as in Claude Projects; a per-thread allowance waits for a session-free window lookup.
- D-02 Inline allowance 24,000 characters, return at 19,200.
- D-03 Local FTS5 only; embeddings later and opt-in, since remote embedding sends project text off the machine.
- D-04 No text pushed into every prompt; search is a tool, as in Claude Projects.
- D-05 Library folders are knowledge by default; the working tree is not.
- D-06 Indexing runs on the main thread in 200-chunk batches; a worker thread follows if profiling calls for it.
- D-07 No release from this thread; another thread owns releases and installs.
### Open
- none

## Tasks

### T-01 Knowledge index, sources and switching rule
- AC: AC-01, AC-02, AC-03, AC-07 | Files: apps/server/src/project/knowledge/*.ts, packages/contracts/src/projectKnowledge.ts, packages/contracts/src/environment.ts, apps/server/src/environment/ServerEnvironment.ts | Test: vp test run apps/server/src/project/knowledge

### T-02 Delivery through the project context
- AC: AC-04 | Files: apps/server/src/project/ProjectWorkspaceService.ts, apps/server/src/project/ProjectContextDelivery.ts, apps/server/src/project/ProjectContextSnapshot.ts, apps/server/src/project/ProjectContextRuntime.ts, apps/server/src/project/knowledge/knowledgeSections.ts, apps/server/src/project/promptFence.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts | Test: vp test run apps/server/src/project/ProjectContextBudget.test.ts apps/server/src/project/ProjectContextDelivery.test.ts apps/server/src/project/ProjectWorkspaceService.test.ts apps/server/src/project/knowledge

### T-03 Agent search and read tools
- AC: AC-05 | Files: apps/server/src/mcp/toolkits/projectKnowledge/*, apps/server/src/mcp/McpHttpServer.ts, apps/server/src/orchestration-v2/runtimeLayer.ts, packages/shared/src/studioMcpToolPresentation.ts, packages/client-runtime/src/studioToolSummary.ts, packages/client-runtime/src/work-log/presentation.ts | Test: vp test run apps/server/src/mcp/toolkits/projectKnowledge apps/server/src/mcp/toolkits/core.test.ts

### T-04 RPCs and the Project knowledge card
- AC: AC-06 | Files: packages/contracts/src/projectWorkspaceRpc.ts, packages/contracts/src/rpc.ts, packages/contracts/src/clientRpcPermissions.ts, apps/server/src/project/ProjectWorkspaceRpc.ts, apps/server/src/auth/RpcAuthorization.ts, apps/server/src/ws.ts, apps/server/src/observability/RpcInstrumentation.ts, packages/client-runtime/src/state/projectWorkspace.ts, apps/web/src/components/studio/ProjectKnowledge.tsx, apps/web/src/studio/projectKnowledgeModel.ts, apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, apps/web/src/components/studio/projectSettingsSearch.logic.ts, apps/web/src/components/studio/projectWorkspace.css, apps/web/tests/project-workspace/* | Test: vp test run apps/web/src/components/studio/ProjectKnowledge.test.tsx packages/contracts/src/projectKnowledge.test.ts

### T-05 Deletion and orphan cleanup
- AC: AC-08 | Files: apps/server/src/project/knowledge/ProjectKnowledge.ts | Test: vp test run apps/server/src/project/knowledge

### T-06 Design document, review and merge
- AC: AC-09 | Files: docs/studio/project-knowledge.md, docs/studio/project-orchestration.md, docs/operations/live-database.md | Test: gh pr checks on the specwithcode-dev pull request

### T-07 Verify and close 0927
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: .specweave/increments/0927-project-knowledge-retrieval/ledger.jsonl | Test: specweave verify 0927
