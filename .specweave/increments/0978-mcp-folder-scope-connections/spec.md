# MCP connections: folder-only Claude entries, labels and exposure

## Problem

Settings > Connections groups some rows as "Private projects only" with text like "Private project auxo-penn-mutual-vb6-react-app". These are Claude Code local-scope MCP servers stored per folder under `projects.<path>.mcpServers` in `~/.claude.json`: they are private to the user and Claude Code loads them only when it runs in that exact folder. They are not SpecWithCode projects and nothing about them is shared. The label reads as if private projects were exposed, it names client folders, and it does not say what the entry does or which agents get it. The user asked on October 20, 2026 what this means and how to handle it properly.

## Scope

In: the label and explanation for folder-scoped Claude entries (`apps/web/src/components/connections/ConnectionMatrix.tsx`), what the inventory payload carries for them (`apps/server/src/project/connections/NativeConnectionDiscovery.ts`), who can read it across paired and linked machines, and that agents only ever see entries for their own folder (`apps/server/src/mcp/toolkits/projectConnections/`).

Out: editing `~/.claude.json`, moving or copying entries between scopes.

## Acceptance Criteria

- [ ] AC-01: The group and rows say what the entry is in plain words: for example the group "Only in one folder (Claude Code)" and a row "Claude Code, only in <folder name>", with a one-line note that Claude Code loads it only in that folder, other folders, projects and providers do not get it, and it is stored in the user's `~/.claude.json`. "Private project" no longer appears for these rows.
- [ ] AC-02: The inventory never carries headers, env values, tokens, args with secrets or full home paths for any entry; folder entries carry only the folder's base name, transport and server name. Test with a fixture holding a header token and an env secret.
- [ ] AC-03: An agent's connection tools (`studio_project_connections_list` and friends) list only entries that apply to the calling thread's own workspace folder; another folder's local entries are never listed to an agent. Test with two folders.
- [ ] AC-04: Viewing another machine's inventory (the machine picker) needs the same scope as reading that machine's settings; a client without it sees counts only. Test over RPC.
- [ ] AC-05: Headless screenshots of the renamed group, light and dark.

## Tasks

### T-01 Audit exposure
- AC: AC-02, AC-03, AC-04 | Files: NativeConnectionDiscovery.ts, projectConnections toolkit, connections RPC | Test: server tests
### T-02 Labels and explanation
- AC: AC-01 | Files: ConnectionMatrix.tsx | Test: component test
### T-03 Evidence
- AC: AC-05 | Files: apps/web tests | Test: headless screenshots
### T-04 Verify and close 0978
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
