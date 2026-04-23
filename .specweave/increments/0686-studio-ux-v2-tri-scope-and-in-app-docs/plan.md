# 0686 — Plan

**Status:** planned • **Companion to:** [spec.md](./spec.md) • [tasks.md](./tasks.md)

## 1. Component Architecture

```
eval-ui (React / Vite)
├── App.tsx
│   ├── TopRail
│   │   ├── BrandLogo          ← NEW (US-001): <a href="#/">Skill Studio</a>
│   │   └── AgentModelPicker   ← EXTEND (US-006): Claude Code row label + banner
│   ├── StudioShell
│   │   ├── LeftPane
│   │   │   ├── AgentScopePicker    ← NEW (US-002): sticky 40px row, two-pane popover
│   │   │   ├── SidebarSearch       ← unchanged
│   │   │   └── Sidebar             ← EXTEND (US-003,4): tri-scope sections, new dividers
│   │   │       ├── SidebarSection  ← EXTEND: add "global" origin + bolder styling
│   │   │       └── SkillRow        ← EXTEND (US-008): symlink chain-link glyph
│   │   ├── RightPanel              ← EXTEND (US-008): add "Install method" row
│   │   └── SetupDrawer             ← NEW (US-005): 480px right-slide, provider registry
│   │       └── SetupProviderView/<provider>.tsx (7 views on ship)
│   └── hooks/
│       ├── useAgentCatalog          ← EXTEND: expose agentScopes from /api/agents/scopes
│       ├── useScopedSkills          ← NEW: subscribes to /api/skills + current active agent
│       └── useSetupDrawer           ← NEW: open(provider) / close / stacking contract

eval-server (Node/Express-ish)
├── api-routes.ts
│   ├── GET /api/skills              ← EXTEND: returns SkillInfo[] with scope + symlink fields
│   └── GET /api/agents/scopes       ← NEW: per-agent installed+global counts, last-sync, health
├── skill-scanner.ts (src/eval/)     ← EXTEND: scanGlobalSkills(agent), symlink detection
└── utils/paths.ts                   ← NEW: expandHome, resolveAgentGlobalDir, cross-platform
```

### Data model deltas

```ts
// src/eval/skill-scanner.ts (extended)
export type SkillScope = "own" | "installed" | "global";

export interface SkillInfo {
  plugin: string;
  skill: string;
  dir: string;                       // fully-resolved absolute path, no '~'
  hasEvals: boolean;
  hasBenchmark: boolean;
  origin: "source" | "installed";    // KEPT for 0683 compat
  scope: SkillScope;                 // NEW (US-003)
  isSymlink: boolean;                // NEW (US-008)
  symlinkTarget: string | null;      // NEW (US-008), absolute realpath or null
  installMethod: "symlinked" | "copied" | "authored";  // NEW (US-008)
  sourceAgent?: string | null;       // agent-id whose scope this skill belongs to (null for OWN)
}
```

```ts
// src/agents/agents-registry.ts (extended)
export interface AgentDefinition {
  /* existing fields ... */
  /** Win32 override for POSIX-only globalSkillsDir entries. When absent, a
   *  deterministic fallback maps '~/.config/X/' to '%APPDATA%/X/'. */
  win32PathOverride?: string;
}
```

```ts
// New endpoint response
export interface AgentScopeStats {
  agentId: string;
  displayName: string;
  installedCount: number;      // skills in <cwd>/<localSkillsDir>
  globalCount: number;         // skills in <expandHome(globalSkillsDir)>
  lastSync: string | null;     // ISO timestamp from sync.ts lockfile
  health: "ok" | "stale" | "missing";
  resolvedLocalDir: string;    // absolute, platform-native
  resolvedGlobalDir: string;   // absolute, platform-native
  sharedFolderGroup?: string[];// consumer agent IDs when folder is shared
}

export interface AgentScopesResponse {
  agents: AgentScopeStats[];
  suggested: string;
  sharedFolders: { path: string; consumers: string[] }[];
}
```

## 2. Architecture Decision Records (ADRs)

### ADR-01 — Tri-scope sidebar: Own / Installed / Global (sections, not tabs)

**Status:** accepted • **Date:** 2026-04-22

