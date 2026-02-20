# Tasks: vskill audit - Local Project Security Auditing

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Foundation

### US-001: Run Local Security Audit (P1)

#### T-001: Define audit types and interfaces
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-05, AC-US2-04 | **Status**: [x] completed

**Description**: Create `src/audit/audit-types.ts` with all TypeScript interfaces for the audit module: `AuditConfig`, `AuditFinding`, `AuditResult`, `AuditSummary`, `DataFlowTrace`, `AuditPattern`, and output format enums.

**AC**: AC-US1-05, AC-US2-04

**Implementation Details**:
- Create `src/audit/` directory
- Define `AuditFinding` extending existing `SecurityFinding` with file path, confidence, snippet, data flow
- Define `AuditConfig` for all configurable options
- Define `AuditResult` as the top-level result container
- Export all types from `src/audit/index.ts`
- All imports must use `.js` extensions (ESM requirement)

**Test Plan**:
- **File**: `src/audit/audit-types.test.ts`
- **Tests**:
  - **TC-001**: AuditFinding type is correctly importable and all fields are typed
    - Given the audit-types module is imported
    - When creating an AuditFinding object with all required fields
    - Then TypeScript compiles without errors
  - **TC-002**: AuditConfig default values are correct
    - Given the default config factory is called
    - When checking all fields
    - Then defaults match spec (maxFiles: 500, severityThreshold: 'low', tier1Only: false)

**Dependencies**: None
**Hint**: haiku

---

#### T-002: Implement file discovery engine
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Description**: Create `src/audit/file-discovery.ts` that walks the filesystem to discover scannable files. Reuse logic from `repo-scanner.ts` (isScannable, isBinary checks) but adapted for local paths (no git clone needed). Add .gitignore respect and configurable exclude patterns.

**AC**: AC-US1-01, AC-US1-02

**Implementation Details**:
- Extract and reuse `SCANNABLE_EXTENSIONS`, `ALWAYS_SCAN`, `isBinary`, `isScannable` from `repo-scanner.ts`
- Add `.gitignore` parsing (simple glob matching, no new dependencies)
- Support both directory scanning (recursive walk) and single-file scanning
- Configurable: `excludePaths`, `maxFiles`, `maxFileSize`
- Skip: `.git/`, `node_modules/`, `dist/`, `build/`, `coverage/`, `.next/`, vendor dirs
- Return `AuditFile[]` with path, content, sizeBytes

**Test Plan**:
- **File**: `src/audit/file-discovery.test.ts`
- **Tests**:
  - **TC-003**: Discovers .ts, .js, .py files in a directory tree
    - Given a temp directory with mixed file types
    - When discoverAuditFiles is called
    - Then returns only scannable files
  - **TC-004**: Skips node_modules and .git directories
    - Given a temp directory with node_modules/ and .git/ subdirs
    - When discoverAuditFiles is called
    - Then those directories are not traversed
  - **TC-005**: Scans a single file when path points to a file
    - Given a path to a single .ts file
    - When discoverAuditFiles is called
    - Then returns exactly one AuditFile
  - **TC-006**: Respects maxFiles limit
    - Given a directory with 10 files and maxFiles=5
    - When discoverAuditFiles is called
    - Then returns at most 5 files
  - **TC-007**: Skips binary files
    - Given a directory with a binary file and a text file
    - When discoverAuditFiles is called
    - Then only the text file is returned
  - **TC-008**: Respects exclude patterns
    - Given excludePaths: ["**/test/**"]
    - When discoverAuditFiles is called
    - Then files in test/ directories are excluded

**Dependencies**: T-001
**Hint**: opus

---

#### T-003: Implement extended audit patterns
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Description**: Create `src/audit/audit-patterns.ts` with project-audit-specific patterns. Import and extend the existing `SCAN_PATTERNS` to create a combined `AUDIT_PATTERNS` array with 15-20 additional patterns for SQL injection, SSRF, broken access control, hardcoded secrets, insecure deserialization, XSS, and open redirects.

**AC**: AC-US1-03

