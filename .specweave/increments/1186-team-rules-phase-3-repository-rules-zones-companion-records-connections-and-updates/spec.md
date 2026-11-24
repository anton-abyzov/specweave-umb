# Team rules phase 3: repository rules, zones, companion, records, connections and updates

## Problem

Phases 1 and 2 (PRs #1197 and #1223) enforce one machine file. A 10-person team with no device management cannot use that, and a consultant's laptop is either fully locked or not at all. `connections`, `updates` and `zones` are validated but do nothing. The provider CLIs outside the app ignore the rules. Nobody can say who ran what: events record only user, agent or system. The owner approved phases 1 to 3 on November 2, 2026; the hosted console stays on hold.

Design: `1169-t3-code-changes-since-october-30-and-organization-policies/reports/organization-policy-spec.md`. Earlier phases: `1170-*`, `1178-*`.

## Scope

In: repository rules, zones, strictest combination with machine and carried rules, `rules companion`, `rules records` with person and device, settings-change events, enforcement of `connections` and `updates`, web and desktop rendering, readable refusals on phones.

Out: the hosted console, SSO and any new recurring cost. The update install flow beyond reading `updates` at its existing decision points. Pulling updates from a company feed (D-07). New iOS or Android UI for per-project rules (D-08).

## Acceptance Criteria

- [ ] AC-01: Repository rules come from `.specwithcode/team-rules.json` at the default branch's remote-tracking ref. An uncommitted edit, a staged edit or a local commit not on that ref changes nothing.
- [ ] AC-02: A repository file may set only `owner`, `contact`, `agents`, `ai.providers`, `ai.models` and `connections`. Any other key, including `ai.pin`, `reach`, `tools`, `telemetry`, `updates` and `zones`, is an error. An invalid file holds agent turns in that repository only and leaves other projects alone.
- [ ] AC-03: Zones match every Git remote of the working folder, normalized so SSH and HTTPS forms agree, with userinfo dropped and never printed. All matching zones apply. A zone cannot set a pin.
- [ ] AC-04: Sources combine to the strictest value: lowest ceiling and routine limit, intersection of providers and connections, a model must fit every list. No source loosens another, and a machine hold outranks everything. Each refusal names the source that caused it.
- [ ] AC-05: The combined rules hold for each thread at the dispatch gate, the turn chokepoint, new threads, routine save, enable and run, project saves, coordinator raises, local and machine fallback and the ceiling carried out to another machine. Under a combined limit that the machine file does not set, a provider instance with its own launch values is refused rather than launched.
- [ ] AC-06: Web and desktop show the project's limit in the chat permission menu and the notice with its one-click switch down, and a Team rules row labels repository rules "A team agreement, not a security boundary". Zones are labelled as set by the machine's owner.
- [ ] AC-07: `rules check`, `show` and `explain` take `--repository <path>`, and `rules show` and the docs state what each new source cannot do.
- [ ] AC-08: `rules companion` prints a `managed-settings.json` and a `requirements.toml` matching the rules, with `--output <dir>` to write them, and names any rule the provider has no equivalent for rather than dropping it silently.
- [ ] AC-09: `rules records` prints JSONL of events with person, device and machine, filterable by `--since` and `--until`, or `--output <file>`. It reads the database the supported way and never prints secrets, message text or setting values.
- [ ] AC-10: Every settings write made while machine rules exist adds a settings-change event naming the changed setting paths, person and device, without their values.
- [ ] AC-11: `connections.allow` refuses saving, checking and calling a project connection outside the list and refuses enabling native connections outside it, naming who set the list, while reading and revoking stay available.
- [ ] AC-12: `updates.automatic: false` stops automatic checks and downloads and locks the preference; `true` keeps them on and locks the preference; a person can still ask for an update. `updates.feed` turns off updates from the public feed and names the company's feed. A hold treats automatic updates as off.
- [ ] AC-13: A machine or repository with no rules behaves and looks as it does today: no new row, label or database write, and at most one bounded Git read per working folder per rules poll interval.

## Approach

**Engine.** `TeamRulesState` stays the one question every check asks. A new pure `teamRulesCombine(machine, layers)` in `packages/shared/src/teamRules.ts` returns an ordinary state, so `teamRulesTurnRefusal` and every other answer work unchanged. The active state gains optional `sources`, which name who set the ceiling, routine limit, providers, models and connections for refusal wording, and `modelLists`, because the intersection of two glob lists is not a glob list. The fingerprint stays the machine's: `same-rules` compares machine files, never a per-project view. Glob matching moves from a regular expression to a linear matcher, because repository patterns are no longer administrator text.

**Reader.** `apps/server/src/teamRules/TeamRulesScope.ts` runs `git config --get-regexp` for remotes and `git cat-file` for the file, with `GIT_*` variables removed, a three-second timeout and a five-second per-folder cache with single flight. No remote means no repository rules and no further Git. A failed read keeps the last answer. With no answer yet, it counts as no repository rules, unless the machine has zones: then that folder is on hold, because the zone could apply. `TeamRulesShape` gains `forWorkspace(cwd)`, so tests keep `teamRulesOf`.

**Enforcement.** Each per-thread site swaps `currentTeamRules` for `teamRulesForThread`, which resolves `worktreePath ?? workspaceRoot`. Machine-wide sites (`reach`, `tools`, telemetry, `same-rules`) keep the machine state. The launch check goes in `RuntimePolicy`, so adapters are untouched.

**Clients.** A new RPC returns the project's combined summary, called only from the chat and project settings. It is absent or undefined with no rules, and a failure from an older server reads as no rules. The machine summary gains optional `connections` and `updates`. No new refusal reason: older builds decode a closed list, so connection refusals use `tools` and repository holds use `hold`.

**Records.** One migration adds `team_rules_actors` (command id, person, device, session) and `team_rules_settings_changes`. Both are written only while machine rules exist. `rules records` reads `orchestration_v2_events` joined to actors, emitting type, ids and time but no payload, and merges settings changes by time. Person is the session's principal or subject, else the service's OS user. Device is the session's client metadata.

**Companion.** Pure mapping in `apps/server/src/teamRules/companion.ts`. Claude: `permissions.disableBypassPermissionsMode`, `permissions.disableAutoMode`, `allowedMcpServers`. Codex: `allowed_approval_policies`, `allowed_sandbox_modes`, `[mcp_servers.*]`. Key names checked against current provider docs on November 2, 2026.

Rejected: a parallel engine for scoped rules. Reading the working tree. Reading rules once at thread start, because a tightening applies to the next turn. Fetching the remote from a turn, because a gate must not reach the network. A zone pin, because an instance is launched once for all folders.

Risks: a shell agent can edit `.git/config` or move a remote-tracking ref, so zones and repository rules bind cooperative use; the docs say so, and only machine-wide rules hold against that. A project whose root is not a Git repository matches nothing even when it contains client repositories.

## Decisions

### Asked
- D-01 Phases 1 to 3 approved, hosted console on hold → owner, November 2, 2026.
### Defaulted (change any before sw-do)
- D-02 Repository rules bind on any machine that opens the repository, with or without machine rules, labelled as a team agreement.
- D-03 Repository rules apply after a fetch updates the ref. The app never fetches to read them.
- D-04 Zones match every remote, not just `origin`, so adding a remote can only tighten. Repository rules read `origin`, else the only remote; the default branch is `origin/HEAD`, else `main`, else `master`.
- D-05 `zones[].ai.pin` becomes an error. Zones enforced nothing before this, so no working setup depends on it.
- D-06 Records start when machine rules appear; earlier events export with null person and device. Message text and setting values stay out.
- D-07 `updates.feed` stops updates from the public feed and names the company's feed, with no download from it, because pointing the updater elsewhere means changing the install flow the owner excluded. The rule is enforced in the tightening direction; installing from the feed is left to the company's own deployment and stated in the docs.
- D-08 Phones get readable typed refusals and rows for the two new machine rules through shared code. Per-project pickers on iOS and Android wait for a later increment.
- D-09 During a hold a person can still ask for an update, because the update may be the repair.
### Open
- none

## Tasks

### T-01 Engine: combination, sources, linear glob, zone and repository parsing
- AC: AC-02, AC-03, AC-04, AC-13 | Files: packages/contracts/src/teamRules.ts, packages/shared/src/teamRules.ts | Test: `cd packages/shared && node ../../node_modules/vite-plus/bin/vp test run src/teamRules.test.ts`

### T-02 Scope reader from Git
- AC: AC-01, AC-02, AC-03, AC-13 | Files: apps/server/src/teamRules/TeamRulesScope.ts, apps/server/src/teamRules/TeamRules.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/teamRules/TeamRulesScope.test.ts`

### T-03 Enforcement at per-thread chokepoints
- AC: AC-05 | Files: apps/server/src/orchestration-v2/Orchestrator.ts, apps/server/src/orchestration-v2/RuntimePolicy.ts, apps/server/src/orchestration-v2/FullAccessApprovals.ts, apps/server/src/orchestration-v2/MachineLimitHandoff.ts, apps/server/src/scheduledTasks/ScheduledTaskService.ts, apps/server/src/project/ProjectRuntimeAccess.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/orchestration-v2/TeamRulesEnforcement.test.ts`

### T-04 Connections
- AC: AC-11 | Files: apps/server/src/project/ProjectConnectionService.ts, packages/shared/src/teamRules.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectConnectionService.test.ts`

### T-05 Updates at their decision points
- AC: AC-12 | Files: apps/desktop/src/updates/DesktopUpdates.ts, apps/desktop/src/updates/updateFeedGate.ts, apps/desktop/src/ipc/methods/serviceUpdates.ts, apps/web/src/components/settings/UpdatePreferencesSection.tsx | Test: `cd apps/desktop && node ../../node_modules/vite-plus/bin/vp test run src/updates/updateFeedGate.test.ts`

### T-06 Records: actors, settings changes, export
- AC: AC-09, AC-10, AC-13 | Files: apps/server/src/persistence/Migrations.ts, apps/server/src/teamRules/TeamRulesRecords.ts, apps/server/src/cli/rules.ts, apps/server/src/serverSettings.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/teamRules/TeamRulesRecords.test.ts`

### T-07 CLI: repository flag, companion, what each source cannot do
- AC: AC-07, AC-08 | Files: apps/server/src/cli/rules.ts, apps/server/src/teamRules/companion.ts | Test: `cd apps/server && node ../../node_modules/vite-plus/bin/vp test run src/cli/rules.test.ts src/teamRules/companion.test.ts`

### T-08 Web and desktop, phone rows
- AC: AC-06, AC-13 | Files: apps/web/src/teamRules/teamRulesView.ts, apps/web/src/teamRules/useTeamRules.ts, apps/web/src/components/ChatView.tsx, apps/web/src/components/settings/TeamRulesSection.tsx, apps/mobile/src/state/teamRules.ts | Test: `cd apps/web && node ../../node_modules/vite-plus/bin/vp test run src/teamRules/teamRulesView.test.ts`

### T-09 Docs and headless screenshots
- AC: AC-07, AC-13 | Files: docs/user/team-rules.md, apps/web/tests/team-rules/verify.mjs | Test: `node apps/web/tests/team-rules/verify.mjs`

### T-10 Verify and close 1186
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-12, AC-13 | Files: .specweave/increments/1186-team-rules-phase-3-repository-rules-zones-companion-records-connections-and-updates/reports/ | Test: `specweave verify 1186`
