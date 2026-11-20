# Machine menu says what differs per repository, and Sync sees every nested repository

## Problem

On M5, the composer's machine menu for the specweave project shows m4, linux-mini and m1 each with an orange chip "1 of 1 repositories differ" (Anton, November 20, 2026, `reports/screens/machine-menu-before.png`). The project folder holds six repositories: the umbrella root and five clones under `repositories/anton-abyzov/` (specweave, specweave-status, specwithcode, vskill, vskill-platform). Anton asked why the count is one of one, whether a chip is the right form, and for multi-repository projects to be handled properly.

## Findings (code read on `1434-account-switch-cleanup`, which matches `origin/main` `311d73cfa` for these files)

**1. Sync's scan gives up on the whole folder when it meets one link to a folder.** `projectSync.status` lists repositories with `handoffGit.discover` (`apps/server/src/fleet/ProjectSync.ts:614`). That walk was written for a machine handoff and refuses a tree with any directory symlink: `unsafe-path` at `apps/server/src/fleet/handoffGit.ts:271`. Sync catches every such refusal and falls back to the root alone with `scanLimited: true` (`ProjectSync.ts:616-629`).

Measured on M5: the project folder has 204 directory links outside `node_modules` (10 in `.claude/skills`, 191 inside the nested clones, mostly vskill's 40 tracked links and installed skills). Nine of them are tracked in the umbrella (`.claude/skills/sw-*` pointing at `.agents/skills/`), so every checkout of the umbrella has them. The walk itself is inside its limits (12,462 of 20,000 folders, 94,000 of 200,000 entries). So n = 1 is the root, and the five nested repositories are never read.

On m4, linux-mini and m1 this is inferred, not measured: they hold the same tracked links, so the same fallback applies. T-08 confirms it per machine.

**2. The chip hides that the scan was cut short.** `machineSyncFact` counts differences before it looks at `scanLimited` (`apps/web/src/studio/machineRowState.ts:76-92`). A limited scan can never read "Same", but it reads "1 of 1 repositories differ" with no sign that five repositories were skipped.

**3. Every row is orange because of M5's own files.** A repository differs when either side has uncommitted files (`machineRowState.ts:80`). M5's root has 70 uncommitted files (increment records), so all three rows differ whatever the other machines hold. The difference belongs to M5, and the chip puts it on m4, linux-mini and m1.

**4. The chip says nothing a person can act on.** The status carries `path`, `branch`, `head` and `clean` per repository (`packages/contracts/src/projectSync.ts:77`), and the menu reduces it to two numbers. It does not name the repository or say how it differs (other branch, other commit, uncommitted files, missing).

**5. Orange is the wrong tone.** Since November 19 every machine runs its own coordinator on its own branches (`decision_sync_and_hand_off`). Machines differing is the normal state, so a warning colour on every row trains the eye to ignore it.

**6. The app already has the right repository list, in another module.** `ProjectRepositoryDiscovery.ts` (increment 1276) finds the clones a project's threads can use: a walk three levels deep that skips dot and dependency folders and does not abort on links, joined with the repositories `.specweave/config.json` declares and the saved Environment repositories. It finds exactly the five nested clones here (they are in this thread's project context). The umbrella's config declares only three of them, so the declared list alone would miss specwithcode and specweave-status. A walk for every `.git` would also pick up `tmp/free-series/test-free-lane-1.0.192/state/repo`, a test fixture that no other machine has.

## Scope

In: Sync lists the project's repositories from the same discovery the rest of the app uses; the status carries what a per-repository comparison needs; the menu row states the difference in words, with a per-repository list on hover, focus or press; single-repository projects never read "1 of 1"; the eight phrase catalogs; a headless fixture with before and after captures.

Out: the handoff walk (`handoffGit.discover` keeps refusing links for handoffs); the Sync dialog's plan and steps beyond receiving the longer repository list; Add to another machine; the folder copy behind "Compare all files…"; phone apps.

## Acceptance Criteria

