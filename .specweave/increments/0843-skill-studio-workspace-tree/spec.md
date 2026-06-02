---
increment: 0843-skill-studio-workspace-tree
title: Skill Studio Workspace Tree — GitHub-mapped Sidebar with Login
type: feature
priority: P1
status: paused
created: 2026-05-10T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Studio Workspace Tree — GitHub-mapped Sidebar with Login

## Overview

Deliver the user's actual ask: **"GitHub login from inside the macOS app, with folders mapped to GitHub repos in a tree-view sidebar with proper icons and professional design."**

70-80% of the surface already ships in code:

- **0831 (Enterprise Tier)** built `ConnectedRepoWidget` (580 LOC, tested) but never mounted it (deferred to a follow-up). The component-state notes from 0831's DoD also referenced a `SkillCountBadge`, but the Architect's 2026-05-10 codebase exploration confirmed only the planned-build was deferred — no badge component file exists yet, so US-002 covers both building and mounting it. 0831 also shipped the folder classifier (`folders/classifier.rs`) and git-remote parser (`folders/git_remote.rs`) that this increment leans on.
- **0834 (Account Cabinet)** shipped `AccountShell.tsx` (650 LOC) with the `/account/repos` and `/account/repos/connect` deep-link routes, plus `useConnectedRepos` hook and `ConnectedReposTable`.
- **0836 (Security Hardening)** locked the eval-server to loopback, gated all API calls with `X-Studio-Token`, removed `account_get_token` from the WebView surface, and consolidated keychain storage. Anything new in 0843 inherits — and must not regress — that posture.

This increment finishes the deferred mounts (US-001, US-002), introduces a single icon library (US-003), adds the new aggregating tree view that the user actually wants (US-004), and stands up an automated end-to-end test rig against a real sandbox repo (US-005).

**Brainstorm trio (2026-05-09)**: the *Pragmatist* lens won — reuse `react-virtuoso` (already in deps), add only `lucide-react`, mount-don't-rebuild Sidebar.tsx, and keep platform unchanged. The Advocate's bigger ambitions (`@primer/octicons-react`, `react-arborist`, multi-org switcher, Cmd+K) are deferred. The Critic's concerns (no notarization regression, no new attack surface, sandbox-PAT pre-flight) are encoded as constraints and as AC-US5-02.

## Personas

### P-001: GitHub-Connected Skill Author (primary)
A vskill user who has already signed in to GitHub via the OAuth Device Flow shipped in 0831. They are working across 3-15 local folders — most are GitHub clones, a few are scratch notes or skill drafts not yet pushed. They want a glance-level answer to "which folder is which repo, and which one am I editing right now?" without opening a separate panel.

### P-002: Multi-Project Pragmatist
A consultant juggling 30-100 workspace roots across 3-5 GitHub orgs. Performance and clarity matter more than animation. Needs virtualized rendering, distinct icons per state, and avatar caching so the tree does not thrash on every workspace switch.

### P-003: Privacy-Conscious Disconnect-First User
A user who does not want to sign in to GitHub at all (or has signed out). The sidebar must remain useful: every existing 0831 "signed-out" affordance keeps working, the WorkspaceTree degrades gracefully (folder names, no remote info), and no token is ever exposed to the WebView (0836 invariant).

### P-004: Future-Self Maintainer
The team-of-agents that will ship US-006+ in the next phase (Cmd+K, drag-drop, multi-org). They need the new code to be sibling-only (no Sidebar.tsx refactor), single icon library, and an E2E rig that survives PAT rotations and CI environments without the secret.

## Scope

**In scope (this increment):**

1. Mount `ConnectedRepoWidget` into `Sidebar.tsx` (signed-in only, gated on `account_get_user_summary().signedIn`).
2. Mount `SkillCountBadge` into `StatusBar.tsx` with tier-conditioned label.
3. Add `lucide-react` (single new dep) and migrate at least 5 inline SVG icons to it.
4. Build new sibling `WorkspaceTree.tsx` component aggregating workspace roots into a connected/disconnected tree with right-click menu, keyboard nav, virtualization, avatar caching, and per-row state machine.
5. Add new Tauri IPC `list_workspace_roots_with_repo_info()` aggregating existing 0831 classifier + git-remote logic in one parallel call.
6. Sandbox-PAT E2E rig (`e2e/desktop/workspace-tree-sandbox.spec.ts`) using `anton-abyzov/vskill-test-sandbox` and a fine-grained read-only PAT.

