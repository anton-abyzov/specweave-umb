---
increment: 0680-registry-versioning-v2-phase1
title: "Registry Versioning v2 — Phase 1 (server-side author-declared SemVer)"
project: vskill-platform
test_mode: TDD
tdd_enforcement: strict
---

# Tasks: Registry Versioning v2 — Phase 1

## Execution Order + Parallelism

```
Phase A (no deps — all can run in parallel):
  T-001 → T-002   Schema migration RED → GREEN
  T-003 → T-004   Inline SemVer parser RED → GREEN
  T-005 → T-006   Frontmatter parser RED → GREEN
  T-007 → T-008   Tree-hash module RED → GREEN

Phase B (depends on Phase A):
  T-009            Regression guard baseline check (needs T-004, T-006, T-008, T-002)
  T-010            Author mode accept — RED (needs T-004, T-006, T-008)
  T-011            Duplicate rejection — RED (needs T-004)
  T-012            Backward version rejection — RED (needs T-004)
  T-013            GREEN: publish.ts branch (needs T-009..T-012)

Phase C (depends on T-013):
  T-014 → T-015   Tree-hash supply-chain gap RED → GREEN
  T-016 → T-018   Publisher attribution RED → GREEN (can parallel with T-014..T-015)

Phase D (depends on T-002 + T-004):
  T-019..T-024 → T-025   Backfill endpoint RED → GREEN

Phase E (depends on all phases):
  T-026   Playwright E2E
  T-027   Full vitest regression sweep
  T-028   Migration safety row-count check
```

AC coverage map:
  US-001: T-009, T-010, T-011, T-012, T-013
  US-002: T-007, T-008, T-014, T-015
  US-003: T-016, T-017, T-018
  US-004: T-019, T-020, T-021, T-022, T-023, T-024, T-025
  US-005: T-001, T-002, T-027, T-028

---

## US-005: Additive Schema Evolution with Migration Safety

### T-001: RED — Failing schema shape assertion test
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-03 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `prisma/schema.prisma` does not yet contain the new versioning fields → When Vitest runs `src/lib/__tests__/schema-versioning-v2.test.ts` (new) which uses `fs.readFileSync("prisma/schema.prisma")` to assert presence of: `versioningMode`, `distTags`, `latestStable` on Skill; `major`, `minor`, `patch`, `prerelease`, `buildMetadata`, `treeHash`, `manifest`, `releaseNotes`, `declaredBump`, `bumpSource`, `yanked`, `yankedAt`, `yankReason`, `deprecated`, `deprecationMsg`, `publishedBy`, `immutable` on SkillVersion; model `DistTagEvent`; `@@index([skillId, tag, createdAt(sort: Desc)])` → Then all assertions fail (module content does not contain these tokens)
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/schema-versioning-v2.test.ts` (new — static schema assertion)

---

### T-002: GREEN — Write Prisma schema additions + generate migration
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given the failing T-001 schema test → When `prisma/schema.prisma` is extended with all additive fields per plan.md §3 (Skill: `versioningMode String @default("auto")`, `distTags Json @default("{}")`, `latestStable String?`; SkillVersion: 14 new nullable/defaulted columns; new `DistTagEvent` model with uuid id, skillId, tag, version, actor, createdAt, and `@@index([skillId, tag, createdAt(sort: Desc)])`; two new SkillVersion composite indexes) and `npx prisma migrate dev --create-only` generates the migration SQL → Then T-001 passes; the migration SQL contains only `ADD COLUMN`, `CREATE TABLE`, `CREATE INDEX` statements (zero `DROP`, zero `ALTER COLUMN ... NOT NULL` against existing columns); migration applies cleanly
**Files**: `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma`, `repositories/anton-abyzov/vskill-platform/prisma/migrations/{ts}_versioning_v2_phase1/migration.sql` (new)
**Notes**: Review migration SQL before applying. `versioningMode` default `"auto"`. `yanked`/`deprecated`/`immutable` have boolean defaults. All other new SkillVersion columns nullable without default.

---

## US-002: Server-side treeHash Parity with CLI

### T-003: RED — Failing SemVer 2.0 parser tests
**User Story**: US-001, US-002 | **AC**: AC-US2-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `src/lib/integrity/semver.ts` does not exist → When Vitest runs `src/lib/integrity/__tests__/semver.test.ts` with: `parseSemver("1.2.3-beta.1+build.1")` expected to return structured object; `compareSemver("1.0.0-alpha","1.0.0")` expected `-1`; `compareSemver("1.0.0","1.0.0")` expected `0`; `compareSemver("2.0.0","1.9.9")` expected `1`; full pre-release ordering chain (alpha < alpha.1 < beta.2 < rc.1 < release); build metadata ignored; `isValidSemver("not-semver")` returns false; ~30-case SemVer 2.0 conformance fixture → Then all tests fail with module-not-found
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/integrity/__tests__/semver.test.ts` (new), `repositories/anton-abyzov/vskill-platform/src/lib/integrity/semver.ts` (placeholder stub)

