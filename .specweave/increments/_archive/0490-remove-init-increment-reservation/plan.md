# Implementation Plan: Remove 0001-project-setup reservation

## Overview

This is a documentation cleanup with a code audit confirmation. The `specweave init` command (v1.0.415) already does not create any `0001-project-setup` increment. However, documentation still references this phantom increment, causing confusion for new users. The work consists of updating stale docs and confirming no legacy code paths remain.

## Architecture

### Affected Components
- **docs-site/docs/quick-start.md**: Shows `0001-project-setup/` in init output tree; first user increment shown as `0002-click-counter`
- **docs-site/docs/glossary/terms/greenfield.md**: Uses `0001-project-setup-and-auth` as an example increment name

### Code Audit Targets (confirmation only, no changes expected)
- **src/cli/helpers/init/directory-structure.ts**: `createDirectoryStructure()` creates only core dirs (increments/, cache/, state/, logs/reflect/). No seed increment.
- **src/cli/commands/init.ts**: Init flow calls `createDirectoryStructure` -> `copyTemplates` -> `createConfigFile`. None create increment folders.
- **src/core/increment/increment-utils.ts**: `getNextIncrementNumber()` gap-fills from candidate=1, returns `"0001"` on fresh project.

### No Changes Needed
- **src/templates/CLAUDE.md.template**: Already correctly says "Your first increment starts at 0001"
- **src/templates/AGENTS.md.template**: Shows `0001-feature/` as a generic example (correct)

## Technology Stack

- **Markdown**: Documentation files only
- **No runtime code changes**: Audit-only for source files

## Design Decisions

**ADR: Documentation-only approach** -- The init command was already simplified in v1.0.415. The `0001-project-setup` reservation was removed with that refactoring. This increment only cleans up stale docs that were not updated at that time.

**ADR: Keep greenfield example as user-created** -- The greenfield glossary uses `0001-project-setup-and-auth` in a code example showing user commands. Rename to avoid confusion but keep the intent.

## Implementation Phases

### Phase 1: Documentation Updates
1. Update quick-start.md: Remove phantom increment, renumber first user increment to 0001
2. Update greenfield glossary: Rename misleading example

### Phase 2: Code Audit
3. Confirm no init code creates increments (expected: no code changes needed)

## Testing Strategy

- Run existing unit tests for init to confirm nothing breaks
- Manual verification: `specweave init` on a fresh directory should create no increment folders

## Risk Assessment

- **Low risk**: Documentation-only changes with no behavior impact
- **No test changes expected**: No existing test references `0001-project-setup` in the init flow
