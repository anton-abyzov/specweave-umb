# 1487 Guided onboarding tour: skills, other machines, model tracks and where settings live

## Problem

On November 25, 2026 Anton asked for a guided tour of at least 10 steps covering four things: how to manage skills, how to use other machines, how to change the model by track, and where project settings and global settings live. New users have three ways to learn the app today. The "What you can do" checklist (1179) lists five setup items. Quick guides (1459) has three illustrated cards. The first feature guide (1398) walks through one sample feature. None of them points at the real controls. Skills, the Daily, Complex and Review tracks, Machines and the Project and App settings groups are in different places, and nothing shows where they are.

This increment was planned as 1486. Main took 1486 first (`1486-skill-deprecation-pointer`), so on November 25, 2026 it moved to 1487. App commits, PR #935 and code comments still say 1486.

## Scope

In: a 14-step coachmark tour that runs on the real app. Each step spotlights a real element, says one short sentence, and has Next, Back and Skip. You start it from Quick guides on Overview, or from Settings > General > Guided tour, where settings search finds it. It never starts on its own. It works on a single-machine install. It comes with translations in all eight catalogs, unit and component tests, and a headless verifier that runs a real built server on a scratch home and screenshots every step.

Out: a tour on the phone, saved tour progress, a forced first-run stage, changes to the 1387 first-run walker, and a command palette entry (D-04).

## Acceptance Criteria

- [x] AC-01: The tour has 14 steps, in this order:
  1. Welcome: what the tour covers, on Overview.
  2. Projects: the sidebar Projects heading.
  3. Project settings: the settings sidebar's Project group.
  4. App settings: the settings sidebar's App group, and the scope line on each section (This project, This machine, This device).
  5. Skills: the Skills section header.
  6. Find and install: the skill search.
  7. Per-agent switches and "Also add on": the skills table, or the empty skills message.
  With no project, steps 5 and 6 point at the Skills entry in the settings sidebar, because the Skills page only asks for a project.
  8. Daily: the Daily track header.
  9. Complex: the Complex track header.
  10. Review: the Review track header.
  11. One chat's model: the Overview New chat button, explaining the model chip and "Switch model and continue…".
  12. Machines: the Machines section header.
  13. Moving work: the "Moving work between machines" section header, naming "Move thread…" and "Move running threads…".
  14. Take it again: the Settings > General Guided tour row.
- [x] AC-02: Each step dims the page and spotlights its target with a ring. A card beside the target shows "Step N of 14", a title, one sentence, and Back, Next (Done on the last step) and Skip tour. Back is disabled on step 1. Esc skips, Left and Right arrows move between steps, and focus lands on Next at every step. The card is a labelled dialog, and with reduced motion nothing animates.
- [x] AC-03: A step opens its own page first (Overview, Settings > General, Skills, Models or Machines) and waits up to 3 seconds for its target. Step 1 is a centred card with no target. Steps 2 to 14 mark each target as required or optional, and a step keeps looking for its first target after a stand-in draws. A missing optional target, such as the sidebar on a 390 px phone layout, shows the card centred. A missing required target also shows it centred, but marks the card `data-tour-target="missing"`, so the verifier fails at 1440 px.
- [x] AC-04: The tour changes nothing. The dim layer blocks clicks, no key reaches the app under it, and the tour writes no setting and creates no chat, draft or project. Skip and Done return to the page the tour started on, its pages replace history entries instead of adding them, and closing Settings afterwards goes where it would have gone before the tour.
- [x] AC-05: There are two entry points, and neither starts the tour on its own. The Quick guides dialog has "Take the tour", which closes the dialog first. Settings > General has a "Guided tour" row with a "Take the tour" button, and settings search finds that row for "tour", "onboarding" and "guide".
- [x] AC-06: The tour works with one machine and no project. The Machines and Moving work steps say the second machine is optional ("With one machine, nothing here needs setting until you join another."). The flow never needs another machine, a project or an agent.
- [x] AC-07: The copy uses the app's real labels. Section names, group names and track names come from `SETTINGS_SECTION_LABELS`, `SETTINGS_NAV_GROUPS` and `MODEL_TRACK_LABELS`, and a test checks they match. Every phrase the tour shows is in all eight phrase catalogs (de, es, fr, ja, ko, pt, ru, zh), and a test checks that too. The copy says "machine", never "environment", uses no em dashes, and has one sentence per step.
- [x] AC-08: `scripts/studio-verify/guided-tour.mjs` runs headless against a real built server on a scratch home. It starts the tour from Quick guides and walks every step at 1440×900 dark and at 390×844 light. It saves one screenshot per step and viewport to the increment's `reports/guided-tour/`. It fails on a missing required target at 1440, on horizontal overflow, on a page error, or when Skip does not return to Overview. It also checks Back, and that Esc ends the tour.
- [x] AC-09: A reviewer from a different model family, Gemini 4 Neon (GPT-6.2 Sol if Neon has no quota, never Grok), reviews the app PR. Its findings are fixed or answered, the PR is merged when green, and the app release is requested with `bash scripts/release/request-release.sh --by "<thread>"`.

## Approach

