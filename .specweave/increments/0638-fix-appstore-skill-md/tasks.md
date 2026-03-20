# Tasks: Fix appstore skill security scan false positives

## Domain: Scanner

### T-001: Write failing tests for CT-004 pattern narrowing
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given CT-004 pattern, When scanning `ASC_BYPASS_KEYCHAIN` or "macOS Keychain is unavailable", Then no finding is produced
- Given CT-004 pattern, When scanning `security default-keychain` or `SecKeychainFindGenericPassword` or `keychain.get(`, Then a critical finding is produced

### T-002: Narrow CT-004 regex pattern in patterns.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given the updated CT-004 pattern, When running tier1 scan, Then T-001 tests pass

### T-003: Add CT-004 to DOCUMENTATION_SAFE_PATTERNS
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given CT-004 inside a fenced code block, When running tier1 scan, Then severity is downgraded to "info"

## Domain: Content

### T-004: Remove nested fencing in appstore SKILL.md
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given the updated SKILL.md, When checking for nested fenced blocks, Then no ```markdown wrapper contains inner ```bash blocks

### T-005: Verify appstore SKILL.md scan score >= 80
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given all fixes applied, When running runTier1Scan() on appstore SKILL.md, Then score >= 80 and verdict is PASS

### T-006: Run full scanner test suite
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [x] completed
**Test Plan**: Given all changes, When running npx vitest run src/scanner/, Then all tests pass with 0 failures
