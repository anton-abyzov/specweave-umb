# Cloud sessions and Linux workers for SpecWithCode

## Problem

SpecWithCode runs every thread on a Mac in the owner's private fleet. When the Macs are asleep, busy or away, work stops. Anthropic now ships cloud sessions (GA September 23, 2026 on Pro, Max and Team) that run Claude Code on Anthropic-hosted VMs at no extra charge beyond plan usage, and the fleet code already supports Linux hosts over Tailscale, but the app has no way to start, follow or bring back a cloud session, and no documented path to pair a Linux VPS. Research and pricing: ~/Projects/github/studio-research-notes/cloud-sessions-2026-10-16.md.

## Scope

In: an Anthropic cloud sessions service in the server that wraps the Claude Code CLI (availability probe, create, follow-up, list, teleport command); MCP tools so a coordinator can send work to the cloud; a Connections card in Settings; `studio_machine_list` reporting the cloud option; a user doc; landing copy that keeps "local by default" and adds "cloud when you want it"; a Linux worker guide and release artifacts as the last task. Out: managed compute we host and bill, self-hosted environment runners (Team-only), reading a cloud session's transcript (Anthropic offers no API), moving an existing local thread to the cloud (the CLI cannot), any change to the hosted relay.

## Acceptance Criteria

- [ ] AC-01: The server reports cloud session availability from the installed Claude Code CLI as one of `ready`, `needs_login`, `unsupported_auth`, `cli_missing`, `cli_too_old`, each with a one-line reason and fix, and never stores or prints a credential.
- [ ] AC-02: `studio_cloud_session_create {task, projectId?, worktreePath?, upload?}` starts `claude --cloud` in the project checkout under a pseudo-terminal, returns the session id and claude.ai/code URL, refuses a checkout whose branch has no pushed upstream unless `upload` is set, and records the session.
- [ ] AC-03: `studio_cloud_session_send {sessionId, message}` queues a follow-up through `claude -p --cloud <id> --output-format json` and returns the CLI's `{ok, url}` or its exact error text.
- [ ] AC-04: `studio_cloud_session_list` and Settings > Connections show recorded sessions with URL, repository, branch, created and last-sent times, and a ready-to-copy `claude --teleport <id>` command; records survive a server restart.
- [ ] AC-05: `studio_machine_list` includes a `cloud` entry carrying the availability status and the tool to call, without changing the existing machine rows.
- [ ] AC-06: A user doc explains cloud sessions, their plan requirements, the one-way nature of teleport and the GitHub push requirement; the landing page keeps local as the default and names cloud as an option.
- [ ] AC-07: A Linux VPS can be paired as a fleet worker: the release workflow publishes Linux x64 and arm64 server archives, and a doc walks through Tailscale, install, `serve --tailscale-serve`, pairing and `studio-fleet.json`.

## Approach

1. `packages/contracts/src/cloudSessions.ts`: availability, record, create/send inputs and results; export from the contracts index and add `cloud` to `OrchestratorMcpMachineListResult`.
2. `apps/server/src/cloudSessions/CloudSessions.ts`: Effect service. Probe runs `claude --version` and `claude auth status` (JSON, fields `loggedIn`, `authMethod`, `subscriptionType` only). Create spawns the CLI through node-pty (the loader in `terminal/NodePtyAdapter.ts`) with `TERM=dumb`, parses the labelled lines `Session ID:` and `View:` with a URL regex fallback, times out at 4 minutes and keeps the raw tail for the error. Send uses `node:child_process` with `--output-format json`. Records live in `<home>/userdata/cloud-sessions.json`, written atomically.
3. `apps/server/src/mcp/toolkits/cloud/{tools,handlers}.ts`: the three tools; register the toolkit where `MachinesToolkit` is registered; `machines/handlers.ts` adds the `cloud` field.
4. `packages/contracts/src/environmentHttp.ts` group `cloudSessions`: GET list, POST create, POST send; `apps/server/src/cloudSessionsHttp.ts` following `studioFleetHttp.ts` (orchestration read scope for list, same-origin check for mutations).
5. `apps/web/src/studio/cloudSessions.ts` (atom and requests) and `apps/web/src/components/settings/CloudSessionsConnections.tsx` rendered from `routes/settings.connections.tsx`.
6. Docs: `docs/user/cloud-sessions.md`; landing copy in the specweave repo docs-site `/code` page.
7. Linux worker: `scripts/release/release.sh` publishes `studio-<ver>-linux-{x64,arm64}.tar.gz`; `docs/user/linux-worker.md`.

