---
increment: 0664-skill-version-awareness
title: "Skill Version Management - Phase 1: Know What You Have"
status: active
test_mode: TDD
coverage_target: 90
updated: 2026-04-14
---

# Tasks: Skill Version Management - Phase 1

> Dependency order: US-001 (Platform API) → T-006 (API client) → US-002 (CLI outdated) → US-003 (post-install hint) + US-004 (Studio badge)

---

## US-001: Batch Check-Updates API Endpoint

> **Project**: vskill-platform | **File**: `src/app/api/v1/skills/check-updates/route.ts` (new)

### T-001: Create POST /api/v1/skills/check-updates route with core response logic
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed
**Test**: Given a POST to `/api/v1/skills/check-updates` with `{"skills":[{"name":"owner/repo/skill","version":"1.0.0"}]}` where DB has `currentVersion:"1.0.2"` → When the endpoint processes the request → Then HTTP 200 with `{"results":[{"name":"owner/repo/skill","installed":"1.0.0","latest":"1.0.2","updateAvailable":true}]}`; Given an empty `skills` array → When processed → Then HTTP 200 with `{"results":[]}`

---

### T-002: Handle unknown skills (not in registry) returning null latest
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given a POST with `{"name":"owner/repo/missing","version":"1.0.0"}` that has no DB row → When the endpoint processes it → Then the result entry has `{"latest":null,"updateAvailable":false}`; Given a skill where installed version matches `currentVersion` → When processed → Then `updateAvailable` is `false`

---

### T-003: Validate 100-skill hard limit (HTTP 400)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05
**Status**: [x] completed
**Test**: Given a POST body with an array of 101 skill entries → When the endpoint validates the request → Then HTTP 400 with `{"error":"Maximum 100 skills per request"}` and no DB query is executed

---

### T-004: Apply per-IP rate limiting (60 req/hour → HTTP 429)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07
**Status**: [x] completed
**Test**: Given a single client IP that has already made 60 requests within the current hour → When the 61st request arrives → Then HTTP 429 is returned with a `Retry-After` header; Given a fresh IP → When the first request arrives → Then HTTP 200 is returned

---

### T-005: Cache responses in KV with 5-minute TTL
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06
**Status**: [x] completed
**Test**: Given a POST request with a specific skill list → When the same request is made again within 5 minutes → Then the response is served from KV cache (no DB round-trip); Given the TTL expires → When the same request arrives → Then a fresh DB query runs and the cache is refreshed

---

## US-002: vskill outdated Command

> **Project**: vskill | Depends on T-001 through T-005 (API endpoint must exist)

### T-006: Add checkUpdates() function to API client (src/api/client.ts)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 (API bridge)
**Status**: [x] completed
**Test**: Given a `skills` array `[{name:"owner/repo/skill",version:"1.0.0"}]` → When `checkUpdates(skills)` is called with a mocked `apiRequest` returning `{results:[...]}` → Then the function POSTs to `/api/v1/skills/check-updates` and returns the `results` array; Given `apiRequest` throws a network error → When `checkUpdates` is called → Then the error propagates (not swallowed)

---

### T-007: Create src/commands/outdated.ts — read lockfile and build skill list
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-06
**Status**: [x] completed
**Test**: Given a `vskill.lock` with 10 entries each having `name`, `version`, and `source` → When `outdatedCommand()` runs → Then `readLockfile()` is called, `resolveFullName()` is applied per entry, and a single `checkUpdates()` call is made with all 10 resolved names; Given no lockfile or an empty lockfile → When the command runs → Then it prints `"No skills installed."` and exits with code 0

---

### T-008: Render outdated table and "all up to date" message
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given the API returns 3 skills with `updateAvailable:true` out of 10 total → When the command renders output → Then a table with columns `Skill | Installed | Latest | Bump | Tier` lists only the 3 outdated skills and exits with code 1; Given the API returns zero `updateAvailable:true` entries → When the command renders → Then it prints `"All skills are up to date."` and exits with code 0

---

### T-009: Handle API errors and --json flag
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05
**Status**: [x] completed
**Test**: Given the API call throws a network error → When `outdatedCommand()` runs → Then a warning is printed to stderr and the process exits with code 1 without crashing; Given `--json` flag is passed and API returns updates → When the command runs → Then the raw `CheckUpdateResult[]` array is written to stdout with no table formatting

---

