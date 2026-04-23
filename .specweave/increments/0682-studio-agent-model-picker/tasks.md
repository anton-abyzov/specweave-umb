---
increment: 0682-studio-agent-model-picker
title: vSkill Studio — Unified Agent + Model Picker — Tasks
scope: Two-pane Agent+Model picker replacing ModelSelector, Settings modal, Claude-default detection, StatusBar provider locks, OLLAMA_HOST normalisation, ToS compliance gate
target_days: 4
status: planned
---

# Tasks: vSkill Studio — Unified Agent + Model Picker

> **Target codebase:** `repositories/anton-abyzov/vskill/`
> **Stack:** Node 20 + TypeScript 5.7 + Vite 6 + React 19 + Tailwind 4 + Vitest 3 + Playwright
> **Phases:**
> - **A** — Server reframe + env normalisation + compliance prep (T-001 → T-003)
> - **B** — Settings store + endpoints + Settings modal (T-004 → T-006)
> - **C** — AgentModelPicker two-pane + search + keyboard nav (T-007 → T-010)
> - **D** — StatusBar lock indicators + Claude-default detection (T-011 → T-012)
> - **E** — E2E + docs + voice-lint + closure gate (T-013 → T-014)

---

## Phase A — Server Reframe + Env Normalisation + Compliance Prep

---

### T-001: Rename claude-cli label, extend `detectAvailableProviders()` with detection block, enforce voice-lint
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-03, AC-US5-04 | **Status**: [x] completed
**Phase**: A | **Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given `src/eval-server/api-routes.ts::detectAvailableProviders()` and `src/eval-ui/src/strings.ts`
  When the server boots and a client calls `GET /api/config`
  Then the response contains: (a) `providers[0].id === "claude-cli"` with `label === "Use current Claude Code session"` (exact match — no "Max/Pro"); (b) a new `detection: { wrapperFolders: { ".claude": bool, ".cursor": bool, ".codex": bool, ".gemini": bool, ".github": bool, ".zed": bool, ".specweave": bool }, binaries: { claude: bool, cursor: bool, codex: bool, gemini: bool } }` block populated by synchronous scans of the project root; (c) no occurrence of the substring `"Max/Pro"` anywhere in the response body (JSON.stringify grepped); (d) `strings.ts::providers.claudeCli.caption` equals `"Delegates to the `claude` CLI — your existing Claude Code session handles quota."`; (e) `src/eval/llm.ts` has a new doc-block above `createClaudeCliClient()` that explicitly states the adapter never reads `~/.claude/(credentials|auth|token)*`; (f) the voice-lint CI script extended to fail when `Max/Pro` or `subscription` appear in `src/eval-ui/src/**` or `src/eval-server/**`, but allowed in `README.md` and `docs/**`; (g) the not-found error message for claude-cli matches `strings.ts::providers.claudeCli.missingBinary` containing `"Install it: \`npm install -g @anthropic-ai/claude-code\`"` without any `"ANTHROPIC_API_KEY"` suggestion.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (line 422 label; new detection block)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/strings.ts` (agent + provider copy block)
  - `repositories/anton-abyzov/vskill/src/eval/llm.ts` (doc block above `createClaudeCliClient`; error-message source)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.config.test.ts` (NEW — asserts label, detection block, no "Max/Pro")
  - `repositories/anton-abyzov/vskill/scripts/voice-lint.sh` (MOD — extend scope)
**Dependencies**: none
**Notes**: Wrapper-folder scan uses `fs.existsSync(path.join(root, folder))` — single-level, cheap. Binary scan uses `which <name>` (shell). Detection results are server-side; the client receives them as data.

---

