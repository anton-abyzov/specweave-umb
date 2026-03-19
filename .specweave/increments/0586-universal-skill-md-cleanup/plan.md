# Implementation Plan: Universal SKILL.md + Dead Code Cleanup

## Overview

Three targeted changes: restructure SKILL.md for universal CLI-first usage, remove dead pre-generation code, update help text.

## Architecture

No architectural changes. This is a documentation + dead code cleanup refactor.

### Components Modified
- `plugins/specweave/skills/increment/SKILL.md`: Restructured Steps 3-4, Critical Rules
- `src/cli/commands/create-increment.ts`: Removed dead `getNextIncrementNumber()` call
- `bin/specweave.js`: Updated next-id description

## Implementation Phases

### Phase 1: SKILL.md Restructure
- Remove legacy 3c two-step creation section
- Reorder Step 4: direct writing as default, team delegation as enhancement
- Update Critical Rules to be non-absolute

### Phase 2: Dead Code Removal
- Replace pre-generation block with simple placeholder assignment
- Remove unused import

### Phase 3: Help Text
- Update next-id command description

## Testing Strategy

- Existing unit tests for increment-utils and create-increment-auto-id must pass
- Verify SKILL.md only references TeamCreate/Agent/SendMessage in the enhanced section
