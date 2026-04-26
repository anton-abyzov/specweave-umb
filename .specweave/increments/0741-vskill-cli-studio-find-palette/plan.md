---
increment: 0741-vskill-cli-studio-find-palette
title: "vskill CLI Studio Find Palette — Architecture"
type: feature
created: 2026-04-26
---

# Plan: vskill CLI Studio Find Palette

## Design

### Two-surface architecture

The change touches **two surfaces** in the same `vskill` package:

```
┌──────────────────────────────────────────────────────────────────────┐
│ vskill/src/eval-ui  (browser, React+Vite, dist/eval-ui bundle)       │
│                                                                      │
│  App.tsx                                                             │
│   ├─ TopRail                                                         │
│   │   └─ FindSkillsNavButton  (NEW — button + ⌘⇧K hint)              │
│   │                                                                  │
│   ├─ <Suspense> + <FindSkillsPalette>  (NEW, lazy)                   │
│   │   ├─ SearchPaletteCore (port of platform SearchPalette.tsx)      │
│   │   ├─ MiniTierBadge, TaintWarning  (ported)                       │
│   │   └─ onSelect → opens SkillDetailPanel                           │
│   │                                                                  │
│   ├─ <Suspense> + <SkillDetailPanel>  (NEW, lazy)                    │
│   │   ├─ TrustBadge, TierBadge, RepoLink, RepoHealthBadge,           │
│   │   │  TaintWarning, SectionDivider, TerminalBlock  (ported)       │
│   │   └─ Versions list (last 5) + Copy install command + Toast       │
│   │                                                                  │
│   └─ Global keydown listener: ⌘⇧K / Ctrl+Shift+K → openFindSkills    │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              │  fetch /api/v1/studio/search
                              │  fetch /api/v1/stats
                              │  fetch /api/v1/skills/<owner>/<repo>/<skill>[/versions]
                              │  POST  /api/v1/studio/telemetry/<kind>
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ vskill/src/eval-server  (Node http on hashed port, e.g. 3162)        │
│                                                                      │
│  eval-server.ts:132 — router miss → shouldProxyToPlatform(req.url)?  │
│   yes → proxyToPlatform(req, res)                                    │
│   no  → static-serve dist/eval-ui                                    │
│                                                                      │
│  platform-proxy.ts                                                   │
│   ├─ shouldProxyToPlatform(url):                                     │
│   │     /api/v1/skills/*           (existing, unchanged)             │
│   │     /api/v1/studio/search      (NEW)                             │
│   │     /api/v1/studio/telemetry/  (NEW)                             │
│   │     /api/v1/stats              (NEW)                             │
│   ├─ getPlatformBaseUrl()                                            │
│   │     env VSKILL_PLATFORM_URL                                      │
│   │     default https://verified-skill.com                           │
│   └─ proxyToPlatform()                                               │
│         req.pipe(upstreamReq)  (body stream)                         │
│         upstreamRes.pipe(res)  (SSE-safe)                            │
│         strip hop-by-hop headers per RFC 2616 §13.5.1                │
│         502 envelope on upstream failure                             │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    https://verified-skill.com
                  (or http://localhost:3017 for dev)
```

### Component layout

New tree under `vskill/src/eval-ui/src/components/FindSkillsPalette/`:

```
FindSkillsPalette/
├── FindSkillsPalette.tsx           # Lazy-loaded shell — manages open state, mounts overlay
├── SearchPaletteCore.tsx           # Port of platform SearchPalette.tsx (680 LOC)
├── FindSkillsNavButton.tsx         # TopRail button with shortcut-hint badge
├── SkillDetailPanel.tsx            # Detail view with version selector + install panel
├── components/
│   ├── MiniTierBadge.tsx           # Ported from vskill-platform
│   ├── TrustBadge.tsx              # Ported
│   ├── TierBadge.tsx               # Ported
│   ├── RepoLink.tsx                # Ported (next/link → <a>)
│   ├── RepoHealthBadge.tsx         # Ported
│   ├── TaintWarning.tsx            # Ported
│   ├── SectionDivider.tsx          # Ported
│   └── TerminalBlock.tsx           # Ported
├── lib/
│   ├── sanitize-html.ts            # Copy of vskill-platform/src/lib/sanitize-html
│   └── skill-url.ts                # Copy of vskill-platform/src/lib/skill-url (next/link removed)
└── __tests__/
    ├── FindSkillsPalette.test.tsx
    ├── SearchPaletteCore.test.tsx
    ├── FindSkillsNavButton.test.tsx
    └── SkillDetailPanel.test.tsx
```

