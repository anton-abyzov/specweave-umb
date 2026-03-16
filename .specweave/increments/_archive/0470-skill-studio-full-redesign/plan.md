# Architecture Plan: Skill Studio Full Redesign

## 1. Overview

Transform the Skill Studio from a sidebar-nav + page-route architecture to a master-detail split-pane layout. The skill list becomes a permanent left panel, the workspace becomes an inline right panel with tabbed navigation replacing the LeftRail icon bar, and all full-page navigation is eliminated.

**Repository**: `repositories/anton-abyzov/vskill/`
**Target code**: `src/eval-ui/` (React 19 + Vite 6 + Tailwind v4)
**Server**: `src/eval-server/` (custom Node.js HTTP server)
**CLI**: `src/commands/eval.ts` + `src/commands/eval/serve.ts` + `src/index.ts`

## 2. Architecture Decisions

### AD-01: Layout Model -- Split-Pane via CSS Grid

**Decision**: Replace the current `flex h-screen` sidebar+main layout in `App.tsx` with a CSS Grid root: `grid-template-columns: 280px 1px 1fr`. The 1px column is the visual divider.

**Rationale**: CSS Grid gives precise column sizing, the divider can be a simple styled `<div>` rather than border trickery, and both panels get independent scroll containers naturally. The `280px` is fixed per spec (no drag-resize, per out-of-scope).

**What changes**:
- `App.tsx` -- gutted and rebuilt as the split-pane shell
- Sidebar nav (NAV_ITEMS, Links) -- removed entirely
- `HashRouter` and `<Routes>` -- replaced with state-driven rendering

**What stays**: `ModelSelector` component, `api.ts`, `globals.css` design tokens, all six workspace panel components.

### AD-02: Navigation Model -- State-Based, No Router

**Decision**: Remove `react-router-dom` entirely. Navigation is driven by a single `selectedSkill: { plugin: string; skill: string } | null` state in a new top-level `StudioContext`.

**Rationale**: The redesign eliminates all page-level routes. The skill list and detail panel coexist on the same screen -- there are no "pages" to route between. The existing `WorkspaceProvider` uses `useSearchParams` to sync the active panel to the URL; this will be replaced with local state.

**Impact on existing code**:

| Component | Change |
|-----------|--------|
| `WorkspaceProvider` | Remove `useSearchParams` import and both `useEffect` hooks that sync panel to/from URL. Active panel is already in reducer state. |
| `WorkspaceHeader` | Remove `<Link to="/">Skills</Link>` breadcrumb. Replace with static breadcrumb text (list is always visible). Logic extracted into new `DetailHeader`. |
| `CreateSkillPage` | Remove `useNavigate`. After creation, call a callback prop `onCreated(plugin, skill)` instead. |
| `SkillListPage` | Decomposed into `SkillGroupList`, `SkillCard`, `SkillGroupHeader`. `<Link>` elements become `<button>` click handlers. |
| `SkillWorkspace` | Remove `useParams`. Accept `plugin`/`skill` as props. |
| `main.tsx` | Remove `HashRouter` wrapper. |

### AD-03: Component Decomposition

```
App.tsx (StudioProvider shell)
  StudioLayout.tsx
    LeftPanel (280px)
      StudioHeader            -- brand, project name, ModelSelector
      SkillSearch             -- search input + summary count
      NewSkillButton          -- accent button, triggers create mode
      SkillGroupList          -- scrollable grouped skill cards
        SkillGroupHeader      -- plugin name, icon, skill count
        SkillCard             -- name, stats, status pill, selected state
    Divider (1px)
    RightPanel (flex: 1)
      (no skill selected)     -> EmptyState "Select a skill"
      (creating)              -> CreateSkillInline (adapted CreateSkillPage)
      (skill selected)        -> WorkspaceProvider wrapping detail view
        DetailHeader          -- breadcrumb + status pills + counts
        TabBar                -- 6 horizontal tabs with icons + dots
        TabContent            -- active panel component
```

**Reuse matrix**:

| Component | Reuse | Modification |
|-----------|-------|-------------|
| `EditorPanel` | As-is | None |
| `TestsPanel` | As-is | None |
| `RunPanel` | As-is | None |
| `ActivationPanel` | As-is | None |
| `HistoryPanel` | As-is | None |
| `DepsPanel` | As-is | None |
| `ModelSelector` | As-is | None |
| `WorkspaceProvider` | Mostly as-is | Remove `useSearchParams` usage |
| `WorkspaceHeader` | Replaced | Logic extracted into new `DetailHeader` |
| `SkillListPage` | Decomposed | Split into `SkillGroupList` + `SkillCard` + `SkillGroupHeader` |
| `LeftRail` | Removed | Replaced by horizontal `TabBar` |
| `CreateSkillPage` | Adapted | Remove router deps, add `onCreated` callback |

