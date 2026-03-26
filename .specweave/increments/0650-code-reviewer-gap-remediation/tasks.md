# Tasks: Code Reviewer Gap Remediation

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

## Phase 1: Orchestrator Updates

### T-001: Add gate check, model tiering, PR context, and finding validation to SKILL.md
**User Story**: US-001, US-002, US-003, US-006 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03, AC-US3-01, AC-US3-02, AC-US3-03, AC-US5-03, AC-US6-01 | **Status**: [x] Completed

**Description**: Update the code-reviewer SKILL.md orchestrator with 4 changes:
1. New Section 0.5 "Gate Check": for PR scope, query `gh pr view --json isDraft,state,additions,deletions`, skip if draft/closed/<5 lines. Document `--force` bypass.
2. Updated Section 1 "Smart Reviewer Routing": add reviewer-comments (any code files) and reviewer-tests (test files or testable source) to the routing table. Set model column: opus for logic/security, sonnet for all others. Update reviewer count from 6 to 8.
3. New Section 1.5 "PR Context Fetching": for PR scope, fetch title/body via `gh pr view --json title,body`. Add `[PR_TITLE]` and `[PR_BODY]` to placeholder replacement in Section 2.
4. New Section 3.5 "Finding Validation": after aggregation, spawn one haiku validator per CRITICAL/HIGH finding. Validator receives finding text + code snippet + confirm/reject/downgrade instructions. Exclude rejected findings, adjust severity on downgrades.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/skills/code-reviewer/SKILL.md`

**Implementation Details**:
- Insert Section 0.5 after Section 0 (Scope Detection), before Section 1
- Update the routing table in Section 1 to include 8 reviewers with model column
- Insert Section 1.5 after routing, before Section 2
- Update Section 2 placeholder replacement to include `[PR_TITLE]`, `[PR_BODY]`
- Insert Section 3.5 after Section 3 (Result Aggregation), before Section 4
- Update the opening paragraph to say "up to 8 specialized reviewer agents"

**Test Plan**:
- **TC-001**: Gate check section exists
  - Given the updated SKILL.md
  - When I search for "Gate Check" section
  - Then it contains `gh pr view --json isDraft,state,additions,deletions`, skip conditions for draft/closed/<5 lines, and `--force` flag documentation
- **TC-002**: Routing table has 8 reviewers with model tiering
  - Given the updated routing table in Section 1
  - When I count reviewer rows
  - Then there are 8 rows; logic and security show `opus`; performance, silent-failures, types, spec-compliance, comments, tests show `sonnet`
- **TC-003**: PR context fetching section exists
  - Given the updated SKILL.md
  - When I search for "PR Context" section
  - Then it contains `gh pr view --json title,body` and describes `[PR_TITLE]`/`[PR_BODY]` placeholder replacement
- **TC-004**: Finding validation section exists
  - Given the updated SKILL.md
  - When I search for "Finding Validation" section
  - Then it describes spawning haiku validators per CRITICAL/HIGH finding with confirm/reject/downgrade instructions

**Dependencies**: None

---

## Phase 2: Existing Agent Template Updates (Parallelizable)

### T-002: Add DO NOT FLAG and PR CONTEXT to team-lead reviewer agents [P]
**User Story**: US-004, US-006 | **Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US6-02, AC-US6-03 | **Status**: [x] Completed

**Description**: Add two new sections to each of the 3 team-lead reviewer agent templates:
1. **DO NOT FLAG** section (before RULES) with 3-5 domain-specific suppression patterns
2. **PR CONTEXT** placeholder (after REVIEW TARGET) with instructions to use it for severity calibration

Files:
- `plugins/specweave/skills/team-lead/agents/reviewer-logic.md`: DO NOT FLAG items: intentional fallthrough in switch, defensive undefined checks for optional params, explicit any in test fixtures, retry loops with intentional delays, deprecated-but-working API usage with migration plan
- `plugins/specweave/skills/team-lead/agents/reviewer-security.md`: DO NOT FLAG items: intentional timing-constant comparison for auth, bcrypt/argon2 cost factor (not "slow"), test-only credentials in fixtures, CORS * on public read-only endpoints, localhost-only development servers
- `plugins/specweave/skills/team-lead/agents/reviewer-performance.md`: DO NOT FLAG items: startup-only initialization code, admin-only endpoints with low traffic, intentional sequential awaits for ordering dependencies, small fixed-size arrays with O(n^2) ops, dev-mode verbose logging

**Implementation Details**:
- In each file, add `PR CONTEXT:\n  Title: [PR_TITLE]\n  Description: [PR_BODY]` block after the REVIEW TARGET line
- Add a line in the MISSION or RULES section: "If the PR description acknowledges a limitation or trade-off, downgrade related findings to INFO"
- Add `DO NOT FLAG:` section before the `RULES:` section in each template

**Test Plan**:
- **TC-005**: reviewer-logic.md has DO NOT FLAG section
  - Given the updated reviewer-logic.md
  - When I search for "DO NOT FLAG"
  - Then it contains at least 3 suppression patterns including "intentional fallthrough"
- **TC-006**: reviewer-security.md has DO NOT FLAG section
  - Given the updated reviewer-security.md
  - When I search for "DO NOT FLAG"
  - Then it contains at least 3 suppression patterns including "timing-constant comparison"
- **TC-007**: reviewer-performance.md has DO NOT FLAG section
  - Given the updated reviewer-performance.md
  - When I search for "DO NOT FLAG"
  - Then it contains at least 3 suppression patterns including "startup-only initialization"
- **TC-008**: All 3 team-lead templates have PR CONTEXT placeholder
  - Given the 3 updated team-lead agent templates
  - When I search for "PR CONTEXT" in each
  - Then each contains `[PR_TITLE]` and `[PR_BODY]` placeholders and severity calibration instruction

**Dependencies**: None

---

### T-003: Add DO NOT FLAG and PR CONTEXT to code-reviewer agents [P]
**User Story**: US-004, US-006 | **Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US6-02, AC-US6-03 | **Status**: [x] Completed

**Description**: Add two new sections to each of the 3 code-reviewer agent templates:
1. **DO NOT FLAG** section (before RULES) with 3-5 domain-specific suppression patterns
2. **PR CONTEXT** placeholder (after REVIEW TARGET) with instructions to use it for severity calibration

Files:
- `plugins/specweave/skills/code-reviewer/agents/reviewer-silent-failures.md`: DO NOT FLAG items: intentional empty catch for optional/best-effort operations (e.g., cleanup, telemetry), Promise.allSettled with intentional partial-failure handling, optional chaining on genuinely optional data, event emitters with documented "fire and forget" pattern, graceful degradation fallbacks with logging at debug level
- `plugins/specweave/skills/code-reviewer/agents/reviewer-types.md`: DO NOT FLAG items: explicit any in test mocks/fixtures, generic Record<string, unknown> for validated JSON parse output, type assertions in test setup code, index signatures on genuinely dynamic config objects, enums in existing codebases with consistent usage
- `plugins/specweave/skills/code-reviewer/agents/reviewer-spec-compliance.md`: DO NOT FLAG items: implementation details not mentioned in ACs (internal helper functions, private methods), code organization choices (file splitting, module structure), test utility code not traced to a specific AC, documentation improvements beyond AC scope, logging/observability additions

**Implementation Details**:
- Same pattern as T-002: PR CONTEXT block after REVIEW TARGET, DO NOT FLAG before RULES
- Same severity calibration instruction referencing PR description

**Test Plan**:
- **TC-009**: reviewer-silent-failures.md has DO NOT FLAG section
  - Given the updated reviewer-silent-failures.md
  - When I search for "DO NOT FLAG"
  - Then it contains at least 3 suppression patterns including "intentional empty catch"
- **TC-010**: reviewer-types.md has DO NOT FLAG section
  - Given the updated reviewer-types.md
  - When I search for "DO NOT FLAG"
  - Then it contains at least 3 suppression patterns including "explicit any in test mocks"
- **TC-011**: reviewer-spec-compliance.md has DO NOT FLAG section
  - Given the updated reviewer-spec-compliance.md
  - When I search for "DO NOT FLAG"
  - Then it contains at least 3 suppression patterns including "implementation details not mentioned in ACs"
- **TC-012**: All 3 code-reviewer templates have PR CONTEXT placeholder
  - Given the 3 updated code-reviewer agent templates
  - When I search for "PR CONTEXT" in each
  - Then each contains `[PR_TITLE]` and `[PR_BODY]` placeholders and severity calibration instruction

**Dependencies**: None

---

## Phase 3: New Agent Templates (Parallelizable)

### T-004: Create reviewer-comments.md agent template [P]
**User Story**: US-005, US-004, US-006 | **Satisfies ACs**: AC-US5-01, AC-US5-04, AC-US4-02, AC-US6-02, AC-US6-03 | **Status**: [x] Completed

**Description**: Create a new agent template at `plugins/specweave/skills/code-reviewer/agents/reviewer-comments.md` for comment accuracy analysis.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/skills/code-reviewer/agents/reviewer-comments.md`

