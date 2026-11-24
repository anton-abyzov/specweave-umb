# Fleet skill version push over Connect

## Problem

Skills drift between Anton's machines (M4, M1, M3, ministorm). Changing a skill version means repeating `vskill install` by hand on each machine. PR #946 added a narrow Connect path for the primary to request SpecWithCode installs on fleet machines; nothing does the same for skills.

## Scope

In: a narrow fleet action "install skill <owner/repo/name> at version <X.Y.Z> (user or project scope), pin or not" from the primary to one or all fleet machines over Connect (Tailscale as fallback), reusing #946's transport, DPoP auth, capability flag and answer-first-then-poll pattern; a `fleet skills` CLI with --json; status that ends with the installed version or a named refusal. Out: arbitrary commands, local:/hosted-private sources, Skill Studio UI (1126 calls the CLI), app releases.

## Acceptance Criteria

- [ ] AC-01: `specweave-studio fleet skills <machine|--all> --skill owner/repo/name --version X.Y.Z [--scope user|project --project <id>] [--no-pin] --json` asks each named Connect-reachable machine to install that skill version and prints one JSON result per machine with the installed version read back from that machine's lock, or a named reason (unreachable, unsupported, vskill-missing, invalid-skill, install-failed, unauthorized).
- [ ] AC-02: The machine runs only a fixed argv (`vskill install <skill>@<v> -y` plus `--global` for user scope, cwd = the project's own workspace root resolved from the project id, then `vskill unpin <skill>` when pin is off); skill and version are pattern-checked; no shell, path or URL is accepted.
- [ ] AC-03: Only a coordinator token with the new `fleet:skills` scope, or `environment:maintain` for tokens issued before it, can call the endpoint; the machine advertises `capabilities.fleetSkillUpdate`, and the client reports `unsupported` for machines without it.

## Approach

specweave-studio, worktree ~/.specwithcode/m4/worktrees/specweave-studio/fleet-skills-1125, branch feat/fleet-skills from origin/feat/fleet-connect-updates (#946); PR base main once #946 merges (stacked until then). Copy the #946 shape end to end: scope in packages/contracts/src/auth.ts and fleet/fleetRedemption.ts; StudioFleetSkillInput/status schemas in packages/contracts/src/studioFleet.ts; POST/GET /api/studio/fleet/skills in environmentHttp.ts; new apps/server/src/fleet/fleetSkills.ts (worker, layer, client) modelled on fleetUpdate.ts; handlers in studioFleetHttp.ts; layer in server.ts; `fleet skills` in cli/fleet.ts.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Narrow endpoint, never a terminal or arbitrary-command path (same rule as #946).
- D-02: Pin follows vskill's default (install@X pins); `--no-pin` unpins after install so machines keep updating.
- D-03: Skill Studio triggers pushes through this CLI, so fleet trust stays in SpecWithCode.
### Open
- none

## Tasks

### T-01 Contract, scope and endpoint
- AC: AC-02, AC-03 | Files: specweave-studio/packages/contracts/src/auth.ts, specweave-studio/packages/contracts/src/studioFleet.ts, specweave-studio/packages/contracts/src/environmentHttp.ts, specweave-studio/packages/contracts/src/environment.ts, specweave-studio/apps/server/src/fleet/fleetRedemption.ts, specweave-studio/apps/server/src/environment/ServerEnvironment.ts | Test: pnpm --dir specweave-studio exec vitest run apps/server/src/fleet/fleetSkills.test.ts

### T-02 Worker, handler and CLI
- AC: AC-01, AC-02 | Files: specweave-studio/apps/server/src/fleet/fleetSkills.ts, specweave-studio/apps/server/src/fleet/fleetSkills.test.ts, specweave-studio/apps/server/src/studioFleetHttp.ts, specweave-studio/apps/server/src/server.ts, specweave-studio/apps/server/src/cli/fleet.ts | Test: pnpm --dir specweave-studio exec vitest run apps/server/src/fleet/fleetSkills.test.ts apps/server/src/studioFleetHttp.test.ts

### T-04 Fix Linux process snapshot race exposed by CI
- AC: AC-01 | Files: specweave-studio/apps/server/src/provider/acp/AcpSessionRuntime.ts, specweave-studio/apps/server/src/provider/acp/AcpSessionRuntime.linuxSnapshot.test.ts | Test: cd apps/server && npx vp test run src/provider/acp/AcpSessionRuntime.linuxSnapshot.test.ts src/provider/acp/AcpSessionRuntime.processTree.test.ts

### T-03 Verify and close 1125
- AC: AC-01, AC-02, AC-03 | Files: .specweave/increments/1125-fleet-skill-version-push-over-connect/reports/ | Test: specweave verify 1125; fresh-context review; specweave complete 1125