### AD-04: State Architecture -- Two-Layer Context

**Layer 1 -- StudioContext** (new, lightweight):
```
selectedSkill: { plugin: string; skill: string } | null
mode: "browse" | "create"
searchQuery: string
skills: SkillInfo[]
skillsLoading: boolean
skillsError: string | null
isMobile: boolean          // viewport < 768px
mobileView: "list" | "detail"
```
Actions: `selectSkill`, `clearSelection`, `setMode`, `setSearch`, `refreshSkills`

**Layer 2 -- WorkspaceContext** (existing, per-skill):
- Unchanged except removing `useSearchParams` dependency
- Instantiated fresh when `selectedSkill` changes via React key (`${plugin}/${skill}`)
- Switching skills unmounts/remounts, which triggers `sseStopAll` cleanup

**Why not merge**: WorkspaceContext manages complex per-skill state (SSE streams, run states, inline results, activation). Mixing studio-level state into it would create unnecessary coupling and re-renders across unrelated concerns.

### AD-05: Tab Bar Design -- Horizontal Tabs Replacing LeftRail

**Decision**: Replace the 48px-wide vertical icon LeftRail with a horizontal tab bar below the detail header.

**Design**:
- Full-width row of 6 text tabs with icons: Editor, Tests, Run, Activation, History, Deps
- Grouped with subtle separators matching the LeftRail groups: Build (Editor, Tests) | Evaluate (Run, Activation) | Insights (History, Deps)
- Active tab: bottom 2px accent border + `var(--text-primary)` color
- Inactive: `var(--text-tertiary)`, hover `var(--text-secondary)`
- Activity dots preserved (dirty indicator on Editor, running on Run, activation running, regressions on History)
- Keyboard shortcuts (Ctrl+1..6) preserved via existing `handleKeyDown` in `WorkspaceInner`

**Rationale**: The LeftRail's icon-only 48px column was necessary when the workspace needed all remaining width. In the master-detail layout, horizontal tabs give clearer labels (text + icon vs icon-only) and the detail panel uses a `flex-col` layout (header -> tabs -> content) instead of a grid with the rail.

### AD-06: Responsive Layout -- CSS Media Queries + useMediaQuery Hook

**Below 768px**: Single-column layout.
- Default: Show only the left panel (skill list)
- Selecting a skill transitions to a full-width detail view with a back button
- Back button restores skill list, preserving search/filter state
- Driven by `StudioContext.mobileView`: `"list"` | `"detail"`

**768px -- 1024px**: Left panel narrows from 280px to 240px via media query override on the grid template.

**Above 1024px**: Full split-pane at 280px / 1fr.

### AD-07: CLI -- `vskill studio` as Top-Level Command

**Decision**: Add a new top-level Commander command `studio` in `src/index.ts` that delegates to `runEvalServe()`.

```typescript
program
  .command("studio")
  .description("Launch the Skill Studio UI for local skill development")
  .option("--root <path>", "Root directory (default: current dir)")
  .option("--port <number>", "Port for Skill Studio server")
  .action(async (opts) => {
    const { runEvalServe } = await import("./commands/eval/serve.js");
    const root = opts.root ? resolve(opts.root) : resolve(".");
    const port = opts.port ? parseInt(opts.port, 10) : null;
    await runEvalServe(root, port);
  });
```

**Banner**: The server already prints `"Skill Studio: http://localhost:${port}"` in `eval-server.ts` line 81. AC-US5-05 is already satisfied.

`vskill eval serve` continues to work unchanged (AC-US5-04).

### AD-08: Category Icons via Nano Banana Pro

**Decision**: One-time generation script at `scripts/generate-studio-icons.ts`.

**Implementation**:
- Script calls Nano Banana Pro API (`gemini-3-pro-image-preview`) with VertexAI key
- Prompt: "Minimalist line-art icon representing {plugin-name}, white lines on transparent background, 32x32 pixels, single subject, no text"
- Output stored as `src/eval-ui/public/images/icons/{plugin-name}.webp` (32x32 WebP)
- Empty-state illustration: `src/eval-ui/public/images/empty-studio.webp` (128x128, theme-neutral)
- Fallback: Missing icon renders `IconSkills` SVG (the existing box/package icon) at 16x16

**Eval server change**: Add `.webp: "image/webp"` to `MIME_TYPES` in `eval-server.ts`.

**Why build-time, not runtime**: Icons are static per plugin name. Runtime generation would require API keys in the running environment and add startup latency.

### AD-09: Search -- Client-Side with Debounce

**Decision**: Client-side filtering using 200ms debounce via `setTimeout` in `StudioContext`. No server-side search needed.

