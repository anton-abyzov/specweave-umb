# Tasks: vskill-platform — skill page must always render

## Task Notation

- `[ ]` not started · `[x]` completed
- `**AC**:` field is the bidirectional link to spec.md
- `**Test Plan**:` block precedes implementation (TDD red→green)

## Phase 1: TDD Red — failing tests

### T-001: Inspect existing test conventions in vskill-platform
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Description**: Read sibling unit tests in `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/` (or wherever data.ts tests already live) to confirm Vitest mocking pattern for Prisma. Capture the import paths for `getDb` / Prisma client and the spy convention for `console.warn`.
**Test Plan**: N/A — discovery task.
**Output**: Notes inline below; no file produced. (Confirmed: existing tests use `vi.mock('@/lib/db', ...)` with mocked Prisma client; `console.warn` is spied via `vi.spyOn(console, 'warn')`.)

### T-002: Write failing Vitest cases for `getBlocklistEntryBySkillName`
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Description**: Add `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/data-failsoft.test.ts`. Two cases for `getBlocklistEntryBySkillName`:
1. **Throws → returns null + warns**: stub `db.blocklistEntry.findFirst` to reject with `new Error('simulated D1 failure')`. Assert: function resolves to `null`, `console.warn` called once with first arg starting with `[getBlocklistEntryBySkillName] DB error:`.
2. **Resolves with row → unchanged shape**: stub `findFirst` to resolve with a fixture entry. Assert: function returns the mapped `BlockedSkillData` shape (fields: `skillName, sourceUrl, sourceRegistry, threatType, severity, reason, discoveredBy, discoveredAt`).
**Test Plan**:
- **File**: `src/lib/__tests__/data-failsoft.test.ts`
- **TC-001 (Given/When/Then)**: Given `db.blocklistEntry.findFirst` is mocked to reject with `Error('simulated D1 failure')` — When `getBlocklistEntryBySkillName('a/b/c')` is awaited — Then the result is `null` AND `console.warn` was called exactly once with first arg matching `/^\[getBlocklistEntryBySkillName\] DB error:/`.
- **TC-002 (Given/When/Then)**: Given `db.blocklistEntry.findFirst` resolves with `{ skillName: 'evil-skill', sourceUrl: 'https://example.com', sourceRegistry: 'npm', threatType: 'malware', severity: 'critical', reason: 'C2 callback', discoveredBy: 'human-review', discoveredAt: new Date('2026-04-01T00:00:00Z'), isActive: true }` — When awaited — Then the result equals `{ skillName, sourceUrl, sourceRegistry, threatType, severity, reason, discoveredBy, discoveredAt: '2026-04-01T00:00:00.000Z' }` (ISO string).
**Expected**: TC-001 fails (current code throws); TC-002 passes.

### T-003: Write failing Vitest cases for `getRejectedSubmissionBySkillName`
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Description**: Two cases mirroring T-002 for `getRejectedSubmissionBySkillName`:
1. **Throws → returns null + warns** with prefix `[getRejectedSubmissionBySkillName] DB error:`.
2. **Resolves with row → unchanged shape**: fixture submission with one stateEvent, assert returned `RejectedSkillData` includes `rejectionReason` from `metadata.reason` and `rejectionTrigger` from event `trigger`.
**Test Plan**:
- **File**: `src/lib/__tests__/data-failsoft.test.ts` (same file as T-002)
- **TC-003 (Given/When/Then)**: Given `db.submission.findFirst` is mocked to reject with `Error('simulated D1 failure')` — When `getRejectedSubmissionBySkillName('a/b/c')` is awaited — Then the result is `null` AND `console.warn` called exactly once with first arg matching `/^\[getRejectedSubmissionBySkillName\] DB error:/`.
- **TC-004 (Given/When/Then)**: Given `db.submission.findFirst` resolves with a submission whose `stateEvents[0]` has `trigger: 'tier1_scan'` and `metadata: { reason: 'C2 callback detected' }` — When awaited — Then the result includes `rejectionReason: 'C2 callback detected'`, `rejectionTrigger: 'tier1_scan'`, and the original `skillName, repoUrl, createdAt, updatedAt`.
**Expected**: TC-003 fails (current code throws); TC-004 passes.

### T-004: Run vitest red gate
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Description**: From `repositories/anton-abyzov/vskill-platform/`, run `npx vitest run src/lib/__tests__/data-failsoft.test.ts`. Confirm TC-001 and TC-003 fail with the thrown `simulated D1 failure` propagating. Confirm TC-002 and TC-004 pass.
**Test Plan**: Manual verification of vitest output — exit code non-zero, two FAIL lines.
**Expected output prefix**: `FAIL  src/lib/__tests__/data-failsoft.test.ts > getBlocklistEntryBySkillName > returns null on DB error`.

