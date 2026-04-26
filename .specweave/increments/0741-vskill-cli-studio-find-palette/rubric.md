---
increment: 0741-vskill-cli-studio-find-palette
title: "vskill CLI Studio Find Palette"
generated: 2026-04-26
source: derived-from-spec
---

# Quality Contract

This rubric is the per-increment quality contract consumed by closure gates (`sw:code-reviewer`, `/simplify`, `sw:grill`, `sw:judge-llm`, `sw:done`). It is derived from the user stories and ACs in `spec.md`.

## Functional acceptance (from spec.md)

- [ ] **Palette discovery (US-001, US-002)**: ⌘⇧K (Mac) / Ctrl+Shift+K (Win/Linux) opens the FindSkillsPalette from any view in eval-ui. The TopRail "Find skills" button opens the same palette via `openFindSkills` CustomEvent. Existing ⌘K (CommandPalette) and ⌘P (ProjectCommandPalette) bindings continue to work without regression.
- [ ] **Search UX parity (US-003)**: 150ms debounce, 60s SWR cache, AbortController cancellation, IntersectionObserver pagination (10-page hard cap), trending fallback for empty queries, full keyboard navigation (↑↓ Enter Esc + type-to-search), MiniTierBadge / BLOCKED / TAINTED inline.
- [ ] **Detail view (US-004)**: In-eval-ui lazy-loaded panel renders skill metadata (TrustBadge, TierBadge, RepoLink, RepoHealthBadge, TaintWarning), last 5 versions (newest first, default = latest), TerminalBlock install command swapped per selected version, Copy → clipboard + toast, blocked-skill panel swap, Back-to-results restores previous query from sessionStorage.
- [ ] **Proxy extension (US-005)**: `shouldProxyToPlatform()` matches `/api/v1/skills/*`, `/api/v1/studio/search`, `/api/v1/studio/telemetry/`, and `/api/v1/stats`. Default upstream is `https://verified-skill.com`, overridable via `VSKILL_PLATFORM_URL`. Fire-and-forget telemetry POSTs MUST NOT block UI on failure.

## Non-functional requirements (from spec.md FRs)

- [ ] **FR-001 A11y WCAG 2.1 AA**: visible focus, non-color-only state indicators, contrast ≥ 4.5:1 / 3:1, focus trap + restoration on overlay open/close. Verified by `@axe-core/playwright` with zero serious/critical violations.
- [ ] **FR-002 Keyboard-completable**: every flow works without a mouse — palette open via ⌘⇧K, navigate with ↑↓, activate with Enter, close with Esc; detail panel Tab order back → versions → copy.
- [ ] **FR-003 Reduced motion**: `prefers-reduced-motion: reduce` collapses palette open/close transitions to static fade, disables shortcut-hint pulse, disables toast slide-in.
- [ ] **FR-004 Telemetry fire-and-forget**: all POSTs use `keepalive: true`, are not awaited; failures (network, 4xx, 5xx) silently swallowed in production (no `console.error`).
- [ ] **FR-005 Theme parity**: light + dark themes verified via existing CSS variable tokens; no hard-coded `#000` / `#fff` outside TerminalBlock.
- [ ] **FR-006 Bundle-size budget**: `dist/eval-ui` gzip delta < 50KB after the change; FindSkillsPalette + SkillDetailPanel both lazy-loaded.

## Performance budgets (from spec.md)

- [ ] Palette open: < 100ms warm from event to first paint.
- [ ] Search results visible: < 350ms p95 cache-warm.
- [ ] Detail panel TTFB: < 600ms p95 cache-warm.

## Test coverage (TDD)

- [ ] Every AC has a Given/When/Then test plan in tasks.md and a corresponding Vitest or Playwright test in code (RED → GREEN → REFACTOR).
- [ ] Vitest unit coverage ≥ 90% on new components (palette shell, SearchPaletteCore, NavButton, DetailPanel).
- [ ] Vitest integration coverage on `platform-proxy.test.ts` for the 3 new prefixes (positive + negative).
- [ ] Playwright E2E covers the full happy path: open palette → search → select → copy → toast.
- [ ] Regression test: ⌘K and ⌘P still open their respective existing palettes.

## Security

- [ ] Skill identifier sanitized with `^[a-zA-Z0-9._@/-]+$` before injection into install command (matches 0717 contract).
- [ ] Search highlight rendering uses `sanitize-html` helper — XSS-safe.
- [ ] No PII in telemetry payloads (only `skillName`, `q`, `version`, `ts`).
- [ ] Hop-by-hop headers stripped per RFC 2616 §13.5.1 (existing platform-proxy behavior preserved).

## Architecture compliance

- [ ] Browser → localhost only — no direct cross-origin calls to `verified-skill.com` (per `project_studio_cors_free_architecture` memory). All upstream calls go through `eval-server` proxy.
- [ ] No platform-side changes — increment is purely a consumer extension.
- [ ] Component ports do not introduce `next/*` imports into eval-ui.
- [ ] New CustomEvent name (`openFindSkills`) does not collide with existing `openSearch` (CommandPalette) or `studio:*` (StudioContext) events.

## Closure gates (executed by `sw:done`)

- [ ] `sw:code-reviewer` → `code-review-report.json` with 0 critical/high/medium findings (fix loop, max 3 iterations).
- [ ] `/simplify` → 3-parallel-agent review passes; flagged duplication / inefficiencies addressed.
- [ ] `sw:grill` → `grill-report.json` written; concerns addressed or explicitly waived.
- [ ] `sw:judge-llm` → `judge-llm-report.json` written; consent given (or waiver recorded).
- [ ] `sw:validate` → 130+ rule checks pass.
- [ ] All `tasks.md` tasks marked `[x]`; all `spec.md` ACs marked `[x]`.
- [ ] `npx vitest run` and `npx playwright test` both pass.
