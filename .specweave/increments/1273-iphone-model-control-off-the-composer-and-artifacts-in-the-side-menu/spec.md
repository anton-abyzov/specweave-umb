# iPhone model control off the composer and Artifacts in the side menu

Mockup: [reports/mockup/mockup-full.png](reports/mockup/mockup-full.png), source page `reports/mockup/mockup.html`.

Related: 1264 (which artifacts count as deliverables), 1268 (inline media in messages and the thumbnail variant of signed asset URLs). This increment adds no inline media and no new deliverable rule.

## Problem

Anton's report from November 10, 2026, on an unfolded iPhone Duo (`~/Downloads/Screenshot 2026-11-10 at 2.59.19 PM.png`):

> "maybe the model could also be moved to the right because you could accidentally click on it every time you do something. Also, there is no way to see artifacts, for example, those reports, right? There should also be, maybe on the side menu, a button or a way to see it."

Two separate gaps in the native app (`apps/ios`, bundle `com.specwithcode.ios`):

- **The model pill is in the composer's tap zone.** PR #106 added `ModelOptionsMenu` to `composerArea` (`apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift:825-854`). Its label is the model plus every trait ("Claude Opus 5.5 · 1M · Medium Fast · Ultracode · Thinking On"), so on a thread it grows to the composer's full width, 46 points tall, about 10 points above the text field. A tap aimed at the text field or the plus button opens the options menu.
- **The app has no artifacts view.** There is no artifact model, list or `projects.libraryRead` call in `apps/ios`. A report, page, deck or image a thread produced can only be found by scrolling its transcript. The web app has had a project shelf and library since before 1264 (`apps/web/src/components/studio/shell/ProjectArtifactShelf.tsx:612`).

A third, smaller one shows in the same screenshot: the left column's mode chips truncate to "Coor…" and "Th… 1" beside the machine picker.

## Scope

In:

- The model control leaves the composer row and becomes one button in the thread control group: the header on a phone, the status rail on an unfolded Duo.
- The thread subtitle names the model.
- An Artifacts screen for a project: list, kind filters, viewer, share.
- Three ways in: a side menu row, a third mode chip beside Coordinator and Threads, and "Artifacts in this thread" in the thread menu.
- Mode chips that show an icon and a count when the column is tight.
- Unit and UI tests, and simulator screenshots on the Duo and a folded phone.

Out:

- Inline media in messages, the thumbnail variant itself, and agent guidance. Those are 1268.
- Pinning, hiding and registering artifacts from the phone.
- The Expo client in `apps/mobile`, web and desktop.
- A model control on the coordinator and Aide composers. Their sends take no model today.
- Files owned by the iPhone fixes worker: `Support/SpeechDictation.swift`, `project.yml` version fields, and release tooling.

## Acceptance Criteria

- [ ] AC-01: On a thread, nothing tappable sits between the transcript and the composer except the task progress pill and the provider checklist, when a thread has them. A thread with neither shows no row there, and the transcript is taller by that row.
- [ ] AC-02: The thread control group starts with a Model options button (44 by 44 points, Lucide `sliders-horizontal`, accessibility label "Model options", identifier `chat.model-options`). On a phone it is in the header, to the left of the machine button. On an unfolded Duo with the status rail it is the top button of the rail capsule.
- [ ] AC-03: The button opens the same options as today (every trait control, Access, and the "apply from your next message" note) with the full model and trait summary as the menu's title. It shows the iris dot while a change is not sent yet. Choosing an option changes the next send exactly as before; `ModelOptionsUITests` passes against the new button.
- [ ] AC-04: The thread subtitle ends with the short model name ("Thread in specweave · m4 · Opus 5.5"). When it does not fit, the model name is the last part to go.
- [ ] AC-05: Below 375 points of width the button is not drawn, and the thread menu has a "Model options" submenu with the same controls.
- [ ] AC-06: The side menu on a phone has an "Artifacts" row under Aide. It opens the Artifacts screen for the project last opened, with a project switcher in the title. With no project yet, the row is hidden.
- [ ] AC-07: The left column's modes are Coordinator, Threads and Artifacts. When the three labels do not fit beside the machine picker and gear, each unselected chip shows its icon and count only, and no chip text ends in an ellipsis at any width from 320 to 760 points.
- [ ] AC-08: The Artifacts screen lists the project's deliverables newest first under Today and Earlier. Each row has a 48-point thumbnail or kind icon, a title, and a line with the kind, the source thread when known, and the age. Filter chips are All, Reports, Pages, Images and Video, each hidden when it would be empty. Logs, code and data files are not listed, by the same rule and the same test vectors as web.
- [ ] AC-09: Tapping a row opens it: Markdown reports in the app's Markdown view, HTML pages and `html_render` results in a web view with no access to the app's storage, images and video in the native viewer, links in the in-app browser. The viewer has a share button and a link to the source thread. Bytes load through the thread's server or Connect with a signed asset URL, never a raw path.
- [ ] AC-10: On an unfolded Duo, choosing the Artifacts mode shows the list in the left column and the selected artifact in the right pane. The rail capsule then holds Share and the item menu. Folding the phone keeps the opened artifact on screen.
- [ ] AC-11: The thread menu's "Artifacts in this thread" opens the same screen filtered to that thread, including `html_render` pages and files the thread's replies link to. A thread with none shows no menu item.
- [ ] AC-12: Empty, loading, offline and older-server states each have their own text: "No artifacts yet", a skeleton list, "Can't reach m4" with Retry, and "Update SpecWithCode on m4 to see artifacts" when the server lacks `projects.libraryRead`.
- [ ] AC-13: Image rows use the `thumb` variant when the server offers it (1268 AC-05) and a kind icon otherwise. No row downloads a full-size image to draw a thumbnail.
- [ ] AC-14: Simulator screenshots, before and after, on the unfolded Duo and on a 393-point phone, cover the thread, the open menu, the side menu and the Artifacts list and viewer. `HitTargetAuditUITests`, `DuoFoldUITests` and `AdaptiveLayoutUITests` pass.