Decisions: cloud is a separate record, not a thread, because nothing can read its transcript; a thread pretending to be a cloud session would show an empty timeline. Creation stays CLI-driven rather than the routines `/fire` API because `/fire` needs a token the user makes on the web and a saved prompt per routine. Managed compute is deferred; the research note prices it at $0.25 per worker-hour if it is ever sold.

Risks: the CLI's interactive output format can change; the parser is isolated and unit-tested against captured output. Pro accounts hit the 5-hour window fast with parallel sessions; the card links to claude.ai/settings/usage.

## Open questions

- none

## Tasks

### T-01 Contracts and cloud session service
- AC: AC-01, AC-02, AC-03, AC-04 | Files: packages/contracts/src/cloudSessions.ts, packages/contracts/src/index.ts, apps/server/src/cloudSessions/CloudSessions.ts, apps/server/src/cloudSessions/cliOutput.ts, apps/server/src/cloudSessions/cliOutput.test.ts, apps/server/src/cloudSessions/CloudSessions.test.ts | Test: node node_modules/vite-plus/bin/vp test run apps/server/src/cloudSessions

### T-02 MCP tools and machine list
- AC: AC-02, AC-03, AC-04, AC-05 | Files: packages/contracts/src/orchestratorMcp.ts, apps/server/src/mcp/toolkits/cloud/tools.ts, apps/server/src/mcp/toolkits/cloud/handlers.ts, apps/server/src/mcp/toolkits/machines/handlers.ts, apps/server/src/mcp/toolkits/index.ts | Test: node node_modules/typescript/bin/tsc --noEmit --project apps/server/tsconfig.json

### T-03 HTTP and Settings card
- AC: AC-01, AC-04 | Files: packages/contracts/src/environmentHttp.ts, apps/server/src/cloudSessionsHttp.ts, apps/server/src/server.ts, apps/web/src/studio/cloudSessions.ts, apps/web/src/components/settings/CloudSessionsConnections.tsx, apps/web/src/routes/settings.connections.tsx | Test: node node_modules/typescript/bin/tsc --noEmit --project apps/web/tsconfig.json

### T-04 Docs and landing copy
- AC: AC-06 | Files: docs/user/cloud-sessions.md, docs/README.md, repositories/anton-abyzov/specweave/docs-site/src/pages/code.tsx | Test: npm --prefix repositories/anton-abyzov/specweave/docs-site run build

### T-05 Live verification and PR
- AC: AC-02, AC-03 | Files: reports under .specweave/increments/0926-cloud-sessions/reports | Test: one real cloud session created from a scratch repository through the tool, one follow-up sent, both recorded; PR opened against main and linked

### T-06 Linux worker artifacts and guide
- AC: AC-07 | Files: scripts/release/release.sh, docs/user/linux-worker.md, docs/user/install.md | Test: bash scripts/release/release.sh --dry-run

### T-07 Repair cloud release typechecks
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/scratch/release-1042-cloud-repairs/apps/server/src/cloudSessions/, /Users/antonabyzov/.specwithcode/m4/scratch/release-1042-cloud-repairs/apps/server/src/server.ts, /Users/antonabyzov/.specwithcode/m4/scratch/release-1042-cloud-repairs/apps/server/src/ws.layer-types.ts | Test: focused cloud tests and the supported typecheck gate with no new diagnostics; retain all diagnostic severities
