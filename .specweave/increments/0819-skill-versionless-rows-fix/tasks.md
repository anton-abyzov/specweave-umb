# Tasks: Skill Versionless Rows Fix

**Increment**: 0819-skill-versionless-rows-fix
**Test Mode**: TDD (RED → GREEN → REFACTOR per task)
**Coverage Targets**: 95% on new helper, 90% on backfill route, 100% AC coverage in Playwright E2E

---

## US-001 — `createSkillWithVersion()` pair-write helper

### T-001: RED — failing tests for pair-write helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test Plan**:
- Given a mocked `OutboxTx` with `skill.upsert` and access to `writeSkillVersionWithOutbox`
- When `createSkillWithVersion(db, upsertArgs, versionInput, "admin")` runs
- Then both `skill.upsert` AND `skillVersion.create` (via outbox) are called inside the same `$transaction`, and the return value is `{ skill, skillVersion, eventId, payload }`
- Given a Skill row that already has 1+ SkillVersions (count > 0)
- When the helper runs again with the same `name`
- Then no new SkillVersion is written and the returned `skillVersion` reflects the existing latest
- Given an `OutboxTx` where `writeSkillVersionWithOutbox` throws inside the txn
- When the helper runs
- Then the Skill upsert is rolled back — `db.skill.findUnique({ where: { name } })` returns null after the catch
- File: `repositories/anton-abyzov/vskill-platform/src/lib/skills/__tests__/create-skill-with-version.test.ts`

### T-002: GREEN — implement createSkillWithVersion helper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-07 | **Status**: [x] completed
**Test Plan**:
- Given the failing T-001 tests
- When the helper at `repositories/anton-abyzov/vskill-platform/src/lib/skills/create-skill-with-version.ts` is implemented
- Then T-001 tests pass without modification
- Implementation wraps `db.$transaction` with: pre-check `skillVersion.count` → upsert Skill → if count was 0, call `writeSkillVersionWithOutbox(tx, skillRef, versionInput, source, {})` with `bumpSource: "discovery-backfill"` injected via `extraData`. `contentHash` defaults to `sha256("")` when caller omits, preserving F-CR-2C non-empty invariant.

### T-003: REFACTOR — types, exports, docstring invariant
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**:
- Given the GREEN helper
- When types are extracted (`SkillUpsertArgs`, `CreateSkillResult`) and the file-header docstring documents the architecture invariant ("SINGLE call site for paired Skill+SkillVersion writes — see architecture-skill-pair.test.ts")
- Then `npx vitest run` still passes and `npx tsc --noEmit` is clean

---

## US-002 — Refactor rebuild-index admin route

### T-004: RED — integration test for paired write in rebuild-index
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**:
- Given a seeded KV index with one new entry (skill not yet in DB)
- When the rebuild-index route runs successfully
- Then `db.skillVersion.count({ where: { skillId: <new skill id> } })` returns exactly 1
- Given the same KV index re-run after the first pass
- When the rebuild-index route runs a second time
- Then no duplicate `SkillVersion` rows exist for that skill (still count = 1)
- File: extend `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rebuild-index/__tests__/route.test.ts`

### T-005: GREEN — refactor rebuild-index/route.ts to use helper
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given the failing T-004 integration test
- When `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/rebuild-index/route.ts:130` is refactored: pre-check via `db.skill.findUnique({ where: { name }, select: { id: true } })`. On null, call `createSkillWithVersion(...)` with synthesized version inputs. On non-null, fall through to existing update branch unchanged.
- Then T-004 passes; existing rebuild-index tests still pass.

### T-006: REFACTOR — inline cleanup, jsdoc, no behavioral drift
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06 | **Status**: [x] completed
**Test Plan**:
- Given the GREEN refactor
- When the create branch's inline `db.skill.upsert(...)` is fully replaced and a comment notes "publish.ts intentionally untouched — already paired via writeSkillVersionWithOutbox at line 676"
- Then `git diff` shows zero behavioral changes to `publish.ts`, full vitest suite passes.

---

## US-003 — Architecture invariant test

### T-007: RED+GREEN — write architecture-skill-pair.test.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-06 | **Status**: [x] completed
**Test Plan**:
- Given the existing pattern at `src/lib/skill-update/__tests__/architecture.test.ts`
- When a new test at `repositories/anton-abyzov/vskill-platform/src/lib/skills/__tests__/architecture-skill-pair.test.ts` is created — walk + comment-strip + regex `/\b(?:tx|prisma|db|client|trx)\.skill\.(?:create|upsert)\s*\(/` with allowlist `["lib/skills/create-skill-with-version.ts", "lib/submission/publish.ts"]`
- Then `npx vitest run src/lib/skills/__tests__/architecture-skill-pair.test.ts` passes against the post-T-005 codebase

