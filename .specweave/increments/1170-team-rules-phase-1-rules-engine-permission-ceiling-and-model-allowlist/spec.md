# Team rules phase 1: rules engine, permission ceiling and model allowlist

## Problem

No company can set limits for its people in SpecWithCode. Every setting belongs to whoever runs the app, `settings.json` is writable by any shell agent, workers and routines lean to full access, and fallback can move work to a provider the company never approved. A security reviewer cannot approve that. The owner approved phases 1 to 3 of Team rules on November 2, 2026 and held the hosted console.

Design: `1169-t3-code-changes-since-october-30-and-organization-policies/reports/organization-policy-spec.md`. Code map: `reports/policy-enforcement-map.md` in the same increment, taken at `9715811561`.

## Scope

In: the rules engine, the machine file at hardcoded paths, `specweave-studio rules check`, `show` and `explain`, safe hold, the permission ceiling, the provider and model allowlist including fallback, "Set by" locks on web and desktop, and every phase 1 row of the spec's Enforcement table.

Out, schema only: `reach`, `tools`, `connections`, `updates`, `zones`, carried rules, repository rules, records, `rules companion`, iOS and Android rendering. Phase 4 stays on hold. Nothing here has a recurring cost.

## Acceptance Criteria

- [ ] AC-01: The machine file is read only from `/Library/Application Support/SpecWithCode/team-rules.json`, `C:\ProgramData\SpecWithCode\team-rules.json` or `/etc/specwithcode/team-rules.json`. No home directory, `STUDIO_*` value or setting can change the path, and the enforcing server has no path override.
- [ ] AC-02: The file parses to version 1 of the schema. Unknown keys, a wrong version, invalid JSON, an unreadable file, an oversized file and credential-looking pin variables are errors with a path to the offending key. The later-phase sections validate and are reported as declared, not enforced.
- [ ] AC-03: `specweave-studio rules check` exits 0 for valid or absent and non-zero for invalid, `show` prints the effective rules, fingerprint, source path, what is enforced and what the rules cannot do, and `explain` answers why a mode, provider or model is allowed or refused. `--file` validates a candidate without affecting enforcement.
- [ ] AC-04: Safe hold: an invalid file starts no agent turn from any entry point, the server keeps running, and clients and the CLI can read the error. Fixing the file releases the hold without a restart.
- [ ] AC-05: A rules change is picked up without a restart. A tightening applies to the next turn, and removing the rules brings stored choices back unchanged because rules never rewrite stored settings.
- [ ] AC-06: The ceiling refuses, with a typed error naming the owner, any thread create, fork, delegation, mode change or message above it, for people and agents alike. A turn that reaches the provider chokepoint above the ceiling fails instead of running lowered.
- [ ] AC-07: Under a ceiling below full access, a provider or model list, or a pin, instance launch args, environment, binary path, server URL and API endpoint come only from rules, `STUDIO_CODEX_LAUNCH_ARGS` is ignored, and `--dangerously-skip-permissions` or `--permission-mode` cannot change the mode.
- [ ] AC-08: A project permission save above the ceiling is refused and rewrites no thread, and every settings write path, including the MCP tools, passes the same check.
- [ ] AC-09: A routine above `agents.routines` or the ceiling is refused at save and fails at run with a recorded reason, re-checked at every run.
- [ ] AC-10: With a ceiling below full access, a coordinator's Full access neither raises workers nor auto-accepts their prompts.
- [ ] AC-11: The allowlist checks the final provider and model for threads, named models, workers, routines, explicit API-key instances, and fallback including machine-target entries. Fallback picks only approved models, and stops with a reason when none is left.
- [ ] AC-12: A driver outside `ai.providers` never starts, including the ACP registry's `npx` and `uvx` agents. Model calls outside chat turns (found by the entry-point sweep) respect the same list.
- [ ] AC-13: Under `ai.pin`, rules own the provider's environment, so `ANTHROPIC_BASE_URL` in an instance cannot redirect traffic.
- [ ] AC-14: With `telemetry.export` false, OTLP URLs cannot be set and stored ones are not used.
- [ ] AC-15: `ServerConfig` carries a summary. Web and desktop show "Set by <owner>" locks on the affected rows, "Above your team's limit" in the chat permission menu, a one-click switch down for a thread above the ceiling, unapproved models unavailable in pickers, a Team rules section at the top of General settings and a safe-hold notice. Clients without the field keep working and get server refusals.
- [ ] AC-16: With no rules file, behaviour and the settings UI are unchanged.

## Approach

**Engine.** `packages/contracts/src/teamRules.ts` holds the file schema, summary and refusal shapes. `packages/shared/src/teamRules.ts` holds pure logic: parse, rank, glob, allow checks, settings-write check, messages. `apps/server/src/teamRules/` holds the machine reader, the CLI command and server-side guards.

**Reading state.** `TeamRules` is a `Context.Reference` whose default reads the hardcoded file, so production needs no layer wiring and cannot silently run unwired. The reader re-stats on each read and reparses only on change, and a poll publishes changes. Tests provide another value. No environment override exists; `--file` only validates a candidate for the CLI.

**Enforcement.** Server-side, on the machine doing the work:

