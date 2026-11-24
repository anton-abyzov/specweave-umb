# Recognize existing project copies before adding to another machine

## Problem

Add still offers a full copy after the files have arrived, including through GitHub. A folder can exist without being a registered SpecWithCode project. The reported example is fortnite-3js on M5 at /Users/anton/Projects/fortnite-3js: the user reports a clean GitHub clone matching linux-mini, but it is absent from M5's project list. This is supplied evidence, not reverified by this planning task.

The supplied screenshot shows “Add fortnite-3js to m1”, a destination path, all files, checked secrets, project memory and “Copy to m1”. It gives no existing-copy status. The machine list must distinguish availability, project membership and repository/file comparison.

## Scope

In: bounded read-only discovery on the destination; registering and linking an existing folder without transferring repository files; state-driven Add dialog and machine list; optional review of differences; completion refresh and retry safety. Desktop web, including its narrow layout, all eight phrase catalogs.

Out: implementation during this assignment; PR creation; new Git comparison engine; automatic whole-disk search; changing grants/auth; automatic conflict resolution; moving coordinators or threads; native phone UI. No actual project registration or sync is performed by this plan.

Depends on 1435 for repository enumeration, relation and display facts, and 1390 for Sync/Add semantics. Do not supersede or edit those increments. Their shared files are sequential integration points after their owners finish. This increment owns discovery of unregistered folders and action routing, which 1435 explicitly excludes.

## Acceptance Criteria

- [ ] AC-01: Opening Add checks the destination's registered linked projects, registered same-repository projects, suggested folder and bounded project roots. An unregistered matching checkout at a different path is offered with its actual absolute path; no clone, fetch, file transfer or registration occurs during discovery. Checks report completion, limits and read time.
- [ ] AC-02: Matching uses canonical remote identity (host and repository, credential-free SSH/HTTPS equivalents) plus project-relative location inside the repository. A matching commit or folder name alone is insufficient. Same remote with different commits remains a candidate. Forks, different hosts and different subprojects are distinct; multiple matches require a folder choice. Unsupported/absent identity requires explicit folder selection and review, never an automatic match.
- [ ] AC-03: A unique unregistered match reads “Folder found on {machine}” and offers “Use existing folder on {machine}”. Its preview says that the app will register the folder and share the project's goal, instructions and memory, without copying repository files. Completing it creates one registered linked project at that exact path, leaves Git/worktree/ignored/secret files unchanged and opens that machine's project. Retries and concurrent attempts do not create duplicate registrations or links.
- [ ] AC-04: An already registered unlinked candidate reads “Project found · not linked”. Linking uses the existing ProjectLink preview, showing any destination goal, instructions and memory that would be replaced. Existing threads stay attached to their project. Cancel changes nothing; a project already belonging to a different logical project is not silently reassigned. An already linked copy reads “Already on {machine}” with Open and Review differences, never a default full-copy button.
- [ ] AC-05: Repository status and details use 1435's exact comparison data and wording for same commits, branches, ahead/behind, divergence, uncommitted work on each machine, missing and unread repositories. Equal commits do not imply equal ignored files, secrets or memory. Until separately compared, say “Local files and secrets not checked”. Partial nested-repository coverage never reads “Everything matches”.
- [ ] AC-06: Review differences delegates Git work to the existing Sync plan and local file work to Compare all files. The review groups uncommitted/untracked work, eligible ignored data, secrets and project context, naming source and destination. Only selected differences transfer; unchanged content is skipped. No automatic deletion, reset, merge, stash, branch switch or overwrite of destination changes occurs. Conflicts require the existing explicit per-file choice. A dirty/diverged repository may be linked without syncing.
- [ ] AC-07: Ordinary Sync extras remain unticked under 1390; selecting a transfer of local files exposes the existing explicit secrets checkbox, checked by default when the authorized secret route is available. Unchecking sends none. Sign-ins never travel. Tracked-secret warnings and sanitized Git config from 1328 remain; the sealed secret route and destination grants are unchanged. Secret contents never appear in discovery/comparison responses, telemetry or logs. Project context conflicts use ProjectLink's preview rather than file-copy overwrite.
- [ ] AC-08: Machine rows group “On this project” separately from “Add or link”, with reachable existing projects still selectable. A found folder gets “Folder found · use existing”; a missing suggested path after a bounded search says “No copy found in checked folders”, with Browse on the target and Add choices. Offline, disconnected, denied, checking, incomplete and needs-update states never become “No copy” or “Same”. The checked roots/limits appear under Details. No search of every machine's disk runs merely by opening the machine menu.
- [ ] AC-09: Before register/link/apply, the destination revalidates canonical path, repository identity, registration, grants and the comparison revision. A changed/deleted/replaced folder, a changed preview, or a new registration returns to review. Symlink escape, submodule/worktree internals and unsafe roots are not silently adopted. A failed link after registration reports “Added on {machine}; linking needs retry” and retries against that same project ID without copying or deleting files.
- [ ] AC-10: On successful clone, copy, link or sync, project membership and comparison caches refresh on all affected views. Reopening Add after a GitHub clone completed in the app shows Already on or Folder found, never starts a second clone. An external GitHub clone appears on the next explicit recheck. A reload can recover an interrupted link using its operation ID.
- [ ] AC-11: Headless fixtures cover same-commit external clone at another path, linked clean and dirty copies, different commits, several candidates, occupied unrelated folder, no remote, partial umbrella scan, old/offline machine, permission refusal and drift between preview and apply. Keyboard and touch can choose candidates and read status; 390 px and desktop captures in light/dark show no clipped path/action. New phrases exist in all eight catalogs.

