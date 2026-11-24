# 1073 picker audit

October 25, 2026. Sole implementation writer, branch `feat/active-only-project-pickers`, base `b323adb74913af51a4ce710f6e4e558b335ebf1b`.

## Ownership

Read `gh pr diff 703 --name-only`, `gh pr diff 665 --name-only`, `gh pr diff 708 --name-only` before implementation. No implementation file overlaps those PRs. Counts writer `mcp:c3913578-5bdd-4b1f-9b42-45f5c93e09e5` explicitly confirmed no holds on the proposed shared/mobile files and retains counts/lifecycle only. PR #703 owner shorthand `mcp:14680490` did not resolve, but no #703 file is edited so no merge sequencing dependency was created. Planning thread remains read-only. No worktree takeover, stash, shared install or database-file access.

## Source, tags, installed bytes and metadata

- `origin/main` at the base already calls `pullRequestScopeFilterProjects`, which calls `projectPickerMembers`. This is not a missing Code Review consumer.
- `v1.0.76` route already calls `projectPickerMembers`, but that tag's helper returns user projects followed by automated projects. An excluded selected project remains selectable there. Earlier inference from the filter module alone that the helper call was absent was corrected after tracing the route.
- `v1.0.77` helper excludes automated/archive/scratch choices and retains excluded selected context as unavailable.
- `/Applications/SpecWithCode.app` Info.plist and `specweave-studio --version` both report `1.0.76`. This explains the automated rows in the older screenshot. It does not prove running-service/browser assets or postrelease acceptance.
- Supported project API readback, local machine only: Moonbeam Coffee and routing acceptance have `origin: automated`. Run shell acceptance is inferred automated from its app scratch path. Aide and Example Household are active `kind: personal` user contexts, not archived and without an automated flag. Code Review now asks for code purpose; they are excluded there without reclassification. Work/design pickers supporting personal projects retain them. Other machines' metadata remains unverified, and same-name or same-remote registrations are never evidence of automation.
- Independent defect: Code Review deduplicated by environment plus canonical repository. It now deduplicates only repeated environment/project identities and labels distinct checkouts by machine, path and identity as needed.
- Independent grouped-helper defect: separate every-archived/every-automated tests admitted groups whose members were all ineligible for different reasons. Eligibility now requires one member to satisfy the complete predicate.

## Consumer inventory

Management lists (Archived, Automated, project lifecycle/settings management and historical thread lists) retain their separate semantics. Explicit standalone start-without-project actions remain available; ordinary project dropdown rows exclude scratch.

| Surface | Source | Before / disposition |
| --- | --- | --- |
| Code Review wide/narrow project filters | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/pullRequest/pullRequestProjectFilter.logic.ts` | Direct member helper; fixed repository dedup; code purpose; excluded current row disabled |
| Chat project scope | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/Sidebar.logic.ts` | Direct group helper; already active-only |
| Thread move destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/threadMove.logic.ts` | Direct member helper; already active-only |
| Command palette projects | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/CommandPalette.tsx` | Direct member helper; already active-only |
| Overview draft destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/studio/StudioOverview.tsx` | Direct member helper; already active-only |
| Telegram channel project | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/MessagingSettings.tsx` | Direct member helper; already active-only |
| Routine project | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/ScheduledTasksSettings.tsx` | Direct member helper; already active-only |
| ACP sessions/provider project | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/ProviderSettingsPanel.tsx` | Direct member helper; already active-only |
| Settings scope sentence | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/settingsScopeAxis.ts` | Direct group helper; already active-only |
| New chat hero project dropdown | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/chat/DraftHeroHeadline.tsx` | Equivalent member predicate; removed selectable No project row; explicit standalone scratch action retained; selected scratch now unavailable |
| Draft machine project destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/chat/DraftMachinePicker.tsx` | Indirect eligibility through draft destination logic; already excludes ordinary ineligible choices |
| Design connect destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/design/gallery/useConnectDesign.tsx` | Direct member helper with code purpose; already active-only |
| Design/slides Save in; gallery project scope; design from code | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/design/gallery/DesignGalleryPage.tsx` | Equivalent shared projectChoiceIneligibleReason; marks unavailable before offeredProjects |
| Design system owner Save in / Copy into | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/design/systems/OwnerSelect.tsx` | Indirect offeredProjects using classified unavailable metadata |
| Design system Scan from code | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/design/systems/ScanFromCode.tsx` | Indirect offeredProjects with code purpose |
| Chosen work-grant projects | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/MachineWorkGrants.tsx` | Missing direct helper on base; #703 owns repair; untouched |
| Design Copy to project | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/design/gallery/DesignActions.tsx` | Missing direct helper on base; #703 owns repair; untouched |
| Project link dialog | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/studio/ProjectLinkDialog.tsx` | Missing direct helper on base; #703 owns repair; untouched |
| Settings Choose a project notice | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/settings/SettingsScopeNotice.tsx` | Missing direct helper on base; #703 owns repair; untouched |
| Legacy sidebar project scope | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/web/src/components/LegacySidebar.tsx` | Missing direct helper on base; #703 owns repair; untouched |
| React Native home header filter | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/home/HomeRouteScreen.tsx` | Missing on base; now homeProjectPickerScopes shared classification; current excluded context retained |
| React Native thread sidebar filter | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/threads/ThreadNavigationSidebar.tsx` | Missing on base; now homeProjectPickerScopes; historical thread list unaffected |
| React Native new task / shared-content destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/threads/new-task-flow-provider.tsx` | Missing on base; now shared member filter before grouping; excluded persisted target retained; new enqueue refused |
| React Native command palette destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/keyboard/CommandPalette.tsx` | Missing on base; now shared member helper; new-thread action also filtered |
| React Native Settings scope filter | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/settings/settings-environment-filter.tsx` | Missing on base; now settingsProjectChoices uses shared classifier; excluded current selection disabled |
| React Native routine project/default destination | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/settings/SettingsScheduledTasksRouteScreen.tsx` | Missing on base; now shared member helper; current excluded row disabled and save refused |
| React Native routine default project | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/mobile/src/features/settings/scheduled-task-editor.tsx` | Missing on base; now shared member helper before choosing default |
| Swift project search | `/Users/antonabyzov/.specwithcode/m4/worktrees/specweave-studio/feat-active-only-project-pickers/apps/ios/SWCKit/Sources/SWCFeatures/Support/Logic.swift` | Existing active non-automated navigation search; no ordinary project dropdown; no edits |

## Verification boundary

The focused shared tests cover explicit/inferred automation, archived, scratch, missing metadata, active personal/code kinds, classifications changing, mixed groups and excluded selections. Existing consumer tests are run only for the audited picker surfaces. The responsive fixture renders the actual extracted Code Review compact control and the actual narrow filter menu against synthetic data. Its result is source verification, not installed acceptance. Full builds are excluded by Anton's explicit disk instruction. After coordinated merge and sole release, actual installed Code Review behavior and byte/version readback must still pass before increment closure.
