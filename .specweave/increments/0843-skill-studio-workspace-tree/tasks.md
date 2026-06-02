---
increment: 0843-skill-studio-workspace-tree
title: "Skill Studio Workspace Tree — GitHub-mapped Sidebar with Login"
created: 2026-05-10
total_tasks: 15
completed_tasks: 0
---

# Tasks: Skill Studio Workspace Tree

All work lives in `repositories/anton-abyzov/vskill/`.

---

## Phase A — Mounts + Lucide + IPC Foundation

### T-001: RED — Test scaffolding for ConnectedRepoWidget mount in Sidebar
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05 | **Status**: [x]
**Test Plan**:
  Given a Sidebar rendered with `signedIn: true` fixture
  When the component mounts
  Then `ConnectedRepoWidget` is present in the DOM and `SidebarGitHubIndicator` is absent;
  and given `signedIn: false`, the inverse holds and existing snapshot tests still pass
**Files**:
  `src/eval-ui/src/__tests__/Sidebar.signed-in-mount.test.tsx`
**Effort**: ~2h

---

### T-002: GREEN — Surgical mount of ConnectedRepoWidget in Sidebar.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x]
**Test Plan**:
  Given the failing tests from T-001
  When `ConnectedRepoWidget` is imported and mounted at ~line 527, gated on `account_get_user_summary().signedIn`
  Then all Sidebar.signed-in-mount tests pass; net LOC delta in Sidebar.tsx is under 50; clicking the widget navigates to `/account/repos`
**Files**:
  `src/eval-ui/src/components/Sidebar.tsx`,
  `src/eval-ui/src/hooks/useAccountSummary.ts` (new thin wrapper)
**Effort**: ~3h

---

### T-003: RED — Test scaffolding for SkillCountBadge component (three tier fixtures)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05 | **Status**: [x]
**Test Plan**:
  Given `free` tier with counts 0, 25, 50; `pro` with any count; `enterprise` with any count
  When `SkillCountBadge` renders
  Then label reads `"N / 50"` for free, `"N skills"` for pro/enterprise; tooltip text is present per tier
**Files**:
  `src/eval-ui/src/__tests__/SkillCountBadge.test.tsx`
**Effort**: ~2h

---

### T-004: GREEN — Build SkillCountBadge.tsx and mount in StatusBar.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06 | **Status**: [ ]
**Test Plan**:
  Given the failing tests from T-003
  When `SkillCountBadge.tsx` (~80 LOC) is built using `useAccount` (tier + count, NOT missing useTier) and mounted in StatusBar.tsx right slot
  Then all SkillCountBadge tests pass; existing StatusBar.tsx tests still pass; badge renders when signed in
**Files**:
  `src/eval-ui/src/components/SkillCountBadge.tsx` (new),
  `src/eval-ui/src/components/StatusBar.tsx`
**Effort**: ~3h

---

### T-005: Add lucide-react dep and migrate 5+ inline SVG icons
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [ ]
**Test Plan**:
  Given `lucide-react@^0.460.0` added to package.json
  When production build runs before and after the migration
  Then at least 5 inline SVGs in Sidebar.tsx, SkillFileTree.tsx, StatusBar.tsx are replaced with Lucide equivalents using `currentColor`; bundle-size delta is under 50KB gzipped (both numbers recorded in `reports/bundle-size.md`); Playwright snapshot tests pass or are updated with one-line justification
**Files**:
  `package.json`,
  `src/eval-ui/src/components/workspace-tree/icons.ts` (new, re-exports 15 glyphs),
  `src/eval-ui/src/components/Sidebar.tsx`,
  `src/eval-ui/src/components/SkillFileTree.tsx`,
  `src/eval-ui/src/components/StatusBar.tsx`,
  `reports/bundle-size.md` (new)
**Effort**: ~4h

---

### T-006: RED + GREEN — Rust IPC `list_workspace_roots_with_repo_info` with unit tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-07 | **Status**: [ ]
**Test Plan**:
  Given a synthetic `workspace.json` with 5 fixture roots (connected, no-git, no-remote, non-github, error)
  When `list_workspace_roots_with_repo_info` runs via `tokio::task::spawn_blocking` + `buffer_unordered(8)` with 5s per-root timeout
  Then classification is correct for all 5 roots; a slow probe (injected sleep >5s) returns `probe_status: TimedOut` without blocking other roots; mtime cache hits avoid re-probe on unchanged workspace.json; `refresh_workspace_root` patches only the targeted cache entry