**Implementation Details**:
- Import `SCAN_PATTERNS` from `../scanner/patterns.js`
- Define new `AuditPatternCheck` extending `PatternCheck` with `safeContexts` and `confidence`
- Add patterns:
  - SQLi: string concatenation in SQL queries, template literals in queries
  - SSRF: URL construction from variables, request forwarding
  - Broken access control: missing auth middleware, role checks
  - Hardcoded secrets: API key patterns, password assignments, token literals
  - Insecure deserialization: JSON.parse of request body without validation, yaml.load
  - XSS: innerHTML assignment, dangerouslySetInnerHTML, document.write
  - Open redirects: redirect with user-controlled URL
- Export combined `AUDIT_PATTERNS = [...SCAN_PATTERNS, ...PROJECT_PATTERNS]`

**Test Plan**:
- **File**: `src/audit/audit-patterns.test.ts`
- **Tests**:
  - **TC-009**: AUDIT_PATTERNS includes all 37 original SCAN_PATTERNS
    - Given AUDIT_PATTERNS
    - When checking for original pattern IDs
    - Then all 37 original IDs are present
  - **TC-010**: AUDIT_PATTERNS adds at least 15 new project-specific patterns
    - Given AUDIT_PATTERNS
    - When counting patterns beyond the original 37
    - Then at least 15 new patterns exist
  - **TC-011**: SQL injection pattern detects string concatenation in queries
    - Given `"SELECT * FROM users WHERE id = '" + userId + "'"`
    - When scanned
    - Then SQLi pattern fires
  - **TC-012**: SSRF pattern detects URL construction from variables
    - Given `fetch(userProvidedUrl)`
    - When scanned
    - Then SSRF pattern fires
  - **TC-013**: Hardcoded secret pattern detects API key assignments
    - Given `const API_KEY = "sk-1234567890abcdef"`
    - When scanned
    - Then hardcoded secret pattern fires
  - **TC-014**: XSS pattern detects innerHTML assignment
    - Given `element.innerHTML = userInput`
    - When scanned
    - Then XSS pattern fires
  - **TC-015**: Safe contexts suppress false positives
    - Given a pattern with safeContexts and a matching safe line
    - When scanned
    - Then finding is suppressed
  - **TC-016**: All new pattern IDs are unique across combined set
    - Given AUDIT_PATTERNS
    - When extracting all IDs
    - Then no duplicates exist

**Dependencies**: T-001
**Hint**: opus

---

#### T-004: Implement core audit scanner
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-06 | **Status**: [x] completed

**Description**: Create `src/audit/audit-scanner.ts` that orchestrates Tier 1 scanning across all discovered files. Takes an array of `AuditFile` objects, runs the extended pattern set against each, and returns aggregated `AuditResult` with per-file findings, summary statistics, score, and verdict.

**AC**: AC-US1-04, AC-US1-06

**Implementation Details**:
- Accept `AuditFile[]` and `AuditConfig`
- For each file, run pattern matching using `AUDIT_PATTERNS`
- Apply `safeContexts` filtering to reduce false positives
- Aggregate findings into `AuditResult` with summary counts by severity
- Calculate score using existing scoring weights from `tier1.ts`
- Determine verdict (PASS/CONCERNS/FAIL)
- Sort findings: by severity (critical first), then by file path
- Record timing information

**Test Plan**:
- **File**: `src/audit/audit-scanner.test.ts`
- **Tests**:
  - **TC-017**: Returns empty findings for clean files
    - Given an array of files with clean content
    - When runAuditScan is called
    - Then findings array is empty and verdict is PASS
  - **TC-018**: Detects findings across multiple files
    - Given files with different vulnerability types
    - When runAuditScan is called
    - Then findings include entries from each file with correct file paths
  - **TC-019**: Findings are sorted by severity then file path
    - Given files with mixed severity findings
    - When runAuditScan is called
    - Then findings are ordered critical > high > medium > low > info
  - **TC-020**: Summary statistics are accurate
    - Given files producing known finding counts
    - When runAuditScan is called
    - Then summary.critical, summary.high, etc. match expected counts
  - **TC-021**: Score and verdict are calculated correctly
    - Given files producing a known score
    - When runAuditScan is called
    - Then score and verdict match expected values
  - **TC-022**: Duration is tracked
    - Given any input
    - When runAuditScan is called
    - Then durationMs is a non-negative number

