---
increment: 0388-pattern-guided-llm-verdict
title: Task Breakdown
---

# Tasks: Pattern-Guided LLM Verdict

## Phase 1: Scanner Parity (crawl-worker ← platform)

### T-001: Port inline code detection to scanner-patterns.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given a SKILL.md line `"Watch for: \`eval()\`, \`exec()\`"` → When scanned by crawl-worker scanner-patterns.js → Then CE-001 and CI-001 findings have severity "info" (not "critical")

**Implementation**:
- Copy `isInsideInlineCode()` function from `patterns.ts` to `scanner-patterns.js`
- Add inline code downgrade logic to `scanContent()` in `scanner-patterns.js`
- Exclude DCI-abuse patterns from downgrade (same as platform)

---

### T-002: Port markdown prose line detection to scanner-patterns.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given a SKILL.md line `"- Requires sudo privileges"` → When scanned by crawl-worker → Then PE-001 finding has severity "info" (not "high")

**Implementation**:
- Copy `isMarkdownProseLine()` and `MARKDOWN_PROSE_RE` from `patterns.ts`
- Add prose line downgrade logic to `scanContent()` in `scanner-patterns.js`
- Only applies to patterns in `DOCUMENTATION_SAFE_PATTERNS` set

---

### T-003: Port spawn context detection to scanner-patterns.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given `spawn('node', ['script.js'])` → When scanned → Then CI-002 severity is "info". Given `spawn(cmd)` → Then CI-002 severity is "medium".

**Implementation**:
- Copy `SAFE_SPAWN_TARGETS`, `isSpawnWithSafeTarget()`, `isSpawnWithDangerousPattern()`
- Add CI-002 context-aware severity in `scanContent()`

---

### T-004: Port CI-005 exec-like context detection to scanner-patterns.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given `require('child_process')` → CI-005 severity "low". Given `execSync('npm install')` → severity "info". Given `execSync(cmd)` → severity "high".

**Implementation**:
- Copy `isCi005Import()`, `isExecLikeWithSafeTarget()`, `isExecLikeWithDangerousPattern()`
- Add CI-005 context-aware severity in `scanContent()`

---

### T-005: Port CT-003 safe reference detection to scanner-patterns.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given `AWS_SECRET_ACCESS_KEY=your-key-here` → CT-003 severity "info". Given `.aws/credentials` with file read → severity "critical".

**Implementation**:
- Copy `isCt003SafeReference()` from `patterns.ts`
- Add CT-003 context-aware severity in `scanContent()`

---

### T-006: Update DOCUMENTATION_SAFE_PATTERNS and base severities in scanner-patterns.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06, AC-US1-07, AC-US1-08, AC-US1-09, AC-US1-10 | **Status**: [x] completed
**Test Plan**: Given `DOCUMENTATION_SAFE_PATTERNS` set → Then includes CI-002, CI-004, CI-005, DE-005, NA-003. Given CI-002 pattern definition → Then base severity is "low" (not "medium").

**Implementation**:
- Update `DOCUMENTATION_SAFE_PATTERNS` to match platform: add CI-002, CI-004, CI-005, DE-005, NA-003
- Change CI-002 base severity from "medium" to "low"
- Change DE-005 base severity from "medium" to "low"
- Change NA-003 base severity from "medium" to "low"

---

## Phase 2: Negation Context Detection

### T-007: Add negation detection to patterns.ts (platform)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06, AC-US2-07, AC-US2-08 | **Status**: [x] completed
**Test Plan**: Given `"Don't use eval()"` → CE-001 severity "info". Given `"Never call exec()"` → CI-001 severity "info". Given `eval(userInput)` → CE-001 severity "critical". Given DCI line with "don't" → DCI severity stays "critical".

**Implementation**:
- Add `NEGATION_WORDS` array and `isNegatedContext(line, matchStart)` function
- In `scanContent()`, after existing downgrades, check negation for non-DCI patterns
- When negation detected, downgrade severity to "info"

---

### T-008: Add negation detection to scanner-patterns.js (crawl-worker)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Same test cases as T-007 but running against crawl-worker scanner.

**Implementation**:
- Mirror T-007 implementation in `scanner-patterns.js`
- Same negation words, same lookback window, same DCI exclusion

---

## Phase 3: Tier 2 Prompt Enhancement

### T-009: Enhance Tier 2 prompt with critical finding validation (platform)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given Tier 1 with criticalCount > 0 → When Tier 2 prompt is built → Then prompt includes "Critical Findings Validation" section with each critical listed. Given LLM response with `criticalValidation` array → Then parser extracts it into Tier2Result.

**Implementation**:
- In `tier2.ts`, when building user prompt, add critical findings validation section if `tier1Result.criticalCount > 0`
- Each critical finding listed with patternId, match text, 3-line context
- Update response JSON schema to include `criticalValidation` array
- Update `Tier2Result` type to include `criticalValidation?: {patternId: string, verdict: "confirmed"|"false_positive", reason: string}[]`
- Update `parseAnalysisResponse()` to extract `criticalValidation`

---

### T-010: Mirror Tier 2 prompt changes to crawl-worker tier2-scan.js
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Test Plan**: Given crawl-worker Tier 2 scan with critical findings → When prompt is built → Then includes same critical validation section as platform version.

**Implementation**:
- Mirror T-009 prompt enhancement in `tier2-scan.js`
- Mirror `criticalValidation` parsing in `parseAnalysisResponse()`

---

## Phase 4: Routing Logic Changes

### T-011: Replace critical auto-block in finalize-scan with Tier 2 routing
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-06 | **Status**: [x] completed
**Test Plan**: Given T1 with criticals + T2 with all false_positive validations → Then submission NOT blocked, proceeds normally. Given T1 with criticals + T2 confirming threats → Then submission BLOCKED. Given T1 with criticals + no T2 + all criticals downgraded to info → Then submission proceeds. Given T1 with criticals + no T2 + real criticals → Then submission BLOCKED.

**Implementation**:
- Replace `if (tier1.criticalCount > 0)` block in finalize-scan route
- New logic:
  1. Count "real" criticals (severity still "critical" after downgrades)
  2. If T2 present with criticalValidation: block only if any are "confirmed"
  3. If T2 present without criticalValidation: use T2 overall verdict (FAIL → block)
  4. If no T2 and no real criticals (all downgraded): proceed normally
  5. If no T2 and real criticals: BLOCKED (safety fallback)

---

### T-012: Remove early T1-fail exit for criticals in submission-scanner.js
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [x] completed
**Test Plan**: Given T1 scan with critical findings and T2 credentials available → When submission is processed → Then T2 scan runs (not skipped). Given T1 score < 40 with no criticals → Then early finalize still fires.

**Implementation**:
- In `submission-scanner.js`, modify the T1 fail early-exit (step 13)
- If `tier1Result.criticalCount > 0` and T2 credentials available: skip early exit, proceed to T2
- Keep early exit for non-critical T1 failures (score < 40 with criticalCount = 0)
- After T2 runs, send results to finalize-scan (which handles the critical validation)

---

## Phase 5: Testing & Verification

### T-013: Add cross-scanner parity test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 through AC-US1-10 | **Status**: [x] completed
**Test Plan**: Given a set of test inputs (educational content, malicious content, borderline content) → When run through both patterns.ts and scanner-patterns.js scanners → Then both produce identical finding severities for every pattern match.

**Implementation**:
- Create test file that imports both scanners
- Run same inputs through both
- Assert severity parity for each finding
- Include edge cases: inline code, negation, markdown prose, DCI blocks
