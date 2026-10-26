# 1046 Design system workspace and project-linked designs

Linked to 1041 (design creation and reuse, PR #660) and 0973 (design systems from code). Stacked on `fix/1041-design-create-reuse`.

## Problem

Anton, October 23, 2026: "I still don't see a way to start creating a design like the frontend right in the project itself so that they are kind of connected, do we have this link or storage? … each design file is related to a specific project, or it could be without a project. There are two ways: 1. You go to global design in the application and design something, and then you could connect it to a project. 2. You go directly to a project design option, like the board with the control where you could do this." Earlier the same day: "Rework how we exactly display and work with the design system … copy and represent every feature … preview when you click on a file must be working … also from scratch."

Evidence, from the codebase map at `/Users/antonabyzov/Projects/github/studio-research-notes/design-system-workspace-2026-10-24/codebase-map.md`:

- Storage already links designs to owners: a project's designs live in `<repo>/.specweave/design/<id>`, while Playground designs live in the app home and have no project. Nothing moves a design between owners. `design.copy` assigns a new id and starts a fresh history; it drops the thread binding and access, and it breaks every `/design/pg.<id>` link.
- The project design board exists as `/design?project=<id>`, but a project page offers no visible way to reach it. The header "more" menu has Plan, Usage, Routines and Open in new window only (screenshot `project-coordinator-…-e3833b50….png`). The Designs pane button appears only once a project already has a design.
- A design system is a single `system.json`. No page opens one, and after import there is no section view, token editing, file browser, file preview, asset storage or start-from-scratch path. The rename, delete and usage RPCs exist, but no screen calls them.
- Claude's desktop design-system artifact, the reference in nine screenshots plus `project-coordinator-…-01cea632….png`, has:
  - section navigation (Overview, Colors, Typography, Spacing, Corner radius, Shadows, Duration, Easing, Breakpoint, Z index, Control, Opacity, Components, Assets, Files);
  - token tables (colors as Name/Light/Dark with swatch, hex and alpha; typography roles with a live preview and font chip);
  - asset sets with upload;
  - a grouped file browser in which clicking a file previews it, with Download;
  - an artifact menu: Switch artifact, Rename, Duplicate, Share, Open in web, Refresh, Pin, Storage and Delete.

## Scope

In:

- A visible project design entry and board with creation already owned by the project.
- Projectless Playground creation with a later "Connect to a project", which moves the design and keeps its id, history, thread and links.
- "Add from Playground" on the project board.
- A design-system workspace page: sections, token tables with editing, components, assets, and files with click-to-preview and download.
- Starting a design system from scratch.
- Settings rows that open the page, with rename and delete.
- An artifact-style system menu.
- Headless evidence.

Out:

- Figma sync changes.
- Cross-machine moves: a Playground belongs to its own machine.
- Moving a project design back to the Playground.
- Rewriting designs when a token is renamed (the user is warned instead).
- Release and installed acceptance, which belong to the integration owner.

## Acceptance Criteria

- [ ] AC-01: A project page's "more" menu has "Design", which opens that project's design board (`/design?project=<id>`). The board is reachable with zero designs, scopes every create (New design, Design from code, New slides, New design system) to the project, and lists the project's design systems. Archived and automated projects follow the 1041 picker rule.
- [ ] AC-02: A design made from the global Design page without a project stays in the Playground. On a Playground design, "Connect to a project…" (gallery card menu and editor menu) moves it into an eligible project on the same machine. The move keeps the design id, revision, autosave history, named versions, comments, assets, access and thread binding. A design system the project lacks is copied in with the same id. Old `/design/pg.<id>` links redirect to the new address, and a bound Scratch thread moves into the project. A partial failure is reported with a retry and never leaves two editable copies.
- [ ] AC-03: The project board offers "Add from Playground…", which picks a Playground design and connects it using AC-02's move.
- [ ] AC-04: Each design system opens at its own page (`/design/systems/<key>`). Section navigation is derived from its tokens: Overview, Colors, Typography, Spacing, Corner radius, Shadows, Duration, Easing, Breakpoint, Z index, Control, Opacity, Components, Assets and Files with a count. Each section is a table in the reference layout: colors grouped as Name/Light/Dark with swatch, hex and alpha; typography roles with a live preview, a font chip and size steps; Name/Value tables for the rest. Components show sandboxed previews.
- [ ] AC-05: People can add, edit, rename and delete tokens and modes on the page. Each edit is saved with a revision check. A conflict saves nothing over the newer version: it stops further edits and offers Reload, and an open add dialog keeps what was typed so Add works again after Reload. An edit is stamped with user provenance. Agents cannot write through these RPCs. (Amended October 24, 2026; see D-06.)
- [ ] AC-06: Files lists the system's stored files, the generated `tokens.css` and `tokens.json`, and its recorded source files, grouped and captioned with where each is shown. Clicking any file previews it: markdown rendered, text, JSON and CSS as read-only source, images, and fonts as a specimen. Each preview has Download. Source files are read only through the existing root-confined reader with its secret exclusions, and only if the system lists them.
- [ ] AC-07: Assets holds named sets, stored as folders, with upload, delete and download, plus a storage footer showing the size used. Uploads are restricted to an allowlist of types and sizes, symlinks are refused, and paths cannot escape the system folder.
- [ ] AC-08: New design system has "Start from scratch". It creates an empty system with light and dark modes in the chosen owner and opens its page. Settings rows open the page. The page's menu offers Switch system, Rename, Duplicate (copy), Open in Settings, Rescan (for systems with sources), Storage, and Delete with a usage warning.
- [ ] AC-09: Version skew stays safe. New RPCs are gated by capability flags, older servers hide the new actions, no new literals are added to unions that are stored on disk, and new contract fields are optional.
- [x] AC-10: A headless fixture captures every new surface in light and dark at 360, 768 and 1280 px and at 200% zoom into `/Users/antonabyzov/.specwithcode/m4/evidence/design-system-workspace-1046/`. Source, merge and installed acceptance are recorded separately.

## Deferred (follow-up)

- L-4 (low): stored-file checks in `SystemFilesStore` can be raced between `lstat` and `open`. Needs an active local writer racing the app; static links are refused. Follow-up: re-check `dev`/`ino` after open, as `readInsideRoot` does.
- L-6 (low): an open editor drops unsaved edits when another window moves the design. The editor's own Connect flushes first.
- L-2 residual (low): Undo of a removed mode puts the mode back last instead of in its old position.
- Mode-delete Undo size (low): undoing a mode delete sends one `put_token` per token with a value in that mode (`systemEditIntents.ts`), so a system with more than 2,000 such tokens exceeds the 2,000-operation cap (`designSystemEdit.ts`) and the Undo toast reports "The change was not saved". Follow-up: batch the undo or restore the mode in one operation.
- R2-4 crash window (low): if the process stops between writing the forward record and placing a moved design, Playground edits to it are refused until Connect is run again; the rename that places the design keeps this window very short. Follow-up: finish or roll back pending moves at startup.
- F2 of the `fbdb1eaec2` review (medium, main code): `DesignStore.ts` `readJson` and `readDesignAsset` rely on `O_NOFOLLOW` alone, so on Windows they follow a linked record or asset file. Both predate 1046. The fix is a shared lstat-plus-identity open helper, as `fbdb1eaec2` added for stored system files and forward records. It belongs to a main-side Windows pass.
- F4 (low, Windows): a save that replaces a file between `readSystemFile`'s lstat and its open makes that read report "is a link" instead of reading the old or new bytes. Retry once on an identity mismatch.
- F5 (low): no test drives the swap branch (lstat sees one file, the open gets another).
- F6 (low): stored names accept Windows device names (`con`, `aux`, `nul`, `com1`, `lpt1`); refuse them on every platform so checkouts stay portable.
- F7 (low, Windows): a move whose destination folder appears mid-move surfaces as a raw EPERM instead of `conflict`; the rollback still runs.
- N1 (low, `b874c7188a` review): `onDiskName` matches folders case-insensitively with `toLowerCase`, so a planted folder spelled with a look-alike such as the Kelvin sign (U+212A) can take writes meant for `kits`. Such files stay out of the listing and the limits. Match only entries that pass `nameProblem`.
- N2 (low): file results report the spelling that was asked for, not the on-disk one. A move that changes only a folder's case reports success but renames nothing. Only a direct RPC reaches this; the UI does not.
- N3 (low, Windows): `readForward` maps every lstat error to null, not only ENOENT.

## Approach

The full plan, with file:line citations, is the codebase map's section D.

- **Move (AC-02, AC-03).** Add a contract `design.move` with `DesignError.movedTo`, plus capability `designMove`. A new `apps/server/src/design/DesignMove.ts` stages a copy of the folder (plain files only, without `.lock`), places it under the target, writes the forward record `<playground>/.moved/<id>.json`, then removes the source. A retry is idempotent. `DesignService.move` admits only the owner's own sessions. `get`, `watch` and `apply` return `movedTo` when the caller may see the target. On the web, the client calls move and then `thread.move-to-project` for a Scratch thread on this machine. The route replace-redirects on `movedTo`.
- **Project entry (AC-01).** A new `ProjectMoreMenu.tsx`, extracted from `ProjectWorkspaceSurface.tsx`, adds "Design" there. That file shrinks rather than grows. On the board in project scope, add a "Design systems" strip and "Add from Playground…".
- **System editing (AC-05 to AC-08).** A new contract file `designSystemEdit.ts` defines `designSystem.create`, `apply`, `files`, `fileRead`, `filePut` and `fileDelete`, with capability `designSystemEditing`. A shared reducer `packages/shared/src/designSystemOps.ts` recomputes `resolved`. On the server, `DesignSystemEditing.ts` and `SystemFilesStore.ts` store files under `systems/<id>/files/`, with an extension allowlist, `O_NOFOLLOW` and plain-folder checks. Sources are read through `readInsideRoot`. `systemCopy` and move also copy `files/`.
- **System page (AC-04, AC-06 to AC-08).** A route `design.systems.$systemKey.tsx`, with components under `apps/web/src/components/design/systems/workspace/`: section classifier, overview, token tables, components, assets, files browser, preview and menu. All use existing UI tokens and components.
- **Skew.** New state lives in files, not new `system.json` fields. Section placement uses the existing free-form `group`.
- **Risks.** A move adds untracked files to the user's checkout. Files are not part of a system's revision history. A token rename can orphan `{token}` references; the UI warns. `ProjectWorkspaceSurface.tsx` is already 1,753 lines and must not grow.

## Decisions

### Asked
- D-01 Where a project's designs live and how a projectless design joins a project → Anton, October 23, 2026: each design belongs to one project or none; both flows (global then connect, or start from the project board) are required.
### Defaulted (change any before sw-do)
- D-02 Connect moves rather than copies: the id, history, thread and links are kept, and an old link redirects (reversible: a copy stays available as Duplicate).
- D-03 Moving a project design back to the Playground, and moves across machines, are out of scope.
- D-04 The system page is a full route reached from the gallery, the board, Settings and the editor's picker, not a Settings-only view.
- D-05 Section placement for user-made tokens uses the existing `group` string; no new token types.
### Closure
- D-06 October 24, 2026, closure review: AC-05 said "a conflict asks before overwriting". The page never overwrites: a conflict stops edits and offers Reload, so another window's newer edit is never replaced without being seen. The fresh closure review recommended amending the AC rather than adding an Overwrite choice, because overwriting is the riskier behaviour. The design lane amended AC-05. `062fc44f61` keeps an open add dialog and its typed values through the conflict, so the edit is not lost.
- D-07 October 24, 2026, closure review: AC-10 screenshots cover every surface at all four sizes. Sub-states that need an interaction first are captured at 360 and 1280 px only, in light and dark: the open assets menu, the board add dialog, the project list in Connect, the add-dialog conflict notice, the saved edit, the JSON, source and SVG file views, and the Settings systems list. The fixture still runs its layout checks at all four sizes, so at 768 px and 200% zoom these sub-states are covered by those checks, not by screenshots.
### Open
- none

## Tasks

### T-01 Research: Claude design-system artifact and storage map
- AC: AC-01, AC-04 | Files: /Users/antonabyzov/Projects/github/studio-research-notes/design-system-workspace-2026-10-24/codebase-map.md, /Users/antonabyzov/Projects/github/studio-research-notes/design-system-workspace-2026-10-24/claude-design-system-re.md | Test: both files exist with file:line or screenshot citations

### T-02 Move a design between owners (contract and server)
- AC: AC-02, AC-09 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/packages/contracts/src/design.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/server/src/design | Test: vp test run apps/server/src/design packages/contracts/src/design.test.ts

### T-03 Connect to a project, project entry and board (web)
- AC: AC-01, AC-02, AC-03 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/components/design/gallery, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/components/studio/shell/ProjectMoreMenu.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/routes/design.$designKey.tsx | Test: vp test run apps/web/src/components/design/gallery apps/web/src/components/studio/shell

### T-04 Design system editing and files (contract, reducer, server)
- AC: AC-05, AC-06, AC-07, AC-09 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/packages/contracts/src/designSystemEdit.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/packages/shared/src/designSystemOps.ts, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/server/src/design/systems | Test: vp test run packages/shared/src/designSystemOps.test.ts apps/server/src/design/systems

### T-05 Design system page: sections, tables, components, files and preview
- AC: AC-04, AC-05, AC-06, AC-07 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/components/design/systems/workspace, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/routes/design.systems.$systemKey.tsx | Test: vp test run apps/web/src/components/design/systems

### T-06 Start from scratch, Settings wiring and system menu
- AC: AC-08 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/components/design/systems/NewDesignSystemDialog.tsx, /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/src/components/settings/DesignSystemsSettingsView.tsx | Test: vp test run apps/web/src/components/design/systems apps/web/src/components/settings

### T-07 Headless evidence for every new surface
- AC: AC-10 | Files: /Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-1046-design-workspace/apps/web/tests/design-workspace-1046 | Test: headless fixture, light and dark, 360/768/1280 px and 200% zoom; headless true, PWDEBUG=0, PLAYWRIGHT_HTML_OPEN=never

### T-08 PR and exact-head CI
- AC: AC-10 | Files: /Users/antonabyzov/.specwithcode/m4/evidence/design-system-workspace-1046 | Test: gh pr checks on the exact head; merge, release and installed proof stay with the integration owner

### T-09 Verify and close 1046
- AC: AC-10 | Files: /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/1046-design-system-workspace-and-project-designs/ledger.jsonl | Test: specweave verify 1046; fresh-context review; specweave complete 1046
