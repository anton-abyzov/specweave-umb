---
increment: 0682-studio-agent-model-picker
title: >-
  vSkill Studio — Unified Agent + Model Picker (Claude-Default, Two-Pane,
  Searchable)
type: feature
priority: P1
status: completed
created: 2026-04-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: vSkill Studio — Unified Agent + Model Picker

## Overview

The Studio's current `ModelSelector` is a flat single-pane dropdown: every provider's models are listed end-to-end, Anthropic API / OpenRouter rows grey out when no key is set, and there is no way to add a key without leaving Studio. This treats "agent" and "model" as one conflated axis, ignores the fact that **most Studio users are Claude Code natives who should never see a non-default experience**, and fails to surface the breadth of OpenRouter's 300+ model catalog in any searchable way.

This increment rebuilds the control as the **brand-defining command surface** of Studio — Linear/Raycast-level, two-pane, keyboard-first — with four structural changes:

1. **Agent-first, model-second hierarchy.** The top-level choice is the *agent*: **Claude Code** (default), **Anthropic API**, **OpenRouter**, **Cursor**, **Codex CLI**, **Gemini CLI**, **GitHub Copilot**, **Zed**, **Ollama**, **LM Studio**. Once an agent is selected, the right pane lists that agent's models. `agents-registry.ts` already defines 20+ agents with display names and detection commands — we reuse it.
2. **Claude Code is the detected default.** If the project contains `.claude/` (skills, plugins, or agents subfolders) AND the `claude` binary is on PATH, Studio boots with Claude Code preselected — no user action, no toast nag. If `.claude/` is absent but `claude` is installed, Claude Code remains available but not defaulted. If neither is true, the first available agent wins.
3. **Searchable OpenRouter catalog.** A `/api/openrouter/models` endpoint already exists as a pass-through. We extend it with a 10-minute server cache and feed the results into a virtualised, search-as-you-type list showing **name · context window · $prompt/$completion per 1M tokens** as the full row text. Filter is in-memory, 60ms debounce, no network per keystroke.
4. **Inline access CTAs replace grey-out.** Locked providers render a calm lock glyph and a single-line inline CTA ("Add API key →" for Anthropic / OpenRouter, "Install Claude Code →" / "Install Codex CLI →" for CLI-tooled agents). Clicking a CTA opens a **single unified Settings modal** reachable from the picker footer. No separate settings-vs-picker-vs-key surfaces.

Supporting changes carried over from the prior scope cut:

- **Max/Pro reframe** — "Claude (Max/Pro subscription)" becomes **"Use current Claude Code session"**, with a one-line delegation caption and a compliance test proving the adapter never reads `~/.claude/credentials*|auth*|token*`. Required by Anthropic's April 4 2026 ToS update.
- **Env var normalisation** — `OLLAMA_HOST` primary, `OLLAMA_BASE_URL` backcompat, with a `docs/ARCHITECTURE.md §5` env-vars table documenting every env var Studio reads.
- **StatusBar lock indicators** — glanceable per-provider lock/unlock glyphs in the StatusBar.

## Code Location & Scope

**Target codebase:** `repositories/anton-abyzov/vskill/`
- **UI (NEW):** `src/eval-ui/src/components/AgentModelPicker.tsx`, `src/eval-ui/src/components/AgentPane.tsx`, `src/eval-ui/src/components/ModelPane.tsx`, `src/eval-ui/src/components/SettingsModal.tsx`, `src/eval-ui/src/hooks/useAgentCatalog.ts`, `src/eval-ui/src/settings/SettingsContext.tsx`, `src/eval-ui/src/settings/keyStore.ts`
- **UI (MOD):** `src/eval-ui/src/components/StatusBar.tsx` (add ProvidersSegment), `src/eval-ui/src/strings.ts` (agent + provider copy)
- **UI (REPLACE):** `src/eval-ui/src/components/ModelSelector.tsx` — retired in favour of `AgentModelPicker`; call sites updated.
- **Server (MOD):** `src/eval-server/api-routes.ts` (label rename, `/api/settings/keys` endpoints, 10-min cache on `/api/openrouter/models`, detection endpoint)
- **Server (NEW):** `src/eval-server/settings-store.ts` (tiered keychain / localStorage-proxy)
- **Core (MOD + NEW):** `src/eval/llm.ts` (doc-block reframe, swap Ollama to helper), `src/eval/env.ts` (NEW — `resolveOllamaBaseUrl()`), `src/eval/__tests__/claude-cli-compliance.test.ts` (NEW — compliance gate)
- **Agent metadata:** `src/agents/agents-registry.ts` — reused, not modified (unless a new wrapper-folder key needs adding)
- **Docs:** `docs/ARCHITECTURE.md` (env-vars §5), `README.md` (compliance note + links)
- **Tests:** Vitest `__tests__/` alongside new modules; Playwright `e2e/agent-model-picker.spec.ts`

