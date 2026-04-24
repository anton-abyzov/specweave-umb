---
status: ready_for_review
owner: sw:architect
adrs:
  - 0711-01-snapshot-first-anthropic-catalog
  - 0711-02-provenance-storage-shape
  - 0711-03-env-override-precedence
  - 0711-04-staleness-gates
---

# Implementation Plan: Model provenance + Anthropic catalog refresh

## Overview

Replace 5 hardcoded Claude model identifiers (3 in `vskill` source, plus
two consumers in the UI/server pipeline) with a dated, runtime-aware
catalog. Promote `aiMeta` to record the *resolved concrete ID* alongside
the alias the user picked. Add CI + UI staleness gates so this never
silently rots again.

The architecture is pure-function-first: `resolveModelId(provider, input)`
is a single TS function with deterministic precedence (env > live > snapshot).
Every consumer of model identity goes through it.

## Architecture decisions

| ADR | Decision | Why |
|---|---|---|
| **0711-01** | Snapshot-first catalog with optional 24h live fetch | Offline-capable boot; no API key required; eval determinism |
| **0711-02** | Provenance in `aiMeta`; frontmatter stays alias | Audit trail without churning committed SKILL.md files |
| **0711-03** | Precedence `env > live > snapshot` | Day-one support for unreleased Anthropic minors |
| **0711-04** | 90d UI banner, 180d CI hard fail | Stop the silent rot mode `pricing.ts` is in today |

Full ADR text in `.specweave/docs/internal/architecture/adr/0711-*.md`.

## Component design

Five new modules + two extended ones. Pure functions live in `src/eval/`,
HTTP plumbing in `src/eval-server/`, UI hooks in `src/eval-ui/src/hooks/`.

```mermaid
flowchart LR
  subgraph eval["src/eval/ (pure)"]
    snap[anthropic-catalog.ts<br/>SNAPSHOT const]
    fetch[catalog-fetcher.ts<br/>24h cache + fallback]
    resolve[model-resolver.ts<br/>resolveModelId()]
    snap --> resolve
    fetch -.fresh cache.-> resolve
  end
  subgraph server["src/eval-server/"]
    config[/api/config<br/>api-routes.ts]
    skillgen[/api/skills/generate<br/>skill-create-routes.ts]
    config --> resolve
    skillgen --> resolve
  end
  subgraph ui["src/eval-ui/"]
    cat[useAgentCatalog.ts<br/>+snapshotDate, +resolvedConcreteId]
    create[useCreateSkill.ts<br/>aiMetaRef extended]
    config --> cat
    cat --> create
  end
  resolve --> prov[provenance-writer.ts<br/>writes aiMeta+resolvedModelId]
  create --> prov
  skillgen --> prov
```

### 1. `src/eval/anthropic-catalog.ts` (NEW)

Pinned snapshot fixture. Dated. Hand-curated. Refreshed by PR.

```ts
export interface ModelEntry {
  id: string;
  aliases: string[];
  displayName: string;
  pricing: { inputPerMillion: number; outputPerMillion: number };
  status: "current" | "legacy" | "deprecated";
}

export interface CatalogSnapshot {
  snapshotDate: string;            // ISO date
  source: string;                  // URL of source-of-truth at snapshot time
  models: ModelEntry[];
}

export const ANTHROPIC_CATALOG_SNAPSHOT: CatalogSnapshot = { ... };
```

Research agent produces the exact contents in parallel — this module
is the *shape*, not the data. Initial seed is whatever the research
agent returns at snapshot date 2026-04-24.

### 2. `src/eval/model-resolver.ts` (NEW)

Pure function with deterministic precedence (ADR 0711-03):

```ts
export interface ResolvedModel {
  id: string;                      // concrete: "claude-sonnet-4-6"
  alias: string | null;            // input as supplied: "sonnet" or null
  displayName: string;
  pricing: { inputPerMillion: number; outputPerMillion: number } | null;
  snapshotDate: string;
  source: "env-override" | "live" | "snapshot";
}

export function resolveModelId(
  provider: "anthropic" | "claude-cli",
  input: string,
): ResolvedModel;
```

