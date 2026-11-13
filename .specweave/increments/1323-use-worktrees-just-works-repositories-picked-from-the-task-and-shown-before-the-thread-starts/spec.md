# Use worktrees just works: repositories picked from the task and shown before the thread starts

## Problem

Anton, November 13, 2026: "if I enable worktrees, is it mandatory to use repositories, or will it be smart enough to understand which repositories to use automatically, or connect for this project and display it in our environment? Rethink this as well."

Registration is not mandatory today. Increment 1276 (PR 196, November 12, 2026) made every Git clone in the project folder available with nothing to register, listed them on Environment > Repositories, and gave a thread with Use worktrees on in a folder of separate clones its own folder, adding a worktree of each repository it changes (`studio_worktree_add_repository`). What still reads as "not smart" (code on `origin/main` a16c229716, November 13, 2026):

1. A thread that names no increment and no repository always starts with no repository, even when its message names one by path. `emptyThreadFolderLaunch` (`apps/server/src/mcp/toolkits/project/launchWorkspace.ts:143`) never reads the task. Its header says "No repository yet" until the agent adds one, and the composer's "Repositories: Agent decides" gives no hint of what will happen.
2. An increment's task `Files` are owned by a saved Environment repository or a `repositories/<owner>/<repo>` folder only (`apps/server/src/project/incrementRepositories.ts:105-140`). In a folder of separate clones laid out any other way (`services/api` with its own `.git`), a file under that clone is credited to the project folder's own repository, so the thread gets the wrong worktree.
3. The agents' project context still prints the saved entries as raw JSON next to the found list (`apps/server/src/project/ProjectWorkspaceService.ts:555-572`). For this project it shows two saved `specwithcode` entries, one with `"localPath": null`, and an approved folder inside the project folder, all of which 1276 already marks as redundant on the Environment page (AC-16, AC-19). It does not say whether Use worktrees is on, so a reader cannot tell what a launch will do. The coordinator's own brief for this increment read the list as if registration mattered.
4. A project with clones but no goal, instructions, files or saved folders gets no environment section at all (`ProjectWorkspaceService.ts:515-525`, 1276 closing review), so its agents never see the found list.

## Scope

In: picking a launch's repositories from its task text; the composer showing that pick live; increment `Files` owned by any found clone; one repository list in the agents' project context with the switch state and the no-Git case; the found list for projects with no other context. Mockup and options: `reports/options-mockup.html`.

Out: anything 1276 shipped (discovery, Environment > Repositories, the thread chip and popover, "Add repository", guards, cleanup) beyond the lines named here; deleting saved entries (the Environment page's "Remove both" stays the person's click); the mobile composer (it gets the server pick with no live hint); 1276's remaining closing-review items (add-lock race, `realpath` in `resolveWorktreeSetRepositories`, packed `origin/HEAD`, `existing_worktree` names, Windows cmd guard), which stay follow-ups.

## Acceptance Criteria

Picked from the task

- [ ] AC-01: With Use worktrees on, in a project folder of separate clones, a launch that names no increment and no repository (MCP launch, composer "Agent decides", routine, mobile, older client) starts with a worktree of each available found repository its message names: the repository's path relative to the project folder or a file under it (`repositories/anton-abyzov/vskill/src/cli.ts`), the same inside an absolute path from any machine (`/Users/x/umb/repositories/anton-abyzov/vskill`), or the repository's name or relative path in backticks (`` `vskill-platform` ``) when that name is unique. A bare word never counts, so product names in prose (SpecWithCode, specweave) pick nothing. The longest path wins: `repositories/anton-abyzov/specwithcode-dev/x.ts` never picks `specwithcode`. A one-segment path (`api`) counts only with a file under it (`api/src/x.ts`) or in backticks. Inside a word, a mention must start the word or follow `./`, an option (`--dir=`) or an absolute path at least one folder deep, so `src/api/x.ts`, the route `/api/users`, `@acme/web/x` and `github.com/acme/api` name nothing.
- [ ] AC-02: More than 4 named repositories reads as a list, not a task: the thread starts with none and the notice lists them as named. Nothing named: the thread starts with no repository, as today. A name that matches no available repository on this machine is ignored and never fails the launch, and a named clone with no commit to start from (a fresh `git init`) is left out and named in the notice.
- [ ] AC-03: The thread's first message says what it started with and why, for example "This thread starts with a worktree of vskill (repositories/anton-abyzov/vskill), because its task names repositories/anton-abyzov/vskill/src/cli.ts." followed by 1276's rules (add others with `studio_worktree_add_repository`, no installs, do not edit the project folder's clones). The launcher's tool result says the thread starts with a worktree of each repository its message names by path.
- [ ] AC-04: Explicit choices win unchanged: a launch's `repository`, `repositories` or `{type:"root"}`, a composer pick, an increment (AC-05), and Use worktrees off (`WORKTREE_OFF_NOTICE`). A project that is one repository with no separate clones still gets its single worktree, and a folder with no Git repository still works in the folder.

Increments

- [ ] AC-05: An increment's task `Files` path belongs to the deepest saved checkout or found clone that holds it, in any layout, before the `repositories/<owner>/<repo>` and project-root fallbacks. `metadata.json` `repositories` still wins. 1276's increment tests pass unchanged.

The composer

- [ ] AC-06: In a project folder of separate clones, while the composer's worktree launch is on "Agent decides", the Repositories chip shows, only when the server reports the folder holds separate clones (`separateClones` on the environment read), the pick the server will make from the draft as it is typed: "Repositories: Agent decides · vskill", "· 2 named", or plain "Agent decides" when nothing is named. The popover's "Agent decides" line reads "Starts with vskill, named in your message. The agent adds others the task changes." The web and the server call the same function (`packages/shared`), so the hint is the launch.

What agents read

- [ ] AC-07: The agents' environment section shows one repository list. Saved entries the found list covers (1276's `redundantEntries`) are left out of the JSON, and so are approved folders inside the project folder; nothing saved is changed. A line states the switch: "Use worktrees is on for this project: a new thread gets its own folder with a worktree of each repository its task names, and adds others with studio_worktree_add_repository." or "Use worktrees is off for this project: threads work in the project folder." A folder with no Git repository says "This folder holds no Git repository, so threads work in the folder." (a folder that is not a repository and holds no clone of its own says the same in other words, whatever the switch). A clone with no origin is listed as "no remote" and can be picked; its worktree has no pull request.
- [ ] AC-08: A project whose folder holds separate clones gets the environment section even with no goal, instructions, files or saved folders.

