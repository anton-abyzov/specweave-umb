# Implementation Plan: Studio Skill Origin Classification (Consumed vs Editable)

## Overview

Add an `origin` field (`"source" | "installed"`) to every scanned skill by detecting whether its path falls under an agent config directory or other known non-source prefixes. The sidebar splits into two collapsible sections ("Your Skills" / "Installed"), installed skills render with reduced visual weight and a lock icon, and the detail panel disables editing/benchmarking for installed skills. All detection logic is derived from the existing `AGENTS_REGISTRY` plus a small hardcoded supplementary list -- no new dependencies, no API changes, no schema migrations.

## Architecture

### Decision: Path-Prefix Detection over Content Analysis

Origin classification uses **path prefix matching** against the skill's `dir` relative to the scanner `root`. This is deterministic, zero-cost (no file I/O beyond what the scanner already does), and leverages the existing `AGENTS_REGISTRY` as the authoritative source of agent directory patterns.

**Why not content analysis?** Installed and source SKILL.md files are identical in content -- they are literal copies. The only distinguishing signal is *where* they live on disk.

### Decision: Prefix Extraction from `localSkillsDir`

Each agent in `AGENTS_REGISTRY` has a `localSkillsDir` like `.claude/skills`, `.cursor/skills`, `.amp/skills`. The classifier extracts the **top-level directory segment** (e.g., `.claude/`, `.cursor/`, `.amp/`) as the prefix to match. Any relative path starting with that prefix is agent-owned.

The extraction is: `localSkillsDir.split('/')[0] + '/'` -- giving us `.claude/`, `.cursor/`, `.github/`, etc.

