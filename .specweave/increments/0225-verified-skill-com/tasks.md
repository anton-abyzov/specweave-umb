# Tasks: Build & Deploy verified-skill.com

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: CLI Unit Tests (vskill)

### US-011: E2E Testing & Quality (P1)

#### T-001: Scanner patterns unit tests

**Description**: Write comprehensive unit tests for all 37 security scan patterns in `src/scanner/patterns.ts`

**References**: AC-US11-05, AC-US11-06

**Implementation Details**:
- Test each pattern category: command-injection, data-exfiltration, privilege-escalation, credential-theft, prompt-injection, filesystem-access, network-access, code-execution
- Test `scanContent()` returns correct findings with line numbers and context
- Test clean content returns zero findings

**Test Plan**:
- **File**: `src/scanner/patterns.test.ts`
- **Tests**:
  - **TC-001**: scanContent detects command injection patterns (exec, spawn, system)
  - **TC-002**: scanContent detects data exfiltration patterns (fetch, XMLHttpRequest, WebSocket)
  - **TC-003**: scanContent detects privilege escalation patterns (sudo, chmod, chown)
  - **TC-004**: scanContent detects credential theft patterns (.env, SSH keys, AWS)
  - **TC-005**: scanContent detects prompt injection patterns (system prompt override)
  - **TC-006**: scanContent detects filesystem access patterns (rm -rf, path traversal)
  - **TC-007**: scanContent detects network access patterns (curl/wget, reverse shell)
  - **TC-008**: scanContent detects code execution patterns (eval, Function constructor)
  - **TC-009**: scanContent returns empty array for clean content
  - **TC-010**: findings include correct line numbers and context

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Tier 1 scanner unit tests

**Description**: Write unit tests for `src/scanner/tier1.ts` scoring logic and verdict determination

**References**: AC-US11-05, AC-US11-06

**Implementation Details**:
- Test score deductions per severity (critical=25, high=15, medium=8, low=3, info=0)
- Test verdict thresholds (PASS >= 80, CONCERNS 50-79, FAIL < 50)
- Test duration tracking

**Test Plan**:
- **File**: `src/scanner/tier1.test.ts`
- **Tests**:
  - **TC-011**: Clean content scores 100 with PASS verdict
  - **TC-012**: Single critical finding deducts 25 points
  - **TC-013**: Multiple findings accumulate deductions correctly
  - **TC-014**: Score clamps to 0 minimum
  - **TC-015**: Verdict CONCERNS for score 50-79
  - **TC-016**: Verdict FAIL for score below 50
  - **TC-017**: Returns correct patternsChecked count
  - **TC-018**: Returns severity counts (criticalCount, highCount, etc.)

**Dependencies**: T-001
**Status**: [x] Completed

---

#### T-003: Agent registry unit tests

**Description**: Write unit tests for the 39-agent registry in `src/agents/agents-registry.ts`

**References**: AC-US8-05, AC-US11-06

**Implementation Details**:
- Test AGENTS_REGISTRY contains exactly 39 agents
- Test 7 universal + 32 non-universal split
- Test each agent has required fields
- Test detectInstalledAgents function

**Test Plan**:
- **File**: `src/agents/agents-registry.test.ts`
- **Tests**:
  - **TC-019**: Registry contains exactly 39 agents
  - **TC-020**: Exactly 7 agents are universal
  - **TC-021**: Each agent has required fields (id, displayName, localSkillsDir, globalSkillsDir)
  - **TC-022**: No duplicate agent IDs
  - **TC-023**: All agents have parentCompany defined
  - **TC-024**: detectInstalledAgents returns array of detected agents

**Dependencies**: None
**Status**: [x] Completed

---

#### T-004: Lockfile unit tests

**Description**: Write unit tests for `src/lockfile/lockfile.ts` operations

**References**: AC-US8-06, AC-US11-06

**Implementation Details**:
- Test readLockfile, writeLockfile, ensureLockfile, addSkillToLock, removeSkillFromLock
- Mock fs operations