**Implementation Details**:
- Follow the exact structure of reviewer-silent-failures.md as the reference template
- MISSION: find stale comments, misleading docstrings, TODO/FIXME debt, comment-code contradictions, and outdated JSDoc @param/@returns
- CHECKLIST: 8-10 items covering stale comments, misleading descriptions, TODO/FIXME/HACK/XXX debt older than the current change, parameter name mismatches in JSDoc, return type documentation drift, commented-out code blocks, copy-paste comments from other functions, license header staleness
- OUTPUT FORMAT: same structured findings format as other reviewers
- COMMUNICATION: SendMessage to team-lead with REVIEW_COMPLETE signal
- DO NOT FLAG: auto-generated comments (e.g., from codegen tools), TODO items with linked issue numbers, inline type annotations that serve as documentation, comments in test files describing test intent, license headers
- PR CONTEXT: `[PR_TITLE]` and `[PR_BODY]` placeholders with severity calibration
- RULES: same base rules (READ-ONLY, specific file:line, prioritize CRITICAL/HIGH)

**Test Plan**:
- **TC-013**: reviewer-comments.md exists and has correct structure
  - Given the new reviewer-comments.md file
  - When I check its sections
  - Then it contains MISSION, REVIEW TARGET, PR CONTEXT, SCOPE, CHECKLIST, OUTPUT FORMAT, DO NOT FLAG, COMMUNICATION, and RULES sections