**Files**:
  `src-tauri/src/folders/workspace_tree.rs` (new ~250 LOC),
  `src-tauri/src/folders/mod.rs`,
  `src-tauri/src/lib.rs` (register 3 new IPCs: list_workspace_roots_with_repo_info, refresh_workspace_root, invalidate_workspace_cache)
**Effort**: ~8h

---

## Phase B — WorkspaceTree Component

### T-007: RED — Test scaffolding for deriveRowState pure function (11 branches)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ]
**Test Plan**:
  Given `WorkspaceRootInfo` fixtures for every RowState branch: connected_clean, connected_dirty, connected_ahead, connected_behind, disconnected, non_github, no_git, error, timed_out, plus edge cases (missing remote_url, null repo)
  When `deriveRowState(root)` is called
  Then the correct `RowState` string is returned for all 11 cases
**Files**:
  `src/eval-ui/src/components/workspace-tree/__tests__/deriveRowState.test.ts`
**Effort**: ~1h

---

### T-008: GREEN — Build WorkspaceTree core: deriveRowState, StatusDot, SyncStatePill, WorkspaceTreeRow
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-09, AC-US4-10 | **Status**: [ ]
**Test Plan**:
  Given the failing T-007 tests and WorkspaceTree row fixtures
  When the workspace-tree directory is scaffolded with WorkspaceTreeRow, StatusDot, SyncStatePill, WorkspaceTreeEmptyState, WorkspaceTreeLoading, deriveRowState
  Then deriveRowState tests pass; each row variant renders with correct `data-state` attribute, icon, and color token; keyboard nav (ArrowUp/Down/Right/Left/Enter) works per WAI-ARIA tree pattern; empty state and skeleton render at 28px row height, 14-16px icons
**Files**:
  `src/eval-ui/src/components/workspace-tree/deriveRowState.ts`,
  `src/eval-ui/src/components/workspace-tree/StatusDot.tsx`,
  `src/eval-ui/src/components/workspace-tree/SyncStatePill.tsx`,
  `src/eval-ui/src/components/workspace-tree/WorkspaceTreeRow.tsx`,
  `src/eval-ui/src/components/workspace-tree/WorkspaceTreeEmptyState.tsx`,
  `src/eval-ui/src/components/workspace-tree/WorkspaceTreeLoading.tsx`,
  `src/eval-ui/src/components/workspace-tree/__tests__/WorkspaceTreeRow.test.tsx`,
  `src/eval-ui/src/components/workspace-tree/__tests__/keyboard-nav.test.tsx`
**Effort**: ~8h

---

### T-009: GREEN — Build WorkspaceTree top-level with react-virtuoso, useWorkspaceTree hook, avatar cache
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-05, AC-US4-06, AC-US4-07 | **Status**: [ ]
**Test Plan**:
  Given a stubbed IPC returning 200 fixture `WorkspaceRootInfo` entries
  When `WorkspaceTree` mounts via `react-virtuoso`
  Then the rendered DOM contains fewer than 60 row nodes (virtualization assert); mount-to-stable is under 500ms (vitest timing assert against immediate IPC stub); avatar URLs are cached in `Map<owner, url>` and only fetched once per org per session; cache clears on sign-out
**Files**:
  `src/eval-ui/src/components/workspace-tree/WorkspaceTree.tsx`,
  `src/eval-ui/src/components/workspace-tree/index.ts`,
  `src/eval-ui/src/hooks/useWorkspaceTree.ts`,
  `src/eval-ui/src/components/workspace-tree/__tests__/WorkspaceTree.test.tsx`
**Effort**: ~6h

---

### T-010: GREEN — ConnectToGitHubButton, WorkspaceTreeContextMenu, right-click menu
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04, AC-US4-08 | **Status**: [ ]
**Test Plan**:
  Given a disconnected row and a connected row in the WorkspaceTree
  When the "Connect to GitHub" CTA is clicked on a disconnected row
  Then `studio:open-account-tab` CustomEvent fires with `{ tab: 'repos', initialPath: <path> }`; right-click menu shows View on GitHub (connected only), Refresh, and Disconnect; View on GitHub invokes `open_external_url` IPC with the correct URL; Refresh calls `refreshOne(rootId)`
**Files**:
  `src/eval-ui/src/components/workspace-tree/ConnectToGitHubButton.tsx`,
  `src/eval-ui/src/components/workspace-tree/WorkspaceTreeContextMenu.tsx`,
  `src/eval-ui/src/components/workspace-tree/__tests__/ConnectToGitHubButton.test.tsx`,
  `src/eval-ui/src/components/workspace-tree/__tests__/WorkspaceTreeContextMenu.test.tsx`
