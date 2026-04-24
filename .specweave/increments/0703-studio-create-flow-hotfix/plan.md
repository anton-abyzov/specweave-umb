---
increment: 0703-studio-create-flow-hotfix
type: hotfix
status: ready_for_review
owner: sw:architect
mode: retrospective
---

# Implementation Plan: Skill Studio create-flow hotfix (retrospective)

## Overview

Six-bug hotfix to the Skill Studio "New Skill → Generate with AI" flow (shipped in vskill 0.5.98). All changes are surgical: no new modules, no protocol shifts, no schema migrations — just a new read-only GET endpoint, a lazy-loaded page reached through a hash-route takeover, and three small UI fixes (prefill, minHeight, resolved-alias). The plan below is retrospective — it explains *why* the shipped shape won out over the alternatives actually considered during implementation.

## Architecture Decision Log

### ADR-0703-01 — Duplicate pre-check via `GET /skill-exists` (not client-side plugin list)
- **Alternatives**: (a) fetch `/api/authoring/plugins` + filter locally; (b) attempt POST `/create-skill` and rely on the 409 it already returns.
- **Chosen**: new server endpoint `GET /api/authoring/skill-exists` that probes the filesystem directly.
- **Why**: Option (a) has a cache-invalidation window — the plugin list is paged + debounced, and a freshly authored skill wouldn't show up for ~60s; the list also doesn't expose standalone skills. Option (b) meant users had to invest a prompt before learning about the clash (that's literally the bug we were fixing). A single read-only GET gives server-authoritative truth with zero write surface. Validation logic (kebab regex, mode guards) is literally shared with the POST handler — both call `validateKebab()` and resolve via the same `skillDir` rules.
- **Cost**: one extra handler (~35 LOC), shared validator, no new tests infrastructure.

### ADR-0703-02 — `minHeight: ROW_HEIGHT` (not a variable-height row or a larger fixed `ROW_HEIGHT`)
- **Alternatives**: (a) bump `ROW_HEIGHT` to 72px for everyone; (b) measure each row and recompute `useVirtualList` offsets; (c) render `resolvedModel` lines outside the virtualised list.
- **Chosen**: keep `ROW_HEIGHT = 44` constant for the virtualiser and apply `minHeight: ROW_HEIGHT` on the row element itself so 3-line rows can grow naturally.
- **Why**: OpenRouter ships 300+ models and the virtualiser kicks in at `length >= 80` (see `useVirtualList`). Only claude-cli rows display the resolvedModel sub-line, and that list has exactly 3 models — always non-virtualised. So the expensive rows are always in the static branch where variable height is free. Options (a) and (b) would tax 300+ OpenRouter rows to help 3 Claude rows; (c) would duplicate rendering logic.
- **Cost**: a single style change + the in-code comment documenting the invariant (`ModelList.tsx:228-231`).

### ADR-0703-03 — Substring match on alias (not exact model-ID table)
- **Alternatives**: maintain a map `{ "claude-opus-4-7[1m]" → "opus", ... }` for exact resolvedModel → alias lookup.
- **Chosen**: `matchesResolvedAlias(modelId, resolvedModel)` — case-insensitive substring check (`resolvedModel.toLowerCase().includes(modelId.toLowerCase())`).
- **Why**: aliases are stable (`opus`, `sonnet`, `haiku` haven't changed since Claude 3), but concrete model IDs evolve every release (`claude-opus-4-6`, `claude-opus-4-7[1m]`, soon `4.8`). An exact table is a maintenance burden that quietly decays — and when it decays, the resolved hint silently disappears, which is exactly the symptom users already reported. Substring match stays correct without a human in the loop.
- **Cost**: 3 LOC, zero lookup table.

### ADR-0703-04 — Hash-route takeover via `useIsCreateRoute` hook (not a full `<Routes>`/`<Route>` tree)
- **Alternatives**: migrate all existing pages into a proper React Router v6 `<Routes>`/`<Route>` tree mounted at `/`.
- **Chosen**: `HashRouter` wrap in `main.tsx` + `useIsCreateRoute()` hook in `App.tsx` that returns a boolean; when true, `App` renders a `<Suspense>` boundary around a lazy `CreateSkillPage` and short-circuits the default Studio shell.
- **Why**: the full-Routes approach would require touching *every* existing page component (SkillDetailPage, BenchmarkPage, HistoryPage, etc.) that today reads from `useStudio()` state rather than route params. That's a multi-day refactor for zero user-visible benefit. The hook takeover adds ~15 LOC, keeps Studio-mode as the default, and avoids any behavioural change to the other pages. The trade-off — CreateSkillPage cannot share layout chrome with the rest of the Studio — is a non-issue because the Create flow is a full-page takeover by design.
- **Cost**: `HashRouter` wrap (`main.tsx:51-62`), 16-line hook + one conditional render in `App.tsx:52-67,335`, lazy `CreateSkillPage` import that also keeps home-page LCP flat.

## Component design

### Modal pre-check (ADR-0703-01)

```
CreateSkillModal                        eval-server
─────────────────                       ────────────
Click "Generate with AI"
  │
  ├─ routeToGenerator():
  │   setSubmitting(true)
  │   fetch(`/api/authoring/skill-exists?mode=&skillName=&pluginName=`)
  │                                       │
  │                                       ├─ validateKebab(skillName, pluginName?)
  │                                       ├─ resolve skillDir per mode
  │                                       ├─ (existing-plugin) check plugin manifest exists → 404 if not
  │                                       └─ return { exists: existsSync(skillDir), path }
  │   ◀────────────────────────────────────┘
  ├─ if exists: setError(`Skill '…' already exists at …`); return (no navigation)
  └─ else: window.location.assign(`/#/create?…`); onClose()
```

Call site: `CreateSkillModal.tsx:122-170`. Handler: `authoring-routes.ts:196-233`.

### Hash-route takeover (ADR-0703-04)

```
main.tsx              App.tsx                               CreateSkillPage
────────              ───────                               ───────────────
<HashRouter>          function useIsCreateRoute():          (lazy)
  <ThemeProvider>       read window.location.hash
    <App />             subscribe to `hashchange`
  </ThemeProvider>      → boolean
</HashRouter>
                      function Shell():
                        const onCreateRoute = useIsCreateRoute()
                        if (onCreateRoute):
                          return <Suspense fallback={…}>
                                   <CreateSkillPage />
                                 </Suspense>
                        return <StudioLayout …/>   (default)
```

Boundaries: `main.tsx:51-62` (router wrap), `App.tsx:48-50` (lazy import), `App.tsx:52-67` (hook), `App.tsx:335` (conditional render).

### Target-Agents scoping (shown ONLY when active agent ≠ claude-code)

```
CreateSkillPage mount
  │
  ├─ activeAgentId = getStudioPreference<string|null>("activeAgent", null)
  ├─ showTargetAgents = activeAgentId !== "claude-code"
  └─ JSX: `{showTargetAgents && installedAgents.length > 0 && <TargetAgentsSection />}`
```

Call site: `CreateSkillPage.tsx:125-126, 509`. Rationale: claude-code scope lives in `.claude/skills/` and targets Claude Code by definition — surfacing Cursor/Codex/Copilot rows is noise for that scope.

## API contract — `GET /api/authoring/skill-exists`

| Query param | Type | Notes |
|---|---|---|
| `mode` | `"standalone" \| "existing-plugin" \| "new-plugin"` | required |
| `skillName` | kebab-case string (2-64 chars, matches `/^[a-z][a-z0-9-]{0,62}[a-z0-9]$/`) | required |
| `pluginName` | same kebab regex | required when `mode !== "standalone"` |

| Status | Body | When |
|---|---|---|
| 200 | `{ exists: boolean, path: string }` | happy path — `path` is the absolute `skillDir` that was probed |
| 400 | `{ ok: false, code: "invalid-mode" \| "invalid-skill-name" \| "invalid-plugin-name", error }` | input validation |
| 404 | `{ ok: false, code: "plugin-not-found", error }` | `mode = existing-plugin` and plugin manifest is absent |

Read-only. Reuses the validator from the POST handler. Skill dir resolved via the same `join(root, "skills", skillName)` / `join(root, pluginName, "skills", skillName)` rules — no new path-resolution logic.

## Testing architecture

**18 unit tests (Vitest + jsdom) across 4 files:**

| File | Tests | AC trace |
|---|---|---|
| `eval-ui/src/components/__tests__/CreateSkillModal.0703.test.tsx` | 2 | AC-US2-01 (pre-check blocks nav on `exists: true`), AC-US2-02 (happy path navigates to `/#/create`) |
| `eval-ui/src/components/__tests__/ModelList.0703.test.tsx` | 4 | AC-US3-01 (resolved line shows for opus/sonnet/haiku), AC-US3-02 (no spill into neighbour), AC-US3-03 (substring match case-insensitive), AC-US3-04 (no resolved line for non-claude-cli) |
| `eval-ui/src/pages/__tests__/CreateSkillPage.prefill.test.tsx` | 3 | AC-US1-01 (skillName/mode/pluginName/description decoded from query string), AC-US1-02 (prompt textarea reflects description), AC-US1-03 (missing params → empty form, no crash) |
| `eval-ui/src/pages/__tests__/CreateSkillPage.targetAgents.test.tsx` | 3 | AC-US5-01 (hidden when activeAgent=claude-code), AC-US5-02 (shown for non-claude agents), AC-US5-03 (default/null preference shows section) |

**6 integration tests** appended to `eval-server/__tests__/authoring-routes.test.ts` under the existing `describe("0703 — GET /api/authoring/skill-exists")` block: happy-miss, happy-hit (scaffold then re-probe), existing-plugin success, plugin-not-found (404), invalid-skill-name (400), invalid-mode (400) — trace to AC-US2-01 and the API contract above.

Pre-existing tests (modal create-skill POST, picker persistence) keep covering the non-hotfix surface — not re-enumerated here.

## Non-functional notes

- **Accessibility** — No regressions. `ModelRow` keeps `role="option"`, `aria-selected`, `data-testid`. The hash-takeover renders a standard `<Suspense>` boundary with a `role="status"` fallback. Modal error surfacing is the existing inline `role="alert"` — unchanged.
- **Performance** — `CreateSkillPage` is now lazy-loaded, so the home route bundle shrinks (home-page LCP is flat or slightly better). The `skill-exists` probe is one fetch on modal submit (user action) — zero background polling. Virtualiser math (`ROW_HEIGHT = 44`) unchanged; `minHeight` only affects the 3 non-virtualised claude-cli rows.
- **Security** — `skill-exists` is read-only (`existsSync`, no fs writes, no shell). Same kebab validator as the POST handler rejects path-traversal attempts (`../`, absolute paths, whitespace). `pluginName` is constrained to the same regex — the `join(root, pluginName, …)` call cannot escape `root`.
- **Rollback** — Revert is trivial: remove `HashRouter` + `useIsCreateRoute` + the three UI hunks, drop `makeSkillExistsHandler` registration. No persisted state or schema is affected.

## Related ADRs

- `adr/0698-01-skillscope-five-value-union.md` — scope taxonomy that `activeAgent === "claude-code"` branches on.
- `adr/0678-skill-gen-source-model-picker.md` — originating picker this flow extends.
- `adr/0698-03-plugin-cache-version-segment.md` — plugin path layout that `skill-exists` mirrors.
