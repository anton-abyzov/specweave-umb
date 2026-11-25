# 1476 Agent approvals and provider isolation hardening

## Problem

The November 14 to 25 upstream review (increment 1474, wave 1 group B) found 18 rows where our app (`anton-abyzov/specwithcode`, snapshot `56a9515a3`, now `origin/main` `2b7f17e8b`) lets an agent act with more authority than the person granted, shows the person the wrong thing to approve, leaks the server's environment into agent processes, or sends identifying data to analytics. Evidence per row is in `1474.../reports/lanes/b-providers.md`, `s1-security.md`, `s2-security.md`, `a2-server.md`, `a3-server.md`, `c1-platform.md`, `c2-platform.md`.

| Row (upstream sha) | Defect in ours |
|---|---|
| `1dfc746c8f` + `ea4e7c1a60` | `AcpAdapterV2.ts:1361` trims the option id it sends; `:1402` takes the first `allow_once`, which can be Devin's `plan_bypass` |
| `eecb58c6d6` | `CodexAdapterV2.ts:5580` shows the agent's `reason` instead of the command; `codexFileChanges.ts:81` the same for file paths |
| `96290af4e0` | `CodexAdapterV2.ts:749` sends `approvalPolicy: "never"` in Full access, so Codex refuses browser access prompts unseen |
| `b4e47a5a62` | `CursorAdapterV2.ts:344` loads the checkout's `project` settings (rules, hooks, MCP servers) in every mode |
| `166cb00897` | `OpenCodeAdapterV2.ts:671` full-access rules lack `external_directory`, so Task children prompt |
| `b5bef4d939` | `ProviderTurnStartService.ts:553` / `ProviderAuthService.ts:350` sign a provider out on any `/logout` message, from agents and routines too |
| `b0b2c4f952` | `ProviderTurnStartService.ts:1364` sends another agent's or a routine's message to the model as if the person wrote it |
| `700a4644a4` | `ProviderInstanceEnvironment.ts:129` hands the Linux AppImage runtime env to every agent |
| `222288b00f` | `PiDriver.ts:145` runs the Pi status probe (and its extensions) in the server's folder |
| `fe1f1a5732` | `AcpClientTerminals.ts:265` may pass an inherited `STUDIO_ACP_MCP_*` credential to a Devin terminal (unverified) |
| `528687d226` | `AcpRegistrySupport.ts:1576` lets an inherited `NPM_CONFIG_PREFIX` override the managed prefix on Windows |
| `93cd25a99b` | `AcpRegistrySupport.ts:1714` refuses an executable named `..agent` inside its install folder |
| `9791bce798` | `packages/effect-acp/src/client.ts:1017` accepts elicitation modes the client never advertised |
| `4fccab84a0` | `CodexTextGeneration.ts:194` lets plugins, apps and hooks run during title and commit text generation |
| `d6795eac3c` | `GrokTextGeneration.ts:36` inherits the user's Grok always-approve during text generation |
| `5de10b91d9` | `TextGenerationPrompts.ts:198` branch-name prompt has no rule against starting the task |
| `84e4264bb3` | `Identify.ts:196-268` derives the analytics id from Codex and Claude account ids |
| `6b3899f224` + `1bc44f2732` | `ProviderEventIngestor.ts:183` sends raw custom model names (GGUF paths, gateway names) |

## Scope

In: the 18 rows above, each with a test that fails on `origin/main` and passes after, inside group B's files (`apps/server/src/orchestration-v2/Adapters/*`, `apps/server/src/provider/*`, `apps/server/src/textGeneration/*`, `ProviderTurnStartService.ts`, `ProviderEventIngestor.ts`, `apps/server/src/telemetry/*`, `packages/effect-acp/*`, `packages/effect-codex-app-server/*`, `apps/web/src/session-logic.ts`, and their tests).

Out: changes in files other wave 1 groups own (`auth/RpcAuthorization.ts`, `Orchestrator.ts`, `mcp/*`, `packages/contracts/*`, `ProviderTurnControlService.ts` steering, the terminal manager). Those parts are written up in the report for their owners.

## Acceptance Criteria