### State and event flow

- **Cross-component triggering**: a new `window.openFindSkills` `CustomEvent` opens the palette. The naming intentionally avoids the existing `openSearch` event used by `CommandPalette` to prevent dual-listener firing.
- **Open state**: managed inside `FindSkillsPalette.tsx` (local `useState` + the global keydown listener installed in `App.tsx`). No need to extend `StudioContext` for a single boolean.
- **Selected skill (palette → detail)**: passed via internal callback prop. `SkillDetailPanel` opens in response to `onSelect` from `SearchPaletteCore`. When the panel closes, focus returns to the palette and the previous query is restored from `sessionStorage` key `find-skills:last-query`.
- **Toast on copy**: dispatched via the existing `ToastProvider` (already mounted at App root, used elsewhere via `studio:toast` CustomEvent).

### Proxy extension

The single change in `vskill/src/eval-server/platform-proxy.ts`:

```ts
// BEFORE (line 84-86)
export function shouldProxyToPlatform(url: string): boolean {
  return url.startsWith("/api/v1/skills/");
}

// AFTER
const PROXY_PREFIXES = [
  "/api/v1/skills/",
  "/api/v1/studio/search",
  "/api/v1/studio/telemetry/",
  "/api/v1/stats",
] as const;

export function shouldProxyToPlatform(url: string): boolean {
  return PROXY_PREFIXES.some(p => url.startsWith(p));
}
```

Everything else in `platform-proxy.ts` (`getPlatformBaseUrl`, `proxyToPlatform`, hop-by-hop stripping, 502 envelope) is unchanged. The integration point at `eval-server.ts:132-135` already invokes `shouldProxyToPlatform()` → `proxyToPlatform()`, so no eval-server changes.

### Build pipeline

- `npm run build:eval-ui` (existing) bundles `src/eval-ui` → `dist/eval-ui`. The new `FindSkillsPalette` and `SkillDetailPanel` are lazy-loaded (`React.lazy` + dynamic `import()`), so they ship as separate chunks and do NOT bloat the initial bundle.
- Post-build size check: `dist/eval-ui` total gzip delta < 50KB. Implement as a Vitest test that compares pre/post `gzipSync` sizes (or a shell script in CI).

### Tests

- **Unit (Vitest)**:
  - `FindSkillsPalette.test.tsx` — opens on `openFindSkills`, opens on ⌘⇧K, closes on Esc, does NOT open on bare ⌘K.
  - `SearchPaletteCore.test.tsx` — debounce timing (mock `useFakeTimers`), AbortController cancellation on re-query, trending fetch on empty query, IntersectionObserver page-append, sanitize-html output.
  - `FindSkillsNavButton.test.tsx` — dispatches `openFindSkills` on click, renders ⌘⇧K vs Ctrl+Shift+K based on `navigator.platform`, ARIA label correct, no pulse under reduced-motion.
  - `SkillDetailPanel.test.tsx` — renders all 5 versions, install command swaps when non-latest version selected, `isBlocked` swaps in blocked panel, sanitization rejects bad identifiers, Copy writes to clipboard + dispatches toast, Esc closes + restores palette.
- **Integration (Vitest)**:
  - Extend `vskill/src/eval-server/platform-proxy.test.ts` with positive matches for the 3 new prefixes and negative matches for `/api/skills` (no `/v1/`) and `/api/v1/foo`.
- **E2E (Playwright)**:
  - New spec under `vskill/src/eval-ui/playwright/find-skills.spec.ts`. Boots eval-server, opens eval-ui, presses ⌘⇧K, types "obsidian", waits for results, clicks first, verifies detail panel renders, clicks Copy, verifies clipboard contents and toast.

## Rationale

### Why port instead of iframe / link-out?

Three options were considered (asked in plan-mode AskUserQuestion):

1. **Open verified-skill.com in browser** — smallest scope (~1-2 days). Loses the "never leave Studio" promise; jarring context switch; loses opportunity to wire vskill-install actions deeper later.
2. **Hybrid (inline copy command, link out for full detail)** — medium scope. Splits UX across two surfaces, which is worse than fully one or fully the other.
3. **Inside eval-ui (chosen)** — heaviest scope (~4-5 days, 18-25 tasks). Cohesive UX, no context switch, sets up future install-from-Studio flows. Mitigated by porting near-verbatim from a working source rather than designing from scratch.

