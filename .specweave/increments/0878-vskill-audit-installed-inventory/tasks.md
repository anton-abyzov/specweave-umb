# Tasks: Free `vskill audit --installed` — machine-wide skill inventory + scan

Repo: `repositories/anton-abyzov/vskill` · Mode: **TDD (RED→GREEN→REFACTOR)** · Run `npx vitest run` after every task.

## Phase 1: Inventory (US-001)

### T-001: [RED] Inventory tests — walk, plugin cache, dedupe, managed flag, safety
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Test Plan**:
- **File**: `src/audit/__tests__/installed-inventory.test.ts`
- **Tests**:
  - **TC-001**: Given mocked `detectInstalledAgents` (claude-code + cursor) and `mkdtemp` skills roots with `a/SKILL.md`, `b/SKILL.md` → When `inventoryInstalledSkills(cwd)` → Then both skills found with correct agentId/scope/absPath; missing dirs yield 0 without throwing (AC-US1-01).
  - **TC-002**: Given fake plugin cache `{mp}/{plug}/{v1,v2}/skills/x/SKILL.md` and `listEnabledPlugins` returning `plug@mp` → When inventoried → Then only highest version scanned; a second disabled plugin increments `cachedButDisabled` and is not read (AC-US1-02).
  - **TC-003**: Given identical SKILL.md content in claude-code global AND cursor project dirs → When inventoried → Then ONE entry with `locations.length === 2`; a same-named skill with different content is a separate entry (AC-US1-03).
  - **TC-004**: Given mocked `readLockfile` containing skill `a` only → Then `a.managed === true`, `b.managed === false` (AC-US1-04).
  - **TC-005**: Given a symlinked dir cycle, an unreadable dir (mocked EACCES), a 200 KB file, and a `node_modules` dir inside a skill → When inventoried → Then no crash, symlink not traversed, oversize file skipped, node_modules skipped (AC-US1-05).
- Verify: all new tests FAIL (module does not exist yet).

### T-002: [GREEN] Implement `installed-types.ts` + `installed-inventory.ts`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05 | **Depends On**: T-001 | **Status**: [x] completed
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
Minimal implementation per plan.md Design (walk, plugin cache, `readSkillBundle` caps, `computeSha` dedupe, managed cross-ref). All T-001 tests pass.
**Test Plan**: `npx vitest run src/audit/__tests__/installed-inventory.test.ts` → green; full suite stays green.

### T-003: [REFACTOR] Share discovery constants + walk guards
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Depends On**: T-002 | **Status**: [x] completed
**AC**: AC-US1-05
Extract/reuse `SKIP_DIRS`, `SCANNABLE_EXTENSIONS`, `maxFileSize` from `src/audit/file-discovery.ts` instead of local copies; unify symlink/depth guard helpers. Tests stay green.
**Test Plan**: `npx vitest run` → green; grep confirms no duplicated constant arrays.

## Phase 2: Scan orchestration (US-002)

### T-004: [RED] Orchestration tests — verdict compose, blocklist FAIL, offline skip
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Depends On**: T-002 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Test Plan**:
- **File**: `src/audit/__tests__/installed-audit.test.ts`
- **Tests**:
  - **TC-006**: Given mocked `runTier1Scan` returning findings → When `runInstalledAudit` → Then `ScanFinding`s adapted to `InstalledSkillFinding` (patternId/severity/line/context preserved) (AC-US2-01).
  - **TC-007**: Given mocked `checkBlocklist` hit for one skill → Then that skill verdict FAIL and aggregate verdict FAIL regardless of tier1 PASS (AC-US2-02).
  - **TC-008**: Given `offline: true` → Then `checkPlatformSecurity` NOT called, `result.offline === true` (AC-US2-03).
  - **TC-009**: Given 3 skills with severities across the range → Then summary counts/score/verdict follow tier1 scoring conventions (PASS≥80, CONCERNS 50–79, FAIL<50) (AC-US2-04).
- Verify: tests FAIL first.

### T-005: [GREEN] Implement `installed-audit.ts`
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Depends On**: T-004 | **Status**: [x] completed
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
`runInstalledAudit(opts)` with ~5-wide `Promise.allSettled` pool, finding adapter, verdict/summary aggregation, offline probe honoring `--offline`.
**Test Plan**: `npx vitest run src/audit/__tests__/installed-audit.test.ts` → green; full suite green.

### T-006: [REFACTOR] Pure verdict/severity helpers
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Depends On**: T-005 | **Status**: [x] completed
**AC**: AC-US2-04
Extract verdict-aggregation + severity-ordering into small pure functions shared with formatters; no behavior change.
**Test Plan**: `npx vitest run` → green.

## Phase 3: Formatters + CLI wiring (US-003, US-004)

### T-007: [RED] Command-level tests — outputs, flags, exit codes, hint, regression
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03 | **Depends On**: T-005 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03
**Test Plan**:
- **File**: `src/commands/__tests__/audit-installed.test.ts` (12 tests, TC-010..TC-015 incl. sub-cases)
- **Tests**:
  - **TC-010**: Given fixture skills → When `audit --installed` → Then terminal shows summary header + table columns skill/agents/scope/managed/verdict/findings (AC-US3-01).
  - **TC-011**: When `--installed --json` → Then stdout parses as `InstalledAuditResult`, no ANSI; When `--installed --report f.md` → Then markdown file written containing hostname, date, unmanaged headline, offline note when offline (AC-US3-02).
  - **TC-012**: Given PASS/CONCERNS/FAIL scenarios → Then `process.exit` called with 0/1/2 (AC-US3-03).
  - **TC-013**: When `--installed --ci` → Then warning printed and JSON emitted, no SARIF (AC-US3-04).
  - **TC-014**: When `--installed --fix --tier1-only` → Then one-line ignored-flag notice, run proceeds; `--severity high` filters table (AC-US4-02).
  - **TC-015**: Default `vskill audit` (no `--installed`) on a fixture project → Then output identical to before EXCEPT one dim hint line; hint absent with `--json`/`--ci`; existing `audit.test.ts` suite untouched and green (AC-US4-01, AC-US4-03).
- Verify: new tests FAIL first.

### T-008: [GREEN] Formatters + `audit.ts` branch + `index.ts` flags
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03 | **Depends On**: T-007 | **Status**: [x] completed
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US4-01, AC-US4-02, AC-US4-03
Add `formatInstalledTerminal/Report/Json`; extend `AuditCommandOptions`; top branch to `runInstalledAudit`; register `--installed`/`--offline` in index.ts; hint line; ignored-flag notices.
**Test Plan**: `npx vitest run` → entire suite green including pre-existing audit tests unmodified.

### T-009: [REFACTOR] Share summary rendering + docs
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Depends On**: T-008 | **Status**: [x] completed
**AC**: AC-US4-04
Dedupe severity-count rendering between project and installed report formatters; update README CLI section + docs cli-reference with the new mode + example (sales-artifact framing: "free, no account, works offline").
**Test Plan**: `npx vitest run` → green; README/docs contain `audit --installed` example; `npm run build` succeeds.

## Phase 4: Verification

### T-010: E2E sanity + AC sweep
**User Story**: US-001..US-004 | **Satisfies ACs**: all | **Depends On**: T-009 | **Status**: [x] completed
**AC**: AC-US1-01..AC-US4-04
**Test Plan**: Given this dev machine → When `node dist/index.js audit --installed --report /tmp/audit-sanity.md` → Then real inventory including the specweave plugin, exit code matches verdict, report readable; run `--offline` variant; tick every AC checkbox in spec.md; `specweave validate 0878`.
