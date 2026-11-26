# Live collaboration on sheets, whiteboards, docs, designs and pages

## Problem

SpecWithCode's documents (sheets, whiteboards, docs from 1451, designs, html_render pages) are files on the owner's machines, edited by the owner's windows and by agents. Two writers today collide: a sheet save with a stale revision gets a Conflict banner (reload or keep), there is no presence, no shared comments outside designs, no common version history, and no way to share a document with anyone. Each kind has its own header and controls.

On November 24, 2026 Claude shipped artifacts with Share (invite, org-wide, copy link, always share latest version), comments with "Send to Claude", live presence with Claude's cursor, and shared page data, all hosted on Anthropic's servers. The frame-by-frame read is in `reports/live-collaboration-plan.md`. SpecWithCode needs the same experience without moving documents off the owner's machines.

## Scope

In (this increment, slice C1, no new access): live co-editing of sheets between the owner's own approved windows on the home machine and agents, with presence; agent `sheet_write` edits merge instead of conflicting; the shared document header (kind, title, presence, Comments, Versions, Share showing current access read-only) on sheets; the `.xlsx` and `.sheet.json` round trip unchanged.

Out (later slices, see the plan): whiteboards, docs and designs on the envelope (C2); anchored comments with Send to agent and the version drawer (C2); editing from the owner's other machines and phone through Connect (C3); invites to people outside the owner's account with end-to-end encryption (C4, auth change, owner decision); view links, shared page data and relay-held state (C5, owner decision, possible spend).

## Acceptance Criteria

- [ ] AC-01: Two windows of the same machine open on one sheet see each other's cell edits within one second without reload, and neither shows the Conflict banner.
- [ ] AC-02: An agent `sheet_write` while a window edits the same sheet merges both changes; edits to the same cell resolve to one defined value and both appear in the document's activity.
- [ ] AC-03: Each window shows who else is on the sheet (this machine's windows, agents) with a coloured selection flag on the cell they are on; the presence of an agent appears while its write runs.
- [ ] AC-04: The file on disk after a session opens unchanged in Excel (xlsx) and round-trips through `sheet_read`; merge state lives in a sidecar next to the file that is ignored by other tools and removed with the document.
- [ ] AC-05: Every update is checked on the home machine against the document's access before it merges; a view-only session's update is refused and a test proves both the UI gate and the server refusal.
- [ ] AC-06: The shared header (kind badge, title, presence, Comments, Versions, Share) renders the same on sheets as the design studio's header; Share lists current access read-only.
- [ ] AC-07: No new principal, credential, route, relay change or link is added (reviewed in the PR).

## Approach

- Yjs (MIT) document per open sheet on the home machine: Y.Map per sheet keyed by cell, Y.Array for sheet order, maps for styles and charts. Spike the SheetView mapping first.
- A `DocumentSession` service (per `docs/internals/effect-services.md`) holds open documents, applies updates after the access check, broadcasts updates and awareness over the existing WebSocket RPC, debounces writes back to the plain file and appends to a sidecar update log.
- `sheet_write` becomes a Yjs transaction through the same session.
- New dependency: Yjs (and y-protocols for awareness); add to `THIRD_PARTY_NOTICES.md` and pass the brand audit.
- Rejected: Automerge (heavier, no Tiptap binding), OT (needs an always-on sequencer), a cloud copy of the document (documents stay on the owner's machines).

## Decisions

### Asked
- D-01 Outside the owner's account → named invites (email or Connect account), end-to-end encrypted; comment or view by default, edit only when the owner allows it; expiry and revoke; no public links (owner, November 24, 2026).
- D-02 Relay visibility → end-to-end for people outside the owner's account; the owner's own devices keep today's Connect trust (owner, November 24, 2026).
- D-03 Home machine offline → an encrypted copy is kept on the relay so others keep working; the relay holds ciphertext only. This adds Cloudflare storage cost, accepted (owner, November 24, 2026).
- D-04 Shares to the owner's other machines → a document opens on a machine only where that machine's existing per-machine approval already holds; no fleet-wide approval sharing (owner, November 24, 2026).
### Defaulted (change any before sw-do)
- D-05: Yjs is the merge engine for sheets, whiteboards and docs; designs keep server-ordered operations.
- D-06: The plain file stays canonical; merge state is a sidecar.
### Open
- none (D-01 to D-04 shape C3 to C5; C1 needs none of them)

## Tasks

### T-01 Spike: sheet model to Yjs mapping and back
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/documents/sheetYDoc.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/documents/sheetYDoc.test.ts

### T-02 DocumentSession service with access check, sidecar log and file write-back
- AC: AC-02, AC-04, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/documents/DocumentSession.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/handlers.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/tools.ts, repositories/anton-abyzov/specwithcode/apps/server/src/mcp/toolkits/office/handlers.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/OfficeArtifactService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/documents/DocumentSession.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.documents.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/workspace/WorkspaceFileSystem.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/documents/

### T-03 Live sheet editing and presence in the web client
- AC: AC-01, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/office/useSheetEditor.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetGrid.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/documents/ | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/documents/

### T-04 Shared document header on sheets
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/documents/DocumentHeader.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/documents/DocumentHeader.test.tsx

### T-05 Shared mapping, contracts, RPC wiring and the Yjs dependency
- AC: AC-01, AC-05, AC-07 | Files: repositories/anton-abyzov/specwithcode/packages/shared/src/sheetCollab/, repositories/anton-abyzov/specwithcode/packages/shared/package.json, repositories/anton-abyzov/specwithcode/packages/contracts/src/documentSession.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/rpc.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/index.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/environment.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/rpc/client.ts, repositories/anton-abyzov/specwithcode/apps/server/src/documents/DocumentSessionRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/server.ts, repositories/anton-abyzov/specwithcode/apps/server/src/auth/RpcAuthorization.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/environment/ServerEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetFileView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/office/SheetView.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/index.css, repositories/anton-abyzov/specwithcode/pnpm-workspace.yaml, repositories/anton-abyzov/specwithcode/pnpm-lock.yaml, repositories/anton-abyzov/specwithcode/THIRD_PARTY_NOTICES.md, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/preservation-audit.mjs, repositories/anton-abyzov/specwithcode/scripts/studio-toolchain/reviewed-lock-changes.json | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run packages/shared/src/sheetCollab/ packages/contracts/src/clientRpcPermissions.test.ts

Added while implementing C1: the web client holds a Yjs document too, so the pure sheet mapping lives in the shared package (T-01 keeps the server's file and sidecar side), and the new RPC group, its scopes and the dependency notices need files no other task lists.
