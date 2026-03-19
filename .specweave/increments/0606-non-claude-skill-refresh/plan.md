# Implementation Plan

## Overview

Two targeted fixes in two repos (specweave + vskill), no new abstractions.

## Architecture

### Fix 1: Frontmatter Normalization (specweave)

Add `normalizeFrontmatter(content, skillName)` in `plugin-copier.ts`. Applied only to SKILL.md files when `targetSkillsDir` is non-Claude. Regex-based frontmatter manipulation following existing `adapter-base.ts:sanitizeFrontmatter()` pattern but enhanced with `description:` injection and `hooks:` block stripping.

**Key file**: `src/utils/plugin-copier.ts`

### Fix 2: vskill update for Local Sources (vskill)

1. Default no-args behavior to update all (change in `update.ts`)
2. Add `fetchLocal()` in `source-fetcher.ts` — uses `findCoreSkillsDir()` from `sync.ts`
3. Export `findCoreSkillsDir()` from `sync.ts`

**Key files**: `src/commands/update.ts`, `src/updater/source-fetcher.ts`, `src/core-skills/sync.ts`

## Technical Challenges

### Challenge 1: Multi-line hooks YAML block stripping
**Solution**: Match `hooks:` line followed by indented continuation lines
**Risk**: Low — hooks always use consistent YAML indentation

### Challenge 2: Plugin cache may not exist
**Solution**: `findCoreSkillsDir()` already returns null — `fetchLocal()` returns null to skip gracefully
