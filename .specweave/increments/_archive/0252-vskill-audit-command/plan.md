# Implementation Plan: vskill audit - Local Project Security Auditing

## Overview

Extend the vskill CLI with a `vskill audit [path]` command that performs two-tier security scanning on local codebases. The implementation reuses existing scanner infrastructure (`patterns.ts`, `tier1.ts`, `repo-scanner.ts`) and extends it with project-audit-specific patterns, an LLM analysis layer, and multiple output formatters (terminal, JSON, SARIF, markdown report).

## Architecture

### Component Diagram

```
vskill audit [path] [flags]
        |
        v
+-------------------+
| audit.ts (command)|  <-- CLI entry point, parses args
+-------------------+
        |
        v
+-------------------+
| file-discovery.ts |  <-- Walks filesystem, respects .gitignore, filters
+-------------------+
        |
        v
+----------------------------+
| audit-patterns.ts          |  <-- Extended patterns (SQL injection, SSRF, etc.)
| (extends patterns.ts)      |     Reuses SCAN_PATTERNS + adds 15-20 new ones
+----------------------------+
        |
        v
+-------------------+
| audit-scanner.ts  |  <-- Runs Tier 1 on all files, aggregates per-file results
+-------------------+
        |
        v
+-------------------+
| audit-llm.ts      |  <-- Tier 2: LLM analysis on flagged files
| (optional)        |     Data flow tracing, complex vuln detection
+-------------------+
        |
        v
+-------------------+
| audit-types.ts    |  <-- Shared types for the audit module
+-------------------+
        |
        v
+---------------------------------------------+
| Output Formatters                           |
|  - terminal-formatter.ts (default, colored) |
|  - json-formatter.ts (--json)               |
|  - sarif-formatter.ts (--ci)                |
|  - report-formatter.ts (--report)           |
+---------------------------------------------+
```

### Components

- **`src/commands/audit.ts`**: CLI command handler. Parses flags, loads config, orchestrates pipeline.
- **`src/audit/file-discovery.ts`**: Filesystem walker. Extends `repo-scanner.ts` logic for local paths (no git clone needed). Respects `.gitignore`, configurable excludes, max file limits.
- **`src/audit/audit-patterns.ts`**: Extended pattern set. Imports and extends `SCAN_PATTERNS` with project-audit-specific patterns (SQL injection, SSRF, broken access control, hardcoded secrets, XSS, etc.).
- **`src/audit/audit-scanner.ts`**: Orchestrator that runs Tier 1 scanning across all discovered files. Returns per-file results with aggregated statistics.
- **`src/audit/audit-llm.ts`**: Optional LLM-based analysis. Takes flagged files and Tier 1 findings, sends to LLM for data flow analysis and complex vulnerability detection. Configurable provider and timeout.
- **`src/audit/audit-types.ts`**: TypeScript interfaces for audit findings, config, results, and report structures.
- **`src/audit/formatters/terminal-formatter.ts`**: Default colored terminal output.
- **`src/audit/formatters/json-formatter.ts`**: Machine-readable JSON output.
- **`src/audit/formatters/sarif-formatter.ts`**: SARIF v2.1.0 compliant output.
- **`src/audit/formatters/report-formatter.ts`**: Markdown report generator.
- **`src/audit/config.ts`**: Config file loader (`.vskill-audit.json` / `.vskillrc`).
- **`src/audit/index.ts`**: Barrel export for the audit module.

### Data Model

