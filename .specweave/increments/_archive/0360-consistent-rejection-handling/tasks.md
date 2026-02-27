# Tasks: Consistent Rejection Handling

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Platform API

### US-001: Extend Blocklist Check API with Rejection Status (P1)

#### T-001: Extend GET /api/v1/blocklist/check with rejection query
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] Completed

**Description**: Add Submission rejection query to the existing blocklist check endpoint.

**Implementation Details**:
- After existing BlocklistEntry query, add `db.submission.findFirst` for rejected submissions matching skill name
- Return `{ blocked, entry?, rejected, rejection? }` — backward-compatible
- Only query rejections when `name` param is present (not for hash-only queries)

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/blocklist/check/route.ts`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/blocklist/check/__tests__/route.test.ts`
- **Tests**:
  - **TC-001**: Skill rejected only → `{ blocked: false, rejected: true, rejection: {...} }`
    - Given a submission with state REJECTED exists for skill "bad-skill"
    - When GET /api/v1/blocklist/check?name=bad-skill
    - Then response has blocked=false, rejected=true with rejection details
  - **TC-002**: Skill blocked only → `{ blocked: true, entry: {...}, rejected: false }`
    - Given a BlocklistEntry exists but no rejected submission
    - When GET /api/v1/blocklist/check?name=malicious-skill
    - Then response has blocked=true with entry, rejected=false
  - **TC-003**: Skill both blocked and rejected → both fields populated
  - **TC-004**: Clean skill → `{ blocked: false, rejected: false }`
  - **TC-005**: Hash-only query → rejected=false (no rejection check)

**Dependencies**: None

---

#### T-002: Add GET /api/v1/rejections endpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02
**Status**: [x] Completed

**Description**: New API endpoint returning paginated rejected submissions for the Trust Center tab.

**Implementation Details**:
- Query `Submission.findMany` with `state IN (REJECTED, TIER1_FAILED, DEQUEUED)`
- Include latest `ScanResult` per submission (severity counts, score, verdict)
- Order by `updatedAt desc`
- Return `{ rejections: [...], count }`

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/rejections/route.ts`

**Test Plan**:
- **Tests**:
  - **TC-006**: Returns rejected submissions with scan data
  - **TC-007**: Returns empty array when no rejections exist
  - **TC-008**: Excludes active/published submissions

**Dependencies**: None

## Phase 2: CLI

### US-002: CLI Blocks Installation of Rejected Skills (P1)

#### T-003: Add rejection types to CLI blocklist module
**User Story**: US-002 | **Satisfies ACs**: AC-US2-07
**Status**: [x] Completed

**Description**: Add `RejectionInfo` and `InstallSafetyResult` types.

**Files**: `repositories/anton-abyzov/vskill/src/blocklist/types.ts`

**Dependencies**: None

---

#### T-004: Implement checkInstallSafety() function
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed

**Description**: New function that calls the extended blocklist/check API and returns both blocklist and rejection status. Falls back to local checkBlocklist() when API is unreachable.

**Files**: `repositories/anton-abyzov/vskill/src/blocklist/blocklist.ts`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill/src/blocklist/__tests__/blocklist.test.ts`
- **Tests**:
  - **TC-009**: API returns blocked+rejected → returns both
  - **TC-010**: API returns rejected only → blocked=false, rejected=true
  - **TC-011**: API returns clean → both false
  - **TC-012**: API unreachable → falls back to local cache, rejected=false

**Dependencies**: T-003

---

#### T-005: Wire rejection checks into all CLI install paths
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Status**: [x] Completed

**Description**: Replace all 5 checkBlocklist() calls with checkInstallSafety(). Add printRejectedError() and printRejectedWarning() functions.

**Implementation Details**:
- Replace calls at lines 506, 714, 940, 1313, 1426
- Add printRejectedError() — "REJECTED: Skill failed platform verification" with score/state/reason
- Add printRejectedWarning() — warning for --force override
- Blocked takes priority over rejected

**Files**: `repositories/anton-abyzov/vskill/src/commands/add.ts`

**Dependencies**: T-004

## Phase 3: Trust Center UI

### US-003: Trust Center Rejected Skills Tab (P1)

#### T-006: Add Rejected Skills tab to Trust Center page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-06
**Status**: [x] Completed

**Description**: Add third tab to the TABS array and conditional rendering.

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/trust/page.tsx`

**Dependencies**: None

---

#### T-007: Create RejectedSkillsTab component
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] Completed

**Description**: New component mirroring BlockedSkillsTab pattern. Table with expandable rows, search, status badges, score display.

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/trust/RejectedSkillsTab.tsx`

**Dependencies**: T-002, T-006

### US-004: Cross-Reference Rejections in Blocked Skills Detail (P2)

#### T-008: Add rejection cross-reference to BlockedSkillsTab expanded detail
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed

**Description**: In ExpandedDetail, lazy-fetch rejection status when row expands. Show "Also rejected in verification pipeline" badge when applicable.

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/trust/BlockedSkillsTab.tsx`

**Dependencies**: T-001

## Phase 4: Verification

- [x] [T-009] Run vskill-platform tests (1609 passed)
- [x] [T-010] Run vskill CLI tests (528 passed)
- [x] [T-011] Verify all acceptance criteria
