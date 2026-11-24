# Link a project with its copy on another machine

## Problem

The M4 and M3 each have an EasyChamp project with its own coordinator, memory and threads (October 19, 2026). The only way two machines share one project today is a machine handoff, which always moves the coordinator to the destination and refuses large umbrella folders such as the M4's EasyChamp (unique-origin, dirty and symlink rules). Since 1.0.18 remote workers need an explicit shared-project binding, so the M4's coordinator cannot use the M3's copy at all. Projects created before shared identities existed (EasyChamp `5848bdc2`, specweave `1332065e` on the M4) have no `workspaceSettings.logicalProject`. Adding a folder that is already a copy of a project on another machine always creates an unrelated project. The M3 app, not connected to the M4, offers "Personal assistant: Set up", which would create a second assistant. Design: `~/Projects/github/studio-research-notes/project-join-handoff-pairing-2026-10-19.md` sections 2, 3, 4, 5, 8.3, 8.7.

## Scope

In: SpecWithCode (`anton-abyzov/specwithcode-dev`) contracts, server ownership commands and RPCs, web project settings, Settings > Machines summary, Add-folder recognition, personal-assistant Set up guard, docs. Out: copying files (0949), credentials (0950), per-project grants, delegation limits and coordinator takeover (0951). The user's live EasyChamp projects are not linked by this work; the user does that from the released app.

## Acceptance Criteria

- [ ] AC-01: A project without a shared identity gets one (`logical:<uuid>`, itself as the only member, binding epoch 0 active) the first time it takes part in a link, through a server-only ownership path; existing identities and project IDs never change.
- [ ] AC-02: Settings > Project > Machines offers "Link with a project on another machine". It lists candidate projects on every connected machine, ranked by repository fingerprint (section 4.2), and links only after the user picks one; resemblance alone never links.
- [ ] AC-03: The user chooses which coordinator stays (default: the copy with the most recent coordinator activity). After linking, the kept copy's binding is unchanged (same epoch, active); the other copy joins the same identity with a relinquished binding, so its coordinator is read-only and its ordinary workers keep running; both copies list both members, so `isLogicalProjectBinding` holds in both directions.
- [ ] AC-04: After linking, the kept coordinator can launch a worker in the other copy through the existing remote worker path (given the existing "Allow workers" grant), proven in the headless multi-server verification.
- [ ] AC-05: Linking previews memory: notes present on one side only are copied to the kept copy; notes with the same name and different content are shown side by side with keep mine / keep theirs / keep both (`<name>-<machine-slug>.md` (amended October 20, 2026 to match the shipped code and docs)); goal and instructions keep the kept copy's text and show the other's for manual merge. Nothing is overwritten without a choice.
- [ ] AC-06: Link is refused, with a reason naming the fix, when the joining copy already has other members, when either machine is unreachable or lacks the needed scope, when the folder repositories do not match at the root, or when a handoff is in progress. A retry of the same link operation is idempotent.
- [ ] AC-07: Unlink on a member gives it a fresh identity and an active coordinator with a copy of the kept notes, and removes it from the kept copy's members. Existing invariants still refuse resuming a relinquished binding by any other path.
- [ ] AC-08: The sidebar shows a linked project once, with each machine's copy and its role (coordinator, or runs workers).
- [ ] AC-09: Adding a folder scans it: root repo or plain umbrella folder, nested repos, linked worktrees counted as worktrees of their main repository (not duplicate repositories), directory symlinks skipped (not followed, not fatal). When a connected machine has a project whose fingerprint overlaps, the app suggests "Link as a copy of <project> on <machine>" with the match summary and a list of repositories missing here, each with "Clone from origin". It never links or clones without a click. A folder holding a subset of the repositories is a valid copy.
- [ ] AC-10: Settings > Machines shows one row per known machine: whether this app can see it, worker grants held for it, shared projects with role and folder, and its accounts with "also on". For a fleet machine this app is connected to, "Connect both ways" lets that machine's app see this one without pasting a secret into chat; when that cannot be automated it shows the one remaining step.
- [ ] AC-11: Personal assistant Set up, when no connected machine has an assistant, says that an assistant on another Mac is not visible until connected and offers Connect before creating a separate one.
- [ ] AC-12: User docs explain shared projects, linking, unlinking and roles, and correct the old statement that remote workers match by repository alone.

## Approach

