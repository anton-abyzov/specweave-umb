---
increment: 0682-studio-agent-model-picker
title: vSkill Studio — Unified Agent + Model Picker (Technical & Design Plan)
type: plan
status: draft
created: 2026-04-23
architect: sw:architect
design_authority: frontend-design (primary) + sw:architect (structural)
---

# Plan: vSkill Studio — Unified Agent + Model Picker

> **Scope anchor.** Target = the Vite + React SPA at `repositories/anton-abyzov/vskill/src/eval-ui/`, served by the eval-server at `src/eval-server/`. Out of scope: `vskill eval run` headless CLI, `vskill-platform` marketing site, any OAuth flow.

> **Architecture evolution note (2026-04-25):** Originally planned `SettingsContext.tsx + keyStore.ts` were superseded during T-006 implementation by a single `hooks/useCredentialStorage.ts` (no context, file-backed at `~/.vskill/keys.env` resolved via `GET /api/settings/storage-path`). Same surface area; simpler design. Tier model collapsed from `"browser" | "keychain"` to one file-based store. All AC-US4 behavioural acceptance criteria still met.

---

## 0. Problem shape & forces

### 0.1 The control in question is brand-defining, not a dropdown

The model selector is opened dozens of times per session by every Studio user. It is the primary decision surface, the first place eyes land when the user wants to run or compare evals, and one of the few surfaces where Studio can demonstrate — or fail to demonstrate — that it was designed with taste. Treating it as a generic `<select>` with labelled `<option>` elements (current state) is structural malpractice given how central it is.

We are rebuilding it as a **command surface** in the Linear / Raycast lineage: two-pane, keyboard-first, motion-restrained, tabular-numeric in data, calm in copy.

### 0.2 Three forcing functions colliding

| Forcing function | Consequence |
|---|---|
| **Anthropic ToS (Apr 4 2026)** — OAuth consumption of Max/Pro quota from third-party tools is banned; only Claude Code CLI / claude.ai / Claude Desktop are sanctioned consumers | Reframe "Claude (Max/Pro subscription)" as "Use current Claude Code session"; add compliance test + bundle grep gate |
| **Console relocation** — `console.anthropic.com` → `platform.claude.com` | Update all docs + inline links |
| **UX debt** — greyed-out rows, no settings surface, no searchable OpenRouter catalog, agents conflated with models | Rebuild the picker from scratch around an agent-then-model hierarchy |

These converge cleanly: a single reform pass fixes all three.

### 0.3 Claude-default heuristic — why it matters

The typical Studio user is a Claude Code native. The current picker forces them to pick a model from a flat list; the new default rule (`.claude/` present + `claude` binary available → Claude Code preselected, Sonnet model) removes the first click for that majority persona. Fallback order ensures users without Claude still get a sensible default without nagging.

---

## 1. Architectural decisions (ADRs)

### ADR-0682-01: Catalog source-of-truth per agent

**Status**: Accepted · **Date**: 2026-04-23

**Context**: The picker needs to populate a model list for each of ten agents. Each has a different canonical catalog source:

| Agent | Catalog source | Freshness | Keyed? |
|---|---|---|---|
| Claude Code | Hardcoded `["sonnet", "opus", "haiku"]` — these are CLI aliases, not full model ids | Stable for months | No |
| Anthropic API | Hardcoded curated list of current Claude models (Sonnet 4.7 / Opus 4.7 / Haiku 4.5 etc.) — updated when we bump model versions | Changes quarterly | Yes |
| OpenRouter | Live `https://openrouter.ai/api/v1/models` — 300+ entries, prices update weekly | Cache 10 min | Yes |
| Cursor / Codex CLI / Gemini CLI / Copilot / Zed | Hardcoded short list per CLI's known model flags | Stable | No (use local creds) |
| Ollama | Live `http://<host>/api/tags` — returns installed models | Real-time (per open) | No |
| LM Studio | Live `http://<host>/v1/models` | Real-time | No |

**Decision**: Introduce a **single `useAgentCatalog()` hook** in `src/eval-ui/src/hooks/useAgentCatalog.ts` that merges the above into a uniform `AgentCatalog` shape:

```ts
type AgentCatalog = {
  agents: AgentEntry[];
};

type AgentEntry = {
  id: string;                             // matches agents-registry.ts
  displayName: string;
  icon: string;                           // SVG or emoji-free identifier
  wrapperFolder: string | null;           // ".claude", ".cursor", etc.
  wrapperFolderPresent: boolean;          // scan result
  binaryAvailable: boolean;               // `which <binary>` result
  endpointReachable: boolean | null;      // only for Ollama / LM Studio
  ctaType: "api-key" | "cli-install" | "start-service" | null;
  models: ModelEntry[];
  catalogAgeMs?: number;                  // for cached catalogs (OpenRouter)
};

type ModelEntry = {
  id: string;                             // "claude-sonnet-4-6-20260201" etc.
  displayName: string;                    // "Claude Sonnet 4.6"
  contextWindow?: number;                 // 1_000_000
  pricing?: { prompt: number; completion: number };  // $/1M tokens
  billingMode: "per-token" | "subscription" | "free";
};
```

The hook internally:
- Calls `GET /api/config` for server-computed agent availability + hardcoded catalogs.
- Calls `GET /api/openrouter/models` lazily (only when OpenRouter row becomes active or is focused).
- Polls Ollama / LM Studio every 30s while their row is active.
- Deduplicates model ids across agents (some Claude models appear in both Anthropic API and OpenRouter — we keep both entries but tag them with `agentId` for provenance).

**Consequences:**
- One hook, one contract, one cache per source. Components never fetch directly.
- Server-side cache for OpenRouter (10 min) + client stale-while-revalidate (5 min) absorbs the API latency.
- Catalog age surfaced via `X-Vskill-Catalog-Age` header → optional toast if >10 min old.

**Rejected alternatives:**
- Per-component fetches → duplicated network, cache-coherence nightmare.
- Everything server-side → forces a round-trip for agent switches; client-side cache is faster.
- Fully client-side → loses server's single cached OpenRouter fetch shared across browser tabs.

---

### ADR-0682-02: Credential storage tier

**Status**: Accepted · **Date**: 2026-04-23

**Context**: API keys (Anthropic, OpenRouter) must live on-device, never in the repo, never in a synced location, with minimum bar = plaintext-in-localStorage-with-warning, and maximum bar = OS secret store.

**Decision**: Two-tier model.

- **Tier A (baseline, all platforms)**: **eval-server in-memory map**, keyed by `hash(projectRoot) + ":" + provider`, populated by the browser on login via `POST /api/settings/keys`. The browser mirrors to `localStorage` under the same namespaced key so subsequent page loads don't require re-entry. A prominent banner in the Settings modal states the storage contract.
- **Tier B (Darwin opt-in)**: **macOS Keychain**, accessed via `spawn("security", ["add-generic-password", "-s", "vskill-<provider>", "-a", projectHash, "-w", key, "-U"])`. Non-Darwin systems don't show the tier toggle.

**Rejected:**
- **Plaintext `.env.local` or `.vskill/studio.json`** — too easy to accidentally commit; no meaningful security over Tier A.
- **`keytar` / `node-keytar`** — native module, CI/build complexity, not justified at this increment scope. Re-evaluate in a future increment.
- **Shared `~/.vskill/keys.json` with 0600 perms** — cross-project leakage; no per-project scoping.

**Consequences:**
- Tier A works everywhere with zero install.
- Darwin users who value OS-level protection opt into Tier B via the Settings modal toggle.
- `readKey(provider, projectHash)` abstraction in `settings-store.ts` routes to the active tier.
- Tier switch wipes the old tier's entry and re-saves into the new tier.

---

### ADR-0682-03: Claude Code session delegation over OAuth scraping

**Status**: Accepted · **Date**: 2026-04-23

**Context**: Post April 4 2026 ToS, any path that reads `~/.claude/credentials*|auth*|token*` to obtain Anthropic session auth is prohibited.

**Decision**: The Claude Code provider delegates via `child_process.spawn("claude", ["-p", "--model", model])`, identical to the current `createClaudeCliClient()` implementation. It:
1. Pipes user prompt to child stdin.
2. Reads response from child stdout (with timeout).
3. Strips all `CLAUDE*` env vars from the inherited env (prevents nested-session heuristics).
4. Never touches `~/.claude/` files.

Two enforcement gates are added:

- **Unit test** (`claude-cli-compliance.test.ts`) mocks `fs.*` read APIs, runs a full generate, asserts zero calls match `~/.claude/credentials*|auth*|token*`.
- **Bundle grep** runs on `npm run build` output: `grep -r '"\.claude/credentials"\|"\.claude/auth"\|"\.claude/token"' dist/ → must return zero`.

