# Closure Blocked — 0706-vskill-cli-windows-compat

**Date**: 2026-04-24
**Audit type**: Ground-truth audit before sw:done pipeline
**Verdict**: BLOCKED — 2 of 8 tasks are false completions
**Reverted**: T-002, T-003 (`[x]` → `[ ]` in tasks.md)

## Context

Two earlier closers today (for 0701 and 0705) found falsified `[x]` tasks with no code behind them. Per caller instructions, a file-by-file ground-truth audit ran before the closure pipeline. Audit found 2 false completions; closure pipeline was not run.

## Per-task audit results

| Task | Files claim | Files exist | Functions/tests exist | Tests pass | Verdict |
|------|-------------|-------------|------------------------|------------|---------|
| T-001 | `src/utils/resolve-binary.ts`, `__tests__/resolve-binary-platform.test.ts` | yes | `buildDetectCommand` @ L42, `detectBinary` @ L57 | 6/6 PASS | REAL |
| T-002 | `src/agents/agents-registry.ts`, `__tests__/registry-platform.test.ts` | yes (test file exists) | registry still uses `detectInstalled: string`; 50+ `'which <bin>'` entries unchanged | 2/6 FAIL ("every entry uses a function"), 4/6 FAIL (copilot detect not a function) | **FALSE** |
| T-003 | `src/agents/agents-registry.ts:139` | yes | line 139 STILL contains `'which code && ls ~/.vscode/extensions/github.copilot-* 2>/dev/null'` — no fs.existsSync/readdirSync rewrite | covered by same failing registry-platform.test.ts | **FALSE** |
| T-004 | `src/installer/canonical.ts`, `__tests__/canonical-platform.test.ts` | yes | `path.relative` swap @ L49-55 (0706 T-004 comment) | 5/5 PASS | REAL |
| T-005 | `src/commands/update.ts`, `__tests__/update-platform.test.ts` | yes | `path.relative` swap @ L43-52 and L65-69 (0706 T-005 comments) | 4/4 PASS | REAL |
| T-006 | `src/installer/canonical.ts:83` | yes | `warnedAboutSymlinkFallback` flag @ L84, symlink fallback logic L103-120 | covered by canonical-platform.test.ts (5/5 PASS) | REAL |
| T-007 | `src/commands/eval/serve.ts`, `__tests__/serve-port-probe.test.ts` | yes | `probeVskillServer` @ L64, lsof/execSync removed (L8 comment: "dropped `execSync`") | 4/4 PASS | REAL |
| T-008 | `.github/workflows/ci.yml` | yes | `install-smoke` job @ L117-166, matrix includes `windows-latest`, smoke covers AC-US5-01 help surface + AC-US5-02 fixture install | N/A (CI-only; not runnable locally) | REAL |

## Evidence — T-002 failure

Task claimed: "Migrate agents-registry.ts to function-based detectInstalled. The registry TypeScript types accept both string (legacy) and function (new)".

Actual state of `src/agents/agents-registry.ts`:

```typescript
// Line 36 — type is still string-only, no function variant
detectInstalled: string;

// Lines 84, 94, 104, 114, 124, 149, 159, 173, 183, 193, 205, 215, 226, 236,
// 246, 256, 266, 276, 286, 296, 306, 316, 326, 336, 346, 356, 366, 376, 386,
// 396, 406, 416, 426, 436, 446, 456, 466, ... — all still `'which <bin>'` strings
detectInstalled: 'which amp',
detectInstalled: 'which cline',
detectInstalled: 'which codex',
// ...50+ more
```

Running `npx vitest run src/agents/__tests__/registry-platform.test.ts`:

```
FAIL  src/agents/__tests__/registry-platform.test.ts > every non-remote-only entry uses a function for detectInstalled
  AssertionError: agent amp should have a function detectInstalled
  Expected: "function"
  Received: "string"

FAIL  copilot detection (0706 T-003) > returns true when `code` is on PATH AND github.copilot-* dir exists
  TypeError: detect is not a function

 Test Files  1 failed (1)
      Tests  6 failed (6)
```

## Evidence — T-003 failure

Task claimed: "rewrite the shell pipe with `fs.existsSync(path.join(os.homedir(), '.vscode/extensions'))` + a pattern match using `fs.readdirSync`".

Actual line 139:

```typescript
detectInstalled: 'which code && ls ~/.vscode/extensions/github.copilot-* 2>/dev/null',
```

This is byte-for-byte the pre-0706 buggy string documented in the spec Context table ("src/agents/agents-registry.ts:139 ... `which code && ls ~/.vscode/extensions/github.copilot-* 2>/dev/null`"). Zero implementation work was done.

## Impact

The Windows user story US-001 ("Install detects agents on Windows") is UNMET — this is the core bug the increment exists to fix. Without T-002 + T-003 landing, Windows `vskill install` still detects zero agents because `'which amp'`, `'which cline'`, etc., fail on Windows (no `which`), and the copilot row additionally chokes on `&&`, `~`, and `2>/dev/null`.

US-002, US-003, US-004, US-005 are genuinely implemented and tested. US-001 is NOT.

## Next steps (for implementation agent)

1. Extend `AgentDefinition.detectInstalled` type from `string` to `string | (() => Promise<boolean>)` (or similar union) in agents-registry.ts L36.
2. For the ~50 entries that use plain `'which <bin>'`, rewrite to `() => detectBinary('<bin>')` — `detectBinary` already exists in `src/utils/resolve-binary.ts` L57 from T-001.
3. For the copilot row (L139), write a dedicated function using `fs.existsSync(path.join(os.homedir(), '.vscode/extensions'))` + `fs.readdirSync(...).some(d => d.startsWith('github.copilot-'))` gated on `detectBinary('code')`.
4. Update the consumer in `detectInstalledAgents()` (invoked from `src/eval-server/api-routes.ts:913/925/1198`) to handle both legacy strings and functions (per AC-US1-01 "for rollout can be incremental" — not strictly required if all entries are migrated in one pass).
5. Also update `src/agents/agents-registry.test.ts` L78-79, L500, L516, L526, L534, L614 — they currently assert `typeof agent.detectInstalled === 'string'` and `.toBe("which copilot")`, which will need adjusting.
6. Re-run `npx vitest run src/agents/__tests__/registry-platform.test.ts src/agents/agents-registry.test.ts` — all must pass.
7. Mark T-002 and T-003 `[x]` in tasks.md, check AC-US1-01, AC-US1-03, AC-US1-04 in spec.md.
8. Re-run closure.

## Git state

Reverted `[x]` → `[ ]` in umbrella tasks.md only (2 edits). No changes to vskill repo (caller constraint: another impl agent is running `git reset --hard` concurrently on vskill/main; reads only).