**Not in scope:**
- New provider SDKs beyond the listed ten.
- Cloud-hosted secret sync (1Password, Doppler, etc.).
- OAuth flows of any kind for any provider.
- Changes to the headless `vskill eval run` CLI.
- Marketing site (`vskill-platform`).
- Modifications to `agents-registry.ts` beyond possibly adding a `wrapperFolder` field if not present.

**Existing building blocks (REUSE):**
- `src/agents/agents-registry.ts` — agent ids, display names, `detectInstalled` commands.
- `src/eval/llm.ts::createClaudeCliClient()` — already spawns `claude` binary with `stripEnvPrefix: "CLAUDE"`. Compliant; only doc-block + label change.
- `src/eval-server/api-routes.ts::/api/openrouter/models` — already proxies OpenRouter's `/v1/models`. Extend with cache.
- `src/eval-server/api-routes.ts::detectAvailableProviders()` — extend return shape to include agent-level info.
- `src/eval-ui/src/strings.ts` (from 0674) — central voice-controlled copy; add agent + provider entries.
- `0674-vskill-studio-redesign` warm-neutral token palette — reused in all new surfaces.

## Personas

- **P1 — Claude Code native (primary)**: a developer whose daily driver is Claude Code. Their project has `.claude/skills/`, `.claude/plugins/`, and a SpecWeave setup. They expect Claude Code to "just work" as the default and never want to see a Max/Pro-subscription label or an OAuth prompt.
- **P2 — Multi-agent explorer**: a developer testing a skill across Cursor, Codex CLI, and Gemini CLI. Wants the picker to show which agents are installed locally (via wrapper-folder presence + binary availability) and switch between them with keyboard speed.
- **P3 — OpenRouter power user**: a developer comparing Claude, Mistral, DeepSeek, and Qwen models via OpenRouter. Wants to search by name ("qwen") and see price + context window as row metadata, not buried in a tooltip.
- **P4 — API-key developer**: same as P2's API-key flavour — paste a key, see the provider unlock live, never edit shell profiles.
- **P5 — Local-first / Ollama user**: runs Ollama on a GPU workstation. Wants `OLLAMA_HOST` to Just Work.
- **P6 — Compliance reviewer**: audits Studio for ToS compliance. Needs a test proving claude-cli adapter never opens `~/.claude/credentials*`.

## User Stories

### US-001: Claude Code as Auto-Default for `.claude/`-Enabled Projects (P1)
**Project**: vskill

**As a** Claude Code native working in a project with `.claude/skills/` installed
**I want** Studio to default to Claude Code (agent) and Claude Sonnet (model) without any config
**So that** the tool feels native to my workflow — no dropdown fiddling, no "which agent?" prompt

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a project with `.claude/skills/` (or `.claude/agents/` or `.claude/plugins/`) present AND the `claude` binary resolvable via `which claude`, when Studio boots for the first time (no `.vskill/studio.json`), then the picker's `activeAgent` is `"claude-code"`, the `activeModel` is `"sonnet"`, and no toast/banner announces this — the default is silent.
- [x] **AC-US1-02**: Given a project with no `.claude/` subdirectory (even if `claude` binary is installed), when Studio boots fresh, then `claude-code` is **available** in the agent list but NOT the default; instead, the first agent whose availability resolves true wins, in order: Anthropic API (if key) → OpenRouter (if key) → Ollama (if probe succeeds) → LM Studio (if probe succeeds) → Claude Code (fallback; using CLI even without `.claude/` folder is allowed). The chosen default persists to `.vskill/studio.json` on first user-initiated selection.
- [x] **AC-US1-03**: Given a project with `.claude/` present but `claude` binary missing, when Studio boots, then Claude Code agent row shows a lock glyph + inline CTA **"Install Claude Code →"** pointing at `https://docs.claude.com/en/docs/claude-code` in the help popover. Claude Code is NOT auto-defaulted; selection falls through per AC-US1-02.

