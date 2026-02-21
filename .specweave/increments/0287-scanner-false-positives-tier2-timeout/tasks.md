# Tasks: Scanner False Positives & Tier 2 LLM Timeout

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

---

## Phase 1: Fix FS-003 Path Traversal False Positives

### T-001: TDD Red — FS-003 false positive on import lines
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: Given `import X from "../../lib/Y"` → When scanned → Then NO filesystem-access finding

**Description**: Write failing tests that assert import/require lines with `../../` do NOT trigger FS-003.

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/scanner/__tests__/tier1.test.ts`
- **Tests**:
  - **TC-001**: `import X from "../../lib/Y"` → no filesystem-access findings (currently FAILS due to FS-003)
  - **TC-002**: `const x = require("../../utils/helper")` → no filesystem-access findings (currently FAILS)

**Dependencies**: None
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-002: TDD Green — Update FS-003 pattern to require fs-API context
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed
**Test**: Given import lines → no findings. Given `readFileSync("../../etc/passwd")` → FS-003 finding.

**Description**: Change the FS-003 regex in `patterns.ts` from the bare `../../` pattern to one requiring a filesystem function call prefix. Update the existing tier1 test to use an fs-API call context.

**Implementation Details**:
- In `patterns.ts` line ~301, change pattern from:
  `/\.\.[/\\]\.\.[/\\]|\.\.(?:[/\\]){2,}/g`
  to:
  `/(?:readFile|writeFile|appendFile|createReadStream|createWriteStream|open|unlink|stat|lstat|fstat|access|rename|copyFile|chmod|chown|truncate)(?:Sync)?\s*\([^)]*\.\.[/\\]\.\.[/\\]/g`
- In `tier1.test.ts` line ~220, update the test content from `const p = '../../etc/passwd'`
  to `fs.readFileSync('../../etc/passwd')` so the test still exercises FS-003 correctly

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/scanner/__tests__/tier1.test.ts`
- **Tests**:
  - **TC-003**: `fs.readFileSync('../../etc/passwd')` → FS-003 finding with severity `high`
  - **TC-004**: `readFile('../../.env', 'utf8', cb)` → FS-003 finding
  - **TC-005**: TC-001 and TC-002 now pass (imports not flagged)

**Dependencies**: T-001
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

## Phase 2: Raise Tier 2 LLM Timeout

### T-003: TDD Red — assert LLM_TIMEOUT_MS value
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Given tier2.ts constants → When checked → Then LLM_TIMEOUT_MS equals 30_000

**Description**: Add a failing test asserting the new 30s timeout constant. (Simple unit check on exported constant, or integration: verify timeout message says "30000ms".)

**Implementation Details**:
- In `tier2.test.ts`, add a test for LLM timeout behavior: mock AI that never resolves,
  confirm the returned concern message contains the expected timeout duration
- The test will currently fail because LLM_TIMEOUT_MS is still 8_000

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/scanner/__tests__/tier2.test.ts`
- **Tests**:
  - **TC-006**: AI that delays >8s but <30s → should NOT timeout (currently fails at 8s)
  - **TC-007**: Timeout error message reflects 30s timeout label

**Dependencies**: None
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

### T-004: TDD Green — Raise LLM_TIMEOUT_MS and queue timeouts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06 | **Status**: [x] completed
**Test**: Given the new timeout values → Tier 2 completes for slow LLM responses, queue budget is correct

**Description**: Apply the three timeout config changes.

**Implementation Details**:
- `tier2.ts` line 16: change `8_000` to `30_000`, update comment:
  `// LLM calls can take 10-30s; capped at 30s within the 55s per-message budget`
- `consumer.ts` line 9: change `25_000` to `55_000`, update comment:
  `// Per-message timeout — must be less than wrangler max_batch_timeout (60s)`
- `wrangler.jsonc` line ~48: change `"max_batch_timeout": 30` to `"max_batch_timeout": 60`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/scanner/__tests__/tier2.test.ts`
- **Tests**:
  - **TC-008**: All existing tier2 tests still pass after timeout increase
  - **TC-006**: (from T-003) now passes — slow AI resolves within new timeout

**Dependencies**: T-003
**Repo**: `repositories/anton-abyzov/vskill-platform`

---

## Phase 3: Verification

### T-005: Run full scanner test suite and confirm no regressions
**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [x] completed
**Test**: All tests in `src/lib/scanner/__tests__/` pass

**Description**: Run the full test suite to confirm both fixes work together with no regressions.

**Test Plan**:
- **File**: All scanner tests
- **Tests**:
  - **TC-009**: `pnpm test --run` in vskill-platform passes for all scanner tests
  - **TC-010**: No new TypeScript errors in scanner files

**Dependencies**: T-002, T-004
**Repo**: `repositories/anton-abyzov/vskill-platform`
