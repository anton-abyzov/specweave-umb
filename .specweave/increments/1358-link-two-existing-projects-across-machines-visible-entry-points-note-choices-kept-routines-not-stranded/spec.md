# Link two existing projects across machines: visible entry points, note choices kept, routines not stranded

## Problem

Anton has a `specweave` project on the M4 and an older, separately added `specweave` project on the M5. He wants them to become one project without copying again. The app can link them (`projectLink.prepare/accept/commit`), but a two-server reproduction on `origin/main` at `a7fb7a5175` (November 15, 2026; evidence in `~/.specwithcode/m4/evidence/link-existing-project/run16` and `run17`) showed four problems:

1. **The entry is hard to find.** Anton: "where exactly? I don't see it". The sidebar offer is a 14 px link glyph with `role="img"`, no text and no tooltip of its own. **Link…** sits in a Machines section of the Settings "Project" page, which the Settings sidebar lists only when Settings was opened for a project. The machine menu under the composer lists the other copy as "separate project" and offers no link.
2. **Note choices are not kept.** In the link dialog the person picked "Keep M4" for `MEMORY.md` and "Keep both" for `shared.md`. One sync pass later both machines held `MEMORY.md` and `shared.md` with `<<<<<<<` conflict markers, because the joining copy still held its own text and the two-way memory merge saw two unrelated edits.
3. **The joining copy's routines are stranded.** After the link, the M5 project's own routine cannot run, be turned off or be deleted on the M5 ("change, run or delete it there"), and the M4 never received it. The dialog does not mention routines.
4. **No confirmation from the sidebar.** A link started from the sidebar closes the dialog the moment it finishes, without the "Projects linked" step.

What already works and stays as is: one logical project with the kept coordinator active; project ids, threads, goal and instructions stay on their own machine; notes only the joining copy has are copied; Copy to another machine into the existing folder keeps a local branch, uncommitted edits and untracked files.

## Scope

In: a link action in the project's machine menu; a readable sidebar offer; the confirmation step from the sidebar; note choices that survive the first memory sync; a routines notice in the link dialog; turning off and deleting a stranded routine; user docs. Out: moving routines to the coordinator; changes to the folder-copy engine; merging threads or coordinator conversations; the stale pairing step in `scripts/studio-fleet/add-to-machine-live`.

## Acceptance Criteria

- [x] AC-01: In the machine menu under the composer, a copy of the same repository on another machine that is not linked shows "Link with the project on <machine>…", which opens the link dialog on that copy.
- [x] AC-02: The sidebar offer shows the visible word "Link" with a tooltip naming the other project and machine. It is a mouse shortcut inside the project row (hidden from assistive technology, since a button cannot nest in the row button); the row menu item "Link with <project> on <machine>…" is the keyboard and screen reader path. Clicking it opens the link dialog and does not open the project.
- [x] AC-03: A link started from the sidebar shows "Projects linked" until the person chooses Done.
- [x] AC-04: After linking with "Keep <kept machine>" or "Keep both" for a note that differs, the first memory merge leaves the kept machine's text under that name on both machines, with no conflict markers and no `.conflict-` copy. "Keep both" also leaves `<name>-<machine>.md` on both. A joining server that sends no note hashes behaves as before.
- [x] AC-05: The link dialog's review lists the joining copy's routines that stop running (title and count) and says they run only on the coordinator's machine. Nothing is listed when there are none or the server predates the field.
- [x] AC-06: On a copy that does not coordinate, a routine that is not a copy from the coordinator can be turned off and deleted there. Turning it on, editing and running it stay refused, and copies from the coordinator stay refused for every change. This covers the joining copy's own routines after a link. Routines on a machine that handed the coordinator of the same project to another machine keep their existing behaviour (they are marked as that project's copies and stay refused).
- [x] AC-07: `docs/user/shared-projects.md` names the three entry points as they appear, and says what merges and what does not (threads, memory, goal and instructions, routines, files).

## Approach

Work in the verification copy of `anton-abyzov/specwithcode` on branch `fix/1358-link-existing-projects`.

- Contracts (`packages/contracts/src/projectLink.ts`): optional `contentSha256` on each preview note; optional `routines` (id, title) on the preview; optional `superseded` (name, contentSha256) on the commit input. All optional, so old and new servers interoperate.
- Server (`apps/server/src/project/ProjectLink.ts`): preview fills the two fields; commit records each superseded hash as an ancestor in `LinkedMemoryHistory` for that file, so `planMemoryMerge` sees the kept text as the newer version (`theirsIsKnown`) and the joining copy takes it.
- Server (`apps/server/src/scheduledTasks/ScheduledTaskService.ts`): `setEnabled(false)` and `delete` skip the resting refusal for a row without `copiedFrom`.
- Web: `OrchestratorSwitcher.tsx` gains `onLink`; `SidebarProjectList.tsx` renders the offer as a button; `useProjectLinkSuggestions.tsx` keeps the dialog until Done; `ProjectLinkDialog.tsx` sends `superseded` and shows the routines notice.
- Rejected: copying the joining copy's routines to the coordinator at link time. It needs the coordinator's models and grants checked for each routine and changes who owns them; a notice plus a way to remove them is the smaller, reversible step.
- Risk: a hash recorded for a note the person later edits on the joining machine before the first merge. The merge then sees the edit as unknown and falls back to today's behavior, which keeps both texts.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The joining copy's routines are not moved to the coordinator; the dialog names them and they can be turned off or deleted (reversible: a later increment can move them).
- D-02 The link action goes in the machine menu and the sidebar; the Settings "Project" page row stays where it is.
### Open
- none

## Tasks

### T-01 Note choices survive the first memory merge
- AC: AC-04 | Files: [repositories/anton-abyzov/specwithcode/packages/contracts/src/projectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectLink.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectLink.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx] | Test: from apps/server, `node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectLink.test.ts`; from apps/web, `node ../../node_modules/vite-plus/bin/vp test run src/studio/projectLink.test.ts`

### T-02 Routines notice and removable stranded routines
- AC: AC-05, AC-06 | Files: [repositories/anton-abyzov/specwithcode/packages/contracts/src/projectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/scheduledTasks/ScheduledTaskService.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectLinkDialog.test.tsx] | Test: from apps/server, `node ../../node_modules/vite-plus/bin/vp test run src/scheduledTasks`; from apps/web, `node ../../node_modules/vite-plus/bin/vp test run src/components/studio/ProjectLinkDialog.test.tsx`

### T-03 Link entry points and confirmation
- AC: AC-01, AC-02, AC-03 | Files: [repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/SidebarProjectList.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/useProjectLinkSuggestions.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/shell.css, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases] | Test: from apps/web, `node ../../node_modules/vite-plus/bin/vp test run src/components/studio/OrchestratorSwitcher.test.tsx src/components/studio/shell`

### T-04 Docs and two-server proof
- AC: AC-07, AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: [repositories/anton-abyzov/specwithcode/docs/user/shared-projects.md, repositories/anton-abyzov/specwithcode/docs/studio/logical-projects.md, repositories/anton-abyzov/specwithcode/scripts/studio-logical-projects/link-existing.mjs] | Test: build apps/web and apps/server, then `node scripts/studio-logical-projects/link-existing.mjs /absolute/report/dir` exits 0