- [ ] AC-01: An ACP permission answer sends the agent's option id byte for byte (`" a "` stays `" a "`), and neither a person's Approve nor a Full access auto-approval ever answers Devin with `plan_bypass`; a Devin plan exit offering `plan_bypass` and `plan_approve` answers `plan_approve`. Other ACP agents' approvals keep working unchanged.
- [ ] AC-02: A Codex command approval card shows the command (then cwd and network host), with the agent's reason only as a secondary line; a file-change approval lists every path and the grant root, never only the reason. Approvals without a reason look as today.
- [ ] AC-03: A Codex Full access turn sends a granular approval policy with MCP elicitations on, so browser and app access prompts reach us instead of being refused; an elicitation we cannot answer is answered `cancel`, not `decline` (no thread-wide site denial). Recorded replays that carry `never` still decode.
- [ ] AC-04: A Cursor agent in supervised, sandboxed or auto-review mode loads no `project` setting source; Full access without sandbox or auto review still loads it.
- [ ] AC-05: OpenCode Full access rules include an explicit `external_directory` allow, so a Task child that copies only `external_directory` and deny rules does not prompt; other modes are unchanged.
- [ ] AC-06: A chat `/logout` signs a provider out only when a person typed it; one sent by another agent, a routine or an MCP caller leaves the sign-in in place and the thread says to sign out in Settings. A person's `/logout` in chat keeps working.
- [ ] AC-07: A message from another thread's agent, a routine or an MCP tool reaches the model with one leading line naming its sender; a person's message, and slash commands and `$skill` text from anyone, reach it unchanged.
- [ ] AC-08: On the Linux AppImage build, agent sessions get no `APPIMAGE`/`APPDIR` and no AppImage mount entries on `PATH` or `LD_LIBRARY_PATH`; other entries and explicit instance overrides survive.
- [ ] AC-09: The Pi status probe runs in a private empty folder under the provider status cache, not in the server's folder.
- [ ] AC-10: A Devin client terminal never inherits `STUDIO_ACP_MCP_*` or the thread id from the server's environment; only the requesting session's own layer supplies them (or the row is recorded not reproduced with its test kept).
- [ ] AC-11: On Windows the managed ACP install environment has exactly one npm prefix key, ours, whatever case the inherited key used.
- [ ] AC-12: An executable named `..agent` inside its install folder passes the containment check; `../agent` and absolute paths are still refused.
- [ ] AC-13: The ACP client answers an `elicitation/create` whose mode it never advertised with invalid params (`-32602`); advertised modes still reach the handler.
- [ ] AC-14: Codex text generation runs with plugins, apps and connectors (and hooks) off, even when the user's launch args enable them.
- [ ] AC-15: Grok text generation starts in the default permission mode and cancels every permission request.
- [ ] AC-16: The branch-name prompt tells the model to name the branch and not start the task.
- [ ] AC-17: With telemetry on, the analytics id never reads or derives from Codex or Claude account ids; it is a random per-install id.
- [ ] AC-18: Analytics report a model outside the known vendor catalog as `custom:<provider>`, never its raw name; catalog models report as today.
- [ ] AC-19: `reports/red-green.md` records, per row, the test, its red run on `origin/main` and its green run, or "not reproduced" / "already fixed" with the proving `path:line`.

## Approach

Each row is rewritten in our own code (port rule: no upstream names, shas or links in the app repo). Every fix gets a focused test in the file's existing test file. Work runs in four disjoint lanes in one worktree, then lands as four PRs from `origin/main`:

1. PR "agent approvals": T-01 to T-05 (ACP option ids and Devin, Codex approval text and Full access policy, Cursor project settings, OpenCode subagents, ACP elicitation modes).
2. PR "provider isolation": T-07 to T-11 (AppImage env, Pi probe folder, Devin terminal env, npm prefix and containment, text generation).
3. PR "message senders": T-06 (`/logout` from a person only, sender note).
4. PR "analytics privacy": T-12.

Risks: AC-03 changes what Codex Full access asks; elicitations still go to the person, nothing new is auto-granted. AC-06 is a tightening; the person's own path is tested. AC-07 changes the text agents see; the wording is ours.

## Decisions

