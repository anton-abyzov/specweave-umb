# Duplicate greet-app projects in sidebar

## Problem

On October 31, 2026 the M4 sidebar listed greet-app three times and greet-fleet twice among the user's own projects (EasyChamp, olysense, sketchmate, specweave). The phone showed the same before PR #1123.

Evidence (read through `specweave-studio db query` and the creating transcripts):

- The demo-video workflow (session `f1313591`, October 30, 2026 23:09 UTC) registered `greet-app-demo` under `~/.specwithcode/m4/scratch/2026-10-30-fleet-demo/` and `greet-app` under `~/Projects/experiments/greet-app-demo` over MCP. It first asked for `origin:"user"`, which MCP refuses, then created both with no origin. The greet-fleet coordinator registered `~/Projects/experiments/swc-demo-greet-fleet` the same way.
- The scratch copy is classified as automated by its folder. The two `~/Projects/experiments/*demo*` copies are not, so they sit among the user's projects.
- The same workflow called `studio_project_add_to_machine` for M1 (23:47 UTC), which cloned the repository there and created `mcp:c05f425c…`. `addProjectToMachine` stops after the remote `studio_project_create`: it never runs the link handshake. M4's greet-app still lists only its M4 member, M1's copy has its own logical id, and the sidebar shows M1's copies as separate remote-only rows labelled with M1's name ("Anton's MacBoo…"). greet-fleet's remote row has the same cause.

So nothing here is intentional. Two bugs: agent-made demo projects are not recognised as automated, and an agent's add-to-machine leaves the copy unlinked.

## Scope

In: link the copy `studio_project_add_to_machine` makes into the source project's logical project; carry an automated origin to the copy; classify `demo` folders as automated on web, server and iOS. Out: deleting or archiving any project (the user does that; candidates are listed in the report), relinking copies that already exist (the app's Link… flow does that), and the earlier iOS listing fix (PR #1123, already merged).

## Acceptance Criteria

- [ ] AC-01: `studio_project_add_to_machine` with a `projectId` runs prepare on this machine, accept on the target and commit here, so the source project lists the target copy as a member and the copy adopts the same logical id; the result says `linked: true`.
- [ ] AC-02: When the target cannot link (an older version without the accept tool, a refusal or a fingerprint mismatch), the copy is kept and the result says `linked: false` with the reason and how to link it in the app.
- [ ] AC-03: The accept step is reachable only from another machine's worker grant that covers every project, and through the remote tool allowlist; a local agent cannot call it.
- [ ] AC-04: A copy of an automated project is created with `origin:"automated"` on the target.
- [ ] AC-05: A project whose folder path has a `demo` word (`greet-app-demo`, `swc-demo-greet-fleet`) is automated in the shared classifier and in iOS `ProjectOrigin.swift`; a saved origin still wins.
- [ ] AC-06: Released, installed on the M4, with the sidebar showing no greet rows among the user's projects, and the iOS simulator drawer the same.

## Approach

1. `apps/server/src/mcp/toolkits/project/tools.ts` and `handlers.ts`: new `studio_project_link_accept` tool, input and result `ProjectLinkAcceptInput`/`ProjectLinkAcceptResult`, handler calls `ProjectLink.accept`. It refuses callers without a work grant and grants that do not cover every project, like `studio_project_clone`.
2. `apps/server/src/fleet/RemoteStudioMcpClient.ts`: add it to `REMOTE_TOOL_ALLOWLIST`.
3. `apps/server/src/mcp/toolkits/project/addToMachine.ts`: after create, `ProjectLink.prepare` (joining = target environment and created id), remote accept, `ProjectLink.commit` with the accepted member and no notes. Failures after create return `linked:false` with a reason. Pass `origin:"automated"` to the remote create when the source is automated.
4. `packages/shared/src/projectOrigin.ts` and `apps/ios/SWCKit/Sources/SWCWire/ProjectOrigin.swift`: add `demo` to the folder words.

Rejected: letting `studio_project_create` accept a `logicalProject` (any agent could then adopt another project's identity without the fingerprint and refusal checks `accept` runs); hiding remote-only rows on desktop (real projects on other machines are listed on purpose).

Risk: a person's real project in a folder named like `*-demo` moves to Automated; Move to my projects saves their choice and it always wins.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 `demo` counts as an automated folder word → yes (Move to my projects overrides).
- D-02 Existing unlinked copies are not relinked automatically → the user links or archives them.
### Open
- none

## Tasks

### T-01 Link the copy add-to-machine makes
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/server/src/mcp/toolkits/project/addToMachine.ts, apps/server/src/mcp/toolkits/project/tools.ts, apps/server/src/mcp/toolkits/project/handlers.ts, apps/server/src/fleet/RemoteStudioMcpClient.ts, apps/server/src/mcp/toolkits/project/addToMachine.test.ts | Test: cd apps/server && npx vitest run src/mcp/toolkits/project/addToMachine.test.ts

### T-02 Demo folders are automated
- AC: AC-05 | Files: packages/shared/src/projectOrigin.ts, packages/shared/src/projectOrigin.test.ts, apps/ios/SWCKit/Sources/SWCWire/ProjectOrigin.swift | Test: cd packages/shared && npx vitest run src/projectOrigin.test.ts

### T-03 Release and installed check on M4 and the iOS simulator
- AC: AC-06 | Files: .specweave/increments/1157-duplicate-greet-app-projects-in-sidebar/evidence | Test: defaults read /Applications/SpecWithCode.app/Contents/Info CFBundleShortVersionString

### T-04 Verify and close 1157
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: .specweave/increments/1157-duplicate-greet-app-projects-in-sidebar | Test: specweave verify 1157
