# Set up Git and SpecWeave in one click for new projects

## Problem

On M5 (1.0.345) Anton made "firstproject" in first-run setup by picking an empty folder (`/Users/anton/Projects/firstproject`). Board > Set up SpecWeave > "Run specweave init" stopped with red text: "SpecWeave needs a Git repository: this folder is not one. Run git init here first, then try again." The app offers no way forward, so a project started from scratch cannot get SpecWeave.

Evidence, gathered read-only on M5 on November 18, 2026:

- The project was created by command `onboarding:project:create:37415680-…`. First-run setup's folder pick binds the folder with `project.create` and never runs `git init`. The New project form (`projects.createNew`) does run it, followed by a first commit.
- `SpecweaveSetup.run` (`apps/server/src/project/SpecweaveSetup.ts`) refuses any folder outside a Git work tree. The guard is deliberate: outside a repository, `specweave init` runs its own `git init`, `git add .` and commit, which would commit every file in the folder.
- A worker in that project ran `specweave create-increment` and wrote `.specweave/increments/0001-simple-website-with-beautiful-scrolling-and-animation/` (spec.md, plan.md, metadata.json) with no `.specweave/config.json`. It did so because `resolveLaunchIncrement` returns the "Plan it first: specweave create-increment" brief for `increment: "new"` without checking whether the project uses SpecWeave. The Board hides the folder because the project still reads as not using SpecWeave.
- Git on M5 has no global `user.name`, so any commit the app makes there fails.

## Scope

In:
- First-run setup's folder pick creates the project through `projects.createNew` when the server supports it. An empty, unclaimed folder then gets `git init`, the starter files and a first commit; a folder with files is bound as-is, as today.
- An empty folder that holds only OS litter (`.DS_Store`, `Thumbs.db`, `desktop.ini`) counts as empty.
- The SpecWeave setup card on a folder outside any Git work tree offers one button, "Set up Git and SpecWeave". It runs `git init`, then `specweave init`, and keeps the description of what gets added.
- Ticking Use SpecWeave for an existing folder in New project gets the same Git step.
- Increment folders written before SpecWeave was set up appear on the Board after setup, without a migration step.
- With SpecWeave off, `increment: "new"` and `"none"` no longer brief workers to run `specweave create-increment` or `small-fix`. The coordinator gets a warning that suggests setting SpecWeave up.

Out:
- Committing the person's existing files. Their changes stay uncommitted for review.
- The coordinator's wider onboarding wording. The "Onboarding rethink: Chrome and key setup" thread owns it and gets the finding.
- Changes to the specweave CLI. The Git check lives in SpecWithCode.

## Acceptance Criteria