- [ ] AC-01: In a project folder that holds nested clones and directory links (the umbrella's shape: root plus five clones, links in `.claude/skills` and inside a clone), `projectSync.status` returns the root and every nested clone, follows no link, and reports `scanLimited: false`. A linked worktree, a clone staging folder and a clone deeper than the discovery's depth are not listed, as today.
- [ ] AC-02: A nested folder that cannot be verified as a repository of its own (its `.git` is a link, or Git names another top level) is listed `unread` and the other repositories are still read. Only a discovery that stopped at its folder budget sets `scanLimited`.
- [ ] AC-03: Each repository's status adds optional `uncommitted` (count), `upstream`, `ahead` and `behind` (against its local `origin` ref, no network) and `origin` (owner/name). A machine on an older version omits them, and the menu then says less, never something false.
- [ ] AC-04: Given the other machine's commits for the repositories whose commits differ, a machine answers per repository `same`, `ahead`, `behind` (with counts), `diverged` or `unknown` when it does not have that commit, from local Git alone. An older machine without this call yields "Other commit".
- [ ] AC-05: The row's chip for a machine that differs is neutral in colour and says: the one repository and how it differs when exactly one differs ("vskill: 2 commits behind M5"); "{k} of {n} repositories differ" when several do; and for a single-repository project the difference alone ("Other branch", "2 commits behind M5", "Uncommitted files"), never "1 of 1".
- [ ] AC-06: Uncommitted files on the machine shown are a note on its own row ("70 uncommitted files") and do not by themselves make another machine's row differ. "Same as {shown}" still needs equal commits and no uncommitted files on that other machine.
- [ ] AC-07: Hovering, focusing or pressing the chip opens a list "{machine} compared with {shown}" with one line per repository, differing ones first: Same; Other branch (both names); N commits ahead or behind; Diverged; Other commit; N uncommitted files on {machine}; Only on {machine}; Could not be read. It names when the status was read, is reachable by keyboard and by touch, and pressing the chip does not switch the machine shown.
- [ ] AC-08: When either side's scan was limited, or one side is on a version that lists only its root, repositories that side did not list read "Not checked on {machine}", never "Only on …", and the chip says "Only the root was checked" with "needs update" where the version is the cause. This is the only orange chip besides "Could not compare".
- [ ] AC-09: Sync's dialog plans over the same list, so nested clean checkouts are fetched and fast-forwarded like the root, under the unchanged rules (nothing pushed, reset, merged, stashed or switched). A repository on one machine only is offered through the existing clone step.
- [ ] AC-10: All new phrases exist in the eight catalogs, and headless before and after captures of the menu (umbrella with six repositories, single-repository project, one older machine), light and dark, are in `reports/screens/`.

## Approach

Mockup: `reports/mockup-machine-menu.html` (today beside proposed).

**Repository set (server).** `ProjectSync.repositories` stops calling `handoffGit.discover`. It takes the root plus the clones `discoverProjectRepositories` finds inside the project folder, by path relative to the root, leaving out any reached through a link. Each path then passes the per-repository checks the handoff walk made (real folder, `.git` not a link, Git's top level is the folder); one that fails is `unread`, where today it aborts the whole scan. `syncRepositories` keeps removing staging folders and linked worktrees. The set is the one the Environment page, launches and worktrees already show, so the menu and the rest of the app agree on what the project's repositories are. `handoffGit.discover` is untouched: a handoff moves files and keeps its guard.

**Status fields (contract).** `ProjectSyncRepositoryStatus` gains the optional fields of AC-03, read by the code that already computes them for the Sync plan (`projectSyncFacts.ts`), without the fetch. A new call `projectSync.relate` takes up to 128 `{path, head}` pairs and answers with `git merge-base --is-ancestor` and `rev-list --left-right --count` when the commit exists locally. The window asks the machine shown, once per opened list, only for repositories whose commits differ.

**Row and list (web).** `machineSyncFact` returns the summary plus a `repositories` array of per-repository findings; a new `MachineSyncDetail.tsx` renders it in the existing `popover.tsx`. The chip becomes a button inside the row with its own press handling. `SYNC_PILL.differs` becomes the neutral border; a new `limited` tone carries orange.

**Mixed versions.** New fields are optional and `relate` is detected by its "unknown method" answer, as Sync itself is today (`needs-update`). An older machine keeps returning its root alone with `scanLimited: true`, which AC-08 words honestly.

Rejected:
- Skip only `.claude/skills` in the handoff walk. 191 of the 204 links are inside the nested clones, and loosening a handoff guard to fix a menu is the wrong trade.
- List every `.git` under the folder. It picks up test fixtures and scratch clones that no other machine has, and the 20,000-folder limit is 62% used here already.
- Use only the repositories declared in `.specweave/config.json`. This umbrella declares three of five, and a project without SpecWeave declares none.
- Keep the orange chip and add a tooltip. The count would still be wrong and the colour would still cry wolf.
- Compare by ahead and behind against `origin` alone. Each machine's `origin` refs are as old as its last fetch, so two machines on the same commit could read differently.

Risks: Sync starts moving nested repositories on machines that until now only moved the root (AC-09, D-02). The list can be slower with many repositories: status reads stay four at a time and `relate` runs only when the list opens.

## Decisions

### Asked
- none yet

### Defaulted (change any before sw-do)
- D-01 Tone of a row that differs → neutral; orange only when the comparison is incomplete or failed (reversible).
- D-02 Sync also fetches and fast-forwards nested clean checkouts once they are listed → yes, the 1390 rules already cover several repositories (reversible; the alternative is to list them in the menu and leave Sync on the root).
- D-03 Detail form → a popover on the chip, opened by hover, focus or press; no extra row or dialog (reversible).
- D-04 Repository set → the project's discovered clones (1276), not every `.git` and not the declared list alone (reversible).
- D-05 M5's own uncommitted files → shown on M5's row and in the list, not counted against other machines (reversible).

### Open
- none

## Tasks

### T-01 Sync lists the project's discovered repositories
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/projectSyncGit.ts, repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectRepositoryDiscovery.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.nested.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/ProjectSync.nested.test.ts src/fleet/ProjectSync.test.ts src/fleet/ProjectSync.service.test.ts src/project/ProjectRepositoryDiscovery.test.ts

### T-02 Status carries uncommitted count, upstream, ahead, behind and origin
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/projectSyncFacts.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.results.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/ProjectSync.results.test.ts

### T-03 projectSync.relate answers ahead, behind, diverged or unknown from local Git
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/packages/contracts/src/projectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/projectSyncRelate.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/projectSyncRelate.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/ws.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/projectSync.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/server && npx vp test run src/fleet/projectSyncRelate.test.ts

### T-04 Row fact: named difference, neutral tone, own files on own row, limited scans said
- AC: AC-05, AC-06, AC-08 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.ts, repositories/anton-abyzov/specwithcode/apps/web/src/studio/machineRowState.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useProjectSyncMenu.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/useProjectSyncMenu.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/studio/machineRowState.test.ts src/components/studio/useProjectSyncMenu.test.ts src/components/studio/useProjectSyncMenu.hook.test.tsx

### T-05 Per-repository list on the chip
- AC: AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineSyncDetail.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/MachineSyncDetail.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/OrchestratorSwitcher.test.tsx | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/studio/MachineSyncDetail.test.tsx src/components/studio/OrchestratorSwitcher.test.tsx

### T-06 Sync dialog plans over the nested repositories
- AC: AC-09 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSyncDialog.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/projectSyncDialog.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/server/src/fleet/ProjectSync.nested.test.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/components/studio/projectSyncDialog.logic.test.ts src/components/studio/ProjectSyncDialog.test.tsx

### T-07 Phrases in eight catalogs, fixture and captures
- AC: AC-10 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/sync/zh.ts, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/main.tsx, repositories/anton-abyzov/specwithcode/apps/web/tests/coordinator-menu/verify.mjs | Test: cd repositories/anton-abyzov/specwithcode/apps/web && npx vp test run src/i18n/i18n.test.ts && node tests/coordinator-menu/verify.mjs

### T-08 Confirm on the real machines and close
- AC: AC-01, AC-05, AC-08 | Files: .specweave/increments/1435-machine-menu-says-what-differs-per-repository-and-sync-sees-every-nested-repository/reports/live-check.md | Test: on M5 with the released build, open the machine menu for specweave and record each row's chip and list for m4, linux-mini and m1 (six repositories listed per machine on the new version, "Only the root was checked" for one still on the old version) in reports/live-check.md with a capture per row
