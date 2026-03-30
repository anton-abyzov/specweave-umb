# Implementation Plan: Add --bare flag to Claude CLI subprocess spawns

## Overview

Surgical addition of `--bare` to args arrays in three files. Each file has a function that builds CLI arguments for `spawnSync`/`spawn` -- we prepend `--bare` to each. In `llm-plugin-detector.ts`, we also remove the now-redundant `--setting-sources ''` pair since `--bare` subsumes it.

## Architecture

No architectural changes. This modifies argument construction in existing functions.

### Files to Modify

1. **`src/core/llm/providers/claude-code-provider.ts`** - `executeClaudeCommand()` method
2. **`src/core/auto/completion-evaluator.ts`** - `executeClaudeCli()` function
3. **`src/core/lazy-loading/llm-plugin-detector.ts`** - `detectIntent()` call site

### Test Files to Create/Modify

1. **`tests/unit/core/llm/providers/claude-code-provider.test.ts`** - Verify `--bare` in spawn args
2. **`tests/unit/core/auto/completion-evaluator.test.ts`** - Verify `--bare` in spawn args
3. **`tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`** - Verify `--bare` replaces `--setting-sources ""`

## Implementation

### Change 1: claude-code-provider.ts (line ~130)

```typescript
// Before
const args: string[] = [];
if (this.skipPermissions) {
  args.push('--dangerously-skip-permissions');
}
args.push('--print', prompt, '--output-format', 'json', '--model', model);

// After
const args: string[] = ['--bare'];
if (this.skipPermissions) {
  args.push('--dangerously-skip-permissions');
}
args.push('--print', prompt, '--output-format', 'json', '--model', model);
```

### Change 2: completion-evaluator.ts (lines ~294, ~561)

```typescript
// Before (two call sites)
executeClaudeCli(['-p', prompt, '--model', model], timeout);
executeClaudeCli(['-p', prompt, '--model', 'haiku'], timeout);

// After
executeClaudeCli(['--bare', '-p', prompt, '--model', model], timeout);
executeClaudeCli(['--bare', '-p', prompt, '--model', 'haiku'], timeout);
```

### Change 3: llm-plugin-detector.ts (line ~902)

```typescript
// Before
executeClaudeCli(['-p', fullPrompt, '--model', 'haiku', '--output-format', 'json', '--setting-sources', ''], timeout);

// After (--bare subsumes --setting-sources '')
executeClaudeCli(['--bare', '-p', fullPrompt, '--model', 'haiku', '--output-format', 'json'], timeout);
```

## Technology Stack

- **Language**: TypeScript (ESM)
- **Testing**: Vitest with `vi.mock()` for child_process mocking
- **No new dependencies**

## Testing Strategy

TDD: Write failing tests first that assert `--bare` is in the spawn args, then make the changes.

- Mock `child_process.spawn`/`spawnSync` to capture args
- Assert `args[0] === '--bare'` or `args.includes('--bare')`
- Assert `--setting-sources` is NOT in args for llm-plugin-detector
- Run existing test suite to verify no regressions

## Technical Challenges

### Challenge 1: --bare with --dangerously-skip-permissions
**Risk**: Flag ordering might matter.
**Mitigation**: `--bare` goes first (position 0), `--dangerously-skip-permissions` follows. Both are top-level flags processed before the command, so order doesn't matter per Claude CLI argument parser.

### Challenge 2: Existing tests may mock specific arg patterns
**Risk**: Tests checking exact arg arrays will break.
**Mitigation**: Update mocks to expect `--bare` in the args. This is the intended test change.
