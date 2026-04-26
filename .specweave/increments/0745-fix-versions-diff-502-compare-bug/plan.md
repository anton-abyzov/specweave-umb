# Plan: Fix `/versions/diff` 502 Bad Gateway

## Architecture

```
┌─ Studio (eval-server, port 3162)
│   GET /api/skills/{plugin}/{skill}/versions/diff
│   → proxy → https://verified-skill.com/api/v1/skills/{owner}/{repo}/{skill}/versions/diff
│
└─ vskill-platform (Next.js)
    /api/v1/skills/[owner]/[repo]/[skill]/versions/
        ├─ route.ts            ← list ONLY (was: muddled list+diff)
        ├─ compare/route.ts    ← GitHub-aware diff, LCS fallback (canonical engine)
        └─ diff/route.ts       ← NEW: thin adapter over compare (this fix)
```

## Why this shape

- The studio's `getVersionDiff()` URL is wired into release SKUs already (tests at `vskill/src/eval-server/__tests__/version-routes.test.ts`). Changing it would force a coordinated release of `vskill` + `vskill-platform`.
- The `/compare` endpoint already implements every hard part (DB lookups, semver/SHA validation, GitHub `/compare/A...B` API integration with KV caching, 1MB patch truncation, and a local LCS fallback for non-GitHub repos).
- The `VersionDiff` shape `{ from, to, diffSummary, contentDiff }` is what the studio's `ChangelogViewer` already consumes. Returning that shape means **zero studio changes**.

## Adapter behavior

```ts
// versions/diff/route.ts
GET(request, ctx):
  // 1. Delegate to compare's GET handler — same signature
  const compareRes = await compareGET(request, ctx);

  // 2. Pass through error responses unchanged (400/404/500)
  if (!compareRes.ok) return compareRes;

  // 3. Parse compare's body and adapt to VersionDiff shape:
  const data = await compareRes.json();
  // Prefer SKILL.md (most diffs are skill-content), else first file, else empty.
  const skillFile = data.files.find(f => f.filename.endsWith('SKILL.md')) ?? data.files[0];
  const contentDiff = skillFile?.patch ?? '';

  // 4. diffSummary is NOT in compare's response — fetch from DB.
  //    Cheap: one row by (skillId, version) on an indexed pair.
  const diffSummary = await db.skillVersion.findFirst({
    where: { skillId, version: to }, select: { diffSummary: true }
  })?.diffSummary ?? '';

  return NextResponse.json({ from, to, diffSummary, contentDiff });
```

The DB lookup duplicates what compare already did internally. We accept the second hit because:
- It's a cached PK lookup (`@@unique([skillId, version])` exists on SkillVersion).
- Refactoring compare to return `diffSummary` would expand its public contract for one consumer.
- Profiling can hoist this later if it shows up; the studio is human-driven and not on a hot path.

## Cleanup of dead code

Remove from `versions/route.ts`:
- Lines 27-32 (`if (url.pathname.endsWith('/diff') ...) handleDiff(...)`)
- Function `handleDiff` (lines ~87-129)
- Function `computeSimpleDiff` (lines ~131-176)
- Function `positionalDiff` (lines ~178-192)
- Imports/types only used by those functions, if any.

The list endpoint shrinks back to its actual purpose. No behavior change for `/versions` callers.

## Test strategy

| Test | Location | What it asserts |
|---|---|---|
| `route.test.ts:returns VersionDiff shape on success` | `versions/diff/__tests__/route.test.ts` | AC-US1-01, AC-US1-02 |
| `route.test.ts:diffSummary populated from DB` | same | AC-US1-03 |
| `route.test.ts:missing from/to → 400` | same | AC-US1-04 |
| `route.test.ts:malformed version → 400` | same | AC-US1-05 |
| `route.test.ts:skill not found → 404` | same | AC-US1-06 |
| `route.test.ts:version not found → 400` | same | AC-US1-07 |

Existing tests that MUST continue to pass unchanged:
- `versions/compare/__tests__/route.test.ts` — proves the engine is untouched
- `versions/__tests__/route.test.ts` (if it exists) — proves list endpoint unchanged
- `vskill/src/eval-server/__tests__/version-routes.test.ts` — proves studio proxy URL is stable

## Risks

- **Risk**: Compare returns no files (no changes between versions) → `contentDiff: ''`. ChangelogViewer must handle empty string. **Mitigation**: existing test path; the LCS fallback never returns an empty `files[]`, it returns `[{ status: 'unavailable', patch: '' }]`. So `skillFile.patch` is `''`, not undefined. Safe.
- **Risk**: Compare's response includes patches >1MB truncated. Studio's `ChangelogViewer` already shows truncated patches with the trailing marker — no change needed.
- **Risk**: Adapter doubles a Prisma round-trip. **Mitigation**: indexed PK lookup, ~5ms; not on hot path; profile-driven optimization if needed.
