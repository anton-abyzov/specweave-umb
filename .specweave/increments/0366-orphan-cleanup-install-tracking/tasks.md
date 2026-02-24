# Tasks: Orphan cleanup on re-submission + install tracking phone-home

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Orphan Cleanup (Platform)

### US-001: Orphan Skill Cleanup on Re-submission (P1)

#### T-001: Create orphan cleanup module

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04, AC-US1-05 | **Status**: [ ] Not Started

**Description**: Create `src/lib/orphan-cleanup.ts` with a function that deprecates stale Skill records when a skill is being re-submitted.

**Implementation Details**:
- Export `deprecateOrphanSkills(db: PrismaClient, pairs: { repoUrl: string; skillName: string }[]): Promise<number>`
- Use `makeSlug()` from `src/lib/slug.ts` to resolve skill names to slugs
- Query: `db.skill.findMany({ where: { name: { in: slugs }, isDeprecated: false } })` to find active skills
- Update: `db.skill.updateMany({ where: { id: { in: matchedIds } }, data: { isDeprecated: true } })`
- Return the count of deprecated skills
- Idempotent: if no matching non-deprecated skills exist, return 0

**Test Plan**:
- **File**: `src/lib/__tests__/orphan-cleanup.test.ts`
- **Tests**:
  - **TC-001**: deprecates matching non-deprecated Skill records
    - Given a Skill with `name: "my-skill"` and `isDeprecated: false`
    - When `deprecateOrphanSkills` is called with `[{ repoUrl: "https://github.com/org/repo", skillName: "My Skill" }]`
    - Then `updateMany` is called with `isDeprecated: true` for that skill's ID
  - **TC-002**: skips already-deprecated skills
    - Given a Skill with `isDeprecated: true`
    - When `deprecateOrphanSkills` is called
    - Then `updateMany` is not called (or called with empty array)
  - **TC-003**: handles empty input array
    - Given empty pairs array
    - When `deprecateOrphanSkills` is called
    - Then returns 0 and no DB queries are made
  - **TC-004**: handles batch of multiple skills
    - Given 3 pairs, 2 of which match existing skills
    - When `deprecateOrphanSkills` is called
    - Then only the 2 matching skills are deprecated

**Dependencies**: None
**Status**: [ ] Not Started

---

#### T-002: Integrate orphan cleanup into submission route

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-03 | **Status**: [ ] Not Started

**Description**: Call `deprecateOrphanSkills()` inside `POST /api/v1/submissions` for both single-skill and batch submission paths, before creating submission records.

**Implementation Details**:
- In `src/app/api/v1/submissions/route.ts`, import `deprecateOrphanSkills`
- For single-skill path: call with `[{ repoUrl, skillName }]` after validation but before `createSubmission()`
- For batch path: call with the full `skillsToSubmit` array after dedup filtering but before `createSubmissionsBatch()`
- Wrap in try/catch -- orphan cleanup is best-effort (should not block submission)
- Log the count of deprecated skills for observability

**Test Plan**:
- **File**: `src/app/api/v1/submissions/__tests__/route.orphan-cleanup.test.ts`
- **Tests**:
  - **TC-005**: single submission triggers orphan cleanup
    - Given a valid POST with repoUrl + skillName
    - When the submission is processed
    - Then `deprecateOrphanSkills` is called with the matching pair
  - **TC-006**: batch submission triggers orphan cleanup
    - Given a batch POST with multiple skills
    - When the submission is processed
    - Then `deprecateOrphanSkills` is called with all non-deduped skill pairs
  - **TC-007**: orphan cleanup failure does not block submission
    - Given `deprecateOrphanSkills` throws an error
    - When the submission is processed
    - Then the submission is still created successfully (201 response)

**Dependencies**: T-001
**Status**: [ ] Not Started

---

## Phase 2: Install Tracking Endpoint (Platform)

### US-002: Install Tracking Phone-Home from CLI (P1)

#### T-003: Create install tracking API endpoint

**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09 | **Status**: [ ] Not Started

**Description**: Create `POST /api/v1/skills/:name/installs` endpoint that increments `vskillInstalls`.

**Implementation Details**:
- Create `src/app/api/v1/skills/[name]/installs/route.ts`
- Rate limit: IP-based, 60/hour using `checkRateLimit(env.RATE_LIMIT_KV, "install:{ip}", 60, 3600)`
- Look up skill by name: `db.skill.findUnique({ where: { name } })`
- Return 404 if skill not found
- Increment: `db.skill.update({ where: { name }, data: { vskillInstalls: { increment: 1 } } })`
- Return `{ ok: true }` on success
- Accept empty body (skill name from URL param)