**Dependencies**: T-001, T-002, T-003
**Hint**: opus

---

#### T-005: Register audit CLI command
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-06 | **Status**: [x] completed

**Description**: Add the `vskill audit [path]` command to `src/index.ts` and create `src/commands/audit.ts` that wires together file discovery, audit scanner, and terminal output. Handle all CLI flags: `--json`, `--ci`, `--report`, `--fix`, `--tier1-only`, `--exclude`, `--severity`, `--max-files`.

**AC**: AC-US1-01, AC-US1-02, AC-US1-06

**Implementation Details**:
- Register `audit` command in `src/index.ts` with `commander`
- `src/commands/audit.ts`: Parse options, load config, run pipeline
- Default path is `.` (current directory)
- Wire: discoverAuditFiles -> runAuditScan -> format output
- Exit codes: 0 (PASS), 1 (CONCERNS), 2 (FAIL)
- Show progress spinner for large scans

**Test Plan**:
- **File**: `src/commands/audit.test.ts`
- **Tests**:
  - **TC-023**: Command is registered in the CLI
    - Given the program instance
    - When listing commands
    - Then "audit" command exists with correct description
  - **TC-024**: Default path is current directory
    - Given no path argument
    - When audit command runs
    - Then it scans from cwd
  - **TC-025**: Exit code 0 for clean project
    - Given a clean fixture directory
    - When audit runs
    - Then process exits with code 0
  - **TC-026**: Exit code 2 for critical findings
    - Given a fixture with critical vulnerabilities
    - When audit runs
    - Then process exits with code 2

**Dependencies**: T-001, T-002, T-003, T-004
**Hint**: opus

---

## Phase 2: Output Formatters

### US-003: Output Formats and CI Integration (P1)

#### T-006: Implement terminal formatter [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05, AC-US1-04, AC-US1-05 | **Status**: [x] completed

**Description**: Create `src/audit/formatters/terminal-formatter.ts` that renders `AuditResult` as colored terminal output. Show summary header, findings table grouped by file, code snippets with highlighted lines, and footer with statistics.

**AC**: AC-US3-05, AC-US1-04, AC-US1-05

**Implementation Details**:
- Reuse `src/utils/output.ts` color helpers (bold, red, yellow, green, cyan, dim)
- Header: score, verdict, files scanned, duration
- Group findings by file path
- Each finding: severity badge, category, line number, code snippet (2 lines context)
- Footer: total counts by severity
- Truncate long code snippets to 120 chars

**Test Plan**:
- **File**: `src/audit/formatters/terminal-formatter.test.ts`
- **Tests**:
  - **TC-027**: Formats empty results correctly
    - Given an AuditResult with no findings
    - When formatTerminal is called
    - Then output contains "No security issues found"
  - **TC-028**: Groups findings by file
    - Given findings from 3 different files
    - When formatTerminal is called
    - Then output has file path headers for each file
  - **TC-029**: Includes code snippets
    - Given findings with snippet context
    - When formatTerminal is called
    - Then output contains the code snippet text

**Dependencies**: T-001
**Hint**: haiku

---

#### T-007: Implement JSON formatter [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed

**Description**: Create `src/audit/formatters/json-formatter.ts` that serializes `AuditResult` to well-structured JSON output.

**AC**: AC-US3-01

**Implementation Details**:
- JSON.stringify the AuditResult with indentation
- Include all findings, metadata, summary, config used
- Output to stdout (pipe-friendly)

**Test Plan**:
- **File**: `src/audit/formatters/json-formatter.test.ts`
- **Tests**:
  - **TC-030**: Output is valid JSON
    - Given any AuditResult
    - When formatJson is called
    - Then output parses without error via JSON.parse
  - **TC-031**: All findings are present in output
    - Given an AuditResult with 5 findings
    - When formatJson is called and parsed
    - Then parsed.findings has length 5
  - **TC-032**: Summary statistics are included
    - Given an AuditResult
    - When formatJson is called and parsed
    - Then parsed.summary contains critical, high, medium, low, info counts