We also add `pluginCacheDir` prefixes from agents that define them (e.g., Claude Code's `~/.claude/plugins/cache`), but those only apply to global paths. For local paths, the `plugins/cache/` substring check (AC-US1-03) covers all plugin caches regardless of agent.

### Decision: Read-Only Mode via Context Propagation

The `origin` field flows from scanner -> API -> `SkillInfo` type -> `StudioContext` -> `SelectedSkill` -> `WorkspaceProvider`. The workspace checks `origin === "installed"` to conditionally disable run/edit controls. This avoids a new API endpoint or separate read-only mode flag -- the existing data flow carries the signal.

### Components

```
┌─────────────────────────────────────────────────────────────┐
│  skill-scanner.ts                                           │
│  ┌───────────────────────┐                                  │
│  │ classifyOrigin(dir,   │  New pure function               │
│  │   root) -> origin     │  Uses AGENTS_REGISTRY prefixes   │
│  └───────────┬───────────┘  + hardcoded extras + cache check│
│              │                                              │
│  scanSkills() ── adds `origin` to every SkillInfo ──────────│
└──────────────────────────────┬──────────────────────────────┘
                               │
                    API auto-spreads `...s`
                               │
┌──────────────────────────────▼──────────────────────────────┐
│  eval-ui                                                    │
│                                                             │
│  types.ts  ── SkillInfo gets `origin` field                 │
│                                                             │
│  StudioContext ── SelectedSkill gets `origin` field          │
│                                                             │
│  SkillGroupList ── splits skills into source/installed       │
│                    sections with section headers             │
│                                                             │
│  SkillCard ── dims installed skills, shows lock icon         │
│                                                             │
│  InfoBanner ── dismissable banner between sections           │
│                                                             │
│  RightPanel ── passes origin to WorkspaceProvider            │
│  WorkspaceProvider ── exposes isReadOnly derived from origin │
│  DetailHeader ── shows "Read-only" badge for installed       │
│  EditorPanel ── textarea disabled when installed             │
│  RunPanel ── run buttons disabled when installed             │
│  TestsPanel ── edit controls disabled when installed         │
└─────────────────────────────────────────────────────────────┘
```

### Data Model

No database changes. Single field addition to the `SkillInfo` interface:

```
SkillInfo (backend: src/eval/skill-scanner.ts)
──────────────────────────────────────────────
plugin         string
skill          string
dir            string
hasEvals       boolean
hasBenchmark   boolean
origin         "source" | "installed"    <-- NEW

SkillInfo (frontend: src/eval-ui/src/types.ts)
──────────────────────────────────────────────
...existing fields...
origin         "source" | "installed"    <-- NEW

SelectedSkill (StudioContext.tsx)
──────────────────────────────────────────────
plugin         string
skill          string
origin         "source" | "installed"    <-- NEW
```

### API Contracts

No new endpoints. The existing `GET /api/skills` response automatically includes `origin` because `api-routes.ts` uses `...s` spread on scanner results. The frontend `api.getSkills()` already returns whatever the server sends -- no API client change needed either.

## Technology Stack

- **Language/Framework**: TypeScript (Node.js ESM backend, React SPA frontend)
- **Libraries**: No new dependencies. Uses existing `AGENTS_REGISTRY` from `src/agents/agents-registry.ts`
- **Tools**: Vitest for testing

## Implementation Phases

### Phase 1: Backend -- Origin Classification (scanner)

1. **`classifyOrigin` function** in `skill-scanner.ts`
   - Import `AGENTS_REGISTRY` from `../agents/agents-registry.js`
   - Build a `Set<string>` of agent directory prefixes by extracting the first path segment from each `localSkillsDir` (e.g., `.claude/skills` -> `.claude/`)
   - Deduplicate (many agents share prefixes once you go to top-level dir)
   - Add hardcoded extra prefixes: `.specweave/`, `.vscode/`, `.idea/`, `.zed/`, `.devcontainer/`, `.github/`, `.agents/`, `.agent/`
   - Note: `.github/` is already covered by the GitHub Copilot agent entry (`.github/copilot/skills`), but we include it explicitly to catch non-skill files under `.github/` too. The dedup Set handles this.
   - Special case: check if relative path **contains** `plugins/cache/` (not prefix-only)
   - Compute relative path: `path.relative(root, dir)` and normalize to forward slashes
   - Match logic: if relPath starts with any prefix OR contains `plugins/cache/` -> `"installed"`, else `"source"`

2. **Add `origin` to `SkillInfo`** interface and all `skills.push()` call sites
   - Every place that constructs a `SkillInfo` object calls `classifyOrigin(skillDir, root)` to set the `origin` field
   - The `root` parameter is already available in `scanSkills(root)` and threaded through helpers

3. **Prefix computation is done once per `scanSkills` call** (module-level or closure), not per skill. The `AGENTS_REGISTRY` is a static array -- we compute prefixes eagerly.

### Phase 2: Frontend -- Type Updates and Sidebar Split

4. **Update `SkillInfo` in `types.ts`** -- add `origin: "source" | "installed"`

5. **Update `SelectedSkill` in `StudioContext.tsx`** -- add `origin` field so it propagates when a skill is selected

6. **Update `SkillGroupList.tsx`** -- replace plugin-based grouping with origin-based sectioning:
   - First partition all (filtered) skills into `source` and `installed` arrays
   - Within each section, keep existing plugin-based sub-grouping
   - Render "Your Skills" section header, then source skills grouped by plugin
   - Render "Installed" section header, then installed skills grouped by plugin
   - Omit section if its array is empty (AC-US2-02, AC-US2-03)
   - Preserve grouping within search results (AC-US2-04)

7. **Update `SkillCard.tsx`** -- visual de-emphasis for installed skills:
   - When `skill.origin === "installed"`: reduce opacity on text to 0.55, use tertiary color
   - Show a lock icon (inline SVG) next to the skill name for installed skills
   - Source skills: no icon, full opacity (current behavior)

8. **Add `InfoBanner` component** -- dismissable banner in the sidebar:
   - Rendered between "Your Skills" and "Installed" sections (or at top if both exist)
   - Text: "Your Skills are editable source skills you develop. Installed skills are copies consumed by AI agents."
   - Dismiss button stores state in `sessionStorage` key `vskill-origin-banner-dismissed`
   - Only shown when both sections have skills (AC-US5-01)

### Phase 3: Frontend -- Read-Only Mode for Installed Skills

9. **Update `RightPanel.tsx`** -- pass `origin` from `SelectedSkill` through to `WorkspaceProvider`:
   - `WorkspaceProvider` receives new `origin` prop
   - Derives `isReadOnly = origin === "installed"` and exposes it on context value

10. **Update `WorkspaceProvider` and `workspaceTypes.ts`**:
    - Add `origin: "source" | "installed"` to `WorkspaceState`
    - Add `isReadOnly: boolean` derived field to context value
    - Guard `saveContent`, `saveEvals`, `runCase`, `runAll`, `submitAiEdit`, `generateEvals` behind `!isReadOnly`

11. **Update `DetailHeader.tsx`** -- show "Read-only" badge for installed skills:
    - Pill with lock icon and "Read-only" text, styled with surface-3 background

12. **Update `EditorPanel.tsx`** -- disable editing:
    - Textarea gets `readOnly` prop when installed
    - AI Edit button hidden
    - Save button hidden
    - View mode forced to "preview" (read-only users see rendered markdown)

13. **Update `RunPanel.tsx`** -- disable benchmarking:
    - "Run All" and per-case "Run" buttons disabled with tooltip "Cannot benchmark installed skills"
    - Mode selector disabled

14. **Update `TestsPanel.tsx`** -- disable eval editing:
    - "Add eval" button hidden
    - Edit/delete controls on individual evals hidden
    - Content still visible in read-only mode

## Testing Strategy

### Unit Tests (Vitest)

**`classifyOrigin` function** (highest priority):
- Skill under `.claude/skills/foo` -> `"installed"`
- Skill under `.cursor/skills/bar` -> `"installed"`
- Skill under `.specweave/plugins/something` -> `"installed"`
- Skill under `.vscode/skills/baz` -> `"installed"`
- Skill under `some/path/plugins/cache/specweave/skills/foo` -> `"installed"` (contains check)
- Skill under `marketing/skills/smp` -> `"source"`
- Skill under `plugins/marketing/skills/smp` -> `"source"` (standard nested layout)
- Skill under `skills/my-skill` -> `"source"` (root layout)
- Both source and installed copies of the same skill name appear with correct origins

**`scanSkills` integration** (extends existing test file):
- Scanner returns `origin` field on every skill
- Mixed layouts with agent dirs produce correct origin values

**Frontend component tests** (if time permits -- not blocking):
- `SkillGroupList` renders two sections when mixed origins
- `SkillGroupList` renders single section when all source or all installed
- `SkillCard` renders lock icon for installed, no icon for source

### Manual Verification

- Run `npx vskill studio` in a project with both source and installed skills
- Verify sidebar shows two sections with correct skills in each
- Verify installed skill opens in read-only mode
- Verify run buttons are disabled for installed skills
- Verify banner appears and can be dismissed

## Technical Challenges

### Challenge 1: Relative Path Computation Across Scanner Layouts

The scanner supports 5 layouts, and in Layout 4 (self-layout), `root` IS the skill directory itself. When `root === skillDir`, `path.relative(root, dir)` returns `""` -- which matches no prefix and correctly classifies as `"source"`. But we must ensure this edge case is tested.

**Solution**: The `classifyOrigin` function handles the empty-string relative path case explicitly. For Layout 4, the skill is the root itself, so it is always source.

**Risk**: Low. The relative path logic is straightforward and well-tested.

### Challenge 2: Agent Registry Prefix Overlap

Multiple agents may share the same top-level directory (e.g., `.github/copilot/skills` and `.github/` hardcoded prefix). Using a `Set<string>` for prefixes naturally deduplicates.

Some agent `localSkillsDir` values have deeper nesting (e.g., `.github/copilot/skills`) where extracting just `.github/` is intentionally broad -- we want ALL paths under `.github/` classified as installed, not just `.github/copilot/`.

**Solution**: Extract first segment only (`path.split('/')[0] + '/'`). This is the documented design decision in spec.md.

**Risk**: None. The spec explicitly calls for this behavior.

### Challenge 3: `WorkspaceProvider` Prop Threading

`WorkspaceProvider` currently takes `plugin` and `skill` props. Adding `origin` requires updating `RightPanel.tsx` to pass it, and the `SelectedSkill` type to carry it. The `selectSkill` action must include `origin` from the `SkillInfo` at selection time.

**Solution**: Extend `SelectedSkill` to include `origin`, update `selectSkill` call sites to pass it from the `SkillInfo` object.

**Risk**: Low. Straightforward prop threading with TypeScript catching any missed sites at compile time.