---

### US-002: Unified Two-Pane Agent + Model Picker with Keyboard Navigation (P1, P2)
**Project**: vskill

**As a** developer using Studio dozens of times a day
**I want** a two-pane picker where agents live on the left and filtered models live on the right, fully keyboard-driven
**So that** I can change my active model in ≤2 keystrokes without leaving the keyboard

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the picker's trigger button in the top rail (shows current agent icon + current model name), when the user clicks it OR presses `Cmd/Ctrl+K`, then a popover opens within 100ms with two panes side-by-side: **left pane (240px wide)** lists all agents as 36px rows; **right pane (360px wide)** lists the models of the currently-focused agent as 44px two-line rows.
- [x] **AC-US2-02**: Given the popover is open, when it renders, then each agent row shows (in order, left-to-right): (a) the agent's 16×16 icon from `agents-registry.ts`, (b) the agent's display name (e.g., "Claude Code", "Cursor"), (c) a wrapper-folder presence dot — filled `var(--accent)` if the relevant wrapper folder (e.g., `.claude/` for Claude Code) exists in the project root, hollow if absent, (d) a binary/service-availability glyph (small circle filled for available, lock for locked), (e) a "Currently active" 10px badge on the one selected row; hover uses `var(--surface-muted)` background, selected uses `var(--accent-wash)` background + 1px left border in `var(--accent)`.
- [x] **AC-US2-03**: Given the popover is open, when it renders, then each model row in the right pane is 44px tall and shows **two lines**: line 1 is the model display name in Inter Tight 14px medium (e.g., "Claude Sonnet 4.6"); line 2 is metadata in 12px tabular-nums monospace: `"1M ctx · $3.00 / $15.00 per 1M tokens"` (for priced models) or `"128k ctx · subscription"` (for claude-cli) or `"local · 8B · free"` (for Ollama). No icon in the model row (icon is implied by left-pane agent).
- [x] **AC-US2-04**: Given the popover is open, when the user presses `↓` / `↑`, then focus moves within the *currently-focused pane* (agent pane on open, model pane once user navigates right). Pressing `→` moves focus to the model pane (onto the first model), `←` returns to the agent pane, `Tab` / `Shift+Tab` cycles focus within the whole popover, `Enter` on a model row selects it + persists to `.vskill/studio.json` + closes the popover, `Esc` closes without changes.
- [x] **AC-US2-05**: Given the popover is open, when the user highlights a different agent in the left pane (via `↓`/`↑` or hover), then the right pane re-renders with that agent's models *immediately* (no loading spinner for cached catalogs); currently-active model across the whole Studio stays the active selection even when viewing a different agent's list.
- [x] **AC-US2-06**: Given the popover, when it renders, then a footer row (32px tall, separated from content by a 1px `var(--border-default)` rule) contains: (a) a "Settings" button opening the Settings modal (US-004), (b) a faint keyboard-hints line `"↑↓ navigate · Enter select · Esc close"`, each hint styled with a muted-kbd token. The footer is always visible — no scrolling reveals it.
- [x] **AC-US2-07**: Given the popover is open, when the user's `prefers-reduced-motion: reduce` media query matches, then the popover opens instantly (no 120ms fade + 2px translate-up); otherwise it animates in 120ms with `opacity 0 → 1` and `translateY(2px) → 0`.

---

### US-003: OpenRouter Catalog Search (P3)
**Project**: vskill

