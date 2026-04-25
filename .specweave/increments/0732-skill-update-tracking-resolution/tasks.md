# Tasks: 0708 follow-up — tracking source resolution + ID format

## Task Notation
- `[T###]`: Task ID — `[ ]` pending, `[x]` completed
- `[P]`: Parallelizable — no ordering dependency on prior tasks in same phase
- Model hint: `haiku` (mechanical), `sonnet` (default), `opus` (deep reasoning)
- Each task has a **Test Plan** (Given/When/Then) — TDD strict, write the test first.

---

## Phase 1: Resolver precedence chain (US-001)

### T-001: Failing test — resolver returns plugin.json.repository when SKILL.md has no `repository:`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/resolver.test.ts` (new test in existing file)
**Test Plan (Given/When/Then)**:
- Given a Skill row, a SKILL.md whose frontmatter has no `repository`, and a plugin.json with `"repository": "https://github.com/foo/bar"`
- When `resolveTrackingSource()` is invoked
- Then the result is `{ url: "https://github.com/foo/bar", branch: "main" }`

### T-002: Implement plugin.json fallback in `resolveTrackingSource()`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/discovery/resolver.ts`
**Test Plan**: T-001 must transition red → green. Existing 8+ resolver tests stay green.

### T-003: Failing test — resolver falls through to marketplace.json owner inference
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/resolver.test.ts`
**Test Plan**:
- Given a Skill named `acme/widgets/foo`, no SKILL.md `repository`, no `plugin.json.repository`, but a marketplace.json listing plugin `widgets` under owner `acme`
- When `resolveTrackingSource()` runs
- Then result is `{ url: "https://github.com/acme/widgets", branch: "main" }`

### T-004: Implement marketplace.json fallback (3rd-step)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/discovery/resolver.ts`

### T-005: Failing test — branch precedence (SKILL.md > plugin.json.tracking.branch)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/resolver.test.ts`
**Test Plan**:
- Given SKILL.md frontmatter `branch: develop` and plugin.json `tracking.branch: main`
- When the resolver picks a branch
- Then it returns `develop`

### T-006: Implement branch precedence rule
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending | **Model**: haiku

### T-007: Failing test — user-locked rows are not overwritten
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/resolver.test.ts`
**Test Plan**:
- Given a Skill row with `resolutionState: "user-locked"` and a sourceRepoUrl set, and a SKILL.md/plugin.json that would resolve a different URL
- When the resolver runs in write mode
- Then no `db.skill.update` is called for that row; existing values preserved

### T-008: Implement user-locked guard in resolver write path
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending | **Model**: sonnet

### T-009: Failing test — scanner persists sourceRepoUrl/sourceBranch at discovery
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/scanner.test.ts`
**Test Plan**:
- Given a marketplace.json that lists plugin `mobile` with skill `appstore` under `anton-abyzov/vskill`
- When `runSkillUpdateScan()` mints a new Skill row for `anton-abyzov/vskill/appstore`
- Then `db.skill.create` is called with `sourceRepoUrl: "https://github.com/anton-abyzov/vskill"`, `sourceBranch: "main"`

