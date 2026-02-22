# Implementation Plan: vskill install UX improvements

## Overview

This increment makes five targeted changes to the `vskill install` interactive wizard and its supporting prompt utilities. All changes are in the vskill CLI repo (`repositories/anton-abyzov/vskill/`), affecting three files primarily: `src/utils/prompts.ts`, `src/commands/add.ts`, and `src/discovery/github-tree.ts`.

## Architecture

### Components Affected

- **`src/utils/prompts.ts`** -- Core prompt utilities. Changes:
  - Add ANSI escape sequence filtering in `promptCheckboxList` and `promptChoice`
  - Add range/comma input parsing in `promptCheckboxList`
  - Update checkbox render to show instructions with range syntax

- **`src/commands/add.ts`** -- Install wizard flow. Changes:
  - Remove scope and method prompt steps (use defaults: project + symlink)
  - Add `--copy` flag support
  - Pass skill descriptions to checkbox items
  - Update summary display

- **`src/discovery/github-tree.ts`** -- Skill discovery. Changes:
  - Add optional `description` field to `DiscoveredSkill`
  - Fetch first content lines from each SKILL.md to extract descriptions
  - Parallel fetch with graceful fallback

### New Utility Functions

- `parseToggleInput(input: string, maxIndex: number): number[]` -- in `src/utils/prompts.ts`
- `extractDescription(content: string): string | undefined` -- in `src/discovery/github-tree.ts`

## Technology Stack

- **Language**: TypeScript (ESM with `.js` imports)
- **Test Framework**: Vitest
- **No new dependencies** -- all changes use existing Node.js APIs

## Implementation Phases

### Phase 1: Prompt System Enhancements (US-002, US-004)
1. Add `isEscapeSequence()` helper to detect ANSI escape codes
2. Add `parseToggleInput()` to parse range/comma input
3. Integrate both into `promptCheckboxList` and `promptChoice`
4. Update render instructions text

### Phase 2: Wizard Simplification (US-001, US-003)
1. Remove scope and method prompts from the interactive wizard
2. Default to project scope + symlink method
3. Add `--copy` CLI flag
4. Update summary to show defaults
5. Fix prompt label text (remove colons, make concise)

### Phase 3: Skill Descriptions (US-005)
1. Add `description` field to `DiscoveredSkill`
2. Add `extractDescription()` helper
3. Fetch descriptions during discovery (parallel, with timeout)
4. Pass descriptions to checkbox items in wizard

### Phase 4: Testing
1. Unit tests for `parseToggleInput`
2. Unit tests for escape sequence filtering
3. Unit tests for `extractDescription`
4. Integration tests for reduced wizard flow
5. Integration tests for description display

## Testing Strategy

- TDD mode: write failing tests first, then implement
- Unit tests in `*.test.ts` files alongside source
- All existing tests must continue to pass
- New tests use Vitest with ESM mocking (`vi.mock()`)

## Technical Challenges

### Challenge 1: Arrow Keys in Line-Buffered Mode
**Context**: The prompter uses `readline` in line-buffered mode (`terminal: false`), so arrow keys arrive as multi-byte escape sequences within a single line.
**Solution**: Filter lines that start with `\x1b[` or contain only escape sequences. This handles the common case without switching to raw mode.
**Risk**: Low -- escape sequences in line mode are well-defined patterns.

### Challenge 2: Parallel Description Fetching
**Context**: Fetching description content for each skill requires additional HTTP requests during discovery.
**Solution**: Use `Promise.allSettled` with a per-request timeout (3s) to avoid blocking the install flow. Failed fetches result in `undefined` description.
**Risk**: Low -- descriptions are optional and gracefully degrade.