**As a** developer comparing 300+ models via OpenRouter
**I want** a search-as-you-type filter over the catalog with visible name / context window / price metadata
**So that** I can find the right model in <5 seconds without scrolling an endless list

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the user selects the "OpenRouter" agent in the left pane AND has an OpenRouter key stored, when the right pane renders, then a search input sits at the top (above the model list) with placeholder *"Search 300+ models…"* — focus auto-moves to this input when the OpenRouter agent becomes active. The model list below is virtualised (react-window or equivalent) when ≥80 rows exist.
- [x] **AC-US3-02**: Given the search input is focused, when the user types a query, then (a) filter runs client-side with 60ms debounce, (b) matches on model `name` (case-insensitive substring), (c) shows results ranked with exact-prefix matches first, (d) preserves each row's full metadata (name + context window + price), (e) shows a "No models match \"<q>\" [Clear]" row when zero matches — the Clear button restores the full list.
- [x] **AC-US3-03**: Given the `/api/openrouter/models` endpoint is called by the client, when the server handles the request, then the response is served from a 10-minute in-memory cache keyed by the API key; cache miss triggers a fresh fetch from `https://openrouter.ai/api/v1/models` with the key; stale cache is served with a `X-Vskill-Catalog-Age: <seconds>` header when the fresh fetch fails. Clients show a toast *"Using cached catalog ({n} min old)"* when age exceeds 10 minutes.
- [x] **AC-US3-04**: Given the OpenRouter agent is selected but no key is stored, when the right pane renders, then instead of a search input + empty list, it shows a calm inline CTA card with the text *"Add your OpenRouter API key to browse 300+ models"* and a primary button **"Add API key →"** that opens the Settings modal focused on the OpenRouter tab. No search input is shown until a key is present.

---

### US-004: Unified Settings Modal for API Keys (P4)
**Project**: vskill

**As a** developer with API keys for Anthropic and/or OpenRouter
**I want** one Settings modal to manage them all, reachable from the picker footer
**So that** I don't hunt across multiple surfaces to unlock providers

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the picker footer's "Settings" button OR the keyboard shortcut `Cmd/Ctrl+,`, when triggered, then a modal opens titled **"Settings"** with two sections: **"API Keys"** (primary focus) containing Anthropic and OpenRouter rows, and **"Storage"** showing the current tier (on Darwin: "Browser storage" / "macOS Keychain" radio; on non-Darwin: "Browser storage" read-only with a note). A top banner states: *"Keys are stored locally on this device only. Never synced, never committed to git, never transmitted off-device except to the provider's own API."* Banner uses `var(--info)` tokens; no hardcoded hex.
- [x] **AC-US4-02**: Given each provider row in the modal, when rendered, then it exposes: (a) a masked password input with Show toggle (eye icon), (b) a Paste helper button, (c) a Save primary button (disabled while empty/whitespace), (d) a Remove destructive button (disabled when no key stored), (e) a status line `"Key stored locally — updated {ISO8601}"` or `"No key stored"`, (f) a link to the provider's key-issuance page (Anthropic → `platform.claude.com/settings/keys`; OpenRouter → `openrouter.ai/settings/keys`).
- [x] **AC-US4-03**: Given the user pastes a key and clicks Save, when the save succeeds, then (a) a POST to `/api/settings/keys` fires with `{ provider, key, tier }` in the JSON body (never query string), (b) a toast fires *"Anthropic API key saved (local only, never synced)"*, (c) `GET /api/config` reflects `available: true` for that provider within 500ms, (d) the StatusBar lock glyph flips to unlocked, (e) if the Agent+Model picker is open in the background, its locked CTA row for that provider swaps to a live agent row with a subtle 800ms `var(--accent-wash)` flash (skipped under `prefers-reduced-motion`).
- [x] **AC-US4-04**: Given a key is stored, when the user clicks Remove and confirms, then the key is wiped from the chosen tier, the StatusBar glyph reverts to locked, the picker row reverts to its CTA state, and a toast confirms *"Anthropic API key removed"*. No server log path (error or otherwise) ever contains more than the last 4 characters of the key — assert via mocked logger unit test.
- [x] **AC-US4-05**: Given a key input, when the user pastes a value that fails the provider's prefix check (Anthropic `sk-ant-`; OpenRouter `sk-or-`), then an inline non-blocking warning reads *"This doesn't look like a typical {provider} key. Save anyway?"* — Save remains enabled. Empty/whitespace-only input disables Save with inline validation *"Enter a non-empty key"*.

---

### US-005: Max/Pro Reframe — "Use current Claude Code session" (P1, P6)
**Project**: vskill

