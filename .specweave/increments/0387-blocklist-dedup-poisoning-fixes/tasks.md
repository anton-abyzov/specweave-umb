# Tasks: Fix Blocklist Global Poisoning, Duplicate Blocked Submissions, and Crawler Dedup Bypass

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: Scoped Blocklist Matching (US-001)

### T-001: Create shared blocklist check helper

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-04 | **Status**: [x] completed

**Description**: Create `src/lib/blocklist-check.ts` with a `findActiveBlocklistEntry(skillName, repoUrl?)` function that builds a scoped OR query: match entries where `(skillName = X AND sourceUrl = repoUrl) OR (skillName = X AND sourceUrl IS NULL)`.

**Implementation Details**:
- New file: `src/lib/blocklist-check.ts`
- Accept `skillName: string` and optional `repoUrl: string`
- Query: `db.blocklistEntry.findFirst({ where: { skillName, isActive: true, OR: [{ sourceUrl: repoUrl }, { sourceUrl: null }] } })`
- When `repoUrl` is not provided, fall back to name-only matching (backward compat for non-submission contexts)
- Export the function for use across all blocklist check sites

**Test Plan**:
- **File**: `src/lib/__tests__/blocklist-check.test.ts`
- **Tests**:
  - **TC-001**: Returns entry when skillName + sourceUrl match
    - Given a blocklist entry with sourceUrl = "https://github.com/evil/repo"
    - When checking skillName "google" with repoUrl "https://github.com/evil/repo"
    - Then returns the matching entry
  - **TC-002**: Returns null when skillName matches but sourceUrl does not
    - Given a blocklist entry with sourceUrl = "https://github.com/evil/repo"
    - When checking skillName "google" with repoUrl "https://github.com/legit/repo"
    - Then returns null
  - **TC-003**: Returns entry for global ban (sourceUrl = null)
    - Given a blocklist entry with sourceUrl = null
    - When checking skillName "malware-x" with any repoUrl
    - Then returns the matching entry
  - **TC-004**: Returns null for non-blocked skill
    - Given no matching blocklist entries
    - When checking any skillName
    - Then returns null

**Dependencies**: None

---

### T-002: Update processSubmission early blocklist check

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Replace the inline `blocklistEntry.findFirst` in `process-submission.ts` (line 243) with the shared `findActiveBlocklistEntry` helper, passing `repoUrl` from the submission options.

**Implementation Details**:
- Import `findActiveBlocklistEntry` from `@/lib/blocklist-check`
- Replace the `dbEarly.blocklistEntry.findFirst({ where: { skillName, isActive: true } })` with `findActiveBlocklistEntry(skillName, repoUrl)`
- Pass `repoUrl` from `opts.repoUrl`

**Test Plan**:
- Existing `process-submission` tests cover this path
- Add a test case: skill "google" from legit repo should NOT be blocked when only evil repo's "google" is blocklisted

**Dependencies**: T-001

---

### T-003: Update finalize-scan early blocklist check

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Description**: Replace the inline blocklist check in `finalize-scan/route.ts` (line 257) with the shared helper.

**Implementation Details**:
- Import `findActiveBlocklistEntry` from `@/lib/blocklist-check`
- Replace the `db.blocklistEntry.findFirst({ where: { skillName, isActive: true } })` with `findActiveBlocklistEntry(skillName, repoUrl)`
- `repoUrl` is already available in the request body

**Test Plan**:
- Verify via existing finalize-scan route tests

**Dependencies**: T-001

---

### T-004: Update blocklist/check API endpoint

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: Update `GET /api/v1/blocklist/check` to accept optional `repoUrl` query param and use scoped matching.

**Implementation Details**:
- Accept `repoUrl` from `searchParams.get("repoUrl")`
- Use `findActiveBlocklistEntry(name, repoUrl)` instead of direct findFirst
- When `repoUrl` is not provided, use name-only matching (backward compat for CLI clients)

**Test Plan**:
- **File**: `src/app/api/v1/blocklist/check/__tests__/route.test.ts`
- **Tests**:
  - **TC-005**: Returns blocked=true when name + repoUrl match a scoped entry
  - **TC-006**: Returns blocked=false when name matches but repoUrl does not
  - **TC-007**: Returns blocked=true for global ban (sourceUrl=null) regardless of repoUrl
  - **TC-008**: Returns blocked=true when no repoUrl param provided (backward compat)