Remote machines

- [ ] AC-09: The pick runs where the thread launches, against that machine's folder and its own switch: a launch forwarded to another machine carries the message, and a relative path (or an absolute path from the coordinator's machine) names the same repository there. A repository that machine has not cloned is not picked and does not fail the launch (AC-02).

Proof

- [ ] AC-10: A headless fixture renders the composer's Repositories chip and popover with a named repository, in light and dark at 1440 and 390 wide, with no horizontal overflow; screenshots are saved to this increment's `reports/`.

## Approach

All code paths are inside `repositories/anton-abyzov/specwithcode-dev/`.

1. `packages/shared/src/taskRepositories.ts` (new, exported as `@specweave-studio/shared/taskRepositories`): `repositoriesNamedInTask(text, repositories)` returns `{ picked, named }`, each entry `{ relativePath, name, evidence }`, in order of first mention. Pure string work, no Node APIs, so the web composer and the server share it.
2. `launchWorkspace.ts`: `emptyThreadFolderLaunch` takes the message text, picks with (1) from the available found repositories, and returns `repositories: [picked paths]` with the new notice; `ThreadLaunchService.withEmptyThreadFolder` passes `input.initialMessage?.text` before it appends the notice. `EMPTY_THREAD_FOLDER_NOTICE` (handlers' launcher line) says the thread starts with the repositories its message names. Nothing else in the launch path changes, so remote launches (forwarded `studio_thread_launch`) get the pick on the worker.
3. `incrementRepositories.ts`: `incrementRepositoryCandidates` takes the found clones' paths as extra owners (no id, relative path entries); `incrementWorktreeSetRepositories` reads them from `discoverProjectRepositories` (cached 60 s).
4. `ProjectWorkspaceService.ts`: the environment JSON drops redundant saved entries and in-folder approved folders, adds the switch or no-Git line (switch read with `Effect.serviceOption(ServerSettingsService)` and `projectUsesWorktrees`, no new layer requirement), and the early empty return also requires a folder without separate clones.
5. Web: `BranchToolbar.tsx` reads the draft prompt from `composerDraftStore`, `composerRepositoriesLabel` and `ComposerRepositoriesControl` (`BranchToolbar.logic.ts`, `WorkspaceModeControl.tsx`) show the pick. No new RPC: `environmentRead({discover:true})` already gives the found list.
6. Fixture: extend 1276's `apps/web/tests/environment-repositories` harness with a composer state whose draft names a repository.

Options considered (mockup `reports/options-mockup.html`):

- A. Agent adds as it goes (1276 today). No disk until a change, but the thread says "No repository yet" even when the task names one, and the composer cannot say what will happen.
- B. Picked from the task, shown live (chosen). The repositories the task names by path are checked out at launch, the composer shows that pick as you type, the agent adds the rest. Questions with no paths still cost nothing. Risk: a path named only for reading ("compare with repositories/x") gets a worktree it did not need; a worktree shares Git objects and installs nothing, and the 4-name list rule stops a pasted inventory from checking out everything.
- C. Ask every time. The composer requires a pick and MCP launches must name repositories. Precise, but it puts back the registration-like step Anton asked to remove (A-01 in 1276: "the decision will be made by the model").

Rejected inside B: matching bare names in prose (every message here says SpecWithCode and specweave); matching `owner/name` origins (two checkouts share `anton-abyzov/specwithcode`, and pull request links would pick repositories for read-only reviews); remembering picks per project (1276 D-04).

Review (Sonnet 5.5, PR 340): four findings fixed in the same PR: one-segment false positives (path start rule), a no-commit clone failing the thread (commit check before the pick), the composer hint outside folders of separate clones (`separateClones` on the read), and the switch line for a folder that is not a repository. Left: a picked clone whose checkout fails for another reason (an LFS error) still fails the thread, as an explicit pick does today.

Risks: `ProjectWorkspaceService` context churn when the switch flips (one section revision, intended); `BranchToolbar.tsx` re-rendering on every keystroke (the pick is memoized on prompt text and found rows, and the component already subscribes to the draft store); an absolute path to another folder that happens to end in the same relative path (same repository by name, low harm).

## Decisions

### Asked
- none (A-01 in 1276 stands: every repository is available, the model decides; this increment makes the task's own words part of that decision)
### Defaulted (change any before sw-do)
- D-01 Option B: repositories named by path in the task are checked out at launch and shown in the composer before sending.
- D-02 More than 4 named repositories picks none (a list, not a task).
- D-03 Only paths and backticked names count; bare words and origins never do.
- D-04 Saved entries are hidden from agents only when 1276 already calls them redundant; they are never deleted without the person's click on the Environment page.
### Open
- none

## Tasks

### T-01 Shared: repositories a task names
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode-dev/packages/shared/src/taskRepositories.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/src/taskRepositories.test.ts, repositories/anton-abyzov/specwithcode-dev/packages/shared/package.json | Test: specweave-studio checks copy repositories/anton-abyzov/specwithcode-dev --ref 1323-task-repositories >/dev/null && specweave-studio checks run -- sh -c 'cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/packages/shared && pnpm run test taskRepositories'

### T-02 Server: launch picks from the task; increment files owned by found clones
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-09 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/project/launchWorkspace.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/mcp/toolkits/project/launchWorkspace.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/orchestration-v2/ThreadLaunchService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/incrementRepositories.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/incrementRepositories.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectRepositoryDiscovery.ts | Test: specweave-studio checks copy repositories/anton-abyzov/specwithcode-dev --ref 1323-task-repositories >/dev/null && specweave-studio checks run -- sh -c 'cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/apps/server && pnpm run test launchWorkspace incrementRepositories ThreadLaunchService project/handlers'

### T-03 Server: one repository list and the switch in the agents' context
- AC: AC-07, AC-08 | Files: repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/projectEnvironmentContext.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/projectEnvironmentContext.test.ts | Test: specweave-studio checks copy repositories/anton-abyzov/specwithcode-dev --ref 1323-task-repositories >/dev/null && specweave-studio checks run -- sh -c 'cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/apps/server && pnpm run test projectEnvironmentContext ProjectWorkspaceService'

### T-04 Composer: the pick shown live under Agent decides
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/BranchToolbar.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/BranchToolbar.logic.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/BranchToolbar.logic.test.ts, repositories/anton-abyzov/specwithcode-dev/apps/web/src/components/chat/WorkspaceModeControl.tsx, repositories/anton-abyzov/specwithcode-dev/packages/contracts/src/projectEnvironment.ts, repositories/anton-abyzov/specwithcode-dev/apps/server/src/project/ProjectEnvironmentService.ts | Test: specweave-studio checks copy repositories/anton-abyzov/specwithcode-dev --ref 1323-task-repositories >/dev/null && specweave-studio checks run -- sh -c 'cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode/apps/web && pnpm run test BranchToolbar.logic'

### T-05 Headless fixture: composer pick, light and dark, 1440 and 390
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode-dev/apps/web/tests/environment-repositories/main.tsx, repositories/anton-abyzov/specwithcode-dev/apps/web/tests/environment-repositories/verify.mjs | Test: specweave-studio checks copy repositories/anton-abyzov/specwithcode-dev --ref 1323-task-repositories >/dev/null && specweave-studio checks run -- sh -c 'cd /Users/antonabyzov/.specwithcode/m4/verify/specwithcode && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node node_modules/vite-plus/bin/vp build --config apps/web/tests/environment-repositories/vite.config.ts && node apps/web/tests/environment-repositories/verify.mjs /Users/antonabyzov/.specwithcode/m4/evidence/1323-composer'

### T-06 Verify and close 1323
- AC: AC-10 | Files: .specweave/increments/1323-use-worktrees-just-works-repositories-picked-from-the-task-and-shown-before-the-thread-starts/spec.md | Test: gh pr view 340 --repo anton-abyzov/specwithcode --json state,mergeCommit -q '.state+" "+.mergeCommit.oid' | grep -x 'MERGED ed88e2c04cee9ffebbef3f37679e1449c9102ce9'
