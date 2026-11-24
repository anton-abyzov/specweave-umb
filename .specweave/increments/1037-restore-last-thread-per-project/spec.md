# 1037 Restore last thread per project

## Problem
Returning through the project sidebar drops the selected worker and shows the Threads overview. The existing conversation scroll retention does not retain the navigation destination.

## Scope
In: per-project sidebar return destination, browser-local reload persistence, environment identity, stale selection fallback, regression coverage. Out: notifications, report viewer, thread migration, release or service restart.

## Acceptance Criteria
- [ ] AC-01: Sidebar A → B → A restores A's last viewed worker, including rapid switches, without background activity changing the destination.
- [ ] AC-02: Explicit overview navigation and direct thread links win; first visit opens the overview and browser history remains usable.
- [ ] AC-03: Saved destinations survive reload, distinguish projects and machine checkouts, and preserve explicit thread environment identity.
- [ ] AC-04: Delayed loading does not erase the destination; removed, archived or inaccessible saved workers fall back safely without navigating to another project.
- [ ] AC-05: Existing reader scroll intent is preserved; headless before/after evidence, focused tests, production build and exact-head CI substantiate the reviewed PR.

## Approach
Store the last routed project pane destination in a bounded browser-local store keyed by the sidebar project identity, carrying the exact checkout and thread environment. Sidebar links alone use this store and mark restored selections. The active outer project workspace records navigation, not live thread activity. Restored selections wait for inventory and use safe overview fallback; ordinary explicit links retain existing routing. Reuse kept project pages and conversation follow state, with no scroll commands. Verify with focused tests and real project workspace headless fixture.

## Decisions
### Defaulted
- Browser-local persistence follows existing UI preferences; no server writes or fleet replication.
- An explicit overview is itself a remembered destination.
- Archived saved workers return to overview; explicit links to archived threads keep their existing behavior.
### Open
- none

## Tasks
### T-01 Restore sidebar destinations and validate saved selections
- AC: AC-01, AC-02, AC-03, AC-04 | Files: apps/web/src/studio/projectReturnNavigation.ts, apps/web/src/studio/projectReturnNavigation.test.ts, apps/web/src/routes/projects.$projectKey.tsx, apps/web/src/components/studio/shell/SidebarProjectList.tsx, apps/web/src/studio/projectPaneThreads.ts, apps/web/src/studio/useProjectPaneSelection.ts, apps/web/src/components/studio/ProjectWorkspace.tsx, apps/web/src/components/studio/ProjectWorkspaceSurface.tsx, apps/web/src/components/studio/KeptProjectPages.tsx | Test: focused project navigation tests

### T-02 Verify user navigation and reader retention with screenshots
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: apps/web/tests/project-workspace/, apps/web/src/studio/useProjectPaneSelection.test.tsx, apps/web/src/components/studio/shell/SidebarProjectList.layout.test.tsx | Test: headless project workspace navigation fixture and production web build

### T-03 Verify and close 1037
- AC: AC-05 | Files: apps/web/src/routes/projects.$projectKey.tsx, apps/web/src/routes/projectReturnRoute.test.tsx, review evidence | Test: specweave verify 1037; independent review; exact-head PR CI