**Dependencies**: T-001
**Hint**: haiku

---

#### T-008: Implement SARIF formatter [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed

**Description**: Create `src/audit/formatters/sarif-formatter.ts` that generates SARIF v2.1.0 compliant JSON output for CI tool integration (GitHub Code Scanning, etc.).

**AC**: AC-US3-02

**Implementation Details**:
- SARIF v2.1.0 schema: `$schema`, `version`, `runs[]`
- Tool information: name "vskill-audit", version from package.json
- Rules: map each pattern ID to a SARIF rule with id, name, shortDescription, helpUri
- Results: map each finding to a SARIF result with ruleId, message, locations, level
- Level mapping: critical/high -> "error", medium -> "warning", low/info -> "note"
- Locations: physicalLocation with artifactLocation (uri) and region (startLine)

**Test Plan**:
- **File**: `src/audit/formatters/sarif-formatter.test.ts`
- **Tests**:
  - **TC-033**: Output matches SARIF v2.1.0 structure
    - Given an AuditResult
    - When formatSarif is called
    - Then output has $schema, version "2.1.0", runs array
  - **TC-034**: Tool information is correct
    - Given an AuditResult
    - When formatSarif is called
    - Then runs[0].tool.driver.name is "vskill-audit"
  - **TC-035**: Findings map to SARIF results with correct locations
    - Given findings with file paths and line numbers
    - When formatSarif is called
    - Then each result has physicalLocation with correct uri and startLine
  - **TC-036**: Severity maps to correct SARIF levels
    - Given findings of each severity
    - When formatSarif is called
    - Then critical/high -> "error", medium -> "warning", low/info -> "note"

**Dependencies**: T-001
**Hint**: opus

---

#### T-009: Implement markdown report formatter [P]
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed

**Description**: Create `src/audit/formatters/report-formatter.ts` that generates a structured markdown security audit report.

**AC**: AC-US3-03

**Implementation Details**:
- Report sections: Title, Executive Summary, Findings by Severity, File-by-File Breakdown, Recommendations, Scan Metadata
- Write to file at specified path (default: `./security-audit-report.md`)
- Include code snippets in fenced code blocks
- Include summary table with counts
- Include scan configuration used

**Test Plan**:
- **File**: `src/audit/formatters/report-formatter.test.ts`
- **Tests**:
  - **TC-037**: Report contains all sections
    - Given an AuditResult with findings
    - When formatReport is called
    - Then output contains "Executive Summary", "Findings", "Recommendations"
  - **TC-038**: Code snippets are in fenced code blocks
    - Given findings with code snippets
    - When formatReport is called
    - Then snippets are wrapped in triple backticks
  - **TC-039**: Summary table has correct counts
    - Given an AuditResult with known severity counts
    - When formatReport is called
    - Then the summary table matches expected counts

**Dependencies**: T-001
**Hint**: haiku

---

## Phase 3: LLM Integration

### US-002: LLM-Enhanced Analysis on Flagged Files (P1)

#### T-010: Implement LLM analysis engine
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-05, AC-US2-06 | **Status**: [x] completed

**Description**: Create `src/audit/audit-llm.ts` that performs LLM-based security analysis on Tier 1 flagged files. Invokes an LLM via subprocess (configurable command, default: `claude` CLI) with a security analysis prompt.

**AC**: AC-US2-01, AC-US2-05, AC-US2-06

**Implementation Details**:
- Accept flagged files + their Tier 1 findings
- Build a structured prompt with file content and Tier 1 findings context
- Invoke LLM via `child_process.execFile` (not shell to avoid injection)
- Parse structured JSON response from LLM
- Configurable timeout (default 30s per file)
- Configurable concurrency (default 5 files)
- Graceful fallback if LLM unavailable (return Tier 1 results only)
- `--tier1-only` flag skips this entirely