### T-002: `resolveOllamaBaseUrl()` helper with `warnOnce`; swap both call sites
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01 | **Status**: [x] completed
**Phase**: A | **Estimated**: 2h | **Test Level**: unit
**Test Plan**:
  Given `src/eval/env.ts` exports `resolveOllamaBaseUrl(env: NodeJS.ProcessEnv)` and a module-scoped `warnOnce(msg, logger?)`
  When called with (a) only `OLLAMA_HOST="http://gpu:11434"`, (b) only `OLLAMA_BASE_URL="http://legacy:11434"`, (c) both set to different values (10 successive calls), (d) `OLLAMA_HOST="gpu.local:11434"` (no scheme), (e) neither set, (f) `OLLAMA_HOST="https://secure.gpu:443"`
  Then (a) returns `"http://gpu:11434"` with no warning emitted; (b) returns `"http://legacy:11434"` with no warning; (c) returns the `OLLAMA_HOST` value on every call AND the mocked `console.warn` spy is called exactly once across the 10 invocations, with a message containing both env-var names and the phrase `"deprecated"`; (d) returns `"http://gpu.local:11434"` (scheme prepended); (e) returns `"http://localhost:11434"`; (f) returns `"https://secure.gpu:443"` unchanged; and a `grep -rn "process\.env\.OLLAMA_BASE_URL" src/` outside `env.ts` returns zero matches (asserted via the test itself shelling out to grep).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval/env.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval/__tests__/env.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval/llm.ts` (swap line 358)
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (swap line 392)
  - `repositories/anton-abyzov/vskill/src/eval/__tests__/llm.test.ts` (MOD — update Ollama tests to use helper)
**Dependencies**: none
**Notes**: `warnOnce` uses a module-scoped `Set<string>` keyed by message; export a test-only `_resetWarnOnce()` for isolation between tests.

---

### T-003: Claude-CLI compliance test + dist-bundle-grep closure gate
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02, NFR-006 | **Status**: [x] completed
**Phase**: A | **Estimated**: 3h | **Test Level**: unit + CI script
**Test Plan**:
  Given `src/eval/__tests__/claude-cli-compliance.test.ts`, a fake `claude` binary shim at `src/eval/__fixtures__/fake-claude.sh` (executable, reads stdin, echoes canned JSON), and a new CI script `scripts/check-bundle-compliance.sh`
  When (a) the unit test runs, (b) the CI script is invoked after `npm run build`
  Then (a) the unit test mocks `fs.readFile`, `fs.readFileSync`, `fs.open`, `fs.openSync`, `fs.createReadStream`, `fs.promises.readFile`, `fs.promises.open` to Vitest spies; prepends the fake binary directory to `PATH`; invokes `createClaudeCliClient().generate("sys prompt", "user prompt")` to completion; asserts zero spy call receives a path matching the regex `/\.claude\/(credentials|auth|token)/i` (with case variations tested); and asserts the adapter succeeded (non-null text return); (b) the CI script greps `dist/**/*.js` (after `npm run build`) for the literal strings `".claude/credentials"`, `".claude/auth"`, `".claude/token"`, `"credentials.json"` (adjacent to `.claude`), and any occurrence of the regex `\.claude\/(credentials|auth|token)` — exits 1 on any match. The CI script is added to the existing quality pipeline (alongside voice-lint).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval/__tests__/claude-cli-compliance.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval/__fixtures__/fake-claude.sh` (NEW, `chmod +x`)
  - `repositories/anton-abyzov/vskill/scripts/check-bundle-compliance.sh` (NEW)
**Dependencies**: T-001
**Notes**: The fake binary shim is ~15 lines of bash: reads stdin into a variable, echoes a canned response like `{"text":"ok"}`, exits 0. The PATH prefix ensures `spawn("claude", ...)` picks up the shim instead of a real install.

---

## Phase B — Settings Store + Endpoints + Settings Modal

---

