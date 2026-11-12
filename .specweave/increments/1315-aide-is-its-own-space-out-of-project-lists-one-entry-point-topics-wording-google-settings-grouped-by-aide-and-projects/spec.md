# Aide is its own space: out of project lists, one entry point, topics wording, Google settings grouped by Aide and projects

## Problem

Aide, the personal assistant, is stored as a project of kind "personal", and while it is on it still shows as a regular project in several places: the Overview Projects panel and its "N projects" count, the Overview new-chat project picker, the command palette project lists, Move thread, the default new-chat target, the provider settings list and the Google account "Projects that may read it" list (as "Aide (personal)"). Inside Aide, threads are meant to be called topics, but many labels still say thread. The Google account page mixes Aide with projects and calls it a "Personal project", although the same Google sign-in is shared by Aide and any project the owner turns on.

## Scope

In: desktop and web app (apps/web), shared picker rule (packages/client-runtime), server wording (apps/server, packages/shared). Out: iPhone and Android apps (follow-up change), any change to stored data, routes or the per-project grant model.

## Acceptance Criteria

- [ ] AC-01: With Aide on, Aide is not a card in the Overview Projects panel and is not counted in "in N projects"; it has its own entry above Projects that opens it.
- [ ] AC-02: Ordinary project pickers (Overview new chat, command palette go-to and new-thread lists, Move thread, default new chat, provider settings, sidebar scope, Automated and Archived sidebar lists) do not offer Aide; Routines, Messaging and design pickers still do, named as Aide without a "(personal)" suffix.
- [ ] AC-03: Inside Aide every label in the list pane and the open-topic header says topic, never thread; a code project still says thread.
- [ ] AC-04: Settings > Google account shows Aide in its own group above "Projects that may read it"; project counts and "Enable for all" cover projects only; the copy says Aide, not "Personal project"; existing grants are unchanged.
- [ ] AC-05: Server text an agent or person reads names the page "Settings > Google account" consistently and Aide's prompt keeps saying topic.

## Approach

One rule in `projectPicker.ts`: purpose "work" no longer offers a personal assistant (reason "assistant"); a new purpose "any" keeps it for Routines, Messaging and settings scope; "design" keeps it. Overview filters personal groups out of its project cards and counts and renders an Aide entry of its own. `assistantTerms.paneWords` wraps the remaining thread labels. Google settings split the active list into Aide and projects. Routes and stored data stay as they are.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Google connections are shared: one sign-in, per-project switches. So the page stays "Google account", with Aide as its own group rather than a separate Aide-only page.
- D-02 Aide keeps its `/projects/<key>` address; only lists and labels change.
- D-03 Phone apps follow in a separate change, since they ship through the stores.
### Open
- none

## Tasks

### T-01 Lists, pickers and Overview entry
- AC: AC-01, AC-02 | Files: repositories/anton-abyzov/specwithcode/packages/client-runtime/src/state/projectPicker.ts, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/StudioOverview.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/StudioOverview.test.tsx apps/web/src/studio/projectListVisibility.test.ts

### T-02 Topics wording inside Aide
- AC: AC-03 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ThreadsPane.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/studio/shell/ProjectThreadHeader.tsx | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/web/src/studio/assistantTerms.test.ts apps/web/src/components/studio/shell

### T-03 Google account settings grouped by Aide and projects
- AC: AC-04 | Files: repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/GoogleAccountSettings.tsx, repositories/anton-abyzov/specwithcode/apps/web/src/components/settings/googleAccountSettings.logic.ts | Test: cd repositories/anton-abyzov/specwithcode && node scripts/studio-google/verify.mjs

### T-04 Server wording
- AC: AC-05 | Files: repositories/anton-abyzov/specwithcode/apps/server/src/project/ProjectWorkspaceService.ts, repositories/anton-abyzov/specwithcode/apps/server/src/integrations/google/GoogleAccountService.ts | Test: cd repositories/anton-abyzov/specwithcode && node node_modules/vite-plus/bin/vp test run apps/server/src/project/ProjectWorkspaceService.test.ts

### T-05 Verify and close 1315
- AC: AC-01 | Files: repositories/anton-abyzov/specwithcode/CHANGELOG.md | Test: cd repositories/anton-abyzov/specwithcode && bash scripts/release/request-release.sh --released HEAD