**As a** Claude Code native user AND a compliance reviewer
**I want** the claude-cli provider renamed to "Use current Claude Code session" with a compliance-asserted adapter path
**So that** nothing in Studio implies Anthropic Max/Pro subscription scraping, and an automated test proves the adapter never reads `~/.claude/credentials*` family

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the agent list rendered in the picker, when the Claude Code row appears, then its caption under the name reads: *"Delegates to the `claude` CLI — your existing Claude Code session handles quota."* The string `"Max/Pro"` and the word `"subscription"` appear nowhere in picker / Settings / StatusBar copy (voice-lint CI grep enforces on `src/eval-*/` and `src/eval-ui/src/`).
- [x] **AC-US5-02**: Given the compliance test `src/eval/__tests__/claude-cli-compliance.test.ts`, when it runs, then it mocks `fs.readFile`, `fs.readFileSync`, `fs.open`, `fs.openSync`, `fs.createReadStream`, `fs.promises.readFile`, and `fs.promises.open` to spies, executes `createClaudeCliClient().generate("sys", "prompt")` against a fake `claude` binary shim, and asserts zero spy calls receive paths matching `/\.claude\/(credentials|auth|token)/i`. The test ALSO greps `dist/*.js` (compiled bundle from `npm run build`) for the literal strings `".claude/credentials"`, `".claude/auth"`, `".claude/token"` and fails on any match.
- [x] **AC-US5-03**: Given `README.md` and `docs/ARCHITECTURE.md`, when a reader searches for "Claude Max" or "subscription", then the relevant section explicitly states: *"vSkill Studio does not consume your Max/Pro subscription quota directly. It delegates to the official Claude Code CLI, which is the sanctioned consumer per Anthropic's April 2026 ToS."* Link to `https://docs.claude.com/en/docs/claude-code` included.
- [x] **AC-US5-04**: Given the user selects Claude Code but the `claude` binary is missing on PATH, when a generate call is attempted, then the error toast reads: *"Claude Code not found. Install it: `npm install -g @anthropic-ai/claude-code`. Or choose a provider with an API key."* The error does NOT suggest "export ANTHROPIC_API_KEY" as a substitute.

---

### US-006: StatusBar Provider Lock/Unlock Indicators (P1, P4)
**Project**: vskill

**As a** Studio user switching between projects
**I want** a compact row of lock/unlock glyphs in the StatusBar, one per provider
**So that** I can see my access state at a glance without opening the picker

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the StatusBar renders, when providers are known, then between the existing "Health" segment and the `flex: 1` spacer, a new **Providers** segment appears with one 10×10 glyph per provider in the fixed order: Claude Code → Anthropic API → OpenRouter → Ollama → LM Studio. Each glyph is a lock or unlock SVG drawn with `fill="none" stroke="currentColor"` — no hardcoded hex.
- [x] **AC-US6-02**: Given a glyph, when the user hovers or tab-focuses it, then a tooltip shows `"<provider label> — <locked|unlocked>. <action hint>"`, e.g., *"Anthropic API — locked. Click to add a key."* or *"Ollama — unlocked, 3 models."* Clicking a locked API-keyed provider opens the Settings modal focused on that provider tab; clicking a locked CLI-tooled provider opens a help popover with install instructions.
- [x] **AC-US6-03**: Given viewport width below 640px, when StatusBar renders, then the Providers segment collapses into a single summary button *"{n}/{m} providers"*; clicking expands a popover with one row per provider. Above 640px the full row is shown regardless of how many providers are unlocked — no automatic collapse at wider widths.

---

### US-007: Environment Variable Normalisation + Architecture Docs (P5)
**Project**: vskill