**Out of scope (deferred):**

- Cmd+K command palette (Phase 2)
- Drag-drop reordering of workspace roots (Phase 2)
- Multi-org switcher in sidebar header (Phase 4)
- GitHub webhooks for real-time sync state (Phase 4 — on-demand polling is acceptable for v1)
- GHES support beyond a tooltip mention (Phase 3)
- SSO / SAML (Phase 3)
- MDM-managed config (Phase 3)
- Stripe + Team tier (Phase 2)
- `@primer/octicons-react` / `react-arborist` (Pragmatist's reuse argument wins; `lucide-react` + `react-virtuoso` suffice)
- Refactoring `Sidebar.tsx` (1502 LOC — sibling mounts only)

## User Stories

### US-001: Mount ConnectedRepoWidget in the sidebar (P1)
**Project**: vskill

**As a** vskill user signed in to GitHub
**I want** the active project's connected-repo state visible in the sidebar
**So that** I can see at a glance which repo the active workspace maps to and click through to my account.

**Context**: `src/eval-ui/src/components/ConnectedRepoWidget.tsx` (580 LOC) was built and unit-tested in 0831 but never mounted. `Sidebar.tsx` (1502 LOC) renders the existing `SidebarGitHubIndicator` at approximately line 527; this is where the widget belongs as a sibling, not a refactor.

**Acceptance Criteria**:
- [x] **AC-US1-01**: `Sidebar.tsx` imports `ConnectedRepoWidget` and renders it in the project section, gated so it only mounts when `account_get_user_summary().signedIn === true`.
- [x] **AC-US1-02**: When signed out, the existing `SidebarGitHubIndicator` "Sign in" CTA continues to render with no visual or behavioral regression.
- [x] **AC-US1-03**: Clicking the widget navigates to the existing 0834 `/account/repos` deep-link route in `AccountShell.tsx`.
- [x] **AC-US1-04**: The mount adds **fewer than 50 net LOC** to `Sidebar.tsx` (surgical, no refactor).
- [x] **AC-US1-05**: All existing `Sidebar.tsx` tests continue to pass; one new test asserts the widget renders for a signed-in user fixture and does not render for a signed-out fixture.

---

### US-002: Build and mount SkillCountBadge in the status bar (P1)
**Project**: vskill

**As a** vskill user
**I want** my skill-count quota visible in the status bar
**So that** I know when I am approaching the free-tier 50-skill cap.

**Context**: The brainstorm trio's Pragmatist lens stated `SkillCountBadge` was built/tested in 0831 but unmounted; the Architect's codebase exploration on 2026-05-10 confirmed the component does NOT exist on disk (only its test scaffolding does). This US therefore covers BOTH building the component and mounting it. The `useTier` hook from 0833 plus the existing quota-cache (`useAccount.ts`) remain the data source. `StatusBar.tsx` already exists with a right-slot suitable for the badge. Component scope is intentionally narrow — a tier-conditioned label + tooltip; no popover, no upgrade-CTA in v1 (the AccountShell `/account/plan` tab is one click away).

**Acceptance Criteria**:
- [ ] **AC-US2-01**: New file `src/eval-ui/src/components/SkillCountBadge.tsx` is added; it reads tier + count from `useAccount` (existing 0834 hook) and renders a tier-conditioned label.
- [ ] **AC-US2-02**: For tier `free`, the badge label reads `"N / 50"` with N from the quota-cache count; for `pro` and `enterprise`, the label reads `"N skills"` (no cap).
- [ ] **AC-US2-03**: Hovering the badge shows a tooltip explaining the cap (free) or the unlimited tier (pro/enterprise) — copy reuses the existing 0833 quota copy strings if available, otherwise short purpose-built strings.
- [ ] **AC-US2-04**: `StatusBar.tsx` imports `SkillCountBadge` and renders it in the right slot of the status bar.
- [ ] **AC-US2-05**: New unit tests in `src/eval-ui/src/__tests__/SkillCountBadge.test.tsx` cover three tier fixtures (`free` with 0/25/50 counts, `pro` with any count, `enterprise` with any count) and assert the rendered label + tooltip text.
- [ ] **AC-US2-06**: Existing `StatusBar.tsx` tests pass with the new mount; one new test asserts the badge is rendered when the user is signed in.

---

### US-003: Adopt lucide-react as the single icon library (P1)
**Project**: vskill

**As a** developer maintaining the UI
**I want** a single icon library across the app
**So that** I am not hand-rolling inline SVGs in every component.

**Context**: Icons are currently inline SVG (e.g., `SkillFileTree`'s `FolderIcon` at 13×13). `lucide-react` (MIT, ~40KB tree-shaken) is industry standard and aligns with shadcn/ui patterns the team already uses on the platform side. Pragmatist trio member chose this over `@primer/octicons-react` because it is not GitHub-themed and Lucide's icon set covers the WorkspaceTree state machine cleanly.

**Acceptance Criteria**:
- [ ] **AC-US3-01**: `package.json` adds `lucide-react` as a runtime dependency at the version current at install time.
- [ ] **AC-US3-02**: At least **5 inline SVG icons** across `Sidebar.tsx`, `SkillFileTree.tsx`, and `StatusBar.tsx` are migrated to Lucide equivalents (at minimum: `Folder`, `FolderOpen`, `FileText`, `GitBranch`, `Lock`, `Globe`, `ChevronRight`, `ChevronDown` — pick five plus from this set).
- [ ] **AC-US3-03**: Migrated icons use `currentColor` so they inherit existing Tailwind 4 text-color tokens (no hardcoded hex values in new icon usages).
- [ ] **AC-US3-04**: Bundle-size delta is **under 50KB gzipped**, verified by inspecting the production build output before and after the change and recording both numbers in `reports/bundle-size.md`.
- [ ] **AC-US3-05**: Visual regression: existing screenshot or Playwright snapshot tests pass with the new icons, OR snapshots are explicitly updated in this increment's diff with a one-line justification per updated snapshot.

---

### US-004: WorkspaceTree aggregates roots into a connected/disconnected tree (P1)
**Project**: vskill

**As a** vskill user with multiple workspace folders
**I want** a tree-view sidebar that shows each folder's GitHub-connection state at a glance
**So that** I can see which folders are connected, which need to be linked, and the sync state of each connected repo.

**Context**: This is the new visual surface and the increment's largest deliverable. It is a **sibling component**, not a refactor of `Sidebar.tsx`. Workspace roots come from the existing `~/.vskill/workspace.json` store. Per-root info is aggregated by a new Tauri IPC `list_workspace_roots_with_repo_info()` that wraps the existing 0831 `folders/classifier.rs` and `folders/git_remote.rs` logic, parallelized via `rayon`. The renderer uses `react-virtuoso` (already in deps).

Per-row state machine (one of):

| State | Trigger | Visual |
|---|---|---|
| `loading` | IPC pending or 5s timeout retry | slate-400 dot, skeleton text |
| `no_git` | folder is not a git repo | folder icon, basename only |
| `no_remote` | git repo with no remote | folder icon, basename + "no remote" pill |
| `non_github` | remote points elsewhere (incl. GHES) | folder icon, host pill, "GHES is Phase 3" tooltip |
| `disconnected` | github.com remote, user not connected to that org | folder icon, owner/repo, **Connect to GitHub** CTA |
| `connected` | github.com remote, user signed in, repo accessible | avatar + owner/repo + branch + visibility badge + sync dot |
| `error` | classifier or git-remote threw | red-500 dot, inline retry CTA |

**Acceptance Criteria**:
- [ ] **AC-US4-01**: New file `src/eval-ui/src/components/WorkspaceTree.tsx` is added; it accepts no props and reads workspace roots via the new IPC `list_workspace_roots_with_repo_info()`.
- [ ] **AC-US4-02**: For each workspace root the component renders one tree row showing: folder icon, owner/repo (when connected) or basename (when disconnected), branch (when connected), public/private badge (when connected), and a 6px sync-state status dot.
- [ ] **AC-US4-03**: Each row implements all seven state-machine variants `{ loading | no_git | no_remote | non_github | disconnected | connected | error }` with a distinct icon, color, and interactivity per variant per the table above.
- [ ] **AC-US4-04**: Disconnected rows show a "Connect to GitHub" CTA; clicking it opens `AccountShell.tsx` at the existing 0834 route `/account/repos/connect` (no new auth flow).
- [ ] **AC-US4-05**: Avatar URLs are cached in-memory in the renderer via `Map<owner, url>` so a single fetch happens per org per session; cache is cleared on sign-out and on app reload.
- [ ] **AC-US4-06**: Tree uses `react-virtuoso` for virtualization and renders 100+ rows without DOM bloat (asserted by a test that mounts 200 fixture rows and confirms the rendered DOM contains fewer than 60 row nodes).
- [ ] **AC-US4-07**: Tree renders within **500ms** of mount on a workspace with 100 roots, measured via a vitest timing assertion against an IPC stub returning 100 fixture entries (budget: stub returns immediately, render-to-stable budget is 500ms wall clock).
- [ ] **AC-US4-08**: Right-click menu offers **View on GitHub** (uses the existing `open_external_url` IPC), **Refresh** (re-runs the IPC for that one root), and **Disconnect** (clears local mapping, returns the row to `disconnected`) actions per row.
- [ ] **AC-US4-09**: Keyboard navigation supports Arrow Up/Down/Right/Left and Enter, following the pattern already used by `SkillFileTree.tsx` (108 LOC reference); focus is visible and respects existing Tailwind focus-ring tokens.
- [ ] **AC-US4-10**: Empty state ("No workspace roots — open a folder", with CTA to existing workspace-picker IPC) and loading skeleton are implemented and visually consistent with existing Studio shell density: 28px row height, 14-16px icon size, 1px indent guides at 50% opacity.

---

### US-005: Sandbox-PAT E2E rig proves the GitHub flow end-to-end (P1)
**Project**: vskill

**As a** member of the team-of-agents shipping this app
**I want** an automated E2E test that proves "sign in → see tree → see connected vs disconnected → click through to GitHub" works against a real GitHub account
**So that** future regressions are caught before release.

**Context**: Uses `anton-abyzov/vskill-test-sandbox` (create the repo if missing) plus a **fine-grained read-only** Personal Access Token. The PAT is seeded into the OS keychain via the existing `cfg(feature = "test-fixture")` IPC on the desktop side. Pre-flight is mandatory because a misconfigured PAT (write access to non-sandbox repos) is a real risk and must fail loudly.

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A new Playwright test `e2e/desktop/workspace-tree-sandbox.spec.ts` boots the desktop app with `VSKILL_TEST_GITHUB_PAT` seeded into the keychain via the existing test-fixture IPC (gated by `cfg(feature = "test-fixture")` on the Rust side so production builds cannot hit it).
- [ ] **AC-US5-02**: Pre-flight: the test **fails loudly** if the PAT has write access to any non-sandbox repo. A probe write to a forbidden repo MUST return HTTP 403; if it does not, the test aborts with a clear "PAT is over-scoped" error before any other assertion runs.
- [ ] **AC-US5-03**: Test asserts (a) Sidebar shows the user's avatar and login (from `account_get_user_summary`), (b) `WorkspaceTree` displays the test-sandbox folder as `connected` with branch `main`, visibility `public`, sync `clean`, (c) `WorkspaceTree` displays a non-git folder as `disconnected` with the **Connect to GitHub** CTA visible, (d) right-clicking the connected row and choosing **View on GitHub** invokes the stubbed `open_external_url` IPC with `https://github.com/anton-abyzov/vskill-test-sandbox`.
- [ ] **AC-US5-04**: Any test artifacts (test-`*` branches, PRs created during the test run) are deleted in a teardown step that runs even on test failure.
- [ ] **AC-US5-05**: The test **skips with a clear message** if `VSKILL_TEST_GITHUB_PAT` is unset; the suite must not fail in CI environments without the secret.
- [ ] **AC-US5-06**: A README at `e2e/desktop/README.md` documents how to obtain the PAT, the required scopes (`contents:read`, `metadata:read`, `pull-requests:read`), and the **30-day rotation reminder**.

## Functional Requirements

### FR-001: Single-call workspace-roots aggregation IPC
A new Tauri IPC `list_workspace_roots_with_repo_info()` returns `Vec<WorkspaceRootInfo>` where each entry carries `{ root_path, classification, repo: Option<RepoInfo>, sync_state }`. Implemented in Rust, parallelized over roots via `rayon`, using existing `folders/classifier.rs` and `folders/git_remote.rs`. Per-root probe has a 5-second timeout via `tokio::time::timeout`; on timeout the row surfaces `loading` with retry. Reads filesystem only — no network, no token use, no new attack surface.

### FR-002: Renderer-side avatar cache
A `Map<owner, url>` in the renderer caches avatar URLs for the lifetime of the session. Cache is invalidated on sign-out and on app reload. github.com avatars are stable, so a single fetch per org per session is sufficient.

### FR-003: State-machine row component
A pure presentational component renders one of seven states from a discriminated-union `WorkspaceRootInfo`. Icons resolve from `lucide-react`. Colors come from existing Tailwind 4 tokens (emerald-500 connected/clean, amber-500 dirty/ahead, red-500 error, slate-400 loading, violet-500 private, neutral disconnected). Hover row tint and 3px accent left-edge bar on selection use existing tokens.

### FR-004: Re-scan on workspace.json change
The existing chokidar watcher on `~/.vskill/workspace.json` triggers a full re-scan with a 300ms debounce. No webhooks, no real-time GitHub sync (Phase 4).

### FR-005: Sibling mount, no Sidebar refactor
`WorkspaceTree` mounts as a **sibling** of `Sidebar.tsx`, not a child or a replacement. The 1502-LOC `Sidebar.tsx` is not refactored in this increment.

### FR-006: Test-fixture gating
The test-fixture IPC used in US-005 is compiled in only with `cfg(feature = "test-fixture")` on the Rust side and is **not** present in production binaries shipped to users.

## Non-Functional Requirements

- **NFR-001 (Notarization)**: ZERO changes to `src-tauri/Entitlements.plist`. Apple notarization must continue to pass without manual intervention.
- **NFR-002 (Capabilities)**: ZERO new Tauri capabilities or plugin allowlist additions. The new IPC reuses existing filesystem access already granted to 0831 paths.
- **NFR-003 (Dependencies)**: Exactly **one** new npm dependency permitted: `lucide-react`. No `@primer/octicons-react`, no `react-arborist`, no others.
- **NFR-004 (Security posture, 0836)**: All hardening from 0836 must continue to pass: loopback bind, `X-Studio-Token` on every API call, no token in the WebView, canonical keychain. Verified by re-running 0836's hardening test suite as a closure gate.
- **NFR-005 (Performance)**: WorkspaceTree mount-to-stable for 100 roots is under 500ms (AC-US4-07). Single avatar fetch per org per session (FR-002).
- **NFR-006 (Bundle size)**: Net production bundle delta under 50KB gzipped (AC-US3-04).
- **NFR-007 (LOC discipline)**: Sidebar.tsx grows by under 50 net LOC (AC-US1-04). No file in this increment exceeds the 1500-LOC project limit.

## Success Criteria

- **Functional**: All ACs across US-001…US-005 marked `[x]` in `tasks.md` with passing tests.
- **Quality gates** (closure-blocking): `code-review-report.json` clean of critical/high/medium findings, `grill-report.json` present, `judge-llm-report.json` present (or waived with consent), Playwright sandbox suite green when PAT is seeded.
- **Performance**: 100-root WorkspaceTree mounts in under 500ms (vitest assertion). 200-row virtualization keeps DOM under 60 row nodes.
- **Security regression check**: 0836 hardening tests still green; new IPC adds no network surface; production build does not contain `cfg(feature = "test-fixture")` code.
- **User-visible outcome**: Anton can sign in to GitHub from inside the macOS app, see his workspace folders mapped to GitHub repos in a tree-view sidebar with proper Lucide icons, distinguish connected from disconnected at a glance, and click through to `/account/repos/connect` for any disconnected folder.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Sandbox PAT is over-scoped (write access to private repos) | Med | High | AC-US5-02 pre-flight asserts a probe write to a forbidden repo returns 403, aborting before any other test runs. README at `e2e/desktop/README.md` documents the exact scope set. |
| WorkspaceTree perf degrades on slow disks (network drives, encrypted FUSE) | Med | Med | Per-root probe has 5s `tokio::time::timeout`; on timeout the row enters `loading` with retry CTA (AC-US4-03 + edge-case 6 in interview state). |
| `lucide-react` upstream changes an icon name | Low | Low | Pin the version in `package.json` at install time; migrated icons centralize the mapping so a future swap is one file. |
| GHES users see the row as `error` and file bug reports | Low | Med | `non_github` state with a tooltip "GitHub Enterprise Server is a Phase 3 feature" — explicit, not an error (edge-case 5). |
| Sidebar.tsx test snapshots churn from the new mount | Med | Low | AC-US1-04 caps Sidebar growth at <50 LOC; AC-US3-05 allows snapshot updates with one-line justification. |
| Worktrees and submodules confuse the classifier | Low | Med | Reuse existing 0831 `folders/git_remote.rs` behavior (submodule classified as connected via parent repo URL; multiple remotes prefer `origin`); de-dupe by `(owner, repo)` in renderer (edge-cases 2, 3, 4). |
| Avatar fetch fails (rate limit, offline) | Low | Low | Fall back to generated initial-letter SVG matching github.com convention (edge-case 7). |
| Notarization regression from new code paths | Low | High | NFR-001 and NFR-002 prohibit any entitlement or capability change; closure gate runs the existing notarization smoke test on a `--release` build. |

## Definition of Done

A PM-authored checklist used by `/sw:done` to validate closure:

1. **Tasks**: All tasks in `tasks.md` are `[x]` with linked test runs.
2. **ACs**: All ACs across US-001…US-005 are `[x]` in `spec.md`.
3. **Tests green**:
   - `npx vitest run` passes (unit + integration including the 100-root timing assertion and 200-row virtualization assertion).
   - `npx playwright test e2e/desktop/workspace-tree-sandbox.spec.ts` passes when `VSKILL_TEST_GITHUB_PAT` is set, and skips cleanly when it is not.
   - Existing 0836 hardening test suite still green.
4. **Code review**: `code-review-report.json` shows zero critical/high/medium findings (fix loop, max 3 iterations).
5. **Simplify**: `/simplify` run produces no actionable findings, or findings are addressed.
6. **Grill**: `grill-report.json` present, severity counts at acceptable thresholds.
7. **Judge LLM**: `judge-llm-report.json` present, or explicit consent-denied waiver recorded.
8. **PM 3-gate validation** (`/sw:done`):
   - Tasks gate (all tasks complete and tested)
   - Tests gate (all suites green, sandbox suite green-or-skipped)
   - Docs gate (`spec.md`, `plan.md`, `tasks.md` consistent; living docs synced via `sw:sync-docs`)
9. **Constraints honored**:
   - No `Entitlements.plist` change (NFR-001)
   - No new Tauri capability (NFR-002)
   - Exactly one new npm dep (`lucide-react`) (NFR-003)
   - Sidebar.tsx <50 net LOC growth (AC-US1-04)
   - Bundle delta <50KB gzipped, recorded in `reports/bundle-size.md` (AC-US3-04, NFR-006)
10. **External sync**: GitHub issue updated via `/sw:progress-sync` once tasks reach 100%.

## Dependencies

- **0831 (Skill Studio Enterprise Tier)** — provides `ConnectedRepoWidget`, `SkillCountBadge`, `folders/classifier.rs`, `folders/git_remote.rs`, OAuth Device Flow auth.
- **0834 (Account Cabinet)** — provides `AccountShell.tsx`, `useConnectedRepos`, `ConnectedReposTable`, the `/account/repos` and `/account/repos/connect` deep-link routes.
- **0836 (Security Hardening)** — provides loopback bind, `X-Studio-Token`, post-WebView token isolation, canonical keychain. **Must not regress.**
- **Existing deps** — `react-virtuoso` (virtualization), `zustand` (tree state, used by 0828), Tailwind 4 (tokens), `chokidar` (workspace.json watcher), `git2`/libgit2 (Cargo, from 0831), `rayon` (Cargo).

## References

- **Brainstorm**: Advocate / Critic / Pragmatist trio, 2026-05-09 — Pragmatist's reuse-and-mount approach selected over Advocate's larger ambitions and Critic's pure-no-change posture.
- **Interview state**: `.specweave/state/interview-0843-skill-studio-workspace-tree.json` — six categories covered (architecture, integrations, ui-ux, performance, security, edge-cases).
- **0831 spec**: `.specweave/increments/0831-skill-studio-enterprise-tier/spec.md`
- **0834 spec**: `.specweave/increments/0834-account-cabinet/spec.md`
- **0836 spec**: `.specweave/increments/0836-skill-studio-security-hardening/spec.md` (referenced for hardening invariants)
- **Mount targets**: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/Sidebar.tsx`, `StatusBar.tsx`
- **Reuse targets**: `ConnectedRepoWidget.tsx` (580 LOC, 0831), `SkillCountBadge.tsx` (0831), `AccountShell.tsx` (650 LOC, 0834), `useConnectedRepos.ts` (0834), `SkillFileTree.tsx` (108 LOC reference for keyboard nav)
- **New IPC site**: `repositories/anton-abyzov/vskill/src-tauri/src/lib.rs` (registration), Rust modules layered on `src-tauri/src/folders/{classifier,git_remote}.rs`
