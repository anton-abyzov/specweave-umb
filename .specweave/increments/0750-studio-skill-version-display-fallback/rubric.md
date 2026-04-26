---
increment: 0750-studio-skill-version-display-fallback
title: "Studio Skill Version Display — Fallback & Consistency"
generated: "2026-04-26T06:30:00.000Z"
source: auto-generated
---

# Quality Contract

## Coverage

- `resolveSkillVersion` resolver: 100% branch coverage (4 precedence sources × at least one passing test each, plus invalid-semver and all-null fallback paths).
- `VersionBadge` component: every `versionSource` value (`frontmatter`, `registry`, `plugin`, `default`) has a passing render test asserting style and tooltip text.
- Modified files overall: ≥ 90% line coverage.

## Correctness Gates

- **Every skill in studio AVAILABLE renders a version badge.** No conditional skip in `SkillRow`. Verified by component test TC-015 + manual TC-016.
- **Author-declared versions preserved.** `gws 0.1.0`, `obsidian-brain 1.4.0`, `slack-messaging 1.0.0`, `get 1.1.0` continue to display their author values with `versionSource: 'frontmatter'`.
- **No DB writes.** This increment introduces zero SQL migrations and zero scripts that touch existing `Skill` / `SkillVersion` rows.
- **No SKILL.md edits.** No checked-in SKILL.md file in the repo gains a `version:` frontmatter field as part of this increment.
- **TypeScript build clean.** `npx tsc --noEmit` exits 0 after `SkillInfo.version` becomes required.
- **No regressions in existing studio tests.** `npx vitest run src/eval-ui` green.

## Visual / UX

- `versionSource === 'frontmatter'` → badge in normal weight, no `title` attribute.
- `versionSource ∈ {registry, plugin, default}` → badge in italic with a `title` attribute (HTML tooltip) whose text matches one of:
  - `/^Inherited from .+ plugin v\d+\.\d+\.\d+$/` for `plugin`
  - `Inherited from registry` for `registry`
  - `No version declared` for `default`
- Tooltip is keyboard-accessible (native `title` attribute, no custom popover required).

## Performance

- Plugin.json reads cached per-scan via `Map<pluginDir, string|null>` — verified by integration test that asserts at most one `readFileSync` call per unique plugin dir within a single scanner pass.

## Review Gates

- [ ] `sw:code-reviewer` passes with 0 critical/high/medium findings.
- [ ] `/simplify` clean — no duplicate fallback logic across scanner / eval-server / frontend.
- [ ] `sw:grill` report clean — every AC traced to passing tests.
- [ ] `sw:judge-llm` report present (or waived if no consent).
- Manual gate: Anton runs `npx vskill studio` locally and confirms TC-016 through TC-021 pass visually.

## Out-of-Scope (do not enforce in this rubric)

- Publish flow `1.0.0` default at `vskill-platform/src/lib/submission/publish.ts:272` — unchanged.
- CLI `vskill --version` display — different concern.
- Plugin name disambiguation when same skill name lives in multiple plugins — deterministic scan order accepted.