---

### T-004: GREEN — Implement inline SemVer 2.0 parser (~40 LOC)
**User Story**: US-001, US-002 | **AC**: AC-US2-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given failing T-003 tests → When `src/lib/integrity/semver.ts` is implemented per ADR-004 (no `semver` npm; ~40 LOC; exports `parseSemver()`, `compareSemver()`, `isValidSemver()` matching SemVer 2.0 §§9-11) → Then all T-003 tests pass: pre-release identifiers compare correctly (numeric < alphanumeric; fewer identifiers < more when prefix matches); build metadata entirely ignored; `ParsedVersion` interface includes `{ major, minor, patch, prerelease, buildMetadata, raw }`
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/integrity/semver.ts` (new)
**Notes**: Zero new npm deps per ADR-004. API names match `semver` npm for easy Phase 2 swap.

---

### T-005: RED — Failing frontmatter parser tests
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-05 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `src/lib/frontmatter-parser.ts` does not exist → When Vitest runs `src/lib/__tests__/frontmatter-parser.test.ts` asserting: `"---\nversion: 1.2.0\n---\n# Body"` returns `{version:"1.2.0"}`; no frontmatter block returns `{}`; `version: not-semver` returns `{}` (version omitted); frontmatter block >4KB returns `{}`; CRLF in frontmatter handled; unknown fields silently ignored; `version: !!js/function 'return 7'` returns `{}`; `name:` capped at 80 chars; `description:` capped at 500 chars → Then all tests fail with module-not-found
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/frontmatter-parser.test.ts` (new), `repositories/anton-abyzov/vskill-platform/src/lib/frontmatter-parser.ts` (placeholder stub)

---

### T-006: GREEN — Implement inline regex frontmatter parser
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-05 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given failing T-005 tests → When `src/lib/frontmatter-parser.ts` is implemented per ADR-006 (inline regex, no `js-yaml`, allowlist: `version`, `name`, `description`; 4KB hard cap; `isValidSemver()` guard on version; never throws; unknown fields silently dropped) → Then all T-005 tests pass; YAML tag injection `version: !!js/function` returns `{}`; `parseFrontmatter` export matches interface `ParsedFrontmatter { version?, name?, description? }`
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/frontmatter-parser.ts` (new)
**Notes**: Zero new npm deps per ADR-006. Calls `isValidSemver()` from `src/lib/integrity/semver.ts`.

---

### T-007: RED — Failing tree-hash unit + contract tests
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `src/lib/integrity/tree-hash.ts` does not exist → When Vitest runs `src/lib/integrity/__tests__/tree-hash.test.ts` (3-file fixture: SKILL.md, scripts/a.sh, references/guide.md; expected 64-char hex; sort is lexicographic case-sensitive; CRLF→LF before hash; BOM stripped; single-file stable; empty map returns deterministic value) AND `src/lib/integrity/__tests__/tree-hash-contract.test.ts` (fixture hash must exactly match precomputed CLI-side hex from `source-fetcher.ts:47-60`) → Then all tests fail with module-not-found
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/integrity/__tests__/tree-hash.test.ts` (new), `repositories/anton-abyzov/vskill-platform/src/lib/integrity/__tests__/tree-hash-contract.test.ts` (new), `repositories/anton-abyzov/vskill-platform/src/lib/integrity/tree-hash.ts` (placeholder), `repositories/anton-abyzov/vskill-platform/src/lib/integrity/__fixtures__/three-file-skill/` (new fixture directory with 3 small files)
**Notes**: Derive precomputed CLI hex by running `computeSha()` from `repositories/anton-abyzov/vskill/src/updater/source-fetcher.ts:47-60` against the fixture before writing the contract test. Hardcode the expected hex as a string literal.