**Test Plan**:
- **File**: `src/lockfile/lockfile.test.ts`
- **Tests**:
  - **TC-025**: readLockfile returns null when no lockfile exists
  - **TC-026**: readLockfile parses valid lockfile
  - **TC-027**: writeLockfile writes valid JSON
  - **TC-028**: ensureLockfile creates new lockfile when missing
  - **TC-029**: ensureLockfile returns existing lockfile
  - **TC-030**: addSkillToLock adds entry and updates timestamp
  - **TC-031**: removeSkillFromLock removes entry

**Dependencies**: None
**Status**: [x] Completed

---

#### T-005: API client unit tests

**Description**: Write unit tests for `src/api/client.ts` HTTP client

**References**: AC-US11-06

**Implementation Details**:
- Mock global fetch
- Test all 4 API functions: searchSkills, getSkill, submitSkill, getSubmission
- Test error handling

**Test Plan**:
- **File**: `src/api/client.test.ts`
- **Tests**:
  - **TC-032**: searchSkills sends correct URL and returns parsed results
  - **TC-033**: getSkill fetches skill by name
  - **TC-034**: submitSkill POSTs correct payload
  - **TC-035**: getSubmission fetches status by ID
  - **TC-036**: API errors throw with proper messages

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 2: Platform Unit Tests (vskill-platform)

#### T-006: State machine unit tests

**Description**: Write unit tests for `src/lib/pipeline/submission-machine.ts`

**References**: AC-US3-03, AC-US11-06

**Implementation Details**:
- Test all valid transitions
- Test invalid transitions return valid: false
- Test vendor detection
- Test tier2_pass guard (score >= 80)

**Test Plan**:
- **File**: `src/lib/pipeline/__tests__/submission-machine.test.ts`
- **Tests**:
  - **TC-037**: RECEIVED → TIER1_SCANNING via start_scan
  - **TC-038**: TIER1_SCANNING → TIER1_FAILED via tier1_fail
  - **TC-039**: TIER1_SCANNING → TIER2_SCANNING via tier1_pass
  - **TC-040**: TIER2_SCANNING → AUTO_APPROVED via tier2_pass (score >= 80)
  - **TC-041**: TIER2_SCANNING → NEEDS_REVIEW via tier2_concerns
  - **TC-042**: NEEDS_REVIEW → PUBLISHED via admin_approve
  - **TC-043**: NEEDS_REVIEW → REJECTED via admin_reject
  - **TC-044**: Invalid transition returns valid: false
  - **TC-045**: getInitialState returns VENDOR_APPROVED for vendor repos
  - **TC-046**: getInitialState returns RECEIVED for non-vendor repos
  - **TC-047**: isVendorRepo recognizes anthropics, openai, google-gemini orgs
  - **TC-048**: tier2_pass with score < 80 is invalid

**Dependencies**: None
**Status**: [x] Completed

---

#### T-007: Platform scanner unit tests

**Description**: Write unit tests for `src/lib/scanner/` (tier1, tier2, full scan)

**References**: AC-US3-01, AC-US3-02, AC-US3-08, AC-US11-05

**Implementation Details**:
- Test tier1 scan logic (same patterns as CLI)
- Test tier2 LLM scan with mocked AI binding
- Test runFullScan combines results correctly

**Test Plan**:
- **File**: `src/lib/scanner/__tests__/scanner.test.ts`
- **Tests**:
  - **TC-049**: Tier 1 scan detects all pattern categories
  - **TC-050**: Tier 1 scoring matches CLI implementation
  - **TC-051**: Tier 2 scan sends correct prompt to AI
  - **TC-052**: Tier 2 parses valid JSON response
  - **TC-053**: Tier 2 handles malformed AI response gracefully
  - **TC-054**: Full scan returns overall verdict as worst of both tiers
  - **TC-055**: Full scan score averages both tier scores
  - **TC-056**: Full scan skips Tier 2 when no AI binding provided

**Dependencies**: None
**Status**: [x] Completed

---

#### T-008: Auth unit tests

**Description**: Write unit tests for `src/lib/auth.ts` JWT and password logic

**References**: AC-US7-01, AC-US7-02, AC-US11-06

**Implementation Details**:
- Test JWT sign/verify for access and refresh tokens
- Test password hashing and verification
- Test role hierarchy
- Test requireAuth and requireRole middleware

