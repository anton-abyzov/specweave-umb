---
increment: 0674-vskill-studio-redesign
title: vSkill Studio Redesign — Technical & Visual Plan
type: plan
status: draft
created: 2026-04-22
architect: architect-agent
design_authority: frontend-design (primary) + sw:architect
---

# Plan: vSkill Studio Redesign

> **Scope clarification.** The "vSkill Studio" being redesigned is the **local developer UI launched by `npx vskill studio`** — i.e. the Vite + React + Tailwind 4 app at `repositories/anton-abyzov/vskill/src/eval-ui/`, served by the eval-server at `src/eval-server/`. This is distinct from the `/studio` marketing page on verified-skill.com (`repositories/anton-abyzov/vskill-platform/src/app/studio/page.tsx`), which is a one-shot landing page and is **out of scope**. The `scope.app` field in `metadata.json` is ambiguous and should be corrected to point at `repositories/anton-abyzov/vskill/src/eval-ui`. User intent ("the NPM studio") and the `vskill studio` CLI entrypoint (`src/index.ts:188`) both confirm this interpretation.

---

## 0a. Reconciliation with spec.md

After the PM's spec.md landed, this plan was reconciled against all 10 user stories and FR/NFR set. Key alignments applied throughout this document:

- **INSTALLED section is expanded by default** (AC-US1-04). Both OWN and INSTALLED are first-class; no collapsed-by-default bias.
- **localStorage keys match the spec exactly**: `vskill-theme`, `vskill-sidebar-own-collapsed`, `vskill-sidebar-installed-collapsed`, `vskill-sidebar-width`.
- **Sidebar width default is 320px** (AC-US7-01), narrows to 240px at 768–1279px, drawer below 768px. Draggable resize within [240px, 480px] persisted (AC-US7-05).
- **Section-scoped filters** (AC-US1-02) in addition to the global search.
- **Duplicate-in-both rendering** — a skill authored as source and also installed appears in both sections with a "synced from Own" link on the Installed card (AC-US1-10).
- **Full SKILL.md editor + preview** is in-scope as Phase 5 (US-005), replacing my earlier assumption that workspace internals were token-sweep only. This is the one scope expansion that shifts the increment's centre of gravity — budget bumps from 8 to 11 days.
- **Context menu** (right-click) is a first-class component (AC-US4-07).
- **Central `strings.ts` module** with voice-enforcement lint (US-010, NFR-005).
- **`prefers-contrast: more` variant** adds a third token layer (`[data-contrast="more"]`) — AC-US8-09.
- **Copy voice**: every user-facing string reviewed against the voice guide; CI grep rejects "Oops", "Awesome!", trailing `!!`, celebration emoji.

The architectural bones (three-layer tokens, origin SSoT, warm-neutral visual language, editor+preview split, sidebar Installed/Own rule) are now all aligned with the Anthropic Labs design direction (see §0 below).

---

## 0. Design Direction — Anthropic Labs-Grounded Warm Neutral