---

### T-008: GREEN — Port tree-hash algorithm from CLI (10-line copy per ADR-002)
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given failing T-007 tests → When `src/lib/integrity/tree-hash.ts` is implemented as a copy of `source-fetcher.ts:47-60`: sort `Object.keys(files)` lexicographically, concat `path + "\0" + normalizeContent(content) + "\n"` per file, SHA-256 via `node:crypto`, 64-char lowercase hex; `normalizeContent` strips leading `\uFEFF` BOM, replaces `\r\n` with `\n` → Then all T-007 unit tests pass AND the contract test byte-matches the precomputed CLI hex; `computeTreeHash(files: Record<string, string>): string` is the exported signature
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/integrity/tree-hash.ts` (new)
**Notes**: Add pointer comment referencing `repositories/anton-abyzov/vskill/src/updater/source-fetcher.ts:47-60`. Uses `node:crypto` (available in Cloudflare Workers via `@cloudflare/unenv-preset`). Zero new npm deps.

---

## US-001: Server Frontmatter-Aware Publish with versioningMode Flag

### T-009: RED — Baseline regression guard: 9/9 existing tests pass before modifications
**User Story**: US-001 | **AC**: AC-US1-01 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `src/lib/__tests__/skill-version-creation.test.ts` exists with 9 tests covering the auto-patch-bump path → When `npx vitest run src/lib/__tests__/skill-version-creation.test.ts` is run against the unmodified `publish.ts` → Then all 9 pass (baseline confirmed); this file is NOT modified during this increment; this result is the reference for the regression guard that must still hold after T-013
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-version-creation.test.ts` (read-only)
**Notes**: Record the 9/9 output before any publish.ts changes. Run again after T-013 to confirm no regression.

---

### T-010: RED — Failing test: author mode accepts valid declared version
**User Story**: US-001 | **AC**: AC-US1-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a new file `src/lib/__tests__/skill-version-author-mode.test.ts` using the hoisted `mockDb` pattern from `skill-version-creation.test.ts`; skill mock has `versioningMode="author"`; `parseFrontmatter` mock returns `{version:"1.2.0"}`; latest SkillVersion mock is `version="1.1.5"`; `computeTreeHash` mock returns a fixed hex string → When the test calls `publishSkill()` → Then the test currently FAILS (RED) because the author-mode branch does not exist in publish.ts; the expected outcome (once GREEN) is: `skillVersion.create` called with `version="1.2.0"`, `major=1`, `minor=2`, `patch=0`, `bumpSource="frontmatter"`
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-version-author-mode.test.ts` (new)

---

### T-011: RED — Failing test: duplicate version rejected with 409 version_duplicate
**User Story**: US-001 | **AC**: AC-US1-03 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a test case in `skill-version-author-mode.test.ts`; skill has `versioningMode="author"`; latest SkillVersion mock is `version="1.2.0"`; frontmatter declares `version: 1.2.0` (same) → When `publishSkill()` is called → Then currently FAILS (RED); expected: `MonotonicityError` thrown with `statusCode=409`, `code="version_duplicate"`, `declared="1.2.0"`, `latest="1.2.0"`; `skillVersion.create` NOT called; `$transaction` rolls back
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-version-author-mode.test.ts` (extend)

