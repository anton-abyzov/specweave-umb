# Implementation Plan: vskill update — unified skill update across all source types

## Overview

Add source-aware routing to `vskill update` by parsing the lockfile `source` field and routing to the correct fetch strategy per source type. Introduces two new modules: a pure source parser (`source-resolver.ts`) and an async fetcher (`source-fetcher.ts`). The update command is modified to use these, with registry as fallback.

## Architecture

### Components

- **`src/resolvers/source-resolver.ts`** (NEW): Pure parser. Parses lockfile `source` strings into a typed discriminated union. No I/O.
- **`src/updater/source-fetcher.ts`** (NEW): Async fetcher. Routes `ParsedSource` to the correct fetch strategy and returns `FetchResult | null`.
- **`src/commands/update.ts`** (MODIFY): Wires in the parser + fetcher before the existing `getSkill()` call. Registry becomes fallback.

### Data Model

```typescript
// source-resolver.ts
export type ParsedSource =
  | { type: "registry"; skillName: string }
  | { type: "github"; owner: string; repo: string }
  | { type: "github-plugin"; owner: string; repo: string; pluginName: string }
  | { type: "marketplace"; owner: string; repo: string; pluginName: string }
  | { type: "local"; baseName: string }
  | { type: "unknown"; raw: string };

// source-fetcher.ts
export interface FetchResult {
  content: string;
  version: string;
  sha: string;
  tier: string;
}
```

### Source String Formats

| Source String | Parsed Type |
|---|---|
| `"registry:name"` | `{ type: "registry", skillName: "name" }` |
| `"github:owner/repo"` | `{ type: "github", owner, repo }` |
| `"github:owner/repo#plugin:name"` | `{ type: "github-plugin", owner, repo, pluginName }` |
| `"marketplace:owner/repo#name"` | `{ type: "marketplace", owner, repo, pluginName }` |
| `"local:specweave"` | `{ type: "local", baseName: "specweave" }` |
| `""` / unrecognized | `{ type: "unknown", raw }` |

### Fetch Strategies

| Type | Strategy |
|---|---|
| `registry` | `getSkill(name)` — unchanged |
| `github` | `getDefaultBranch()` → fetch `raw.githubusercontent.com/{owner}/{repo}/{branch}/skills/{name}/SKILL.md` (fallback: root `SKILL.md`) |
| `github-plugin` | fetch `marketplace.json` → `getPluginSource()` → fetch all `plugins/{name}/skills/*/SKILL.md` via Trees API |
| `marketplace` | Same as `github-plugin` (both are GitHub repos with marketplace.json) |
| `local` | Skip with message: "managed by specweave refresh-plugins" |
| `unknown` | Return null → caller falls back to registry |

## Technology Stack

- **Language**: TypeScript (ESM, `--moduleResolution nodenext`, all imports use `.js` extension)
- **Testing**: Vitest with `vi.hoisted()` for mock variables
- **Reused utilities**: `getDefaultBranch()`, `discoverSkills()` (github-tree.ts), `getPluginSource()`, `getPluginVersion()` (marketplace.ts), `getSkill()` (client.ts), `runTier1Scan()` (scanner)

**Architecture Decisions**:
- **New `src/updater/` directory**: Keeps fetching logic separate from the command. Mirrors `src/resolvers/` pattern.
- **Registry as fallback, not primary**: Preserves backward compatibility. Entries without a `source` field or with `unknown` type fall through to `getSkill()`.
- **No lockfile schema changes**: `source` field already exists on all entries. No migration needed.
- **`github-plugin` and `marketplace` share fetch logic**: Both are GitHub repos with `.claude-plugin/marketplace.json`. Single internal helper handles both.

## Implementation Phases

### Phase 1: Source Parser (pure, TDD)
- Write `source-resolver.test.ts` with all parsing test cases first
- Implement `source-resolver.ts`

### Phase 2: Source Fetcher (async, TDD)
- Write `source-fetcher.test.ts` mocking `fetch` and GitHub utilities
- Implement `source-fetcher.ts` with all fetch strategies

### Phase 3: Wire into update command
- Add new test cases to `update.test.ts` (mock `fetchFromSource`)
- Modify `update.ts` to import and use `parseSource()` + `fetchFromSource()`

## Testing Strategy

TDD for all three phases. Tests written before implementation.

- **source-resolver.test.ts**: ~10 unit tests, pure parsing logic (no mocks needed)
- **source-fetcher.test.ts**: ~8 tests mocking `fetch`, `getDefaultBranch`, `getSkill`, `getPluginSource`
- **update.test.ts** (extended): ~6 new integration tests mocking `fetchFromSource`

Coverage target: ≥90% for new modules.

## Technical Challenges

### Challenge 1: Plugin directory multi-file fetch
Updating `github-plugin` / `marketplace` sources requires fetching multiple SKILL.md files (one per sub-skill), not a single file. The Trees API response lists all paths; we filter by `plugins/{name}/skills/*/SKILL.md`.

**Solution**: Fetch all matching paths in parallel. Combined SHA = SHA of concatenated sorted contents. If any fetch fails, skip the entire plugin update and report an error.

**Risk**: Rate limiting for large plugins. Mitigated by `GITHUB_TOKEN` propagation.

### Challenge 2: `local:specweave` non-resolvable path
The `local:specweave` source is a symbolic name, not an absolute path. The actual SpecWeave installation directory is not stored in the lockfile.

**Solution**: For any `local:` source, print informational skip message and return null. No fetch attempted.

### Challenge 3: Backward compatibility
Lockfile entries from old installs may have `source: ""` or `source: "github:owner/repo"` without a `registry:` prefix.

**Solution**: Unknown/empty sources fall back to `getSkill(name)` with a dim warning. Existing behavior preserved.
