# Per-project machine grants, delegation limits and coordinator takeover

## Problem

Pairing is three one-way, machine-wide trusts (October 19, 2026): an app connection, a fleet membership holding a 365-day management token, and a 30-day worker grant with `orchestration:read` and `orchestration:operate`. A worker grant lets a coordinator run in any admitted project on the worker and with any of the worker's sign-ins; nothing limits which accounts remote work may use. A worker thread launched on B can start work back on A (no origin chain or hop limit). `fleet remove` leaves the management token valid on the other machine. A machine cannot see or revoke, in one place, who may run work on it. When a shared project's coordinator machine is offline, nothing can continue: there is no takeover. Design: `~/Projects/github/studio-research-notes/project-join-handoff-pairing-2026-10-19.md` section 8.

## Scope

In: delegation path and hop limit for remote launches; per-project scoping and an account policy on worker grants, enforced by the worker machine; "Who can run work on this Mac" with revoke; remote revocation on `fleet remove`; manual coordinator takeover with replicated coordinator notes; evaluation of narrowing the management token. Out: linking (0948 provides membership; build takeover on top of it), file copy (0949), secrets (0950).

## Acceptance Criteria

- [ ] AC-01: Every remote launch carries a delegation path of environment IDs and a hop count. The receiving machine refuses, with an error naming the path, when its own ID is already on the path or the hop count exceeds the grant's limit (default 2 for the owner's own machines, 1 for grants marked as another person's). Threads launched remotely record their origin path and pass it on.
- [ ] AC-02: A worker grant can be scoped to listed shared projects (default for newly allowed machines: all projects linked to that coordinator) and carries an account policy: all of this machine's sign-ins, named provider instances, or none. The worker machine enforces both at execution; a launch outside scope or needing a disallowed account is refused with a reason. Existing grants keep working unchanged (treated as all projects, all accounts).
- [ ] AC-03: Settings > Machines on a worker shows "Who can run work on this Mac": each coordinator machine, its scope, account policy, runtime cap and expiry, with Revoke. Revoke refuses new launches at once and interrupts running remote-launched threads after a 2-minute grace.
- [ ] AC-04: `fleet remove` (CLI and Settings) revokes the management token on the other machine when it is reachable, and otherwise reports that it is still valid there and how to revoke it.
- [ ] AC-05: On a member copy of a shared project whose coordinator machine has been unreachable for at least 10 minutes, "Take over coordinator here" (one confirmation) makes this copy the coordinator at epoch+1 with the old owner as predecessor. When the old owner is reachable again it is demoted to a relinquished member, and coordinator turns it ran while disconnected are listed for review. No automatic failover.
- [ ] AC-06: Members keep a read-only replica of the coordinator's memory notes, goal and instructions, refreshed on link and whenever a change is seen while both machines are reachable, so a takeover starts with them.
- [ ] AC-07: The management token's scopes are narrowed for new invitations if "Connect machine", worker grant minting and pairing still work end to end; otherwise the reason it cannot be narrowed is documented in `docs/studio/fleet.md`.
- [ ] AC-08: User docs describe grants, account policy, revoke, delegation limits and takeover.

## Approach

Contracts: `packages/contracts/src/studioFleet.ts` (grant scope, account policy, hop limit), `orchestratorMcp.ts` (delegation path on launch). Server: `apps/server/src/fleet/workerGrantMint.ts`, `FleetWorkerGrants.ts`, `RemoteWorkers.ts`, `RemoteStudioMcpClient.ts`, `remoteWorkerMatching.ts`; receiving-side enforcement in the session scope checks (`EnvironmentAuth.ts`, `SessionStore.ts`) and thread launch admission; `studioFleetJoin.ts` for remote revoke on remove; takeover in `ProjectLink.ts` from 0948 plus a `supersede` call to the returning owner and `logicalProject.ts` helpers. Web: `MachineWorkGrants.tsx` embedded in 0948's Machines screen, takeover action in project settings. Verification: extend `scripts/studio-logical-projects/verify.mjs` (three isolated servers) with an A to B to A cycle, scope and account refusals, revoke with grace, and takeover with the owner stopped and restarted.

## Decisions

### Asked
- none (the user asked to implement all recommendations, October 19, 2026)
### Defaulted
- D-01: Grants marked as another person's machine default to account policy "none" and hop limit 1.
- D-02: Takeover is manual only; no automatic failover.
- D-03: Existing grants are treated as unscoped until the user edits them, so nothing breaks on update.

## Tasks

### T-01 Delegation path and hop limit
- AC: AC-01 | Files: packages/contracts/src/orchestratorMcp.ts, apps/server/src/fleet/RemoteWorkers.ts, apps/server/src/mcp/toolkits/orchestrator/remote.ts, tests | Test: vp test run apps/server/src/fleet

### T-02 Grant scope and account policy, enforced on the worker
- AC: AC-02 | Files: packages/contracts/src/studioFleet.ts, apps/server/src/fleet/workerGrantMint.ts, apps/server/src/fleet/FleetWorkerGrants.ts, apps/server/src/auth (session scope checks), tests | Test: vp test run apps/server/src/fleet apps/server/src/auth

### T-03 Who can run work on this Mac, revoke with grace, remote revoke on remove
- AC: AC-03, AC-04 | Files: apps/web/src/components/settings/MachineWorkGrants.tsx, apps/server/src/studioFleetJoin.ts, apps/server/src/cli/fleet.ts, tests | Test: vp test run on touched tests; headless screenshots

### T-04 Coordinator takeover and replicated notes (after 0948 merges)
- AC: AC-05, AC-06 | Files: apps/server/src/project/ProjectLink.ts, packages/contracts/src/logicalProject.ts, apps/web/src/components/studio/ProjectMachinesSettings.tsx, tests | Test: vp test run apps/server/src/project/ProjectLink.test.ts

### T-05 Management token narrowing evaluation, docs, three-server verification
- AC: AC-07, AC-08 | Files: apps/server/src/studioFleetInvite.ts, docs/studio/fleet.md, docs/user/add-a-machine.md, scripts/studio-logical-projects/verify.mjs | Test: node scripts/studio-logical-projects/verify.mjs <owned report dir>

### T-06 PR, merge, release and installed check
- AC: all | Files: none | Test: PR Gate green; installed build shows grants on the M3

### T-07 Verify and close 0951
