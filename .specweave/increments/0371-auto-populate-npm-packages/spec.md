# 0371: Auto-populate npm packages for skills

## Problem
The dashboard shows "1 npm package" despite 3000+ skills from 3000+ repos. The `npmPackage` field is never auto-populated during the publish pipeline — only manually-seeded skills have it. `package.json` is already fetched during scanning but only used for security analysis.

## User Stories

### US-001: Auto-extract npm package name during publish
As a platform operator, I want npm package names to be automatically extracted from package.json when skills are published, so that npm download metrics are tracked without manual intervention.

**Acceptance Criteria:**
- [x] AC-US1-01: `extractNpmPackageName()` utility extracts `name` from valid package.json
- [x] AC-US1-02: Private packages (`"private": true`) are skipped
- [x] AC-US1-03: Invalid npm names are rejected
- [x] AC-US1-04: `processSubmission` extracts npm name and passes to `publishSkill`
- [x] AC-US1-05: `publishSkill` stores `npmPackage` on the Skill record (unverified)
- [x] AC-US1-06: Existing callers of `publishSkill` (admin approve, restore) continue working

### US-002: Backfill existing skills
As a platform operator, I want to backfill npm package names for all existing skills, so the dashboard shows accurate npm metrics.

**Acceptance Criteria:**
- [x] AC-US2-01: Admin endpoint `/api/v1/admin/npm-backfill` processes skills with null npmPackage
- [x] AC-US2-02: Groups by repoUrl to avoid duplicate GitHub fetches
- [x] AC-US2-03: Supports `?dryRun=true` for preview
- [x] AC-US2-04: Rate-limit aware (batched with pauses)
- [x] AC-US2-05: Auth follows existing pattern (X-Internal-Key or SUPER_ADMIN)
