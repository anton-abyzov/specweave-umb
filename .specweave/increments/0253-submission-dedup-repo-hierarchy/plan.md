# Plan: Submission Deduplication and Repository Hierarchy

## Architecture Decision

### Repository Model

Add a `Repository` table as the parent entity for skills and submissions:

```
Repository (owner, name) ──┬── Skill (name, repoUrl)
                            └── Submission (repoUrl, skillName)
```

Normalized URL: `https://github.com/{owner}/{repo}` (strip trailing slashes, .git suffix, path fragments).

### Deduplication Strategy

Three-layer dedup:

1. **Discovery-time enrichment**: When discovering skills, cross-reference against existing submissions/skills to return per-skill status
2. **Submission-time check**: Before creating a submission, check for existing pending/processing submissions or verified skills with same (repoUrl, skillName)
3. **Database constraint**: Unique index on `Submission(repoUrl, skillName, state)` filtered to active states (RECEIVED, QUEUED, SCANNING) to prevent concurrent duplicates

### Bulk Submit

New endpoint `POST /api/v1/submissions/bulk` that:
1. Accepts `{ repoUrl, skills: [{ name, path }] }`
2. Auto-creates/reuses Repository record
3. Batch dedup check against existing submissions + skills
4. Creates only new submissions
5. Returns per-skill status

### Key Design Decisions

- **KV + Prisma hybrid**: Submissions remain in KV for processing (7-day TTL) but dedup checks go through Prisma since verified skills persist there
- **Repository is optional FK**: Existing skills without repository links continue to work (migration adds nullable FK, backfill later)
- **Bulk endpoint is additive**: Existing single POST endpoint unchanged, bulk is new

## Files to Modify

| File | Change |
|------|--------|
| `prisma/schema.prisma` | Add `Repository` model, add `repositoryId` FK to `Skill` and `Submission` |
| `src/lib/submission-store.ts` | Add dedup check in `createSubmission()`, add `bulkCreateSubmissions()` |
| `src/lib/scanner.ts` | Add `enrichDiscoveryWithStatus()` that cross-refs discovered skills with DB |
| `src/app/api/v1/submissions/route.ts` | Add dedup check before creation |
| `src/app/api/v1/submissions/bulk/route.ts` | New bulk submit endpoint |
| `src/app/api/v1/submissions/discover/route.ts` | Enrich response with per-skill status |
| `src/app/submit/page.tsx` | Use bulk submit, show status badges, pre-deselect verified |

## Implementation Order

1. Prisma schema + migration (Repository model, FKs)
2. URL normalization utility + tests
3. Repository CRUD in submission-store
4. Dedup check logic + tests
5. Bulk submit endpoint + tests
6. Discovery enrichment + tests
7. Submit page UI updates
8. Backfill existing skills with repository links