## Phase 2: TDD Green — implementation

### T-005: Apply fail-soft to `getBlocklistEntryBySkillName`
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Description**: Edit `repositories/anton-abyzov/vskill-platform/src/lib/data.ts` lines 296-301. Replace the trailing `throw err;` with `return null;`. Keep the `console.warn` line unchanged.
**Test Plan**: T-002's TC-001 + TC-002 must both pass after this edit.

### T-006: Apply fail-soft to `getRejectedSubmissionBySkillName`
**User Story**: US-001 | **AC**: AC-US1-02, AC-US1-04 | **Status**: [x] completed
**Description**: Edit `src/lib/data.ts` lines 352-357. Same change: `throw err;` → `return null;`.
**Test Plan**: T-003's TC-003 + TC-004 must both pass after this edit.

### T-007: Run vitest green gate
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Description**: `npx vitest run src/lib/__tests__/data-failsoft.test.ts` — all four cases pass.
**Test Plan**: vitest exit code 0, four PASS lines.

### T-008: Run full vitest suite for regressions
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Notes**: Pre-existing failures in `data.test.ts` (5 cases on `getSkills`/`getSkillCategories`/`getSkillCount`/`getVerifiedSkillCount`/`getSkillByName` CF_PAGES production-mode tests) and 38 unrelated test files (jose JWT `payload must be an instance of Uint8Array`, env-related) all reproduce on `main` without my change — verified via `git stash`/`stash pop` cycle. Zero NEW failures introduced by this increment.
**Description**: `npx vitest run` from `repositories/anton-abyzov/vskill-platform/`. No new failures vs. baseline.
**Test Plan**: Exit code 0; if pre-existing failures exist, diff against the previous run to confirm none are new.

## Phase 3: E2E regression

### T-009: Add Playwright smoke test for the soft-404 contract
**User Story**: US-001 | **AC**: AC-US1-05 | **Status**: [x] completed
**Description**: Add `tests/e2e/skill-not-found.spec.ts`. Single test that visits `/skills/no-such-publisher-9999/no-such-repo/no-such-skill?t=${Date.now()}` and asserts:
1. HTTP response status is 200.
2. Page body text contains `Skill Not Found`.
3. Page body text does NOT contain any of: `digest:`, `could not be loaded`, `Application error`, `client-side exception`.
**Test Plan**:
- **File**: `tests/e2e/skill-not-found.spec.ts`
- **TC-005 (Given/When/Then)**: Given the URL `/skills/no-such-publisher-9999/no-such-repo/no-such-skill?t=<ts>` — When the browser navigates and reaches networkidle — Then `response.status() === 200`, `body.innerText` includes `Skill Not Found`, AND none of the forbidden error strings appear anywhere in the page text.

### T-010: Run Playwright smoke against production
**User Story**: US-001 | **AC**: AC-US1-05 | **Status**: [x] completed
**Notes**: Used `CI=1 E2E_BASE_URL=https://verified-skill.com` env vars (CI=1 disables the auto-started dev server in `playwright.config.ts`; `E2E_BASE_URL` is the env-var name not BASE_URL). Test passes in 3.2s. Adjusted assertion: body contains `404 — Not found` (visible) and `<title>` matches `/Skill Not Found/` (set by `generateMetadata`); the literal `Skill Not Found` is not in the rendered body.
**Description**: Run `BASE_URL=https://verified-skill.com npx playwright test tests/e2e/skill-not-found.spec.ts` (or whatever the existing `playwright.config.ts` BASE_URL convention is). Confirm green.
**Test Plan**: playwright exit code 0; test report shows 1 passed.

## Phase 4: Closure

### T-011: Flip ACs in spec.md
**User Story**: US-001, US-002 | **AC**: all | **Status**: [x] completed
**Description**: Edit `spec.md`: change `- [ ] **AC-US1-01**` … `- [ ] **AC-US2-02**` to `- [x]`.
**Test Plan**: N/A — bookkeeping.

### T-012: Mark increment ready for review
**User Story**: US-001 | **AC**: all | **Status**: [x] completed
**Description**: Update `metadata.json` `status` from `active` → `ready_for_review` after T-001..T-011 are all `[x]`.
**Test Plan**: N/A — bookkeeping.

### T-013: Commit and push (umbrella + child repo)
**User Story**: US-001 | **AC**: all | **Status**: [ ] not started
**Description**: Two commits — one in `repositories/anton-abyzov/vskill-platform/` (the data.ts + tests change) and one in the umbrella for the increment artifacts. Then `git push` both.
**Test Plan**: `git status` clean afterward in both repos.
