---
increment: 0252-vskill-audit-command
title: "vskill audit - Local Project Security Auditing"
type: feature
priority: P1
status: active
created: 2026-02-20
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vskill audit - Local Project Security Auditing

## Overview

Extends the vskill CLI with a `vskill audit [path]` command that performs security auditing on local codebases. The command runs a two-tier scanning pipeline: Tier 1 performs fast regex-based pattern matching (reusing existing `src/scanner/patterns.ts`), followed by targeted LLM-based analysis on flagged files to trace data flows and identify complex vulnerabilities (command injection, SSRF, broken access control, etc.).

The command outputs structured findings with severity, confidence, code snippets, data flow traces, and suggested fixes. It supports multiple output modes: `--fix` (suggest fixes), `--ci` (SARIF output + exit codes), `--json` (machine-readable JSON), and `--report` (markdown report file).

Integrates with SpecWeave via a `/sw:security-scan` skill wrapper.

**Target repository**: `repositories/anton-abyzov/vskill/`

## User Stories

### US-001: Run Local Security Audit (P1)
**Project**: specweave

**As a** developer
**I want** to run `vskill audit [path]` on my local project directory
**So that** I can identify security vulnerabilities before deploying or publishing

**Acceptance Criteria**:
- [x] **AC-US1-01**: Running `vskill audit .` from a project root scans all scannable files (ts, js, py, sh, md, json, yaml, etc.) recursively, skipping node_modules, .git, and binary files
- [x] **AC-US1-02**: Running `vskill audit path/to/file.ts` scans a single file
- [x] **AC-US1-03**: Tier 1 regex scanning reuses existing `SCAN_PATTERNS` from `src/scanner/patterns.ts` plus new project-audit-specific patterns (SSRF, broken access control, SQL injection, hardcoded secrets, insecure deserialization)
- [x] **AC-US1-04**: Output displays findings grouped by file, sorted by severity (critical > high > medium > low > info)
- [x] **AC-US1-05**: Each finding includes: severity, category, file path, line number, matched code snippet (with 2 lines context), and confidence level
- [x] **AC-US1-06**: Exit code 0 for no issues, 1 for warnings (medium/low), 2 for critical/high findings

---

### US-002: LLM-Enhanced Analysis on Flagged Files (P1)
**Project**: specweave

**As a** developer
**I want** Tier 1 flagged files to be analyzed by an LLM for deeper vulnerability assessment
**So that** I get accurate results with reduced false positives and can discover complex vulnerabilities that regex alone cannot detect

**Acceptance Criteria**:
- [x] **AC-US2-01**: Files with Tier 1 findings are passed to a local LLM analysis step (Claude CLI or configurable provider)
- [x] **AC-US2-02**: LLM analysis traces data flows from user input to dangerous sinks (exec, SQL queries, file operations, HTTP requests)
- [x] **AC-US2-03**: LLM analysis identifies complex vulnerabilities: command injection chains, SSRF via URL construction, broken access control, insecure deserialization
- [x] **AC-US2-04**: Each LLM finding includes a confidence score (high/medium/low) and data flow trace
- [x] **AC-US2-05**: LLM analysis is optional and skipped with `--tier1-only` flag
- [x] **AC-US2-06**: LLM analysis respects a configurable timeout (default 30s per file, max 5 files concurrently)

---

### US-003: Output Formats and CI Integration (P1)
**Project**: specweave

**As a** developer or CI pipeline
**I want** multiple output formats for audit results
**So that** I can integrate security scanning into automated workflows and review results in different contexts

**Acceptance Criteria**:
- [x] **AC-US3-01**: `--json` flag outputs machine-readable JSON with all findings, metadata, and summary statistics
- [x] **AC-US3-02**: `--ci` flag outputs SARIF v2.1.0 format and uses appropriate exit codes (0/1/2)
- [x] **AC-US3-03**: `--report` flag generates a markdown report file at the specified path (default: `./security-audit-report.md`)
- [x] **AC-US3-04**: `--fix` flag appends suggested remediation steps to each finding (from LLM analysis or pattern-based suggestions)
- [x] **AC-US3-05**: Default output (no flags) shows a human-readable colored terminal summary with table of findings

---

### US-004: Audit Configuration (P2)
**Project**: specweave

**As a** developer
**I want** to configure audit behavior via a config file or CLI flags
**So that** I can customize scanning for my project's specific needs

**Acceptance Criteria**:
- [x] **AC-US4-01**: `.vskill-audit.json` or `.vskillrc` in project root allows configuring: exclude paths, severity threshold, custom patterns, LLM provider
- [x] **AC-US4-02**: `--exclude <glob>` flag excludes files/dirs matching the pattern
- [x] **AC-US4-03**: `--severity <level>` flag sets minimum severity to report (default: low)
- [x] **AC-US4-04**: `--max-files <n>` flag limits the number of files scanned (default: 500)

---

### US-005: SpecWeave Skill Integration (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** a `/sw:security-scan` skill that wraps `vskill audit`
**So that** I can trigger security audits from within SpecWeave workflows

**Acceptance Criteria**:
- [x] **AC-US5-01**: `/sw:security-scan` skill wrapper invokes `vskill audit` on the current project
- [x] **AC-US5-02**: Results are formatted for SpecWeave consumption and stored in increment reports directory
- [x] **AC-US5-03**: Skill respects SpecWeave project context (scans the correct repository in multi-repo setups)

## Functional Requirements

### FR-001: File Discovery Engine
Recursively walk the target path discovering scannable files. Respect `.gitignore` patterns. Skip binary files, node_modules, .git, and vendor directories. Support configurable max file count and max file size limits.

### FR-002: Extended Pattern Set for Project Auditing
Extend the existing 37 SCAN_PATTERNS with project-audit-specific patterns:
- SQL injection (parameterized query detection, string concatenation in queries)
- SSRF (URL construction from user input, request forwarding)
- Broken access control (missing auth checks, role bypass patterns)
- Hardcoded secrets (API keys, tokens, passwords in source)
- Insecure deserialization (JSON.parse of untrusted input, pickle, yaml.load)
- Open redirects (redirect URL from user input)
- XSS patterns (innerHTML, dangerouslySetInnerHTML, document.write)

### FR-003: SARIF Output Compliance
Generate SARIF v2.1.0 compliant output for CI integration. Include tool information, run metadata, results with locations, and rule definitions.

### FR-004: Markdown Report Generation
Generate a structured markdown report including: executive summary, findings by severity, file-by-file breakdown, remediation recommendations, and scan metadata.

## Success Criteria

- Tier 1 scan of a 1000-file project completes in < 10 seconds
- False positive rate < 30% on common open-source projects
- SARIF output validates against the SARIF v2.1.0 schema
- Unit test coverage >= 90%
- All existing scanner tests continue to pass

## Out of Scope

- Remote repository scanning (existing `repo-scanner.ts` handles that)
- Cloud-hosted scanning service / SaaS dashboard
- Auto-fix / code modification (only suggests fixes, does not apply them)
- Language-specific AST parsing (regex + LLM approach only)
- Binary analysis / compiled code scanning

## Dependencies

- Existing `src/scanner/patterns.ts` (37 regex patterns)
- Existing `src/scanner/tier1.ts` (scoring engine)
- Existing `src/scanner/repo-scanner.ts` (file discovery logic to reuse/extend)
- Existing `src/utils/output.ts` (terminal formatting)
- `commander` package (CLI framework, already a dependency)
