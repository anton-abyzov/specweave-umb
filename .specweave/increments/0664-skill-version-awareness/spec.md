---
increment: 0664-skill-version-awareness
title: 'Skill Version Management - Phase 1: Know What You Have'
type: feature
priority: P1
status: completed
created: 2026-04-14T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Version Management - Phase 1: Know What You Have

## Problem Statement

Users have no way to know whether their installed skills are outdated. The `vskill update` command blindly re-fetches every skill without telling users what changed or whether updates are available. There is no `vskill outdated` equivalent (like `npm outdated`), no post-install hint when a newer version exists, and Studio shows no version status for installed skills. Users discover they are behind only when they notice missing functionality.

## Goals

- Let users see which installed skills have newer versions available via a single CLI command
- Provide a batch check-updates API endpoint so the CLI can compare all installed versions in one round trip
- Show a throttled post-install hint when other installed skills have updates available
- Display version badges in the Studio eval-ui so users see latest version at a glance

## User Stories

### US-001: Batch Check-Updates API Endpoint (P1)
**Project**: vskill-platform
**As a** vskill CLI consumer
**I want** a single API endpoint that accepts a list of skill names with their installed versions and returns which ones have updates available
**So that** the CLI can determine outdated skills in one request instead of N individual calls

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a POST request to `/api/v1/skills/check-updates` with body `{"skills": [{"name": "owner/repo/skill", "currentVersion": "1.0.0"}]}`, when the latest published version is "1.0.2", then the response includes `{"updates": [{"name": "owner/repo/skill", "hasUpdate": true, "currentVersion": "1.0.0", "latestVersion": "1.0.2", "versionBump": "patch", "diffSummary": "...", "certTier": "CERTIFIED", "certScore": 95}]}`
- [x] **AC-US1-02**: Given a POST request with an optional `sha` field `{"skills": [{"name": "owner/repo/skill", "currentVersion": "1.0.0", "sha": "abc123"}]}`, when the sha matches the latest version's gitSha, then `hasUpdate` is `false` even if version strings differ
- [x] **AC-US1-03**: Given a POST request with a skill name that does not exist in the registry, when the endpoint processes the request, then that skill entry has `"latestVersion": null` and `"hasUpdate": false`
- [x] **AC-US1-04**: Given a POST request with an empty `skills` array, when the endpoint processes the request, then it returns HTTP 200 with an empty `updates` array
- [x] **AC-US1-05**: Given a POST request with more than 100 skills, when the endpoint processes the request, then it returns HTTP 400 with error `"Maximum 100 skills per request"`
- [x] **AC-US1-06**: Given the endpoint is public (no auth required), when a response is returned, then it is cached in KV with a TTL appropriate for version freshness (e.g., 5 minutes)
- [x] **AC-US1-07**: Given the same client IP makes more than 60 requests in one hour, when the next request arrives, then it returns HTTP 429 with a `Retry-After` header

---

### US-002: vskill outdated Command (P1)
**Project**: vskill
**As a** skill user
**I want** to run `vskill outdated` and see a table of installed skills that have newer versions on the registry
**So that** I know what to update without running `vskill update` blindly

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given skills are installed in `vskill.lock`, when running `vskill outdated`, then it reads all `SkillLockEntry` records, extracts name and version, and calls the batch check-updates API in a single POST request
- [x] **AC-US2-02**: Given 3 of 10 installed skills have updates available, when the command completes, then it prints a table with columns: `Skill | Installed | Latest | Bump | Tier` showing only the 3 outdated skills
- [x] **AC-US2-03**: Given no installed skills have updates available, when running `vskill outdated`, then it prints "All skills are up to date." and exits with code 0
- [x] **AC-US2-04**: Given the API is unreachable or returns an error, when running `vskill outdated`, then it prints a warning message to stderr and exits with code 1 without crashing
- [x] **AC-US2-05**: Given `vskill outdated --json` is invoked, when the command completes, then it outputs the full `updates` array from the API response as JSON to stdout (no table formatting)
- [x] **AC-US2-06**: Given no skills are installed (empty lockfile or no lockfile), when running `vskill outdated`, then it prints "No skills installed." and exits with code 0

---

### US-003: Post-Install Update Hint (P1)
**Project**: vskill
**As a** skill user
**I want** to see a hint after `vskill install` if other installed skills have updates available
**So that** I am reminded to check for updates periodically without being nagged on every install

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the last update check was more than 24 hours ago (or never performed), when a `vskill install` completes successfully and N skills have updates, then a hint line is printed after the install summary: `N skill(s) have updates available. Run \`vskill outdated\` to see them.`
- [x] **AC-US3-02**: Given the last update check was less than 24 hours ago, when `vskill install` completes, then no update hint is shown regardless of available updates
- [x] **AC-US3-03**: Given the update check is performed and completes, when the hint is shown (or suppressed), then `lastUpdateCheck` timestamp is written to `vskill.lock` to throttle future checks
- [x] **AC-US3-04**: Given the version check fails (network error, API down, timeout), when `vskill install` completes, then the hint is silently skipped — install is never blocked or delayed by the hint
- [x] **AC-US3-05**: Given the skill being installed is the only skill in the lockfile, when `vskill install` completes, then no hint is shown (nothing else to check)

---