### T-008: VERIFY — break-the-test sanity check
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [x] completed
**Test Plan**:
- Given the architecture test passing
- When `db.skill.upsert(...)` is temporarily inserted into a random non-allowlisted file (e.g. `src/lib/api-helpers.ts`)
- Then the test fails with a message naming the file and approximate location; revert the injection and confirm pass restored

---

## US-004 — Backfill admin route

### T-009: RED — backfill route auth, dryRun, batch, pagination tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-09, AC-US4-10, AC-US4-11 | **Status**: [x] completed
**Test Plan**:
- Given an unauthenticated POST to `/api/v1/admin/backfill-versionless-skills`
- When the request lands
- Then the response is 401 (or 403 for non-admin JWT)
- Given an authenticated POST with `?dryRun=true&batch=100`
- When 3 Skills exist (1 versioned, 2 versionless)
- Then response is `{ dryRun: true, scanned: 3, updated: 0, skipped: 1, errors: [] }` and `db.skillVersion.count` is unchanged
- Given an authenticated POST with `?cursor=<id>`
- When the route paginates
- Then only Skills with `id > cursor` are scanned
- File: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versionless-skills/__tests__/route.test.ts`

### T-010: GREEN — implement backfill-versionless-skills route
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-08, AC-US4-09, AC-US4-10 | **Status**: [x] completed
**Test Plan**:
- Given the failing T-009 tests
- When `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-versionless-skills/route.ts` is implemented mirroring `backfill-versions/route.ts` (auth, dryRun, batch clamp 1..500, cursor pagination, jsonResponse helpers, error array shape `{kind, id, message}`)
- Then T-009 tests pass.
- Implementation: paginate Skill rows where no SkillVersion exists. For each, derive synthesis inputs from columns + KV cache (`skillmd:${skill.id}` for contentHash, `sha256("")` fallback). Call `writeSkillVersionWithOutbox` with `bumpSource: "discovery-backfill"`, `source: "admin"`.

### T-011: idempotency + chronology tests
**User Story**: US-004 | **Satisfies ACs**: AC-US4-06, AC-US4-07, AC-US4-12, AC-US4-13 | **Status**: [x] completed
**Test Plan**:
- Given 2 versionless Skills with distinct `certifiedAt` values
- When the backfill route runs (real, not dryRun) twice in a row
- Then first run: `updated: 2, skipped: 1`. Second run: `updated: 0, skipped: 3` (idempotency)
- And for each backfilled SkillVersion, `createdAt === skill.certifiedAt` (chronology mitigation per AC-US4-06 — prevents spurious /check-updates fanout)

### T-012: REFACTOR — extract orphan-detection query helper
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed (no extraction — query is in one place; premature abstraction skipped per task plan)
**Test Plan**:
- Given the GREEN backfill route
- When the "find Skills with zero SkillVersions" query is duplicated in tests vs production
- Then extract to `findVersionlessSkills(db, { batch, cursor })` if and only if the duplication is real and not premature

---

## US-005a — `/versions` route returns `unversioned: true`

### T-013: RED — versions route 3-branch test
**User Story**: US-005a | **Satisfies ACs**: AC-US5a-01, AC-US5a-02, AC-US5a-03, AC-US5a-04 | **Status**: [x] completed
**Test Plan**:
- Given a Skill row with 0 SkillVersions
- When `GET /api/v1/skills/o/r/s/versions` is called
- Then response is HTTP 200 with body `{ versions: [], count: 0, unversioned: true, currentVersion: <skill.currentVersion> }`
- Given a Skill row with 2 SkillVersions
- When the same endpoint is called
- Then response is HTTP 200 and the body has `count: 2`, no `unversioned` field
- Given no Skill row exists for that owner/repo/slug
- Then response is HTTP 404 with the existing not-found shape
- File: extend `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts` (create if missing)

### T-014: GREEN — modify versions route
**User Story**: US-005a | **Satisfies ACs**: AC-US5a-01, AC-US5a-02, AC-US5a-03 | **Status**: [x] completed
**Test Plan**:
- Given the failing T-013 tests
- When `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts` is modified: after the existing query, check `if (count === 0)` and return `{ versions: [], count: 0, unversioned: true, currentVersion: dbSkill.currentVersion }`. Skill-not-found path stays 404.
- Then T-013 passes.

---

## US-005b — Skill Studio detail panel UI copy

### T-015: RED — Vitest snapshot test for SkillDetailPanel unversioned branch
**User Story**: US-005b | **Satisfies ACs**: AC-US5b-01, AC-US5b-02, AC-US5b-03, AC-US5b-04, AC-US5b-05 | **Status**: [x] completed
**Test Plan**:
- Given a mocked `/versions` response `{ versions: [], count: 0, unversioned: true, currentVersion: "1.0.0" }`
- When `SkillDetailPanel` renders
- Then the DOM contains `data-testid="skill-detail-unversioned"` with text matching `Discovered — no published version yet (currentVersion: 1.0.0)`
- Given a mocked response with `count > 0`
- Then the existing version list renders (no unversioned testid)
- File: `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/__tests__/SkillDetailPanel.test.tsx`

### T-016: GREEN — update SkillDetailPanel.tsx
**User Story**: US-005b | **Satisfies ACs**: AC-US5b-01, AC-US5b-02, AC-US5b-03, AC-US5b-04 | **Status**: [x] completed
**Test Plan**:
- Given the failing T-015 snapshot
- When `repositories/anton-abyzov/vskill/src/eval-ui/src/components/FindSkillsPalette/SkillDetailPanel.tsx:595` is modified to read `meta.unversioned` (from the merged metadata+versions response) and conditionally render the new copy with `data-testid="skill-detail-unversioned"`
- Then T-015 passes; existing tests remain green.

---

## End-to-end + deploy

### T-017: Playwright E2E `0819-versionless-skills.spec.ts`
**User Story**: US-005a, US-005b | **Satisfies ACs**: AC-US5a-05, AC-US5b-06 | **Status**: [ ] pending
**Test Plan**:
- Given the deployed platform + studio
- When the test calls `GET /api/v1/skills/gitroomhq/postiz-agent/postiz/versions` (post-backfill)
- Then `count >= 1` and `versions[0].version === "1.0.0"`
- Given the bare-name slug `postiz`
- When the test calls `GET /api/v1/skills/postiz/versions`
- Then HTTP 404 (regression guard for resolveSkillName behavior)
- Given the studio open at the postiz detail panel
- When the page loads
- Then `data-testid="skill-detail-versions"` shows the v1.0.0 row AND the "see all versions →" link `href` resolves to `https://verified-skill.com/skills/gitroomhq/postiz-agent/postiz/versions` (200)
- Given a synthetic Skill with no SkillVersion (seeded for the test)
- When the studio detail panel loads
- Then `data-testid="skill-detail-unversioned"` is visible with the new copy
- File: `repositories/anton-abyzov/vskill-platform/tests/e2e/0819-versionless-skills.spec.ts`

