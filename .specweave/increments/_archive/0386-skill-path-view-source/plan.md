# Implementation Plan: Add skillPath to Skill model and View Source link

## Overview

Add `skillPath` (optional String) to the Skill Prisma model, copy it during `publishSkill()`, expose in API via `mapDbSkillToSkillData()`, and render a "Source" meta row on the skill detail page with a GitHub deep-link.

## Architecture

### Data Model Change
- `Skill.skillPath: String?` — path to SKILL.md within repo (e.g., "plugins/foo/skills/bar/SKILL.md")
- Nullable to handle existing rows and skills without linked submissions

### Data Flow
```
Submission.skillPath → publishSkill() → Skill.skillPath → mapDbSkillToSkillData() → API → Frontend
```

### Deep-Link Format
```
{repoUrl}/blob/HEAD/{skillPath}
```
Example: `https://github.com/anton-abyzov/specweave/blob/HEAD/plugins/frontend/skills/architect/SKILL.md`

## Files Modified

1. `prisma/schema.prisma` — add `skillPath String?` to Skill model
2. `src/lib/submission-store.ts` — add `skillPath` to create/update in `publishSkill()`
3. `src/lib/types.ts` — add `skillPath` to `SkillData` interface
4. `src/lib/data.ts` — add `skillPath` mapping in `mapDbSkillToSkillData()`
5. `src/app/skills/[name]/page.tsx` — add "Source" meta row

## Files Created

1. `scripts/backfill-skill-path.ts` — one-time backfill script

## Deployment Steps

1. Run Prisma migration (`npx prisma migrate dev --name add-skill-path`)
2. Deploy application
3. Run backfill script (`npx tsx scripts/backfill-skill-path.ts --execute`)
