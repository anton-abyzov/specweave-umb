# Team rules phase 2: reach, tools, carried ceiling and fingerprints

## Problem

Phase 1 (PR #1197, `ecf3851fb7`) stops a machine's own agents going above its rules. It validates `reach` and `tools` but does not enforce them, so a phone, Connect, another machine or a webhook can still reach a locked-down laptop, and an agent can still drive Chrome, the desktop, Google or Telegram. Work sent to another machine runs under that machine's rules only, so a coordinator with a ceiling can reach full access through a rule-free worker. Nobody can see which machines in a fleet differ. iOS and Android show no rules at all. The owner approved phases 1 to 3 on November 2, 2026.

Design: `1169-t3-code-changes-since-october-30-and-organization-policies/reports/organization-policy-spec.md`. Phase 1: `1170-team-rules-phase-1-rules-engine-permission-ceiling-and-model-allowlist`.

## Scope

In: `reach` (phones, connect, machines with `same-rules` and machine-target filtering, webhooks), `tools` (chrome, computerUse, google, telegram), the carried ceiling, rule fingerprints and drift in Machines, iOS and Android rendering with typed server refusals for older builds, every phase 2 row of the spec's Enforcement table, and the phase 1 gaps listed below.

Out: repository rules, zones, `rules companion`, records, `connections`, `updates` (phase 3). The hosted console stays on hold. Nothing here has a recurring cost.

## Acceptance Criteria

- [ ] AC-01: `reach.phones: false`: new phone links, mints and phone token or cookie exchanges are refused, and an existing phone session fails authentication with a typed reason and has its open sockets closed. No session is revoked, so removing the rule restores the phone and no other machine unpairs it.
- [ ] AC-02: `reach.connect: false`: link, relay config, mint, health, relay client install, Connect invites and the CLI's `link` and `publish` are refused; a running tunnel stops within one rules poll and returns when the rule is removed, without deleting link secrets; requests arriving over Connect fail authentication; agent activity stops publishing.
- [ ] AC-03: `reach.machines: "none"` refuses every outbound credentialed call and every inbound coordinator or worker credential, invites, joins, grants, folder copies and project links included. Identity-only probes still run so the Machines page stays truthful.
- [ ] AC-04: `reach.machines: "same-rules"` allows a peer only when its fingerprint equals this machine's, checked on both sides at each call. A missing fingerprint, a hold or an older peer is a mismatch. Refusals name the machine and say the rules differ.
- [ ] AC-05: Fallback machine targets are filtered by `reach.machines`, including `same-rules`; with none left the same-machine fallback step runs as usual. `allowConnectFrom` cannot lower the connect permission under `reach.machines`.
- [ ] AC-06: `reach.webhooks: false` refuses a webhook before reading its body, refuses creating or rotating a webhook routine, stops the relay holding webhooks and hides the relay hook URL.
- [ ] AC-07: `tools.chrome: false` refuses the agent Chrome tools and `chrome_peer`, refuses extension pairing and disconnects a paired extension, hides Claude in Chrome, and keeps preview tools working.
- [ ] AC-08: `tools.computerUse: false` refuses computer tools at the broker and refuses turning the setting on. `tools.google: false` refuses the Google tools, sign-in and token use while disconnect stays available. `tools.telegram: false` stops the poll loop and refuses pairing while unpair stays available.
- [ ] AC-09: Work crossing machines (remote launch, handoff, migrate, machine-limit handoff, project move) carries the stricter of the sender's ceiling and the thread's carried ceiling. The working machine enforces the stricter of its own and the carried one at dispatch and at the turn chokepoint, for the thread and its children, also with no rules file of its own. A local agent cannot set or clear it through tool arguments.
- [ ] AC-10: A coordinator with a ceiling below Full access refuses to send work to a peer that does not advertise carried rules. A thread back on the machine that set its carried ceiling follows that machine's live rules.
- [ ] AC-11: Machines settings show each reachable machine's rule fingerprint and flag drift against this machine, including no rules and hold. With no rules on this machine or any peer, the row is unchanged.
- [ ] AC-12: iOS and Android show a Team rules section, "Set by" locks on the affected rows, limited permission pickers and readable refusals. Their decoders tolerate the field missing, and older builds get typed server refusals with a readable message.
- [ ] AC-13: The `serverRefreshProviders` reply is filtered. A routine with a check is refused at save and enable under a limit. A routine resuming an unbound thread passes the provider and model check. Direct tests cover the text generation refusal, the hold early return in `sync` and ACP prepare refusal.
- [ ] AC-14: With no rules file and no carried ceiling, behaviour and every client's UI are unchanged. `rules show` and docs say what these rules cannot do.

## Approach

**Engine.** New pure answers in `packages/shared/src/teamRules.ts`: `teamRulesReachRefusal`, `teamRulesMachineRefusal`, `teamRulesToolRefusal`, `teamRulesCarriedRefusal`, `teamRulesOutgoingCeiling`. New refusal reasons `reach`, `machines`, `tools`, `ceiling`. `TeamRulesSummary` gains `reach` and `tools`; `teamRulesStateFromSummary` round-trips them, so clients ask the same questions as the server.

**Enforcement, on the machine doing the work:**

| Rule | Where |
|---|---|
| Phones | `EnvironmentAuth` authenticate, exchange and WS ticket; `studioFleetHttp` phone routes; a rules watcher closes sockets |
| Connect | `ManagedEndpointRuntime.applyConfig`, `CloudLink` entries, `cli/connect.ts`, `fleetAddresses`, inbound `arrivedOverConnect`, a rules watcher in `server.ts` |
| Machines, outbound | `reachFleetMachine` and `fleetAuthorization`, `RemoteWorkers`, `HandoffPeers`, `folderTransfer`, `ProjectLink`, `studioFleetHttp`, `studioFleetJoin` |
| Machines, inbound | `McpOAuth`, `handoffRoute`, `EnvironmentAuth` coordinator principals, credential minting |
| Machine targets | `MachineLimitHandoff` |
| Webhooks | `webhookRoute`, `ScheduledTaskService`, `HeldHooksWaker`, `CloudLink`, `server.ts` |
| Tools | Toolkit handlers, `ComputerUseBroker`, `BrowserExtension`, `GoogleAccountService`, `TelegramChannel`, `ClaudeAdapterV2`, `ProviderSessionManager` |
| Carried ceiling | `OrchestrationV2ThreadOrigin.carried`, read in the `Orchestrator` gate and `RuntimePolicy` |

**Fingerprint.** `ExecutionEnvironmentDescriptor` gains optional `teamRules` (status, fingerprint) and `capabilities.teamRulesCarried`. Outbound same-rules reads the descriptor on every credentialed reach instead of the five-minute identity cache. Inbound reads a fingerprint header sent by `fleetAuthorization`. Machines reads the same descriptor through `discoverFleet`, and connected environments' `serverConfig.teamRules`.

**Carried ceiling.** Stored on the thread's origin, not in `work-grants.json`, whose 90-day and 5,000-entry eviction would fail open. The gates already hold the thread, so no IO per turn. Accepted only from a grant client through `delegation` or from a verified handoff peer through `ReplicateMeta`.

**Clients.** Web gets locks through the existing `TeamRulesLabel` pattern. Android is Expo React Native and reuses the shared engine. iOS decodes an optional `teamRules` and also picks up the summary from the `providerStatuses` stream.

Rejected: revoking phone sessions, because `phoneLinks` carries a revoke to every other machine and rules must not rewrite state. Carrying the model allowlist, because the spec carries the ceiling and `same-rules` covers the rest. Silent lowering on arrival beyond phase 1's handoff clamp.

Risks: `same-rules` compares a self-reported fingerprint, so it catches drift, not a hostile machine; any edit to the file changes the fingerprint, by design. Device type is self-reported, so a client claiming `desktop` escapes the phones rule; `reach.connect` and the network still bound it. A browser session already paired to a machine is a person's device, not a machine credential, so `reach.machines` does not end it.

## Decisions

### Asked
- D-01 Phases 1 to 3 approved, hosted console on hold → owner, November 2, 2026.
### Defaulted (change any before sw-do)
- D-02 During a hold, running tunnels, existing sessions and existing fleet connections stay (the design's "stay reachable to repair"), while new pairings, links, Connect setup, webhooks, outbound work and agent tools are refused, because a broken file could be hiding a `false`. A machine that restarts during a hold brings back its stored tunnel, for the same reason.
- D-03 The fingerprint sits in the public descriptor beside `label` and `serverVersion`. The file holds no credentials and every local user can read it, and the alternative needs a worker grant the Machines page does not always have.
- D-04 A carried ceiling applies on a machine with no rules file, since the work came from a rules machine. The no-rules promise covers work that did not.
- D-05 Thread origin records `from`, the environment that set the ceiling. On return to that environment the carried value is dropped and live rules apply, so removing the rules restores the thread.
- D-06 Continue here keeps the carried ceiling unless the receiving machine set it.
- D-07 `chrome: false` does not refuse `enableAgentBrowserAccess`, because that setting also governs preview. The check is at use.
- D-08 `allowConnectFrom` is ignored when `reach.machines` is set.
- D-09 A project move lowers the mode at the source and passes the ceiling in its bundle. The client drives the transfer, so the source cannot refuse an older destination: that machine starts inside the ceiling but does not keep it. Stated in the docs.
- D-10 A thread carrying a ceiling cannot schedule routines, because a routine holds no origin and would outlive it.
### Open
- none

## Tasks

### T-01 Engine: reach, tools, carried ceiling
- AC: AC-01, AC-04, AC-09, AC-14 | Files: packages/contracts/src/teamRules.ts, packages/shared/src/teamRules.ts | Test: `cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/teamRules.test.ts`

### T-02 Reach: machines, same-rules and machine targets
- AC: AC-03, AC-04, AC-05 | Files: apps/server/src/fleet/fleetTransport.ts, apps/server/src/studioFleet.ts, apps/server/src/studioFleetHttp.ts, apps/server/src/auth/McpOAuth.ts, apps/server/src/handoff/handoffRoute.ts, apps/server/src/auth/EnvironmentAuth.ts, apps/server/src/orchestration-v2/MachineLimitHandoff.ts, packages/contracts/src/environment.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/fleetTransport.teamRules.test.ts src/orchestration-v2/MachineLimitHandoff.test.ts src/teamRules/TeamRulesReach.test.ts`

### T-03 Reach: phones
- AC: AC-01 | Files: apps/server/src/auth/EnvironmentAuth.ts, apps/server/src/studioFleetHttp.ts, apps/server/src/teamRules/ | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/auth/EnvironmentAuth.test.ts`

### T-04 Reach: Connect
- AC: AC-02 | Files: apps/server/src/cloud/ManagedEndpointRuntime.ts, apps/server/src/cloud/CloudLink.ts, apps/server/src/cloud/http.ts, apps/server/src/cli/connect.ts, apps/server/src/server.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/cloud/ManagedEndpointRuntime.test.ts`

### T-05 Reach: webhooks
- AC: AC-06 | Files: apps/server/src/scheduledTasks/webhookRoute.ts, apps/server/src/scheduledTasks/ScheduledTaskService.ts, apps/server/src/relay/HeldHooksWaker.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/scheduledTasks/webhookRoute.test.ts`

### T-06 Tools
- AC: AC-07, AC-08 | Files: apps/server/src/mcp/toolkits/chrome/handlers.ts, apps/server/src/mcp/toolkits/computer/handlers.ts, apps/server/src/computerUse/ComputerUseBroker.ts, apps/server/src/mcp/toolkits/google/handlers.ts, apps/server/src/integrations/google/GoogleAccountService.ts, apps/server/src/channels/TelegramChannel.ts, apps/server/src/browserExtension/BrowserExtension.ts, apps/server/src/orchestration-v2/ProviderSessionManager.ts, apps/server/src/orchestration-v2/Adapters/ClaudeAdapterV2.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/mcp/toolkits/chrome src/mcp/toolkits/google src/computerUse/ComputerUseBroker.test.ts src/channels/TelegramChannel.test.ts`

### T-07 Carried ceiling
- AC: AC-09, AC-10 | Files: packages/contracts/src/orchestrationV2.ts, packages/contracts/src/orchestratorMcp.ts, apps/server/src/fleet/workGrantPolicy.ts, apps/server/src/fleet/RemoteWorkers.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/handoff/, apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/RuntimePolicy.ts, apps/server/src/orchestration-v2/FullAccessApprovals.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/TeamRulesCarried.test.ts src/fleet/RemoteWorkers.test.ts src/mcp/threadOrigin.test.ts`

### T-08 Phase 1 gaps
- AC: AC-13 | Files: apps/server/src/provider/ProviderRegistry.ts, apps/server/src/scheduledTasks/ScheduledTaskService.ts, apps/server/src/textGeneration/TextGeneration.test.ts, apps/server/src/provider/ProviderInstanceRegistryHydration.teamRules.test.ts, apps/server/src/provider/acp/AcpRegistrySupport.test.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/provider/ProviderRegistry.test.ts src/scheduledTasks/ScheduledTaskService.lifecycle.test.ts src/textGeneration/TextGeneration.test.ts src/provider/ProviderInstanceRegistryHydration.teamRules.test.ts src/provider/acp/AcpRegistrySupport.test.ts`

### T-09 Web locks, fingerprints and drift
- AC: AC-11, AC-14 | Files: apps/web/src/teamRules/, apps/web/src/components/settings/, apps/web/tests/team-rules/ | Test: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/teamRules src/components/settings/machinesSettings.logic.test.ts`

### T-10 Android and React Native rendering
- AC: AC-12, AC-14 | Files: apps/mobile/src/features/threads/, apps/mobile/src/features/settings/, apps/mobile/src/state/ | Test: `cd apps/mobile && node ../../node_modules/vite-plus/bin/vp test run --config ../../vite.config.ts --dir . teamRules`

### T-11 iOS rendering
- AC: AC-12, AC-14 | Files: apps/ios/SWCKit/Sources/, apps/ios/SWCKit/Tests/, apps/ios/UITests/ | Test: `cd apps/ios && make test-core`

### T-12 Docs and provenance
- AC: AC-14 | Files: docs/user/team-rules.md, apps/server/src/cli/rules.ts, UPSTREAM.md | Test: `node scripts/studio-brand-audit.mjs`

### T-13 Verify and close 1178
- AC: all | Files: reports/ | Test: typecheck gate, focused suites, headless and simulator screenshots, fresh-context review SHIP on the exact head, green check-runs, squash merge.
