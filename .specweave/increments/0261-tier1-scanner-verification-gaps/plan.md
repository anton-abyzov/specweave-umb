# Implementation Plan: Fix Tier 1 Scanner Verification Gaps

## Overview

This is a focused bugfix across two repos (vskill CLI + vskill-platform) touching scan patterns, file fetching, and security check handling. All changes are additive or regex adjustments -- no structural refactoring needed.

## Architecture

### Affected Components

1. **Scan Patterns** (3 files to update):
   - `repositories/anton-abyzov/vskill/src/scanner/patterns.ts` -- primary pattern definitions
   - `repositories/anton-abyzov/vskill-platform/src/lib/scanner/patterns.ts` -- platform copy
   - `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts` -- legacy inline copy

2. **Platform Submission Pipeline** (2 files):
   - `repositories/anton-abyzov/vskill-platform/src/lib/scanner.ts` -- `fetchRepoFiles()` to fetch more files
   - `repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` -- scan concatenated content

3. **CLI Security Check** (2 files):
   - `repositories/anton-abyzov/vskill/src/commands/add.ts` -- add null-warning for platform security
   - `repositories/anton-abyzov/vskill/src/security/platform-security.ts` -- no changes needed (already returns null correctly)

### Changes Detail

#### Gap 1: New Pattern CI-008 (Pipe-to-shell)

```typescript
{
  id: "CI-008",
  name: "Pipe-to-shell execution",
  severity: "critical",
  description: "Detects piping downloaded content to a shell interpreter",
  pattern: /\b(?:curl|wget)\b[^|]*\|\s*(?:ba|z|da|k)?sh\b/g,
  category: "command-injection",
}
```

This catches: `curl URL | bash`, `curl -sL URL | sh`, `wget URL | bash`, `wget -qO- URL | zsh`, etc. The `[^|]*` allows any flags/URLs between the command and the pipe. The shell matcher covers `bash`, `sh`, `zsh`, `dash`, `ksh`.

Pattern count increases from 37 to 38. Update all `patternsChecked` test assertions.

#### Gap 2: Fix NA-001 Regex

Current: `/\b(?:curl|wget)\s+(?:-[a-zA-Z]*\s+)*(?:https?:\/\/|[\`"'])/g`

Problem: `-qO-` has a trailing dash that `[a-zA-Z]*` doesn't match.

Fixed: `/\b(?:curl|wget)\s+(?:-[\w=-]+\s+)*(?:https?:\/\/|[\`"'])/g`

The `[\w=-]+` matches letters, digits, underscores, equals, and dashes -- covering all common flag formats.

#### Gap 3: Extended File Fetching

Update `fetchRepoFiles()` to also attempt fetching:
- `index.js`
- `index.ts`
- `CLAUDE.md`
- `AGENTS.md`

Add a new field `additionalFiles: string[]` to `RepoFiles` interface. In `processSubmission()`, concatenate `skillMd` + additional files content before passing to `runTier1Scan`.

#### Gap 4: Null Warning for Platform Security

Add a console warning when `checkPlatformSecurity()` returns null in both `installSingleSkillLegacy()` and `installOneGitHubSkill()`.

## Technology Stack

- **Language**: TypeScript (ESM)
- **Testing**: Vitest (TDD -- RED/GREEN/REFACTOR)
- **Repos**: vskill (Node.js CLI), vskill-platform (Next.js 15 / Cloudflare Workers)

## Implementation Phases

### Phase 1: Pattern Fixes (CI-008 + NA-001)
- Add CI-008 pipe-to-shell pattern to all 3 pattern files
- Fix NA-001 regex in all 3 pattern files
- Update pattern count assertions (37 -> 38)
- TDD tests for both patterns

### Phase 2: Platform Multi-File Scanning
- Extend `RepoFiles` interface
- Extend `fetchRepoFiles()` to fetch additional files
- Update `processSubmission()` to scan concatenated content
- TDD tests for extended fetching and scanning

### Phase 3: Platform Security Null Warning
- Add warning output in `add.ts` for both install paths
- TDD test for warning behavior

### Phase 4: Verification
- Run all existing test suites in both repos
- Verify no regressions in pattern matching

## Testing Strategy

TDD mode: RED -> GREEN -> REFACTOR for each gap.

- **Unit tests**: Pattern matching for CI-008, NA-001 updates
- **Integration tests**: `processSubmission()` with multi-file content
- **Regression**: All existing tier1 scanner tests must pass

## Technical Challenges

### Challenge 1: Pattern Count Synchronization
Three files contain the same 37 patterns. Adding CI-008 makes it 38.
**Solution**: Update all three files and all `patternsChecked` test assertions.
**Risk**: Missing one file. Mitigated by searching for "37" in tests.

### Challenge 2: fetchRepoFiles Backward Compatibility
Adding new fields to `RepoFiles` must not break existing callers.
**Solution**: New `additionalFiles` field is an array, defaults to empty. Existing destructuring still works.
**Risk**: Low -- additive change only.

### Challenge 3: Regex Complexity
The pipe-to-shell pattern must not cause excessive backtracking.
**Solution**: Use `[^|]*` (bounded by pipe character) rather than `.*` to prevent catastrophic backtracking.
