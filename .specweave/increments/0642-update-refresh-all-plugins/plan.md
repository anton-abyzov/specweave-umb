---
increment: 0642-update-refresh-all-plugins
---

# Architecture Plan

## Overview

One-line fix in `src/cli/commands/update.ts`. Change `all: options.all` to `all: options.all ?? true` so `specweave update` refreshes all plugins by default, matching `init` behavior.

## Root Cause

`update.ts:394` passes `options.all` (undefined by default) to `refreshPluginsCommand()`. This causes `refresh-plugins.ts:287` to filter to only the core `sw` plugin. Non-core skills like `help/` are never refreshed.

## Files Modified

| File | Change |
|------|--------|
| `src/cli/commands/update.ts:394` | `all: options.all ?? true` |
| `src/cli/commands/update.ts` (docstrings) | Reflect new default |
| `tests/unit/cli/commands/update.test.ts` | Expect `all: true` |