**Rationale**: Spec explicitly notes local skill counts are small. The full list is fetched on mount via `api.getSkills()`.

**Implementation**: `StudioContext` maintains `searchQuery` (raw) and computes `filteredSkills` via `useMemo` over the debounced query: `skills.filter(s => s.skill.toLowerCase().includes(debouncedQuery.toLowerCase()))`.

## 3. File Change Map

### New Files

| File | Purpose |
|------|---------|
| `src/eval-ui/src/StudioContext.tsx` | Top-level studio state (selected skill, search, mode, responsive) |
| `src/eval-ui/src/components/StudioLayout.tsx` | Root split-pane CSS Grid layout |
| `src/eval-ui/src/components/LeftPanel.tsx` | Left panel container (header + search + new button + list) |
| `src/eval-ui/src/components/RightPanel.tsx` | Right panel container (detail, empty state, or create form) |
| `src/eval-ui/src/components/SkillSearch.tsx` | Search input with 200ms debounce |
| `src/eval-ui/src/components/SkillGroupList.tsx` | Grouped scrollable skill cards |
| `src/eval-ui/src/components/SkillCard.tsx` | Individual skill card with selection highlight |
| `src/eval-ui/src/components/TabBar.tsx` | Horizontal 6-tab bar with icons and activity dots |
| `src/eval-ui/src/components/DetailHeader.tsx` | Skill detail header (breadcrumb + stats pills) |
| `src/eval-ui/src/components/EmptyState.tsx` | Empty states (no selection, no skills, search miss, error) |
| `src/eval-ui/src/components/CreateSkillInline.tsx` | Inline skill creation (adapted from CreateSkillPage) |
| `src/eval-ui/src/hooks/useMediaQuery.ts` | Responsive breakpoint detection hook |
| `scripts/generate-studio-icons.ts` | One-time Nano Banana Pro icon generation script |

### Modified Files

| File | Change |
|------|--------|
| `src/eval-ui/src/App.tsx` | Rewrite as `StudioProvider` + `StudioLayout` |
| `src/eval-ui/src/main.tsx` | Remove `HashRouter` wrapper |
| `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` | Remove `useSearchParams` import and URL sync effects |
| `src/eval-ui/src/pages/workspace/SkillWorkspace.tsx` | Accept `plugin`/`skill` as props, remove `useParams` |
| `src/eval-ui/src/pages/CreateSkillPage.tsx` | Remove `useNavigate`, add `onCreated` callback prop |
| `src/index.ts` | Add `studio` command (insert before `program.parse()`) |
| `src/eval-server/eval-server.ts` | Add `.webp: "image/webp"` to `MIME_TYPES` |
| `src/eval-ui/src/styles/globals.css` | Add tab bar styles, responsive breakpoint rules |
| `src/eval-ui/package.json` | Remove `react-router-dom` |

### Removed Files

| File | Replacement |
|------|-------------|
| `src/eval-ui/src/pages/workspace/LeftRail.tsx` | `TabBar.tsx` (horizontal tabs) |
| `src/eval-ui/src/pages/workspace/WorkspaceHeader.tsx` | `DetailHeader.tsx` |
| `src/eval-ui/src/pages/SkillListPage.tsx` | `SkillGroupList.tsx` + `SkillCard.tsx` + `SkillGroupHeader` |

## 4. Data Flow Diagrams

### Skill Selection

```
SkillCard click
  -> StudioContext.selectSkill({ plugin, skill })
  -> selectedSkill state updates
  -> RightPanel re-renders, key={`${plugin}/${skill}`}
  -> WorkspaceProvider mounts fresh (old one unmounts, SSE cleaned up)
  -> WorkspaceProvider fetches detail + evals + benchmark via api.*
  -> DetailHeader + TabBar + active panel render with loaded data
```

### Search

```
User keystroke in SkillSearch
  -> raw query stored immediately (controlled input)
  -> 200ms debounce fires StudioContext.setSearch(debouncedQuery)
  -> useMemo recomputes filteredSkills
  -> SkillGroupList re-renders with filtered list
  -> Empty groups hidden, empty-results message shown if 0 matches
```

### Skill Creation

```
"New Skill" button click
  -> StudioContext.setMode("create")
  -> RightPanel renders CreateSkillInline
  -> User fills form, submits
  -> CreateSkillInline calls api.createSkill(...)
  -> onCreated(plugin, skill) callback fires
  -> StudioContext.refreshSkills() + selectSkill({ plugin, skill })
  -> mode resets to "browse", new skill auto-selected
```

### Mobile Navigation (< 768px)

```
Default: mobileView = "list", only LeftPanel visible
  -> User taps SkillCard
  -> selectSkill() + setMobileView("detail")
  -> LeftPanel hidden, RightPanel full-width with back button
  -> User taps back button
  -> setMobileView("list")
  -> LeftPanel visible again, search state preserved
```