---

### T-012: RED — Failing test: backward version rejected with 409 version_not_monotonic
**User Story**: US-001 | **AC**: AC-US1-04 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a test case in `skill-version-author-mode.test.ts`; skill has `versioningMode="author"`; latest SkillVersion mock is `version="1.0.0"`; frontmatter declares `version: 0.9.0` → When `publishSkill()` is called → Then currently FAILS (RED); expected: `MonotonicityError` thrown with `code="version_not_monotonic"`, `declared="0.9.0"`, `latest="1.0.0"`; no row created
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-version-author-mode.test.ts` (extend)

---

### T-013: GREEN — Implement versioningMode branch in publish.ts
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given all RED tests in T-010, T-011, T-012 are failing and T-009 baseline is 9/9 → When `publish.ts:210-284` is modified to: (1) create `src/lib/integrity/errors.ts` with `MonotonicityError extends Error` carrying `{statusCode:409, code, declared, latest}`; (2) branch on `skill.versioningMode` at the version-computation site (line ~231); (3) `"auto"` branch: existing code verbatim — zero behavior change; (4) `"author"` branch: call `parseFrontmatter()`, extract declared version, call `compareSemver()`, throw `MonotonicityError` on equal (version_duplicate) or less (version_not_monotonic); (5) wrap transaction with `SELECT id FROM "Skill" WHERE id=? FOR UPDATE` per ADR-003; (6) populate `major/minor/patch/prerelease/buildMetadata` from `parseSemver()` on new row; (7) if `versioningMode="author"` but frontmatter has no valid version: fall back to auto-patch-bump path, set `bumpSource="auto-patch"` (AC-US1-05) → Then T-010, T-011, T-012 pass; T-009 still 9/9 (regression holds); AC-US1-05 fallback test also passes
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts`, `repositories/anton-abyzov/vskill-platform/src/lib/integrity/errors.ts` (new)
**Notes**: The error response shape per ADR-003: `{error, declared, latest, skillId, hint}`. API layer catches `MonotonicityError` and serializes to HTTP 409. Any other throw becomes 500.

---

## US-002: Supply-Chain Gap Closed — treeHash Covers All Files

### T-014: RED — Failing test: same SKILL.md + different scripts/ produces different treeHash
**User Story**: US-002 | **AC**: AC-US2-01 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a new test `src/lib/__tests__/tree-hash-publish.test.ts`; Submission A: `SKILL.md="# v1"` + `scripts/run.sh="echo hello"`; Submission B: `SKILL.md="# v1"` (identical) + `scripts/run.sh="echo world"` (1 char diff); both for the same skill → When both `publishSkill()` calls are simulated with mocked DB → Then test currently FAILS (RED) because `treeHash` is not yet threaded into publish.ts; expected: `skillVersion.create` called with different `treeHash` values for A and B
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/tree-hash-publish.test.ts` (new)

---

### T-015: GREEN — Thread treeHash into publish.ts alongside contentHash
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02, AC-US2-03 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given failing T-014 test → When `publish.ts` is extended to: collect all skill files from the submission scan into `Record<string,string>` (SKILL.md + scripts/** + references/**); call `computeTreeHash(files)` before the transaction; pass `treeHash` into `skillVersion.create` data → Then T-014 passes (scripts/ mutation produces different hash); T-009 regression guard still 9/9; `treeHash` populated under both `auto` and `author` modes; AC-US5-04 (behavior otherwise identical) confirmed
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts`

---

## US-003: Publisher Attribution on Every New Version Row