## Approach

### Existing code and dependencies

Read-only inspection of the shared app checkout on November 20, 2026 found:
- packages/shared/src/existingCopy.ts already matches registered copies by logical membership, then repository identity and relative project location, and detects several matches.
- apps/web/src/studio/addToMachine.ts destinationPlan distinguishes clone, consolidate and refuse, but only for the inspected path.
- apps/web/src/components/chat/AddToMachineDialog.tsx inspects the chosen path and starts a source scan; it has no discovery of an unregistered checkout elsewhere.
- apps/server/src/sourceControl/SourceControlRepositoryService.ts owns inspectDestination.
- apps/server/src/fleet/folderCopyRegistration.ts already reuses a project registered at the same workspaceRoot, but it is tied to a copy result.
- apps/web/src/studio/addToMachineCopy.ts has conflict choices and refuses take-theirs on diverged repositories. Reuse this machinery rather than add another transfer route.

The supplied screenshot may be from a different deployed revision. At implementation time trace every Add entry point in the current 1390 code, including Settings and the folder-copy route, to the same discovery state. Do not revive removed HandoffShare components or the old main/extra coordinator language.

### Discovery contract

Add a destination-side project-copy query and guarded adoption command. Return bounded candidate records: canonical path, registration/logical membership, credential-free repository identity, project-relative path, identity confidence, checkedAt, completeness and supported capabilities. Repository facts come from 1435's shared reader. An unregistered candidate gets a short-lived destination-issued inspection handle bound to path, source identity, grant and revision; do not accept arbitrary client paths through projectSync as a shortcut.

Search in order: registered project records; the suggested exact path; the destination's configured projects root; its platform home Projects directory (when distinct); a root explicitly chosen with Browse. Search at most three directory levels per configured root, 5,000 entries total and 5 seconds; return partial results immediately at a limit. Skip dependency/cache/dot directories and all symlinks, do not descend into discovered repositories looking for separate copies. Reuse platform path handling and safe repository inspection. Roots must be within the caller's existing permitted scope. No credentials are needed and no network Git command runs.

A candidate's root remote identifies the project; 1435 checks nested repositories after selection. An umbrella with missing nested clones is still an existing umbrella, with an incomplete/different repository set. Unsupported non-Git projects use the existing explicit folder comparison, without claiming identity by name. Worktrees may be shown as requiring manual review; never adopt an internal .git or staging folder.

### UI states and actions

| Destination state | Title/status | Primary action | Secondary |
| --- | --- | --- | --- |
| Checking | Checking {project} on {machine} | disabled | Cancel |
| Unregistered match | Folder found on {machine} | Use existing folder on {machine} | Choose another folder |
| Registered unlinked | Project found · not linked | Review link to {machine} | Open separately |
| Linked | Already on {machine} | Open on {machine} | Review differences |
| Several matches | Choose a folder on {machine} | Continue after selection | Browse on {machine} |
| None in checked roots | Add {project} to {machine} | Download from GitHub | Copy whole folder / Browse |
| Offline/denied/old build | Could not check {machine}, with reason | Retry or existing connection/update action | Cancel |
| Occupied unrelated path | This folder holds another project | Choose another folder | Cancel |

Use existing folder is a clear registration/link action, not a combined hidden sync. The next view offers Review differences if useful. Already on describes presence, not byte equality. Status detail is 1435's component, not a second set of comparison labels. “Everything matches” is unnecessary; show the scope actually checked. The machine list uses neutral status text, with orange only for failed/limited checks as in 1435.

Mockup: reports/mockup.svg (two primary states, a machine menu, and the differences review). Values and counts in it are illustrative, not live observations.

