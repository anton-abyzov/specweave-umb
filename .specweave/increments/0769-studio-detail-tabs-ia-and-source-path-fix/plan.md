# Implementation Plan: 0769 — Studio detail tabs IA + plugin-cache source-path fix + hide CheckNow

## Overview

This is a bundled bug-fix increment with three parts that share UI surface but
have independent root causes. We sequence them as **A → C → B** so the
foundational data-shape change (Part A) is in place before the IA reorg (Part
B) starts touching the same files; Part C is a one-line gate that rides on top
of Part A's `installMethod` classification.

```
┌─────────────────────────────────────────────────────────────┐
│ Part A: Plugin-scanner correctness                          │
│   - SkillInfo gains sourcePath (true marketplace clone)     │
│   - installMethod becomes lstat-based (fixes "symlinked     │
│     (target unresolved)")                                   │
│   - File-tree route resolves from sourcePath, not cache     │
│   - DetailHeader path chip + InstallMethodRow read truth    │
└──────────────────────┬──────────────────────────────────────┘
                       │ (foundation lands first)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Part C: Hide CheckNowButton on plugin-cache scope           │
│   - One-line gate in RightPanel.tsx                         │
│   - Depends on scopeV2/installMethod from Part A            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ Part B: Persona-conditional tab IA                          │
│   - Tab descriptors with visibleWhen() predicates           │
│   - SubTabBar pattern for Run/Trigger/Versions sub-modes    │
│   - History+Leaderboard absorbed into Run                   │
│   - Activation history → sub-tab of Trigger (renamed)       │
│   - Deps tab → SkillOverview right-rail                     │
│   - Dead code: TabBar.tsx, SkillWorkspace.tsx               │
└─────────────────────────────────────────────────────────────┘
```

## Part A — Plugin-scanner source path & install method (Bugs 1 + 3)

### Root cause

`src/eval/plugin-scanner.ts:78-101` records the per-version **cache** snapshot
as `SkillInfo.dir` and hardcodes `installMethod: "symlinked"` regardless of
what `lstat()` would say. The marketplace clone — the **true** source — at
`~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` is
never recorded anywhere in the SkillInfo. Three downstream consumers break:

1. **DetailHeader path chip** (`DetailHeader.tsx:228-252`) — shows the cache
   `~/.claude/plugins/cache/.../<sha>/skills/<skill>` instead of the
   marketplace clone the user actually authored / can `git status`.
2. **InstallMethodRow** (`DetailHeader.tsx:290-308`) — renders "Symlinked
   (target unresolved)" because the cache directory is **not** a symlink:
   `lstat()` returns false, but the field was still hardcoded `"symlinked"`,
   so the helper falls through to the "unresolved" branch.