### T-010: Implement write-at-discovery in scanner
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/scanner.ts` (around lines 362–389)

---

## Phase 2: Backfill script (US-002)

### T-011: Failing test — backfill --dry-run writes nothing, prints summary
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04 | **Status**: [ ] pending | **Model**: sonnet
**File**: `scripts/__tests__/backfill-source-repo-url.test.ts` (new)
**Test Plan**:
- Given a fixture DB with 5 orphan Skill rows and a mocked marketplace.json fetch returning a plugin matching 3 of them
- When the backfill script runs with `--dry-run`
- Then no `db.skill.update` call fires AND stdout contains `resolved: 3, skipped: 2, failed: 0` AND exit code is 0

### T-012: Failing test — backfill is idempotent (second run = zero writes)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `scripts/__tests__/backfill-source-repo-url.test.ts`
**Test Plan**:
- Given a fixture DB; backfill runs once, all writes succeed
- When backfill runs a second time with same inputs
- Then `db.skill.update` is called zero times AND exit code is 0

### T-013: Failing test — backfill exits non-zero when any group fetch fails
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] pending | **Model**: sonnet
**File**: `scripts/__tests__/backfill-source-repo-url.test.ts`
**Test Plan**:
- Given a fixture DB; mocked marketplace fetch returns 500 for one group
- When backfill runs (without --dry-run)
- Then exit code is 1 AND stdout contains `failed: ≥1`

### T-014: Failing test — happy-path resolves and writes all matched rows
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-05 | **Status**: [ ] pending | **Model**: sonnet
**File**: `scripts/__tests__/backfill-source-repo-url.test.ts`
**Test Plan**:
- Given a fixture DB with 91 orphan rows under `anton-abyzov/vskill/*` and a marketplace.json listing all 91 slugs
- When backfill runs (without --dry-run)
- Then 91 rows have `sourceRepoUrl: "https://github.com/anton-abyzov/vskill"`, `sourceBranch: "main"` AND exit 0

### T-015: Failing test — backfill skips slug not present in marketplace.json
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] pending | **Model**: haiku
**File**: `scripts/__tests__/backfill-source-repo-url.test.ts`
**Test Plan**:
- Given an orphan `acme/widgets/missing-skill` and marketplace.json listing only `widgets/other-skill`
- When backfill runs
- Then `missing-skill` is reported as skipped (not failed) and not updated

### T-016: Implement `scripts/backfill-source-repo-url.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..05 | **Status**: [ ] pending | **Model**: sonnet
**File**: `scripts/backfill-source-repo-url.ts` (new), `package.json` (add npm script `backfill:source-repo`)
**Test Plan**: Tests T-011..T-015 must transition red → green.

---

## Phase 3: Skill-ID-format dual-accept (US-003)

### T-017: Failing test — DO filter accepts UUID match
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/update-hub.test.ts`
**Test Plan**:
- Given a connected client with filter `["uuid-abc"]` and event with `skillId: "uuid-abc"`, no `skillSlug`
- When the DO fans out
- Then the client receives the event

### T-018: Failing test — DO filter accepts slug match
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/update-hub.test.ts`
**Test Plan**:
- Given a connected client with filter `["sk_published_acme/foo/bar"]` and event with `skillId: "uuid-abc"`, `skillSlug: "sk_published_acme/foo/bar"`
- When the DO fans out
- Then the client receives the event

### T-019: Failing test — mixed-format filter csv works
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/__tests__/update-hub.test.ts`
**Test Plan**:
- Given filter `["uuid-abc", "sk_published_x/y/z"]` and event with `skillId: "uuid-abc"`, `skillSlug: "sk_published_x/y/z"`
- When fanout runs
- Then the client receives exactly one event (no duplicate)

### T-020: Implement DO dual-format filter check
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/lib/skill-update/update-hub.ts` (line 144)

### T-021: Failing test — publish endpoint augments event with skillSlug
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/app/api/v1/internal/skills/publish/__tests__/route.test.ts`
**Test Plan**:
- Given a publish request with payload `{ skillId: "uuid-abc", ... }` and a Skill row with `name: "acme/foo/bar"`
- When the route forwards to the DO
- Then the forwarded body contains `skillSlug: "sk_published_acme/foo/bar"`

### T-022: Failing test — publish endpoint omits skillSlug when skill not found
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: haiku
**File**: `src/app/api/v1/internal/skills/publish/__tests__/route.test.ts`
**Test Plan**:
- Given payload with unknown `skillId`
- When the route forwards
- Then `skillSlug` is absent (not empty string), DO still receives the event

### T-023: Implement publish-time slug augmentation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending | **Model**: sonnet
**File**: `src/app/api/v1/internal/skills/publish/route.ts`, `src/lib/skill-update/types.ts` (add optional `skillSlug` to `SkillUpdateEvent`)

### T-024: Add doc-comment block stating ID-format contract
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending | **Model**: haiku
**Files**: `src/lib/skill-update/update-hub.ts` (top), `src/app/api/v1/skills/stream/route.ts` (top), `src/lib/skill-update/publish-client.ts` (top)
**Test Plan**: Manual review. Comment must answer: which IDs are accepted in `?skills=`, why dual-accept, what happens with the other format.

### T-025: End-to-end real-SSE test for slug-ID subscriber
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending | **Model**: sonnet
**File**: `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useSkillUpdates.real-sse.slug.test.ts` (new, mirrors `.real-sse.test.ts` pattern)
**Test Plan**:
- Given the same real-SSE harness from the existing `useSkillUpdates.real-sse.test.ts`, but the Studio hook subscribes with a slug ID `sk_published_acme/foo/bar`
- When the test server emits a real `event: skill.updated` frame with `skillId: "uuid-abc"`, `skillSlug: "sk_published_acme/foo/bar"`
- Then the `<UpdateBell>` badge increments to 1 (proves the dual-accept path end-to-end)

---

## Phase 4: Production verification (after deploy)

### T-026: Run backfill --dry-run against prod Neon
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending | **Model**: opus
**Test Plan**: Manual verification step. Run `node scripts/backfill-source-repo-url.ts --dry-run` from `vskill-platform/` with prod `DATABASE_URL`. Eyeball: ~90 proposed updates for `anton-abyzov/vskill/*`, exit 0, no rows touched. Capture stdout in increment notes.

### T-027: Run backfill (live) against prod Neon
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending | **Model**: opus
**Test Plan**:
- Given T-026 dry-run output is sane
- When `node scripts/backfill-source-repo-url.ts` runs without `--dry-run`
- Then `SELECT count(*) FROM "Skill" WHERE name LIKE 'anton-abyzov/vskill/%' AND "sourceRepoUrl" IS NULL` returns 0 (verified via psql or Prisma script)

### T-028: Real-release end-to-end smoke test
**User Story**: US-001, US-003 | **Satisfies SCs**: SC-001, SC-002 | **Status**: [ ] pending | **Model**: opus
**Test Plan**:
- Given the worker is deployed and backfill has run
- When a trivial commit is pushed to `anton-abyzov/vskill@main`
- Then within ≤2 cron ticks (~20 min), an SSE client subscribed via slug ID receives an `event: skill.updated` frame for the affected skill (verified by curl + tee to log file, mirror of the `/tmp/appstore-prod-watch4.log` flow used in 0708 verification)

---

## Cross-cutting

### T-029: Run full vskill-platform skill-update suite green
**Satisfies SCs**: SC-003 | **Status**: [ ] pending | **Model**: haiku
**Test Plan**: `npx vitest run src/lib/skill-update src/app/api/v1/internal/skills/publish` reports ≥150 tests, 0 failures, 0 skips.

### T-030: Run full vskill eval-ui hook suite green
**Satisfies SCs**: SC-003 | **Status**: [ ] pending | **Model**: haiku
**Test Plan**: `npx vitest run src/eval-ui/src/hooks/__tests__/` reports all green, including the new `useSkillUpdates.real-sse.slug.test.ts`.

---

## Phase order summary

1. **Phase 1** (T-001..T-010): resolver + scanner write-at-discovery — **must land first** so US-001 ACs are green before backfill code can rely on them.
2. **Phase 2** (T-011..T-016): backfill script — depends on resolver helpers from Phase 1 for shared parsing logic.
3. **Phase 3** (T-017..T-025): DO dual-format + Studio E2E — independent of Phase 1/2 in code, but should follow them in commit order to keep PR scope coherent.
4. **Phase 4** (T-026..T-028): production verification — runs only after Phases 1–3 ship + deploy.
5. **Cross-cutting** (T-029, T-030): final all-green check before `/sw:done`.

Total: 30 tasks, ~22 net new test cases. TDD strict — every implementation task is preceded by a failing-test task in the same phase.