**Dependencies**: T-001

---

### T-005: Update blocklist-upsert dedup lookup

**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed

**Description**: Update `upsertBlocklistEntry` to include `sourceUrl` in its existing findFirst dedup lookup, so entries from different repos remain separate.

**Implementation Details**:
- In `blocklist-upsert.ts` line 42-48, add `sourceUrl: input.sourceUrl ?? null` to the WHERE clause
- This prevents merging entries from different repos that happen to have the same skillName

**Test Plan**:
- **File**: `src/lib/__tests__/blocklist-upsert.test.ts`
- **Tests**:
  - **TC-009**: Upsert for same skillName from different repos creates separate entries
  - **TC-010**: Upsert for same skillName from same repo updates existing entry

**Dependencies**: None (can be parallelized with T-001)

---

### T-006: Update remaining blocklist check sites

**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Description**: Update all remaining inline blocklist checks to use the shared helper:
- `src/lib/data.ts` (line 212-213)
- `src/app/api/v1/submissions/[id]/route.ts` (line 26-27)
- `src/app/api/v1/admin/reports/[id]/route.ts` (line 78-79)
- `src/app/api/v1/admin/submissions/[id]/reject/route.ts` (line 116)

**Implementation Details**:
- Each site already has access to `repoUrl` or `submission.repoUrl`
- Replace direct `findFirst` calls with `findActiveBlocklistEntry(skillName, repoUrl)`

**Test Plan**:
- Existing test suites cover these code paths
- Manual verification that seed data still blocks correctly

**Dependencies**: T-001

---

## Phase 2: Blocked Dedup (US-002)

### T-007: Add blocked kind to submission dedup

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed

**Description**: Update `checkSubmissionDedup` and `checkSubmissionDedupBatch` to return `kind: "blocked"` for BLOCKED submissions.

**Implementation Details**:
- In `submission-dedup.ts`, add `| { kind: "blocked"; submissionId: string }` to `DedupStatus` type
- In `checkSubmissionDedup` line 55: split BLOCKED from the REJECTED group
  - Before the REJECTED check, add: `if (existing.state === "BLOCKED") return { kind: "blocked", submissionId: existing.id }`
- In `checkSubmissionDedupBatch` line 145: same split
  - Before the REJECTED check, add BLOCKED handling

**Test Plan**:
- **File**: `src/lib/__tests__/submission-dedup.test.ts`
- **Tests**:
  - **TC-011**: Returns kind="blocked" when latest submission is BLOCKED
    - Given a submission with state BLOCKED
    - When checking dedup for same repoUrl + skillName
    - Then returns `{ kind: "blocked", submissionId: "<id>" }`
  - **TC-012**: Batch dedup returns kind="blocked" for BLOCKED submissions

**Dependencies**: None (can be parallelized)

---

### T-008: Handle blocked dedup in submission POST

**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04 | **Status**: [x] completed

**Description**: Update POST `/api/v1/submissions` to short-circuit on `dedup.kind === "blocked"`.

**Implementation Details**:
- In `submissions/route.ts` around line 506-521, add a case for `dedup.kind === "blocked"`:
  ```typescript
  if (dedup.kind === "blocked") {
    return NextResponse.json(
      { blocked: true, submissionId: dedup.submissionId },
      { status: 200 },
    );
  }
  ```
- In the batch path (line 592), add `dedup.kind === "blocked"` to the skip condition
- In the internal sequential path (line 690), add `dedup.kind === "blocked"` to the skip condition

**Test Plan**:
- **File**: `src/app/api/v1/submissions/__tests__/route.dedup.test.ts`
- **Tests**:
  - **TC-013**: POST returns 200 with blocked=true when skill is blocked
  - **TC-014**: Batch submission skips blocked skills

**Dependencies**: T-007

---

## Phase 3: Crawler Dedup Race Fix (US-003)

### T-009: Reorder markDiscovered to write-ahead pattern

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: In `github-discovery.ts` `processRepo()`, move `markDiscovered` BEFORE the HTTP POST to prevent race conditions.

