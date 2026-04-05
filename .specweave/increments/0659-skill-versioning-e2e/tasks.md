---
increment: 0659-skill-versioning-e2e
title: "End-to-End Skill Versioning"
status: completed
generated: 2026-04-04
test_mode: TDD
---

# Tasks: End-to-End Skill Versioning

## Coverage Map

| AC-ID | Task(s) |
|-------|---------|
| AC-US1-01 | T-005, T-006 |
| AC-US1-02 | T-005, T-006 |
| AC-US1-03 | T-005, T-006 |
| AC-US1-04 | T-005, T-006 |
| AC-US1-05 | T-005, T-006 |
| AC-US1-06 | T-005, T-006 |
| AC-US2-01 | T-007, T-008 |
| AC-US2-02 | T-007, T-008 |
| AC-US2-03 | T-007, T-008 |
| AC-US2-04 | T-007, T-008 |
| AC-US2-05 | T-007, T-008 |
| AC-US2-06 | T-007, T-008 |
| AC-US3-01 | T-001, T-002 |
| AC-US3-02 | T-003, T-004 |
| AC-US3-03 | T-003, T-004 |
| AC-US3-04 | T-001, T-002 |
| AC-US3-05 | T-001, T-002 |
| AC-US4-01 | T-009, T-010 |
| AC-US4-02 | T-009, T-010 |
| AC-US4-03 | T-011, T-012 |
| AC-US4-04 | T-011, T-012 |

---

## Domain: vskill-platform

### US-003: Persist SKILL.md Content During Scanning

### T-001: [RED] Schema migration tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given the Prisma schema lacks a `content` field on SkillVersion → When the migration `add-skill-version-content` is applied → Then SkillVersion has a nullable `content` Text column, existing rows remain intact, and SkillVersion writes that omit `content` succeed

---

### T-002: [GREEN] Apply schema migration — add content field to SkillVersion
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04, AC-US3-05
**Status**: [x] completed
**Test**: Given T-001 tests are failing → When `content String?` is added to the SkillVersion model in `prisma/schema.prisma` and `npx prisma migrate dev --name add-skill-version-content` runs cleanly → Then the column exists in the database and all T-001 tests pass

---

### T-003: [RED] Scan pipeline KV content-persistence tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given a submission arrives with `repoFiles.skillMd` containing valid SKILL.md text → When `process-submission.ts` executes the Tier 1 scan → Then a KV key `skillmd:{id}` is written with the raw string and a 7-day TTL; when `repoFiles.skillMd` is absent no KV write occurs and processing continues

---

### T-004: [GREEN] Implement KV SKILL.md store in scan pipeline
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given T-003 tests are failing → When a `kvForContent.put('skillmd:{id}', repoFiles.skillMd, { expirationTtl: 604800 })` call is inserted after the `contentHash` computation in `process-submission.ts` → Then the KV write tests pass and the remainder of the scan pipeline is unaffected

---

### US-001: SkillVersion Creation on Publish

### T-005: [RED] publishSkill SkillVersion creation tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06
**Status**: [x] completed
**Test**: Given a skill has zero SkillVersion rows and `skillmd:{id}` is in KV → When `publishSkill()` runs with contentHash X → Then a v1.0.0 SkillVersion is created with content and `diffSummary=null`, `skill.currentVersion` is set to "1.0.0"; a second call with a different hash creates v1.0.1 with a non-null diffSummary; a call with the same hash updates certifiedAt only (no new row); SkillVersion creation failure does not abort publish

---

### T-006: [GREEN] Implement SkillVersion creation in publishSkill
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06
**Status**: [x] completed
**Test**: Given T-005 tests are failing → When the SkillVersion block (read KV content, query latest version, compare contentHash, bump patch or re-cert, create row, update `skill.currentVersion`, delete KV key) is added to `submission-store.ts` after the Skill upsert, wrapped in try/catch → Then all T-005 tests pass

---

### US-002: Version API Endpoints

### T-007: [RED] Version API endpoint tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Status**: [x] completed
**Test**: Given a skill with 3 SkillVersion rows exists → When GET `/api/v1/skills/owner/repo/skill/versions` is called → Then versions are returned sorted by createdAt desc, `content` is excluded, cursor pagination works; GET `.../versions/1.0.1` returns the version with `content`; GET `.../versions/diff?from=1.0.0&to=1.0.1` returns `diffSummary` and `contentDiff`; unknown skill slug returns 404; missing `from`/`to` on diff returns 400

---

### T-008: [GREEN] Implement version list, detail, and diff API routes
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Status**: [x] completed
**Test**: Given T-007 tests are failing → When `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts` (list + diff) and `versions/[version]/route.ts` (detail) are created following the existing skill route pattern with correct Cache-Control headers and error payloads → Then all T-007 tests pass

---

## Domain: vskill (CLI)

### US-004: Fix CLI Version Resolution

### T-009: [RED] fetchGitHubFlat version resolution tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given `fetchGitHubFlat` fetches SKILL.md with `version: 2.1.0` in frontmatter and `entry.version` is `1.0.0` → When `fetchGitHubFlat` resolves the version → Then it returns `"2.1.0"`; given SKILL.md has no version frontmatter field → Then it returns `"1.0.0"` (entry.version fallback)

---

### T-010: [GREEN] Fix fetchGitHubFlat to extract version from frontmatter
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given T-009 tests are failing → When `src/updater/source-fetcher.ts` is updated to call `extractFrontmatterVersion(content)` (imported from `../utils/version.js`) and returns `frontmatterVersion || entry.version` → Then both T-009 test cases pass and the `.js` extension is used per ESM/nodenext config

---

### T-011: [RED] `vskill versions` command tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed
**Test**: Given the platform API returns 3 versions for `owner/repo/skill` → When `vskill versions owner/repo/skill` is run → Then a formatted table of version/certTier/createdAt rows is printed to stdout; given the API returns 404 → Then a clear error message is printed to stderr and the process exits non-zero

---

### T-012: [GREEN] Implement `vskill versions` subcommand
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed
**Test**: Given T-011 tests are failing → When a `versions` subcommand is registered in the vskill CLI that calls GET `/api/v1/skills/:owner/:repo/:skill/versions`, formats the response as a table, and handles 404 with a non-zero exit → Then all T-011 tests pass
