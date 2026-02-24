# 0362: Validate npm Package Ownership

## Problem

Homepage shows 527M npm downloads across 6 "npm packages" — but these are mainstream packages (eslint, sentry, playwright) arbitrarily linked to skills. The `Skill.npmPackage` field has no ownership validation, so any skill can claim any npm package.

## Solution

During enrichment, cross-reference each skill's `npmPackage` against the npm registry's `repository.url` to verify the skill repo actually publishes that package. Only count verified packages in stats.

## User Stories

### US-001: npm Package Ownership Verification
As the platform, I verify that a skill's claimed npm package actually belongs to its repository, so that download stats are accurate.

- [x] **AC-US1-01**: Prisma schema has `npmPackageVerified Boolean @default(false)` on Skill model
- [x] **AC-US1-02**: `normalizeNpmRepoUrl()` handles git+, git://, SSH, github: shorthand formats
- [x] **AC-US1-03**: Enrichment fetches npm registry metadata for unverified skills
- [x] **AC-US1-04**: When npm `repository.url` matches skill `repoUrl`, sets `npmPackageVerified = true`
- [x] **AC-US1-05**: When npm `repository.url` mismatches, clears `npmPackage = null` and `npmDownloads = 0`
- [x] **AC-US1-06**: When npm registry fetch fails, skips verification (no data loss)
- [x] **AC-US1-07**: Already-verified skills skip registry fetch on subsequent cycles
- [x] **AC-US1-08**: Stats queries filter by `npmPackageVerified = true` for npm counts/downloads
- [x] **AC-US1-09**: Admin bulk enrich endpoint also performs verification
- [x] **AC-US1-10**: All existing tests pass, new tests cover verification scenarios
