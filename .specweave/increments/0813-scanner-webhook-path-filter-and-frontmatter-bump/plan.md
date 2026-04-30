# Implementation Plan: Webhook path-filter + frontmatter-driven bumps

## Architecture

```
                     GitHub push payload
                     ┌──────────────────────────────────────┐
                     │ commits: [                            │
                     │   { added: [...], removed: [...],     │
                     │     modified: ["agents.json", ...] }, │
                     │   ...                                  │
                     │ ]                                      │
                     │ ref: "refs/heads/main"                 │
                     └────────────┬───────────────────────────┘
                                  ▼
              POST /api/v1/webhooks/github/route.ts
   ─────────────────────────────────────────────────────────────
   existing: HMAC verify → DO dedup → ref/branch parse → skill match
                                              │
                                              ▼
                          NEW: collect changedPaths from commits[]
                                              │
                                              ▼
                       NEW: filter `matches` by path overlap with
                            each skill's directory (skillPath dirname)
                                              │
                                              ▼
                       enqueueScanHigh per surviving skill + emit
                       webhook.skipped.path-mismatch for filtered

                     scanner.scanOneSkill (after 0811 fetch)
                     ┌──────────────────────────────────────┐
                     │ fetchSkillMdAtSha → real content      │
                     └────────────┬───────────────────────────┘
                                  ▼
                       NEW: readFrontmatterVersion(content)
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                                 ▼
              has frontmatter version              no frontmatter version
                       │                                   │
                       ▼                                   ▼
            semver compare to            fallback to existing deriveNextVersion
            skill.currentVersion              (legacy compat)
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
     greater        equal           lower
       │               │               │
       ▼               ▼               ▼
  use frontmatter  SKIP bump      reject (downgrade),
  for new row      advance lastSeen, log warn, no advance
                   metric: skipped
```

## Modules

### Modified — `src/app/api/v1/webhooks/github/route.ts`
- Extend `PushPayload` type with `commits?: Array<{ added?: string[]; removed?: string[]; modified?: string[] }>`.
- Add helper `collectChangedPaths(commits)` returning `Set<string>` (union of all three arrays across all commits, or `null` if commits array is missing/empty).
- Add helper `skillTouched(skill, changedPaths)`:
  - If `changedPaths` is `null` → return `true` (defensive default).
  - Compute `skillDir`: if `skill.skillPath` is null/empty → `""`. Otherwise extract directory (everything before the last `/`).
  - Return `true` if any `changedPath` startsWith `skillDir + "/"` OR `changedPath === skill.skillPath` itself.
- Filter `matches` by `skillTouched`. Track filtered count. Emit metric per filtered skill.
- Update response shape: `{ ok: true, enqueued: <N>, skipped: <M> }`.

### Modified — `src/lib/skill-update/scanner.ts`
- Import `readFrontmatterVersion` from `@/lib/skill-md/inject-version-if-missing`.
- After the existing `realHashAvailable` branch (where we computed `contentHash` from the fetched content), if a real fetch succeeded, also extract `frontmatterVersion = readFrontmatterVersion(fetched.content)`.
- Add helper `compareSemver(a, b)` returning `-1 | 0 | 1` (or `null` if either is unparseable).
- Replace the unconditional `const newVersion = await deriveNextVersion(skill.currentVersion);` with:
  - If `frontmatterVersion` is null → fall back to `deriveNextVersion`. Emit `scanner.bump.fallback.no-frontmatter`.
  - Compare `frontmatterVersion` vs `skill.currentVersion`:
    - `> 0` (greater) → `newVersion = frontmatterVersion`. Continue with bump.
    - `=== 0` (equal) → SKIP bump. Update `lastSeenSha + lastCheckedAt`. Emit `scanner.bump.skipped.no-frontmatter-bump`. Return `{status: "unchanged"}`.
    - `< 0` (lower) → SKIP bump. Do NOT advance lastSeenSha. Emit `scanner.bump.rejected.downgrade`. Return `{status: "unchanged"}`.
    - `null` (unparseable) → fall back to `deriveNextVersion`. Emit `scanner.bump.fallback.unparseable-frontmatter`.
