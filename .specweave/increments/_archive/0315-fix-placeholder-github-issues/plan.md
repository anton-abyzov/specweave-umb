# Implementation Plan: Fix Placeholder GitHub Issue Creation

## Overview

Add multi-layer defense against creating GitHub issues from template placeholders. Primary fix is a 1-line guard in the TypeScript parser; secondary fixes harden the bash handlers.

## Architecture

### Defense Layers (Defense-in-Depth)

1. **File-level guard** (existing): `isTemplateFile()` in `ExternalIssueAutoCreator.createForIncrement()` — catches fully-template specs
2. **Story-level guard** (NEW): Skip `[Story Title]` in `parseUserStories()` — catches individual placeholder stories in partially-filled specs
3. **Bash-level guard** (NEW): `grep '[Story Title]'` in both bash handlers — catches template specs in the bash code path
4. **Debounce increase** (NEW): 10s → 30s — gives PM more time to fill the spec before handler fires

### Files Modified

| File | Change |
|------|--------|
| `src/sync/external-issue-auto-creator.ts` | Add placeholder skip in `parseUserStories()` |
| `plugins/specweave-github/hooks/github-auto-create-handler.sh` | Add template guard + increase debounce |
| `plugins/specweave/hooks/v2/handlers/universal-auto-create-dispatcher.sh` | Fix path resolution + add template guard + increase debounce |
| `tests/unit/sync/external-issue-auto-creator.test.ts` | Add placeholder skip tests |

## Implementation Phases

### Phase 1: TypeScript Guard (US-001)
- Add `[Story Title]` skip in `parseUserStories()` after line 340
- Add bracket-placeholder skip pattern
- Add unit tests

### Phase 2: Bash Guards (US-002)
- Add template marker grep guard to `github-auto-create-handler.sh`
- Add template guard to `universal-auto-create-dispatcher.sh`
- Fix dispatcher path resolution for umbrella repos
- Increase debounce to 30s in both files

### Phase 3: Cleanup (US-003)
- Close issues #1238-#1248 via `gh issue close`

## Testing Strategy

- Unit tests for `parseUserStories()` placeholder skip
- Manual verification of bash handler exit on template spec
- Run existing test suite to verify no regressions