- **TC-014**: reviewer-comments.md mission covers required categories
  - Given the MISSION section of reviewer-comments.md
  - When I check for required analysis types
  - Then it mentions stale comments, misleading docstrings, TODO/FIXME debt, and comment-code contradictions
- **TC-015**: reviewer-comments.md follows communication protocol
  - Given the COMMUNICATION section
  - When I check the SendMessage format
  - Then it signals REVIEW_COMPLETE to team-lead with finding counts

**Dependencies**: None

---

### T-005: Create reviewer-tests.md agent template [P]
**User Story**: US-005, US-004, US-006 | **Satisfies ACs**: AC-US5-02, AC-US5-04, AC-US4-02, AC-US6-02, AC-US6-03 | **Status**: [x] Completed

**Description**: Create a new agent template at `plugins/specweave/skills/code-reviewer/agents/reviewer-tests.md` for test coverage analysis.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/skills/code-reviewer/agents/reviewer-tests.md`

**Implementation Details**:
- Follow the exact structure of reviewer-silent-failures.md as the reference template
- MISSION: find missing test coverage for changed code, weak assertions, test-production drift, and test anti-patterns
- CHECKLIST: 8-10 items covering untested public functions/exports, assertions that only check truthiness (expect(result).toBeTruthy()) instead of specific values, test files that import mocks but never assert on mock calls, changed production code with no corresponding test changes, snapshot tests covering dynamic content, test descriptions that don't match what the test actually verifies, missing edge case coverage (null, empty, boundary), flaky test patterns (timing-dependent, order-dependent)
- OUTPUT FORMAT: same structured findings format as other reviewers
- COMMUNICATION: SendMessage to team-lead with REVIEW_COMPLETE signal
- DO NOT FLAG: test utility/helper files without their own tests, E2E tests that intentionally cover broad flows, test setup code (beforeEach/afterEach) without assertions, generated test scaffolds, configuration-only test files
- PR CONTEXT: `[PR_TITLE]` and `[PR_BODY]` placeholders with severity calibration
- RULES: same base rules (READ-ONLY, specific file:line, prioritize CRITICAL/HIGH)

**Test Plan**:
- **TC-016**: reviewer-tests.md exists and has correct structure
  - Given the new reviewer-tests.md file
  - When I check its sections
  - Then it contains MISSION, REVIEW TARGET, PR CONTEXT, SCOPE, CHECKLIST, OUTPUT FORMAT, DO NOT FLAG, COMMUNICATION, and RULES sections
- **TC-017**: reviewer-tests.md mission covers required categories
  - Given the MISSION section of reviewer-tests.md
  - When I check for required analysis types
  - Then it mentions missing test coverage, weak assertions, test-production drift, and test anti-patterns
- **TC-018**: reviewer-tests.md follows communication protocol
  - Given the COMMUNICATION section
  - When I check the SendMessage format
  - Then it signals REVIEW_COMPLETE to team-lead with finding counts

**Dependencies**: None

---

## Phase 4: Verification

### T-006: Verify all templates have consistent structure
**User Story**: US-004, US-005, US-006 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US5-04, AC-US6-02 | **Status**: [x] Completed

**Description**: Read all 8 agent templates and verify structural consistency: every template has DO NOT FLAG section, PR CONTEXT placeholder, standard OUTPUT FORMAT, COMMUNICATION protocol with REVIEW_COMPLETE signal, and RULES section.

**Implementation Details**:
- Read all 8 agent templates
- Verify each contains: DO NOT FLAG (3-5 items), PR CONTEXT with [PR_TITLE] and [PR_BODY], OUTPUT FORMAT with severity levels, COMMUNICATION with REVIEW_COMPLETE SendMessage, RULES with READ-ONLY constraint
- Verify SKILL.md routing table has 8 entries with correct model assignments
- Verify SKILL.md has gate check, PR context fetching, and finding validation sections

**Test Plan**:
- **TC-019**: All 8 templates have DO NOT FLAG
  - Given all 8 agent template files
  - When I search for "DO NOT FLAG" in each
  - Then all 8 contain the section with at least 3 items each
- **TC-020**: All 8 templates have PR CONTEXT
  - Given all 8 agent template files
  - When I search for "PR CONTEXT" in each
  - Then all 8 contain [PR_TITLE] and [PR_BODY] placeholders
- **TC-021**: SKILL.md routing table is complete
  - Given the updated SKILL.md
  - When I check the routing table
  - Then it has 8 reviewer entries with correct model assignments (2 opus, 6 sonnet)

**Dependencies**: T-001, T-002, T-003, T-004, T-005