- Make these branches BEFORE the existing content-hash-equality dedup so the order is: (1) real-hash dedup (still skips identical content even if frontmatter mismatched), (2) frontmatter check.

### Modified — `src/app/api/v1/webhooks/github/__tests__/route.test.ts` (extend or create)
- 6 new test cases covering AC-US1-01..06 (one push, three tracked skills, various touched/untouched permutations + commits-empty + skillPath-null).

### Modified — `src/lib/skill-update/__tests__/scanner.test.ts`
- 4 new tests covering AC-US2-02..05 (frontmatter version greater/equal/lower/missing).
- Update existing TC-S02 fixture so frontmatter version is bumped (otherwise it'd hit the new "equal" skip path and break).

## Reused utilities

- `readFrontmatterVersion` — `src/lib/skill-md/inject-version-if-missing.ts:42`.
- `enqueueScanHigh` — `src/lib/skill-update/enqueue.ts`.
- Existing webhook HMAC verify + DO dedup — unchanged.

## Semver compare helper

Lightweight, no dep:
```ts
function compareSemver(a: string, b: string): -1 | 0 | 1 | null {
  const re = /^(\d+)\.(\d+)\.(\d+)/;
  const ma = re.exec(a), mb = re.exec(b);
  if (!ma || !mb) return null;
  for (let i = 1; i <= 3; i++) {
    const da = +ma[i], db = +mb[i];
    if (da !== db) return da > db ? 1 : -1;
  }
  return 0;
}
```

## ADR (inline)

**Decision**: When content changes but frontmatter version is unchanged, the scanner SKIPS the bump rather than auto-bumping or committing back to the source repo.
**Rationale**: Authors are the sole authority on version numbers. Surprise bumps (the symptom that started this whole investigation) erode trust in registry semantics. Committing back to the source repo would require GitHub App write scope and adds blast-radius for misconfiguration. The simpler model — "bump SKILL.md to publish" — matches every other package registry (npm, PyPI, crates.io).
**Alternatives**: (1) Auto-bump and commit back via GitHub App — rejected, requires write scope per repo. (2) Auto-bump without commit-back (current 0811 behavior) — rejected, this is what caused the bug. (3) Reject the push at webhook time — rejected, web-hook is wrong layer.

**Decision**: Webhook path-filter falls back to enqueue-all when `commits[]` is missing or empty.
**Rationale**: GitHub omits `commits[]` for huge pushes (>2048 commits) and some non-push events. Refusing to enqueue would risk missing real updates. The 0811 content-hash gate ensures the consumer-side cost is bounded even if the queue absorbs an extra fan-out.

## Test strategy

| File | Type | Coverage |
|------|------|----------|
| `src/app/api/v1/webhooks/github/__tests__/route.test.ts` | vitest unit | webhook path-filter (6 cases) |
| `src/lib/skill-update/__tests__/scanner.test.ts` | vitest unit | frontmatter-driven bumps (4 new + 1 updated) |

## Deploy + smoke

1. `rm -rf .open-next && npm run build && npm run build:worker && npm run deploy`.
2. Trigger a webhook by pushing an unrelated commit to a tracked repo. Inspect the response: `{enqueued: 0, skipped: N}` for repos like vskill where no skill paths were touched.
3. Push a commit that changes a SKILL.md WITHOUT bumping the frontmatter version. Wait for cron tick. Verify NO new SkillVersion row was created. Metric `scanner.bump.skipped.no-frontmatter-bump` increments.
4. Push a commit that changes a SKILL.md AND bumps frontmatter `version:` to e.g. 1.2.0. Verify a new SkillVersion row appears with `version: "1.2.0"` (NOT 1.1.1).
5. Verify `count(*) FROM "SkillVersion" WHERE "contentHash" LIKE 'sha256:pending:%'` is still 0 (residual cleanup persisted).