Contracts: `packages/contracts/src/logicalProject.ts` gains the link operation shapes (`ProjectLinkPrepare`, `ProjectLinkPreview`, `ProjectLinkAccept`, `ProjectLinkCommit`, `ProjectUnlink`) and the fingerprint type; `projectWorkspace.ts` unchanged except where the ownership command needs a link mode. Server: `ProjectCommands.ts` ownership gets explicit modes `adopt-identity` (no identity yet), `link-member` (kept copy adds a member, binding unchanged), `join-as-member` (standalone copy adopts the identity with `state: "transferred"` and `successor` = kept member, which the existing join guard already allows), `unlink` (fresh identity). New `apps/server/src/project/ProjectLink.ts` service plus RPCs in `ProjectWorkspaceRpc.ts`, scoped like handoff (`settings:write`, `orchestration:operate`) and listed in `CLIENT_GUARDED_RPC_SCOPES`; the destination checks grants at execution. The client drives the two machines like handoff does (prepare on the kept machine, preview and accept on the joining machine, commit on the kept machine), with an operation ID for idempotency. Fingerprint: `apps/server/src/project/projectFingerprint.ts` reusing `handoffGit` discovery rules but tolerant of a plain root, worktree `.git` files (resolve `commondir`) and directory links. Web: `ProjectMachinesSettings.tsx` (link and unlink dialog with memory preview), `useNewProject.ts` suggestion card, `MachinesSettings.tsx`, `personalAssistant.ts` guard, sidebar grouping in `projectGrouping.ts`. Extend `scripts/studio-logical-projects/check.mjs` and `verify.mjs` (three isolated servers) for link, worker launch and unlink.

## Decisions

### Asked
- none (the user said "implement all the recommendations", October 19, 2026)
### Defaulted
- D-01: The client app orchestrates the two machines, as handoff does; no new server-to-server channel in this increment.
- D-02: The joining copy's coordinator thread stays as read-only history (relinquished binding); nothing is deleted.
- D-03: Memory merge copies into the kept copy only; the member keeps its own notes as they were.
- D-04: Machine-wide "Allow workers" stays the authorization for remote work until 0951 adds per-project grants.

## Tasks

### T-01 Identity adoption and link ownership modes
- AC: AC-01, AC-03, AC-06, AC-07 | Files: packages/contracts/src/logicalProject.ts, apps/server/src/orchestration-v2/ProjectCommands.ts, apps/server/src/orchestration-v2/ProjectCommands.test.ts | Test: vp test run apps/server/src/orchestration-v2/ProjectCommands.test.ts packages/contracts/src/logicalProject.test.ts

### T-02 ProjectLink service, RPCs and memory merge preview
- AC: AC-03, AC-04, AC-05, AC-06, AC-07 | Files: apps/server/src/project/ProjectLink.ts, apps/server/src/project/ProjectLink.test.ts, apps/server/src/project/ProjectWorkspaceRpc.ts, packages/client-runtime (guarded scopes) | Test: vp test run apps/server/src/project/ProjectLink.test.ts

### T-03 Link and unlink UI, sidebar roles
- AC: AC-02, AC-03, AC-05, AC-08 | Files: apps/web/src/components/studio/ProjectMachinesSettings.tsx, packages/client-runtime/src/state/projectGrouping.ts, apps/web/src/studio/projectDomain.ts | Test: vp test run on the touched web tests; headless screenshots

### T-04 Folder fingerprint and Add-folder suggestion with clone of missing repositories
- AC: AC-09 | Files: apps/server/src/project/projectFingerprint.ts, apps/server/src/project/projectFingerprint.test.ts, apps/web/src/hooks/useNewProject.ts | Test: vp test run apps/server/src/project/projectFingerprint.test.ts

### T-05 Settings > Machines summary, Connect both ways, assistant Set up guard
- AC: AC-10, AC-11 | Files: apps/web/src/components/settings/MachinesSettings.tsx, apps/web/src/studio/personalAssistant.ts | Test: vp test run on the touched web tests; headless screenshots

### T-06 Docs and headless multi-server verification
- AC: AC-04, AC-12 | Files: docs/user/shared-projects.md, docs/user/add-a-machine.md, scripts/studio-logical-projects/check.mjs, scripts/studio-logical-projects/verify.mjs | Test: node scripts/studio-logical-projects/verify.mjs <owned report dir>

### T-07 PR, merge, release and installed check
- AC: all | Files: none | Test: PR Gate green; installed service version; link verified on the installed build between isolated test projects

### T-08 Verify and close 0948
