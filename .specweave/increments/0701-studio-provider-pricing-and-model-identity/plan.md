# Implementation Plan: Studio provider pricing and model identity

## Overview

Three surgical changes to vskill: add a filesystem probe for the active Claude Code model in the eval-server, extend the Anthropic provider model list with pricing data, and fix the LM Studio CTA wording. No new routes, no schema changes, no external deps.

## Architecture

### Components

| Component | File | Purpose |
|---|---|---|
| `resolveClaudeCodeModel()` | `vskill/src/eval-server/api-routes.ts` | New pure helper. Reads `~/.claude/settings.json`, extracts `model` field, returns `string \| null`. Catches ENOENT, permission errors, JSON parse errors. |
| `PROVIDER_MODELS["anthropic"]` | `vskill/src/eval-server/api-routes.ts` | Extended model entries with `pricing: { prompt, completion }` (USD per 1M tokens). |
| `/api/config` handler | `vskill/src/eval-server/api-routes.ts` | Propagates `resolvedModel` onto the `claude-cli` provider and `pricing` onto each Anthropic model. |
| `ServerConfigResponse` types | `vskill/src/eval-ui/src/hooks/useAgentCatalog.ts` | Extended to include `resolvedModel?: string \| null` and per-model `pricing?: { prompt, completion }`. |
| `toAgentEntry` | `useAgentCatalog.ts` | Copies server-supplied `pricing` and `resolvedModel` into `AgentEntry` / `ModelEntry`. |
| `ModelList.tsx` | `vskill/src/eval-ui/src/components/ModelList.tsx` | Renders resolvedModel as secondary line on Claude Code rows (when present). |
| `strings.ts` | `vskill/src/eval-ui/src/strings.ts` | `providers.lmStudio.startServiceCta` updated + new `startServiceTooltip`. |
| `LockedProviderRow.tsx` | `vskill/src/eval-ui/src/components/LockedProviderRow.tsx` | Wires the new tooltip to the locked LM Studio row via `title` attr. |

### Data flow

```
~/.claude/settings.json ──► resolveClaudeCodeModel() ──► /api/config response
                                                              │
                                                              ▼
                                         useAgentCatalog ──► AgentEntry.resolvedModel
                                                              │
                                                              ▼
                                                         ModelList row render
```

For pricing:

```
PROVIDER_MODELS["anthropic"] (with pricing)
        │
        ▼
/api/config response (per-model pricing)
        │
        ▼
useAgentCatalog.toAgentEntry ──► ModelEntry.pricing
        │
        ▼
ModelList.formatMetadata ──► "$3.00 / $15.00 per 1M tokens"
```

## Pricing Table (source of truth)

| Model ID | Input $/1M | Output $/1M | Notes |
|---|---|---|---|
| `claude-opus-4-7` | 15 | 75 | |
| `claude-opus-4-6` | 15 | 75 | |
| `claude-sonnet-4-6` | 3 | 15 | |
| `claude-haiku-4-5-20251001` | 1 | 5 | |

Source: https://www.anthropic.com/pricing (snapshot 2026-04-24). Re-verify annually.

## Error Handling

- `readFileSync` throws ENOENT → return `null` (fine, no settings file present).
- `readFileSync` throws EACCES → return `null` (log at debug only).
- `JSON.parse` throws → return `null`.
- Parsed JSON has no `model` field or value is not a string → return `null`.
- Parsed JSON has extra fields → ignored (we only read `model`).

## Testing Strategy

### Unit tests (Vitest)
- `resolveClaudeCodeModel()`: missing file → null, malformed JSON → null, valid file with `"model": "claude-opus-4-7[1m]"` → returns that exact string, valid file with `"model": "sonnet"` → returns "sonnet", file with non-string model → null.
- `PROVIDER_MODELS["anthropic"]` structure: every entry has numeric `pricing.prompt` and `pricing.completion` > 0.
- `/api/config` handler: returns `resolvedModel` on claude-cli provider; returns `pricing` on each anthropic model.
- `useAgentCatalog.toAgentEntry`: copies pricing + resolvedModel from server payload.
- `ModelList.formatMetadata`: produces "$3.00 / $15.00 per 1M tokens" for per-token with pricing.

### Component tests (React Testing Library)
- `ModelList` for Claude Code agent: when `resolvedModel` is set, renders sub-line; when null, renders nothing extra.
- `ModelList` for Anthropic agent: renders non-zero price.
- `strings.ts`: `providers.lmStudio.startServiceCta` equals "Start LM Studio server →"; tooltip exported.

### No integration tests needed
Pure pass-through of filesystem + static data; Vitest mocks cover all branches.

## ADR References

No new ADRs required. This extends existing architecture without decision points worthy of an ADR.

## Non-Functional

- **Performance**: +1 `readFileSync` call per `/api/config` (<1ms for a <10KB file). No new network calls.
- **Security**: Read-only access to a file the process already trusts. Only extracts `model` string.
- **Compatibility**: Backward-compatible — all new fields are optional. Older clients ignore them.
