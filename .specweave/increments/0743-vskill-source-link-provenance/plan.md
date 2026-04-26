---
increment: 0743-vskill-source-link-provenance
title: "vskill source-link provenance"
created: 2026-04-26
---

# Architecture Plan

## Layer map

| Layer | File | Change | Lines |
|-------|------|--------|-------|
| 1 (CLI) | `repositories/anton-abyzov/vskill/src/commands/add.ts` | Direct-repo install: persist `sourceRepoUrl` + `sourceSkillPath` from `DiscoveredSkill.path` | 2086-2103 |
| 1 (CLI) | `repositories/anton-abyzov/vskill/src/commands/add.ts` | Single-skill legacy install: same fields, path from in-scope `skillSubpath` | 2716-2730 |
| 1 (CLI) | `repositories/anton-abyzov/vskill/src/commands/add.ts` | `SkillInstallResult` type: add optional `sourceSkillPath?: string` | type def |
| 2 (server) | `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` | `resolveSourceLink`: drop `?? "SKILL.md"` fallback; return `skillPath: null` for legacy entries | 794-800 |
| 3 (UI) | `repositories/anton-abyzov/vskill/src/eval-ui/src/components/DetailHeader.tsx` | `SourceFileLink` receives `repoUrl={skill.repoUrl ?? null}`; `AuthorLink` unchanged | 200-204 |

## Reuse (no new code where existing fits)

- **`DiscoveredSkill.path`** (`src/discovery/github-tree.ts:80-87`) already holds the relative path. No URL parsing needed.
- **`skillSubpath`** (`src/commands/add.ts:2568`) already extracts the path for the legacy install path.
- **`SourceFileLink` copy-chip mode** (`src/eval-ui/src/components/SourceFileLink.tsx:109-136`) is the existing safe fallback when `repoUrl` is absent.
- **Lockfile types** already declare the new fields as optional (`src/lockfile/types.ts:24-26`).
- **Existing test scaffolding** — extend, don't duplicate:
  - `src/eval-server/__tests__/skill-metadata-source-link.test.ts` (Layer 2)
  - `src/eval-ui/src/components/__tests__/DetailHeader.source-link.test.tsx` (Layer 3)
  - `src/lockfile/lockfile.test.ts` (Layer 1 fixture shape)

## Order of work (RED-GREEN-REFACTOR)

Start with the smallest blast radius, end with the broadest:

1. **Layer 2** — pure resolver function. Update existing test to assert `null` instead of `"SKILL.md"`, then change the fallback. Local impact only.
2. **Layer 3** — depends on Layer 2 contract. Invert the homepage-fallback regression test; change `DetailHeader` to drop the fallback.
3. **Layer 1** — biggest change. Add tests covering both lockfile-write paths, then thread `sourceSkillPath` through.

## Contract changes (intentional)

Two existing test assertions are inverted as part of this fix — these are the documented contract changes:

- `skill-metadata-source-link.test.ts:99` — `expect(md.skillPath).toBe("SKILL.md")` becomes `expect(md.skillPath).toBeNull()` (AC-US2-01).
- `DetailHeader.source-link.test.tsx:133-147` — homepage-only renders `source-file-link` anchor becomes renders `source-file-copy` chip (AC-US3-01).

Both are intentional — the previous behaviour was the bug.

## Out of scope (deferred)

- Backfill migration for existing lockfiles. Natural reinstall fixes them.
- Marketplace plugin install path (`src/commands/add.ts:595-621`). Plugin entries hold multiple skills; the resolver fallback there is documented and correct for flat layouts.
- AuthorLink homepage handling. Profile link is harmless.

## Risk assessment

- **Risk**: legacy lockfiles where `sourceSkillPath` is genuinely `"SKILL.md"` (a flat-layout repo with the SKILL.md at root) lose their anchor and get the copy-chip until next install.
  - **Mitigation**: copy-chip is the existing fallback; user can copy the local path. Reinstall restores the anchor with the explicit path. Single-skill flat-layout repos are uncommon in the user's workspace; the dominant case is multi-skill plugin repos.
- **Risk**: a downstream consumer relies on the documented `"SKILL.md"` default.
  - **Mitigation**: grep confirms `resolveSourceLink` is only consumed by `buildSkillMetadata` in the same file; no external consumer.

## Verification gates

Per CLAUDE.md testing pipeline:
1. RED-GREEN passes for each layer (`npx vitest run` in vskill repo).
2. Full vskill test suite green.
3. End-to-end manual: rebuild + reinstall greet-anton + restart studio + verify anchor opens real file.
4. Closure pipeline: `sw:code-reviewer` then `/simplify` then `/sw:grill` then `/sw:judge-llm` then `/sw:done`.
