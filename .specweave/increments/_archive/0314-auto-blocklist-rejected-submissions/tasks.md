# Tasks: Auto-Blocklist Rejected Queue Submissions

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Service (TDD)

### US-003: Blocklist Upsert with Severity Escalation (P1)

#### T-001: Implement threat type mapper
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Description**: Create `src/lib/scanner/threat-type-mapper.ts` -- a pure function that maps Tier 1 scanner `PatternCategory` values to blocklist `threatType` values.

**Implementation Details**:
- Map `command-injection` -> "malicious-code"
- Map `data-exfiltration` -> "data-exfiltration"
- Map `privilege-escalation` -> "malicious-code"
- Map `credential-theft` -> "credential-theft"
- Map `prompt-injection` -> "prompt-injection"
- Default fallback -> "policy-violation"
- Export `mapCategoryToThreatType(category: PatternCategory): string`
- Export `inferThreatTypeFromFindings(findings: ScanFinding[]): string` that picks the most severe finding's category

**Test Plan (TDD -- write tests FIRST)**:
- **File**: `src/lib/scanner/__tests__/threat-type-mapper.test.ts`
- **Tests**:
  - **TC-001**: Maps each PatternCategory to the correct threatType
    - Given each of the 5 categories
    - When `mapCategoryToThreatType` is called
    - Then returns the mapped threatType
  - **TC-002**: inferThreatTypeFromFindings picks the most severe category
    - Given findings with mixed severities and categories
    - When `inferThreatTypeFromFindings` is called
    - Then returns the threatType of the highest-severity finding
  - **TC-003**: inferThreatTypeFromFindings returns "policy-violation" for empty findings
    - Given an empty findings array
    - When `inferThreatTypeFromFindings` is called
    - Then returns "policy-violation"

**Dependencies**: None
**Model**: haiku

---

#### T-002: Implement blocklist upsert service
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [x] completed

**Description**: Create `src/lib/blocklist-upsert.ts` with a shared `upsertBlocklistEntry()` function used by both auto-blocklist and admin reject flows.

**Implementation Details**:
- Accept `UpsertBlocklistInput` (skillName, sourceUrl, sourceRegistry, threatType, severity, reason, evidenceUrls, discoveredBy)
- Check for existing entry: `findFirst({ where: { skillName, sourceRegistry, isActive: true } })`
- If exists:
  - Escalate severity only (critical=4 > high=3 > medium=2 > low=1, keep higher)
  - Merge `evidenceUrls` arrays (union, deduplicate)
  - Update `reason` to latest
  - Preserve original `discoveredAt` and `discoveredBy`
  - Refresh `updatedAt` (automatic via Prisma @updatedAt)
  - Return `{ action: "updated", entry }`
- If new:
  - Create entry with all provided fields
  - Return `{ action: "created", entry }`
- Use Prisma transaction for atomicity of the find+update/create

**Test Plan (TDD -- write tests FIRST)**:
- **File**: `src/lib/__tests__/blocklist-upsert.test.ts`
- **Tests**:
  - **TC-004**: Creates new blocklist entry when none exists
    - Given no existing entry for skillName
    - When `upsertBlocklistEntry` is called
    - Then a new entry is created with action "created"
  - **TC-005**: Updates existing entry with severity escalation
    - Given an existing entry with severity "medium"
    - When `upsertBlocklistEntry` is called with severity "critical"
    - Then severity is updated to "critical" with action "updated"
  - **TC-006**: Does NOT downgrade severity
    - Given an existing entry with severity "critical"
    - When `upsertBlocklistEntry` is called with severity "low"
    - Then severity remains "critical"
  - **TC-007**: Merges evidenceUrls arrays
    - Given an existing entry with evidenceUrls ["url1"]
    - When `upsertBlocklistEntry` is called with evidenceUrls ["url2", "url1"]
    - Then evidenceUrls becomes ["url1", "url2"] (union, deduplicated)
  - **TC-008**: Preserves original discoveredAt and discoveredBy
    - Given an existing entry created by "admin-alice" at time T1
    - When `upsertBlocklistEntry` is called by "system:tier1-scan"
    - Then discoveredBy remains "admin-alice" and discoveredAt remains T1
  - **TC-009**: Updates reason to latest
    - Given an existing entry with reason "old reason"
    - When `upsertBlocklistEntry` is called with reason "new reason"
    - Then reason becomes "new reason"