```typescript
/** Configuration for an audit run */
interface AuditConfig {
  excludePaths: string[];
  severityThreshold: Severity;
  maxFiles: number;
  maxFileSize: number;
  tier1Only: boolean;
  llmProvider: 'claude' | 'openai' | 'local' | null;
  llmTimeout: number; // ms per file
  llmConcurrency: number;
  customPatterns: PatternCheck[];
  fix: boolean;
}

/** A single audit finding */
interface AuditFinding {
  id: string;                    // e.g., "AF-001"
  ruleId: string;                // Pattern ID (e.g., "CI-001", "SSRF-001")
  severity: Severity;
  confidence: 'high' | 'medium' | 'low';
  category: string;
  message: string;
  filePath: string;              // Relative to audit root
  line: number;
  column?: number;
  endLine?: number;
  snippet: string;               // Code snippet with context
  dataFlow?: DataFlowTrace;      // From LLM analysis
  suggestedFix?: string;         // Remediation suggestion
  source: 'tier1' | 'llm';
}

/** Data flow trace from LLM analysis */
interface DataFlowTrace {
  steps: DataFlowStep[];
}

interface DataFlowStep {
  file: string;
  line: number;
  description: string;
  code: string;
}

/** Complete audit result */
interface AuditResult {
  rootPath: string;
  startedAt: string;
  completedAt: string;
  durationMs: number;
  filesScanned: number;
  filesWithFindings: number;
  findings: AuditFinding[];
  summary: AuditSummary;
  config: AuditConfig;
}

interface AuditSummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  total: number;
  score: number;       // 0-100
  verdict: ScanVerdict; // PASS | CONCERNS | FAIL
}
```

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`)
- **CLI Framework**: Commander.js (existing dependency)
- **Testing**: Vitest (existing dev dependency)
- **File Discovery**: Node.js `fs/promises` (reuse pattern from `repo-scanner.ts`)
- **LLM Integration**: Subprocess call to `claude` CLI or `npx` adapter (no new runtime dependencies)
- **No new dependencies** for Tier 1 scanning (pure regex + existing code)

**Architecture Decisions**:

- **ADR-001: Reuse existing patterns, not fork**: Import `SCAN_PATTERNS` from `patterns.ts` and extend with a separate `AUDIT_PATTERNS` array. This keeps the existing scanner untouched and allows the audit command to have additional project-specific patterns without affecting SKILL.md scanning.
- **ADR-002: LLM via subprocess, not SDK**: Invoke the LLM via subprocess (`claude` CLI or configurable command) rather than adding an SDK dependency. This keeps the package lightweight, avoids API key management in the CLI, and lets users bring their own LLM.
- **ADR-003: SARIF as first-class output**: SARIF is the industry standard for static analysis tools. Supporting it enables integration with GitHub Code Scanning, VS Code SARIF Viewer, and other CI/CD tools without custom adapters.
- **ADR-004: Separate audit/ directory**: All audit-specific code lives in `src/audit/` to avoid polluting the existing `src/scanner/` module, which is focused on SKILL.md verification.

## Implementation Phases

### Phase 1: Foundation (T-001 to T-005)
- Audit types and interfaces
- File discovery engine (extend repo-scanner logic)
- Extended audit patterns (project-specific)
- Core audit scanner (Tier 1 orchestrator)
- CLI command registration

### Phase 2: Output Formatters (T-006 to T-009)
- Terminal formatter (default colored output)
- JSON formatter
- SARIF v2.1.0 formatter
- Markdown report generator

### Phase 3: LLM Integration (T-010 to T-012)
- LLM analysis engine (subprocess-based)
- Data flow tracing
- Fix suggestions

### Phase 4: Configuration & Polish (T-013 to T-015)
- Config file loader
- Integration tests (end-to-end audit on test fixtures)
- SpecWeave skill wrapper

## Testing Strategy

**TDD mode** (RED -> GREEN -> REFACTOR for each task):

- **Unit tests**: Each module (`file-discovery.ts`, `audit-scanner.ts`, `audit-patterns.ts`, formatters) has a corresponding `.test.ts` file
- **Integration tests**: End-to-end tests using fixture directories with known vulnerabilities
- **SARIF validation**: Test SARIF output against the schema
- **Coverage target**: 90%+ across all new code
- **Existing tests**: All existing `src/scanner/*.test.ts` tests must continue to pass

## Technical Challenges

### Challenge 1: False Positive Management
**Problem**: Regex patterns produce false positives on legitimate code (e.g., `exec` in test descriptions, `eval` in comments about security).
**Solution**: Add `safeContexts` regex arrays to patterns. Use LLM tier to filter false positives with data flow analysis. Add per-file `.vskill-ignore` comment support.
**Risk**: Medium. Mitigated by confidence scores and LLM verification.

### Challenge 2: LLM Availability and Latency
**Problem**: LLM analysis requires a working LLM provider which may not be available or may be slow.
**Solution**: LLM tier is optional (`--tier1-only` to skip). Configurable timeout. Graceful fallback to Tier 1 only results if LLM fails. Concurrent file analysis with configurable parallelism.
**Risk**: Low. Tier 1 provides value even without LLM.

### Challenge 3: Large Repository Performance
**Problem**: Scanning thousands of files must be fast.
**Solution**: Stream-based file discovery with early termination at max file limit. Tier 1 is pure regex (microseconds per file). LLM only runs on flagged files (typically < 10% of total). Progress indicator for long scans.
**Risk**: Low. The existing repo-scanner already handles this pattern.
