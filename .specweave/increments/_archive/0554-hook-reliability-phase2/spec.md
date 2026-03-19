---
increment: 0554-hook-reliability-phase2
title: Fix Remaining Hook Reliability Issues
type: bug
priority: P1
status: completed
created: 2026-03-17T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Remaining Hook Reliability Issues

## Problem Statement

SpecWeave hook scripts have five classes of reliability defects discovered during deep analysis: (1) PreToolUse fires on every Edit/Write regardless of target file, adding 200-500ms overhead per operation; (2) dashboard cache update scripts skip priority/type normalization that rebuild scripts perform, creating phantom counter keys; (3) matcher_content regexes match string literals inside JSON payloads, causing false positives on test files; (4) five jq `| length` operations lack null-coalescing, crashing on empty/null arrays; (5) four scripts use bare `.specweave/` relative paths that break when cwd differs from project root.

## Goals

- Eliminate unnecessary hook invocations on non-increment file operations
- Ensure dashboard cache consistency between update and rebuild paths
- Prevent false-positive hook triggers from test file content
- Harden all jq operations against null/empty inputs
- Make all scripts resilient to arbitrary working directory

## User Stories

### US-001: PreToolUse matcher_content and early file_path exit (P1)
**Project**: specweave
**As a** developer using SpecWeave
**I want** the PreToolUse hook to only fire when editing increment files
**So that** non-increment file operations do not incur 200-500ms overhead

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the PreToolUse entry in hooks.json, when the hook configuration is inspected, then a matcher_content field exists with a file_path-scoped regex targeting `.specweave/increments/`
- [x] **AC-US1-02**: Given pre-tool-use.sh receives a tool_input for a file outside `.specweave/increments/`, when the script starts, then it exits with code 0 before invoking jq
- [x] **AC-US1-03**: Given pre-tool-use.sh previously used `[[ ! -d ".specweave" ]]`, when the script runs from a subdirectory, then it locates the project root via a walk-up loop or lib/common-setup.sh sourcing instead of relying on a bare relative path

---

### US-002: Dashboard cache normalization and fallback path (P1)
**Project**: specweave
**As a** developer viewing the SpecWeave dashboard
**I want** the update-dashboard-cache.sh script to normalize priority and type values identically to rebuild-dashboard-cache.sh
**So that** increments with raw values like "medium" do not create phantom counter keys

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given update-dashboard-cache.sh processes an increment with `priority: "medium"`, when normalization runs, then the value is mapped to `P1` matching the rebuild script behavior
- [x] **AC-US2-02**: Given update-dashboard-cache.sh processes an increment with raw type values, when normalization runs, then the type is normalized using the same function as rebuild-dashboard-cache.sh
- [x] **AC-US2-03**: Given rebuild-dashboard-cache.sh fallback path references `$PROJECT_ROOT/plugins/...`, when the script runs at hook time where PROJECT_ROOT is unset, then the path resolves via `BASH_SOURCE` instead

---

### US-003: matcher_content false positive elimination (P1)
**Project**: specweave
**As a** developer editing test files that contain `.specweave/increments/` as string literals
**I want** the matcher_content regex to only match the file_path field in JSON tool input
**So that** hooks do not falsely trigger on test file content

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given hooks.json PostToolUse matcher_content, when updated, then the regex is scoped to `"file_path"\s*:\s*"[^"]*\.specweave/increments/`
- [x] **AC-US3-02**: Given hooks.json PreToolUse matcher_content, when updated, then the regex uses the same file_path-scoped pattern
- [x] **AC-US3-03**: Given .claude/settings.json matcher_content, when updated, then the regex uses the same file_path-scoped pattern
- [x] **AC-US3-04**: Given a Write tool call targeting `/tmp/test.ts` whose content contains the string `.specweave/increments/0001-foo`, when the hook evaluates matcher_content, then the hook does not trigger

---