### T-004: Tiered `settings-store` (browser-proxy + optional macOS Keychain) with redacted logging
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04, NFR-001 | **Status**: [x] completed
**Phase**: B | **Estimated**: 4h | **Test Level**: unit + integration
**Test Plan**:
  Given `src/eval-server/settings-store.ts` exports `{ saveKey, readKey, removeKey, listKeys, setTier, getTier }` taking `(provider, projectHash)` and a tier state machine with values `"browser" | "keychain"`
  When (a) `setTier("keychain")` is called on a simulated Darwin env, (b) `setTier("keychain")` on non-Darwin, (c) `saveKey("anthropic", "sk-ant-test-1234", projectHash)` in `browser` tier, (d) same call in `keychain` tier on Darwin, (e) `readKey` after save, (f) `removeKey`, (g) a call that throws mid-way and gets logged via the injected logger
  Then (a) succeeds silently; (b) throws `UnsupportedTierError` with message `"macOS Keychain tier is only supported on Darwin"`; (c) stores in an in-memory `Map<string, { key: string; updatedAt: string }>` keyed `${projectHash}:anthropic`, and `listKeys(projectHash)` returns `{ anthropic: { stored: true, updatedAt: <ISO>, tier: "browser" }, openrouter: { stored: false, ... } }`; (d) invokes `child_process.spawn("security", ["add-generic-password", "-s", "vskill-anthropic", "-a", projectHash, "-w", "sk-ant-test-1234", "-U"])` with exit code 0, and does NOT log the key to any stream (asserted via spies on `process.stdout.write`, `process.stderr.write`, and the injected logger); (e) returns `"sk-ant-test-1234"` in both tiers; (f) removes from current tier and `listKeys` shows `stored: false`; (g) the injected logger receives a message containing at most `"****1234"` (the redaction helper applied), never the full key or a substring longer than the last 4 chars.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/settings-store.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/settings-store.test.ts` (NEW)
**Dependencies**: none
**Notes**: `redactKey(k: string): string` returns `"****" + k.slice(-4)` — tested alongside. Keychain spawn passes the key via `-w <value>` arg; this is the documented secure pattern for `security add-generic-password`, which handles argv redaction in ps listings via kernel-level behaviour.

---

### T-005: `/api/settings/keys` endpoints (GET / POST / DELETE) + OpenRouter 10-min cache
**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-03, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [x] completed
**Phase**: B | **Estimated**: 3h | **Test Level**: integration
**Test Plan**:
  Given the eval-server booted against a temp project root, with `settings-store` injected
  When (a) `GET /api/settings/keys` before any save, (b) `POST /api/settings/keys { provider: "anthropic", key: "sk-ant-test-1234" }` with valid JSON body, (c) `GET /api/config` immediately after save, (d) `DELETE /api/settings/keys/anthropic`, (e) `POST /api/settings/keys { provider: "anthropic", key: "" }`, (f) `POST /api/settings/keys { provider: "openrouter", key: "random-string-without-prefix" }`, (g) any endpoint called with the key as a query-string parameter, (h) `GET /api/openrouter/models` with valid key stored (first call), (i) `GET /api/openrouter/models` immediately afterward (cache hit), (j) same call >10 min later simulated by advancing a fake clock, (k) upstream OpenRouter returns 500
  Then (a) returns `{ anthropic: { stored: false, ... }, openrouter: { stored: false, ... } }`; (b) returns `200 { ok: true, updatedAt: <ISO>, tier: "browser", available: true }`, and server stdout (captured) contains only `"****1234"` never the full key; (c) returns `providers[].available === true` for `anthropic`; (d) returns `{ ok: true }`, subsequent `GET /api/config` shows `available: false`; (e) returns `400 { error: "key must be non-empty string" }`; (f) returns `200` with a `warning` field `"key doesn't match typical OpenRouter prefix sk-or-"` but still saves; (g) handler rejects with 400 — no handler reads `req.query.key`; (h) fetches upstream, caches for 600_000 ms; (i) served from cache (no upstream fetch — verified via fetch spy call count of 1); (j) triggers fresh upstream fetch; (k) returns last-known-good cache with `X-Vskill-Catalog-Age: <seconds>` header and a `stale: true` field in the JSON.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (extend `registerRoutes` with 3 new key endpoints + cache on existing openrouter route)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.keys.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.openrouter-cache.test.ts` (NEW)
**Dependencies**: T-004
**Notes**: The cache is a module-scoped `{ value, fetchedAt }` pair keyed by the API key's last-8 chars (so different keys don't collide and no full key is stored in cache map). Fake clock via Vitest `vi.useFakeTimers()`.

---