### Linking and differences

Use ProjectService and the existing ProjectLink prepare/accept/commit transaction. Do not bootstrap a project by faking a completed copy. An operation receipt records the canonical target and created/reused project ID so reload and retry can resume; failed linking leaves a visible registered project and a recoverable link operation. Existing destination metadata is never silently replaced. Do not start work or move conversations merely by linking.

Git differences use 1390 Sync with 1435's repository list. Non-Git differences remain behind Compare all files, including its drift checks, conflict review and unchanged-file skipping. Secrets are unavailable until the existing route permits them; do not invent a general secret hash API. Compare context via existing ProjectLink revisions and preview. LAN transport from 1334 remains a whole-folder-copy optimization only; discovery/link-only does not trigger it or a transfer.

### Integration and verification

Read project_checkout_queue again before any future app edit; this planning assignment has not acquired or changed the shared app checkout. 1435 and 1390 retain ownership of their work. Integrate after their API shape settles; do not duplicate their comparison code to bypass that dependency. Keep files under 1,500 lines by extracting the discovery pane/state helper.

Tests below are future focused checks, not claimed results. Full lint/typecheck/suites, if required, run only through specweave-studio checks run in its managed checks copy. Headless browser checks use product preview tools when available and save evidence. Final verify/closure happens only after implementation and its required review, not when this plan is delivered.

## Decisions

### Asked
- None. This assignment explicitly requests a plan and mockup only.

### Defaulted (change any before sw-do)
- D-01 Prefer link-only for an existing folder. Optional sync follows as a separate reviewed action, so finding files does not imply permission to overwrite them.
- D-02 Search known project locations with explicit budgets, never the whole disk. Browse covers other locations; incomplete search is stated.
- D-03 Same remote plus project-relative location identifies candidates; commit equality is only comparison evidence.
- D-04 Keep 1390's opt-in Sync extras and the existing checked secret choice inside an explicitly selected local-file transfer. Registration alone sends no secret files.
- D-05 Do not eagerly scan every machine. Menu shows registered/cached facts, selected destination triggers fresh bounded discovery.

### Open
- None requiring a user decision. These reversible defaults are ready for review.

## Tasks

### T-01 Destination discovery, adoption and retry contract
- AC: AC-01, AC-02, AC-03, AC-04, AC-09 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectCopies.ts, repositories/anton-abyzov/specwithcode/packages/contracts/src/clientRpcPermissions.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectCopies.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectCopiesRpc.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectCopies.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectLink.ts, repositories/anton-abyzov/specwithcode/apps/server/src/sourceControl/SourceControlRepositoryService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/observability/RpcInstrumentation.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts, repositories/anton-abyzov/specwithcode/packages/shared/src/existingCopy.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/project/ProjectCopies.test.ts src/project/ProjectLink.test.ts src/sourceControl/SourceControlRepositoryService.test.ts

### T-02 One destination state across Add, machine menu and completion
- AC: AC-03, AC-04, AC-05, AC-08, AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCopies.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectCopies.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/addToMachine.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AddToMachineDialog.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/ExistingProjectCopy.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AddToMachineDialog.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AddProjectToMachine.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/AddProjectToMachine.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/AddToMachineJobRunner.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/AddToMachineJobRunner.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/studio/projectCopies.test.ts src/components/chat/AddToMachineDialog.test.tsx src/components/studio/OrchestratorSwitcher.test.tsx src/components/settings/AddProjectToMachine.test.tsx src/components/AddToMachineJobRunner.test.tsx

### T-03 Route selected differences through existing Sync and copy review
- AC: AC-05, AC-06, AC-07, AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AddToMachineConsolidate.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/chat/AddToMachineConsolidate.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/studio/addToMachineCopy.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/addToMachine.verify.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && node ../../node_modules/vite-plus/bin/vp test run src/fleet/addToMachine.verify.test.ts src/fleet/FolderCopyHandoff.updating.test.ts

### T-04 Localize and capture the full state matrix headlessly
- AC: AC-08, AC-11 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/project-copies/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/project-copies/vite.config.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/project-copies/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/i18n/i18n.test.ts && node ../../node_modules/vite-plus/bin/vp build --config tests/project-copies/vite.config.ts && node tests/project-copies/verify.mjs

### T-05 Verify and close 1439
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10, AC-11 | Files: .specweave/increments/1439-recognize-existing-project-copies-before-adding-to-another-machine/reports/ | Test: specweave verify 1439

After implementation, record focused checks, headless captures and required fresh-context review in reports; then complete via sw-done. The increment remains planned and open while the user reviews this proposal.