Replaces inline lookups in `llm.ts:158` (`normalizeAnthropicModel`),
`pricing.ts:92` (`getProviderPricing`), and `api-routes.ts:643`
(`PROVIDER_MODELS` static). All three rewire to call this.

### 3. `src/eval/catalog-fetcher.ts` (NEW, server-only)

```ts
export async function getAnthropicCatalog(): Promise<CatalogSnapshot>;
```

Reads `~/.vskill/cache/anthropic-catalog.json`. If <24h old and valid,
returns it. Otherwise calls `https://api.anthropic.com/v1/models` with
`ANTHROPIC_API_KEY` (when present), normalizes the response into
`CatalogSnapshot` shape, writes the cache, returns it. On any
failure — no key, network error, malformed response — returns
`ANTHROPIC_CATALOG_SNAPSHOT`. Never throws.

### 4. `src/eval-ui/src/hooks/useResolvedModel.ts` (NEW)

Thin React hook that wraps the `/api/config` response shape:

```ts
export function useResolvedModel(provider: string, alias: string): {
  resolved: ResolvedModel | null;
  isStale: boolean;     // snapshotDate > 90 days
};
```

The Studio picker uses this to render the staleness banner (ADR
0711-04). `useAgentCatalog.ts` is extended (NOT replaced) to forward
`snapshotDate` + `resolvedConcreteId` from `/api/config`.

### 5. `src/eval/provenance-writer.ts` (NEW)

Centralizes the `aiMeta` extension so both `save-draft` and
`createSkill` paths write the same shape. Pure function:
`(meta, resolved) → extendedMeta`. Today's call sites at
`skill-create-routes.ts:1218-1221` and `:1234-1240` rewire through
this helper.

### 6. Extended: `src/eval-ui/src/hooks/useCreateSkill.ts`

`aiMetaRef` shape changes from `{prompt, provider, model, reasoning}`
to `{prompt, provider, model, reasoning, resolvedModelId, snapshotDate, resolverSource}`.
Backward-compatible: readers tolerate `undefined` on the new fields
for pre-0711 drafts.

### 7. Extended: `src/eval-ui/src/hooks/useAgentCatalog.ts`

`ModelEntry` (line 16) gains `snapshotDate?: string` and
`resolvedConcreteId?: string`. `ServerConfigResponse.providers[].models[]`
(line 61-66) gains the same fields. Forwarding logic at line 154-160
copies them into the canonical `ModelEntry`.

## API contract changes

### `GET /api/config` response shape

Adds two fields per anthropic-family model:

```diff
 {
   "id": "claude-sonnet-4-6",
   "label": "Claude Sonnet 4.6 (API)",
-  "pricing": { "prompt": 3, "completion": 15 }
+  "pricing": { "prompt": 3, "completion": 15 },
+  "snapshotDate": "2026-04-24",
+  "source": "snapshot"
 }
```

And per-provider:

```diff
 {
   "id": "anthropic",
   "label": "Anthropic API",
+  "catalogSnapshotDate": "2026-04-24",
   "models": [...]
 }
```

OpenRouter / OpenAI / Google providers are **not** modified — that is
the explicit non-goal below. (0710 owns OpenRouter; later increments
own OpenAI / Google.)

### `POST /api/skills/generate` response

The SSE `done`/`complete` event payload gains a `resolvedModel` block:

```diff
 {
   "name": "my-skill",
   "description": "...",
-  "model": "sonnet",
+  "model": "sonnet",
+  "resolvedModel": {
+    "id": "claude-sonnet-4-6",
+    "snapshotDate": "2026-04-24",
+    "source": "snapshot"
+  },
   ...
 }
```

`useCreateSkill.handleGenerate` (line 380-390) reads it into the
extended `aiMetaRef`.

## Testing architecture

