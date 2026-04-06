# Implementation Plan: Fix shell hook permission errors

## Overview

Remove `; true` from all DCI hook patterns in SKILL.md and command .md files. Convert inline patterns in commands to script calls.

## Approach

1. Update tests first (TDD RED) — remove `; true` assertions so tests fail against current source
2. Remove `; true` from 16 SKILL.md files (21 occurrences including skill-context.sh calls)
3. Convert 8 command .md inline patterns to script calls
4. Verify all tests pass (TDD GREEN)

## Risk

Zero behavioral change. Both scripts already exit 0.