## Approach

All paths are under `apps/ios/SWCKit/Sources/` unless they start with `apps/` or `packages/`.

1. **Model control.**
   - `SWCFeatures/Chat/ModelOptionsMenu.swift`: split the label from the menu body. Add an icon-only label style and a title section carrying the full summary. Export the body as a view builder so the thread menu can host it as a submenu.
   - `SWCFeatures/Chat/ChatView.swift`: remove the pill from `composerArea`; add the button as the first item of `threadControlButtons`, which already moves between the header and the rail. Gate it on `showsModelOptions` and on width.
   - `SWCFeatures/Chat/ChatKind.swift` (`ChatKindLine`): append the short model name.
2. **Mode chips.** `SWCFeatures/Drawer/ColumnHeader.swift`: add the `.artifacts` mode, and use `ViewThatFits` to fall back from labels to icon and count.
3. **Data.**
   - `SWCWire/ProjectLibrary.swift` (new): decode `ProjectLibrarySnapshot` and `ProjectThreadReportsSnapshot` from `packages/contracts/src/projectLibrary.ts`.
   - `SWCSync/Artifacts.swift` (new): the artifact model, kinds, the deliverable rule, and the per-thread derivation from `file_change` items, linked files and `html_render` dynamic tool items (`SWCWire/TurnItem.swift:60`).
   - `SWCSync/LiveEngine+Artifacts.swift` (new): `projects.libraryRead` and `projects.threadReportsRead`, with the older-server case. `SWCSync/FixtureEngine.swift`: fixture artifacts.
4. **Shared rule.** Move the deliverable test vectors out of the web unit test into `packages/shared/src/artifactDeliverable.vectors.json`, read by both the web test and the Swift test, so the two rules cannot drift.
5. **Screens.**
   - `SWCFeatures/Artifacts/ArtifactsView.swift`, `ArtifactRow.swift`, `ArtifactViewer.swift` (new).
   - `SWCFeatures/Navigation/Router.swift`: routes `.artifacts(project, thread?)` and `.artifact(id)`.
   - `SWCFeatures/Drawer/DrawerView.swift` and `SidebarView.swift`: the row.
   - `SWCFeatures/RootView.swift`: the Artifacts mode puts the list in the navigation column and the viewer in the detail pane.
6. **Icons.** `Weave/Components/ProjectAvatar.swift` (`WeaveLucide`): add `library`, `file-text`, `presentation`, `film`, `image`, `globe`, `link`, `share`. The app keeps drawing SF Symbols mapped from Lucide names.

Rejected:

- **Right-aligning the pill in the same row.** It stays 10 points above the send and stop buttons, the most tapped spot on the screen.
- **Shrinking it to a chip inside the composer bar.** It crowds the mic and send buttons and still sits in the typing zone.
- **A bottom sheet for options.** One more tap for every change, and the native menu already works with VoiceOver.
- **An artifacts strip above the composer.** That is the tap zone this increment clears.
- **A tab bar.** The app's navigation is the drawer and the column modes.

Risks:

- The phone header gets a third control. At 375 to 392 points the title has about 150 points; AC-05 covers narrower.
- `html_render` pages run their own scripts. The viewer uses a non-persistent web view with no app cookies and no JavaScript bridge.
- Thread-derived artifacts exist only for threads whose turn items the phone has loaded; the project list is the server's.

## Decisions

### Asked
- none

### Defaulted (change any before sw-do)
- D-01: The model control lives with the machine and thread buttons (header on a phone, rail on the Duo), not on the composer's right edge.
- D-02: The subtitle shows the short model name only; traits appear in the menu title.
- D-03: The side menu row opens the last project's artifacts with a switcher, not a list across all projects. A cross-project list would need one request per project and per machine.
- D-04: Read-only in this increment: no pin, hide or register on the phone.
- D-05: Mode chips fall back to icon and count rather than scrolling.
- D-06: The coordinator and Aide composers stay as they are.

### Open
- O-01: 1268's T-00 and T-04 list files under `apps/mobile` (the Expo client), but the App Store iPhone app is `apps/ios`. Its owner should confirm which client AC-01 and AC-04 of 1268 mean. If it is `apps/ios`, 1268 owns `SWCFeatures/Chat/ChatAttachments.swift` and the Markdown image view, and this increment only reuses them in the viewer.
- O-02: Order with 1268. AC-13 needs the `thumb` variant; until it ships, image rows show a kind icon.

## Tasks

Test commands run from `apps/ios`.

### T-01 Model options button in the thread control group
- AC: AC-01, AC-02, AC-03, AC-05 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/ModelOptionsMenu.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/UITests/ModelOptionsUITests.swift, apps/ios/UITests/ComposerUITests.swift | Test: Tools/sim.sh test -only-testing:SpecWithCodeUITests/ModelOptionsUITests -only-testing:SpecWithCodeUITests/ComposerUITests

### T-02 Model name in the thread subtitle
- AC: AC-04 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatKind.swift, apps/ios/SWCKit/Tests/SWCFeaturesTests/ChatKindLineTests.swift | Test: make test-core

### T-03 Three mode chips that never truncate
- AC: AC-07 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Drawer/ColumnHeader.swift, apps/ios/UITests/AdaptiveLayoutUITests.swift | Test: Tools/sim.sh test -only-testing:SpecWithCodeUITests/AdaptiveLayoutUITests

### T-04 Library wire types, artifact model and shared deliverable vectors
- AC: AC-08, AC-11, AC-12 | Files: apps/ios/SWCKit/Sources/SWCWire/ProjectLibrary.swift, apps/ios/SWCKit/Sources/SWCSync/Artifacts.swift, apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Artifacts.swift, apps/ios/SWCKit/Sources/SWCSync/FixtureEngine.swift, apps/ios/SWCKit/Tests/SWCSyncTests/ArtifactsTests.swift, packages/shared/src/artifactDeliverable.vectors.json, apps/web/src/artifactShelf.test.ts | Test: make test-core && npx vitest run apps/web/src/artifactShelf.test.ts

### T-05 Artifacts list and viewer
- AC: AC-08, AC-09, AC-12, AC-13 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Artifacts/ArtifactsView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Artifacts/ArtifactRow.swift, apps/ios/SWCKit/Sources/SWCFeatures/Artifacts/ArtifactViewer.swift, apps/ios/SWCKit/Sources/Weave/Components/ProjectAvatar.swift, apps/ios/UITests/ArtifactsUITests.swift | Test: Tools/sim.sh test -only-testing:SpecWithCodeUITests/ArtifactsUITests

### T-06 Entry points and Duo master-detail
- AC: AC-06, AC-10, AC-11 | Files: apps/ios/SWCKit/Sources/SWCFeatures/Navigation/Router.swift, apps/ios/SWCKit/Sources/SWCFeatures/Drawer/DrawerView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Drawer/SidebarView.swift, apps/ios/SWCKit/Sources/SWCFeatures/RootView.swift, apps/ios/SWCKit/Sources/SWCFeatures/Chat/ChatView.swift, apps/ios/UITests/DrawerUITests.swift, apps/ios/UITests/DuoFoldUITests.swift, apps/ios/UITests/ThreadMenuUITests.swift | Test: Tools/sim.sh test -only-testing:SpecWithCodeUITests/DrawerUITests -only-testing:SpecWithCodeUITests/DuoFoldUITests -only-testing:SpecWithCodeUITests/ThreadMenuUITests

### T-07 Before and after evidence on the Duo and a folded phone
- AC: AC-14 | Files: apps/ios/Tools/shots.sh, apps/ios/UITests/HitTargetAuditUITests.swift | Test: Tools/sim.sh smoke
