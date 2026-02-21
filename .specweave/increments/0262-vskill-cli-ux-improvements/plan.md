# Implementation Plan: vskill CLI UX Improvements

## Overview

Three focused CLI UX changes in `repositories/anton-abyzov/vskill/`: rename `init` to `install` (alias `i`), add `search` alias for `find`, and make `submit` accept full GitHub URLs. All changes are isolated to `src/index.ts`, `src/commands/submit.ts`, `src/commands/init.ts`, and `README.md`.

## Architecture

### Components
- **src/index.ts**: Commander.js command registrations -- rename `init` to `install` with `.alias("i")`, add `.alias("search")` on `find`
- **src/commands/init.ts**: Update internal help text references from `vskill init` to `vskill install`
- **src/commands/submit.ts**: Add URL parsing to extract `owner/repo` from full GitHub URLs before existing validation
- **src/utils/validation.ts**: Add `parseGitHubSource()` function for URL normalization
- **README.md**: Update command reference table

### Data Model
No data model changes. The lockfile format, agent registry, and API client are untouched.

### API Contracts
No API changes. All changes are CLI-layer only.

## Technology Stack

- **Language/Framework**: TypeScript (ESM, `--moduleResolution nodenext`)
- **Libraries**: Commander.js (already has `.alias()` support)
- **Tools**: Vitest for testing

**Architecture Decisions**:
- **URL parsing in validation.ts**: Keeps submit.ts clean and makes the parser independently testable. The `parseGitHubSource()` function returns `owner/repo` string from either format.
- **No deprecation for init**: Clean break -- the command is renamed, not aliased. This avoids code complexity and confusion for a pre-1.0 tool.
- **search as alias, not separate command**: Uses Commander's `.alias()` so both `find` and `search` share the exact same registration. Zero code duplication.

## Implementation Phases

### Phase 1: Command renaming (index.ts + init.ts)
- Rename `init` to `install` with alias `i` in Commander registration
- Update console messages in `init.ts` referencing `vskill init`

### Phase 2: Search alias (index.ts)
- Add `.alias("search")` to the `find` command registration

### Phase 3: Submit URL support (validation.ts + submit.ts)
- Add `parseGitHubSource()` to validation.ts
- Update submit.ts to use it before owner/repo parsing
- Add tests for URL parsing edge cases

### Phase 4: Documentation (README.md)
- Update Commands section
- Update any references to `init` in code comments

## Testing Strategy

- Unit tests for `parseGitHubSource()` in `src/utils/__tests__/validation.test.ts`
- Update existing `submit.test.ts` to add URL-based test cases
- Manual verification of `--help` output for renamed commands
- Run full `vitest run` to ensure no regressions

## Technical Challenges

### Challenge 1: ESM import extensions
**Solution**: All imports must use `.js` extensions per project convention
**Risk**: Low -- existing pattern is well-established