New folder `apps/web/src/components/studio/guidedTour/`:
- `guidedTour.logic.ts`: the step list (id, route, target selectors, whether the target is required, and title and body phrases with `{label}` values), pure next and back helpers, and card placement (below the target, else above, else centred, kept inside the viewport).
- `guidedTourStore.ts`: a tiny external store (`startGuidedTour`, `endGuidedTour`, `useGuidedTour`) that records the page the tour started on.
- `GuidedTour.tsx`: the host, mounted once in `__root.tsx` inside the app shell. It navigates to the step's route, polls for the target, scrolls it into view, and redraws the spotlight with a fixed box-shadow cutout on resize and scroll. It renders the card and handles keys with a capture listener, so Settings' own Esc handling never runs.
- `GuidedTourSetting.tsx`: the Settings > General row button.

Existing files change only for small hooks:
- `QuickGuides.tsx`: a controlled dialog with a "Take the tour" button.
- `SettingsPanels.tsx`: one row.
- `settingsSearch.ts`: one search item.
- `SettingsSidebarNav.tsx`: a `data-settings-nav-group` attribute.
- The phrase catalogs: one import and one spread each.

`StudioSidebar.tsx` (1,490 lines) is not touched; the tour targets the existing `#sws-side-projects`. Settings sections are targeted by their existing anchor ids (`#project-skills`, `#model-track-daily`, `#machines`, `#handoff-mode`) and their header `[data-settings-scroll-target]`.

Rejected alternatives:
- A third-party tour library: a new dependency, and the spotlight here is about 40 lines.
- Putting the tour inside the Quick guides cards: it would not point at real UI.
- Starting it on its own after setup: no forced flow, per the brief.

Risks:
- Settings pages render late on a cold server. The 3 s wait and the verifier's required-target check catch it.
- Labels can drift. The tour reads them from the constants.
- `SettingsPanels.tsx` (4,031 lines), `settingsSearch.ts` and the phrase catalogs are already over the 1,500-line rule. This increment adds at most 8 lines to each and puts all new code in new files under 400 lines.

File overlap: active 1459 also edits `QuickGuides.tsx` and the phrase catalogs. 1459's change is merged on app main, and this increment builds on it.

## Decisions

### Asked
- D-01 Checklist or tour → a guided tour (Anton, November 25, 2026). This reverses 1179's choice of a checklist over a tour. The checklist stays.

### Defaulted (change any before sw-do)
- D-02 Where it starts → from Quick guides on Overview and from Settings > General, never on its own (reversible).
- D-03 Length → 14 steps, so each of the four topics gets two or more stops (reversible).
- D-04 No command palette entry → `CommandPalette.tsx` is 4,542 lines; Settings search finds the row instead (reversible).
- D-05 The per-thread model step points at New chat on Overview, because the model chip exists only inside a chat. It names the chip and "Switch model and continue…" in words (reversible).
- D-06 Tracks are explained where they are set (Settings > Models). The app has no per-launch track picker to point at (reversible).
- D-07 Nothing is saved about the tour: no "seen" flag, because it never starts on its own (reversible).

### Open
- none

## Tasks

### T-01 Tour steps, store and phrases
- AC: AC-01, AC-03, AC-06, AC-07 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/guidedTour/guidedTour.logic.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/guidedTour/guidedTour.logic.test.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/guidedTour/guidedTourStore.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/guidedTour, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/de.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/es.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/fr.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ja.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ko.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/pt.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/ru.ts, repositories/anton-abyzov/specwithcode/apps/web/src/i18n/phrases/zh.ts | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/guidedTour/guidedTour.logic.test.ts

### T-02 Tour overlay, mount and entry points
- AC: AC-02, AC-03, AC-04, AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/guidedTour/GuidedTour.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/guidedTour/GuidedTour.test.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/guidedTour/GuidedTourSetting.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/QuickGuides.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/routes/__root.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsPanels.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/settingsSearch.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/SettingsSidebarNav.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/ProjectSkillsSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/sidebar/mainAppLocation.ts, repositories/anton-abyzov/specwithcode/CHANGELOG.md, repositories/anton-abyzov/specwithcode/docs/user/welcome-wizard.md | Test: cd repositories/anton-abyzov/specwithcode/apps/web && node ../../node_modules/vite-plus/bin/vp test run src/components/studio/guidedTour src/components/studio/StudioOverview.test.tsx

### T-03 Headless walk of every step
- AC: AC-08, AC-06 | Files: repositories/anton-abyzov/specwithcode/scripts/studio-verify/guided-tour.mjs, repositories/anton-abyzov/specwithcode/docs/operations/checks.md, .specweave/increments/1487-guided-onboarding-tour-skills-other-machines-model-tracks-and-where-settings-live/reports | Test: test -s .specweave/increments/1487-guided-onboarding-tour-skills-other-machines-model-tracks-and-where-settings-live/reports/guided-tour/receipt.json

### T-04 Review, merge and release request
- AC: AC-09 | Files: .specweave/increments/1487-guided-onboarding-tour-skills-other-machines-model-tracks-and-where-settings-live/reports/review.md | Test: test -s .specweave/increments/1487-guided-onboarding-tour-skills-other-machines-model-tracks-and-where-settings-live/reports/review.md

### T-05 Verify and close 1487
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09 | Files: none | Test: specweave verify 1487-guided-onboarding-tour-skills-other-machines-model-tracks-and-where-settings-live