**Test Plan**:
- **File**: `src/audit/audit-llm.test.ts`
- **Tests**:
  - **TC-040**: Builds correct prompt with file content and Tier 1 findings
    - Given a file with Tier 1 findings
    - When buildLlmPrompt is called
    - Then prompt contains file content and finding summaries
  - **TC-041**: Parses valid LLM JSON response
    - Given a mock LLM returning valid JSON findings
    - When analyzeFlaggedFile is called
    - Then returns parsed AuditFinding objects
  - **TC-042**: Returns empty findings on LLM timeout
    - Given a mock LLM that times out
    - When analyzeFlaggedFile is called
    - Then returns empty array (graceful fallback)
  - **TC-043**: Skips LLM when tier1Only is true
    - Given config with tier1Only: true
    - When runLlmAnalysis is called
    - Then returns immediately with no findings
  - **TC-044**: Respects concurrency limit
    - Given 10 files and concurrency limit of 3
    - When runLlmAnalysis is called
    - Then at most 3 LLM processes run simultaneously

**Dependencies**: T-001, T-004
**Hint**: opus

---

#### T-011: Implement data flow tracing
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Description**: Extend the LLM prompt in `audit-llm.ts` to request data flow traces. Parse the LLM's data flow trace output into `DataFlowTrace` objects and attach them to findings.

**AC**: AC-US2-02, AC-US2-03

**Implementation Details**:
- Extend LLM system prompt to request: source -> transformation -> sink traces
- Request identification of: user input sources, data transformations, dangerous sinks
- Parse `dataFlow` field from LLM response into `DataFlowTrace` structure
- Validate trace steps have required fields (file, line, description, code)

**Test Plan**:
- **File**: `src/audit/audit-llm.test.ts` (extend)
- **Tests**:
  - **TC-045**: Data flow trace is parsed from LLM response
    - Given an LLM response with dataFlow field
    - When parsed
    - Then DataFlowTrace has valid steps with file, line, description, code
  - **TC-046**: Missing data flow is handled gracefully
    - Given an LLM response without dataFlow
    - When parsed
    - Then finding.dataFlow is undefined (not an error)

**Dependencies**: T-010
**Hint**: opus

---

#### T-012: Implement fix suggestions
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed

**Description**: When `--fix` flag is set, extend each finding with a suggested remediation. For Tier 1 findings, provide pattern-based fix suggestions (lookup table). For LLM findings, include the LLM's recommended fix.

**AC**: AC-US3-04

**Implementation Details**:
- Create `src/audit/fix-suggestions.ts` with a pattern-ID-to-fix-suggestion map
- For each Tier 1 finding, look up the fix suggestion by pattern ID
- For LLM findings, include `suggestedFix` from LLM response
- Fix suggestions are strings describing the recommended remediation (not code patches)

**Test Plan**:
- **File**: `src/audit/fix-suggestions.test.ts`
- **Tests**:
  - **TC-047**: Every audit pattern ID has a fix suggestion
    - Given the fix suggestions map
    - When checking all AUDIT_PATTERNS IDs
    - Then each ID has a non-empty fix suggestion
  - **TC-048**: Fix suggestion is attached to finding when --fix is set
    - Given config with fix: true
    - When audit scan runs
    - Then every finding has a suggestedFix field
  - **TC-049**: Fix suggestion is absent when --fix is not set
    - Given config with fix: false
    - When audit scan runs
    - Then findings do not have suggestedFix field

**Dependencies**: T-003, T-010
**Hint**: opus

---

## Phase 4: Configuration & Integration

### US-004: Audit Configuration (P2)

#### T-013: Implement config file loader
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Description**: Create `src/audit/config.ts` that loads audit configuration from `.vskill-audit.json` or `.vskillrc` in the project root, merged with CLI flag overrides.

**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04

**Implementation Details**:
- Search for `.vskill-audit.json` or `.vskillrc` in the audit root path
- Parse JSON config file
- Merge with defaults, then override with CLI flags
- Validate config values (severity is valid, maxFiles > 0, etc.)
- Return merged `AuditConfig`