**Dependencies**: None
**Model**: opus

---

## Phase 2: Pipeline Integration

### US-001: Auto-Blocklist on Critical Tier 1 Failure (P1)

#### T-003: Wire auto-blocklist into processSubmission
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Description**: Modify `src/lib/queue/process-submission.ts` to call `upsertBlocklistEntry()` after a TIER1_FAILED rejection when `criticalCount > 0`.

**Implementation Details**:
- After the `if (tier1Result.verdict === "FAIL" || tier1WeightedScore < 50)` block at line ~199
- Add check: only if `tier1Result.criticalCount > 0`
- Call `inferThreatTypeFromFindings(tier1Result.findings)` for threatType
- Determine severity from highest finding severity
- Call `upsertBlocklistEntry()` wrapped in try/catch
  - On success: log "Auto-blocklist entry {created|updated} for {skillName}"
  - On failure: `console.error()` only, never throw
- The rejection state update (line 200-201) already runs before this hook
- Do NOT auto-blocklist on missing SKILL.md rejections (line 136-138, those have 0 findings)
- Include submission repoUrl as sourceUrl in the blocklist entry

**Test Plan (TDD -- write tests FIRST)**:
- **File**: `src/lib/queue/__tests__/process-submission-autoblocklist.test.ts`
- **Tests**:
  - **TC-010**: Auto-blocklists on Tier 1 FAIL with criticalCount > 0
    - Given a submission with Tier 1 result: verdict FAIL, criticalCount 2
    - When processSubmission completes
    - Then upsertBlocklistEntry is called with inferred threatType and severity
  - **TC-011**: Does NOT auto-blocklist on low-score rejection (criticalCount 0)
    - Given a submission with Tier 1 result: verdict FAIL, score 30, criticalCount 0
    - When processSubmission completes
    - Then upsertBlocklistEntry is NOT called
  - **TC-012**: Does NOT auto-blocklist on missing SKILL.md rejection
    - Given a submission with no SKILL.md found
    - When processSubmission completes
    - Then upsertBlocklistEntry is NOT called
  - **TC-013**: Rejection succeeds even if blocklist upsert throws
    - Given a submission with criticalCount > 0 and upsertBlocklistEntry throws
    - When processSubmission completes
    - Then the submission state is TIER1_FAILED (rejection succeeded)
  - **TC-014**: Auto-blocklist sets discoveredBy to "system:tier1-scan"
    - Given a critical Tier 1 failure
    - When processSubmission auto-blocklists
    - Then the entry has discoveredBy "system:tier1-scan"

**Dependencies**: T-001, T-002
**Model**: opus

---

### US-002: Admin Opt-In Blocklist on Manual Rejection (P1)

#### T-004: Add blocklist opt-in to admin reject API
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04, AC-US2-05, AC-US2-06, AC-US4-01 | **Status**: [x] completed

**Description**: Modify `src/app/api/v1/admin/submissions/[id]/route.ts` PATCH handler to accept optional blocklist fields and call `upsertBlocklistEntry()` on rejection with opt-in.

**Implementation Details**:
- Add optional fields to request body parsing: `addToBlocklist?: boolean`, `threatType?: string`, `severity?: string`
- When `action === "reject" && addToBlocklist === true`:
  - Validate `threatType` against allowed values (prompt-injection, credential-theft, malicious-code, policy-violation, admin-rejected)
  - Default `severity` to "medium" if not provided
  - Call `upsertBlocklistEntry()` with:
    - skillName from submission
    - sourceUrl from submission.repoUrl
    - reason from the rejection reason
    - discoveredBy: admin user identifier
  - Wrap in try/catch, log failures
- Augment response with `blocklistAction: "created" | "updated" | null`
- Note: This route currently uses mock data. The blocklist call needs real DB access via `getDb()`.

