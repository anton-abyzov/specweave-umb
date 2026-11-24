# 0912 Keep saved project names and show update results

## Problem

The installed 1.0.10 candidate contains the 0908 fix, but the sidebar still shows repository names when canonical projects coexist with differently named handoff-proof checkouts. The header uses the selected checkout's saved title. A native sidebar update check succeeds in 432ms and finds no newer release, but displays no result. Publishing the same 1.0.10 version cannot update an already installed 1.0.10 candidate.

## Scope

In: sidebar/header name consistency, visible manual update results including handled errors, focused tests/build/review, and coordinated normal-updater acceptance. Out: modifying project records, changing repository grouping identity, taking over 0907 handoff gates or competing release publication.

## Acceptance Criteria

- [ ] AC-01: The sidebar uses the same resolved checkout's saved project title as the header, including conflicting custom proof titles, exact remote selections and saved machine selection; grouping identity remains unchanged.
- [ ] AC-02: Manual sidebar update checks visibly report no newer update with the installed version, and expose handled check errors; offered/downloaded update actions continue to work.
- [ ] AC-03: Focused regressions, production build, independent review and rendered browser checks pass, and all scoped changes are pushed.
- [ ] AC-04: A coordinated release higher than the installed candidate is detected through the normal updater, with install/relaunch and actual names/update feedback verified when the release owner yields the live app.

## Approach

Reuse StudioSidebar's displayedCheckouts resolution, which mirrors the project workspace's URL/saved-machine selection, instead of inventing a canonical title from group member ordering. Preserve keys, navigation destinations and stored titles. Inspect update result state rather than the attempted-check boolean; emit concise manual-only feedback. Use isolated branches based on frozen 0907 source 133ebdec; never mutate the running candidate. Release chat Improve SpecWithCode release output coordinates publication with the next release owner. 0907/1.0.10 remains frozen; the successor version is the normal-updater acceptance target. No global Node/toolchain changes.

## Open questions

- Native update acceptance waits for the release owner's explicit handover of the live app; no additional user authorization is needed for the requested update.

## Tasks

### T-01 Use the resolved checkout name in the sidebar
- AC: AC-01 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/StudioSidebar.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/studio/shell/StudioSidebar.test.tsx | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/web/src/components/studio/shell/StudioSidebar.test.tsx

### T-02 Show manual update results
- AC: AC-02 | Files: repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarUpdatePill.tsx, repositories/anton-abyzov/specweave-studio/apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx | Test: cd repositories/anton-abyzov/specweave-studio && node node_modules/vite-plus/bin/vp test run apps/web/src/components/sidebar/SidebarUpdatePill.test.tsx

### T-03 Review, build, render and push the fixes
- AC: AC-03 | Files: .specweave/increments/0912-project-names-update-feedback/reports | Test: git diff --check

### T-04 Verify the normal installed update path
- AC: AC-04 | Files: .specweave/increments/0912-project-names-update-feedback/reports/native-acceptance.md | Test: git diff --check