The user picked option 3 explicitly. The cost is borne by porting effort; risk is mitigated because the source SearchPalette and detail components have battle-tested behavior on production verified-skill.com.

### Why ⌘⇧K instead of ⌘K?

eval-ui already binds:
- ⌘K → `CommandPalette` (project switcher / fuzzy search of LOCAL skills)
- ⌘P → `ProjectCommandPalette` (project picker)

Three options were considered:

1. **⌘⇧K (chosen)** — keeps both existing palettes intact; no regression; small UX cost (one more shortcut to learn). Mac convention for "shifted variant" is widespread (e.g., ⌘T new tab vs ⌘⇧T reopen tab).
2. **Reuse ⌘K with a unified palette** — would require refactoring `CommandPalette` into a sectioned palette (Local / Marketplace / Project). Larger scope, higher risk, regresses the focused fast-fuzzy-search of locals.
3. **⌘/** — works but is less discoverable (no widely-known convention).

⌘⇧K respects the principle of least surprise: existing muscle memory works unchanged.

R-02 calls out that some Chrome builds bind ⌘⇧K to a DevTools function. If empirically confirmed during implementation, fall back to ⌘⌥K and update the badge — captured as a contingency, not a blocker.

### Why extend platform-proxy instead of adding a new proxy module?

`platform-proxy.ts` is already battle-tested for SSE, hop-by-hop stripping, body streaming, and 502 envelopes. Per memory `project_studio_cors_free_architecture`, the architecture rule is "browser → localhost only", and the existing proxy is the canonical chokepoint. Adding a second proxy module would split that chokepoint, making auditing harder. The change is a one-line predicate edit; the rest of the proxy machinery is reused unchanged.

### Why a new event name (`openFindSkills`) instead of reusing `openSearch`?

The `CommandPalette` in eval-ui already listens for `openSearch` (per Explore agent finding). If both palettes listen for the same event, both would open simultaneously — visually broken. Using a distinct event name (`openFindSkills`) keeps each palette's contract independent. The platform's `FindNavButton` uses `openSearch` because the platform context has only one search palette to open.

### Why pure-React component ports (no abstraction layer)?

The 8 detail components (TrustBadge, TierBadge, etc.) are small (avg ~60 LOC each) and have no Next.js dependencies except `next/link` in `RepoLink` (replaced with `<a>`). Building a shared `@vskill/ui` package would add 2-3 days of build-system work for ~500 LOC of leaf components. Direct copy is 30 minutes per component, with diff-based maintenance going forward. A shared package can be revisited later if more surfaces start sharing components.

### Why no platform-side changes?

Per Explore subagent: every endpoint the palette + detail view need is already shipped:
- `/api/v1/skills/search` (general)
- `/api/v1/studio/search` (rate-limit-isolated for studio traffic, shipped in 0716)
- `/api/v1/stats` (trending)
- `/api/v1/studio/telemetry/[kind]` (search-select, install-copy)
- `/api/v1/skills/[owner]/[repo]/[skill]` and `.../versions`

This increment is purely a consumer extension. Platform stays untouched.

## ADR References

No new ADRs required. The change is a tactical port with a one-line proxy extension. Existing relevant context:
- `project_studio_cors_free_architecture` memory — codifies the browser→localhost rule that this increment honors.
- `project_vskill_studio_runtime` memory — codifies the eval-server vs Vite-dev distinction that motivates this increment's existence.

If implementation surfaces a need to formalize the "ported component" pattern across surfaces, an ADR can be created in a follow-up increment.

## Open Questions (deferred to implementation)

- **Q1**: Should the version list show the publisher's avatar next to author email? Source `vskill-platform` shows author email only — match unless visual review surfaces a need.
- **Q2**: Should "see all on verified-skill.com" link be `target="_blank"` or open in the user's default browser via `shell.openExternal` (Electron-style)? eval-ui runs in regular browsers, so `target="_blank"` is correct. Confirm.
- **Q3**: Should we record telemetry locally (eval-server log) in addition to forwarding upstream? Out of scope — fire-and-forget upstream only, per FR-004.
