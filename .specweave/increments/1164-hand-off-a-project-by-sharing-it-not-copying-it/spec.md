# Hand off a project by sharing it, not copying it

## Problem

The handoff dialog copies the project folder by default and shows a review screen, and the coordinator window shows a folder-difference banner afterwards. The owner wants one project on many machines instead (decided 2026-11-02, "Share notes, clone on demand"): the other machine gets the project's settings, memory and repository list, clones what each task needs, and only Git moves code. Memory and the repo list must stay in sync both ways, and consolidate when the coordinator moves back.

## Scope

In: a minimal dialog (pick a machine, "Add <machine>": clone the project's own repo from Git, link, share settings and memory; "Also move the coordinator there" as a checkbox; "Copy files instead" under More options); removing the review step and the folder-difference banner from the default path; server-side continuous sync of memory and the repo list between linked copies; three-way memory consolidation when the coordinator returns. Out: moving worker transcripts; the repository list and worker brief (#1168).

## Acceptance Criteria

- [ ] AC-01: The handoff dialog opens on one choice, a machine and an "Add <machine>" button; that path clones the project's repo from Git, links it as a workers copy and shares goal, instructions and memory, with no file copy and no review screen.
- [ ] AC-02: "Also move the coordinator there" moves the coordinator over the same path; "Copy files instead" stays available under More options; a project without a Git remote says so and offers the copy.
- [ ] AC-03: The coordinator window no longer shows the folder-difference review for a copy added this way.
- [ ] AC-04: Memory and the repository list sync between linked copies from server to server, without an open app window.
- [ ] AC-05: When the coordinator moves back, each memory file merges against the last shared version; non-overlapping edits merge, a real clash becomes one file flagged for the coordinator, not .conflict copies.

## Approach

Step 1 reuses Add to another machine (apps/server/src/mcp/toolkits/project/addToMachine.ts, apps/web/src/components/chat/AddToMachineDialog.tsx) behind the handoff dialog (ProjectMachineHandoff.tsx, ProjectMoveOptions.tsx). Step 2 moves linked memory sync from the web app loop to the server. Step 3 keeps the last shared revision per file as the merge base. The repository list comes from #1168: the note repositories.md (a table plus a machine-readable list in an HTML comment), built from the coordinator's folder and matched by remote, travels like any note; a remote worker's first message names each repo and tells it to reuse an existing clone or clone on demand. There is no pre-launch clone. Consolidation merges repositories.md's list section by key.

## Decisions

- D-01 Default is share and clone on demand; copy is the rare option (owner, 2026-11-02, repositories thread).

## Tasks

### T-01 Minimal handoff dialog: Add machine by clone and link
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/studio/ProjectMachineHandoff.tsx, apps/web/src/components/studio/ProjectMoveOptions.tsx | Test: cd apps/web && npx vp test run src/components/studio

### T-02 Server-side sync of memory and repository list
- AC: AC-04 | Files: apps/server/src/project | Test: cd apps/server && npx vp test run src/project

### T-03 Consolidate memory when the coordinator moves back
- AC: AC-05 | Files: apps/server/src/fleet, apps/server/src/project | Test: cd apps/server && npx vp test run src/fleet src/project

### T-04 Verify and close 1164
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1164-hand-off-a-project-by-sharing-it-not-copying-it