**Test Plan**:
- **File**: `src/app/api/v1/skills/[name]/installs/__tests__/route.test.ts`
- **Tests**:
  - **TC-008**: increments vskillInstalls for existing skill
    - Given a skill named "my-skill" with `vskillInstalls: 5`
    - When POST `/api/v1/skills/my-skill/installs`
    - Then `vskillInstalls` becomes 6 and response is `{ ok: true }`
  - **TC-009**: returns 404 for non-existent skill
    - Given no skill named "nonexistent"
    - When POST `/api/v1/skills/nonexistent/installs`
    - Then response is 404 with `{ error: "Skill not found" }`
  - **TC-010**: rate limits at 60/hour per IP
    - Given 60 requests from the same IP in the current window
    - When the 61st request arrives
    - Then response is 429 with `Retry-After` header
  - **TC-011**: rate limit failure does not block the request
    - Given `checkRateLimit` throws
    - When POST `/api/v1/skills/my-skill/installs`
    - Then the install is still counted (rate limiting is best-effort)

**Dependencies**: None (parallel with T-001/T-002)
**Status**: [ ] Not Started

---

## Phase 3: CLI Phone-Home (vskill CLI repo)

#### T-004: Add reportInstall function to CLI API client

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [ ] Not Started

**Description**: Add a `reportInstall(skillName: string)` function to `src/api/client.ts` in the vskill CLI repo.

**Implementation Details**:
- Add `reportInstall(skillName: string): Promise<void>` to `src/api/client.ts`
- Check `process.env.VSKILL_NO_TELEMETRY === "1"` -- return early if set
- Use `fetch()` with `AbortController` + 2-second timeout
- POST to `${BASE_URL}/api/v1/skills/${encodeURIComponent(skillName)}/installs`
- Empty body, `Content-Type: application/json`, `User-Agent: vskill-cli`
- Wrap entire function body in try/catch that silently returns (no console output, no throw)
- Export but do NOT await at call sites (fire-and-forget)

**Test Plan**:
- **File**: `src/api/client.test.ts` (extend existing test file)
- **Tests**:
  - **TC-012**: sends POST to correct URL
    - Given a skill name "my-skill"
    - When `reportInstall("my-skill")` is called
    - Then fetch is called with `https://verified-skill.com/api/v1/skills/my-skill/installs` and method POST
  - **TC-013**: respects VSKILL_NO_TELEMETRY
    - Given `process.env.VSKILL_NO_TELEMETRY = "1"`
    - When `reportInstall("my-skill")` is called
    - Then fetch is NOT called
  - **TC-014**: swallows network errors silently
    - Given fetch rejects with a network error
    - When `reportInstall("my-skill")` is called
    - Then the function resolves without throwing
  - **TC-015**: uses 2-second timeout via AbortController
    - Given fetch hangs
    - When `reportInstall("my-skill")` is called
    - Then the abort signal fires after 2000ms

**Dependencies**: T-003 (endpoint must exist, but CLI tests mock fetch)
**Status**: [ ] Not Started

---

#### T-005: Call reportInstall from add command

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04 | **Status**: [ ] Not Started

**Description**: Integrate `reportInstall()` into `src/commands/add.ts` at all successful install exit points.

**Implementation Details**:
- Import `reportInstall` from `../api/client.js`
- Call `reportInstall(skillName)` (no await) after each successful install log message
- There are multiple success paths in add.ts (plugin install, single skill, batch skills, local skill) -- add to each
- The call is fire-and-forget: `reportInstall(skillName).catch(() => {})` as a safety net

**Test Plan**:
- **File**: Manual verification (add.ts is a CLI entry point, tested via integration)
- **Tests**:
  - **TC-016**: verify phone-home fires after successful `vskill add`
    - Given a successful skill installation
    - When the install completes
    - Then `reportInstall` is called with the installed skill name

**Dependencies**: T-004
**Status**: [ ] Not Started

---

## Phase 4: Verification

#### T-006: End-to-end verification

**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [ ] Not Started

**Description**: Run all tests, verify builds succeed for both repos, and confirm acceptance criteria.

**Implementation Details**:
- Run `npx vitest run` in vskill-platform to verify all new + existing tests pass
- Run `npx vitest run` in vskill CLI to verify all new + existing tests pass
- Run `npm run build` in both repos to verify TypeScript compilation
- Review all ACs in spec.md and mark as satisfied

**Test Plan**:
- All existing tests still pass (no regressions)
- All new tests pass
- Build succeeds in both repos

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Status**: [ ] Not Started