**Consequences:**
- Users must install `@anthropic-ai/claude-code` globally to use this provider.
- Error path for missing binary says "Install Claude Code", never suggests an API-key substitute.
- The provider is self-documenting: the caption below its label reads *"Delegates to the `claude` CLI — your existing Claude Code session handles quota."*

**Rejected:**
- **OAuth scrape** → ToS violation.
- **Embedded OAuth flow** → same violation, plus credential-handling complexity.
- **Mandatory API key** → hostile to the primary persona P1.

---

### ADR-0682-04: Agent-THEN-model two-pane hierarchy

**Status**: Accepted · **Date**: 2026-04-23

**Context**: The current flat dropdown conflates "which agent am I using?" with "which model?". These are different mental models:
- Agent = the *environment* consuming the model (Claude Code session vs API call vs Cursor IDE vs Codex CLI). Affects auth model, billing mode, transport.
- Model = the *weights* answering the prompt (Sonnet 4.6 vs Opus 4.7 vs llama3.1:8b). Affects capability, cost, latency.

Evidence from analogous tools:
- **Cursor**, **Raycast**, **Linear**, **Warp** — all use two-pane or left-rail-grouped choosers for nested choices.
- **VS Code command palette** uses a flat list because the space is ~20 items, not 300+.

**Decision**: Two-pane popover.

- **Left pane (240px)**: agent list, 36px rows, shows wrapper-folder presence dot + availability glyph + active badge.
- **Right pane (360px)**: models of the *focused* agent (not necessarily the active agent), 44px two-line rows with name + metadata.
- **Footer (32px)**: Settings button, keyboard hints.
- **Keyboard model**: `↑/↓` within current pane; `→` moves focus from agent→model pane; `←` returns; `Enter` selects the focused model and closes; `Esc` cancels; `Cmd+K` toggles open/close; `Tab` / `Shift+Tab` cycles within the popover (focus trap).

**Consequences:**
- Users understand which *kind* of consumer they've chosen before committing to a specific model.
- OpenRouter's 300-entry model pane gets its own search scope — doesn't flood a single flat list.
- Agent rows can carry distinct CTAs ("Install Claude Code" vs "Add API key") without polluting model rows.

**Rejected:**
- **Flat list with provider headers** (status quo) — conflates concerns; OpenRouter dominates visually.
- **Command-palette (single flat searchable list)** — search works, but agent context is lost and CTAs have nowhere natural to live.
- **Tabs** — ugly at 10 tabs; nested under the agent rail feels generic.

---

## 2. Frontend-design ground rules

Applied to every new surface in this increment.

### 2.1 Typography