| Test file | Covers | Type |
|---|---|---|
| `src/eval/__tests__/model-resolver.test.ts` | `resolveModelId` precedence matrix (env / live / snapshot / unknown alias / unknown ID) | unit (vitest) |
| `src/eval/__tests__/anthropic-catalog.test.ts` | Snapshot shape: every entry has pricing + status; `snapshotDate` is ISO; aliases unique | snapshot |
| `src/eval/__tests__/catalog-fetcher.test.ts` | 24h cache hit, cache miss → fetch, fetch error → snapshot fallback, no API key → snapshot fallback | unit (vitest, fs+fetch mocked) |
| `src/eval/__tests__/catalog-staleness.test.ts` | Asserts `snapshotDate` is <180 days old AND every `pricing.ts` row is <180 days old. **CI hard fail (ADR 0711-04).** | unit (date-only, deterministic) |
| `src/eval-server/__tests__/api-routes.config.test.ts` | `/api/config` propagates `snapshotDate` and `resolvedConcreteId` | integration |
| `src/eval-server/__tests__/skill-create-routes.aiMeta.test.ts` | `aiMeta` written to `draft.json` and history includes `resolvedModelId`, `snapshotDate`, `resolverSource` | integration |
| `src/eval-ui/src/hooks/__tests__/useCreateSkill.provenance.test.ts` | `aiMetaRef` includes resolved fields after generate; survives round-trip through `saveDraft` | unit (vitest, fetch mocked) |
| Manual / preview | Pick Opus → `/api/config` returns provenance → `.specweave/aiMeta.json` (history entry) contains resolved ID | E2E manual |

Coverage target: 90% on the four new `src/eval/*` modules. ACs map
1:1 onto the rows above (PM will own that mapping in `tasks.md`).

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Snapshot research lands wrong pricing** (e.g. Opus 4.7 listed at $5/$25 in `pricing.ts:19-20` looks low — Anthropic public pricing is $15/$75 per 0701 ADR) | High | Eval cost reports off by 3× | Research agent returns *with citations*; snapshot test asserts pricing came from the cited source URL; reviewer cross-checks against the 0701 ADR before merge |
| **Cache file lives in `~/.vskill/` which CI may not have writable** | Medium | Catalog-fetcher errors silently, falls back to snapshot — but the test for fetcher needs to assert this gracefully | `catalog-fetcher.ts` swallows `EACCES`/`ENOENT` on cache write. Test covers the read-only-FS case |
| **Merge conflict with 0710** (OpenRouter pricing units hotfix) — both touch the `pricing` field on `ModelEntry` | Medium | Wasted rebase | Scope is anthropic-only. We do not modify OpenRouter rows in `PRICING`/`PROVIDER_MODELS`/`useAgentCatalog`. Coordinate with 0710 owner before landing |

## Non-goals

- **OpenRouter / OpenAI / Google catalog refresh.** This increment is
  Anthropic-only. The pattern (snapshot + resolver + provenance) is
  designed to extend to other providers in a later increment, but
  the code for those providers stays as-is.
- **Pinning frontmatter to concrete IDs.** ADR 0711-02 explicitly
  rejects this. Frontmatter `model:` stays an alias.
- **Replacing `pricing.ts` wholesale.** We replace only the anthropic
  block; OpenAI / Google rows are untouched.
- **Live `/v1/models` at boot.** Snapshot-first per ADR 0711-01;
  the live fetcher is opportunistic, not on the critical path.
- **Surfacing provenance in committed SKILL.md.** It lives in
  `evals/history/*.json` and `draft.json` only.

## Phase ordering for `/sw:do`

1. **Foundation** — `anthropic-catalog.ts` (snapshot) + `model-resolver.ts`
   (pure function) + their tests. No consumers wired yet.
2. **Server wiring** — `api-routes.ts` `PROVIDER_MODELS`, `pricing.ts`
   `PRICING` anthropic block, and `llm.ts` `ANTHROPIC_NORMALIZE` all
   rewire to `resolveModelId`. `/api/config` adds the new fields.
3. **Provenance writer** — `provenance-writer.ts` + `aiMeta` extension
   in `skill-create-routes.ts`.
4. **UI** — `useAgentCatalog`, `useResolvedModel`, `useCreateSkill`
   provenance plumbing + Studio picker banner.
5. **Gates** — `catalog-fetcher.ts` (24h cache) + `catalog-staleness.test.ts`
   (CI hard fail).
