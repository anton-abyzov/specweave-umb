---
increment: 0801-studio-scope-breadcrumb-fix
title: "Studio header breadcrumb shows correct scope (PROJECT/PERSONAL/PLUGIN)"
---

# Plan

## Architectural Context

The Studio sidebar uses **scopeV2** (`SkillScope` union with 5 values) introduced in 0698, derived into two simpler axes:
- `group: "available" | "authoring"` — top-level grouping
- `source: "project" | "personal" | "plugin"` — the sub-section / scope label

The header breadcrumb predates 0698 and still reads the **legacy** `origin` field (`"source" | "installed"`), which was a 2-way classification meaning "user-authored vs agent-installed". That distinction collapses two distinct concepts when the agent is the user's home directory:
- A skill in `~/.claude/skills/...` (project-tier symlink) → `installed`, `source: "project"`
- A skill in `~/.agents/skills/...` (personal-tier symlink) → `installed`, `source: "personal"`

Both render as `PROJECT` today because origin is the only field consulted. Fix is to switch the breadcrumb to consult `source` (or fall back to `origin` for legacy fixtures).

## Affected Files

| File | Change |
|---|---|
| `src/eval-ui/src/StudioContext.tsx` | Extend `SelectedSkill` interface with `source?: SkillSource`. Update `loadSkills` hash restorer to support 3-segment form and copy `found.source`. Update `selectSkill` to write 3-segment hash. Update `revealSkill` to write 3-segment hash. |
| `src/eval-ui/src/components/TopRail.tsx` | Replace `originLabel` derivation. Compute label from `selected.source` first, falling back to `selected.origin` for legacy. Map `source` → `strings.scopeLabels.{sourceProject,sourcePersonal,sourcePlugin}`. |
| `src/eval-ui/src/App.tsx` | Update `onSelect` callback (line 583) to pass `source: s.source` from the SkillInfo into `selectSkill`. |
| `src/eval-ui/src/components/RightPanel.tsx` | Update `selectSkill({ ..., origin: "source" })` call (line 301) to also pass a `source` value. |
| `src/eval-ui/src/components/UpdateBell.tsx` | Update `selectSkill({...})` call (line 184) to pass `source` if known. |
| `src/eval-ui/src/components/__tests__/TopRail.test.tsx` | Update existing assertions and add new tests for personal/plugin/legacy-fallback. |
| `src/eval-ui/src/__tests__/StudioContext.first-load.test.tsx` | Add test for 3-segment hash parsing. |

## Hash Format Migration

```
Old: #/skills/{plugin}/{skill}                    (2 segments after /skills/)
New: #/skills/{source}/{plugin}/{skill}           (3 segments after /skills/)
```

Parser strategy in `loadSkills`:

```ts
// Try 3-segment first
let m = hash.match(/^#\/skills\/(project|personal|plugin)\/([^/]+)\/([^/?]+)/);
let source: SkillSource | undefined;
let plugin: string | undefined;
let skill: string | undefined;
if (m) {
  source = m[1] as SkillSource;
  plugin = m[2];
  skill = m[3];
} else {
  // Legacy 2-segment fallback
  m = hash.match(/^#\/skills\/([^/]+)\/([^/?]+)/);
  if (m) {
    plugin = m[1];
    skill = m[2];
  }
}
```

Skill match priority:
1. If `source` was parsed: filter by `source && plugin && skill`.
2. Else: filter by `plugin && skill`, take first match, derive `source` from the found skill.

This means saved bookmarks (legacy hash) keep working; new selections write the new format.

## Label Derivation (TopRail)

```ts
function scopeLabel(selected: SelectedSkill): string {
  if (selected.source === "project") return strings.scopeLabels.sourceProject;   // "Project"
  if (selected.source === "personal") return strings.scopeLabels.sourcePersonal; // "Personal"
  if (selected.source === "plugin") return strings.scopeLabels.sourcePlugin;     // "Plugins"
  // Legacy fallback: no source field. Conservative: installed without source
  // most often means a personal symlink.
  return selected.origin === "installed"
    ? strings.scopeLabels.sourcePersonal
    : strings.scopeLabels.sourceProject;
}
```

Color tokens:

```ts
const effectiveSource = (selected: SelectedSkill): SkillSource =>
  selected.source ?? (selected.origin === "installed" ? "personal" : "project");

const scopeColor = (source: SkillSource): string => {
  if (source === "project") return "var(--status-installed)"; // existing token reused
  if (source === "plugin")  return "var(--color-accent-ink)";  // existing accent
  return "var(--text-secondary)";                                // personal stays neutral
};
```

## Risk Analysis

| Risk | Mitigation |
|---|---|
| Hash format change breaks existing bookmarks | Legacy 2-segment parser fallback (AC-US2-03). |
| 25+ tests mock SelectedSkill without `source` | Make `source` optional on the type — fallback path covers them (AC-US1-05). |
| Same skill name in two scopes (e.g. personal + plugin copy) | New 3-segment hash disambiguates; legacy 2-segment matches first found, acceptable (no regression vs today). |
| Existing `dispatchNavigateScope` event still receives legacy `origin` | Out of scope — sidebar listener already handles both shapes; will refactor in a follow-up if needed. |

## Test Strategy

1. **Unit (vitest)**: TopRail label rendering for all 3 source values + legacy fallback. StudioContext hash parsing (3-segment + legacy 2-segment + malformed).
2. **Manual smoke**: Open Studio, click skills from each scope, verify header crumb. Reload page, verify crumb persists. Paste a legacy 2-segment hash into URL, verify it still selects.
3. **No E2E**: This is a pure UI rendering bug; vitest + manual is sufficient.
