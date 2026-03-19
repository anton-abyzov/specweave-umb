# Plan: Tool-Agnostic Command References — Phases 2-4

## Approach

Automated sed replacements across 3 scopes, run in parallel via subagents.

## Phase 2: SKILL.md (31+ files)
- sed replace `/sw:` → `sw:` and `/sw-` → `sw-` in all .md files under plugins/specweave/skills/
- Preserve `Skill({ skill: "sw:..."})` calls (no slash to remove)

## Phase 3: Docs-Site (199 files)
- sed replace same patterns in docs-site/docs/**/*.md

## Phase 4: TypeScript Source (~103 files)
- sed replace in all .ts files EXCEPT phase-detector.ts and project-scope-guard.ts
- Those 2 files have functional `/sw:` parsing that must be preserved
- Run vitest to verify no regressions

## Excluded Files
- `src/core/workflow/phase-detector.ts` — COMMAND_MAPPINGS, analyzeCommands, getNextPhaseCommand
- `src/core/hooks/project-scope-guard.ts` — regex for skill invocation detection