**Test Plan**:
- **File**: `src/audit/config.test.ts`
- **Tests**:
  - **TC-050**: Returns defaults when no config file exists
    - Given no config file in the directory
    - When loadAuditConfig is called
    - Then returns default AuditConfig
  - **TC-051**: Loads and merges .vskill-audit.json
    - Given a .vskill-audit.json with excludePaths: ["vendor/"]
    - When loadAuditConfig is called
    - Then config.excludePaths includes "vendor/"
  - **TC-052**: CLI flags override config file values
    - Given config file with maxFiles: 100 and CLI flag maxFiles: 50
    - When loadAuditConfig is called with CLI overrides
    - Then config.maxFiles is 50
  - **TC-053**: Invalid severity value throws error
    - Given config with severity: "invalid"
    - When loadAuditConfig is called
    - Then throws a validation error

**Dependencies**: T-001
**Hint**: haiku

---

#### T-014: End-to-end integration tests
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US1-06, AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Description**: Create integration test fixtures and end-to-end tests that exercise the full audit pipeline from file discovery through formatted output.

**AC**: AC-US1-01, AC-US1-04, AC-US1-06, AC-US3-01, AC-US3-02

**Implementation Details**:
- Create `src/audit/__fixtures__/` with:
  - `clean-project/` - no vulnerabilities
  - `vulnerable-project/` - known vulnerabilities of each type
  - `mixed-project/` - some clean, some vulnerable files
- Test full pipeline: discover -> scan -> format
- Verify exit codes, JSON output structure, SARIF compliance

**Test Plan**:
- **File**: `src/audit/audit-integration.test.ts`
- **Tests**:
  - **TC-054**: Clean project produces PASS verdict and exit code 0
    - Given the clean-project fixture
    - When full audit pipeline runs
    - Then verdict is PASS, exit code is 0
  - **TC-055**: Vulnerable project detects all planted vulnerabilities
    - Given the vulnerable-project fixture with 5 known vulns
    - When full audit pipeline runs
    - Then all 5 vulnerabilities are found
  - **TC-056**: JSON output is valid and complete
    - Given the mixed-project fixture
    - When audit runs with --json
    - Then output parses as valid JSON with all required fields
  - **TC-057**: SARIF output has correct structure
    - Given the vulnerable-project fixture
    - When audit runs with --ci
    - Then SARIF output has valid schema, runs, results, rules

**Dependencies**: T-004, T-005, T-006, T-007, T-008
**Hint**: opus

---

### US-005: SpecWeave Skill Integration (P2)

#### T-015: Create /sw:security-scan skill wrapper
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: Create a SpecWeave skill file that wraps `vskill audit` for use within SpecWeave workflows. The skill invokes the audit command on the current project and stores results in the increment reports directory.

**AC**: AC-US5-01, AC-US5-02, AC-US5-03

**Implementation Details**:
- Skill file location: TBD (depends on SpecWeave skill registration mechanism)
- Invoke `vskill audit` with `--json` flag on the current repository
- Parse JSON output and format for SpecWeave consumption
- Store report in `.specweave/increments/{current}/reports/security-audit.md`
- In multi-repo setups, detect the correct repository from SpecWeave project context

**Test Plan**:
- **File**: Manual verification (skill wrapper is a SKILL.md/command file, not a .ts module)
- **Tests**:
  - **TC-058**: Skill invokes vskill audit on correct path
    - Given a SpecWeave project with a repository
    - When /sw:security-scan is invoked
    - Then vskill audit runs on the repository root
  - **TC-059**: Results are stored in reports directory
    - Given a successful audit
    - When skill completes
    - Then security-audit.md exists in the increment reports directory

**Dependencies**: T-005, T-007, T-009
**Hint**: opus

---

## Phase 5: Verification

- [ ] [T-060] Run full test suite and verify >= 90% coverage
- [ ] [T-061] Verify all existing scanner tests still pass
- [ ] [T-062] Verify all acceptance criteria in spec.md
