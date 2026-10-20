# Design workspace: artifacts, ownership and agent tools

## Problem

The user wants SpecWithCode to be a studio for designs, design systems and slides that belong to a project and can be reused from code, matching what Claude's desktop app now offers (Design gallery, chat plus canvas, design-system picker) but working with every provider. Today the app has no design artifact at all: a Library artifact is a `hub.json` entry of kind file or link, thread artifacts are parsed from messages, `html_render` pages are one-off attachments, and nothing has versions (research: ~/Projects/github/studio-research-notes/design-workspace-2026-10-20/specwithcode-architecture-map.md, claude-design-inventory.md). Without a shared, owned, versioned document model, the canvas, design systems and slides lanes would each invent their own storage.

## Scope

In: the design document and design-system schemas, their storage (project-owned in the checkout, personal Playground in the app home), autosave revisions and named versions with restore, explicit ownership with copy between Playground and projects, references that survive handoff and linked machines, the model-neutral `design_*` MCP tools, the Design gallery route with sidebar, command palette and Library entry points, and the "Design from code" start that opens an agent thread bound to a design.

Out: the canvas editor tools (0974), design-system extraction and Figma (0973), slides (0975), sharing to other people or publishing anywhere (not requested; export only), real-time multi-user editing.

## Acceptance Criteria