| Bypass | Where |
|---|---|
| Launch args, env, binary path, ACP registry, pin | Team rules transform on the instance config map in `ProviderInstanceRegistryHydration` |
| `STUDIO_CODEX_LAUNCH_ARGS` | `provider/codexLaunchArgs.ts` |
| Turn chokepoint, hold, final model | `RuntimePolicy.resolve` |
| People and agents, typed refusal | `Orchestrator` dispatch gate, beside the mode limit check |
| Project save, MCP settings tools | `persistSettingsUpdate` in `serverSettings.ts` |
| Routines | `ScheduledTaskService` save and run |
| Coordinator raise | `FullAccessApprovals` |
| Named model, routing, fallback, machine targets, API-key instances | Filtered provider list plus final-selection check |
| OTLP | Settings write check and the observability read |

**Refuse, not lower.** Stored values stay; the check is on use. Handoff arrival is the one lowering, because the thread must exist to be repaired.

**Clients.** `ServerConfig.teamRules` is optional. `SettingsRow` gains a lock. The summary reaches rows through one hook.

Rejected: a settings-path lock list, because a rename would silently unlock it. A file under the home directory, because agents can write it. Server exit on a bad file, because a typo would cut the fleet off from the machine that needs repair.

Risks: stripping instance environment under a ceiling can remove an API key a person relied on, which `rules show` states. Windows uses the fixed `C:\ProgramData` path, so a machine with a relocated ProgramData folder must use the default location. Claude loads user, project and local settings, so its allow rules still widen tools. A provider's `homePath` can redirect credentials and configuration. Remote probes and terminals read stored instance values. A running turn finishes under the rules it started with.

## Decisions

### Asked
- D-01 Phases 1 to 3 approved, hosted console on hold → owner, November 2, 2026.
### Defaulted (change any before sw-do)
- D-02 OTLP row is in phase 1 through a small `telemetry.export` key, since the spec's phase table assigns it nowhere and the brief says to close every non-reach row.
- D-03 `reach.machines` filtering of machine targets waits for phase 2. In phase 1 a machine-target entry is still subject to the model allowlist.
- D-04 `ai.pin` may set `environment`, `launchArgs` and `binaryPath`. Credential-looking variable names are a file error, because every user can read the file.
- D-05 A rules file with insecure ownership or permissions is a warning in `rules check` and `show`, not a hold. Holding would punish a machine for a deployment detail that only an administrator can fix.
- D-06 Launch ownership also applies under `ai.providers` and `ai.models`, and also covers `serverUrl` and `apiEndpoint`, because `--model` or an endpoint could bypass the list.
- D-07 A stored default from before the rules lowers at use (`teamRulesClampMode`) because nobody asked for it. A request above the limit is refused.
- D-08 The settings surface is a section at the top of General, shown only with rules, not a page: no route or nav entry exists on a machine without rules, which keeps AC-16 literal.
- D-09 Text generation, decision model, voice, triage and managed agents CLI respect the same list. `telemetry.export: false` disables OTLP at server start, including environment values.
- D-10 Forms with no permission picker (routine forms, design gallery) start inside the limit instead of being refused for a mode nobody picked. `reach`-style fleet worker access stays with the server refusal until phase 2.
### Open
- none

## Tasks

### T-01 Rules schema and engine
- AC: AC-02, AC-16 | Files: packages/contracts/src/teamRules.ts, packages/shared/src/teamRules.ts | Test: `cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/teamRules.test.ts`

### T-02 Machine reader, safe hold state and CLI
- AC: AC-01, AC-03, AC-04, AC-05 | Files: apps/server/src/teamRules/, apps/server/src/cli/rules.ts, apps/server/src/binCli.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/teamRules src/cli/rules.test.ts`

### T-03 Turn chokepoint and dispatch gate
- AC: AC-04, AC-06, AC-11 | Files: apps/server/src/orchestration-v2/RuntimePolicy.ts, Orchestrator.ts, ThreadMessageIntake.ts, FullAccessApprovals.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/TeamRulesEnforcement.test.ts`

### T-04 Instance ownership: launch args, environment, binary, drivers, pin
- AC: AC-07, AC-12, AC-13 | Files: apps/server/src/provider/ProviderInstanceRegistryHydration.ts, provider/codexLaunchArgs.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/provider/TeamRulesInstances.test.ts`

### T-05 Settings writes, project save and telemetry
- AC: AC-08, AC-14 | Files: apps/server/src/serverSettings.ts, project/ProjectRuntimeAccess.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/serverSettings.teamRules.test.ts`

### T-06 Routines
- AC: AC-09 | Files: apps/server/src/scheduledTasks/ScheduledTaskService.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/scheduledTasks/ScheduledTaskService.teamRules.test.ts`

### T-07 Allowlist: providers, routing, fallback and other model calls
- AC: AC-10, AC-11, AC-12 | Files: packages/shared/src/providerFallback.ts, apps/server/src/orchestration-v2/ProviderFallbackWorker.ts, apps/server/src/decisions/DecisionModel.ts | Test: `cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/providerFallback.test.ts`

### T-08 Web and desktop locks
- AC: AC-15, AC-16 | Files: packages/contracts/src/server.ts, apps/web/src/components/settings/, apps/web/src/components/chat/ChatComposer.tsx | Test: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/teamRules`

### T-09 Docs and provenance
- AC: AC-03 | Files: docs/user/team-rules.md, UPSTREAM.md | Test: `node scripts/studio-brand-audit.mjs`

### T-10 Verify and close
- AC: all | Files: reports/ | Test: typecheck gate, focused suites, headless screenshots, fresh-context review SHIP on the exact head, green check-runs, squash merge.