### T-016: RED — Failing test: publishedBy populated from submission.userId
**User Story**: US-003 | **AC**: AC-US3-01 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a test case added to `skill-version-author-mode.test.ts`; submission mock has `userId="user_abc123"` (matches `kv-store.ts:69` payload shape); skill uses either `versioningMode` → When `publishSkill()` is called → Then test currently FAILS (RED) because `publishedBy` is not yet set in publish.ts; expected: `skillVersion.create` receives `publishedBy="user_abc123"`
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-version-author-mode.test.ts` (extend)

---

### T-017: RED — Failing test: null userId causes server validation error (no anonymous publishes)
**User Story**: US-003 | **AC**: AC-US3-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a test case where submission mock has `userId=null` → When `publishSkill()` is called → Then test currently FAILS (RED); expected: a server-side validation error is thrown before the transaction; `skillVersion.create` NOT called; no partial row written; the error is not a `MonotonicityError` (distinct type)
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-version-author-mode.test.ts` (extend)

---

### T-018: GREEN — Populate publishedBy in publish.ts
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given failing T-016 and T-017 tests → When `publish.ts` is extended to: (1) read `submission.userId`; (2) guard: if null/undefined, throw `MissingAttributionError` before the transaction; (3) pass `publishedBy: submission.userId` into `skillVersion.create` → Then T-016 and T-017 pass; T-009 9/9 regression guard holds; `publishedBy` is null only on backfill rows (where `bumpSource="legacy-backfill"`)
**Files**: `repositories/anton-abyzov/vskill-platform/src/lib/submission/publish.ts`

---

## US-004: Admin Backfill Endpoint for Historical Version Rows

### T-019: RED — Failing test: backfill returns 401 without internal auth
**User Story**: US-004 | **AC**: AC-US4-05 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `src/app/api/v1/admin/backfill-versions/route.ts` does not exist → When a new test in `src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` calls `POST /api/v1/admin/backfill-versions` without a valid `X-Internal-Key` header → Then test fails with module-not-found (RED); expected behavior once GREEN: HTTP 401/403 response, zero DB rows modified
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` (new), `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/route.ts` (placeholder stub)

---

### T-020: RED — Failing test: dryRun=true reports counts without writing
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given the test file from T-019 extended; mock DB has 5 SkillVersion rows with `major=null`; 3 Skill rows with `distTags={}`; valid `X-Internal-Key` header present → When `POST /api/v1/admin/backfill-versions?dryRun=true` → Then test currently FAILS (RED); expected: response `{dryRun:true, scanned:5, updated:5, skipped:0, errors:[]}` AND zero Prisma `update` calls made
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` (extend)

---

### T-021: RED — Failing test: major/minor/patch populated from version string
**User Story**: US-004 | **AC**: AC-US4-01 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given test with SkillVersion mocks: `version="1.4.2"` (null major), `version="0.0.1"` (null major), `version="2.0.0-rc.1"` (null major) → When backfill endpoint runs (no dryRun) → Then test currently FAILS (RED); expected: three `skillVersion.update` calls with `{major:1,minor:4,patch:2}`, `{major:0,minor:0,patch:1}`, `{major:2,minor:0,patch:0,prerelease:"rc.1"}` respectively
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` (extend)

---

### T-022: RED — Failing test: distTags initialized on Skill rows
**User Story**: US-004 | **AC**: AC-US4-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given test with 3 Skill mocks: `distTags={}`, `currentVersion="1.4.2"` each → When backfill runs → Then test currently FAILS (RED); expected: `skill.update` called with `distTags:{"latest":"1.4.2"}` for each; Skill rows with non-empty `distTags` are skipped (not updated again)
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` (extend)

---

### T-023: RED — Failing test: idempotent second run writes zero rows
**User Story**: US-004 | **AC**: AC-US4-03 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given test where all SkillVersion rows already have `major != null`, `treeHash != null`, `bumpSource != null`; all Skill rows have non-empty `distTags` → When backfill runs → Then test currently FAILS (RED); expected: `{scanned:N, updated:0, skipped:N, errors:[]}` AND zero Prisma update calls; result is byte-identical to a hypothetical second run
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` (extend)

---

### T-024: RED — Failing test: historical treeHash=contentHash + bumpSource=legacy-backfill
**User Story**: US-004 | **AC**: AC-US4-04 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given test with SkillVersion mock having `contentHash="abc123de"`, no multi-file snapshot reachable → When backfill runs → Then test currently FAILS (RED); expected: `skillVersion.update` called with `treeHash="abc123de"` (fallback = contentHash) AND `bumpSource="legacy-backfill"` per ADR-005 sub-decision (c); imprecision is surfaced via the flag, not hidden
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/__tests__/route.test.ts` (extend)

