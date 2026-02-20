# 0244: Plugin Security Self-Scan

## Problem

External security auditors (Gen Agent Trust Hub, Socket, Snyk) flag issues in our published skills that we could catch ourselves before publishing. The jira-sync skill received a MEDIUM-risk audit with 4 findings (CREDENTIALS_UNSAFE, DATA_EXFILTRATION, COMMAND_EXECUTION, PROMPT_INJECTION) — all preventable with pre-publish validation.

We need an internal security scanning capability that runs against our own SKILL.md files before they reach external auditors.

## Context

- **Trigger**: Gen Agent Trust Hub audit of `jira-sync` skill on skills.sh (Feb 17, 2026)
- **Related**: Increment 0242 (malicious skills registry) covers external skill scanning
- **This increment**: Internal self-scan for our own plugins before publishing

## User Stories

### US-001: SKILL.md Security Linter

As a plugin author, I want to run a security scan against SKILL.md files before publishing, so that external auditors find fewer issues.

**Acceptance Criteria:**
- [x] AC-US1-01: Scan detects CREDENTIALS_UNSAFE — skills that instruct agents to collect or write secrets
- [x] AC-US1-02: Scan detects DATA_EXFILTRATION — skills that read secrets and transmit to user-controlled destinations without strict validation
- [x] AC-US1-03: Scan detects COMMAND_EXECUTION — skills using Bash with unquoted variable interpolation in shell commands
- [x] AC-US1-04: Scan detects PROMPT_INJECTION — skills that interpolate untrusted input without boundary markers or sanitization
- [x] AC-US1-05: Scan produces a report with finding, severity, line reference, and suggested fix
- [x] AC-US1-06: Exit code reflects scan result (0=pass, 1=concerns, 2=fail)

### US-002: Pre-Publish Hook Integration

As a plugin author, I want the security scan to run automatically before `npm publish` or `/sw:npm`, so I can't accidentally publish a flagged skill.

**Acceptance Criteria:**
- [x] AC-US2-01: Scan integrates as a pre-publish step in the npm release workflow
- [x] AC-US2-02: Publish is blocked if any CRITICAL or HIGH findings exist
- [x] AC-US2-03: MEDIUM and LOW findings produce warnings but don't block

### US-003: Scan All Plugins in Batch

As a maintainer, I want to scan all plugins at once and get a summary report, so I can prioritize fixes across the entire plugin ecosystem.

**Acceptance Criteria:**
- [x] AC-US3-01: Batch scan covers all `plugins/*/skills/*/SKILL.md` files
- [x] AC-US3-02: Summary table shows skill name, finding count by severity, and overall status
- [x] AC-US3-03: Results are exportable as JSON for CI integration

## Detection Rules

### CREDENTIALS_UNSAFE (MEDIUM)
- Pattern: Skill instructs agent to prompt for tokens/passwords/keys
- Pattern: Skill writes secrets to files (`.env`, config files)
- Pattern: Bash snippets with `cat >> .env` or `echo TOKEN=`
- Fix: Skill should only CHECK for credential presence, never collect or write

### DATA_EXFILTRATION (MEDIUM)
- Pattern: Skill reads secrets and passes to `curl`/`fetch` with user-controlled URLs
- Pattern: Domain validation allows wildcards or IP addresses
- Fix: Strict hostname validation, HTTPS-only, SSRF prevention (no localhost/private IPs)

### COMMAND_EXECUTION (LOW)
- Pattern: Bash snippets with unquoted `$VARIABLE` in command arguments
- Pattern: `eval`, `source`, or `sh -c` with user input
- Fix: Double-quote all variables, use array arguments where possible

### PROMPT_INJECTION (LOW)
- Pattern: User input interpolated into bash without sanitization
- Pattern: No boundary markers between trusted and untrusted content
- Fix: Add input validation regex, boundary markers, sanitization steps

## Technical Notes

- Implement as a SpecWeave skill (`/sw:skill-audit`) or standalone script
- Parse SKILL.md as markdown, extract bash code blocks, apply regex rules
- Consider AST-based bash analysis for more accurate detection
- Map findings to the same categories that Gen Agent Trust Hub uses for consistency

## Priority

HIGH — directly impacts our public reputation on skills.sh audits page
