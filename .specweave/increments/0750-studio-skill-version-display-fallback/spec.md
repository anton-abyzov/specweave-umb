---
increment: 0750-studio-skill-version-display-fallback
title: Studio Skill Version Display — Fallback & Consistency
type: feature
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Skill Version Display — Fallback & Consistency

## Overview

The vskill studio sidebar (`localhost:3162`, AVAILABLE list of 62 skills) shows version badges inconsistently. A handful of skills with `metadata.version` declared in frontmatter render badges (`gws 0.1.0`, `obsidian-brain 1.4.0`, `slack-messaging 1.0.0`, `get 1.1.0`); the majority of `sw:*` skills render no badge because their SKILL.md frontmatter omits the `version:` field.

Root cause: `vskill/src/eval-ui/src/components/VersionBadge.tsx:29` returns `null` when `version` is falsy, and `SkillRow.tsx:139-141` only renders the badge when `skill.version` is truthy. The scanner emits `version: null` for skills without frontmatter version, even though the registry's `currentVersion` defaults to `"1.0.0"` (`vskill-platform/src/lib/search.ts:303,429`) and most `sw:*` skills are bundled with a plugin whose `.claude-plugin/plugin.json` has a usable version (already read at `vskill/src/commands/marketplace.ts:50-66`).

This increment introduces a deterministic precedence chain so every skill shows a version, with a visual disambiguator that distinguishes author-declared versions from inherited ones.

```
Resolution order:
  frontmatter.version  >  registry.currentVersion  >  plugin.json.version  >  "0.0.0"
```

## User Stories

### US-001: Every skill shows a version badge (P1)
**Project**: vskill

**As a** vskill studio user
**I want** every skill in the AVAILABLE sidebar to show a version badge
**So that** I can compare skill maturity at a glance without confusing "no badge" with "no version"

**Acceptance Criteria**:
- [x] **AC-US1-01**: For every skill returned by the studio's local skill scan and remote search, the sidebar renders a version badge — no blank slots
- [x] **AC-US1-02**: `VersionBadge` component never returns `null` when given a `SkillInfo` produced by the resolver
- [x] **AC-US1-03**: A skill with no frontmatter version, not in the registry, and not in any plugin renders `0.0.0` rather than hiding the badge

---

### US-002: Author-declared frontmatter version takes precedence (P1)
**Project**: vskill

**As a** skill author who explicitly sets `metadata.version` in my SKILL.md
**I want** that version to appear in the studio
**So that** I retain authorial control over my skill's published version (e.g., `gws` stays at `0.1.0` because it is pre-1.0)

**Acceptance Criteria**:
- [x] **AC-US2-01**: When SKILL.md frontmatter contains a valid semver `version:` field, the resolver returns that exact value with `versionSource: 'frontmatter'`
- [x] **AC-US2-02**: Frontmatter `0.1.0` wins over registry `currentVersion: 1.0.0` (i.e. registry default never overrides explicit author choice)
- [x] **AC-US2-03**: Invalid semver in frontmatter is ignored and the resolver falls through to the next source

---

### US-003: Inherited versions are visually distinguishable (P1)
**Project**: vskill

**As a** vskill studio user
**I want** to tell at a glance whether a skill's version was author-declared or inherited from its plugin/registry
**So that** I don't mistake a plugin-bundled `2.3.0` for an author-curated `2.3.0`

**Acceptance Criteria**:
- [x] **AC-US3-01**: When `versionSource === 'frontmatter'`, the badge renders in normal (non-italic) weight with no tooltip
- [x] **AC-US3-02**: When `versionSource` is `registry`, `plugin`, or `default`, the badge renders in italic with a `title` attribute (HTML tooltip) describing provenance — e.g. `"Inherited from SpecWeave plugin v2.3.0"`, `"Inherited from registry"`, or `"No version declared"`
- [x] **AC-US3-03**: Tooltip text varies by source so users can distinguish plugin-inherited from registry-inherited from default

---

### US-004: Plugin authors get version updates "for free" (P2)
**Project**: vskill