**Context.** Today OWN/INSTALLED partitions the sidebar. Introducing GLOBAL (home-level skills for the active agent) raises the question: third section, tabs, filter dropdown, or collapsible "view mode"?

**Decision.** Three sibling `SidebarSection` instances (OWN → INSTALLED → GLOBAL). Not tabs. Not a view toggle.

**Rationale.**
- Scope is a "where does this live" question, not a "what am I doing" mode switch. Sections express coexistence; tabs express mutual exclusion.
- The user almost always wants to see all three simultaneously — authoring while referencing what's already installed.
- Virtual scroll + collapse already solve the length concern; total n is bounded by disk contents (≤ 200 typical).
- Keyboard nav (j/k) walks flat top→bottom — matches the visual order and is trivial to extend from the existing two-section flatten.

**Alternatives rejected.**
- Tabs: hides 2/3 of content, forces click to switch, breaks cross-section search.
- View-mode toggle ("all / only-mine / only-installed"): adds modal state, same hiding problem.
- Filter chips: weaker visual hierarchy, no per-scope counts without extra UI.

**Consequences.**
- `SidebarSection` gains a `"global"` origin variant with a new color token and label.
- Each section carries its own collapse key in localStorage.
- Divider treatment becomes meaningful (ADR-02 visual direction).

---

### ADR-02 — Agent-scope picker above the sidebar (composes with AgentModelPicker)

**Status:** accepted • **Date:** 2026-04-22

**Context.** 0682 introduced `AgentModelPicker` in the top rail — it chooses which AGENT+MODEL to use for LLM calls (benchmarks, evals). 0686 needs a control that chooses which AGENT's filesystem surface the sidebar shows. Could overload AgentModelPicker. Could build a third control.

**Decision.** Build a distinct `AgentScopePicker` component that reuses the `PopoverShell` + `AgentList` primitives from 0682 but with its own trigger (full-width sticky row above sidebar) and its own right pane (`AgentScopeStatsPane` — counts, last-sync, health, "Switch for this studio session" CTA).

**Rationale.**
- The two choices are orthogonal: you might run benchmarks with OpenRouter (AgentModelPicker) while browsing Cursor's installed skills (AgentScopePicker).
- Reusing `PopoverShell` + `AgentList` keeps the design language identical — same keyboard shortcuts, same popover geometry, same fade-in.
- A single control with tabs would coerce users into a concept they don't have.

**Alternatives rejected.**
- Extend `AgentModelPicker` with a "scope" tab: violates single-responsibility; two persisted selections in one popover confuses mental model.
- Put the scope picker in SettingsModal: hides the switch behind two clicks for a high-frequency operation.

**Consequences.**
- New `useAgentScope` hook backed by `studio.json` (same file as `saveStudioSelection` from 0682 — just a new key `activeScopeAgent`).
- Sticky positioning in the left pane; needs one scroll-container wrapping the search + sections.

---

### ADR-03 — In-app setup docs: slide-over drawer per provider (not a separate page)

**Status:** accepted • **Date:** 2026-04-22

**Context.** User needs inline setup guidance for 7 providers (anthropic-api, openai, openrouter, gemini, ollama, lm-studio, claude-code). Three shapes competed: (a) separate `/docs` page, (b) modal, (c) right-slide drawer.

**Decision.** Right-slide 480px drawer (`SetupDrawer`), opened from multiple entry points via a shared `useSetupDrawer(provider)` hook. Content is a registry lookup — each provider has its own view component in `components/SetupProviderView/<provider>.tsx`.

**Rationale.**
- Drawer preserves the user's context (sidebar + detail remain visible behind the 40% backdrop).
- Registry (not switch statement) keeps each provider's content a small, independently-testable module. Adding an 8th provider = one file + one registry entry.
- Not a page: the URL stays on the user's work; back button doesn't lose state.
- Not a modal stacked on SettingsModal: the increment enforces single-modal-at-a-time (AC-US5-07).

**Alternatives rejected.**
- Separate `/docs` page: breaks the studio-first principle; duplicates navigation.
- Inline expandable panel in the picker: cramped; setup code blocks need width.
- Modal stacked on SettingsModal: confuses focus trap + backdrop ownership.

