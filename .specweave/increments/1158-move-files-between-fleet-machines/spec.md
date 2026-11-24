# Move files between fleet machines

## Problem

An agent thread on one machine (M1, M3, M4, Ministorm) that needs a file from another machine has no known path. Attachments are local to one machine, folder copy is an app-only RPC, `studio_project_add_to_machine` moves only tracked files, and SSH with the M4 fleet key was refused on purpose. Agents improvise or stop and ask.

Separately, a plain message to the specweave coordinator failed on November 1, 2026 with "The repository path must stay inside an approved project folder." Another session had renamed the app checkout and left a symlink at the old path, so the guard in `ProjectEnvironmentRuntime.ts` refused it. The guard was right; the wording blames a repository path and gives no way out.

## Scope

In: one MCP tool, `studio_file_transfer`, that carries a file over the existing fleet `/mcp` connection in either direction; a rule for rebuild, fetch or send in advance; owner-approved, payload-encrypted secret transfer; agent instructions; a clear folder-changed error.

Out: new grants, or any change to machine or filesystem grants; folders (folder copy owns those); resume across calls; a Settings UI.

## Acceptance Criteria

- [ ] AC-01: `studio_file_transfer {machine, direction, path}` moves one regular file either way, verifies SHA-256, writes atomically, and never overwrites an existing file.
- [ ] AC-02: The caller must hold a ready grant on that machine. With none, the refusal says who can fix it and tells a worker to ask its coordinator to send the file. No grant is created or widened.
- [ ] AC-03: On the receiving machine, paths are limited to folders the grant already covers (covered projects, their approved folders, managed worktrees and scratch, the transfer inbox). Credential locations are always refused. Chunk tools refuse callers that are not another machine's grant.
- [ ] AC-04: A secret-like file (by path, or by content such as a service-account `private_key`) moves only after the owner approves a card naming the file and both machines, and only under a full-access grant. Bytes are encrypted with an X25519 and AES-256-GCM key made for that transfer, limited to 1 MiB, and written with mode 0600.
- [ ] AC-05: File bytes and secrets never reach tool results, thread activity, chat or the MCP trace log.
- [ ] AC-06: The receiving machine's free space is checked first; a refusal names the machine and both sizes. A long transfer returns `running` with a `transferId` that a later call can read.
- [ ] AC-07: Agent instructions and tool descriptions give the rule: rebuild when sources and toolchain are here and it is cheap, otherwise fetch; secrets only through this tool; send files before a launch or a migrate.
- [ ] AC-08: A moved, renamed or symlink-replaced approved folder fails with a message that says so and how to fix it, and the guard still refuses.
- [ ] AC-09: Live: a real file and a test secret move between two real machines on the released build.

## Approach

Reuse: `RemoteStudioMcpClient` (routing Connect then tailnet, DPoP, grant and expiry checks), `workGrantAccess`, `isSecretLikeProjectPath` and `isUntrackedSecretConfigPath`, `MAX_SECRET_FILE_BYTES`, `exposesProtectedRealPath`, `ProjectActionRequests` for the card.

New: `apps/server/src/fleet/fileTransfer/` (pure file, crypto and policy logic plus a service), `apps/server/src/mcp/toolkits/fileTransfer/` (the agent tool and two internal tools, `studio_file_offer` and `studio_file_chunk`, both on `REMOTE_TOOL_ALLOWLIST`). The caller drives every byte, so one grant serves both directions. Chunks are 2 MiB of base64 over `/mcp`.

Rejected: a new HTTP route (a second credential path, and the client refuses to send a grant anywhere but `/mcp`); extending folder copy (operation, manifest and UI built for folders); SSH (refused on purpose).

Risk: Cloudflare terminates TLS on Connect tunnels. Payload encryption hides secrets from a passive relay and logs. It does not authenticate the key exchange against an active relay, because fleet machines hold no pinned public keys for each other. Recorded as a known limit.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Owner approval lives on a card in the calling thread on the calling machine; only a full-access grant may carry a secret.
- D-02 A worker whose machine has no grant back asks its coordinator, which sends the file. Grants stay as they are.
- D-03 Maximum 4 GiB per file, received into `<stateDir>/transfers/<id>/` unless a covered destination is named.
### Open
- none

## Tasks

### T-01 Clear folder-changed error
- AC: AC-08 | Files: packages/contracts/src/projectEnvironment.ts, apps/server/src/project/ProjectEnvironmentRuntime.ts, apps/server/src/project/ProjectEnvironmentService.ts | Test: cd apps/server && pnpm exec vp test run src/project/ProjectEnvironmentRuntime.test.ts src/orchestration-v2/ProviderFailure.test.ts

### T-02 File, crypto and path policy
- AC: AC-01, AC-03, AC-04, AC-06 | Files: apps/server/src/fleet/fileTransfer/ | Test: cd apps/server && pnpm exec vp test run src/fleet/fileTransfer

### T-03 MCP tools and owner card
- AC: AC-02, AC-03, AC-04, AC-05, AC-06 | Files: apps/server/src/mcp/toolkits/fileTransfer/, apps/server/src/fleet/RemoteStudioMcpClient.ts, apps/server/src/project/ProjectActionRequests.ts | Test: cd apps/server && pnpm exec vp test run src/mcp/toolkits/fileTransfer

### T-04 Agent instructions
- AC: AC-07 | Files: apps/server/src/provider/StudioOrchestrationInstructions.ts, docs/internals/agent-instructions.md | Test: cd apps/server && pnpm exec vp test run src/provider/StudioOrchestrationInstructions.test.ts

### T-05 PR, release and live transfer
- AC: AC-09 | Files: none | Test: live transfer receipt between two real machines

### T-06 Verify and close 1158
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: none | Test: specweave verify 1158-move-files-between-fleet-machines