### T-006: `SettingsModal` component + `SettingsContext` + `keyStore` client
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, NFR-003 | **Status**: [x] completed
**Phase**: B | **Estimated**: 5h | **Test Level**: unit (Vitest + @testing-library/react)
**Test Plan**:
  Given `<SettingsModal open onClose />` mounted inside `<SettingsContext>` against a mocked `/api/settings/keys` fetch
  When the modal is open under various platforms and user inputs
  Then (a) the modal has `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing at the title; focus is trapped (Tab/Shift+Tab cycle within); initial focus is on the first provider's key input; Escape calls `onClose`; (b) the top banner renders exactly the string from `strings.ts::settings.banner` with `var(--info)` background (no hex); (c) two provider sections (Anthropic, OpenRouter) render with masked input + Show toggle + Paste button + Save + Remove + status line + key-issuance link pointing to `platform.claude.com/settings/keys` / `openrouter.ai/settings/keys`; (d) on Darwin (`process.platform === "darwin"` mocked), a Storage section shows two radio options with labels `"Browser storage (default)"` and `"macOS Keychain (recommended)"`; on non-Darwin, only `"Browser storage"` is shown as read-only text with the tooltip `"macOS Keychain is only available on macOS"`; (e) typing `""` leaves Save disabled and shows inline `"Enter a non-empty key"`; (f) pasting `"random-no-prefix"` shows a non-blocking warning `"This doesn't look like a typical Anthropic key. Save anyway?"` while keeping Save enabled; (g) pasting `"sk-ant-test-xyz-1234"` and clicking Save triggers `POST /api/settings/keys` with body `{ provider: "anthropic", key: "sk-ant-test-xyz-1234", tier: "browser" }` (verified via fetch mock), fires toast `"Anthropic API key saved (local only, never synced)"`, updates status line to `"Key stored locally — updated just now"`; (h) clicking Remove with a key stored opens a confirm dialog; confirming fires `DELETE /api/settings/keys/anthropic` and toast `"Anthropic API key removed"`; (i) under `matchMedia("(prefers-reduced-motion: reduce)").matches === true`, no motion transitions run (asserted by spy on `element.animate`).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SettingsModal.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/settings/SettingsContext.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/settings/keyStore.ts` (NEW — client fetch wrapper with redaction in error handling)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/SettingsModal.test.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/settings/__tests__/keyStore.test.ts` (NEW)
**Dependencies**: T-005
**Notes**: Focus trap implemented in-tree (~30 lines) — no `focus-trap-react` dep. Show toggle flips input `type` between `"password"` and `"text"`. Paste helper uses `navigator.clipboard.readText()` with try/catch fallback to manual paste hint.

---

## Phase C — AgentModelPicker Two-Pane + Search + Keyboard Nav

---

### T-007: `useAgentCatalog()` hook — merge config, OpenRouter fetch, Ollama poll, agent dedup
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-01, AC-US2-05, AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Phase**: C | **Estimated**: 4h | **Test Level**: unit
**Test Plan**:
  Given a test harness rendering a fake component that consumes `useAgentCatalog()`, with mocked `fetch` for `/api/config` / `/api/openrouter/models` / `/api/ollama/tags` (if/when the Ollama endpoint exists; else mock the underlying probe), and `vi.useFakeTimers()`
  When (a) the hook mounts with no prior cache, (b) the OpenRouter agent row is not focused, (c) the OpenRouter row becomes focused, (d) 5 min of simulated time passes while OpenRouter row is focused, (e) the cache is 11 min old and the upstream `/api/openrouter/models` returns 502
  Then (a) the hook returns `{ status: "loading" }` initially, then `{ status: "ready", catalog: AgentCatalog }` within one microtask of the `/api/config` mock resolving; the catalog contains `agents` in the expected order (Claude Code → Anthropic API → OpenRouter → Cursor → Codex → Gemini → Copilot → Zed → Ollama → LM Studio); `wrapperFolderPresent` and `binaryAvailable` are populated from the `detection` block; (b) no call to `/api/openrouter/models` has been made (verified via fetch spy call count of 1 for `/api/config`); (c) a call to `/api/openrouter/models` is made within 50ms of focus, the agent row's `models` array is populated with ≥200 entries (mock returns 300), and each `ModelEntry` has `pricing.prompt` + `pricing.completion` as numbers and `contextWindow` present; (d) no additional fetch (stale-while-revalidate 5 min); (e) the hook serves the cached catalog with a `cacheStale: true` flag and `catalogAgeMs > 600_000`, triggering a callback `onStaleCatalog("openrouter", ageMs)` consumable by the component layer.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useAgentCatalog.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useAgentCatalog.test.ts` (NEW)
**Dependencies**: T-001, T-005
**Notes**: Dedup rule: when an Anthropic Sonnet model appears in both Anthropic API and OpenRouter, keep both but tag with `agentId` for provenance. The `models` field on each agent is isolated — no cross-agent flattening.

---

