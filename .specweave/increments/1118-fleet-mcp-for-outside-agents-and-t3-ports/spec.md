# Fleet MCP for outside agents and T3 ports

## Problem

Theo showed three T3 Code features on 2026-10-26..28 (X posts 2115386654..., 2115398275385921844, 2115409288432906341):
Day 27 in-app "triage" (clone the exact source version, playbook, cut an issue), Day 28 one thread starting
subagents on other machines after an agent-requested "Link a machine" consent, and Day 29 an outside chat bot
driving the whole fleet through one MCP server ("which computers can you reach", "spin up a Haiku thread on
each and report disk/RAM"), with the new threads badged "From <client> · <machine>".

SpecWithCode already has an OAuth 2.1 MCP server at `/mcp` (DCR, PKCE, pairing-code approval, DPoP), reachable
publicly over the Connect tunnel, plus a fleet with work grants and remote launch. The demos still fail for us:

- An outside client (ChatGPT connector, Claude.ai connector, a bot) is refused on every cross-machine call
  (`remote.ts` requireThreadCaller, `remoteLaunch.ts`), and `studio_machine_list` does not probe for it.
- Clients that can only send a static `Authorization` header (Grok/xAI remote MCP, OpenAI Responses `mcp`
  tool, n8n, bots) cannot authenticate at all: no MCP client token can be minted outside OAuth.
- Remote launches require a project already on the target; there is no projectless remote launch and no way to
  get a repo cloned there. Provisioning checks `gh auth status` but never sets up a git credential helper, so a
  machine can show "signed in" and still fail `git clone` of a private repo; SSH-refused clones never retry HTTPS.
- Threads carry no origin, so nothing shows which client or machine started them.
- There is no multi-thread wait, so "start one per machine and collect results" needs N separate waits.
- No outside-agents guide; Copy MCP URL is not route-aware; triage reports the CLI version instead of the
  running server's, references a placeholder host, and the `via-triage` label is missing on the public repo.

Evidence: gap map at reports/gap-map.md (6 readers + critic, spot-checked file:line).

## Scope

In: outside-agent docs; route-aware MCP URL; upstream MCP/triage/clone fixes; provision credential helper;
static MCP client tokens; outside OAuth/static clients doing fleet work on linked machines within their access;
projectless remote launch; multi-thread wait; thread origin + header badge; remote clone forwarding;
black-box verification.

Out (later increments, see reports/gap-map.md): agent-requested link card and two-step Link a machine modal,
read-only worker tier, Lineage rows for remote children, in-app triage palette command and DesktopCliShim,
OAuth refresh tokens, Guest links, boring-sidebar polish, upstream PeerLinks pairing to non-fleet machines.

## Acceptance Criteria

- [ ] AC-01: docs/user/outside-agents.md explains connecting Claude Code, Codex, ChatGPT, Claude.ai, Grok/OpenAI Responses and bots, and agent refusals point at the right settings page.
- [ ] AC-02: Copy MCP URL picks the route this device is connected over and offers the public Connect MCP URL when one exists.
- [ ] AC-03: Upstream MCP fixes are in: optional tool parameters accept null.
- [ ] AC-04: `triage` reports the running server's version, falls back to main when the tag is not on the public repo, has no placeholder host, and the public mirror ensures the via-triage label.
- [ ] AC-05: Clones retry over HTTPS when the SSH key is refused, copy-to-machine clones the fork, and `[blob:none]` remotes are recognised.
- [ ] AC-06: Provisioning detects a missing git credential helper and runs `gh auth setup-git` when gh is signed in, and readiness reports it.
- [ ] AC-07: `auth mcp-token create --access <level> --label <name> [--ttl]` mints a revocable MCP client token that `/mcp` accepts as a bearer; it is listed and revocable like other MCP clients.
- [ ] AC-08: An outside MCP client (OAuth or static token) can list machines with reachability and models, and launch, read, send to, wait on and interrupt threads on fleet machines, never above its own access or the machine grant.
- [ ] AC-09: A remote launch with no project starts a scratch thread on the target machine.
- [ ] AC-10: `studio_threads_wait` waits on several local or remote threads (any/all, timeout) and returns each one's status and last reply.
- [ ] AC-11: Threads started by an outside client or another machine record an origin and show a "From <client> · <machine>" header badge.
- [ ] AC-12: An agent or outside client can ask a fleet machine (with an all-projects grant) to clone a repo, then launch there.
- [ ] AC-13: A headless black-box run against an isolated server: no-token 401, static token, tools/list, machine list, multi-wait, revoke then 401.

## Approach

Build on our fleet/work-grant stack rather than porting upstream PeerLinks wholesale (that would add a second
cross-machine path with its own storage and access model). Port upstream fixes by design, not cherry-pick, since
the orchestrator has diverged by tens of thousands of lines. MIT provenance kept.

Outside-client principal: `requireThreadCaller` becomes `requireFleetPrincipal`, accepting a thread caller or an
MCP client session (OAuth or static). Effective ceiling = min(client access, machine grant runtime cap). Client
launches have no reportBack (polling/wait only). Hop/cycle checks stay in `assertGrantMayReach`.
Full-access semantics stay strict: grants change only threads they started.

Static token: reuse `issueMcpClientSession` with subject MCP_CLIENT_SUBJECT, label, access, TTL (default 30d),
listed with OAuth clients and revoked the same way.

Owner gate: AC-07, AC-08 and AC-12 change who may run work on a machine (auth). Ship behind a PR; Anton accepts
manually before release.

## Decisions

### Asked
- D-01 Implement now? → yes, user asked "plan and implement this properly" (2026-10-28).
### Defaulted (change any before sw-do)
- D-02 Extend our fleet grants instead of porting upstream PeerLinks → default (reversible).
- D-03 Full-access links still change only threads they started (stricter than Theo) → default.
- D-04 Static MCP tokens default to 30-day TTL, auto access ceiling unless --access given → default.
- D-05 Guest links, boring sidebar, link-consent card: later increments → default.
- D-06 The black-box check does not start a real thread (it would spend paid provider usage on the Mac's real logins); launch paths are covered by remoteLaunch/RemoteWorkers unit tests → default.
### Open
- none

## Tasks

### T-01 Outside-agents guide and settings-path fix
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/docs/user/outside-agents.md, repositories/anton-abyzov/specweave-studio/docs/user/remote-access.md, repositories/anton-abyzov/specweave-studio/docs/README.md, repositories/anton-abyzov/specweave-studio/README.md, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/workGrantAccess.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/machines/tools.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/project/handlers.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && test -s docs/user/outside-agents.md && ! grep -rn "Connections > Who can run work" apps/server/src && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/workGrantAccess

### T-02 Route-aware Copy MCP URL
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/connection/presentation.ts, repositories/anton-abyzov/specweave-studio/packages/client-runtime/src/connection/presentation.test.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/settings/ConnectionsSettings.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run packages/client-runtime/src/connection/presentation

### T-03 Upstream MCP fixes
- AC: AC-03 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/McpHttpServer.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/McpHttpServer.test.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/McpHttpServer

### T-04 Triage version, tag fallback, label
- AC: AC-04 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/cli/triage.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/cli/triagePrompt.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/cli/consoleStdin.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/serverRuntimeState.ts, repositories/anton-abyzov/specweave-studio/.github/triage/PLAYBOOK.md, repositories/anton-abyzov/specweave-studio/scripts/public-mirror/publish.mjs | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/cli/triage

### T-05 Clone fixes from upstream
- AC: AC-05 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/sourceControl/SourceControlRepositoryService.ts, repositories/anton-abyzov/specweave-studio/packages/shared/src/cloneUrl.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/project/RepositoryIdentityResolver.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/GitVcsDriverCore.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/vcs/GitVcsDriver.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/sourceControl packages/shared/src/cloneUrl apps/server/src/vcs/GitVcsDriverCore apps/server/src/project/RepositoryIdentityResolver

### T-06 Provision git credential helper
- AC: AC-06 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/provision/probe.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provision/runner.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/provision/plan.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/provision.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/provision

### T-07 Static MCP client tokens
- AC: AC-07 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/cli/auth.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/auth/McpOAuth.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/auth/EnvironmentAuth.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/auth/McpOAuth apps/server/src/cli/auth

### T-08 Outside clients do fleet work
- AC: AC-08, AC-09 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/orchestrator/remote.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/project/remoteLaunch.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/machines/handlers.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/fleet/RemoteWorkers.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/fleet/RemoteWorkerStore.ts, repositories/anton-abyzov/specweave-studio/packages/contracts/src/orchestratorMcp.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/orchestrator apps/server/src/mcp/toolkits/project apps/server/src/mcp/toolkits/machines apps/server/src/fleet/RemoteWorkers

### T-09 Multi-thread wait
- AC: AC-10 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/orchestrator/tools.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/orchestrator/handlers.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/orchestrator/threadsWait.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/mcp/toolkits/orchestrator

### T-10 Thread origin and header badge
- AC: AC-11 | Files: repositories/anton-abyzov/specweave-studio/packages/contracts/src/orchestrationV2.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/orchestration-v2/ProjectionStore.ts, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ThreadOriginBadge.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/chat/ChatHeader.tsx | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/web/src/components/chat/ThreadOriginBadge packages/contracts/src/orchestrationV2

### T-11 Remote clone forwarding
- AC: AC-12 | Files: repositories/anton-abyzov/specweave-studio/apps/server/src/fleet/RemoteStudioMcpClient.ts, repositories/anton-abyzov/specweave-studio/apps/server/src/mcp/toolkits/project/tools.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node node_modules/vite-plus/bin/vp test run apps/server/src/fleet/RemoteStudioMcpClient apps/server/src/mcp/toolkits/project

### T-12 Black-box outside-agent check
- AC: AC-13 | Files: repositories/anton-abyzov/specweave-studio/scripts/studio-verify/outside-agent-mcp.mjs | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/fleet-mcp-1118 && node scripts/studio-verify/outside-agent-mcp.mjs

### T-13 Verify and close 1118
- AC: AC-01, AC-13 | Files: .specweave/increments/1118-fleet-mcp-for-outside-agents-and-t3-ports/reports/verify.md | Test: specweave verify 1118-fleet-mcp-for-outside-agents-and-t3-ports
