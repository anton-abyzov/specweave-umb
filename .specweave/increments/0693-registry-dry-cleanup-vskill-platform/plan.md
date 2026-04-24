# 0693 Plan — Registry DRY

## Architecture Decision

**Use a generated `agents.json` artifact** rather than runtime cross-repo imports.

Why: `crawl-worker/**` is plain JS (no TS toolchain) and lives inside vskill-platform, a separate repo from vskill. Direct TS imports would require either bundling vskill into vskill-platform or adding a TS build step to the worker. JSON is the cheapest, most portable interchange.

## Source of Truth

**Canonical**: `vskill/src/agents/agents-registry.ts`
- Existing: `AGENTS_REGISTRY: AgentDefinition[]` (49 agents, each with `prefixes: string[]`)
- New export: `NON_AGENT_CONFIG_DIRS: readonly string[]` — the 8 dirs currently in skill-scanner's `EXTRA_CONFIG_DIRS`

## Components

### 1. `vskill/scripts/generate-agents-json.ts` (NEW)
Reads `AGENTS_REGISTRY` + `NON_AGENT_CONFIG_DIRS`, writes:
```json
{
  "version": 1,
  "generatedAt": "<ISO>",
  "agentPrefixes": ["claude", "cursor", "copilot", ...],
  "nonAgentConfigDirs": [".specweave", ".vscode", ...]
}
```
Output path: `vskill/agents.json` (root) for in-repo consumers and copy source.

### 2. vskill build wiring
- Add to `vskill/package.json`: `"generate:agents-json": "tsx scripts/generate-agents-json.ts"`
- Hook into existing build: `prebuild` → calls generate script

### 3. vskill-platform prebuild copy
- Add `vskill-platform/scripts/sync-agents-json.cjs` that copies `../vskill/agents.json` → `vskill-platform/crawl-worker/agents.json` and `vskill-platform/src/lib/agents.json`
- Wire into `vskill-platform/package.json` as `prebuild`
- Loud failure with actionable message if source missing

### 4. Consumers

| Consumer | Old | New |
|---|---|---|
| `vskill/src/eval/skill-scanner.ts` | `EXTRA_CONFIG_DIRS` (local const) | `import { NON_AGENT_CONFIG_DIRS } from '../agents/agents-registry'` |
| `vskill-platform/src/lib/skill-path-validation.ts` | hardcoded `AGENT_CONFIG_PREFIXES` (TS) | `import agentsJson from './agents.json'` (TS resolveJsonModule) |
| `vskill-platform/crawl-worker/sources/queue-processor.js` | hardcoded array | `require('../agents.json')` (CJS read) |
| `vskill-platform/crawl-worker/lib/repo-files.js` | hardcoded array | `require('../agents.json')` |

## Risks

- **Stale agents.json in CI**: prebuild step must be deterministic — fail loudly if file missing
- **Coordination with parallel agent**: `impl-cli-coverage` may add agents to `AGENTS_REGISTRY`. We add `NON_AGENT_CONFIG_DIRS` at a clearly separated section near the bottom of the file. No structural changes to the array itself.

## Test Strategy

- Unit tests next to source: `agents-registry.test.ts` (extend), `skill-scanner.test.ts` (extend)
- Integration test: add a temp agent → run generate script → assert all 4 consumers see the new prefix
- Smoke: `npm run build` in both repos, no errors