**Test Plan (TDD -- write tests FIRST)**:
- **File**: `src/app/api/v1/admin/submissions/[id]/__tests__/route.blocklist.test.ts`
- **Tests**:
  - **TC-015**: Reject with addToBlocklist creates blocklist entry
    - Given a valid reject request with addToBlocklist: true, threatType: "admin-rejected", severity: "medium"
    - When PATCH is called
    - Then response includes blocklistAction: "created"
  - **TC-016**: Reject without addToBlocklist does NOT create blocklist entry
    - Given a reject request without addToBlocklist
    - When PATCH is called
    - Then response includes blocklistAction: null
  - **TC-017**: Reject succeeds even if blocklist upsert throws
    - Given addToBlocklist: true and upsertBlocklistEntry throws
    - When PATCH is called
    - Then response status is 200 with the rejection confirmed
  - **TC-018**: Invalid threatType returns 400
    - Given addToBlocklist: true with threatType: "invalid-type"
    - When PATCH is called
    - Then response status is 400
  - **TC-019**: Reject with addToBlocklist uses rejection reason as blocklist reason
    - Given a reject request with reason "Malicious prompt injection" and addToBlocklist: true
    - When PATCH is called
    - Then blocklist entry reason is "Malicious prompt injection"

**Dependencies**: T-002
**Model**: opus

---

## Phase 3: UI Updates

### US-002: Admin Opt-In Blocklist on Manual Rejection (P1)
### US-004: Blocklist Action Feedback (P2)

#### T-005: Add blocklist checkbox and feedback to admin reject form
**User Story**: US-002, US-004 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US4-02 | **Status**: [x] completed

**Description**: Update `src/app/admin/submissions/[id]/page.tsx` to add an "Also add to blocklist" checkbox to the reject action, with conditional threatType/severity dropdowns and inline feedback toast.

**Implementation Details**:
- Add state: `addToBlocklist: boolean` (default false)
- Add state: `rejectThreatType: string` (default "admin-rejected")
- Add state: `rejectSeverity: string` (default "medium")
- When "reject" action is used:
  - Show checkbox: "Also add to blocklist" (unchecked by default)
  - When checked, show threatType dropdown (options: prompt-injection, credential-theft, malicious-code, policy-violation, admin-rejected) and severity dropdown (critical, high, medium)
  - Include these fields in the PATCH request body
- On response with `blocklistAction`:
  - Show inline toast: "Blocklist entry created" or "Blocklist entry updated"
  - Toast auto-dismisses after 4 seconds
- Note: The current page already has a separate "Add to Blocklist" button for REJECTED/TIER1_FAILED states. The new checkbox is specifically on the reject action itself, not the post-hoc blocklist button.

**Test Plan (TDD -- write tests FIRST)**:
- **File**: `src/app/admin/submissions/[id]/__tests__/page.blocklist.test.tsx`
- **Tests**:
  - **TC-020**: Reject form shows "Also add to blocklist" checkbox
    - Given the admin is viewing a submission in reviewable state
    - When the reject action is initiated
    - Then a checkbox "Also add to blocklist" is visible
  - **TC-021**: Checking the checkbox reveals threatType and severity dropdowns
    - Given the "Also add to blocklist" checkbox
    - When the checkbox is checked
    - Then threatType dropdown (defaulting to "admin-rejected") and severity dropdown (defaulting to "medium") appear
  - **TC-022**: Unchecking the checkbox hides the dropdowns
    - Given the threatType/severity dropdowns are visible
    - When the checkbox is unchecked
    - Then the dropdowns are hidden
  - **TC-023**: Toast appears when blocklistAction is in response
    - Given a reject request returns blocklistAction: "created"
    - When the response is received
    - Then an inline toast "Blocklist entry created" appears

**Dependencies**: T-004
**Model**: opus

---

## Phase 4: Verification

#### T-006: Integration verification and AC sign-off
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run full test suite, verify all acceptance criteria, and confirm end-to-end flow.

**Implementation Details**:
- Run `npm run test` in vskill-platform to verify all tests pass
- Run `npm run build` to verify no build errors
- Manually verify each AC against the implementation
- Check that test coverage meets 80% target for new files

**Test Plan**:
- All TC-001 through TC-023 pass
- Build succeeds with no TypeScript errors
- Coverage report shows >= 80% for new files

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Model**: haiku
