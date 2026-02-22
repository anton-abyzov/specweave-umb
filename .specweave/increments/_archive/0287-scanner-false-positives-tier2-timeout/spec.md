---
increment: 0287-scanner-false-positives-tier2-timeout
title: "Scanner False Positives & Tier 2 LLM Timeout"
type: bug
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug: Scanner False Positives & Tier 2 LLM Timeout

## Overview

Two production bugs cause valid skill submissions to be incorrectly rejected:

1. **FS-003 path traversal false positives**: The pattern matches `../../` anywhere including normal
   relative import statements (`import X from "../../lib/Y"`), causing innocent skills to receive
   high-severity findings and a CONCERNS verdict.

2. **Tier 2 LLM timeout**: `LLM_TIMEOUT_MS = 8_000` is too short for `llama-3.1-70b-instruct`,
   which takes 10-30s. Every Tier 2 scan times out, returning a conservative CONCERNS verdict and
   leaving `intentAnalysis`/`scopeAlignment` as error strings in submission records.

**Root cause evidence** (submission `sub_522b9026`):
- 3 high FS-003 findings at L45, L46, L620 — all import statements
- Tier 2 LLM timeout at exactly 8000ms visible in logs

---

## User Stories

### US-001: Fix FS-003 false positives on import paths (P1)
**Project**: vskill-platform

**As a** skill author
**I want** the scanner to only flag `../../` patterns that appear in filesystem API calls
**So that** normal relative imports do not produce false-positive path traversal findings

**Acceptance Criteria**:
- [x] **AC-US1-01**: `import X from "../../lib/Y"` does NOT trigger FS-003
- [x] **AC-US1-02**: `require("../../utils/helper")` does NOT trigger FS-003
- [x] **AC-US1-03**: `fs.readFileSync("../../etc/passwd")` DOES trigger FS-003 (true positive preserved)
- [x] **AC-US1-04**: `readFile("../../.env", "utf8")` DOES trigger FS-003
- [x] **AC-US1-05**: The FS-003 pattern is updated in `patterns.ts`; severity remains `high`
- [x] **AC-US1-06**: Existing tier1.test.ts "filesystem-access" test is updated to use an fs-API call context and passes

---

### US-002: Raise Tier 2 LLM timeout to support llama-3.1-70b (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** Tier 2 LLM analysis to complete successfully for typical submissions
**So that** submissions receive real intent analysis instead of timeout error strings

**Acceptance Criteria**:
- [x] **AC-US2-01**: `LLM_TIMEOUT_MS` in `tier2.ts` is raised to 30,000 (30s)
- [x] **AC-US2-02**: `MESSAGE_TIMEOUT_MS` in `consumer.ts` is raised to 55,000 to match new LLM budget
- [x] **AC-US2-03**: `max_batch_timeout` in `wrangler.jsonc` is raised to 60 (seconds)
- [x] **AC-US2-04**: The comment on `LLM_TIMEOUT_MS` is updated to reference the new MESSAGE_TIMEOUT_MS budget
- [x] **AC-US2-05**: The comment on `MESSAGE_TIMEOUT_MS` is updated to reference the new `max_batch_timeout` (60s)
- [x] **AC-US2-06**: Existing tier2 tests continue to pass (no behaviour change for mocked AI)

---

## Functional Requirements

### FR-001: FS-003 pattern requires filesystem API context
The revised FS-003 regex must only match `../../` (or deeper) when the pattern appears as an
argument to a filesystem API function call on the same line. Supported function names:
`readFile`, `writeFile`, `appendFile`, `createReadStream`, `createWriteStream`, `open`,
`unlink`, `stat`, `lstat`, `fstat`, `access`, `rename`, `copyFile`, `chmod`, `chown`,
`truncate` (with optional `Sync` suffix).

### FR-002: Queue timeout budget
New budget hierarchy:
- `wrangler.jsonc max_batch_timeout`: 60s (hard wrangler limit)
- `consumer.ts MESSAGE_TIMEOUT_MS`: 55,000ms (5s margin)
- `tier2.ts LLM_TIMEOUT_MS`: 30,000ms (leaves 25s for fetch + tier1 + DB ops)

---

## Success Criteria

- Skills with only import statements containing `../../` receive NO filesystem-access findings
- Tier 2 LLM analysis completes for submissions where the model responds within 30s
- All existing scanner tests pass

## Out of Scope

- Multi-line path traversal detection (e.g., variable assigned `../../` then passed to fs call)
- Switching to a different LLM model
- Optimizing repo fetch time

## Dependencies

- `repositories/anton-abyzov/vskill-platform/src/lib/scanner/patterns.ts` (FS-003)
- `repositories/anton-abyzov/vskill-platform/src/lib/scanner/tier2.ts` (LLM_TIMEOUT_MS)
- `repositories/anton-abyzov/vskill-platform/src/lib/queue/consumer.ts` (MESSAGE_TIMEOUT_MS)
- `repositories/anton-abyzov/vskill-platform/wrangler.jsonc` (max_batch_timeout)