**Consequences.**
- `useSetupDrawer` owns the single-modal contract: if `settingsOpen === true`, close Settings before opening drawer.
- Each `SetupProviderView` is a pure function of its provider config + an optional `onCopy` callback. No network.

---

### ADR-04 — Cross-platform path resolution (single utility, adapter for POSIX-only registry entries)

**Status:** accepted • **Date:** 2026-04-22

**Context.** Registry entries use POSIX semantics (`~/.config/agents/skills`). Windows `os.homedir()` returns `C:\Users\<name>` — naive `"~/.config/..."` string manipulation either drops the path separator or emits POSIX literals. Also, `.config/` is a Linux XDG convention with no native Windows analogue.

**Decision.** Single utility module `src/utils/paths.ts`:

```ts
export function expandHome(p: string): string {
  if (!p.startsWith("~")) return p;
  const rest = p.slice(1).replace(/^[/\\]/, "");
  // Split remaining segments using BOTH separators so registry POSIX entries
  // survive on win32 before being re-joined with path.sep.
  const parts = rest.split(/[/\\]+/);
  return path.join(os.homedir(), ...parts);
}

export function resolveAgentGlobalDir(agent: AgentDefinition): string {
  if (process.platform === "win32" && agent.win32PathOverride) {
    return expandHome(agent.win32PathOverride);
  }
  if (process.platform === "win32" && agent.globalSkillsDir.startsWith("~/.config/")) {
    // Deterministic fallback: map ~/.config/X → %APPDATA%/X
    const tail = agent.globalSkillsDir.slice("~/.config/".length);
    return path.join(os.homedir(), "AppData", "Roaming", ...tail.split("/"));
  }
  return expandHome(agent.globalSkillsDir);
}
```

**Rationale.**
- One function, one contract — every call site goes through `expandHome` or `resolveAgentGlobalDir`.
- Explicit `.config` fallback means no registry rewrite required; existing 49-agent table works as-is.
- The `win32PathOverride` field is the escape hatch for agents whose Windows location differs from the `.config` fallback.

**Alternatives rejected.**
- Rewriting each registry entry per-platform: 49 × 3 = 147 entries; drift risk.
- Leaving resolution to each caller: scatter of bugs, already seen in `skill-scanner.ts` split-by-`/`.

**Consequences.**
- All existing call sites that do `p.replace("~", homedir)` or similar get audited and replaced.
- Unit tests mock `os.platform()` + `os.homedir()` for all 3 OSes.
- API responses guaranteed tilde-free (AC-US7-04).

---

### ADR-05 — Symlink surfacing: SkillInfo.isSymlink + target + install method (scanner is SSoT)

**Status:** accepted • **Date:** 2026-04-22

**Context.** `vskill add` can install via symlink (from a plugin cache) or copy. Today the UI has no way to know which. A user editing a symlinked SKILL.md is silently editing the plugin cache — confusion.

**Decision.** Extend `SkillInfo` with `isSymlink`, `symlinkTarget`, `installMethod`. Set in `skill-scanner.ts` via `fs.lstatSync` + `fs.realpathSync`. Frontend renders a chain-link glyph on the row and an "Install method" row in the detail panel.

**Algorithm.**
1. For each skill's `dir`, call `lstatSync(dir)`. If `isSymbolicLink()` → set `isSymlink = true`.
2. Call `realpathSync(dir)` with a visited-inode set (seeded from `fs.statSync(dir).ino`). If the resolved inode appears twice → log warning, set `symlinkTarget = null`, keep `installMethod = "symlinked"`.
3. `installMethod`: `"authored"` when `scope === "own"`, else `"symlinked"` if `isSymlink`, else `"copied"`.

**Rationale.**
- Scanner is already the single source for origin classification. Adding symlink detection here keeps the contract tight.
- Visited-inode guard prevents hangs on cyclic symlinks without try/catch of unknown depth.
- `installMethod` is a derived, stable enum — easier for UI than booleans scattered across fields.

**Consequences.**
- `SkillInfo` grows by 3 fields — all stable, JSON-serializable, backward-compatible.
- `/api/skills` enrichment step sets these fields before sending.
- UI renders a tooltip from `symlinkTarget` (truncated with mid-ellipsis for long paths).

## 3. Visual Direction

### Bolder section divider