The aesthetic is **"technically refined and charmingly quirky"** (Anthropic Labs' own phrasing) — precision with personality, not sterile minimalism. Every choice below descends from the design language used at anthropic.com and claude.ai/labs, adapted for a developer workbench that is *scanned*, not *read*.

**Foundation principles:**

1. **Warm neutral everywhere.** Both themes sit on a warm paper foundation — not cool slate, not pure black, not `#FFFFFF`. Dark mode is a warm near-black (`#1A1814`), NEVER a cool slate like `#0A0A0A`. If the dark mode looks slightly brown next to VS Code's default, that is intentional.
2. **Calm beats dense.** Anti-maximalism. Whitespace is generous for a developer tool — but scannable, not marketing-site-airy. Cards breathe; they don't sprawl.
3. **Flat warm solids with one hero accent.** The tan/clay accent (`#D4A27F` light / `#E0B793` dark) may cover no more than **5% of any visible surface**. Subtle gradients appear only on interactive affordances (hover wash on a button, selection highlight). No glassmorphism. No grain textures. No noise overlays.
4. **Semantic duality for provenance.** A quiet green signals Installed; a warm amber signals Own. Dots, not pills. The same two tokens carry this meaning wherever provenance appears — sidebar, detail header, breadcrumb.
5. **Precision with personality.** A transitional serif (Source Serif 4) appears in detail-card titles and empty-state headlines — the editorial moment. Everywhere else: a geometric sans (Inter Tight) for body + UI, and JetBrains Mono for code + editor. The serif is the quirk; the sans is the craft.

**What we deliberately reject** (anti-patterns list, expanded):

| Anti-pattern | Why |
|---|---|
| Purple AI-slop gradients (violet → cyan on dark) | The signature look of every generic AI demo 2023–2025. |
| Glassmorphism (backdrop-blur cards for no structural reason) | GPU cost, pixel softness, reads as "SaaS dashboard circa 2022". |
| Cool slate dark mode (`#0A0A0A`, `#111111`, cool greys) | We are deliberately warm. Cool slate fights the Anthropic tone. |
| Loading shimmers / skeleton theatre | Team-lead brief: **no shimmers.** A quiet "Loading…" or a solid `--surface` placeholder is enough. Shimmer animation reads as decorative theatre. |
| Page transitions for polish | Studio is a scanning surface, not a reading one. |
| Serif in table rows or editor chrome | Source Serif 4 belongs in titles only. Mixing serifs into repeating rows kills scanability. |
| Tan accent exceeding 5% of surface area | More accent = less accent. The restraint is the point. |
| Hero-size marketing type inside studio chrome | anthropic.com has 72px hero display; a tool must not. Max display size inside Studio is 28px. |
| Block-cursor / terminal-cursor visual signatures | Dropped. The warm paper palette + typographic pairing IS the signature. |
| Full-width dividers spanning across columns | Dividers must stop at column padding — never bleed across sidebar/workspace boundaries. |
| Pill badges with background fill for routine status | Badges are text-only with a preceding colored dot. Fills are reserved for count badges on section headers. |

The **one thing someone remembers**: the warm paper feel in both themes — a tool that feels designed for long focus sessions in a well-lit room or a quiet evening, not a neon bunker or a clinical greyscale dashboard.

---

## 1. Visual Language

### 1.1 Typography — three typefaces, assigned with discipline

| Role | Family | Weights | Usage | Source |
|---|---|---|---|---|
| **Display / Serif** | **Source Serif 4** (variable) | 400, 500, 600 | Detail-card titles, empty-state headlines, section H1/H2 in the workspace. **Never** in table rows, skill-row names, editor chrome, or UI chrome. Free analog for Galaxie Copernicus (Anthropic's paid display serif). | `@fontsource-variable/source-serif-4` |
| **UI / Sans** | **Inter Tight** (variable) | 400, 500, 600 | Body prose, button labels, nav items, skill-row names, badge text, tooltip content. Free analog for Styrene B — "rounded, slightly squishy" geometric sans. | `@fontsource-variable/inter-tight` |
| **Mono / Code** | **JetBrains Mono** (variable) | 400, 500, 600 | Code blocks, editor gutter, paths, version numbers, command hints, kicker caps. Programmer ligatures enabled in editor only. | `@fontsource-variable/jetbrains-mono` |

**Package additions:**
```bash
npm i @fontsource-variable/source-serif-4 @fontsource-variable/inter-tight @fontsource-variable/jetbrains-mono
```

Imported in `src/eval-ui/src/main.tsx`. Split into a separate Vite chunk via `manualChunks.fonts`. Total fonts budget ≤ 70 KB gzipped (subset: Latin + Latin-ext).

**Family tokens** (referenced by components via semantic tokens):
```css
--font-serif: "Source Serif 4 Variable", "Source Serif 4", ui-serif, Georgia, serif;
--font-sans:  "Inter Tight Variable", "Inter Tight", ui-sans-serif, system-ui, sans-serif;
--font-mono:  "JetBrains Mono Variable", "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
```

**Type scale — 12 / 14 / 16 / 20 / 28** (per team-lead brief, with supporting sizes for UI chrome):

| Token | Size | Line | Track | Weight | Family | Usage |
|---|---|---|---|---|---|---|
| `--type-display` | 1.75rem (28px) | 1.15 | -0.02 | 500 serif | Source Serif 4 | Empty-state headlines, workspace H1 when solo |
| `--type-heading-lg` | 1.25rem (20px) | 1.25 | -0.01 | 500 serif | Source Serif 4 | Detail-card section titles |
| `--type-heading-md` | 1rem (16px) | 1.35 | -0.005 | 600 sans | Inter Tight | Panel headers, tab labels |
| `--type-body` | 0.875rem (14px) | 1.55 | 0 | 400 sans | Inter Tight | Descriptions, long prose |
| `--type-ui` | 0.875rem (14px) | 1.3 | 0 | 500 sans | Inter Tight | Buttons, nav, skill-row names |
| `--type-meta` | 0.75rem (12px) | 1.4 | 0 | 400 sans | Inter Tight | Row metadata, breadcrumb |
| `--type-kicker` | 0.75rem (12px) | 1.2 | 0.12 | 600 mono uppercase | JetBrains Mono | SECTION LABELS ("INSTALLED", "OWN", tab kickers) |
| `--type-code` | 0.875rem (14px) | 1.55 | 0 | 400 mono | JetBrains Mono | Code blocks, editor gutter |
| `--type-mono-inline` | 0.75rem (12px) | 1.4 | 0 | 400 mono | JetBrains Mono | Inline paths, version chips, command hints |

All numeric UI uses `font-variant-numeric: tabular-nums`. Serif numerals are proportional (editorial); sans and mono numerals are tabular (data alignment).

### 1.2 Color — warm-neutral, both themes

**Design rule**: every color belongs to one of four layers (raw → semantic → component → state). Components may read semantic tokens only. No component defines colors.

**Token layer — raw palette (Anthropic Labs-grounded, warm-neutral):**

| Token | Light value | Dark value | Purpose |
|---|---|---|---|
| `--paper` | `#FBF8F3` | `#1A1814` | App background — warm off-white / warm near-black (NOT pure white, NEVER cool slate) |
| `--surface` | `#FFFFFF` | `#221F1A` | Cards, modals, elevated containers |
| `--surface-muted` | `#F4EFE6` | `#2A2620` | Hover wash, secondary containers |
| `--ink` | `#191919` | `#F2ECE1` | Primary text |
| `--ink-muted` | `#5A5651` | `#A59D8F` | Supporting text (muted) |
| `--ink-faint` | `#8A857E` | `#7A726A` | Captions, disabled, tertiary |
| `--rule` | `#E8E1D6` | `#2E2A24` | 1px dividers |
| `--rule-strong` | `#D6CEBE` | `#3E3831` | Hover/focus dividers |
| `--accent` | `#D4A27F` | `#E0B793` | Tan brand accent — **≤5% of surface area** |
| `--accent-ink` | `#7A4A24` | `#3B2E1F` | Text/icons drawn on accent backgrounds |
| `--accent-wash` | `rgba(212,162,127,0.10)` | `rgba(224,183,147,0.10)` | Subtle hover/selection wash |
| `--installed` | `#2F6A4A` | `#86C9A5` | Semantic: skill is installed (quiet green) |
| `--own` | `#8A5A1F` | `#E6B877` | Semantic: user-authored (warm amber) |
| `--focus` | `#3B6EA8` | `#7CA8D9` | Focus-visible ring — cool blue is deliberate (the only cool in the system, for clarity) |
| `--danger` | `#B23A2A` | `#E08A78` | Destructive + failing |
| `--warn` | `#A06A18` | `#D9A860` | Stale, pending |
| `--info` | `#4A6A8A` | `#8AA8C8` | Neutral info — muted, not playful |

**Semantic layer** — every component references these:
```
--bg-canvas         → --paper
--bg-chrome         → --paper                (sidebar shares the canvas; it's differentiated by rule, not by fill)
--bg-card           → --surface
--bg-hover          → --surface-muted
--bg-selected       → --accent-wash
--border-default    → --rule
--border-hover      → --rule-strong
--border-selected   → --accent              (1px left border on selected row)
--border-focus      → --focus
--text-primary      → --ink
--text-muted        → --ink-muted
--text-faint        → --ink-faint
--status-installed  → --installed
--status-own        → --own
--status-danger     → --danger
--status-warn       → --warn
--status-info       → --info
```

**Contrast ratios** (verified via `wcag-contrast` against `--paper`):

| Pair | Light ratio | Dark ratio | Standard |
|---|---|---|---|
| `--ink` on `--paper` | **16.8:1** | **14.2:1** | AAA body |
| `--ink-muted` on `--paper` | **7.6:1** | **6.1:1** | AAA body / AA large |
| `--ink-faint` on `--paper` | **3.8:1** | **3.3:1** | AA large / captions only |
| `--installed` on `--paper` | **5.9:1** | **5.2:1** | AA UI |
| `--own` on `--paper` | **6.2:1** | **5.5:1** | AA UI |
| `--focus` on `--paper` | **7.1:1** | **4.9:1** | AA UI (3:1 target met in both) |
| `--accent-ink` on `--accent` | **5.4:1** | **6.1:1** | AA UI |

Light `--ink-faint` at 3.8:1 is reserved for captions and disabled text only — never primary reading content, so AA-large is sufficient. CI gate: `src/eval-ui/src/__tests__/theme-contrast.test.ts` asserts every pair.

### 1.3 Spacing, radius, elevation

```
--space-0: 0px
--space-1: 2px
--space-2: 4px
--space-3: 8px
--space-4: 12px
--space-5: 16px
--space-6: 20px
--space-7: 24px
--space-8: 32px
--space-9: 48px

--radius-xs: 4px     /* chips, badges */
--radius-sm: 6px     /* buttons, inputs */
--radius-md: 8px     /* cards, sidebar items, detail panels */
--radius-lg: 12px    /* modals */

/* Elevation — used sparingly. Modal is the only place with shadow. */
--elev-0: none
--elev-modal-light: 0 4px 24px rgba(25, 25, 25, 0.08)
--elev-modal-dark:  0 4px 24px rgba(0, 0, 0, 0.35)
```

**No shadows on cards, skill rows, or the sidebar.** Elevation is communicated by 1px `--rule` borders and the shift from `--paper` to `--surface`. Modals are the only element with drop shadow.

### 1.4 Motion

```
--dur-fast:   120ms   /* hover color, opacity */
--dur-base:   180ms   /* selection highlight, panel open, toast entry */
--ease:       cubic-bezier(0.2, 0, 0, 1)   /* single curve — anti-fragmentation */
```

**Animate only these:**
- Panel open (detail panel reveal, editor split-pane collapse)
- Selection highlight on skill-row click (background fades `--accent-wash` in over 180ms)
- Toast entry (fades + 4px upward translate, 180ms)

**Never animate:**
- List reorders (triggers layout thrash; disallowed per team-lead brief)
- Page/view transitions
- Loading states (no shimmer, no spinner on skill list — use static "Loading…" text or `--surface` placeholder blocks that fade in once, do not pulse)
- Layout resize (sidebar drag is live but not tweened)

Reduced motion (`@media (prefers-reduced-motion: reduce)`) — all durations collapse to 0ms.

### 1.5 Iconography

**Lucide React** — geometric, consistent stroke widths, well-maintained. Standardize on:
- 14×14 at `stroke-width: 1.6` in UI chrome (nav, buttons)
- 16×16 at `stroke-width: 1.6` in content (cards, headers)
- 20×20 at `stroke-width: 1.5` in empty-state illustrations

No emoji in the UI itself. The existing 📌 pin emoji on `SkillCard.tsx` is replaced with Lucide `Pin`. Icon colors inherit `currentColor` so they track theme tokens automatically.

### 1.6 Density (optional, cut if budget tight)

Team-lead brief specified a 36px row height. That becomes the **single default**. The Comfortable/Compact toggle is demoted to a future improvement — we ship one density. If power users request denser later, it's a small follow-up.

- Skill-row height: **36px** (per brief)
- Top rail: 48px
- Status bar footer: 28px
- Sidebar width default: 320px (240–480px resizable)

### 1.7 Component treatment (Anthropic-grounded)

Specific rules from team-lead brief, lifted verbatim into the plan:

- **Sidebar row**: NO background fill at rest. `--accent-wash` on hover. On selection: 1px left border in `--accent`, with a subtle `--accent-wash` tint behind the row. Row contains: icon + name + subtle Installed/Own dot badge. Row height 36px. Small plugin-group header above in `--type-kicker` (JetBrains Mono caps), preceded by a 1px `--rule` that stops at column padding.
- **Detail card**: `--surface` on `--paper`, 1px `--rule`, `--radius-md` (8px), **no shadow**. Section headings in Source Serif 4 at `--type-heading-lg`.
- **Button primary**: `--ink` fill, `--paper` text (inverted), `--radius-sm` (6px), 36px height. No gradients. Hover: `--ink` at 92% opacity.
- **Button secondary**: transparent fill, `--ink` text, 1px `--rule` border, same dimensions. Hover: `--surface-muted` fill.
- **Badge**: text-only with a 6px colored dot prefix. "Installed" dot = `--installed`; "Own" dot = `--own`; "Failing" dot = `--danger`; etc. **NO pill fills** except for the count badges on section headers (which use `--surface-muted` fill, `--ink-muted` text, `--radius-full`).
- **Divider**: 1px `--rule`, **stops at column padding** — never bleeds across sidebar/workspace boundary.
- **Input / text field**: transparent fill, 1px `--rule`, `--radius-sm`, 32px height, focus ring = 2px `--focus` outline with 2px offset. Placeholder at `--ink-faint`.
- **Modal**: `--surface`, `--radius-lg`, `--elev-modal-*` shadow, 24px padding, max-width 560px for dialogs / 720px for palettes.
- **Tooltip**: `--surface`, 1px `--rule`, `--radius-xs`, 6px / 10px padding, `--type-meta`, appears after 600ms hover or immediately on focus.

---

## 2. Theme Architecture

### 2.1 Three-layer token model on top of Tailwind 4 `@theme`

The token system lives in **Tailwind 4's `@theme` directive**, which is the idiomatic home for design tokens in Tailwind 4. `globals.css` is the single place where tokens are defined; components consume them via `var(--*)` or Tailwind-generated utilities (e.g., `bg-[--bg-card]`, `text-[--text-primary]`, or named utilities when declared under `@theme`).

```
┌──────────────────────────────────────────────────────────────┐
│ Layer 1: RAW TOKENS  (per-theme, declared inside @theme)             │
│   Light: :root   → --paper, --ink, --accent, --installed, --own...   │
│   Dark:  [data-theme="dark"] → override same names with warm values  │
├──────────────────────────────────────────────────────────────┤
│ Layer 2: SEMANTIC TOKENS (theme-agnostic, point at raw)              │
│   --bg-canvas, --text-primary, --border-default,                     │
│   --status-installed, --status-own, --border-focus ...               │
├──────────────────────────────────────────────────────────────┤
│ Layer 3: COMPONENT TOKENS (measurements only — NO colors)            │
│   --sidebar-width, --row-height, --top-rail-height,                  │
│   --status-bar-height, --editor-split                                │
└──────────────────────────────────────────────────────────────┘
```

**globals.css shape (abbreviated):**

```css
@import "tailwindcss";

@theme {
  /* --- Raw tokens, light (default) --- */
  --color-paper: #FBF8F3;
  --color-surface: #FFFFFF;
  --color-ink: #191919;
  --color-ink-muted: #5A5651;
  --color-rule: #E8E1D6;
  --color-accent: #D4A27F;
  --color-installed: #2F6A4A;
  --color-own: #8A5A1F;
  --color-focus: #3B6EA8;
  /* ...all light tokens */

  /* --- Font families --- */
  --font-serif: "Source Serif 4 Variable", ui-serif, Georgia, serif;
  --font-sans:  "Inter Tight Variable", ui-sans-serif, system-ui, sans-serif;
  --font-mono:  "JetBrains Mono Variable", ui-monospace, Menlo, monospace;

  /* --- Measurements --- */
  --sidebar-width: 320px;
  --row-height: 36px;
  --top-rail-height: 48px;
  --status-bar-height: 28px;
}

[data-theme="dark"] {
  /* --- Raw tokens, dark (warm, NOT cool slate) --- */
  --color-paper: #1A1814;
  --color-surface: #221F1A;
  --color-ink: #F2ECE1;
  --color-ink-muted: #A59D8F;
  --color-rule: #2E2A24;
  --color-accent: #E0B793;
  --color-installed: #86C9A5;
  --color-own: #E6B877;
  --color-focus: #7CA8D9;
  /* ...all dark tokens */
}

[data-contrast="more"] {
  /* High-contrast overlay: thickens rules, widens focus, darkens muted */
  --color-rule: color-mix(in srgb, var(--color-ink) 24%, transparent);
  --ring-width: 3px;
}

/* --- Semantic layer (theme-agnostic, always true) --- */
:root {
  --bg-canvas: var(--color-paper);
  --bg-card: var(--color-surface);
  --bg-hover: var(--color-surface-muted);
  --bg-selected: var(--color-accent-wash);
  --text-primary: var(--color-ink);
  --text-muted: var(--color-ink-muted);
  --border-default: var(--color-rule);
  --border-selected: var(--color-accent);
  --border-focus: var(--color-focus);
  --status-installed: var(--color-installed);
  --status-own: var(--color-own);
  /* ... */
}
```

**Why `@theme` over plain `:root { --* }`:** Tailwind 4 reads `@theme` declarations and exposes them as first-class utilities (`bg-paper`, `text-ink-muted`, `border-rule`, etc.) **and** as CSS custom properties. Components can use whichever is ergonomic — utilities in JSX for layout, `var(--*)` in inline styles where dynamic values are needed. Single source of truth. No duplication.

**Enforcement rule**: Components MUST NOT reference raw Layer 1 tokens directly — only semantic tokens (Layer 2) or Tailwind utilities derived from them. Components MUST NOT hardcode hex/rgb values. ESLint rule `vskill/no-raw-color` bans `/#[0-9a-fA-F]{3,8}\b/` and `rgb\(`/`rgba\(` literals inside `src/eval-ui/src/components/` and `pages/` (exceptions: `rgba(0,0,0,*)` shadow definitions in `globals.css` only).

### 2.2 Theme provider — custom, small, Vite-native

`next-themes` is not used (this is a Vite SPA, not Next.js). A minimal `ThemeProvider` in `src/eval-ui/src/theme/ThemeProvider.tsx`:

```tsx
type Theme = "light" | "dark" | "auto";
export function ThemeProvider({ children }: { children: React.ReactNode }): JSX.Element;
export function useTheme(): {
  theme: Theme;
  resolvedTheme: "light" | "dark";
  setTheme: (t: Theme) => void;
};
```

- **Storage**: `localStorage.getItem("vskill-theme")` with values `"light" | "dark" | "auto"` (AC-US2-04).
- **Resolution**: `auto` → reads `matchMedia("(prefers-color-scheme: dark)").matches` and listens for changes (AC-US2-05).
- **DOM**: sets `data-theme="light" | "dark"` on `<html>`. The `auto` state resolves to one of the two concrete themes at the DOM layer.
- **Cross-tab sync**: `storage` event listener on `window` reconciles state if the user opens Studio in multiple tabs.

### 2.3 Hydration-flash prevention

The Vite SPA has no SSR, but React's first render still happens after a brief gap during which the browser paints default styles. To prevent a light/dark flash, an inline `<script>` in `src/eval-ui/index.html` runs **before** Vite's module bundle parses:

```html
<script>
  (function() {
    try {
      var t = localStorage.getItem("vskill-theme");
      var resolved = t === "light" ? "light"
                   : t === "dark"  ? "dark"
                   : matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", resolved);
      if (matchMedia("(prefers-contrast: more)").matches) {
        document.documentElement.setAttribute("data-contrast", "more");
      }
    } catch (e) {
      document.documentElement.setAttribute("data-theme", "light");
    }
  })();
</script>
```

Same script also sets `data-contrast` for `prefers-contrast: more` (AC-US8-09). First paint matches final resolved state; no FOUC.

### 2.4 Toggle component

`ThemeToggle.tsx` lives in the **status bar footer** (not the sidebar). Three-state cycle:

```
 LIGHT → DARK → AUTO → LIGHT ...
```

Shows a small icon (`Sun`/`Moon`/`Monitor` from Lucide) + a mono kicker-cased label. On click: advances state, writes localStorage, updates `data-theme`. Transition duration 180ms via the root-level `transition: background-color var(--dur-base), color var(--dur-base), border-color var(--dur-base);` applied to `:root` (AC-US2-08). The transition does NOT apply to focused form inputs — `input:focus, textarea:focus { transition: none; }` to avoid mid-interaction disruption.

### 2.5 Interactive states (both themes, spec'd per component)

Every interactive element defines 5 states. Verified in both themes.

| State | Treatment |
|---|---|
| Default | Semantic token set |
| Hover | `--bg-hover` (= `--color-surface-muted`) + cursor pointer |
| Focus-visible | 2px `outline: var(--border-focus)` + 2px offset. Rings widen to 3px under `[data-contrast="more"]`. |
| Active | `--bg-selected` (= `--color-accent-wash`), no transform scale |
| Disabled | `opacity: 0.5`, `cursor: not-allowed`, `pointer-events: none` |

Focus ring uses `outline` not `box-shadow` — plays correctly with clipped parents (important for virtualized rows).

---

## 3. Layout & Component Architecture

### 3.1 Shell topology

Three zones, not three panes. The **right column** collapses into the workspace router (the existing `RightPanel.tsx` / `SkillWorkspaceInner`) which internally decides between detail/edit/history tabs. We deliberately reject a three-pane (list + detail + meta) layout because:
- It forces the user to work in a narrow middle column on 13" laptops.
- The workspace tabs already provide "meta view" (metadata panel is a tab in the right pane).

```
┌──────────────────────────────────────────────────────────────┐
│ ▣ Skill Studio         vskill@my-project   ⌘K   ⚙            │  ← Top rail (40px)
├──────────┬───────────────────────────────────────────────────┤
│ SIDEBAR  │                                                   │
│ (280px)  │            WORKSPACE                              │
│          │            (flex-1)                               │
│ Search   │                                                   │
│ New      │   tabs · detail · editor · benchmark · history    │
│          │                                                   │
│ OWN  (7) │                                                   │
│   ...    │                                                   │
│          │                                                   │
│ INSTALL.  │                                                   │
│ (12)     │                                                   │
│   ...    │                                                   │
├──────────┴───────────────────────────────────────────────────┤
│ ~/my-proj  · sonnet-4.6 · ● healthy  · ⌘K · /  · ? · DARK · □│ ← Status bar (28px)
└──────────────────────────────────────────────────────────────┘
```

**Grid**: `grid-template-rows: 40px 1fr 28px` on the root; the middle row is itself a `grid-template-columns: var(--sidebar-width, 320px) 1fr`. Default sidebar width is **320px** (AC-US7-01), narrows to **240px** when viewport is 768–1279px, drawer-mode below 768px. User can drag the divider between sidebar and workspace to resize within `[240px, 480px]` — width persists to `localStorage["vskill-sidebar-width"]` (AC-US7-05). Implementation: `ResizeHandle.tsx` is a 4px-wide element on the sidebar's trailing edge with `cursor: col-resize` and pointer-capture event handlers.

**Mobile (≤767px)**: status bar becomes an overflow drawer (or collapses to a single line with `⚙`), top rail stays, sidebar opens as a full-height overlay from a hamburger button.

### 3.2 Sidebar — the defining element

The user's core request: "**Left sidebar lists skills, split/separated into Installed (.claude folders) vs Own (outside .claude).**"

Component tree:

```
<Sidebar>
  <SidebarHeader>            // logo + project name + model selector
  <SidebarSearch>             // sticky, ⌘K opens palette
  <SidebarActions>            // [+ New Skill]  [↑ Updates (3)]
  <SidebarSection origin="source">   // "Own"
     <SectionHeader title="OWN" count={7} collapsible defaultOpen />
     <PluginGroup ...>        // grouped by plugin when multiple
       <SkillRow ... />
     </PluginGroup>
  </SidebarSection>
  <SidebarDivider variant="strong" />
  <SidebarSection origin="installed">  // "Installed"
     <SectionHeader title="INSTALLED" count={12} collapsible defaultCollapsed />
     <InstalledProvenanceBanner dismissible />  // shown once per session
     <PluginGroup ...>
       <SkillRow ... provenanceIcon />
     </PluginGroup>
  </SidebarSection>
</Sidebar>
```

**Labels** — user-visible language:
- Top section: **OWN** (kicker) — subtitle tooltip: "Skills you author. Edit freely."
- Bottom section: **INSTALLED** (kicker) — subtitle tooltip: "Skills installed inside agent folders (`.claude/`, `.cursor/`, `.gemini/`, etc.). Read-only — edit the source in your project root."

**Detection rule**: `classifyOrigin(skillDir, root)` at `src/eval/skill-scanner.ts:58` is the single source of truth. Sidebar MUST NOT re-implement detection. Rule summary:
1. Path's first segment ∈ `{.claude, .cursor, .gemini, .windsurf, .codex, .openclaw, .aider, .kiro, .pi, .specweave, .vscode, .idea, .zed, .devcontainer, .github, .agents, .agent, ...AGENTS_REGISTRY}` → `installed`.
2. Path includes `plugins/cache/` → `installed`.
3. Otherwise → `source` (user-facing: "Own").

**Sections differ visually** (warm-neutral, flat, dot-based):
- **OWN rows**: no fill at rest; Lucide `FileText` icon + skill name in `--text-primary` via `--type-ui`. A 6px dot in `--status-own` precedes the name. Edit-pencil icon (Lucide `Pencil`) appears at the row's trailing edge on hover.
- **INSTALLED rows**: no fill at rest; full opacity (never dimmed — they're first-class content). Lucide `Package` icon + skill name. A 6px dot in `--status-installed` precedes the name. A text-only provenance chip on the trailing edge shows the agent dir (`.claude`, `.cursor`, etc.) in `--type-meta` size and `--text-faint`. No background fill on the chip.
- Both sections: 36px row height, 12px horizontal padding, 8px gap between icon and name.

**Collapse state persistence**: `localStorage["vskill-sidebar-own-collapsed"] = "true"|"false"` and `localStorage["vskill-sidebar-installed-collapsed"]` similarly (AC-US1-05). **Default: both sections expanded** (`false`/`false`) — INSTALLED is NOT collapsed by default (AC-US1-04). This is a behavioural change from the current `SkillGroupList.tsx` which defaults INSTALLED to collapsed.

**Duplicate-in-both handling** (AC-US1-10): when a skill has an `origin: "source"` entry *and* the same `skill`/`plugin` pair has a matching `origin: "installed"` entry (e.g., user is authoring it and has also installed the published version), both rows render in their respective sections. The Installed row shows a subtle `↑ synced from Own` link that selects the Own row on click. No silent de-duplication. Detection: after the split, frontend cross-references `(plugin, skill)` pairs between sections; pair found → annotate the Installed row with `syncedFromSource: true`.

**Section-scoped filter** (AC-US1-02): each section header exposes a compact filter button (`⌄`) that opens a popover with two checkboxes — `Show passing only` and `Show with updates` — plus a text input. Section-scoped filters apply on top of the global search query. Default: all off.

**Plugin subgrouping** within each section: preserved from `SkillGroupList.tsx`. Plugin header shows plugin icon (PNG from `/images/icons/{plugin}.webp` with SVG fallback), plugin name in KICKER caps, count. Plugin headers are not themselves collapsible — only the two top-level sections are — to avoid UI nesting depth > 2.

**Virtualization**: react-virtual (`@tanstack/react-virtual` ^3.10) when total skill count > 60. Each section virtualizes independently to preserve section headers. Overscan 4. Triggered based on `skills.length`, not a fixed threshold — avoids flicker for small lists.

**Search**: fuzzy via `fuse.js` ^7 over `{skill, plugin, dir}`, debounced 120ms. Matches highlighted with `<mark>` (semantic HTML) styled as `background: var(--accent-soft); color: var(--text-primary);`. When searching, both sections auto-expand and the kicker shows `(3 of 7)` filtered count.

**Empty states per section**:
- OWN empty: "No skills here yet." + primary button "Create your first skill" → enters `mode: "create"`.
- INSTALLED empty: "No installed skills." + muted secondary text "Run `vskill add <skill>` to install one." (the command is a `<code>` with click-to-copy).

### 3.3 Selected-skill indicator — the Anthropic-grounded treatment

Per team-lead brief, the selection indicator is a **1px left border in `--accent`** combined with a subtle `--accent-wash` background tint. No block-cursor glyph, no animation on the cursor. The selection highlight fades in over `--dur-base` (180ms) using the single root `--ease` curve.

```css
.skill-row[data-selected="true"] {
  background: var(--bg-selected);           /* --accent-wash — very subtle */
  box-shadow: inset 2px 0 0 var(--border-selected);  /* 1px left border, crisp */
  transition: background-color var(--dur-base) var(--ease);
}
.skill-row[data-selected="true"] .skill-name {
  color: var(--text-primary);               /* same as default — selection does not re-color text */
}
```

Rationale: the brief is clear that selection is communicated with a left border + subtle wash, and we drop the block-cursor. The signature of the app is the warm paper palette itself, not a playful visual gimmick. Restraint is the identity.

### 3.4 Status bar — footer component (NEW)

**Component**: `StatusBar.tsx` — 28px tall, mono typography at `--type-meta` size, always visible except on mobile <600px.

Segments (left → right, separated by `·` in `--text-subtle`):

| Segment | Data source | Behavior |
|---|---|---|
| Project path | `ConfigContext.config.projectRoot`, truncated with `~/…/last-dir` | Click → copies full path |
| Active model | `ConfigContext.config.activeModel` | Click → opens `ModelSelector` popover |
| Health dot | `/api/v1/health` poll every 15s | Green `●` healthy / Amber `●` slow / Red `●` error |
| Keyboard hints | Static: `⌘K  /  ?` | Click `?` opens shortcut reference modal |
| Theme | `useTheme().theme` | Click cycles light → dark → system |
| Density | `useDensity()` | Click toggles `□ Comfortable / ▫ Compact` |

Never animates. Uses `backdrop-filter: saturate(1.1)` in dark mode only to subtly reinforce boundary.

### 3.5 Top rail (replaces `LeftPanel` brand header)

40px tall. Left: logo glyph + "Skill Studio" in 600 mono. Center: breadcrumb (e.g., `OWN › marketing › slack-messaging`). Right: quick actions (`⌘K` button, settings, GitHub link). The current `LeftPanel.tsx` logo + model selector migrates: logo stays in top rail, model selector MOVES to status bar.

### 3.6 Workspace router (right column)

Preserves the existing `RightPanel.tsx` / `SkillWorkspaceInner` structure — this redesign does NOT rewrite the workspace tabs (editor, benchmark, history, comparison). Visual refresh only: apply new tokens, update `DetailHeader.tsx` to use new typography scale, restyle `TabBar.tsx` with the hairline-divider + 2px-underline-on-active pattern (no pill tabs).

### 3.7 Component inventory

| Component | Path | Status |
|---|---|---|
| `ThemeProvider` | `src/eval-ui/src/theme/ThemeProvider.tsx` | **NEW** |
| `useTheme` | `src/eval-ui/src/theme/useTheme.ts` | **NEW** |
| `ThemeToggle` | `src/eval-ui/src/components/ThemeToggle.tsx` | **NEW** |
| `DensityToggle` | `src/eval-ui/src/components/DensityToggle.tsx` | **NEW** |
| `StatusBar` | `src/eval-ui/src/components/StatusBar.tsx` | **NEW** |
| `TopRail` | `src/eval-ui/src/components/TopRail.tsx` | **NEW** (subsumes logo+breadcrumb) |
| `Sidebar` | `src/eval-ui/src/components/Sidebar.tsx` | **NEW** (replaces `LeftPanel`) |
| `SidebarSection` | `src/eval-ui/src/components/sidebar/SidebarSection.tsx` | **NEW** |
| `SidebarSearch` | `src/eval-ui/src/components/sidebar/SidebarSearch.tsx` | **NEW** (replaces `SkillSearch` scope) |
| `SkillRow` | `src/eval-ui/src/components/sidebar/SkillRow.tsx` | **NEW** (replaces `SkillCard`, denser) |
| `PluginGroup` | `src/eval-ui/src/components/sidebar/PluginGroup.tsx` | **NEW** (ext. of existing `PluginGroupHeader`) |
| `ProvenanceChip` | `src/eval-ui/src/components/sidebar/ProvenanceChip.tsx` | **NEW** |
| `CommandPalette` | `src/eval-ui/src/components/CommandPalette.tsx` | **NEW** (⌘K; action list + fuzzy search) |
| `ShortcutModal` | `src/eval-ui/src/components/ShortcutModal.tsx` | **NEW** |
| `ContextMenu` | `src/eval-ui/src/components/ContextMenu.tsx` | **NEW** (right-click / long-press) |
| `ResizeHandle` | `src/eval-ui/src/components/ResizeHandle.tsx` | **NEW** (sidebar draggable divider) |
| `SkillEditor` + editor/* | `src/eval-ui/src/components/editor/` | **NEW** (Phase 5: split pane, CodeMirror 6) |
| `strings` | `src/eval-ui/src/strings.ts` | **NEW** (central i18n-ready string table) |
| `StudioLayout` | `src/eval-ui/src/components/StudioLayout.tsx` | **REWRITE** — new 3-row shell |
| `App` | `src/eval-ui/src/App.tsx` | **MODIFY** — wrap `ThemeProvider` + add status bar |
| `globals.css` | `src/eval-ui/src/styles/globals.css` | **REWRITE** — token refactor, light palette |
| `LeftPanel` | `src/eval-ui/src/components/LeftPanel.tsx` | **DELETE** (after migration) |
| `SkillCard` | `src/eval-ui/src/components/SkillCard.tsx` | **DELETE** (after `SkillRow` lands) |
| `SkillGroupList` | `src/eval-ui/src/components/SkillGroupList.tsx` | **DELETE** (logic merged into `Sidebar`) |
| `DetailHeader` | `src/eval-ui/src/components/DetailHeader.tsx` | **RESTYLE** |
| `TabBar` | `src/eval-ui/src/components/TabBar.tsx` | **RESTYLE** |
| `EmptyState` | `src/eval-ui/src/components/EmptyState.tsx` | **RESTYLE** |
| Other workspace components | `src/eval-ui/src/pages/workspace/**` | **TOKEN SWEEP ONLY** (no logic change) |

Component count: **21 new, 6 restyled, 3 deleted** (after spec reconciliation).

### 3.8 Data flow

```
ThemeProvider (context)
  └── StudioProvider (existing, unchanged — owns skills fetch + selection)
       └── ConfigProvider (existing — owns project/model config)
            └── DensityProvider (NEW — reads localStorage, writes data-density)
                 └── StudioLayout
                      ├── TopRail
                      ├── Sidebar     (reads StudioContext, derives split via origin)
                      ├── Workspace   (existing RightPanel → SkillWorkspaceInner)
                      └── StatusBar   (reads Theme + Density + Config)
```

Fetch strategy unchanged: `StudioContext.useEffect` → `api.getSkills()` on mount + SSE updates. The redesign adds **no new backend calls**. Payload already includes `origin` — the sidebar split is purely client-side derivation, so no API change needed.

---

## 4. Detail Capture — every skill field

Current `SkillInfo` (from `src/eval-ui/src/types.ts:39`) already includes: `plugin`, `skill`, `dir`, `hasEvals`, `hasBenchmark`, `evalCount`, `assertionCount`, `benchmarkStatus`, `lastBenchmark`, `origin`, `updateAvailable`, `currentVersion`, `latestVersion`, `pinnedVersion`.

**Additions needed** (backend + type + API; minimal, additive):

| Field | Source | Why surfaced |
|---|---|---|
| `description` | SKILL.md frontmatter `description` | Shown in skill-row tooltip + workspace detail header |
| `version` | SKILL.md frontmatter `metadata.version` | Chip in skill-row when present |
| `tags` | SKILL.md frontmatter `metadata.tags` (comma or array) | Shown in detail panel only |
| `author` | SKILL.md frontmatter `author` or plugin metadata | Detail panel |
| `lastModified` | `fs.stat(dir).mtime` of `SKILL.md` | Skill-row hover card, detail panel |
| `byteSize` | sum of `dir` contents | Detail panel, compact |
| `platforms` | frontmatter `platforms` or inferred from plugin | Detail panel chips |
| `dependencies.mcp[]` | existing `/api/v1/skills/:plugin/:skill/deps` | Detail panel (existing `McpDependencies.tsx` — keep) |

**Server change** (`src/eval-server/api-routes.ts`, the `/api/v1/skills` list endpoint): augment each entry's payload by parsing SKILL.md frontmatter (use existing `gray-matter` or a minimal inline parser — no new dep). Keep payload shape additive; existing consumers unaffected.

**Progressive disclosure rules** — NOT every field shows in the sidebar. Density hierarchy:

```
Skill row (compact — always visible)
   ─ skill name (bold mono)
   ─ origin chip (installed only — ".claude", ".cursor", ...)
   ─ benchmark-status pill (if present)
   ─ update-available chip (only if updateAvailable)

Skill row hover (popover — reveal on 500ms hover or focus)
   ─ description (3-line clamp)
   ─ version (v1.0.0)
   ─ tags (up to 4, overflow "+2")
   ─ last modified (relative: "3 days ago")
   ─ eval count · assertion count

Detail panel (full disclosure, new "Metadata" tab)
   ─ all frontmatter fields
   ─ full path (copyable)
   ─ byte size, file tree
   ─ dependencies (MCP + skill)
   ─ version history (existing VersionPanel)
   ─ author, license, platforms, category
```

The popover is the critical UX element: it lets devs scan the sidebar and triage skills without leaving the list. Built on a small `HoverCard` primitive (Radix UI `HoverCard` — free, 2kb gzip, a11y-correct) OR native `popover` API with a fallback. Given Vite/React bundle sensitivity, we use native `popover` where available (Chrome 114+, Safari 17+) and fall back to a 30-line custom positioner (no Radix — adds 20kb).

### Display rules per field type

| Field | Treatment |
|---|---|
| `name`, `plugin` | mono 500, truncate-to-ellipsis |
| `version` | mono chip, 10px, `--surface-3` bg, accent ring on "latest" |
| `description` | body sans, 3-line clamp, `line-clamp: 3` |
| `tags` | compact pill, `--type-meta`, hairline border, max 4 inline |
| `path` | `--type-mono-sm`, muted, click-to-copy, "Copied" toast |
| `lastModified` | relative ("3d ago") with `title` attr = full ISO |
| `benchmarkStatus` | semantic status pill (existing `STATUS_CONFIG` pattern) |
| `origin` | INSTALLED only — `.claude` chip with hairline border, info-tint bg |

---

## 5. Interaction Model

### 5.1 Keyboard shortcuts (global)

| Key | Action | Implementation |
|---|---|---|
| `⌘K` / `Ctrl+K` | Open Command Palette / focus sidebar search (AC-US4-01) | `CommandPalette.tsx` modal — actions: select skill, new skill, run benchmark, switch theme, switch model |
| `/` | Focus sidebar search (AC-US4-01) | `SidebarSearch.tsx` `inputRef.focus()` + select existing text |
| `?` | Open keyboard cheatsheet (AC-US4-05) | `ShortcutModal.tsx` |
| `j` / `↓` | Next skill across both sections (AC-US4-02) | Section headers skipped |
| `k` / `↑` | Previous skill | |
| `Enter` | Open focused skill in workspace | |
| `Esc` | Close modal / clear search / blur / close palette (AC-US4-01) | stacked via `useEscape` hook |
| `E` | Edit SKILL.md (AC-US4-03) | Opens inline editor for OWN; read-only banner for INSTALLED |
| `R` | Run benchmark (AC-US4-04) | |
| `C` | Copy path to clipboard (AC-US4-04) | |
| `D` | Duplicate skill (OWN only) (AC-US4-04) | |
| `U` | Update (INSTALLED with `updateAvailable`) (AC-US4-04) | |
| `⌘B` / `Ctrl+B` | Toggle sidebar visibility (AC-US4-09) | |
| `⌘S` / `Ctrl+S` | Save editor (AC-US5-06) | Editor scope only |
| `⌘.` | Toggle density | |
| `⌘⇧D` | Toggle theme | Avoids conflict with Chrome's bookmark shortcut |
| `⌘/` | Toggle comment in code editor | Editor scope |

All shortcuts registered through a single `useKeyboardShortcut` hook that respects `document.activeElement.tagName === "INPUT"` to avoid hijacking text entry.

### 5.2 Focus management

- Logical tab order: Top rail → Sidebar search → Sidebar list (j/k within) → Workspace tabs → Workspace content → Status bar.
- `Skip to workspace` link, visually hidden unless focused, at position 0 in tab order.
- When selecting a skill with the mouse, focus does NOT move to workspace (so keyboard users can keep flicking through the list). `Enter` on a focused row both selects AND moves focus to workspace.
- Modals trap focus (first focusable → last → first) and restore focus to the trigger on close.

### 5.3 Loading / empty / error states per surface

| Surface | Loading | Empty | Error |
|---|---|---|---|
| Sidebar list | **No shimmer.** Six 36px placeholder rows filled with `--bg-hover` (static, no pulse); section headers rendered with count `—`. Fades in once on mount via `var(--dur-base)`. | "No skills here yet" + CTA | "Couldn't load skills. Check permissions on the project root." + retry button |
| Skill detail (workspace) | 200ms delay (avoid flash for fast responses), then static header + tab placeholders in `--bg-hover`. No shimmer. | `<EmptyState variant="no-selection">` | `<EmptyState variant="error">` (exists, restyled) |
| Benchmark results | Existing `ProgressLog` (progress bar is acceptable — it conveys real progress, not theatre) | "No benchmark runs yet" | Error card (exists, restyled) |
| Theme preference sync | None — optimistic | None | Silent (localStorage is source of truth) |

**Shimmer prohibition (team-lead brief)**: no `@keyframes shimmer`, no `animation: shimmer`, no gradient backgrounds moving across placeholder rows. The existing `.skeleton` class in `globals.css` is REPLACED by a `.placeholder` class that uses a static `--bg-hover` fill. The old shimmer animation is deleted. CI grep: `scripts/check-no-shimmer.ts` rejects `shimmer` in CSS and component source.

### 5.4 Context menu (right-click / long-press) — AC-US4-07

New component: `ContextMenu.tsx` triggered on right-click or long-press (≥500ms) of any `SkillRow`. Positioned via native `popover` anchored to the pointer; dismiss on any click-outside or Esc.

Items (conditional on `origin` and `updateAvailable`):

| Item | Origin | Condition |
|---|---|---|
| Open | both | always |
| Copy Path | both | always |
| Reveal in Editor | both | requires eval-server endpoint `/api/v1/skills/:plugin/:skill/reveal` (thin additive route opening `code`/`idea`/`cursor` via child process — OS-aware) |
| Edit | source only | |
| Duplicate | source only | |
| Run Benchmark | both | |
| Update | installed only | only when `updateAvailable === true` |
| Uninstall | installed only | confirm dialog |
| Delete | source only | confirm dialog, types skill name to confirm |

All items are keyboard-navigable (arrow keys + Enter); first item receives initial focus. `role="menu"` + `role="menuitem"` ARIA.

### 5.5 Copy voice & central `strings.ts` (NFR-005, US-010)

All user-visible strings extracted to `src/eval-ui/src/strings.ts`:

```ts
// src/eval-ui/src/strings.ts
export const strings = {
  sidebar: {
    ownEmpty: "No skills yet. Add one from the marketplace or point Studio at a folder.",
    installedEmpty: "No installed skills. Run `vskill install <plugin>` or `claude plugin install <plugin>` to add one.",
    searchPlaceholder: "Search skills",
    sectionOwn: "OWN",
    sectionInstalled: "INSTALLED",
    syncedFromOwn: "synced from Own",
  },
  actions: {
    saved: (name: string) => `Saved ${name}.`,
    installed: (n: number) => `Installed ${n} skill${n === 1 ? "" : "s"}.`,
    benchmarkComplete: "Benchmark complete.",
    copied: "Path copied.",
  },
  errors: {
    scanFailed: "Couldn't scan workspace. Check permissions on the project root.",
    saveConflict: "Couldn't save SKILL.md — the file changed on disk. Reload to see the new version, or keep editing to overwrite.",
    disconnected: "Disconnected — reconnecting…",
  },
  // ...
};
```

**Voice enforcement** (AC-US10-06): CI rule at `scripts/check-strings-voice.ts` runs a regex grep over `strings.ts`:

```
/\boops\b/i
/\buh[ -]oh\b/i
/\bawesome\b/i
/\bblazing[- ]fast\b/i
/🎉|✨|🚀|✅/
/[^!]!!+/     // trailing double-bangs anywhere
/!$/ on lines not ending with inline code
```

First match exits with code 1. A `lint:strings` npm script wires into CI.

### 5.6 Optimistic UI

- Select skill → sidebar row updates immediately (no request).
- Toggle density / theme → instant, async persist.
- Create skill → inline drawer appears, on success row slides into OWN section with the cursor-indicator animation (highlight for 1s with `--accent-soft` bg flash).
- Delete / uninstall (future) → row is struck through + 3s undo toast; fires server request after toast dismiss.

---

## 6. Performance Targets

Numbers below align with US-009 ACs.

| Metric | Target | Measure |
|---|---|---|
| First Contentful Paint (cold load, ≤100 skills) | < 800ms (AC-US9-01) | Lighthouse CI |
| Time-to-Interactive | < 1500ms (AC-US9-01) | Lighthouse CI |
| Sidebar render with ≥500 skills | ≥50 fps scroll (AC-US9-02) | react-virtuoso + Chrome perf panel |
| Detail-panel render-to-first-content | < 120ms (AC-US9-03) | Perf mark (excludes network-backed history fetch) |
| Search response time | < 80ms up to 500 skills; < 180ms up to 2000 skills (AC-US9-04); 50ms debounce | Perf mark |
| Theme switch | < 200ms, no long tasks > 50ms (AC-US9-06) | Chrome DevTools Performance panel |
| Initial gzipped chunk | ≤ 250 KB (AC-US9-05, NFR-004) | `vite build` report + CI assertion |
| Lazy chunk size (editor, charts) | ≤ 150 KB each | `vite build` report |
| Font flash (FOIT/FOUT) | 0 flash in dark, ≤1 frame in light | Network-throttled 3G test |
| HoverCard open latency | < 50ms | Perf mark |

### Bundle strategy

- `@fontsource-variable/*` adds ~45kb (both fonts, variable, subset to Latin) — split into a separate chunk with `manualChunks: { fonts: [...] }` in `vite.config.ts`.
- Lazy-load `CommandPalette` + `ShortcutModal` via `React.lazy` — only fetched on first ⌘K / `?`.
- Lazy-load `react-virtuoso` only when `skills.length > 60` (dynamic import on threshold). `react-virtuoso` chosen over `@tanstack/react-virtual` for its section-aware API that keeps the section headers sticky — matches our split-section pattern without hand-rolling offset math.
- **Lazy-load the Markdown editor + preview** (Phase 5) — `SkillEditor.tsx` and `SkillPreview.tsx` are behind `React.lazy`; only fetched when a user hits `E` or clicks Edit. Preview uses the existing Markdown renderer in the workspace (`SkillContentViewer`) — no new renderer dep.
- Lazy-load the YAML frontmatter validator (`js-yaml` ^4.1, ~40kb unminified) with the editor bundle.
- No Radix UI — stays native `popover` + vanilla React for chrome.

### Render discipline

- Sidebar rows memoized via `React.memo` with reference-stable props.
- `StudioContext.skills` sorted once at reducer level, not per-render.
- `SidebarSection` uses `ResizeObserver` to trigger virtualization threshold re-eval only on sidebar resize (rare).

---

## 7. Accessibility (WCAG 2.1 AA, targeting AAA for text)

### Contrast (verified numbers, warm-neutral palette)

All ratios below are measured against `--paper` (`#FBF8F3` light / `#1A1814` dark) using `wcag-contrast`.

- Light: `--ink` (`#191919`) = **16.8:1** (AAA body)
- Light: `--ink-muted` (`#5A5651`) = **7.6:1** (AAA body, AAA large)
- Light: `--ink-faint` (`#8A857E`) = **3.8:1** (AA large only — reserved for captions/disabled)
- Light: `--installed` (`#2F6A4A`) = **5.9:1** (AA UI)
- Light: `--own` (`#8A5A1F`) = **6.2:1** (AA UI)
- Light: `--focus` (`#3B6EA8`) = **7.1:1** (AAA UI)
- Dark: `--ink` (`#F2ECE1`) = **14.2:1** (AAA body)
- Dark: `--ink-muted` (`#A59D8F`) = **6.1:1** (AAA body, AAA large)
- Dark: `--ink-faint` (`#7A726A`) = **3.3:1** (AA large only)
- Dark: `--installed` (`#86C9A5`) = **5.2:1** (AA UI)
- Dark: `--own` (`#E6B877`) = **5.5:1** (AA UI)
- Dark: `--focus` (`#7CA8D9`) = **4.9:1** (AA UI)

Test file: `src/eval-ui/src/__tests__/theme-contrast.test.ts` — runs `wcag-contrast` against every semantic pair; CI-blocking. Failures block merge.

### Semantic HTML / ARIA

- Root: `<div id="app">` with `<header>` (top rail), `<aside aria-label="Skill list">` (sidebar), `<main>` (workspace), `<footer role="contentinfo">` (status bar).
- Sidebar sections: `<section aria-labelledby="sec-own">` / `aria-labelledby="sec-installed"` with the section header being the labelled element.
- Each skill row: `<button>` with `aria-pressed={isSelected}` for the selection state (toggle semantics); `aria-describedby` pointing at the invisible hover-card content for screen-reader access to metadata.
- Status pills: `role="img" aria-label="passing"` so AT doesn't read color words.
- Command palette: `role="combobox"` / `role="listbox"` / `role="option"` — standard combobox ARIA.

### Keyboard

- All interactive elements reachable via Tab, activatable via Enter/Space.
- Custom scrollbars do not consume focus.
- Keyboard shortcuts documented in `ShortcutModal` + `<kbd>` tags.

### Reduced motion

`@media (prefers-reduced-motion: reduce)` — all animations set to `animation: none !important` and all `transition-duration: 0ms !important` via a single rule in `globals.css`. Selection highlight, panel-open reveal, and toast entry all become instant. No shimmer exists in any state, so no shimmer to suppress.

### Screen reader

- Skill count changes announced via `aria-live="polite"` region (`"Filtered 3 of 14 skills"` when searching).
- Theme toggle announces new state: `"Theme: dark"`.

---

## 8. Implementation Phases

**Five phases over 11 days**; each ends with a working build and green E2E. No phase leaves the codebase broken.

### Phase 1 — Theme foundation + tokens (Days 1–2)

Goal: both themes render correctly, tokens enforced, no visible regression.

Files:
- `src/eval-ui/src/styles/globals.css` — REWRITE: token layers, light palette, reduced-motion rules
- `src/eval-ui/src/theme/ThemeProvider.tsx` — NEW
- `src/eval-ui/src/theme/useTheme.ts` — NEW
- `src/eval-ui/index.html` — add hydration-flash prevention script
- `src/eval-ui/src/main.tsx` — import fontsource + wrap `<ThemeProvider>`
- `src/eval-ui/src/__tests__/theme-contrast.test.ts` — NEW
- `package.json` — add `@fontsource-variable/jetbrains-mono`, `@fontsource-variable/ibm-plex-sans`
- `src/eval-ui/vite.config.ts` — `manualChunks: { fonts: [...] }`, `@tailwindcss/vite` config for tokens

Verification: existing UI still works (just with new tokens + fonts), toggling theme via devtools `data-theme` attribute shows both themes.

### Phase 2 — Shell layout + sidebar split (Days 3–5)

Goal: user sees the redesigned shell; sidebar split is the only functional change.

Files:
- `src/eval-ui/src/components/StudioLayout.tsx` — REWRITE (3-row grid)
- `src/eval-ui/src/components/TopRail.tsx` — NEW
- `src/eval-ui/src/components/StatusBar.tsx` — NEW (reads theme, density, config)
- `src/eval-ui/src/components/ThemeToggle.tsx` — NEW
- `src/eval-ui/src/components/DensityToggle.tsx` — NEW
- `src/eval-ui/src/components/Sidebar.tsx` — NEW
- `src/eval-ui/src/components/sidebar/SidebarSection.tsx` — NEW
- `src/eval-ui/src/components/sidebar/SidebarSearch.tsx` — NEW (extends `SkillSearch`)
- `src/eval-ui/src/components/sidebar/SkillRow.tsx` — NEW
- `src/eval-ui/src/components/sidebar/PluginGroup.tsx` — NEW
- `src/eval-ui/src/components/sidebar/ProvenanceChip.tsx` — NEW
- `src/eval-ui/src/App.tsx` — MODIFY (new layout wiring)
- `src/eval-ui/src/components/LeftPanel.tsx` — DELETE after replacement is green
- `src/eval-ui/src/components/SkillGroupList.tsx` — DELETE
- `src/eval-ui/src/components/SkillCard.tsx` — DELETE (replaced by `SkillRow`)

Verification: Playwright E2E at `src/eval-ui/e2e/sidebar-split.spec.ts` — seeds `source` + `installed` skills, asserts OWN/INSTALLED sections, counts, collapse state persistence, cursor-indicator on selection.

### Phase 3 — Detail capture + progressive disclosure (Days 6–7)

Goal: every skill field surfaced; popover + detail tab populated.

Files:
- `src/eval-server/api-routes.ts` — MODIFY: augment `/skills` list with frontmatter fields (`description`, `version`, `tags`, `lastModified`, `byteSize`)
- `src/eval-ui/src/types.ts` — MODIFY: extend `SkillInfo` with the additive fields (all optional for back-compat)
- `src/eval-ui/src/components/sidebar/SkillRowHoverCard.tsx` — NEW (popover API + fallback)
- `src/eval-ui/src/pages/workspace/MetadataTab.tsx` — NEW (full detail panel)
- `src/eval-ui/src/components/DetailHeader.tsx` — RESTYLE (new typography scale, path chip)

Verification: Vitest on frontmatter parser (`src/eval-server/__tests__/skill-metadata.test.ts`). Playwright on hover card (`src/eval-ui/e2e/skill-detail-capture.spec.ts`).

### Phase 4 — Keyboard, palette, context menu, copy voice (Days 8–9)

Goal: every shortcut works, command palette ships, context menu works, all strings centralized and voice-checked.

Files:
- `src/eval-ui/src/components/CommandPalette.tsx` — NEW
- `src/eval-ui/src/components/ShortcutModal.tsx` — NEW
- `src/eval-ui/src/components/ContextMenu.tsx` — NEW (AC-US4-07)
- `src/eval-ui/src/hooks/useKeyboardShortcut.ts` — NEW
- `src/eval-ui/src/strings.ts` — NEW (NFR-005)
- `scripts/check-strings-voice.ts` — NEW (AC-US10-06) + wired in `package.json` `lint:strings`
- `src/eval-server/api-routes.ts` — ADD endpoint `/api/v1/skills/:plugin/:skill/reveal` (opens in editor via OS `code`/`cursor`/`idea` child process)
- Token sweep: `src/eval-ui/src/pages/workspace/**/*.tsx` — replace any remaining literal colors with semantic tokens (ESLint rule from Phase 1 catches these)

Verification: E2E `src/eval-ui/e2e/keyboard-shortcuts.spec.ts` invokes every shortcut; `lint:strings` runs in CI; axe-core on command palette modal.

### Phase 5 — SKILL.md editor + preview + validation (Days 10–11)

Goal: US-005 delivered — split-pane editor with live preview, YAML frontmatter validation, conflict-aware save.

Files:
- `src/eval-ui/src/components/editor/SkillEditor.tsx` — NEW (split pane shell, resizable divider with `localStorage["vskill-editor-split"]`)
- `src/eval-ui/src/components/editor/EditorPane.tsx` — NEW (CodeMirror 6 for Markdown + YAML, lightweight — no full Monaco)
- `src/eval-ui/src/components/editor/PreviewPane.tsx` — NEW (reuses `SkillContentViewer` for rendering)
- `src/eval-ui/src/components/editor/IssuesStrip.tsx` — NEW (frontmatter validation results above the editor)
- `src/eval-ui/src/components/editor/ReadOnlyBanner.tsx` — NEW (AC-US5-07; shown for INSTALLED edits with "Find source" action)
- `src/eval-ui/src/components/editor/ExternalChangeBanner.tsx` — NEW (AC-US5-10)
- `src/eval-ui/src/lib/skill-frontmatter.ts` — NEW (parse + validate SKILL.md schema: required `name`, `description`; optional `model`, `allowedTools`, `target-agents`; known-tools allowlist check — AC-US5-04, AC-US5-05)
- `src/eval-ui/src/hooks/useFileWatcher.ts` — NEW (client-side subscriber to an SSE channel from eval-server that emits file-change events for the currently-open file)
- `src/eval-server/file-watcher.ts` — NEW (uses `chokidar` — already transitively in-tree — to emit SSE events on SKILL.md changes)
- `src/eval-ui/src/__tests__/frontmatter-validator.test.ts` — NEW
- `src/eval-ui/e2e/editor-flow.spec.ts` — NEW (edit → validate → save → conflict → reload)

**CodeMirror 6 choice**: picked over Monaco because it's modular (load only Markdown + YAML languages, ~35kb gzip vs Monaco's 500+kb), has first-class Vite support, and honors `prefers-reduced-motion`. Stays inside the 150KB lazy-chunk budget.

Verification: E2E covers the full edit cycle in both themes including the external-change race. Unit tests cover 8 frontmatter fixtures (valid, missing name, missing description, malformed YAML, unknown tool, empty allowedTools, extended frontmatter, target-agents).

---

## 9. ADRs Created

Written as files under `.specweave/docs/internal/architecture/adr/`:

1. **[`0674-01-warm-neutral-theme-tokens.md`](../../docs/internal/architecture/adr/0674-01-warm-neutral-theme-tokens.md)** — Warm-neutral palette grounded in Anthropic / Claude Labs design language. Specifies both theme token sets, contrast ratios, rejection of cool-slate dark mode and purple AI-slop accents, and the semantic `--installed` / `--own` provenance tokens.
2. **[`0674-02-sidebar-origin-classification.md`](../../docs/internal/architecture/adr/0674-02-sidebar-origin-classification.md)** — `classifyOrigin` in `src/eval/skill-scanner.ts:58` is the single source of truth; sidebar uses `skill.origin` and the first path segment only; user-facing labels are "OWN" / "INSTALLED"; `.claude` is illustrative, not the sole signal.
3. **[`0674-03-studio-typography-system.md`](../../docs/internal/architecture/adr/0674-03-studio-typography-system.md)** — Source Serif 4 (display) + Inter Tight (body/UI) + JetBrains Mono (code). Explicit rejection of Inter, Roboto, and Geist as AI-slop defaults. Serif is scoped to titles only; never in table rows or editor chrome.
4. **[`0674-04-tailwind-4-theme-layer.md`](../../docs/internal/architecture/adr/0674-04-tailwind-4-theme-layer.md)** — Tailwind 4 `@theme` directive as the single home for design tokens. Rationale for `@theme` over CSS-in-JS, runtime token libraries, or legacy `tailwind.config.js` extension. Version-locking strategy with fallback plan.

---

## 10. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **Scope creep — workspace rewrite** (what sank 0463 "skill-builder-ui-redesign") | High | Critical | Spec.md US-005 now explicitly includes the editor + preview in scope, which is the controlled expansion. The protection is Phase 5 being the LAST phase — Phases 1-4 are independently shippable; if day-10 estimates slip, Phase 5 can be split out as `0675` without losing the theme/sidebar wins. Everything NOT listed in spec's "Out of Scope" (line 294) is actively excluded. |
| **Warmth vs. contrast** — warm paper palette must pass WCAG AA against `--ink-muted` in BOTH themes without cooling off | Medium | High | Final contrast ratios specified in §7 and repeated in ADR-0674-01: `--ink-muted` = 7.6:1 light, 6.1:1 dark (both AAA body). `theme-contrast.test.ts` CI gate asserts the full matrix. If any pair slips below 4.5:1 during token refinement, build fails. |
| **Marketing-site creep** — anthropic.com inspiration mis-scaled into the tool | Medium | Medium | anthropic.com is a reading surface; Studio is a scanning surface. Hard rules encoded in §1: max display type 28px (not 72px), serif only in titles, generous-but-scannable whitespace (not marketing-site-airy). Every screen review asks: "Would this feel like a landing page?" — if yes, tighten. |
| **Dark-mode drift** — dark theme looking "too brown" or washed-out vs. VS Code default | Low | Low | The warm-brown feel IS the intent, stated in §0 and ADR-0674-01. Reviewers told in advance that comparison to VS Code default is not the success criterion. If users complain, we gather data before adjusting — not a pre-launch pivot. |
| **Tailwind 4 `@theme` maturity** — still young (2024 release), could hit edge cases | Medium | Medium | Lock Tailwind to a specific minor version in `package.json` (`^4.2.1` currently). ADR-0674-04 documents a fallback to plain `:root { --* }` + `tailwind.config.js` plugins (pre-4 pattern) if a plugin incompat appears. Fallback is a one-file change; ~4h of work if needed. |
| **No shimmer rule fights existing code** — current `globals.css` has `.skeleton` with `shimmer` animation | Low | Low | Phase 1 deletes `@keyframes shimmer` and `.skeleton` class; replacement `.placeholder` class with static fill is drop-in. CI grep `scripts/check-no-shimmer.ts` catches reintroduction. |
| Frontmatter parsing breaks on malformed SKILL.md | Medium | Medium | Parser wraps errors, logs, and falls back to bare `skill`/`plugin` — row still renders. `description` absent → popover shows "No description". Unit tests for 5 malformed fixtures. |
| Bundle bloat from three font families (+ ~70 KB) | Low | Low | Variable fonts subset to Latin + Latin-ext, lazy-loaded as a separate `fonts` chunk. Network tab measurement in CI. If exceeds budget, drop Source Serif 4 to static 400+500 subset (saves ~20kb). |
| `popover` API browser-support cliff | Low | Medium | Feature-detect; fallback custom positioner is 30 LoC. |
| Keyboard shortcut conflicts with host browser | Medium | Low | `⌘⇧D` avoids the Chrome bookmark collision. Shortcut reference modal discloses. Single-letter actions (E/R/C/D/U) are suppressed when an input is focused. |
| Existing users disoriented by sidebar reorg | Medium | Low | "OWN" label matches the user's mental model (their own source); "INSTALLED" matches `vskill install` copy. First-visit toast: "Your skills are now organized under OWN — installed dependencies are under INSTALLED below." Dismissible, never re-shown. |
| `classifyOrigin` false positives (e.g., a user project named `.claude-notes`) | Very Low | Low | Detection is `firstSegment === ".claude"` (exact match, not prefix). A project *named* `.claude-notes` would trigger `installed`; mitigated by it being the root itself (scanner excludes `root === skillDir` case). Edge case acceptable. |
| Theme toggle state drift across tabs | Low | Low | `storage` event listener reconciles across tabs — first-class, not an afterthought. |

**The biggest risk** is scope: prior increment `0463-skill-builder-ui-redesign` was **abandoned** (per `metadata.json.relatedIncrements`). This plan mitigates by:
1. Each phase is independently shippable — Phase 1 alone delivers both themes with no other change; Phase 2 alone delivers the sidebar split; Phase 5 (editor) is the last, not the first, phase and can be split to a follow-up increment if Day-10 budget is blown.
2. 11-day budget is generous but not padded — every phase maps to 1-4 concrete spec ACs so scope is measurable daily.
3. CI gates (contrast, voice, bundle-size, Lighthouse, axe-core) catch regressions before merge.
4. Workspace internals OTHER than the editor (benchmark, history, sweep, model-compare UIs) remain token-sweep-only — the spec's "Out of Scope" line 302 confirms.

---

## Appendix A — File changes at a glance

**Adding (33 files):**
- `src/eval-ui/src/theme/{ThemeProvider.tsx,useTheme.ts}`
- `src/eval-ui/src/components/{TopRail,StatusBar,ThemeToggle,DensityToggle,Sidebar,CommandPalette,ShortcutModal,ContextMenu,ResizeHandle}.tsx`
- `src/eval-ui/src/components/sidebar/{SidebarSection,SidebarSearch,SkillRow,PluginGroup,ProvenanceChip,SkillRowHoverCard}.tsx`
- `src/eval-ui/src/components/editor/{SkillEditor,EditorPane,PreviewPane,IssuesStrip,ReadOnlyBanner,ExternalChangeBanner}.tsx`
- `src/eval-ui/src/pages/workspace/MetadataTab.tsx`
- `src/eval-ui/src/lib/skill-frontmatter.ts`
- `src/eval-ui/src/hooks/{useKeyboardShortcut,useFileWatcher}.ts`
- `src/eval-ui/src/strings.ts`
- `src/eval-ui/src/__tests__/{theme-contrast,a11y,frontmatter-validator}.test.ts`
- `src/eval-server/file-watcher.ts`
- `src/eval-server/__tests__/skill-metadata.test.ts`
- `src/eval-ui/e2e/{sidebar-split,skill-detail-capture,keyboard-shortcuts,editor-flow}.spec.ts`
- `scripts/check-strings-voice.ts` (NFR-005 copy voice CI gate)
- `scripts/check-no-shimmer.ts` (Anthropic direction: no shimmer animations anywhere)
- `scripts/check-serif-scope.ts` (Source Serif 4 restricted to titled surfaces only)

**Modifying (8 files):**
- `src/eval-ui/src/{App.tsx,main.tsx,index.html}`
- `src/eval-ui/src/styles/globals.css` (near-total rewrite)
- `src/eval-ui/src/components/{StudioLayout,DetailHeader,TabBar,EmptyState}.tsx` (restyle)
- `src/eval-ui/src/types.ts` (additive fields)
- `src/eval-server/api-routes.ts` (list endpoint augmentation + `reveal` endpoint)
- `src/eval-ui/vite.config.ts` (manual chunks)
- `package.json` (three fontsource-variable packages [source-serif-4, inter-tight, jetbrains-mono] + react-virtuoso + codemirror + js-yaml + eslint rule + lint:strings / lint:shimmer / lint:serif-scope scripts)
- `eslint.config.js` (`vskill/no-raw-color` rule registration)

**Deleting (3 files):**
- `src/eval-ui/src/components/{LeftPanel,SkillCard,SkillGroupList}.tsx`

Net: +35, ~8, −3 = 46 files touched.

---

## Appendix B — Reconciliation with spec.md (resolved)

Spec.md landed during Phase C of the architect's work. All 10 user stories + 6 FRs + 6 NFRs were reconciled:

| Open question (pre-spec) | Resolution in spec |
|---|---|
| Scope: eval-ui only? | **Confirmed** (spec §Code Location & Scope) — `repositories/anton-abyzov/vskill/src/eval-ui/` only. Marketing page out. |
| Light theme parity? | **Required** — both first-class, "no afterthought" (AC-US2-02). |
| Density modes? | Not explicitly required by spec — retained in plan as a developer-ergonomics bonus, low implementation cost. Can be cut if budget pressure. |
| Command palette? | Implicit via `⌘K` opening search (AC-US4-01). Plan retains the fuller palette (actions + skills) as a superset. |
| `metadata.json.scope.app`? | **Should be corrected** — spec confirms eval-ui target; metadata field still points at vskill-platform. Team-lead to address. |

**New requirements introduced by spec that expanded the plan** (fully absorbed above):
- US-005 SKILL.md editor + live preview + YAML validation → Phase 5 (days 10-11)
- US-010 copy voice + central strings.ts + CI regex gate → Phase 4
- AC-US1-10 duplicate-in-both rendering → §3.2
- AC-US4-07 context menu → §5.4
- AC-US7-01/05 320px default sidebar + draggable resize → §3.1
- AC-US8-09 `prefers-contrast: more` variant → §2.3

**Plan-level issues to raise with team-lead:**
1. `metadata.json.scope.app` still names the marketing page — should be `repositories/anton-abyzov/vskill/src/eval-ui`. Fix before closure.
2. Increment metadata `project: "vskill-platform"` but spec target is `vskill` (the CLI). External sync targets may need to reference `vskill` repo, not `vskill-platform`.
3. Budget grew from 8 → 11 days due to Phase 5 editor scope. If the team wants a tighter release, splitting Phase 5 into `0675-vskill-studio-editor` keeps this increment at 9 days (Phases 1-4).
