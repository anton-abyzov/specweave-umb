# Implementation Plan — 0675 Skill-Creator Detection Hotfix

## Overview

Extend `isSkillCreatorInstalled()` in `repositories/anton-abyzov/vskill/src/utils/skill-creator-detection.ts` with two new detection branches, add one optional field to `AgentDefinition`, and fix one caller. Strict TDD: tests first, then implementation. No architectural changes, no new modules.

## Architecture

**Pure filesystem-only utility.** The function signature is unchanged: `export function isSkillCreatorInstalled(projectRoot?: string): boolean`. All new logic lives inside the existing function body. No call sites require refactoring except `serve.ts:28` (one-line fix to pass `root`).

### Current detection order (preserved)

1. `~/.agents/skills/skill-creator` — global canonical
2. `{projectRoot}/.agents/skills/skill-creator` — project canonical (hardcoded `.agents/skills`)
3. Each agent's `globalSkillsDir/skill-creator` — registry-driven
4. Each agent's `pluginCacheDir` nested walk — two-level tree under `{dir}/{marketplace}/`

### New detection branches

**Branch 2b — project-local agent-native installs** (after step 2, before step 3):

```ts
if (projectRoot) {
  for (const agent of AGENTS_REGISTRY) {
    if (existsSync(join(projectRoot, agent.localSkillsDir, 'skill-creator'))) return true;
  }
}
```

- Re-uses existing `AGENTS_REGISTRY` — no hardcoded `.claude/skills`, `.cursor/skills`, etc.
- Guarded by `if (projectRoot)` — preserves behavior when called with no args.
- Idempotent overlap with step 2: when an agent's `localSkillsDir === '.agents/skills'` the same path is checked twice. Cost: one extra `existsSync` call. No correctness issue.

**Branch 4b — marketplace-synced plugins** (interleaved with step 4's agent loop):

```ts
if (agent.pluginMarketplaceDir) {
  const mktRoot = agent.pluginMarketplaceDir.replace('~', home);
  try {
    if (existsSync(mktRoot)) {
      for (const mkt of readdirSync(mktRoot, { withFileTypes: true })) {
        if (!mkt.isDirectory()) continue;
        const pluginsDir = join(mktRoot, mkt.name, 'plugins');
        if (!existsSync(pluginsDir)) continue;
        for (const plugin of readdirSync(pluginsDir, { withFileTypes: true })) {
          if (plugin.isDirectory() && plugin.name.includes('skill-creator')) return true;
        }
      }
    }
  } catch { /* ignore permission errors */ }
}
```

- Mirrors the existing `pluginCacheDir` walker pattern (try/catch around readdirSync, `includes('skill-creator')` predicate).
- Key structural difference from cache walker: extra `'plugins'` segment between marketplace and plugin dirs (`{mktRoot}/{marketplace}/plugins/{plugin}/` vs `{cacheDir}/{marketplace}/{plugin}/`).
- Short-circuits on first match.

### Agent registry change

New optional field on `AgentDefinition` (`src/agents/agents-registry.ts`):

```ts
/** Directory path where marketplace-synced plugin SOURCES are stored.
 *  Differs from pluginCacheDir — cache holds INSTALLED plugins at {dir}/{marketplace}/{plugin}/,
 *  while marketplaces hold SOURCES at {dir}/{marketplace}/plugins/{plugin}/. */
pluginMarketplaceDir?: string;
```

Populated only on `claude-code` entry: `pluginMarketplaceDir: '~/.claude/plugins/marketplaces'`. All other agents leave it undefined.

### Caller fix

`src/commands/eval/serve.ts:28` — change `isSkillCreatorInstalled()` to `isSkillCreatorInstalled(root)`. `root` is already resolved earlier in the same file (via `resolve(opts.root || process.cwd())`), trivially available in scope.

## Components Touched

| Component | File | Change Type |
|---|---|---|
| Detection logic | `src/utils/skill-creator-detection.ts` | Extend (add 2 branches) |
| Agent schema | `src/agents/agents-registry.ts` | Add optional field |
| Claude Code registry entry | `src/agents/agents-registry.ts` line 164 | Populate new field |
| CLI caller | `src/commands/eval/serve.ts` line 28 | One-line arg pass |
| Tests | `src/utils/__tests__/skill-creator-detection.test.ts` | **New file** |

**No changes to:** `src/eval-server/skill-create-routes.ts` (caller already passes `root` via closure), `src/eval-ui/src/components/LeftPanel.tsx` (UI consumes `GET /api/skill-creator-status` unchanged), `src/eval-ui/src/api.ts` (API shape unchanged).

## Test Strategy

**Pattern**: mirror `src/lockfile/project-root.test.ts:1-61` for real temp-dir fixtures + `src/core/__tests__/baseline.test.ts:33-88` for `vi.hoisted` + `vi.mock` of `node:os`.

**Mock setup** (test file header):

```ts
import { vi } from 'vitest';

const osMock = vi.hoisted(() => ({ home: '' }));
vi.mock('node:os', async () => {
  const actual = await vi.importActual<typeof import('node:os')>('node:os');
  return { ...actual, homedir: () => osMock.home };
});
```

Before each test, point `osMock.home` at a fresh `mkdtempSync` dir. This lets the test drive every path that resolves `~` without touching the real `$HOME`.

**Fixture helper**:

```ts
function createSkillCreatorAt(base: string, relativePath: string) {
  const dir = join(base, relativePath, 'skill-creator');
  mkdirSync(dir, { recursive: true });
  writeFileSync(join(dir, 'SKILL.md'), '---\nname: skill-creator\n---\n');
}
```

**Coverage matrix**: 13 test cases, one per AC (AC-US1-01..06, AC-US2-03..04, AC-US3-01..05). AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-05, AC-US4-* are asserted by reading source files (not runtime tests) — covered via `fs.readFileSync` + regex or schema assertions inside one dedicated "registry schema" test block.

## ADR Notes

**Decision**: Widen detection rather than refactor `AGENTS_REGISTRY` schema to unify `globalSkillsDir`/`pluginCacheDir`/`pluginMarketplaceDir` into a generic `searchPaths` array.
**Rationale**: Schema unification is a larger change that risks breaking callers in `detectInstalledAgents()` and `agents-installed-endpoint.test.ts`. Scope of hotfix is narrow; a forward-compatible additive field is safer. Follow-up refactor tracked as a backlog item for a non-hotfix increment.

**Decision**: Keep `include('skill-creator')` substring match in both walkers rather than exact equality.
**Rationale**: Existing cache walker uses substring match (probably to handle versioned plugin dir names like `skill-creator-v2`). Preserve consistency — future can tighten to exact match if versioned dirs become standardized.

## Verification Plan

1. **RED gate**: run `npx vitest run src/utils/__tests__/skill-creator-detection.test.ts` after only the test file lands. Expect AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-03 to FAIL.
2. **GREEN gate**: after implementing the two branches + field + caller fix, same command reports all cases passing.
3. **Regression gate**: `npx vitest run` full suite stays green (eval-server tests, lockfile tests, command tests untouched).
4. **Typecheck gate**: `npx tsc --noEmit` clean (new optional field doesn't break existing registry consumers).
5. **Manual smoke**: boot Studio from specweave-umb root (`node dist/index.js eval serve --root .`), hit `/api/skill-creator-status`, confirm `{"installed": true}`. Visual: left panel shows green banner.
6. **Negative smoke**: temporarily rename `.claude/skills/skill-creator` → `.claude/skills/skill-creator.bak`, reload page, confirm yellow "not installed" banner returns. Restore.