- Between each of the three sections: a 3px solid block of `var(--color-rule)` (opaque line, full sidebar width, no 14px inset like the current hairline).
- 1px inset shadow on top: `box-shadow: inset 0 1px 0 color-mix(in srgb, var(--color-rule) 50%, transparent)` — gives the divider perceived depth without visual noise.
- Above + below the divider: 12px breathing room.

### Section header

- Typography: **14px Source Serif 4** (display serif), weight 600, letter-spacing `0.12em`, text-transform uppercase, `font-feature-settings: "smcp" 0` (force explicit caps, not small-caps glyphs).
- Kicker uses a colorized text color per scope:
  - OWN → `var(--color-own)` (warm amber, existing token).
  - INSTALLED → `var(--color-accent)` (blue, existing).
  - GLOBAL → `var(--color-global)` (slate violet `#8B8FB1` light / `#6F748F` dark — new token added in `styles/tokens.css`).
- Right side of header: count in `font-mono` tabular-nums; status-dot (6px) to the left of the count; optional `N updates ▾` chip (existing 0683 component, unchanged).

### AgentScopePicker trigger

- Full-width row, 40px tall, sticky at top of the scroll container.
- Left: 6px dot (green/amber/grey), then active agent display name in `font-sans` 13px weight 500.
- Right: `▾` chevron + scope summary "(12 · 38)" meaning 12 installed / 38 global in mono.
- Hover: 4% surface tint. Focus: 2px focus ring.
- Matches the `AgentModelPicker` trigger geometry but horizontal (not pill) — intentionally a "banner" shape to signal section-level scope.

### SetupDrawer

- 480px wide, right-slide, 200ms cubic-bezier(0.2,0,0,1) enter; backdrop 40% black with 120ms fade.
- Header: provider name + icon + close `×` (Esc closes).
- Body sections (vertical rhythm, 16px between):
  1. "What this is" — one sentence, 14px regular.
  2. "Required env vars" — table of monospace names with copy buttons.
  3. "Get a key" — button-styled link to the verified console URL.
  4. (local providers only) "Install & run" — bash code block(s).
  5. "Learn more" — footer link, 12px.
- Keyboard: Esc closes, Tab cycles inside the drawer, focus returns to the trigger on close.

### Symlink glyph

- 10px chain-link SVG, rendered right-aligned in the `SkillRow` before the version/updates chip.
- Tooltip appears on hover + focus; content: `"symlinked → <symlinkTarget>"` truncated with mid-ellipsis after 60 chars.

## 4. Cross-Platform Validation

### Unit-test matrix (mocking `os.platform()` + `os.homedir()`)

| Input (registry entry) | darwin | linux | win32 |
| --- | --- | --- | --- |
| `~/.claude/skills` | `/Users/me/.claude/skills` | `/home/me/.claude/skills` | `C:\Users\me\.claude\skills` |
| `~/.cursor/skills` | `/Users/me/.cursor/skills` | `/home/me/.cursor/skills` | `C:\Users\me\.cursor\skills` |
| `~/.config/agents/skills` | `/Users/me/.config/agents/skills` | `/home/me/.config/agents/skills` | `C:\Users\me\AppData\Roaming\agents\skills` (fallback) |
| `~/.config/opencode/skills` | `/Users/me/.config/opencode/skills` | `/home/me/.config/opencode/skills` | `C:\Users\me\AppData\Roaming\opencode\skills` (fallback) |
| `~/.gemini/antigravity/skills` | `/Users/me/.gemini/antigravity/skills` | `/home/me/.gemini/antigravity/skills` | `C:\Users\me\.gemini\antigravity\skills` |

### Scanner contract assertions (platform-agnostic)

- `/api/skills` responses NEVER contain `~` (grep check in T-013).
- Every `dir` in responses passes `path.isAbsolute(dir) === true`.
- On the 49-agent registry fixture, `resolveAgentGlobalDir(agent)` never throws and returns an absolute path on all 3 platforms.

### Integration

- Playwright E2E runs on chromium only; where OS matters (symlink creation), tests use Node fixtures set up pre-navigation.

## 5. Anti-Patterns (Explicit Rejections)