## 5. Implementation Phases

### Phase 1: Foundation (US-005 + infrastructure)

1. Add `vskill studio` CLI command in `src/index.ts`
2. Add `.webp` MIME type to `eval-server.ts`
3. Create `StudioContext.tsx` with state management
4. Create `useMediaQuery.ts` hook
5. Remove `react-router-dom` from `package.json`, update `main.tsx`

### Phase 2: Layout Shell (US-001)

1. Create `StudioLayout.tsx` with CSS Grid
2. Create `LeftPanel.tsx` container
3. Create `RightPanel.tsx` container
4. Create `StudioHeader.tsx` (brand + ModelSelector)
5. Rewrite `App.tsx` as `StudioProvider` + `StudioLayout` shell
6. Add responsive CSS for 768px and 1024px breakpoints to `globals.css`

### Phase 3: Skill List (US-002 + US-008 partial)

1. Create `SkillSearch.tsx` with debounced input
2. Create `SkillGroupHeader` with plugin name and icon
3. Create `SkillCard.tsx` with selection state and status pill
4. Create `SkillGroupList.tsx` composing headers and cards
5. Create `EmptyState.tsx` for no-skills and no-search-results
6. Wire `StudioContext` skill loading and search filtering

### Phase 4: Detail Panel (US-003 + US-008 partial)

1. Create `DetailHeader.tsx` extracting logic from `WorkspaceHeader`
2. Create `TabBar.tsx` with horizontal tabs, icons, and activity dots
3. Modify `WorkspaceProvider` to remove `useSearchParams` dependency
4. Modify `SkillWorkspace.tsx` to accept props instead of `useParams`
5. Wire `RightPanel` to render `WorkspaceProvider` + tabs + panel content
6. Create error state with retry button in `RightPanel`
7. Preserve keyboard shortcuts (Ctrl+1..6)

### Phase 5: Skill Creation Inline (US-004)

1. Create `CreateSkillInline.tsx` adapting `CreateSkillPage`
2. Add `onCreated` callback for post-creation skill selection
3. Add "New Skill" button in `LeftPanel` below search
4. Wire active state on the button when create mode is active

### Phase 6: Responsive Layout (US-006)

1. Implement mobile view toggle via `StudioContext.mobileView`
2. Add back button in `RightPanel` for mobile view
3. CSS media queries for single-column at < 768px
4. Left panel width reduction at 768px-1024px
5. Verify search/filter state preservation on back navigation

### Phase 7: Category Icons (US-007)

1. Create `scripts/generate-studio-icons.ts` using Nano Banana Pro API
2. Generate icons for known plugin groups
3. Generate empty-state illustration
4. Store assets in `src/eval-ui/public/images/icons/`
5. Wire icon rendering in `SkillGroupHeader` with fallback

## 6. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| WorkspaceProvider remounting on skill switch kills SSE streams | Medium | Correct behavior. `sseStopAll` runs on unmount, cleaning up streams. Switching skills should abandon previous runs. |
| CreateSkillPage depends on `useNavigate` | Low | Only used for post-creation redirect. Replace with `onCreated` callback prop -- one line. |
| WorkspaceHeader uses `<Link>` for breadcrumb back-nav | Low | List is always visible; replace `<Link>` with `<span>`. |
| Performance with 50+ skills | Low | ~4000px scroll height, no virtualization needed. Search filter reduces rendered count. |
| `react-router-dom` removal breaks imports in panel components | Medium | Verified: none of the 6 panel components (`EditorPanel`, `TestsPanel`, `RunPanel`, `ActivationPanel`, `HistoryPanel`, `DepsPanel`) import from `react-router-dom`. Only `WorkspaceHeader`, `WorkspaceContext`, `SkillListPage`, `CreateSkillPage`, `App.tsx`, and `main.tsx` use it. |

## 7. Testing Strategy

- **Unit tests**: `StudioContext` reducer logic, search debounce and filtering, `useMediaQuery` hook
- **Component tests**: `SkillCard` selection state rendering, `TabBar` active tab + activity dots, `EmptyState` variants (no selection, no skills, search miss, error)
- **Integration tests**: Click skill card -> detail renders, type search -> filter applies, create skill -> list refreshes and selects
- **E2E tests**: Launch via `vskill studio` -> skill list loads -> select skill -> switch tabs -> all panels render
- **Responsive tests**: Viewport resize triggers mobile layout, back button works, search state preserved

## 8. No New Runtime Dependencies

The redesign **removes** `react-router-dom` and adds zero new runtime dependencies. All components use React 19 built-ins, Tailwind v4, and the existing CSS variable system.

The icon generation script (`scripts/generate-studio-icons.ts`) is dev-time only, using native `fetch`.