### Asked
- none (brief and launch message settle scope, PR grouping and reviewer)
### Defaulted (change any before sw-do)
- D-01 Codex Full access with a granular policy shows supported elicitations (browser and app access) to the person rather than auto-accepting them; unsupported ones answer `cancel`. Nothing is granted that Full access did not already grant (reversible).
- D-02 The `providers:manage` scope check on RPC dispatch of `/logout` lives in `auth/RpcAuthorization.ts` (group A); this increment blocks agent, routine and MCP senders at turn start and reports the RPC part to group A.
- D-03 The sender note helper lives beside turn start (not in `packages/contracts`, group A's area); steering in `ProviderTurnControlService.ts` and handoff history are reported as follow-ups.
- D-04 The analytics install id is a random id stored with the server's state; an existing id file is reused.
### Open
- none

## Tasks

### T-01 ACP permission answers: exact option id, no Devin bypass
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/DevinAcp.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpAdapterV2.permissionOptions.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/orchestration-v2/Adapters/AcpAdapterV2.permissionOptions.test.ts src/orchestration-v2/Adapters/AcpRegistryAdapterV2.test.ts

### T-02 Codex approvals show what runs; Full access keeps browser prompts
- AC: AC-02, AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/codexFileChanges.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/CodexMcpElicitation.ts, repositories/anton-abyzov/specwithcode/apps/web/src/session-logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/session-logic.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.fileChanges.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/codexFileChanges.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/CodexMcpElicitation.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/orchestration-v2/Adapters/CodexAdapterV2.test.ts src/orchestration-v2/Adapters/CodexAdapterV2.fileChanges.test.ts src/orchestration-v2/Adapters/codexFileChanges.test.ts src/provider/CodexMcpElicitation.test.ts && cd ../web && corepack pnpm exec vp test run --passWithNoTests --project unit src/session-logic.test.ts

### T-03 Cursor project settings only in unsandboxed Full access
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CursorAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/CursorAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/orchestration-v2/Adapters/CursorAdapterV2.test.ts

### T-04 OpenCode Full access subagents
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/Adapters/OpenCodeAdapterV2.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/orchestration-v2/Adapters/OpenCodeAdapterV2.test.ts

### T-05 ACP client refuses unadvertised elicitation modes
- AC: AC-13 | Files: repositories/anton-abyzov/specwithcode/packages/effect-acp/src/client.ts, repositories/anton-abyzov/specwithcode/packages/effect-acp/src/client.test.ts | Test: cd repositories/anton-abyzov/specwithcode/packages/effect-acp && corepack pnpm exec vp test run --config ../../vite.config.ts --dir . src/client.test.ts

### T-06 /logout only from a person; agents see who sent a message
- AC: AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderTurnStartService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderAuthService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderTurnStartService.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderAuthService.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/orchestration-v2/ProviderTurnStartService.test.ts src/provider/ProviderAuthService.test.ts

### T-07 Agent sessions drop the AppImage runtime environment
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/ProviderInstanceEnvironment.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/provider/ProviderInstanceEnvironment.test.ts

### T-08 Pi status probe in a private folder
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/PiDriver.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/Drivers/PiDriver.probe.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/provider/Drivers/PiDriver.probe.test.ts

### T-09 Devin terminals drop inherited MCP credentials
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpClientTerminals.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpClientTerminals.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/provider/acp/AcpClientTerminals.test.ts

### T-10 ACP registry npm prefix and containment
- AC: AC-11, AC-12 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistrySupport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpRegistrySupport.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/provider/acp/AcpRegistrySupport.test.ts

### T-11 Text generation runs without tools, approvals or task starts
- AC: AC-14, AC-15, AC-16 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/textGeneration/CodexTextGeneration.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/codexLaunchArgs.ts, repositories/anton-abyzov/specwithcode/apps/server/src/textGeneration/GrokTextGeneration.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/GrokAcpSupport.ts, repositories/anton-abyzov/specwithcode/apps/server/src/textGeneration/TextGenerationPrompts.ts, repositories/anton-abyzov/specwithcode/apps/server/src/textGeneration/CodexTextGeneration.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/textGeneration/GrokTextGeneration.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/textGeneration/TextGenerationPrompts.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/codexLaunchArgs.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/textGeneration src/provider/codexLaunchArgs.test.ts

### T-12 Analytics identity and custom model names
- AC: AC-17, AC-18 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/telemetry/Identify.ts, repositories/anton-abyzov/specwithcode/apps/server/src/telemetry/Identify.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderEventIngestor.ts, repositories/anton-abyzov/specwithcode/apps/server/src/orchestration-v2/ProviderEventIngestor.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/telemetry src/orchestration-v2/ProviderEventIngestor.test.ts

### T-13 Red-green record
- AC: AC-19 | Files: .specweave/increments/1476-agent-approvals-and-provider-isolation-hardening/reports/red-green.md | Test: test -s .specweave/increments/1476-agent-approvals-and-provider-isolation-hardening/reports/red-green.md

### T-14 ACP agent spawns do not merge the server environment back
- AC: AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpSessionRuntime.ts, repositories/anton-abyzov/specwithcode/apps/server/src/provider/acp/AcpSessionRuntime.environment.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && corepack pnpm exec vp test run src/provider/acp/AcpSessionRuntime.environment.test.ts