**Test Plan**:
- **File**: `src/lib/__tests__/auth.test.ts`
- **Tests**:
  - **TC-057**: signAccessToken creates valid JWT with 24h expiry
  - **TC-058**: verifyAccessToken validates correct token
  - **TC-059**: verifyAccessToken rejects expired token
  - **TC-060**: signRefreshToken includes type: 'refresh'
  - **TC-061**: hashPassword returns bcrypt hash
  - **TC-062**: verifyPassword matches correct password
  - **TC-063**: verifyPassword rejects wrong password
  - **TC-064**: requireRole enforces SUPER_ADMIN > REVIEWER hierarchy
  - **TC-065**: requireAuth extracts Bearer token from Authorization header

**Dependencies**: None
**Status**: [x] Completed

---

#### T-009: API helpers unit tests

**Description**: Write unit tests for `src/lib/api-helpers.ts` Zod schemas and response builders

**References**: AC-US2-07, AC-US11-06

**Implementation Details**:
- Test Zod validation schemas
- Test pagination parsing
- Test response formatting

**Test Plan**:
- **File**: `src/lib/__tests__/api-helpers.test.ts`
- **Tests**:
  - **TC-066**: SubmissionCreateSchema validates valid GitHub URLs
  - **TC-067**: SubmissionCreateSchema rejects non-GitHub URLs
  - **TC-068**: LoginSchema requires email and password
  - **TC-069**: parsePaginationParams extracts page/limit with defaults
  - **TC-070**: parseSkillSearchParams extracts all filter params
  - **TC-071**: jsonResponse returns NextResponse with correct status
  - **TC-072**: errorResponse returns error JSON

**Dependencies**: None
**Status**: [x] Completed

---

#### T-010: Data layer unit tests

**Description**: Write unit tests for `src/lib/data.ts` in-memory data operations

**References**: AC-US2-02, AC-US2-03, AC-US11-06

**Implementation Details**:
- Test skill filtering, sorting, pagination
- Test submission creation and state updates
- Test search functionality

**Test Plan**:
- **File**: `src/lib/__tests__/data.test.ts`
- **Tests**:
  - **TC-073**: getSkills returns paginated results
  - **TC-074**: getSkills filters by category
  - **TC-075**: getSkills sorts by installs, trending, newest
  - **TC-076**: getSkillByName returns skill or null
  - **TC-077**: searchSkills matches by name and description
  - **TC-078**: submitSkill creates submission with generated ID
  - **TC-079**: updateSubmissionState changes state and adds history
  - **TC-080**: getTrendingSkills returns top N by trending score

**Dependencies**: None
**Status**: [x] Completed

---

#### T-011: Email module unit tests

**Description**: Write unit tests for `src/lib/email.ts` with mocked SendGrid

**References**: AC-US10-01, AC-US10-02, AC-US11-06

**Implementation Details**:
- Mock @sendgrid/mail
- Test all 5 notification types
- Test HTML escaping

**Test Plan**:
- **File**: `src/lib/__tests__/email.test.ts`
- **Tests**:
  - **TC-081**: sendSubmissionReceived sends correct template
  - **TC-082**: sendAutoApproved includes badge URL
  - **TC-083**: sendNeedsReview lists concerns
  - **TC-084**: sendRejected includes reason
  - **TC-085**: escapeHtml prevents XSS
  - **TC-086**: Email is not sent when no recipient provided

**Dependencies**: None
**Status**: [x] Completed

---

## Phase 3: Run & Fix

#### T-012: Run all CLI tests and fix failures

**Description**: Execute `npm test` in vskill repo and fix any failing tests

**References**: AC-US11-05, AC-US11-06

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Status**: [x] Completed

---

#### T-013: Run all platform tests and fix failures

**Description**: Execute `npm test` in vskill-platform repo and fix any failing tests

**References**: AC-US11-05, AC-US11-06

**Dependencies**: T-006, T-007, T-008, T-009, T-010, T-011
**Status**: [x] Completed

---

## Phase 4: Verification

#### T-014: Verify all ACs and mark complete

**Description**: Review all 67 ACs across 11 user stories, mark satisfied ones complete

**References**: All ACs

**Dependencies**: T-012, T-013
**Status**: [x] Completed