**As a** developer running Ollama on a GPU workstation
**I want** Studio to honour `OLLAMA_HOST` as primary (matching Ollama's own docs), and to document every env var it reads in one place
**So that** my existing `OLLAMA_HOST=...` config works without duplication, and operators can audit env-var contracts

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given `src/eval/env.ts` exports `resolveOllamaBaseUrl(env)`, when called with various combinations, then precedence is (1) `env.OLLAMA_HOST`, (2) `env.OLLAMA_BASE_URL`, (3) `"http://localhost:11434"`; bare `host:port` values (e.g., `gpu.local:11434`) have `http://` prepended; both set with different values emits a once-per-process `warnOnce` log *"Both OLLAMA_HOST and OLLAMA_BASE_URL are set. Using OLLAMA_HOST ({value}). OLLAMA_BASE_URL is deprecated."* Both call sites in `src/eval/llm.ts` and `src/eval-server/api-routes.ts` delegate to this helper; grep verifies zero inline `process.env.OLLAMA_BASE_URL` reads remain outside `env.ts`.
- [x] **AC-US7-02**: Given `docs/ARCHITECTURE.md`, when a reader opens §5 "Environment Variables", then a table lists every env var Studio reads: `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`, `OLLAMA_HOST` (primary), `OLLAMA_BASE_URL` (fallback, deprecated), `VSKILL_EVAL_PROVIDER`, `VSKILL_EVAL_MODEL`, `CODEX_API_KEY`, plus any others. Each row includes: name, precedence/fallback, default, required-yes/no, where-it's-read (file:line), and purpose.
- [x] **AC-US7-03**: Given the README and `docs/ARCHITECTURE.md`, when a reader searches for `OLLAMA_HOST`, then an example appears: `OLLAMA_HOST=http://gpu-server:11434 npx vskill studio`, accompanied by a note that `OLLAMA_BASE_URL` is preserved for backcompat but deprecated.

---

## Functional Requirements (cross-cutting)

- **FR-001**: Picker state persists to `.vskill/studio.json` as `{ activeAgent: string, activeModel: string, updatedAt: ISO8601 }`. The file is gitignored by default (Studio's first run ensures `.gitignore` contains `.vskill/`).
- **FR-002**: All user-facing strings route through `src/eval-ui/src/strings.ts` (0674's voice registry). Voice-lint CI grep rejects `"Max/Pro"`, `"subscription"` in picker/settings/StatusBar surfaces, celebration emoji, and trailing `!!`.
- **FR-003**: No key value or OAuth token appears in any log, error, toast, network URL, or compiled bundle. Redaction helper `redactKey(k)` returns `"****" + k.slice(-4)`.
- **FR-004**: Agent detection cache TTL is 30 seconds; OpenRouter catalog cache TTL is 10 minutes server-side + 5 minutes client stale-while-revalidate.
- **FR-005**: `.vskill/studio.json` writes are atomic (write to `.tmp` then rename) to survive crashes mid-write.

## Non-Functional Requirements

- **NFR-001 — Security**: Keys never stored in synced locations; compliance test blocks closure if `~/.claude/credentials*|auth*|token*` reads are detected.
- **NFR-002 — Performance**: Popover opens ≤100ms (tested under CPU-4x throttle in Playwright); search filter runs in ≤16ms per keystroke for 500-row list; catalog refetch invisible under stale-while-revalidate.
- **NFR-003 — Accessibility**: Full keyboard flow (no mouse); focus trap in Settings modal; ARIA labels on every glyph; `role="listbox"` on panes; `aria-selected` on active rows; `prefers-reduced-motion` honoured globally.
- **NFR-004 — Theming**: Every new element uses 0674 warm-neutral tokens; no hardcoded hex outside `globals.css`; CI grep enforces.
- **NFR-005 — Observability**: Settings save/remove, catalog cache hit/miss, agent-switch, and model-select each emit structured events (redacted) to the existing telemetry channel.
- **NFR-006 — Compliance**: A blocking closure gate requires the claude-cli-compliance test to pass + the dist bundle grep to return zero matches for credential-file path literals.

## Out of Scope (explicit)

- OAuth flows (any provider).
- Cloud secret stores (1Password, Doppler, Infisical, AWS Secrets Manager).
- Per-team / shared key policies.
- Key rotation / expiry reminders.
- New provider SDKs beyond the ten listed (Claude Code, Anthropic API, OpenRouter, Cursor, Codex CLI, Gemini CLI, Copilot, Zed, Ollama, LM Studio).
- Marketing site (`vskill-platform`).
- Changes to the headless `vskill eval run` CLI.
- "Coming soon" placeholders for unimplemented providers — omit rather than stub.

## Dependencies

- 0674-vskill-studio-redesign — warm-neutral token palette, Inter Tight / JetBrains Mono font loading, `strings.ts` convention, StatusBar component.
- 0677-lm-studio-provider — aware of; LM Studio appears as an agent in the picker with that increment's probe logic.
- `agents-registry.ts` — reused for agent display names + `detectInstalled` commands.

## Open Questions (resolved in plan)

1. **Q-001**: Catalog source-of-truth for each agent? → **ADR-0682-01**.
2. **Q-002**: Credential storage tier? → **ADR-0682-02**.
3. **Q-003**: Claude Code session delegation vs alternatives? → **ADR-0682-03**.
4. **Q-004**: Agent-then-model UI hierarchy vs flat list vs command-palette? → **ADR-0682-04**.
