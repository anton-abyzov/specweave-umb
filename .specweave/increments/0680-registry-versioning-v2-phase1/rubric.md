---
increment: 0680-registry-versioning-v2-phase1
title: "Registry Versioning v2 — Phase 1 (server-side author-declared SemVer)"
generated: "2026-04-22"
source: sw-planner
version: "1.0"
status: pending
---

# Quality Contract: Registry Versioning v2 — Phase 1

## How to read this rubric

- **[blocking]** — must PASS before `/sw:done` will close the increment
- **[advisory]** — recorded in the closure report; does not block
- **Evaluator**: `sw:grill` = automated adversarial review agent; `human` = manual operator check
- **Result**: `[ ] PENDING` until evaluated

---

## Functional Correctness (AC coverage)

### R-001: Auto-mode publish path unchanged [blocking]
- **Source**: AC-US1-01
- **Evaluator**: sw:grill
- **Verify**: Run `npx vitest run src/lib/__tests__/skill-version-creation.test.ts` after all Phase 1 changes; confirm 9/9 pass with zero modifications to the test file
- **Threshold**: 9/9 tests pass; `bumpSource` on auto-path rows is `"auto-patch"` or absent; no 409 errors on any pre-existing submission flow
- **Result**: [ ] PENDING

### R-002: Author mode creates version row with declared SemVer [blocking]
- **Source**: AC-US1-02
- **Evaluator**: sw:grill
- **Verify**: Unit test in `skill-version-author-mode.test.ts` — skill with `versioningMode="author"`, frontmatter `version: 1.2.0`, latest version `1.1.5` → `skillVersion.create` called with `version="1.2.0"`, `major=1`, `minor=2`, `patch=0`, `bumpSource="frontmatter"`
- **Threshold**: Exact field values match; no auto-patch fallback triggered when valid frontmatter version present
- **Result**: [ ] PENDING

### R-003: Duplicate version rejected HTTP 409 VERSION_DUPLICATE [blocking]
- **Source**: AC-US1-03
- **Evaluator**: sw:grill
- **Verify**: Unit test — `versioningMode="author"`, declared `1.2.0` matches existing latest `1.2.0` → `MonotonicityError` thrown with `code="version_duplicate"`, `statusCode=409`; no SkillVersion row created
- **Threshold**: Error code matches exactly `"version_duplicate"`; zero DB writes on rejection path
- **Result**: [ ] PENDING

### R-004: Backward version rejected HTTP 409 VERSION_MONOTONICITY_VIOLATION [blocking]
- **Source**: AC-US1-04
- **Evaluator**: sw:grill
- **Verify**: Unit test — `versioningMode="author"`, declared `0.9.0`, existing latest `1.0.0` → `MonotonicityError` with `code="version_not_monotonic"`; `declared="0.9.0"`, `latest="1.0.0"` in error body
- **Threshold**: Backward move (0.9.0 < 1.0.0 by SemVer) reliably rejected; no partial writes
- **Result**: [ ] PENDING

### R-005: Missing/invalid frontmatter version falls back to auto-patch [blocking]
- **Source**: AC-US1-05
- **Evaluator**: sw:grill
- **Verify**: Two sub-cases: (a) `versioningMode="author"` + no `version:` in frontmatter → auto-patch-bump executes, `bumpSource="auto-patch"`; (b) `version: not-semver` → same auto-patch fallback
- **Threshold**: No 422 or 409 thrown on fallback path; `bumpSource` correctly recorded
- **Result**: [ ] PENDING

### R-006: Different scripts/ content produces different treeHash [blocking]
- **Source**: AC-US2-01
- **Evaluator**: sw:grill
- **Verify**: Unit test — two submissions with identical SKILL.md but `scripts/run.sh` differing by one character → resulting `SkillVersion.treeHash` values are not equal
- **Threshold**: treeHash values differ; test passes deterministically across repeated runs
- **Result**: [ ] PENDING

### R-007: Server treeHash byte-identical to CLI algorithm [blocking]
- **Source**: AC-US2-02
- **Evaluator**: sw:grill
- **Verify**: Contract test in `tree-hash-contract.test.ts` — 3-file fixture hashed by `computeTreeHash()` must equal precomputed hex produced by `repositories/anton-abyzov/vskill/src/updater/source-fetcher.ts:47-60` against the same fixture; same sort order, concat format, normalization, output length
- **Threshold**: Exact 64-char hex string equality; contract test must remain in CI and never be skipped
- **Result**: [ ] PENDING