### US-004: Null-coalescing for jq length operations (P1)
**Project**: specweave
**As a** developer running SpecWeave in sessions with empty or uninitialized state
**I want** all jq `| length` operations to have `// []` null-coalescing guards
**So that** scripts do not crash on null or missing array values

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given auto-status.sh lines 132-134 contain 3 jq `| length` operations, when patched, then each operation uses `// [] | length` instead of bare `| length`
- [x] **AC-US4-02**: Given cancel-auto.sh line 54 contains a jq `| length` operation, when patched, then it uses `// [] | length`
- [x] **AC-US4-03**: Given user-prompt-submit.sh line 2191 contains a jq `| length` operation, when patched, then it uses `// [] | length`

---

### US-005: Bare relative path elimination (P1)
**Project**: specweave
**As a** developer whose shell working directory is not the project root
**I want** all hook scripts to locate `.specweave/` via proper root detection
**So that** hooks work correctly regardless of the current working directory

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given startup-health-check.sh uses bare `.specweave/` paths, when patched, then it resolves the project root via walk-up detection or lib/common-setup.sh before referencing `.specweave/`
- [x] **AC-US5-02**: Given status-completion-guard.sh uses bare `.specweave/` paths, when patched, then it resolves the project root before referencing `.specweave/`
- [x] **AC-US5-03**: Given increment-existence-guard.sh uses bare `.specweave/` paths, when patched, then it resolves the project root before referencing `.specweave/`
- [x] **AC-US5-04**: Given pre-tool-use.sh uses bare `.specweave/` paths (beyond the fix in US-001), when patched, then all remaining bare references resolve via the detected root

## Out of Scope

- npm update in umbrella repo (operational, not a source fix)
- Shell script test harness (separate increment)
- Centralizing root detection into a shared lib/common-setup.sh module (separate refactor)
- Proposing a matcher_file_path feature to the Claude Code team
- Refactoring hook scripts to a different language

## Technical Notes

### Dependencies
- hooks.json configuration format (Claude Code hook system)
- .claude/settings.json matcher_content syntax
- jq availability in shell environment
- BASH_SOURCE variable for path resolution

### Constraints
- matcher_content regexes must conform to Claude Code's regex engine (PCRE-compatible)
- Walk-up root detection must terminate at filesystem root to avoid infinite loops
- Normalization functions must be idempotent (normalizing an already-normalized value is a no-op)

### Architecture Decisions
- Use walk-up loop pattern (`while [[ "$dir" != "/" ]]; do ... dir=$(dirname "$dir"); done`) rather than importing a shared library, since centralizing into lib/common-setup.sh is a separate refactor
- Duplicate normalization functions from rebuild into update script rather than extracting shared code, keeping the fix minimal

## Non-Functional Requirements

- **Performance**: PreToolUse hook skip path must exit in under 5ms for non-increment files (no jq invocation)
- **Compatibility**: All fixes must work on macOS (BSD) and Linux (GNU) shells; no bash 5+ features required
- **Reliability**: No jq operation in any hook script may crash on null, empty, or missing input

## Edge Cases

- **Symlinked .specweave/**: Walk-up root detection must follow symlinks when checking for `.specweave/` directory existence
- **Nested .specweave/ directories**: Walk-up should find the nearest `.specweave/` ancestor, not a parent workspace
- **Empty metadata.json**: Normalization must handle missing priority/type fields gracefully (default to "P2"/"feature")
- **matcher_content with special characters**: File paths containing regex metacharacters (brackets, dots) in directory names must not break the scoped regex

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Walk-up loop hits symlink cycle | 0.1 | 5 | 0.5 | Cap iterations at 50 levels |
| Regex change breaks legitimate hook triggers | 0.2 | 8 | 1.6 | Verify regex matches all `.specweave/increments/*/spec.md` path patterns before deploying |
| Duplicated normalization diverges from rebuild over time | 0.3 | 4 | 1.2 | Add code comment referencing rebuild script as source of truth |

## Success Metrics

- Zero hook invocations for file operations outside `.specweave/increments/`
- Dashboard cache matches rebuild output after update operations (no phantom keys)
- Zero false-positive hook triggers from test files containing `.specweave/increments/` strings
- Zero jq crashes from null/empty arrays across all hook scripts
- All hook scripts pass when invoked from non-root working directories
