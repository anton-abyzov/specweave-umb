---
increment: 0659-skill-versioning-e2e
title: End-to-End Skill Versioning
type: feature
priority: P1
status: completed
created: 2026-04-05T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
skill_chain:
  - 'sw:pm'
---

# Feature: End-to-End Skill Versioning

## Overview

All 111K+ published skills are stuck at version 1.0.0. The SkillVersion Prisma model exists but was never wired into the publish pipeline. This increment connects SkillVersion creation to publishSkill(), auto-bumps patch version when SKILL.md content changes, persists SKILL.md content per version in the database, exposes version history via API endpoints, and fixes the CLI version resolution bug.

**Storage decision**: SKILL.md content (5-50KB) stored as a `Text` column on SkillVersion in PostgreSQL (Neon). No R2 or KV needed.

## User Stories

### US-001: SkillVersion Creation on Publish (P1)
**Project**: vskill-platform

**As a** skill author
**I want** a new version record created automatically when I publish a changed skill
**So that** my skill has an auditable version history tied to actual content changes

**Acceptance Criteria**:
- [x] **AC-US1-01**: When publishSkill() runs and no SkillVersion exists for the skill, a v1.0.0 SkillVersion record is created with the current contentHash, gitSha, certTier, certMethod, certScore, and labels
- [x] **AC-US1-02**: When publishSkill() runs and the latest SkillVersion.contentHash differs from the current submission's contentHash, a new SkillVersion is created with the patch version bumped (e.g., 1.0.0 → 1.0.1)
- [x] **AC-US1-03**: When publishSkill() runs and the latest SkillVersion.contentHash matches the current submission's contentHash (re-certification only), no new SkillVersion is created; existing version's certTier/certScore/certifiedAt are updated in place
- [x] **AC-US1-04**: The Skill.currentVersion field is updated to match the newly created SkillVersion's version string
- [x] **AC-US1-05**: A diffSummary is computed and stored on the new SkillVersion describing what changed from the previous version (null for v1.0.0)
- [x] **AC-US1-06**: The SKILL.md content from the scan pipeline is stored on the SkillVersion record's `content` field

---

### US-002: Version API Endpoints (P2)
**Project**: vskill-platform

**As a** skill consumer or platform integrator
**I want** API endpoints to list versions, fetch a specific version, and compare versions
**So that** I can inspect a skill's change history and understand what changed between releases

**Acceptance Criteria**:
- [x] **AC-US2-01**: GET `/api/v1/skills/:owner/:repo/:skill/versions` returns a paginated list of SkillVersion records sorted by createdAt descending, with fields: version, contentHash, certTier, certScore, diffSummary, createdAt
- [x] **AC-US2-02**: Pagination uses cursor-based pagination with `?cursor=<id>&limit=<n>` (default limit 20, max 100)
- [x] **AC-US2-03**: GET `/api/v1/skills/:owner/:repo/:skill/versions/:version` returns a single SkillVersion record including the full SKILL.md `content` field
- [x] **AC-US2-04**: GET `/api/v1/skills/:owner/:repo/:skill/versions/diff?from=X&to=Y` returns a diff object with `from`, `to`, `diffSummary`, and `contentDiff` (unified diff of SKILL.md content between the two versions)
- [x] **AC-US2-05**: All version endpoints return 404 with `{ error: "Skill not found" }` when the skill slug doesn't match any published skill
- [x] **AC-US2-06**: The diff endpoint returns 400 with `{ error: "..." }` when `from` or `to` version is missing or doesn't exist for the skill

---

### US-003: Persist SKILL.md Content During Scanning (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** SKILL.md content captured during Tier 1 scanning to be available at publish time
**So that** SkillVersion records can store content without re-fetching from GitHub

**Acceptance Criteria**:
- [x] **AC-US3-01**: A `content` Text field is added to the SkillVersion Prisma model via migration
- [x] **AC-US3-02**: The process-submission pipeline passes the fetched SKILL.md content string through to publishSkill() so it can be stored on the SkillVersion
- [x] **AC-US3-03**: publishSkill() accepts and stores SKILL.md content on the SkillVersion record
- [x] **AC-US3-04**: The Prisma migration runs cleanly against the existing Neon database with 111K+ skills and zero SkillVersion rows (additive column, no data migration needed)
- [x] **AC-US3-05**: Existing submissions in the pipeline that lack content still publish successfully (content field is nullable, defaults to null)

---

### US-004: Fix CLI Version Resolution (P2)
**Project**: vskill

**As a** skill user running vskill CLI
**I want** accurate version information from installed skills and a command to list available versions
**So that** I can tell which version I have and what versions exist

**Acceptance Criteria**:
- [x] **AC-US4-01**: fetchGitHubFlat() parses the `version` field from SKILL.md frontmatter instead of returning the stale entry.version from the lock file
- [x] **AC-US4-02**: If SKILL.md frontmatter has no `version` field, fetchGitHubFlat() falls back to entry.version (backward compatibility)
- [x] **AC-US4-03**: `vskill versions <owner>/<repo>/<skill>` command lists all published versions by calling GET `/api/v1/skills/:owner/:repo/:skill/versions`, displaying version, certTier, and createdAt in a formatted table
- [x] **AC-US4-04**: `vskill versions <owner>/<repo>/<skill>` returns a clear error message when the skill is not found or has no versions

## Functional Requirements

### FR-001: Version Bump Logic
publishSkill() determines the version bump as follows:
1. Query latest SkillVersion for the skill (ordered by createdAt desc)
2. If none exists → create v1.0.0
3. If latest.contentHash === current contentHash → skip version creation (update cert fields on latest)
4. If hashes differ → bump patch (1.0.0 → 1.0.1), create new SkillVersion

### FR-002: Content Hash Propagation
The contentHash computed in process-submission.ts (SHA-256 of SKILL.md) must be passed through storeScanResult → publishSkill → SkillVersion creation. The existing `contentHashAtScan` field on Submission already carries this value.

### FR-003: Diff Computation
diffSummary is a human-readable string computed by comparing the previous version's content with the new content. If previous content is null (legacy versions pre-content-storage), diffSummary should be "Initial tracked version" or similar.

## Success Criteria

- All newly published skills with changed content get incrementing version numbers
- Re-certifications (same content) do not create spurious versions
- Version history is accessible via API for any published skill
- CLI `vskill versions` command works end-to-end against the API
- Zero regression in existing publish pipeline (111K+ skills unaffected)

## Out of Scope

- Major/minor version bumps (only patch auto-bump in this increment)
- UI for version history browsing (API-only for now)
- Version pinning in vskill install (future increment)
- R2 or KV storage for SKILL.md content (PostgreSQL Text column only)
- Backfilling SkillVersion records for existing 111K skills (future migration)
- Version-specific install (`vskill add skill@1.0.3` syntax)

## Dependencies

- Neon PostgreSQL database accessible for Prisma migration
- Existing Tier 1 scan pipeline (process-submission.ts) functioning
- vskill-platform API deployment infrastructure (Cloudflare Workers)
- vskill CLI release pipeline for publishing updated CLI