### T-018: Deploy via push-deploy.sh + tail wrangler
**User Story**: US-001..US-005a | **Satisfies ACs**: deploy gate for AC-US5a-05 | **Status**: [ ] pending
**Test Plan**:
- Given all unit + integration tests passing
- When `./scripts/push-deploy.sh origin main` runs from `repositories/anton-abyzov/vskill-platform/`
- Then pipeline completes: db:generate → db:migrate → build → build:worker → deploy → cache-warm. Tail `npx wrangler tail` for 60s post-deploy and confirm no error log lines.

### T-019: Production backfill — dry-run, review, real
**User Story**: US-004 | **Satisfies ACs**: AC-US4-11, AC-US4-12 in production | **Status**: [ ] pending
**Test Plan**:
- Given the deployed worker
- When `pkill -f "specweave dashboard"` runs (per `feedback_dashboard_kills_rate_limit.md` — avoid GitHub rate-limit collision)
- And `curl -X POST "https://verified-skill.com/api/v1/admin/backfill-versionless-skills?dryRun=true&batch=100" -H "X-Internal-Key: $INTERNAL_KEY"` runs first
- Then the dry-run reports the orphan count for review (expected ≥1 — at minimum postiz)
- And subsequently `curl -X POST ".../backfill-versionless-skills?batch=100"` runs without dryRun, reports `updated: N, skipped: M`
- And `curl https://verified-skill.com/api/v1/skills/gitroomhq/postiz-agent/postiz/versions` returns `count: 1` post-backfill (success criterion)

---

## Closure

After T-001 through T-019 complete, run `/sw:done 0819` which triggers:
1. `sw:code-reviewer` — fixes any critical/high/medium findings (max 3 iterations)
2. `/simplify` — DRY/readability pass
3. `/sw:grill` — adversarial quality interrogation
4. `/sw:judge-llm` — Opus extended-thinking validation
5. PM 3-gate (tasks/tests/docs)
6. `/sw:progress-sync` — push status to GitHub Issues (umbrella → vskill-platform repo)

**Total tasks**: 19 covering 44 ACs across 6 user stories.
