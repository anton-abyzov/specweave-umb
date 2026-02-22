# Spec: Cleanup Dead CLI Commands

**Increment**: 0213 | **Type**: hotfix | **Priority**: P2

## Problem

`src/commands/version.ts` exports `versionCommand()` but is never imported anywhere. Commander's `.version()` flag in `index.ts` already handles version output. The file is dead code.

## Solution

Delete `src/commands/version.ts`.

## Acceptance Criteria

- [x] AC-01: `src/commands/version.ts` is removed
- [x] AC-02: All existing tests still pass
- [x] AC-03: `vskill --version` still works via commander's built-in flag
