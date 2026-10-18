# Manage MCP servers from the Connections library

## Problem

Settings > Connections in SpecWithCode lists MCP servers across Codex, Claude Code, plugins and other AI tools (PR #351), but the only edits are "Add to" between Codex and Claude Code and "Enable" for a Codex entry. Anton asked (2026-10-18, project thread) to add, remove and turn servers off from the library, across every tool on a machine.

## Scope

In (step 1, one machine, user scope): add a new server to chosen tools; turn a server off and on; remove it; copy it to every tool that can run it; turn a whole plugin off and on; a masked preview before every write; a backup and Undo for every write. Tools: Codex, Claude Code, Claude Desktop, Gemini CLI, Copilot CLI, Cursor, OpenCode, Windsurf.
Out: copying across machines, a Test launch, project-scope writes, a catalog (steps 2 and 3).

## Acceptance Criteria

- [x] AC-01: Adding a server with a command or URL writes a valid entry to each ticked tool's user file in that tool's format, refuses a taken name, and leaves the rest of each file intact.
- [x] AC-02: Turning off a Codex server sets `enabled = false`; turning off a server in a tool without an off switch parks the entry in SpecWithCode's state folder, the library still shows it as Disabled, and turning it on restores it unchanged.
- [x] AC-03: Remove deletes one tool's entry, and "Add to all tools" copies a portable entry to every tool that lacks it and can run it.
- [x] AC-04: Turning a Codex or Claude Code plugin off or on flips its enabled flag and its servers follow.
- [x] AC-05: Every action can be previewed first. The preview names each file and shows the entry with env, header and secret-shaped values masked, and nothing is written.
- [x] AC-06: Every write saves a backup; Undo restores each file only when nobody changed it since, and a file changed since the read is never overwritten.
- [x] AC-07: The library offers each action where it applies, shows the preview before saving, and offers Undo after; verified headless in a private instance.

## Approach

Contracts: `NativeConnectionApplyInput` becomes a union of actions (enable, copy, disable, remove, copyAll, add, plugin, undo) with an optional `preview`; the apply result gains an optional `change` (preview lines and the change id for Undo). Old clients keep sending enable/copy unchanged.
Server: pure text edits per tool format in `NativeConnectionEdit.ts`; orchestration (read, plan, preview, backup, write, undo, parked store) in `NativeConnectionManage.ts` with its file and path helpers passed in, so the new module adds no Node built-in imports. Parked entries and backups live under the server's state dir (`connections/`). Discovery reports parked entries as Disabled.
Web: a row action menu, an Add server form and a confirm dialog with the masked preview, plus an Undo notice.
Risk: `.claude.json` is rewritten by Claude Code; every write rechecks the file text it planned against.

## Open questions

- none

## Tasks

### T-01 Contracts for the manage actions
- AC: AC-05 | Files: packages/contracts/src/nativeConnections.ts | Test: npx vp test run apps/server/src/project/connections

### T-02 Per-tool text edits
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/server/src/project/connections/NativeConnectionEdit.ts, apps/server/src/project/connections/NativeConnectionEdit.test.ts | Test: npx vp test run apps/server/src/project/connections/NativeConnectionEdit.test.ts

### T-03 Manage orchestration, preview, backups, Undo, parked store
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/server/src/project/connections/NativeConnectionManage.ts, apps/server/src/project/connections/NativeConnectionManage.test.ts, apps/server/src/project/connections/NativeConnectionDiscovery.ts | Test: npx vp test run apps/server/src/project/connections

### T-04 Library UI for the actions
- AC: AC-07 | Files: apps/web/src/components/connections/ConnectionMatrix.tsx, apps/web/src/components/connections/ConnectionEditor.tsx, apps/web/src/components/connections/NativeConnectionsPanel.tsx | Test: npx vp test run apps/web/src/components/connections

### T-05 Private-instance check
- AC: AC-07 | Files: reports/connections-library/manage.md | Test: node scratch headless script against a private dev instance