### US-004: Studio Version Badge on SkillCard (P2)
**Project**: vskill
**As a** Studio user viewing installed skills
**I want** to see a version badge indicating if an update is available
**So that** I can identify which skills need updating from the Studio web UI

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the eval-server is running, when `GET /api/skills/updates` is called, then it executes `vskill outdated --json` internally and returns the parsed JSON result
- [x] **AC-US4-02**: Given the `SkillInfo` type in `eval-ui/src/types.ts`, when the type is extended, then it includes optional fields: `updateAvailable?: boolean`, `currentVersion?: string`, `latestVersion?: string`
- [x] **AC-US4-03**: Given a skill has `updateAvailable: true`, when the SkillCard renders, then it shows a yellow pill badge with an up-arrow icon displaying the latest version number
- [x] **AC-US4-04**: Given a skill has `updateAvailable: false` or the field is absent, when the SkillCard renders, then no update badge is shown
- [x] **AC-US4-05**: Given the eval-server `/api/skills/updates` call fails or times out, when the Studio loads, then skill cards render normally without version badges (graceful degradation)

## Out of Scope

- Automatic background update checks (Phase 2)
- `vskill update --interactive` with per-skill selection (Phase 2)
- Breaking change detection between versions (Phase 2)
- Version pinning in vskill.lock (Phase 2)
- Changelog generation between versions (Phase 2)
- Push notifications for new versions (Phase 2)
- Auto-updating skills without user action (Phase 2)

## Non-Functional Requirements

- **Performance**: Batch check-updates endpoint responds in under 500ms for up to 100 skills (p95)
- **Reliability**: Post-install hint never blocks or delays the install flow; failures are silently swallowed
- **Caching**: Batch endpoint responses cached in KV to avoid repeated DB queries for the same skill set
- **Rate Limiting**: 60 requests/hour per IP on the batch endpoint, consistent with existing `applyRateLimit` patterns
- **Compatibility**: Lockfile schema extended only with `lastUpdateCheck` field; all existing fields unchanged

## Edge Cases

- **Skill not in registry**: Locally-installed skills (from GitHub direct) that have no registry entry return `hasUpdate: false, latestVersion: null` — skipped in table output
- **Malformed version strings**: Non-semver versions (e.g., "latest", "dev") treated as not comparable; skipped with a dim warning in CLI output
- **Lock entries without version**: `SkillLockEntry` records lacking a `version` field are excluded from the outdated check
- **Concurrent lockfile access**: Reading lockfile is atomic; writing `lastUpdateCheck` uses the existing lockfile write path
- **Empty lockfile**: `vskill outdated` with no installed skills prints "No skills installed." and exits 0
- **More than 100 installed skills**: CLI batches into multiple requests if needed (unlikely but handled)

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Batch endpoint slow with large skill lists | 0.3 | 4 | 1.2 | Prisma `findMany` with `IN` clause on skill name, index on `name` column, cap at 100 |
| Version comparison edge cases (pre-release, build metadata) | 0.4 | 3 | 1.2 | Use `semver` library for comparison, fall back to string equality |
| Post-install hint adds latency to install flow | 0.2 | 6 | 1.2 | Fire-and-forget async check, never await in critical path |
| KV cache staleness after new version publish | 0.5 | 2 | 1.0 | Short TTL (5 min); acceptable lag for version awareness |

## Technical Notes

### Existing Patterns (from codebase exploration)
- **Lockfile**: `vskill.lock` with `VskillLock` interface — `skills: Record<string, SkillLockEntry>` where entries have `version`, `sha`, `tier`, `source`
- **CLI commands**: Commander.js with dynamic imports in `src/index.ts` — pattern: `program.command("outdated").action(async () => { const { outdatedCommand } = await import("./commands/outdated.js"); ... })`
- **Eval-server routes**: Router class with `registerRoutes()` pattern in `src/eval-server/api-routes.ts`
- **SkillInfo type**: `src/eval-ui/src/types.ts` — extend with version fields
- **Rate limiting**: `applyRateLimit(request, keyPrefix, limit, windowSec)` from `src/lib/rate-limit.ts`
- **KV caching**: Prefix-based keys with TTL, e.g., `skills:check-updates:{hash}`
- **Prisma schema**: `Skill.currentVersion`, `SkillVersion.version/certTier/certScore/diffSummary/versionBump` all available

### Constraints
- Batch endpoint must use POST to avoid URL length limits with many skill names
- Cloudflare Workers environment: `process.env` unavailable, use `env` handler parameter
- Response shape must include all fields needed for both CLI table and Studio badge rendering
- `vskill.lock` write for `lastUpdateCheck` must not conflict with concurrent install operations

### Architecture Decisions
- Single batch endpoint vs individual per-skill checks: batch chosen to avoid N+1 API calls
- Post-install hint checks all other installed skills (not just the one being installed) to maximize value
- Studio badge data flows through eval-server route that shells out to `vskill outdated --json` — reuses CLI logic, no duplication
- API path uses `/skills/check-updates` (not `/packages/`) to align with existing route namespace in the platform

## Success Metrics

- `vskill outdated` is used by 20% of active CLI users within 30 days of release
- Post-install hint leads to 10% increase in `vskill update` command usage
- Batch endpoint p95 latency under 300ms for typical workload (10-30 skills)