**Effort**: ~4h

---

### T-011: GREEN — Mount WorkspaceTree in App.tsx behind features.workspaceTree flag
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ]
**Test Plan**:
  Given `features.workspaceTree: true` and `features.workspaceTree: false` fixture states
  When App.tsx is rendered
  Then WorkspaceTree mounts above Sidebar when flag is true, is absent when false; `studio:open-account-tab` event listener is registered; existing App.tsx tests pass
**Files**:
  `src/eval-ui/src/App.tsx`,
  `src/eval-ui/src/__tests__/App.workspace-tree-mount.test.tsx`
**Effort**: ~2h

---

## Phase C — Sandbox-PAT E2E Rig

### T-012: RED + GREEN — cfg(feature = "test-fixture") IPC dev_inject_test_token
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [ ]
**Test Plan**:
  Given `cargo build --features test-fixture`
  When `dev_inject_test_token(token)` IPC is called
  Then token is written to the same `auth::token_store` path used by production OAuth; a grep of the release binary (no feature flag) returns 0 matches for `dev_inject_test_token`; the `auth::test_fixture::dev_inject_writes_token_store` cargo test passes
**Files**:
  `src-tauri/Cargo.toml` (add `[features] test-fixture = []`),
  `src-tauri/src/auth/test_fixture.rs` (new, gated `#[cfg(feature = "test-fixture")]`),
  `src-tauri/src/lib.rs` (conditional registration)
**Effort**: ~3h

---

### T-013: GREEN — Playwright sandbox-pat-preflight spec and workspace-tree E2E spec
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05 | **Status**: [ ]
**Test Plan**:
  Given `VSKILL_TEST_GITHUB_PAT` set to the fine-grained PAT scoped to `anton-abyzov/vskill-test-sandbox`
  When the E2E suite runs
  Then: (a) pre-flight probe write to `octocat/Hello-World` returns 403/404 — suite aborts with "PAT is over-scoped" if not; (b) avatar and login visible in Sidebar; (c) sandbox folder row is `connected` with branch `main`, visibility `public`, sync `clean`; (d) non-git folder shows `disconnected` with Connect CTA; (e) right-click View on GitHub invokes stubbed `open_external_url` with `https://github.com/anton-abyzov/vskill-test-sandbox`; (f) teardown deletes any `test-*` branches/PRs; (g) suite skips cleanly when PAT env var is absent
**Files**:
  `e2e/desktop/sandbox-pat-preflight.spec.ts` (new),
  `e2e/desktop/workspace-tree-sandbox.spec.ts` (new)
**Effort**: ~6h

---

### T-014: Docs — e2e/desktop/README.md with PAT obtain steps and rotation reminder
**User Story**: US-005 | **Satisfies ACs**: AC-US5-06 | **Status**: [ ]
**Test Plan**:
  Given a contributor who needs to run the E2E suite locally
  When they read `e2e/desktop/README.md`
  Then they find: how to obtain the fine-grained PAT, the required scopes (`contents:read`, `metadata:read`, `pull-requests:read`), how to set `VSKILL_TEST_GITHUB_PAT`, and the 30-day rotation reminder referencing ADR-0843-04
**Files**:
  `e2e/desktop/README.md` (new)
**Effort**: ~1h

---

## Phase D — Final Gate

### T-015: Full test suite green + bundle-size delta recorded + CHANGELOG updated
**User Story**: US-001..US-005 | **Satisfies ACs**: AC-US1-01..AC-US5-06 (closure gate) | **Status**: [ ]
**Test Plan**:
  Given all previous tasks complete
  When the full pipeline runs
  Then: `cargo test` passes (all workspace_tree + test_fixture units green); `npx vitest run` passes (all component + hook tests green, 100-root timing assert under 500ms, 200-row DOM assert under 60 nodes); `npx tsc --noEmit` passes; `npx playwright test e2e/desktop/workspace-tree-sandbox.spec.ts` passes when `VSKILL_TEST_GITHUB_PAT` is set and skips cleanly when absent; `reports/bundle-size.md` contains both before/after gzipped sizes (delta under 50KB); 0836 hardening test suite still green; `CHANGELOG.md` vskill entry for 1.0.19 documents US-001..US-005 summary
**Files**:
  `CHANGELOG.md`,
  `reports/bundle-size.md`
**Effort**: ~3h