### T-010: Register `outdated` command in src/index.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 through AC-US2-06 (CLI entry point)
**Status**: [x] completed
**Test**: Given the built CLI binary → When `vskill outdated` is invoked from the shell → Then the dynamic import loads `outdated.ts` and `outdatedCommand()` executes without an "unknown command" error; Given `vskill outdated --json` → When invoked → Then the `--json` option is parsed and forwarded to `outdatedCommand()`

---

## US-003: Post-Install Update Hint

> **Project**: vskill | **File**: `src/commands/add.ts` | Parallel to US-002 (different file)

### T-011: Emit post-install hint when newer version exists and 24h elapsed
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-05
**Status**: [x] completed
**Test**: Given `lastUpdateCheck` in lockfile is older than 24 hours (or absent) and `getSkill()` returns `registryVersion:"1.0.3"` while `installedVersion` is `"1.0.0"` → When `vskill install <skill>` completes → Then a dim hint line is printed: `"Hint: v1.0.3 available (installed v1.0.0). Run vskill update <name> to update."`; Given the skill being installed is the only skill in the lockfile → When install completes → Then no hint is shown

---

### T-012: Throttle hint with lastUpdateCheck timestamp in lockfile
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03
**Status**: [x] completed
**Test**: Given `lastUpdateCheck` in lockfile is less than 24 hours ago → When `vskill install` completes → Then no hint is printed regardless of available updates; Given the hint fires (or would fire) → When the check completes → Then `lastUpdateCheck` is written to `vskill.lock` via the existing lockfile write path

---

### T-013: Silently skip hint on network/version-check failure
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04
**Status**: [x] completed
**Test**: Given the hint code block throws an exception (simulated network timeout) → When `vskill install` executes the post-install phase → Then the install completes successfully with exit 0, no error is printed to stdout or stderr, and the hint is silently omitted

---

## US-004: Studio Version Badge on SkillCard

> **Project**: vskill (eval-server + eval-ui) | Depends on US-002 (`vskill outdated --json` must be available)

### T-014: Add GET /api/skills/updates route to eval-server
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] completed
**Test**: Given the eval-server is running and `vskill outdated --json` is available → When `GET /api/skills/updates` is called → Then the route shells out to `vskill outdated --json`, parses the JSON output, and returns it as the response body with HTTP 200; Given `vskill outdated` exits non-zero → When the route is called → Then HTTP 200 with an empty array is returned (graceful degradation, not 500)

---

### T-015: Extend SkillInfo type in eval-ui/src/types.ts
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02
**Status**: [x] completed
**Test**: Given the `SkillInfo` interface in `eval-ui/src/types.ts` → When the type is extended → Then it includes the optional fields `updateAvailable?: boolean`, `currentVersion?: string`, and `latestVersion?: string`; Given existing code using `SkillInfo` without the new fields → When TypeScript compiles → Then no type errors occur (all fields are optional)

---

### T-016: Render version badge on SkillCard (present / absent)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04
**Status**: [x] completed
**Test**: Given a `SkillInfo` object with `updateAvailable:true` and `latestVersion:"1.0.3"` → When `SkillCard` renders → Then a yellow pill badge with an up-arrow icon displaying `"1.0.3"` is visible in the rendered output; Given `updateAvailable:false` or the field is absent → When `SkillCard` renders → Then no version badge element is present in the DOM

---

### T-017: Graceful degradation when eval-server updates API fails
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05
**Status**: [x] completed
**Test**: Given the fetch to `/api/skills/updates` in the Studio client fails with a network error or 5xx → When the Studio page loads → Then all `SkillCard` components render normally without badges and no error boundary is triggered; Given the API call times out → When the Studio loads → Then cards are rendered with default state (no badges)

---

## Coverage Summary

| AC ID | Covered By |
|-------|------------|
| AC-US1-01 | T-001 |
| AC-US1-02 | T-002 |
| AC-US1-03 | T-002 |
| AC-US1-04 | T-001 |
| AC-US1-05 | T-003 |
| AC-US1-06 | T-005 |
| AC-US1-07 | T-004 |
| AC-US2-01 | T-006, T-007, T-010 |
| AC-US2-02 | T-008 |
| AC-US2-03 | T-008 |
| AC-US2-04 | T-009 |
| AC-US2-05 | T-009 |
| AC-US2-06 | T-007 |
| AC-US3-01 | T-011 |
| AC-US3-02 | T-012 |
| AC-US3-03 | T-012 |
| AC-US3-04 | T-013 |
| AC-US3-05 | T-011 |
| AC-US4-01 | T-014 |
| AC-US4-02 | T-015 |
| AC-US4-03 | T-016 |
| AC-US4-04 | T-016 |
| AC-US4-05 | T-017 |