- [x] AC-01: In first-run setup, choosing an empty folder (or one holding only `.DS_Store`) creates the project as a Git repository with a first commit when Git has an identity. Without an identity the project is still created and the commit failure is reported softly. A folder with files is bound without any file change.
- [x] AC-02: When the project folder is not inside a Git work tree, the workspace read returns `gitRepository: false`, and the SpecWeave setup row shows "Set up Git and SpecWeave" in place of "Run specweave init", keeping the description of what gets added. There is no dead-end red text.
- [x] AC-03: `projects.specweaveSetUp` with `initGit: true` runs `git init` in a folder with no `.git` in it or any parent, then `specweave init`, and stages nothing. It then attempts an empty first commit so branches and worktrees have a base; that commit's failure is soft. Without `initGit` the server returns today's message unchanged, for older clients.
- [x] AC-04: Git that cannot start, or times out, is reported as such and not as "not a repository". A folder inside a parent repository is still refused.
- [x] AC-05: After setup, an increment folder that existed under `.specweave/increments/` before `specweave init` (like firstproject's 0001) stays in place and shows on the Board.
- [x] AC-06: In a project without SpecWeave, `delegate_task`/`create_threads`/`studio_thread_launch` with `increment: "new"` or `"none"` give the worker a brief that says SpecWeave is off and asks it not to create increment folders. The launch result carries a warning that offers setup from the Board.
- [x] AC-07: firstproject on M5, after the release, gets SpecWeave from the Board's one button, and 0001 appears on its Board.

## Approach

1. `packages/contracts/src/projectWorkspace.ts`: add the optional key `gitRepository` to the read result, optional `initGit` to the set-up input, and optional `gitInitialized` to the result. The error's `needs` literal stays as it is, so older clients still decode it.
2. `SpecweaveSetup.ts`: `setUp(cwd, { initGit })`. Split the `rev-parse` outcomes into spawn failure, timeout, and not-a-repository. For not-a-repository with `initGit`, walk the parents for `.git` on disk and refuse if one is found. Otherwise run `git init --initial-branch=<init.defaultBranch|main>`, then run the CLI. The CLI sees `.git` and skips its own add and commit. Then try `git commit --allow-empty -m "Initial commit"` and ignore a failure.
3. `ProjectWorkspaceService.ts`: return `gitRepository` from a bounded on-disk walk for `.git`, and pass `initGit` through. `ManagedProjectFolders.addSpecweaveToExisting` passes `initGit: true`, because ticking Use SpecWeave is the request. `isUnclaimedEmptyFolder` ignores OS litter.
4. Web: `ProjectSpecweaveSetting` takes `gitRepository`. When it is false, the button reads "Set up Git and SpecWeave" and the description adds the Git step. First-run setup `ProjectsStep` uses `projects.createNew` for the folder pick when the server supports it, and falls back to `project.create` otherwise.
5. `launchIncrement.ts`: "new" and "none" check for SpecWeave like the inherit path does. With SpecWeave off they return `SPECWEAVE_OFF_BRIEF` and a warning.

Rejected alternatives:
- Letting `specweave init` run its own `git init`. It commits the whole folder, secrets included.
- A data migration of increment folders. The tested CLI keeps them, so none is needed.
- A new error `needs: "git"` literal. Older clients would fail to decode it.

Risks:
- A new button label breaks a release walker that clicks "Run specweave init". Check the scripts that use it.
- `projects.createNew` names the folder from its title. For a folder pick the title is the folder's base name, so `existingProjectFolder` always resolves the chosen folder itself.

## Decisions

### Asked
- none (the task names the behaviour)
### Defaulted (change any before sw-do)
- D-01 First commit after "Set up Git and SpecWeave" is empty (`--allow-empty`); the person's files and SpecWeave's are left uncommitted for review, matching the existing "left for you to review and commit" rule.
- D-02 Ticking Use SpecWeave on an existing non-Git folder in New project also runs `git init` (consent is the tick).
### Open
- none

## Review

Adversarial review: muse-wonder-full-1.0 at xhigh (taskClass review, runtime full-access), as Anton asked.

## Tasks

### T-01 Server: Git step in SpecWeave setup and the read hint
- AC: AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectWorkspace.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/SpecweaveSetup.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ManagedProjectFolders.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vitest run src/project/SpecweaveSetup.test.ts src/project/ManagedProjectFolders.test.ts

### T-02 Web: one-click "Set up Git and SpecWeave" and Git for first-run folder picks
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectSpecweaveSetting.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/onboarding/ProjectsStep.tsx, repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectWorkspace.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vitest run src/components/studio/ProjectWorkspaceSettings.test.tsx src/components/onboarding

### T-03 Launch briefs respect SpecWeave being off
- AC: AC-06 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/launchIncrement.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/launchIncrement.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vitest run src/project/launchIncrement.test.ts

### T-04 Review, merge, release, verify on M5
- AC: AC-07 | Files: .specweave/increments/1392-set-up-git-and-specweave-in-one-click-for-new-projects/reports/ | Test: on M5, Board of firstproject shows 0001 after "Set up Git and SpecWeave"