- [ ] AC-01: `packages/contracts` defines `DesignDocument` (schema `swc.design/1`, kind `design` or `slides`, pages, nodes frame/rect/ellipse/line/path/text/image/note/html/component, comments, provenance) and `DesignSystem` (schema `swc.design-system/1`, tokens with per-mode values and file:line provenance, components, sources, review state). Decoding rejects unknown node types and non-finite geometry; a round-trip test covers every node type.
- [ ] AC-02: One pure reducer in `packages/shared` applies design operations (add/update/delete/move node, add/rename/delete/reorder page, set title, set design system, add/resolve comment). The client and server both use it; it never mutates its input and rejects an operation on a missing id with a typed error.
- [ ] AC-03: A project design is stored at `<project root>/.specweave/design/<designId>/design.json`, with assets under `assets/` named by content hash and autosave revisions under `.history/` (ignored by a `.gitignore` the store writes). A Playground design uses the same layout under the app's private home (`<home>/design/playground/`). No design file is written outside those two roots, and paths are resolved through the project's registered root, never from a path the client sends.
- [ ] AC-04: Every write is compare-and-set on `revision` under a file lock and written atomically. A stale write returns a conflict with the current revision; two concurrent writers never lose an edit (test with parallel writers).
- [ ] AC-05: Autosave keeps the last 100 revisions. "Save version" writes a named, immutable version under `versions/` that travels with the repository. Restore makes a new revision from any revision or version; history lists both, newest first.
- [ ] AC-06: Each design and design system records its owner (`project` with environmentId and projectId, or `playground` with environmentId). "Copy to project" and "Copy to Playground" create a new id with `provenance.copiedFrom` (owner, id, revision) and never move or link the source. Copying to a project requires the user to pick the project; agents cannot copy across owners without a user-approved action.
- [ ] AC-07: A thread in project A cannot read or write a design owned by project B or by the Playground through MCP or RPC (server rejection tested), and a Playground thread cannot read project designs. Design systems follow the same rule; using another owner's system requires a copy.
- [ ] AC-08: A design reference stores owner, design id and repository-relative path. It resolves on any linked member of the same logical project (another machine's checkout of the repository) and on the destination after a thread handoff; a missing file shows "Not on this machine yet" with the member that has it, not an error.
- [ ] AC-09: MCP tools `design_list`, `design_get`, `design_create`, `design_apply` (operations with `expectedRevision`), `design_history`, `design_save_version`, `design_restore`, `design_screenshot` (PNG of a page or frame through the existing headless renderer) and `design_system_list`/`design_system_get` work for every provider through the one MCP server. Read-only tools are in the Claude read-only allowlist; every tool has a presentation entry.
- [ ] AC-10: The sidebar shows Design under Assistant. `/design` lists designs with tabs All, Playground and Projects, a project filter, search, grid and list views, and cards with a live thumbnail, kind, owner and "Edited N min ago". The Make something new row shows only kinds that work in this build. The command palette has "Open Design".
- [ ] AC-11: A project's Library shows a Designs group listing that project's designs with open, copy to Playground and reveal file actions.
- [ ] AC-12: "Design from code" asks for the project, creates a design owned by it and starts an agent thread in that project bound to the design (default model: the project's worker model, Claude Opus 5.5 high on this machine), with instructions to use `design_*` tools and the project's design system. No provider-specific code path.
- [ ] AC-13: Headless screenshots (light and dark) of the gallery, the Library Designs group and the Design from code dialog, plus server tests for storage, CAS, history, ownership rejection and reference resolution.

## Approach

Contracts first (`packages/contracts/src/design.ts`, `designRpc.ts`), then the pure reducer and the HTML renderer used for thumbnails, screenshots and export (`packages/shared/src/design/ops.ts`, `render.ts`). Server: `apps/server/src/design/DesignStore.ts` (paths, lock, CAS, atomic write, history pruning), `DesignService.ts` (Effect service, ownership checks), `DesignRpc.ts` bound like `ProjectWorkspaceRpc.ts`, scopes in `clientRpcPermissions.ts`. MCP: `apps/server/src/mcp/toolkits/design/{tools,handlers}.ts` registered in `McpHttpServer.ts`, screenshot through `registerImageTool` and the `HtmlRender` headless path. Web: `apps/web/src/routes/design.tsx`, `components/design/DesignGallery.tsx`, sidebar row in `StudioSidebar.tsx`, palette action in `CommandPalette.tsx`, Library group in `LibraryPane.tsx`.

Storage in the checkout, not the app database: designs belong to the project, travel with Git and folder copy, survive handoff, and are plain files any agent can read. Rejected: a database table (would not travel with the project and needs migration on handoff), and `hub.json` (CLI-owned, no history).

Visual language: the app's existing tokens and `components/ui` primitives; no lock or brain icons (0965 guard). Private is the default and the only state, so cards show the owner, not a lock.

Risk: conflict hotspots with active lanes in `clientRpcPermissions.ts`, `RpcInstrumentation.ts`, `ws.ts` and `__root.tsx` (0966, 0967, 0969). Keep edits additive and rebase before merge.

## Decisions

### Asked
- D-01: Project attachment vs a common playground → both, with explicit ownership and copy (user, October 20, 2026).
### Defaulted (change any before sw-do)
- D-02: No Share button. Export (PNG, HTML, PDF in 0974) replaces it; sharing to people was not requested and would publish content.
- D-03: Copy, never link, across owners, so no project content leaks into another owner by reference.
- D-04: Autosave history lives in `.history/` next to the design and is git-ignored; named versions are committed with the project.
### Open
- none

## Tasks

### T-01 Design contracts and schemas
- AC: AC-01 | Files: packages/contracts/src/design.ts, designRpc.ts, index.ts | Test: packages/contracts design round-trip and rejection tests

### T-02 Shared reducer and renderer
- AC: AC-02 | Files: packages/shared/src/design/ops.ts, render.ts, package exports | Test: reducer and renderer unit tests

### T-03 Design store
- AC: AC-03, AC-04, AC-05 | Files: apps/server/src/design/DesignStore.ts | Test: store tests with temp project roots, parallel writers

### T-04 Ownership, copy and references
- AC: AC-06, AC-07, AC-08 | Files: apps/server/src/design/DesignService.ts, DesignRpc.ts, clientRpcPermissions.ts | Test: service tests incl. cross-owner rejection and linked-member resolution

### T-05 Design MCP tools
- AC: AC-09 | Files: apps/server/src/mcp/toolkits/design/*, McpHttpServer.ts, studioMcpToolPresentation.ts, ClaudeAdapterV2.ts allowlist | Test: handlers tests, core.test.ts, ClaudeAdapterV2 cross-check

### T-06 Design gallery and navigation
- AC: AC-10 | Files: apps/web/src/routes/design.tsx, components/design/DesignGallery.tsx, StudioSidebar.tsx, CommandPalette.tsx | Test: component tests, headless fixture

### T-07 Library Designs group
- AC: AC-11 | Files: apps/web/src/components/studio/shell/LibraryPane.tsx | Test: component test

### T-08 Design from code
- AC: AC-12 | Files: components/design/DesignFromCodeDialog.tsx, server thread start | Test: component and server tests

### T-09 Evidence
- AC: AC-13 | Files: apps/web/tests/design-workspace/*, scripts/studio-verify/design-workspace.mjs | Test: headless Playwright light and dark

### T-10 Verify and close 0972
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