**Implementation Details**:
- In `processRepo()` (around line 680-748):
  1. BEFORE the HTTP POST, call `markDiscovered(c.fullName, c.skillPath, c.source)` for each candidate
  2. After successful POST, update with submissionId: `markDiscovered(c.fullName, c.skillPath, c.source, subId)`
  3. On POST failure (non-201/409), the discovery record remains -- no rollback needed
- This eliminates the race window between parallel batches

**Test Plan**:
- **File**: `src/lib/crawler/__tests__/github-discovery.test.ts`
- **Tests**:
  - **TC-015**: markDiscovered is called before submission POST
    - Given a new candidate repo
    - When processRepo runs
    - Then markDiscovered is called before env.WORKER_SELF_REFERENCE.fetch
  - **TC-016**: On POST failure, discovery record persists
    - Given a candidate that was markDiscovered
    - When the submission POST returns 500
    - Then hasBeenDiscovered still returns true
  - **TC-017**: On POST success, discovery record is updated with submissionId
    - Given a successful submission POST returning submissionId
    - When processRepo completes
    - Then markDiscovered was called a second time with the submissionId

**Dependencies**: None (can be parallelized with Phase 1 and 2)

---

## Phase 4: Critical Scan → Immediate Block (US-004)

### T-010: Add critical pattern detection to scan results

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-04 | **Status**: [x] completed

**Description**: After Tier 1 scan completes, check if any matched patterns have `severity: "critical"`. If yes, transition to BLOCKED instead of TIER1_FAILED.

**Implementation Details**:
- In `process-submission.ts`, after `tier1Result` is computed (around line 451):
  1. Extract critical pattern IDs from scan results (e.g., `CI-001`, `CT-003`)
  2. If `criticalPatterns.length > 0`: transition to BLOCKED with descriptive reason
  3. If no critical patterns but still FAIL: use existing TIER1_FAILED path
- Same logic in `finalize-scan/route.ts` for VM scanner results

**Test Plan**:
- **File**: `src/lib/queue/__tests__/process-submission.critical-block.test.ts`
- **Tests**:
  - **TC-018**: Scan with critical pattern → BLOCKED state
    - Given a scan result with CI-001 (exec call, severity: critical)
    - When processSubmission processes the result
    - Then state transitions to BLOCKED (not TIER1_FAILED)
  - **TC-019**: Scan with only high/medium patterns → TIER1_FAILED state
    - Given a scan result with only high-severity patterns
    - When processSubmission processes the result
    - Then state transitions to TIER1_FAILED (unchanged behavior)
  - **TC-020**: BLOCKED reason includes specific pattern IDs
    - Given a scan with critical patterns CI-001 and CT-003
    - When BLOCKED state is set
    - Then reason contains "Immediate block: critical violations CI-001, CT-003"

**Dependencies**: T-001 (uses shared blocklist helper for entry creation)

---

### T-011: Create scoped blocklist entry on critical block

**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03, AC-US4-05 | **Status**: [x] completed

**Description**: When a submission is blocked due to critical violations, auto-create a scoped blocklist entry.

**Implementation Details**:
- After transitioning to BLOCKED, call `upsertBlocklistEntry`:
  ```typescript
  await upsertBlocklistEntry({
    skillName,
    sourceUrl: repoUrl,
    threatType: "critical-violation",
    severity: "critical",
    reason: `Immediate block: critical violations ${criticalIds.join(", ")}`,
    discoveredBy: "system:critical-scan",
  });
  ```
- This uses the updated scoped upsert from T-005

**Test Plan**:
- **File**: `src/lib/queue/__tests__/process-submission.critical-block.test.ts`
- **Tests**:
  - **TC-021**: Blocklist entry created with sourceUrl = repoUrl (scoped)
  - **TC-022**: Entry has discoveredBy = "system:critical-scan"
  - **TC-023**: Entry has severity = "critical" and threatType = "critical-violation"

**Dependencies**: T-005, T-010

---

## Phase 5: Validation

### T-012: Run full test suite

**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run `npx vitest run` in the vskill-platform repo and verify all tests pass.

**Test Plan**:
- All existing tests continue to pass
- New tests for scoped blocklist matching pass
- New tests for blocked dedup pass
- Crawler dedup ordering tests pass
- Critical scan → BLOCKED tests pass

**Dependencies**: T-001 through T-011