### R-008: treeHash stable across all nesting depths [blocking]
- **Source**: AC-US2-03
- **Evaluator**: sw:grill
- **Verify**: Unit test — skill bundle with `SKILL.md`, `scripts/a.sh`, `scripts/sub/deep.sh`, `references/docs/guide.md` → all 4 files included; output is identical on two consecutive calls with same input
- **Threshold**: Every file present in hash input; hash is stable (deterministic)
- **Result**: [ ] PENDING

### R-009: publishedBy populated from submission.userId [blocking]
- **Source**: AC-US3-01
- **Evaluator**: sw:grill
- **Verify**: Unit test — submission has `userId="user_abc123"` → new SkillVersion row has `publishedBy="user_abc123"` under both `auto` and `author` versioningMode
- **Threshold**: Field value matches submission userId exactly; present on every new version row
- **Result**: [ ] PENDING

### R-010: Anonymous publish (no userId) blocked with validation error [blocking]
- **Source**: AC-US3-02
- **Evaluator**: sw:grill
- **Verify**: Unit test — submission `userId=null` → server-side validation error thrown before transaction; no `skillVersion.create` call; no partial row in mock DB
- **Threshold**: Error is distinct from MonotonicityError; no DB write occurs
- **Result**: [ ] PENDING

### R-011: Backfill populates major/minor/patch from version string [blocking]
- **Source**: AC-US4-01
- **Evaluator**: sw:grill
- **Verify**: Integration test — SkillVersion rows with `version="1.4.2"`, `"0.0.1"`, `"2.0.0-rc.1"` and `major=null` → after backfill: correct integer components and prerelease string on each row
- **Threshold**: Parsed values match SemVer parse of the version string; unparseable versions go to `errors[]` and are skipped (not updated, not failed)
- **Result**: [ ] PENDING

### R-012: Backfill initializes Skill.distTags to {"latest": currentVersion} [blocking]
- **Source**: AC-US4-02
- **Evaluator**: sw:grill
- **Verify**: Integration test — Skill rows with empty `distTags={}` → after backfill: `distTags={"latest":"<currentVersion>"}`; Skills already having non-empty distTags are unchanged
- **Threshold**: Exact JSON shape; idempotency: Skill with pre-existing non-empty distTags is skipped
- **Result**: [ ] PENDING

### R-013: Backfill idempotent — second run writes zero rows [blocking]
- **Source**: AC-US4-03
- **Evaluator**: sw:grill
- **Verify**: Integration test — run backfill twice on same data snapshot; second run response shows `updated=0`, `skipped=total`; all column values byte-identical after both runs
- **Threshold**: `updated=0` on second run; no errors; no changed values
- **Result**: [ ] PENDING

### R-014: Historical treeHash fallback = contentHash with bumpSource flag [blocking]
- **Source**: AC-US4-04
- **Evaluator**: sw:grill
- **Verify**: Integration test — SkillVersion with `contentHash="abc123"` and no reachable scripts snapshot → backfill sets `treeHash="abc123"` and `bumpSource="legacy-backfill"`
- **Threshold**: Exact value equality; `bumpSource` correctly flags imprecise hash for Phase 2 consumers
- **Result**: [ ] PENDING

### R-015: Backfill endpoint returns 401 without internal auth [blocking]
- **Source**: AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: Integration test — `POST /api/v1/admin/backfill-versions` without `X-Internal-Key` header → HTTP 401 (or 403 per `hasInternalAuth` semantics); zero DB rows modified
- **Threshold**: Status code is 401 or 403; no writes occur
- **Result**: [ ] PENDING

### R-016: Schema migration is additive-only (no DROP, no NOT NULL on existing) [blocking]
- **Source**: AC-US5-01
- **Evaluator**: human
- **Verify**: Review generated `prisma/migrations/{ts}_versioning_v2_phase1/migration.sql` — confirm: only `ADD COLUMN`, `CREATE TABLE`, `CREATE INDEX` statements present; zero `DROP COLUMN`, zero `DROP TABLE`, zero `ALTER COLUMN ... NOT NULL` against existing columns; `versioningMode` default `"auto"` present; nullable columns have no forced defaults
- **Threshold**: SQL review passes with zero forbidden statement types; reviewed and signed off before `prisma migrate deploy` in staging
- **Result**: [ ] PENDING