3. **Editor "No files found"** — `skill-resolver.ts:15-40` only searches under
   the eval-server `root` (the studio's own repo). The cache lives at
   `~/.claude/plugins/cache/...`, **outside** that root. `assertContained()`
   then forces a 404 from `/api/skills/:plugin/:skill/files`
   (`api-routes.ts:2179-2228`). The 404 is silently swallowed by
   `useSkillFiles.ts:27-30` (`catch { setFiles([]) }`), so the file browser
   shows "No files found" with no error.

### Architectural decisions

#### A.1 — `SkillInfo.sourcePath` field

Add an optional field to `SkillInfo` in
`src/eval/skill-scanner.ts` (the producer SSoT) and mirror it in
`src/eval-ui/src/types.ts:248` (the consumer). Semantics:

| Producer                       | `dir` (current)                                | `sourcePath` (new)                           |
|--------------------------------|------------------------------------------------|----------------------------------------------|
| `scanInstalledPluginSkills`    | `~/.claude/plugins/cache/<mp>/<plugin>/<v>/skills/<skill>` | `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>` (or `null` if not present) |
| `scanAuthoredPluginSkills`     | project-local skill dir                        | same as `dir` (or `null` for parity)         |
| `scanSkillsTriScope` own       | project skill dir                              | `null` (own = `dir` IS source)               |
| `scanSkillsTriScope` installed | project-local installed copy                   | `null` (no separate "marketplace" concept)   |
| `scanSkillsTriScope` global    | `~/.claude/skills/<skill>`                     | `null`                                       |

**Rule**: `sourcePath` is set to the marketplace clone path when it exists and
is a dir; otherwise `null`. Consumers that need a "best path to show the user"
do `sourcePath ?? dir`. The existing `dir` field is preserved unchanged so
benchmark/run paths that load `SKILL.md` from the **resolved cache** (which is
what Claude Code actually executes) keep working.

This is documented in **ADR 0769-01** (see below).

#### A.2 — `installMethod` enum: keep two-value, lstat-based

Recommendation: **keep the existing two-value classification**
(`symlinked | copied`) for installed/global; do **not** introduce a third
`"cached"` value. Reasoning:

- `installed` skills can already be either symlinked (link to a plugin clone)
  or copied (file-tree copy). Adding `"cached"` for plugin-cache rows would
  conflate the source-of-truth question with the install-shape question.
- The plugin-cache snapshot at
  `~/.claude/plugins/cache/.../<sha>/skills/<skill>` is **not** a symlink; the
  marketplace clone is the symlink target users care about. Calling it
  "symlinked" was a producer-side bug, not a UI taxonomy gap.

So we delete the line `installMethod: "symlinked"` at
`plugin-scanner.ts:94` and replace with
`installMethodFor(skillDir, "global", undefined)` from
`skill-scanner.ts:543-551` (or an equivalent inline `lstatSafeIsSymlink`
call). Result for plugin-cache rows: `"copied"` (the cache snapshot is a
real directory of files, not a link), which is correct.

#### A.3 — File-tree resolver path-prefix safety

The resolver currently restricts to a single `root` to prevent path traversal.
We need to resolve plugin skills from `sourcePath` (under
`~/.claude/plugins/marketplaces/`) AND keep the `dir` cache fallback (under
`~/.claude/plugins/cache/`). Both are **outside** the eval-server root.

**Decision**: server-side allowlist of safe roots, lookup-by-key (no
client-supplied path).

```
allowedRoots = [
  resolve(eval-server-root),
  resolve(homedir(), ".claude", "plugins", "marketplaces"),
  resolve(homedir(), ".claude", "plugins", "cache"),
  resolve(homedir(), ".claude", "skills"),
]
```

The `/api/skills/:plugin/:skill/files` route receives only `:plugin` and
`:skill` from URL params. It looks the dir up from a server-side
`SkillDirRegistry` populated by `scanInstalledPluginSkills` and
`scanAuthoredPluginSkills` (already-scanned in-memory). The route never
accepts a `?dir=` query — that would re-introduce traversal. Resolution
order:

1. If a server-cached SkillInfo for `(plugin, skill)` is present, use
   `sourcePath ?? dir`.
2. Else fall back to existing `resolveSkillDir(root, plugin, skill)`.
3. Validate result against `allowedRoots` (must `startsWith()` one of them
   after `resolve()` and reject any input containing `..`).
4. If `lstat(resolved).isSymbolicLink() === true`, also `resolve()` the
   realpath and re-validate against `allowedRoots`.

**No signed URLs**, **no client-supplied paths** — the (plugin, skill) pair
is the cache key.

#### A.4 — `useSkillFiles` error surface

Currently the hook silently swallows fetch errors and shows "No files found".
Change to surface a `loadError: string | null` field that
`SkillFileBrowser` renders as an inline banner ("Couldn't load file tree:
EACCES /Users/.../skill-creator"). The fix-loop is then visible to users
when our own resolver is broken, and we don't have to debug from scratch.

```ts
export interface UseSkillFilesResult {
  files: SkillFileEntry[];
  // ... existing
  loadError: string | null;  // NEW — distinct from per-file `error`
}
```

The existing `error` field stays for "couldn't open this specific file"; the
new `loadError` is only for the list-fetch failure.

### Component dependency map (Part A)

| File                                                | Change              |
|-----------------------------------------------------|---------------------|
| `src/eval/skill-scanner.ts`                         | Add `sourcePath?: string \| null` to `SkillInfo` |
| `src/eval/plugin-scanner.ts:82-101`                 | Compute marketplace clone path, set `sourcePath`; replace hardcoded `installMethod: "symlinked"` with lstat-based call |
| `src/eval/plugin-scanner.ts:145-165`                | Set `sourcePath = skillDir` (or `null`) for authored-plugin scope (parity) |
| `src/eval-server/skill-resolver.ts`                 | New `resolveAllowedSkillDir(plugin, skill, registry, allowedRoots)` |
| `src/eval-server/api-routes.ts:1740-1760`           | Wire `sourcePath` through to `/api/skills` response payload |
| `src/eval-server/api-routes.ts:2169-2228`           | File-tree + file-read routes use registry lookup + allowlist |
| `src/eval-server/api-routes.ts` (new module)        | `SkillDirRegistry` populated at scan time |
| `src/eval-ui/src/types.ts:248-264`                  | Add `sourcePath?: string \| null` to `SkillInfo` |
| `src/eval-ui/src/api.ts:177-235`                    | Pass-through `sourcePath` in normalizer; remove `installMethod = "copied"` default fallback when server provides truth |
| `src/eval-ui/src/components/DetailHeader.tsx:228-252` | Path chip displays `skill.sourcePath ?? skill.dir` |
| `src/eval-ui/src/components/DetailHeader.tsx:290-308` | InstallMethodRow uses real lstat-derived `installMethod` value |
| `src/eval-ui/src/pages/workspace/useSkillFiles.ts:23-31` | Surface `loadError` instead of swallowing |
| `src/eval-ui/src/components/SkillFileBrowser.tsx`   | Render banner when `loadError` is non-null |

### Data flow (Part A)

```
plugin-scanner.scanInstalledPluginSkills()
   │  walks ~/.claude/plugins/cache/<mp>/<plugin>/<v>/skills/<skill>
   │  (existing) — produces dir = cache snapshot
   │  (NEW) — also computes sourcePath = ~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>
   │  (NEW) — installMethod = lstat-based via installMethodFor()
   ▼
SkillInfo[] persisted in SkillDirRegistry (in-memory)
   │
   ├──► api-routes.ts /api/skills (1740-1760) → wire field through
   │       ▼
   │     api.ts normalizer (177-235) → SkillInfo on the wire
   │       ▼
   │     DetailHeader path chip — shows sourcePath
   │     InstallMethodRow — shows "Symlinked from <target>" / "Copied (independent)"
   │
   └──► api-routes.ts /api/skills/:plugin/:skill/files (2179)
           │  registry.lookup(plugin, skill) → sourcePath ?? dir
           │  validate against allowedRoots
           ▼
         SkillFileEntry[] streamed back, useSkillFiles.fetchFileList() succeeds
```

### Type changes (Part A)

```ts
// src/eval/skill-scanner.ts
export interface SkillInfo {
  // ... existing fields
  /**
   * Absolute path to the canonical SOURCE of this skill, when distinct from
   * the runtime location in `dir`. For marketplace-installed plugin skills,
   * this is the marketplace clone path; the runtime cache path lives in
   * `dir`. `null` when source === dir or unknown.
   */
  sourcePath?: string | null;
}

// src/eval-ui/src/pages/workspace/useSkillFiles.ts
export interface UseSkillFilesResult {
  files: SkillFileEntry[];
  activeFile: string;
  secondaryContent: SkillFileContent | null;
  loading: boolean;
  error: string | null;        // per-file open error (existing)
  loadError: string | null;    // NEW — file-list fetch error
  selectFile: (path: string) => void;
  refresh: () => void;
  isSkillMd: boolean;
}
```

### TDD strategy (Part A)

- `src/eval/__tests__/plugin-scanner.sourcepath.test.ts` (new, RED)
  - Scaffolds a fake `~/.claude/plugins/{cache,marketplaces}` tree
  - Asserts `sourcePath` resolves to the marketplace path when it exists
  - Asserts `sourcePath === null` when only the cache exists
  - Asserts `installMethod === "copied"` when the cache snapshot is a plain dir
  - Asserts `installMethod === "symlinked"` when the cache itself is a symlink
- `src/eval-server/__tests__/skill-resolver.allowlist.test.ts` (new, RED)
  - Resolver with mocked registry returns marketplace path for installed
    plugin-cache rows
  - Path traversal (`../../etc/passwd`) is rejected
  - Symlink whose realpath escapes allowlist is rejected
- `src/eval-server/__tests__/api-routes.files-route.test.ts` (extend, RED)
  - File-tree route returns 200 + non-empty list for plugin-cache skills
- `src/eval-ui/src/pages/workspace/__tests__/useSkillFiles.test.ts` (new, RED)
  - When `api.getSkillFiles` rejects, hook exposes `loadError`, not silent
- `src/eval-ui/src/components/__tests__/DetailHeader.path-chip.test.tsx` (new)
  - Path chip prefers `sourcePath` over `dir`
- `src/eval-ui/src/components/__tests__/DetailHeader.installMethod.test.tsx` (extend)
  - Plugin-cache row renders "Copied (independent)" not
    "Symlinked (target unresolved)"

## Part B — Persona-conditional tab IA reorganization

### Current state

`RightPanel.tsx:43-67` exposes 9 flat tabs:

```
Overview | Editor | Tests | Run | Activation | History | Leaderboard | Deps | Versions
```

`WorkspaceContext.tsx:69-74` derives `isReadOnly = origin === "installed"`,
which is the persona signal we use. Plugin-cache skills (Part A) and
agent-global skills are also read-only consumers. Authoring-plugin and
authoring-project are the author personas.

### Target IA

**Author persona** (origin `"source"`, scopeV2 starts with `"authoring-"`)
sees 6 tabs:

```
Overview | Editor | Tests | Trigger | Run | Versions
```

**Consumer persona** (origin `"installed"`, scopeV2 starts with
`"available-"`) sees 3 tabs:

```
Overview | Trigger | Run
```

Sub-tabs (URL: `?tab=run&sub=history`):

| Top tab     | Sub tabs                                          |
|-------------|---------------------------------------------------|
| Trigger     | (Test) → `ActivationPanel`. Author persona also gets a `History` sub-tab pulled from the in-panel activation-history list. |
| Run         | `Latest` → `RunPanel`; `History` → `HistoryPanel`; `Leaderboard` → `LeaderboardPanel` (author-only, since consumer can't run) |
| Versions    | unchanged                                         |

**Overview** picks up Deps + Credentials in a right-rail (decision below).

**Activation rename**: label-only. **Internal symbols
(`ACTIVATION_RUN`, `runActivationTest`, `activation-history.json`,
`PanelId === "activation"`) all stay.** Only the `TAB_LABELS` map and a
new "Trigger" string in `SkillOverview`'s navigation copy change.

### Architectural decisions

#### B.1 — Tab descriptor with `visibleWhen()`

```ts
// src/eval-ui/src/components/RightPanel.tabs.ts (new)
import type { SkillInfo } from "../types";

export interface TabDescriptor {
  id: DetailTab;
  label: string;
  /** Inferred from skill state — origin, scopeV2, isReadOnly. */
  visibleWhen: (ctx: { skill: SkillInfo }) => boolean;
  /** Optional sub-tabs. */
  subTabs?: SubTabDescriptor[];
}

export const TAB_DESCRIPTORS: TabDescriptor[] = [
  { id: "overview", label: "Overview",   visibleWhen: () => true },
  { id: "editor",   label: "Editor",     visibleWhen: ({ skill }) => skill.origin === "source" },
  { id: "tests",    label: "Tests",      visibleWhen: ({ skill }) => skill.origin === "source" },
  { id: "trigger",  label: "Trigger",    visibleWhen: () => true,
    subTabs: [
      { id: "test",    label: "Test",    visibleWhen: () => true },
      { id: "history", label: "History", visibleWhen: ({ skill }) => skill.origin === "source" },
    ] },
  { id: "run",      label: "Run",        visibleWhen: () => true,
    subTabs: [
      { id: "latest",      label: "Latest",      visibleWhen: () => true },
      { id: "history",     label: "History",     visibleWhen: () => true },
      { id: "leaderboard", label: "Leaderboard", visibleWhen: ({ skill }) => skill.origin === "source" },
    ] },
  { id: "versions", label: "Versions",   visibleWhen: () => true },
];
```

`renderTabBar()` calls `TAB_DESCRIPTORS.filter(d => d.visibleWhen({ skill }))`
once per render. No memoization needed — predicate is O(1) and React's
diff handles the DOM minimization.

#### B.2 — `SubTabBar` component + URL encoding

```ts
// src/eval-ui/src/components/SubTabBar.tsx (new)
function SubTabBar({ subTabs, active, onChange }: ...): JSX.Element
```

URL encoding: `?tab=run&sub=history`. Reading: existing `readInitialTab()` in
`RightPanel.tsx:73-79` is extended to also read `sub`. Writing: extend the
sync effect at `RightPanel.tsx:213-225` to write both keys. When the active
top tab changes, we drop the `sub` param (sub-tab selection is per-top-tab).

Each panel inside a top tab is responsible for picking up
`?sub=` from a small `useSubTab()` hook that reads/writes the URL — this
keeps each panel composable and avoids a god-context.

#### B.3 — Reuse strategy (NO rewrites)

All four affected panels stay as-is and become sub-mode children:

| Existing panel                                  | New host             | Sub-tab id     |
|-------------------------------------------------|----------------------|----------------|
| `pages/workspace/RunPanel.tsx`                  | Run                  | `latest`       |
| `pages/workspace/HistoryPanel.tsx`              | Run                  | `history`      |
| `pages/workspace/LeaderboardPanel.tsx`          | Run (author only)    | `leaderboard`  |
| `pages/workspace/ActivationPanel.tsx`           | Trigger              | `test`         |
| `pages/workspace/ActivationPanel.tsx` (history list extracted) | Trigger (author only) | `history` |

For the Activation history sub-tab specifically: `ActivationPanel.tsx`
already holds the in-panel history (state.activationHistory in the reducer).
We extract its list-rendering JSX into a small `ActivationHistoryList`
component (no logic change) and mount it under the Trigger > History sub-tab
when `origin === "source"`. The existing in-panel history block stays where
it is for direct visual continuity inside the Test sub-tab too — we don't
fight a duplicate render because authors choose which to look at.

#### B.4 — Deps tab elimination → SkillOverview right-rail

**Decision**: split the right rail into **two** sections, "Setup" and "Credentials":

- **Setup** — MCP deps + skill deps (the existing `DepsPanel.tsx` sub-tree
  minus credentials)
- **Credentials** — moved out of `DepsPanel.tsx` (which currently embeds
  `CredentialManager.tsx` for installed skills)

We keep them separate because Setup is read-only-friendly (consumers see what
the skill needs) while Credentials are write-action heavy
(consumer-mutable). Mixing them in one collapsible was the source of the
"too dense" feedback.

`SkillOverview.tsx` gains an optional right rail. On mobile / narrow
viewports the rail collapses into stacked sections under the metric grid
(no separate layout — same components, CSS grid `auto-fit` handles it).

#### B.5 — "Activation" → "Trigger" rename (label-only)

| Surface                                         | Change?              |
|-------------------------------------------------|----------------------|
| `TAB_LABELS["activation"]`                      | "Activation" → "Trigger" |
| `SkillOverview.tsx:213` MetricCard "Activations"| keep label "Activations" — refers to the *count*, not the tab |
| `data-testid="metric-activations"`              | unchanged            |
| `runActivationTest()`, `ACTIVATION_RUN`, reducer actions | unchanged |
| `activation-history.json` storage               | unchanged            |
| URL param `?panel=activation`                   | accept BOTH `activation` and `trigger`; canonicalize on write to `trigger` |
| `data-testid="detail-tab-activation"`           | rename to `"detail-tab-trigger"` AND keep the old testid as an alias for one release (most tests already touched in this increment) |

Document the alias in plan.md AND add a deprecation log line.

#### B.6 — Deep-link redirect on persona-flip

If a user lands on `?tab=editor` for an installed skill (e.g., shared a link,
then someone uninstalled the source and reinstalled as plugin-cache), the
predicate excludes Editor. Behavior:

1. Compute the visible tab list with `visibleWhen()`.
2. If `active` (read from URL) is **not** in the visible list, redirect to
   `overview` and dispatch a one-time toast: "This skill is read-only —
   workbench tabs are hidden."
3. URL is rewritten via `history.replaceState` so the back button doesn't
   bounce.

Implementation: extend the existing tab-sync effect at
`RightPanel.tsx:213-225`.

#### B.7 — Dead code removal

After the IA reorg lands, both `TabBar.tsx` and `SkillWorkspace.tsx` are
unused. Verification sequence:

1. `tsc --noEmit` passes (zero unresolved imports).
2. `grep -rn "from.*TabBar\|from.*SkillWorkspace" src/eval-ui/src` returns
   only test files mocking them.
3. Update those test mocks to mock the new tab-descriptor module.
4. Delete the two files in a separate commit so the diff is auditable.

**Risk**: tests currently `vi.mock("../../pages/workspace/SkillWorkspace")`.
We update them to mock the new structure or remove the mocks (now that
RightPanel's tab body isn't a single mega-component, mocks may no longer be
needed).

### Component dependency map (Part B)

| File                                                              | Change             |
|-------------------------------------------------------------------|--------------------|
| `src/eval-ui/src/components/RightPanel.tsx`                       | Replace `ALL_TABS` const with `TAB_DESCRIPTORS` filter; add sub-tab read/write |
| `src/eval-ui/src/components/RightPanel.tabs.ts` (NEW)             | Tab descriptor + `visibleWhen` predicates |
| `src/eval-ui/src/components/SubTabBar.tsx` (NEW)                  | Reusable sub-tab strip |
| `src/eval-ui/src/components/SkillOverview.tsx`                    | Add optional right-rail with Setup + Credentials sections |
| `src/eval-ui/src/components/SkillOverview.RightRail.tsx` (NEW)    | Setup + Credentials wrapper (composes existing DepsPanel sub-components) |
| `src/eval-ui/src/pages/workspace/RunPanel.tsx`                    | Add `useSubTab()` to switch latest/history/leaderboard children |
| `src/eval-ui/src/pages/workspace/ActivationPanel.tsx`             | Extract `ActivationHistoryList`; add `useSubTab()` |
| `src/eval-ui/src/pages/workspace/ActivationHistoryList.tsx` (NEW) | Pure list component for the Trigger>History sub-tab |
| `src/eval-ui/src/pages/workspace/DepsPanel.tsx`                   | DELETE (contents moved to SkillOverview right-rail components) |
| `src/eval-ui/src/components/TabBar.tsx`                           | DELETE (unused) |
| `src/eval-ui/src/pages/workspace/SkillWorkspace.tsx`              | DELETE (unused) |
| Existing tests under `__tests__/`                                 | Update — mocks of SkillWorkspace removed; new tests for visibility predicates |

### TDD strategy (Part B)

- `src/eval-ui/src/components/__tests__/RightPanel.persona-tabs.test.tsx` (NEW, RED)
  - Author skill renders 6 tabs in expected order
  - Consumer skill renders 3 tabs; Editor/Tests/Versions absent
- `src/eval-ui/src/components/__tests__/RightPanel.subtabs.test.tsx` (NEW, RED)
  - `?tab=run&sub=history` mounts HistoryPanel
  - Switching sub-tab updates URL
  - Switching top tab clears `?sub=`
- `src/eval-ui/src/components/__tests__/RightPanel.persona-flip.test.tsx` (NEW)
  - URL `?tab=editor` for installed skill redirects to Overview, shows toast
- `src/eval-ui/src/components/__tests__/SkillOverview.right-rail.test.tsx` (NEW)
  - Setup section lists MCP + skill deps
  - Credentials section renders for installed skills with required envs
- `src/eval-ui/src/pages/workspace/__tests__/ActivationHistoryList.test.tsx` (NEW)
  - Renders empty state, then a list of past runs

## Part C — Hide CheckNowButton for plugin-cache installs

`RightPanel.tsx:497-505` unconditionally renders `<CheckNowButton>` for any
`origin === "installed"` skill, even when the skill is a plugin-cache snapshot
(which has no upstream-tracking story — Part A's
`scopeV2 === "available-plugin"` rows). The button then 404s on click because
there's no `sourceRepoUrl` in the platform.

**Decision** (single-line gate, post-Part A):

```tsx
{skill.origin === "installed"
  && skill.scopeV2 !== "available-plugin"
  && skill.trackedForUpdates && (
    <div ...>
      <CheckNowButton ... />
    </div>
)}
```

`trackedForUpdates` is already in `types.ts:263`. The new clause excludes
plugin-cache rows. Documented but no architectural decision needed.

### Component dependency map (Part C)

| File                                              | Change         |
|---------------------------------------------------|----------------|
| `src/eval-ui/src/components/RightPanel.tsx:497`   | Add `scopeV2 !== "available-plugin"` to gate |

### TDD (Part C)

- `src/eval-ui/src/components/__tests__/RightPanel.checkNow.gate.test.tsx`
  - Plugin-cache skill: button absent
  - Authored installed skill: button present
  - Tracked-for-updates false: button absent (existing test, keep)

## File ownership map

| Domain          | Files (Part)                                                    |
|-----------------|------------------------------------------------------------------|
| Server/scanners | `src/eval/plugin-scanner.ts` (A), `src/eval/skill-scanner.ts` (A) |
| Server/routes   | `src/eval-server/skill-resolver.ts` (A), `src/eval-server/api-routes.ts` (A) |
| UI/types        | `src/eval-ui/src/types.ts` (A), `src/eval-ui/src/api.ts` (A) |
| UI/detail page  | `src/eval-ui/src/components/RightPanel.tsx` (A,B,C), `RightPanel.tabs.ts` (B), `SubTabBar.tsx` (B) |
| UI/header       | `src/eval-ui/src/components/DetailHeader.tsx` (A) |
| UI/overview     | `src/eval-ui/src/components/SkillOverview.tsx` (B), `SkillOverview.RightRail.tsx` (B) |
| UI/panels       | `src/eval-ui/src/pages/workspace/RunPanel.tsx` (B), `ActivationPanel.tsx` (B), `useSkillFiles.ts` (A) |
| UI/dead         | `TabBar.tsx`, `SkillWorkspace.tsx`, `DepsPanel.tsx` (deleted) |

## Migration ordering

1. **A.1 + A.2** — Add `sourcePath` field, fix scanner. RED→GREEN scanner
   tests. No UI change yet.
2. **A.3** — Server `SkillDirRegistry` + allowlist resolver + file-tree
   route fix. RED→GREEN integration tests for file-tree route.
3. **A.4** — `useSkillFiles` `loadError` surface; UI consumers (DetailHeader
   path chip, InstallMethodRow). Manual smoke: open plugin-cache skill,
   verify path chip shows marketplace clone, install method shows "Copied",
   editor file tree populates.
4. **C** — Single-line gate. Test, ship.
5. **B.1 + B.2** — Tab descriptor + sub-tab URL plumbing. Behind a feature
   flag if we want to dark-launch (not strictly necessary — IA change is
   intentional).
6. **B.3 + B.4** — Wire panels as sub-tabs; SkillOverview right-rail.
7. **B.5** — Activation → Trigger rename + alias.
8. **B.6** — Persona-flip redirect.
9. **B.7** — Dead code removal (last; verify with tsc + grep).

## Risk register

| Risk                                                 | Mitigation                                                  |
|------------------------------------------------------|-------------------------------------------------------------|
| Path traversal via `sourcePath`                      | `allowedRoots` allowlist; reject `..`; resolve symlinks and re-validate |
| Stale registry after plugin install                  | `SkillDirRegistry` is rebuilt on every scan tick (existing `scanSkillsTriScope` cadence applies) |
| Deep-link rot after IA change                        | Both `?panel=activation` and `?panel=trigger` accepted for one release |
| Persona flip on uninstall+reinstall                  | Visible-tab check redirects to Overview with toast (B.6) |
| Tests mocking SkillWorkspace                         | Update mocks in same commit as IA change; tsc --noEmit gate |
| `installMethod === "symlinked"` false-negative on case-insensitive macOS FS | `lstatSafeIsSymlink` is already case-correct; no new exposure |
| `useSkillFiles.loadError` masking real load failures | Distinct from per-file `error`; banner copy includes the underlying error message |
| CheckNow gate skipping legitimate authored-installed | `trackedForUpdates` field already gates that case; we only ADD the plugin-cache exclusion |

## Reference list (line numbers)

- `src/eval/plugin-scanner.ts:45-107` — `scanInstalledPluginSkills` (Part A target)
- `src/eval/plugin-scanner.ts:120-169` — `scanAuthoredPluginSkills` (Part A parity)
- `src/eval/skill-scanner.ts:44` — `SkillInstallMethod` type
- `src/eval/skill-scanner.ts:46-82` — `SkillInfo` interface (extend with `sourcePath`)
- `src/eval/skill-scanner.ts:543-559` — `installMethodFor` + `lstatSafeIsSymlink`
- `src/eval-server/skill-resolver.ts:8-40` — `assertContained` + `resolveSkillDir` (Part A.3)
- `src/eval-server/api-routes.ts:1740-1760` — `/api/skills` enrichment (wire `sourcePath`)
- `src/eval-server/api-routes.ts:2179-2228` — `/api/skills/:plugin/:skill/files` route (Part A.3)
- `src/eval-server/api-routes.ts:2230-2265` — `/api/skills/:plugin/:skill/file` (Part A.3 sibling)
- `src/eval-ui/src/types.ts:201-264` — `SkillInfo` consumer shape
- `src/eval-ui/src/api.ts:163-235` — `normalizeSkillInfo`
- `src/eval-ui/src/components/RightPanel.tsx:43-67` — flat 9-tab definition (Part B target)
- `src/eval-ui/src/components/RightPanel.tsx:381-408` — `WorkspacePanel` + `WorkspaceTabSync` (Part B)
- `src/eval-ui/src/components/RightPanel.tsx:497-505` — `CheckNowButton` mount (Part C)
- `src/eval-ui/src/components/DetailHeader.tsx:223-278` — path chip + copy (Part A)
- `src/eval-ui/src/components/DetailHeader.tsx:283-330` — `InstallMethodRow` (Part A)
- `src/eval-ui/src/components/SkillOverview.tsx:84-107` — `installMethodChip` (label only)
- `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx:69-74` — persona signal (`isReadOnly`)
- `src/eval-ui/src/pages/workspace/useSkillFiles.ts:23-31` — silent error swallow (Part A.4)
- `src/eval-ui/src/pages/workspace/HistoryPanel.tsx`, `LeaderboardPanel.tsx`, `ActivationPanel.tsx`, `DepsPanel.tsx` — reused as sub-mode children (Part B)
- `~/.claude/plugins/marketplaces/<mp>/plugins/<plugin>/skills/<skill>/` — confirmed layout
- `~/.claude/plugins/cache/<mp>/<plugin>/<sha>/skills/<skill>/` — confirmed layout

## ADRs

- **ADR 0769-01** — Plugin-scanner source path & install method
  (see `.specweave/docs/internal/architecture/adr/0769-01-plugin-scanner-source-path-and-install-method.md`)