---

### T-025: GREEN — Implement backfill endpoint
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given all failing T-019..T-024 tests → When `src/app/api/v1/admin/backfill-versions/route.ts` is implemented mirroring `backfill-slugs/route.ts:34-50`: `hasInternalAuth()` first; `?dryRun=true` + `?batch=N` (default 100, clamp 1..500); page SkillVersion rows in batches; skip if `major != null AND treeHash != null AND bumpSource != null`; parse via `parseSemver()`; set `treeHash=contentHash` + `bumpSource="legacy-backfill"` for historical rows; skip on parse failure (add to `errors[]`); for Skills: skip if `distTags` non-empty else set `{"latest": currentVersion}`; return `{dryRun, scanned, updated, skipped, errors}` → Then T-019..T-024 all pass
**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versions/route.ts` (new)

---

## US-001 + US-005: E2E and Regression Safety

### T-026: RED+GREEN — Playwright E2E: full auto-mode versioning flow
**User Story**: US-001, US-005 | **AC**: AC-US1-01, AC-US5-04 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given `tests/e2e/skill-versioning.spec.ts` does not exist → When the Playwright test is created and run against a running vskill-platform instance → Then: (1) submit seed repo with SKILL.md body `"# Test v1"` → poll until PUBLISHED (max 30s) → `GET /api/v1/skills/{owner}/{repo}/{skill}/versions` returns 1 row with `version="1.0.0"`; (2) submit again with `"# Test v1\nNEW LINE"` → poll until PUBLISHED → new row `version="1.0.1"`, `diffSummary` contains `"+1"`; (3) navigate `/skills/{owner}/{repo}/{skill}/versions` → both rows render with correct version strings and timestamps; (4) `GET /versions/diff?from=1.0.0&to=1.0.1` → `contentDiff` contains `"+NEW LINE"`; all assertions pass proving `versioningMode="auto"` default is unchanged post-Phase-1
**Files**: `repositories/anton-abyzov/vskill-platform/tests/e2e/skill-versioning.spec.ts` (new)
**Notes**: RED+GREEN combined — test and its passing are the same deliverable. Reuses existing Playwright config and auth helpers from `tests/e2e/`. No author-mode flag set — this is the regression guard proving default auto behavior unchanged.

---

### T-027: Full Vitest regression sweep
**User Story**: US-005 | **AC**: AC-US5-04 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given all source changes from T-002..T-025 are in place → When `npx vitest run` is executed across the full test suite in `repositories/anton-abyzov/vskill-platform/` → Then zero previously-passing tests regress; `skill-version-creation.test.ts` 9/9; `skill-version-content.test.ts` 3/3; all new suites pass; any failure is a blocker that must be resolved before T-028
**Files**: no file changes — verification step only

---

### T-028: Migration safety — row counts identical before/after
**User Story**: US-005 | **AC**: AC-US5-02 | **Project**: vskill-platform | **Status**: [x]
**Test Plan**: Given a seeded test Postgres DB (Docker) with N Skill rows and M SkillVersion rows, and the migration SQL from T-002 → When `npx prisma migrate deploy` is executed against the test DB → Then `SELECT COUNT(*) FROM "Skill"` returns N (unchanged) AND `SELECT COUNT(*) FROM "SkillVersion"` returns M (unchanged); exit code 0; zero rows created, zero rows dropped; confirms AC-US5-02 additive-only guarantee
**Files**: no source changes — verification step
**Notes**: Use `docker compose up -d postgres` + `DATABASE_URL=...` env. Document row counts as a comment in the migration SQL file.