### R-017: Migration preserves all existing row counts [blocking]
- **Source**: AC-US5-02
- **Evaluator**: sw:grill
- **Verify**: Apply migration to seeded test Postgres DB; `SELECT COUNT(*) FROM "Skill"` and `SELECT COUNT(*) FROM "SkillVersion"` before and after migration; counts match
- **Threshold**: N = N; M = M (exact equality, no rows lost or created by migration)
- **Result**: [ ] PENDING

### R-018: DistTagEvent model has correct index [blocking]
- **Source**: AC-US5-03
- **Evaluator**: sw:grill
- **Verify**: Prisma schema assertion test — `DistTagEvent` model present with fields `id`, `skillId`, `tag`, `version`, `actor`, `createdAt`; `@@index([skillId, tag, createdAt(sort: Desc)])` defined; migration SQL contains corresponding `CREATE INDEX`
- **Threshold**: All 6 fields present; index declaration matches spec exactly
- **Result**: [ ] PENDING

### R-019: Post-migration auto-mode publish behavior observationally identical [blocking]
- **Source**: AC-US5-04
- **Evaluator**: sw:grill
- **Verify**: E2E test `skill-versioning.spec.ts` — submit with default versioningMode (no flag set); published version value, response shape, and HTTP status match pre-migration behavior; `treeHash` and `publishedBy` are the only newly-populated additive columns
- **Threshold**: Playwright assertions pass; no HTTP 4xx/5xx on any previously-working publish path
- **Result**: [ ] PENDING

---

## Infrastructure Criteria

### R-020: Unit test coverage on new code >= 95% [blocking]
- **Source**: spec.md coverage_target
- **Evaluator**: sw:grill
- **Verify**: Run `npx vitest run --coverage` on `src/lib/integrity/semver.ts`, `src/lib/integrity/tree-hash.ts`, `src/lib/frontmatter-parser.ts`, `src/lib/integrity/errors.ts`; check line coverage
- **Threshold**: >= 95% line coverage on all four new files
- **Result**: [ ] PENDING

### R-021: Modified publish.ts branch coverage = 100% [blocking]
- **Source**: plan.md §10 coverage targets
- **Evaluator**: sw:grill
- **Verify**: Coverage report shows 100% branch coverage on the `versioningMode` switch in `publish.ts` — both `auto` and `author` paths exercised; all 3 author-mode rejection paths (accept, duplicate, backward) exercised
- **Threshold**: 100% branch coverage on the modified `publish.ts` lines
- **Result**: [ ] PENDING

### R-022: Zero new npm production deps added [advisory]
- **Source**: ADR-004, ADR-006 (no `semver`, no `js-yaml`, no `gray-matter`)
- **Evaluator**: sw:grill
- **Verify**: `git diff package.json` — `dependencies` section has no new entries; only `devDependencies` changes (if any) are allowed
- **Threshold**: Zero new entries in `dependencies` block
- **Result**: [ ] PENDING

### R-023: Workers bundle delta <= 8KB min+gz [blocking]
- **Source**: plan.md §7 non-functional requirements
- **Evaluator**: human
- **Verify**: Run `wrangler deploy --dry-run` before and after Phase 1 changes; compare bundle sizes
- **Threshold**: Delta <= 8KB min+gz; total bundle stays under 1MB Cloudflare limit
- **Result**: [ ] PENDING

### R-024: FOR UPDATE transaction prevents duplicate version rows under concurrency [blocking]
- **Source**: ADR-003, plan.md §10 integration test
- **Evaluator**: sw:grill
- **Verify**: Integration test — 50 concurrent `publishSkill()` calls to same skill with same declared version; assert exactly 1 SkillVersion row created; zero `(skillId, version)` duplicates; all others receive `MonotonicityError 409`
- **Threshold**: Exactly 1 success; N-1 rejections; zero duplicate rows in DB
- **Result**: [ ] PENDING

### R-025: Playwright E2E passes end-to-end [blocking]
- **Source**: plan.md §10 E2E test
- **Evaluator**: sw:grill
- **Verify**: `npx playwright test tests/e2e/skill-versioning.spec.ts` passes all 4 scenarios: initial publish → version 1.0.0; second publish → version 1.0.1 with diffSummary; versions page renders both rows; diff endpoint returns contentDiff
- **Threshold**: All Playwright assertions green; no timeouts on the 30s poll
- **Result**: [ ] PENDING