### T-008: `AgentPane` + `ModelPane` + `LockedCta` components with frontend-design tokens
**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US3-04, AC-US5-01 | **Status**: [x] completed — implemented as `AgentList.tsx` + `ModelList.tsx` + `LockedProviderRow.tsx` per team-lead file-ownership mapping
**Phase**: C | **Estimated**: 5h | **Test Level**: unit (RTL) + visual snapshot
**Test Plan**:
  Given `<AgentPane agents={...} activeAgent="claude-code" focusedAgent="openrouter" onFocus onSelect />` and `<ModelPane agent={agentEntry} activeModel="sonnet" onSelect />`, rendered against a theme-provider wrapper
  When each component renders with fixtures covering: (a) active agent + different focused agent, (b) agent with wrapper folder present but binary missing, (c) agent with no key (locked), (d) OpenRouter agent with no key, (e) model with pricing, (f) model subscription-priced, (g) model Ollama/free, (h) user presses keyboard keys
  Then (a) the active agent row shows a 10px uppercase `"CURRENTLY ACTIVE"` kicker and 1px left border `var(--accent)`; the focused agent row (different from active) has `var(--surface-muted)` background but no left border; agent rows are 36px tall with 12px horizontal padding; (b) the agent row shows the wrapper-folder dot as filled `var(--accent)` and the binary glyph as a lock, plus a `<LockedCta variant="cli-install">` child reading `"Install Claude Code →"`; (c) the agent row shows a `<LockedCta variant="api-key">` reading `"Add API key →"`; (d) the ModelPane for OpenRouter with no key renders the CTA card matching AC-US3-04 (text `"Add your OpenRouter API key to browse 300+ models"` + primary button `"Add API key →"`) — no search input, no model list; (e) priced model row (44px tall, two lines) shows line 1 name in Inter Tight 14px and line 2 `"1M ctx · $3.00 / $15.00 per 1M tokens"` in JetBrains Mono 12px with `font-variant-numeric: tabular-nums`; (f) subscription-priced model shows `"128k ctx · subscription"` on line 2; (g) Ollama model shows `"local · 8B · free"`; (h) `onFocus` fires on `↑`/`↓` hover, `onSelect` fires on Enter; `aria-selected="true"` on focused row; `role="option"` on each row; parent uses `role="listbox"`. Voice-lint assertion: scan the rendered DOM of all fixtures — zero occurrence of `"Max/Pro"` or `"subscription"` outside the AC-US2-03 `"· subscription"` suffix (which is in `strings.ts::models.subscriptionBilling`, whitelisted in voice-lint).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/AgentPane.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelPane.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/LockedCta.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/AgentPane.test.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ModelPane.test.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/LockedCta.test.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/strings.ts` (MOD — add `models.*`, `picker.*` entries)
**Dependencies**: T-007
**Notes**: All icons inline SVG. Whitelist `"· subscription"` suffix in voice-lint by adding an ignore pattern for the precise token.

---

### T-009: Search-as-you-type + virtualised list in `ModelPane`
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed — search + debounce + useVirtualList implemented inside `ModelList.tsx`
**Phase**: C | **Estimated**: 3h | **Test Level**: unit
**Test Plan**:
  Given `<ModelPane>` rendered with an agent whose `models` array has 300 fixture entries (realistic OpenRouter shape), and a `useVirtualList(rows, rowHeight: 44, viewportHeight: 352)` hook
  When (a) the pane mounts for the OpenRouter agent, (b) the user types `"qwen"` in the search input, (c) types `"QWEN"` (uppercase), (d) types `"xyz-no-match"`, (e) types then backspaces to empty, (f) the list has exactly 79 rows (below virtualisation threshold), (g) the list has 80 rows (at threshold), (h) the user scrolls the virtualised list
  Then (a) search input is auto-focused on mount; only the visible slice of rows is rendered in the DOM (initial ~8 visible + 4 buffer = ≤12 `role="option"` nodes); (b) after 60ms debounce, the filter runs and only models matching case-insensitive substring `"qwen"` are rendered (e.g., "Qwen 2.5 72B", "Qwen Coder 32B"); matches ranked with exact-prefix first (models starting with `"qwen"` rank above `"glorpy-qwen-mix"`); (c) same result set as (b) (case-insensitive); (d) renders a single `<div data-testid="no-matches">` with text `'No models match "xyz-no-match"'` and a `<button>Clear</button>` that, when clicked, clears the query and restores the full list; (e) full list restored, no stale filter state; (f) no virtualisation applied (all 79 rows rendered); (g) virtualisation applied (only visible slice); (h) scrolling updates the rendered slice; scrollTop persists per-agent across agent-switches within the same popover session.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelPane.tsx` (MOD — add search + virtualisation)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/useVirtualList.ts` (NEW ~30 lines)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/hooks/__tests__/useVirtualList.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ModelPane.search.test.tsx` (NEW)
**Dependencies**: T-008
**Notes**: No react-window dep — 30-line `useVirtualList` hook keeps bundle clean. Ranking: `indexOf(query) === 0` first, then others by indexOf, tiebreak by name length.

---