**As a** plugin author who ships many skills (e.g., SpecWeave with 62 sw:* skills)
**I want** my skills to inherit the plugin version automatically when frontmatter is omitted
**So that** I don't have to remember to bump each individual SKILL.md frontmatter on every plugin release

**Acceptance Criteria**:
- [x] **AC-US4-01**: For a skill discovered inside a plugin directory containing `.claude-plugin/plugin.json` with a valid `version` field, and where the skill has no frontmatter version and is not found in the registry, the resolver returns the plugin version with `versionSource: 'plugin'`
- [x] **AC-US4-02**: Plugin.json reads are cached per-plugin during a single scanner pass to avoid repeated disk I/O when many skills share a plugin

---

### US-005: No data backfill required (P1)
**Project**: vskill

**As a** maintainer of the existing registry
**I want** the fix shipped without backfilling any database rows or modifying any existing SKILL.md files
**So that** rollout is reversible and zero-risk to historical data

**Acceptance Criteria**:
- [x] **AC-US5-01**: No SQL migration, no script that updates existing `Skill.currentVersion` or `SkillVersion` rows is part of this increment
- [x] **AC-US5-02**: No SKILL.md files in the codebase are modified to add a `version:` frontmatter field as part of this increment (verified via `git status` — no SKILL.md files in diff)
- [x] **AC-US5-03**: Reverting all code changes restores the prior visible behavior (some skills show badges, most don't) with no leftover data drift

## Functional Requirements

### FR-001: Backend version resolver
A pure function `resolveSkillVersion(input): { version: string, versionSource: 'frontmatter'|'registry'|'plugin'|'default' }` lives in vskill scanner code. Inputs: parsed frontmatter version (optional), registry `currentVersion` (optional), plugin.json version (optional). Output: always a non-empty version string with provenance label. Pure, no I/O, fully unit-testable.

### FR-002: Scanner integration
The local skill scanner (`vskill/src/scanner/`) and the eval-server `/api/skills` handler call the resolver and populate `SkillInfo.version` (required string) and `SkillInfo.versionSource`. Plugin.json reads are cached per-plugin within a single scan.

### FR-003: SkillInfo type evolution
`SkillInfo.version` becomes a required `string` (was `string | null | undefined`). New optional `versionSource` field. `normalizeSkillInfo` in `vskill/src/api.ts:226` updated to coerce never-null and pass through `versionSource`.

### FR-004: Source-aware badge rendering
`VersionBadge` accepts `source` prop. Source `frontmatter` → normal style, no tooltip. Sources `registry` | `plugin` | `default` → italic + `title` tooltip. The "return null when falsy" branch is removed.

### FR-005: Sidebar conditional removal
`SkillRow.tsx:139-141` drops the `{skill.version && (...)}` conditional and always renders `VersionBadge`, passing `skill.versionSource`.

## Success Criteria

- 100% of skills in studio AVAILABLE list render a version badge
- 4 representative skills retain author-declared versions: `gws 0.1.0`, `obsidian-brain 1.4.0`, `slack-messaging 1.0.0`, `get 1.1.0`
- ≥50 sw:* skills that previously showed no badge now show plugin version in italic with tooltip
- Resolver unit tests: 100% branch coverage (4 sources × 2-3 edge cases each)
- VersionBadge component tests: source-aware rendering verified

## Out of Scope

- DB backfill of existing `Skill.currentVersion` rows
- Changes to publish flow (`vskill-platform/src/lib/submission/publish.ts:272` 1.0.0 default stays)
- Changes to SKILL.md format / frontmatter parser
- CLI version display (`vskill --version`) — different concern
- Plugin version conflict resolution when same skill name exists in multiple plugins (edge case noted but resolved by deterministic scan order)

## Dependencies

- Existing plugin.json reader at `vskill/src/commands/marketplace.ts:50-66`
- Existing frontmatter parser at `vskill-platform/src/lib/frontmatter-parser.ts:34-67`
- Existing search.ts `currentVersion` default (`vskill-platform/src/lib/search.ts:303,429`)