- **Inter Tight Variable** — all UI rows (agent names, model names, buttons, labels). 400 body / 500 emphasis / 600 headers.
- **JetBrains Mono Variable** — model metadata (context window, pricing) with `font-variant-numeric: tabular-nums`; all keyboard hints; environment variable names in docs.
- No serif anywhere in the picker (reserved for detail-card titles per 0674's rule).

### 2.2 Density

- Agent row: 36px, single line, 12px horizontal padding.
- Model row: 44px, two lines (name + metadata), 12px horizontal padding, 4px vertical gap between lines.
- Footer: 32px. Popover total height max: 440px (10 model rows before virtualisation).
- Panes are **not** equal-width: agent 240px, model 360px. Non-negotiable ratio for scan flow.

### 2.3 Colour (warm-neutral tokens from 0674)

- **At rest**: row background `transparent`; text `var(--text-primary)` for name, `var(--text-muted)` for metadata.
- **Hover**: background `var(--surface-muted)`; no border change.
- **Focus/selected**: background `var(--accent-wash)` + 1px left border in `var(--accent)`; "Currently active" 10px uppercase kicker in `var(--accent-ink)` on `var(--accent-wash)`.
- **Locked row**: same background as at-rest; lock glyph at `var(--text-muted)`; CTA text `var(--accent)`; **no** global opacity reduction and **no** `cursor: not-allowed`.
- **Dividers**: 1px `var(--border-default)` between pane edges and footer.

### 2.4 Motion

- Popover open: `opacity 0→1` + `translateY(2px→0)` over **120ms** with `cubic-bezier(0.2, 0, 0, 1)` easing.
- Popover close: same values reversed over **80ms**.
- Row hover / focus: no transition on background (instant feedback matters more than polish here).
- Just-unlocked flash: `var(--accent-wash)` fades in and out over 800ms.
- **All motion bypassed under `prefers-reduced-motion: reduce`** — popover just appears/disappears; flash skipped.

### 2.5 Copy voice

- Agent labels: exact canonical name (Claude Code, Cursor, Codex CLI, Gemini CLI, GitHub Copilot, Zed, Anthropic API, OpenRouter, Ollama, LM Studio).
- Model row: `"<Display Name>"` line 1; `"<context> ctx · $<prompt> / $<completion> per 1M tokens"` line 2 for priced; `"<context> ctx · subscription"` for CLI-delegated; `"local · <size> · free"` for Ollama/LM Studio.
- CTA text: `"Add API key →"` (API providers), `"Install {Tool} →"` (CLI-tooled agents), `"Start service →"` (Ollama/LM Studio).
- Forbidden: `"Max/Pro"`, `"subscription"` (in picker/settings/StatusBar surfaces), celebration emoji, trailing `!!`, `"Oops"`, `"Awesome"`, `"Coming soon"`.
- Voice-lint grep extends to `src/eval-ui/src/` and `src/eval-server/`.

### 2.6 Anti-patterns rejected (explicitly)

| Anti-pattern | Why rejected |
|---|---|
| Grey-out locked rows with `opacity: 0.4` | Signals "disabled forever" rather than "one click away from unlocked"; also tanks contrast below AA |
| "Coming soon" stubs for unimplemented providers | Clutter; the right move is to omit or to ship |
| Separate modals for API key / settings / picker | Fragments the mental model; one Settings modal, reachable from picker footer |
| Tabs inside the popover | Generic; two-pane rail expresses hierarchy more directly |
| Floating action buttons (FABs) for "Add key" | Doesn't fit the calm/developer-first aesthetic |
| Tooltip-only price display | Price is a first-class selection criterion for OpenRouter users; must live in the row |
| Icons that depend on emoji | Emoji ≠ design system; inline SVG only |
| Provider labels that leak implementation detail (e.g., "Claude (via claude-code CLI)") | Makes the user think about the adapter; the caption handles delegation framing |

---

## 3. Component design

### 3.1 File layout delta

```
repositories/anton-abyzov/vskill/
├── src/
│   ├── eval/
│   │   ├── env.ts                                       # NEW — resolveOllamaBaseUrl() + warnOnce()
│   │   ├── llm.ts                                       # MOD — doc-block reframe, Ollama swap to helper
│   │   └── __tests__/
│   │       ├── env.test.ts                              # NEW
│   │       ├── llm.test.ts                              # MOD — extend Ollama tests
│   │       └── claude-cli-compliance.test.ts            # NEW — fs mock compliance gate
│   ├── eval-server/
│   │   ├── api-routes.ts                                # MOD — label rename, /api/settings/keys, /api/detect/agents, 10-min OpenRouter cache
│   │   ├── settings-store.ts                            # NEW — tiered keychain/localStorage-proxy
│   │   └── __tests__/
│   │       ├── api-routes.config.test.ts                # NEW — asserts label + no "Max/Pro"
│   │       ├── api-routes.keys.test.ts                  # NEW — settings key endpoints
│   │       ├── api-routes.openrouter-cache.test.ts      # NEW — cache behaviour
│   │       └── settings-store.test.ts                   # NEW
│   └── eval-ui/src/
│       ├── components/
│       │   ├── AgentModelPicker.tsx                     # NEW — two-pane popover shell
│       │   ├── AgentPane.tsx                            # NEW — left pane
│       │   ├── ModelPane.tsx                            # NEW — right pane (with search + virtualisation)
│       │   ├── LockedCta.tsx                            # NEW — inline CTA replacing grey-out
│       │   ├── SettingsModal.tsx                        # NEW
│       │   ├── ProvidersSegment.tsx                     # NEW — StatusBar addon
│       │   ├── ModelSelector.tsx                        # DELETE — call sites migrate to AgentModelPicker
│       │   ├── StatusBar.tsx                            # MOD — insert ProvidersSegment
│       │   └── __tests__/ (each component gets a test)
│       ├── hooks/
│       │   ├── useAgentCatalog.ts                       # NEW
│       │   ├── useVirtualList.ts                        # NEW — 30 lines, no lib dep
│       │   └── __tests__/useAgentCatalog.test.ts        # NEW
│       ├── settings/
│       │   ├── SettingsContext.tsx                      # NEW
│       │   └── keyStore.ts                              # NEW — client fetch wrapper
│       └── strings.ts                                   # MOD — agents, providers, picker, settings
├── e2e/
│   └── agent-model-picker.spec.ts                       # NEW
├── docs/
│   └── ARCHITECTURE.md                                  # MOD — new §5 env-vars table
└── README.md                                            # MOD — compliance note, OLLAMA_HOST docs, platform.claude.com
```

### 3.2 Data flow — picker render

```
Component mount → useAgentCatalog() →
  GET /api/config            → { providers: [...], detection: { wrapperFolders: {...}, binaries: {...} } }
  GET /api/openrouter/models → cached 10 min server-side; SWR 5 min client  (lazy on OpenRouter focus)
  polling Ollama/LM Studio   → every 30s while row is active
→ merge into AgentCatalog →
→ AgentModelPicker renders → AgentPane + ModelPane + Footer
```

### 3.3 Data flow — key save

```
User types key → SettingsModal local state → validate (empty + prefix) →
  Save → POST /api/settings/keys { provider, key, tier } →
    settings-store.saveKey(provider, key, tier, projectHash) →
      tier === "keychain" on Darwin: spawn("security", ["add-generic-password", ...]) (key via -w, never logged)
      tier === "browser": eval-server in-memory map + browser localStorage mirror
    → 200 { ok, updatedAt, available, tier } →
  SettingsContext invalidates useAgentCatalog cache →
    next render: provider row renders as live (not locked); 800ms flash
```

### 3.4 Data flow — agent-switch persistence

```
User Enter on model row → AgentModelPicker dispatches select({agent, model}) →
  POST /api/config { provider, model } (existing endpoint)
  writeStudioJson({ activeAgent, activeModel, updatedAt: new Date().toISOString() }) → atomic .tmp-then-rename
  dropdown closes
```

### 3.5 Persistence format

`.vskill/studio.json`:

```json
{
  "activeAgent": "claude-code",
  "activeModel": "sonnet",
  "updatedAt": "2026-04-23T15:30:00.000Z"
}
```

Written atomically. Missing file → defaults computed per AC-US1-01/02. Malformed file → log warning, ignore, rewrite on first selection.

---

## 4. API surface

| Method | Path | Body / Params | Response | Notes |
|---|---|---|---|---|
| `GET` | `/api/config` (existing) | — | `{ provider, model, providers: AgentInfo[], detection: { wrapperFolders: Record<string, bool>, binaries: Record<string, bool> } }` | **MOD**: add `detection` block; rename claude-cli label; include OpenRouter hardcoded-fallback list when no key |
| `GET` | `/api/detect/agents` (new/optional) | — | `{ wrapperFolders: {...}, binaries: {...}, endpoints: {...} }` | Optional — `/api/config` may embed this directly; decide during impl whether a separate endpoint is warranted for polling |
| `GET` | `/api/openrouter/models` (existing) | — | `{ models: [...] }` + `X-Vskill-Catalog-Age: <seconds>` | **MOD**: 10-min in-memory cache; stale served if fresh fetch fails |
| `GET` | `/api/settings/keys` | — | `{ anthropic: { stored, updatedAt?, tier }, openrouter: { ... } }` | Never returns the key value |
| `POST` | `/api/settings/keys` | `{ provider, key, tier? }` | `{ ok, updatedAt, available, tier }` | Validates non-empty; redacts on log |
| `DELETE` | `/api/settings/keys/:provider` | — | `{ ok }` | Wipes from current tier |

All endpoints: JSON body only, no query-string keys, localhost-bound (existing), redact keys to last 4 chars in any log/error.

---

## 5. Testing strategy

### 5.1 Unit tests (Vitest)

- `env.test.ts` — `resolveOllamaBaseUrl` precedence + scheme prepend + warn-once.
- `claude-cli-compliance.test.ts` (NFR-006 gate) — fs mock + fake binary + path assertions + dist bundle grep.
- `settings-store.test.ts` — tier routing, Darwin/non-Darwin branches, redaction unit on mocked logger.
- `api-routes.keys.test.ts` — POST/GET/DELETE happy paths + error paths (empty, prefix warn, query-string rejection).
- `api-routes.openrouter-cache.test.ts` — cache hit/miss, stale-serve on fetch failure, `X-Vskill-Catalog-Age` header.
- `api-routes.config.test.ts` — label rename, no "Max/Pro" in response, detection block present.
- `useAgentCatalog.test.ts` — merges server config + OpenRouter fetch + Ollama poll; honors 30s detection cache; dedups model ids.
- `AgentPane.test.tsx`, `ModelPane.test.tsx`, `AgentModelPicker.test.tsx` — keyboard nav (↑↓→←EnterEscCmdK), focus trap, `aria-selected`, active badge, search filter, virtualisation kicks in at 80 rows.
- `SettingsModal.test.tsx` — focus trap, masked input, paste helper, prefix warning, empty-guard, tier toggle Darwin-only, save/remove + toast emission.
- `LockedCta.test.tsx` — CTA variants (api-key / cli-install / start-service), click fires correct callback, keyboard Enter works.
- `ProvidersSegment.test.tsx` — glyph count + order, tooltip content, responsive collapse <640px, click routes to Settings vs help popover.

### 5.2 Integration tests

- `/api/settings/keys` round-trip → `/api/config` flips `available: true` within 500ms.
- OpenRouter endpoint serves stale cache when upstream 5xx's, with `X-Vskill-Catalog-Age` header.
- `.vskill/studio.json` atomic write survives a simulated mid-write kill (temp file cleanup).

### 5.3 E2E (Playwright)

- `agent-model-picker.spec.ts`:
  - Fresh project with `.claude/skills/` → boot → picker shows Claude Code as default, Sonnet model, no nag toast.
  - `Cmd+K` opens picker → `↓↓↓` to OpenRouter → inline CTA row shown (no grey-out) → Enter on CTA → Settings modal opens focused on OpenRouter tab → paste fake `sk-or-test-1234` → Save → modal closes → picker re-renders with OpenRouter live + 800ms flash → search for "qwen" → list filters → Enter on first result → popover closes → config updated.
  - Repeat flow with keyboard only (no mouse): Tab + Enter / Cmd+K only.
  - StatusBar provider glyphs: initial state shows locks for Anthropic/OpenRouter; after key save, flip to unlock; hover tooltip content verified.

### 5.4 Coverage target

90% on new modules (`useAgentCatalog.ts`, `AgentPane.tsx`, `ModelPane.tsx`, `AgentModelPicker.tsx`, `SettingsModal.tsx`, `settings-store.ts`, `env.ts`, `LockedCta.tsx`, `ProvidersSegment.tsx`).

### 5.5 Closure gates (all must pass)

1. Compliance test green.
2. Bundle-grep returns zero hits for `.claude/credentials|.claude/auth|.claude/token`.
3. Voice-lint grep returns zero hits for `Max/Pro` or `subscription` in picker/settings/StatusBar surfaces.
4. Playwright E2E green (including keyboard-only run).
5. Coverage ≥90% on new modules.
6. README + ARCHITECTURE.md updates present (grep CI).

---

## 6. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OpenRouter catalog shape changes | Low | Medium | Parse defensively; unknown fields ignored; tests against a frozen fixture |
| `security` CLI prompts repeatedly on macOS | Low | Medium | Use consistent `-s` + `-a` pair; `-U` flag avoids duplicate-entry prompts |
| Users with `.claude/` but no `claude` binary confused why Claude isn't default | Medium | Low | AC-US1-03 row shows "Install Claude Code →" CTA making the cause legible |
| Picker trigger conflict with Cmd+K in other components | Low | Medium | Only bind Cmd+K when no input element owns focus (event.target check) |
| Virtualisation jitter on scroll in some browsers | Low | Low | Fixed row heights + `will-change: transform` on list container |
| Future provider added without updating CTA type | Medium | Low | `AgentEntry.ctaType` is required; TypeScript catches at build |
| Ollama polling burns battery on idle tab | Low | Low | Pause polling when `document.visibilityState === "hidden"` |

---

## 7. Rollout

- **Phase A (T-001 → T-003)** — Server reframe + env helper + compliance test. Pure refactor + test additions; no UI impact.
- **Phase B (T-004 → T-006)** — Settings modal + key endpoints + tiered storage. New surface, reachable but not yet consumed by picker.
- **Phase C (T-007 → T-010)** — AgentModelPicker + panes + search + virtualisation. Replaces ModelSelector in one coherent change.
- **Phase D (T-011 → T-012)** — StatusBar ProvidersSegment + Claude-default detection wiring.
- **Phase E (T-013 → T-014)** — E2E + docs (README compliance section + ARCHITECTURE.md §5) + voice-lint + coverage.

No feature flag: the reform is atomic. The 0674 token palette is already shipped, so visual integration is near-free.

---

## 8. Non-goals recap

- No OAuth.
- No cloud secret sync.
- No new providers beyond the ten listed.
- No key rotation logic.
- No per-team policies.
- No changes to headless CLI key resolution.
- No breaking change to existing `OLLAMA_BASE_URL` users.
- No "Coming soon" placeholders.