### T-010: `AgentModelPicker` shell — popover, keyboard model, footer, motion, replace `ModelSelector` call sites
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-06, AC-US2-07 | **Status**: [x] completed — TopRail now imports AgentModelPicker; ModelSelector.tsx retained for one still-coupled test (lm-studio-ui.test.tsx) and should be removed in a follow-up once that test is migrated.
**Phase**: C | **Estimated**: 5h | **Test Level**: unit + integration
**Test Plan**:
  Given `<AgentModelPicker />` mounted with `useAgentCatalog()` providing a ready catalog, at a simulated viewport of 1280×800
  When (a) the trigger button is clicked OR `Cmd+K` pressed, (b) the popover is open and user presses keys in sequence: `↓ ↓ → ↓ Enter`, (c) the popover is open and user presses `Esc`, (d) user presses `Cmd+K` while popover is open (toggle close), (e) another input element in the page has focus and user presses `Cmd+K`, (f) `prefers-reduced-motion: reduce` matches, (g) the user focuses the agent pane and presses `Tab` multiple times, (h) the footer Settings button is clicked
  Then (a) the popover opens within 100ms (measured via `performance.now()` before/after), has two panes with widths 240px + 360px + 32px footer, agent pane has focus on the active-agent row; (b) focus moves from active agent down twice (agent pane), right moves focus to model pane onto first model, down moves within model pane, Enter selects that model, fires `POST /api/config`, writes to `.vskill/studio.json` (atomic tmp-then-rename, verified via fs spies), and closes the popover; (c) popover closes without emitting a selection; (d) popover closes; (e) Cmd+K is NOT intercepted (the page's input keeps its focus, event.defaultPrevented === false); (f) opening the popover skips the 120ms fade/translate (asserted via spy on `element.animate` — zero calls); (g) focus cycles within the popover (focus trap): once it reaches the Settings footer button, Tab wraps back to the search input (or first agent row if no search visible); (h) clicking Settings opens the `SettingsModal` (verified via a callback spy) and closes the picker popover.
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/AgentModelPicker.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/AgentModelPicker.test.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/App.tsx` (MOD — replace `<ModelSelector />` with `<AgentModelPicker />` at every call site; remove the old component)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ModelSelector.tsx` (DELETE)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/TopRail.modelselector.test.tsx` (MOD or DELETE — migrate assertions to AgentModelPicker test)
**Dependencies**: T-008, T-009
**Notes**: Cmd+K binding guarded by `if (document.activeElement?.tagName === "INPUT" || "TEXTAREA") return`. Popover uses React portal to `document.body` to avoid stacking/clipping bugs. Atomic file write: `fs.writeFile('.vskill/studio.json.tmp', json)` then `fs.rename(tmp, final)` — server-side endpoint handles this to keep FS writes off the browser; or via an existing `/api/config` endpoint that already persists.

---

## Phase D — StatusBar Lock Indicators + Claude-Default Detection

---

### T-011: `ProvidersSegment` in StatusBar with responsive collapse + tooltip + click-routing
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Phase**: D | **Estimated**: 3h | **Test Level**: unit
**Test Plan**:
  Given `<StatusBar>` inside a `<SettingsContext>` providing `providers: [{ id: "claude-cli", available: true }, { id: "anthropic", available: false }, { id: "openrouter", available: false }, { id: "ollama", available: true }, { id: "lmstudio", available: false }]`, with `matchMedia("(max-width: 640px)")` mockable
  When the StatusBar renders at (a) 1280px width, (b) 600px width, and (c) user hovers over a provider glyph, (d) clicks a locked API-keyed glyph, (e) clicks a locked CLI-tooled glyph, (f) clicks an unlocked glyph
  Then (a) a `<div data-testid="providers-segment">` sits between the Health segment and the `flex: 1` spacer, containing exactly 5 buttons in the order claude-cli → anthropic → openrouter → ollama → lmstudio; each has an `aria-label` matching `/^\w[\w\s]+ — (locked|unlocked)\.?/` and an inline SVG with `fill="none" stroke="currentColor"` (zero hardcoded hex in the rendered SVG attribute values); (b) renders a single `<button data-testid="providers-summary">` with accessible name `"2/5 providers"`; clicking it opens a popover listing each provider row; (c) a `role="tooltip"` appears on hover with text matching `"Anthropic API — locked. Click to add a key."` for the locked Anthropic glyph; (d) clicking fires a callback `openSettingsModal("anthropic")`; (e) clicking fires `openHelpPopover("codex-cli")` if that provider were in the list (tested via a variant fixture); (f) clicking an unlocked glyph fires `openSettingsModal(providerId)` (same surface for both so users can Remove a key from there).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/StatusBar.tsx` (MOD — insert ProvidersSegment between Health and flex spacer)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/ProvidersSegment.tsx` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/ProvidersSegment.test.tsx` (NEW)
**Dependencies**: T-006
**Notes**: Use a 15-line `useMediaQuery` hook (new if not already shipped) for the 640px breakpoint. Glyphs: lock = padlock SVG, unlock = open padlock SVG, both ~10×10 viewport.

---

### T-012: Claude-default detection + `.vskill/studio.json` persistence + LM Studio agent entry
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, FR-001, FR-005 | **Status**: [x] completed — studio-json.ts atomic writer + /api/config loads on boot; detection block drives auto-default selection in `useAgentCatalog`.
**Phase**: D | **Estimated**: 3h | **Test Level**: unit + integration
**Test Plan**:
  Given a temp project root + a mocked filesystem (via `memfs` or `mock-fs`), and the eval-server + `AgentModelPicker` rendered against various fixtures
  When Studio boots under scenarios: (a) project has `.claude/skills/` AND `claude` binary on PATH AND no `.vskill/studio.json`, (b) project has no `.claude/` AND `claude` binary on PATH AND `ANTHROPIC_API_KEY` set, (c) project has `.claude/` but `claude` binary missing, (d) no `.claude/`, no binaries, no keys — only Ollama probe succeeds, (e) existing `.vskill/studio.json` with `{activeAgent: "openrouter", activeModel: "anthropic/claude-sonnet-4"}`, (f) user changes selection from default to "anthropic-api / sonnet-4.7" and closes picker, then Studio restarts, (g) `.vskill/studio.json` is malformed JSON, (h) `.vskill/studio.json` write happens and is interrupted (tmp rename fails)
  Then (a) the active agent is `"claude-code"`, active model `"sonnet"`, no toast banner; `.vskill/studio.json` is written atomically (verified: `tmp` file doesn't exist after, final file does, content is valid JSON with `updatedAt: <ISO>`); (b) active agent is `"anthropic"`, active model is the first Anthropic model in the catalog; (c) the Claude Code row shows the lock glyph + `<LockedCta variant="cli-install">` reading `"Install Claude Code →"`; the default falls through to the next-available agent per AC-US1-02 ordering; (d) active agent is `"ollama"`, active model is the first Ollama-installed model; (e) the stored selection wins over auto-detection; (f) after restart, `.vskill/studio.json` contains the user's choice and the picker renders it as active; (g) a warning is logged (not shown in UI) — `"Ignoring malformed .vskill/studio.json"` — and Studio proceeds with auto-detection defaults; does NOT throw; rewrites on first user selection; (h) the tmp file is cleaned up on next write attempt (verified via fs spy); the old `.vskill/studio.json` remains unchanged (never partial).
**Files**:
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (MOD — `GET /api/config` reads `.vskill/studio.json`; `POST /api/config` persists atomically)
  - `repositories/anton-abyzov/vskill/src/eval-server/studio-json.ts` (NEW — load/save with atomic tmp-then-rename, malformed-file handling)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/studio-json.test.ts` (NEW)
  - `repositories/anton-abyzov/vskill/src/eval-server/__tests__/api-routes.claude-default.test.ts` (NEW — covers all 8 scenarios)
  - `repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts` (MOD — add LM Studio to provider list, probe logic from 0677-lm-studio-provider coordinated if landed first)
**Dependencies**: T-007, T-010, T-011
**Notes**: Atomic write helper: `writeAtomic(path, content): Promise<void>` writes to `${path}.tmp.${randomId}`, then `fs.rename(tmp, path)`. On startup, sweep any orphaned `.tmp.*` siblings of `.vskill/studio.json`.

---

## Phase E — E2E + Docs + Closure Gate

---

### T-013: Playwright E2E — picker + settings + StatusBar full keyboard flow
**User Story**: US-001, US-002, US-003, US-004, US-006 | **Satisfies ACs**: AC-US1-01, AC-US2-04, AC-US3-02, AC-US4-03, AC-US6-01 (end-to-end coverage) | **Status**: [x] completed — e2e/agent-model-picker.spec.ts covers the three scenarios (Claude default, Cmd+K open, keyboard-only, StatusBar glyphs).
**Phase**: E | **Estimated**: 4h | **Test Level**: e2e (Playwright)
**Test Plan**:
  Given `e2e/agent-model-picker.spec.ts` boots the real eval-server + Studio SPA against a temp project fixture (with `.claude/skills/` pre-seeded and a fake `claude` binary shim), with fetch mocks or a real-enough test OpenRouter response (checked in as a fixture)
  When the test runs three scenarios
  Then — **Scenario 1 (Claude default)**: Studio opens → picker trigger shows `"Claude Code · Sonnet"` within 2s, no banner toast, no red error state anywhere; — **Scenario 2 (Unlock OpenRouter by key save, mouse path)**: user presses `Cmd+K` → picker opens → clicks OpenRouter row → right pane shows the empty-state CTA card (per AC-US3-04) → clicks `"Add API key →"` → Settings modal opens with OpenRouter tab focused and key input focused → pastes `"sk-or-test-xyz-1234"` → clicks Save → modal closes within 1s → toast visible → picker re-renders with OpenRouter now live and a brief flash → search input visible → types `"qwen"` → list filters → clicks first result → picker closes → top-rail trigger now shows `"OpenRouter · Qwen …"` → StatusBar OpenRouter glyph flipped from lock to unlock (asserted via screenshot or data-testid attribute); — **Scenario 3 (Same flow, keyboard only)**: fresh reload → `Cmd+K` → `↓ ↓ ↓` to land on OpenRouter → `Enter` on CTA (or `→ Enter` on the card button) → focus lands on OpenRouter key input → paste via keyboard (or `Cmd+V` against a clipboard stub) → Tab to Save → Enter → Tab back to picker → search input focused → type → Enter on first match → picker closes — the entire flow is completed in <15s with no console errors and no pointer events (verified via a Playwright pointer-event spy). Server log captured during the test contains only `"****1234"` (redacted) never the full key.
**Files**:
  - `repositories/anton-abyzov/vskill/e2e/agent-model-picker.spec.ts` (NEW)
  - `repositories/anton-abyzov/vskill/e2e/fixtures/fake-claude-binary.sh` (NEW, `chmod +x`)
  - `repositories/anton-abyzov/vskill/e2e/fixtures/openrouter-models.json` (NEW — frozen catalog snapshot)
  - `repositories/anton-abyzov/vskill/playwright.config.ts` (MOD if needed — add project fixture path)
**Dependencies**: T-001 through T-012
**Notes**: The fake `claude` binary shim is the same one built in T-003. The OpenRouter fixture is the response body from a real-world `GET /v1/models` captured at planning time, trimmed to ~50 entries for test speed.

---

### T-014: Docs (README compliance + ARCHITECTURE.md §5 env vars) + voice-lint sweep + coverage gate
**User Story**: US-005, US-007 | **Satisfies ACs**: AC-US5-03, AC-US7-02, AC-US7-03 | **Status**: [x] completed — README "## Claude Max/Pro subscription compliance" section added; ARCHITECTURE.md §5.1 env vars table + §5.2 compliance section added; docs.claude.com link present; OLLAMA_HOST example added.
**Phase**: E | **Estimated**: 2.5h | **Test Level**: docs-grep + CI
**Test Plan**:
  Given `README.md` and `docs/ARCHITECTURE.md` at the vskill repo root, plus the voice-lint and coverage scripts integrated into the existing quality pipeline
  When the docs-grep CI check and the voice-lint and coverage checks run after all prior tasks complete
  Then (a) `README.md` contains a section `## Claude Max/Pro subscription compliance` (exact heading) with the sentence *"vSkill Studio does not consume your Max/Pro subscription quota directly"* and a link to `https://docs.claude.com/en/docs/claude-code`; (b) `README.md` contains an Env Vars block referencing `OLLAMA_HOST` as recommended with precedence `OLLAMA_HOST > OLLAMA_BASE_URL > http://localhost:11434` and an example `OLLAMA_HOST=http://gpu-server:11434 npx vskill studio`; (c) `README.md` contains zero occurrences of `console.anthropic.com` (all replaced with `platform.claude.com/settings/keys`); (d) `docs/ARCHITECTURE.md` has a section `## 5. Environment Variables` containing a markdown table with columns `Variable | Default | Required | Read at (file:line) | Purpose`, with rows for `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`, `GOOGLE_API_KEY`, `OLLAMA_HOST`, `OLLAMA_BASE_URL`, `VSKILL_EVAL_PROVIDER`, `VSKILL_EVAL_MODEL`, and `CODEX_API_KEY`, all with file:line references verified to exist (grep-asserted); (e) voice-lint (extended in T-001) returns zero hits for `"Max/Pro"` or `"subscription"` in `src/eval-ui/src/**` and `src/eval-server/**` (excluding the whitelisted `"· subscription"` pricing suffix token); (f) Vitest coverage report shows ≥90% lines on new modules (`useAgentCatalog.ts`, `AgentModelPicker.tsx`, `AgentPane.tsx`, `ModelPane.tsx`, `LockedCta.tsx`, `SettingsModal.tsx`, `settings-store.ts`, `env.ts`, `ProvidersSegment.tsx`, `studio-json.ts`, `useVirtualList.ts`, `keyStore.ts`); (g) the bundle-grep compliance gate from T-003 still passes on the final build.
**Files**:
  - `repositories/anton-abyzov/vskill/README.md` (MOD)
  - `repositories/anton-abyzov/vskill/docs/ARCHITECTURE.md` (MOD — add §5)
  - `repositories/anton-abyzov/vskill/scripts/check-readme-env.sh` (NEW — grep-based CI helper)
  - `repositories/anton-abyzov/vskill/scripts/check-coverage-thresholds.sh` (NEW or MOD — enforce 90% on new modules)
**Dependencies**: T-001, T-002, T-003, T-013 (and all intervening tasks)
**Notes**: The coverage gate reads `coverage/coverage-summary.json` (Vitest output) and asserts `linesPct >= 90` for each listed module. If any existing coverage tooling is in place, extend it; don't duplicate.

---

## Summary

- **Total tasks**: 14
- **Target days**: 4
- **Phases**: A (3 tasks — server + env + compliance) → B (3 tasks — settings store + endpoints + modal) → C (4 tasks — catalog hook + panes + search + picker shell) → D (2 tasks — StatusBar + Claude default) → E (2 tasks — E2E + docs)
- **Test-level coverage**: 10 unit, 2 integration, 1 e2e, 1 docs-grep + coverage gate
- **Dependency graph**: Phase A independent; Phase B depends on nothing in A except T-001 (label); Phase C depends on T-005 + T-006 (endpoints + modal for CTA wiring); Phase D depends on T-006 + T-010; Phase E closes over everything.
- **Exit criteria** (all must be green to close 0682):
  - All 14 tasks `[x]`
  - Compliance unit test (T-003) passes
  - Bundle-grep gate passes (zero hits for `.claude/credentials|.claude/auth|.claude/token`)
  - Voice-lint passes (zero `Max/Pro` / `subscription` in picker/settings/StatusBar surfaces)
  - Playwright E2E (T-013) passes including keyboard-only run
  - README + ARCHITECTURE.md docs-grep passes
  - Coverage ≥90% on all new modules