1. **Modal stacking** — SetupDrawer over SettingsModal. `useSetupDrawer` closes Settings first. Asserted by E2E-04.
2. **Separate "Docs" page outside the studio shell** — the drawer IS the docs experience. No new route. No secondary nav item.
3. **Hardcoded POSIX paths** — no literal `/` separators, no `path.replace("~", ...)`, no string-splice `~` expansion. Lint rule (Biome custom) or grep check in T-013.
4. **Hiding the Own/Installed/Global distinction behind a toggle** — sections always visible (collapsible, not hide-able via view mode).
5. **Greying out agents with no presence** — use a "Not detected" subheading + inline "Set up..." CTA. Never a disabled row. Clickable, opens SetupDrawer.
6. **Quoting numeric Pro/Max quota caps** — no "5-hour window", no "2,000 daily cap". Link out.
7. **Empty-state dead-ends** — every scope empty state offers an action (`vskill new`, `vskill install`, `vskill install --global`).

## 6. File-Change Map (for implementers)

```
NEW:
  src/eval-ui/src/components/BrandLogo.tsx
  src/eval-ui/src/components/AgentScopePicker.tsx
  src/eval-ui/src/components/AgentScopeStatsPane.tsx
  src/eval-ui/src/components/SetupDrawer.tsx
  src/eval-ui/src/components/SetupProviderView/anthropic-api.tsx
  src/eval-ui/src/components/SetupProviderView/openai.tsx
  src/eval-ui/src/components/SetupProviderView/openrouter.tsx
  src/eval-ui/src/components/SetupProviderView/gemini.tsx
  src/eval-ui/src/components/SetupProviderView/ollama.tsx
  src/eval-ui/src/components/SetupProviderView/lm-studio.tsx
  src/eval-ui/src/components/SetupProviderView/claude-code.tsx
  src/eval-ui/src/components/SetupProviderView/registry.ts
  src/eval-ui/src/hooks/useAgentScope.ts
  src/eval-ui/src/hooks/useScopedSkills.ts
  src/eval-ui/src/hooks/useSetupDrawer.ts
  src/utils/paths.ts
  src/utils/__tests__/paths.test.ts
  src/eval/__tests__/skill-scanner.symlinks.test.ts
  src/eval/__tests__/skill-scanner.global-scope.test.ts
  src/eval-server/__tests__/api-agents-scopes.test.ts
  src/eval-ui/src/components/__tests__/AgentScopePicker.test.tsx
  src/eval-ui/src/components/__tests__/SetupDrawer.test.tsx
  src/eval-ui/tests/e2e/0686-*.spec.ts  (6 E2E specs, one per scenario)

EXTEND:
  src/agents/agents-registry.ts            (+ win32PathOverride field, + shared-folder fixture entries)
  src/eval/skill-scanner.ts                (+ scope, symlink fields, global-scope scanner)
  src/eval-server/api-routes.ts            (extend /api/skills, add /api/agents/scopes)
  src/eval-ui/src/types.ts                 (+ scope, isSymlink, symlinkTarget, installMethod)
  src/eval-ui/src/components/Sidebar.tsx   (tri-scope partition, bolder dividers)
  src/eval-ui/src/components/SidebarSection.tsx  (+ "global" origin variant, new typography)
  src/eval-ui/src/components/SkillRow.tsx  (+ symlink glyph)
  src/eval-ui/src/components/RightPanel.tsx (+ "Install method" metadata row)
  src/eval-ui/src/components/AgentModelPicker.tsx (Claude Code row label + banner)
  src/eval-ui/src/styles/tokens.css        (+ --color-global light/dark)
  src/eval-ui/src/strings.ts               (+ setup.* keys, + picker.claudeCodeLabel, + tooltip copy)
  src/eval-ui/src/App.tsx                  (BrandLogo, SetupDrawer mount)
  docs/ARCHITECTURE.md                     (+ §6 in-app docs system, + §7 global vs local scopes)
```

## 7. Rollout

- Behind no feature flag. All changes ship together — tri-scope without picker, or picker without drawer, is a worse UX than the current state.
- 0683 updateCount plumbing is extended in the same PR; a repo-global grep for `outdatedByOrigin` catches all call sites (≤ 6).
- Visual regression: Playwright `toHaveScreenshot` on 3 viewports (standard, narrow, dark-mode).
