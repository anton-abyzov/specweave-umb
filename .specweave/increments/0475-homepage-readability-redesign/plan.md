# Architecture Plan: Homepage Readability Redesign

## Summary

Five CSS/layout-only edits to three existing files. No new components, no data flow changes, no server/client boundary modifications. The architecture is the existing Next.js 15 page structure -- this plan documents the exact edit locations and the one structural change (children-above-video reorder in HomepageDemoHero).

## Decision: No ADR Required

This increment touches inline styles and one JSX reorder within existing components. There are no architectural decisions (no new abstractions, no new patterns, no technology choices). An ADR would be empty ceremony.

## Files Affected

| File | Type | Changes |
|---|---|---|
| `src/app/components/homepage/HomepageDemoHero.tsx` | Client component | Reorder children above video; move CLI copy button into video overlay; remove standalone CLI row |
| `src/app/page.tsx` | Server component | Resize hero badges; extract flaws stat into callout block; resize bottom badges |
| `src/app/globals.css` | Stylesheet | Add `video-copy-btn` hover + responsive rules |

## Component Boundary Analysis

```
page.tsx (server)
  └─ HomepageDemoHero (client, "use client")
       ├─ children slot ← server-rendered React nodes passed as props
       ├─ <video> + play/pause button
       └─ CLI copy button (moves INTO video overlay)
```

The server/client boundary is at `HomepageDemoHero`. Children are server-rendered in `page.tsx` and passed as `ReactNode` props. This boundary does NOT change. The `children` slot simply renders earlier in the JSX tree (above video instead of below).

## Change Details

### C-1: Hero Badge Size Increase (page.tsx, lines 63-96)

Inline style edits on the hero `FEATURED_AGENTS` badge `<span>` elements:

| Property | Before | After |
|---|---|---|
| `fontSize` | `0.625rem` | `0.75rem` |
| `height` | `20px` | `26px` |
| `padding` | `0.125rem 0.3125rem` | `0.25rem 0.5rem` |
| `img width/height` | `11` | `14` |
| `dot width/height` | `4` | `5` |

Text color (`rgba(230,237,243,0.7)`) and border formula (`accentColor + "40"`) unchanged.

### C-2: Children Above Video (HomepageDemoHero.tsx)

Current JSX order inside the max-width container:
1. Video container + play/pause
2. CLI copy row (standalone)
3. `{children}` (heading, stats, badges)

New order:
1. `{children}` (heading, stats, badges)
2. Video container + play/pause + copy button overlay

Implementation: Move the `{children && ...}` block before the video `<div>`. Remove `marginTop: "1.25rem"` from children wrapper (it becomes the first element). Add `marginBottom: "1.25rem"` to the children wrapper to space it from the video below.

### C-3: Standalone Flaws Stat Callout (page.tsx, lines 49-57)

Extract the inline `<span>` containing "36.82% have flaws" from inside the `<p>` and render it as a separate `<div>` block between the paragraph and the "Works with" badges row.

```
Before:  <p>...scanned... <span>36.82% have flaws</span></p>
After:   <p>...scanned...</p>
         <div style={{ callout styles }}>
           <span>36.82%</span> have flaws · <a>Scan results</a>
         </div>
```

Callout styles:
- `borderLeft: "2px solid rgba(245,158,11,0.4)"`
- `paddingLeft: "0.625rem"`
- `marginTop: "0.5rem"`
- `fontSize: "0.8125rem"`, `color: "rgba(230,237,243,0.6)"`
- `fontFamily: mono`

### C-4: Bottom Badge Size Increase (page.tsx, lines 244-283)

Inline style edits on the bottom "Works with" section badges:

| Property | Featured Before | Featured After | Non-Featured Before | Non-Featured After |
|---|---|---|---|---|
| `fontSize` | `0.6875rem` | `0.8125rem` | `0.625rem` | `0.75rem` |
| `height` | `22px` | `28px` | `20px` | `24px` |
| `padding` | `0.1875rem 0.4375rem` | `0.25rem 0.5625rem` | `0.125rem 0.375rem` | `0.1875rem 0.4375rem` |
| `img w/h` | `13` | `16` | `11` | `14` |
| `dot w/h` | `5` | `6` | `4` | `5` |

### C-5: CLI Copy Button in Video Overlay (HomepageDemoHero.tsx)

Remove the standalone CLI copy `<div>` (lines 119-161). Add a pill-shaped copy button inside the video container `<div>` (sibling to the play/pause button), positioned `bottom: 0.75rem; left: 0.75rem`.

Button styles:
- `borderRadius: "999px"` (pill shape)
- `background: "rgba(0,0,0,0.6)"`
- `backdropFilter: "blur(4px)"`
- `border: "1px solid rgba(255,255,255,0.2)"`
- `fontFamily: mono`, `fontSize: "0.6875rem"`, `color: "#fff"`
- `padding: "0.375rem 0.75rem"`
- `className="video-copy-btn"` for CSS hover/responsive rules

### C-6: CSS Rules (globals.css)

Add after existing `.video-play-btn:hover` block:

```css
.video-copy-btn {
  transition: background-color 180ms ease, border-color 180ms ease;
}

.video-copy-btn:hover {
  background: rgba(0, 0, 0, 0.8) !important;
  border-color: rgba(255, 255, 255, 0.4) !important;
}

@media (max-width: 480px) {
  .video-copy-btn {
    font-size: 0.5625rem !important;
    padding: 0.25rem 0.5rem !important;
  }
}
```

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Children-above-video breaks visual flow | Low | Spec is explicit about the order; this matches the original design intent |
| Badge size increase causes line-wrap on narrow viewports | Low | Existing `flexWrap: "wrap"` handles overflow; badges are already responsive |
| Copy button overlaps video content at small viewports | Low | 480px responsive rule shrinks font/padding; button is positioned at bottom-left, away from play/pause at bottom-right |

## Implementation Order

1. **C-6** -- Add CSS rules first (no visual impact until className is used)
2. **C-1** -- Hero badge sizes (isolated inline style changes)
3. **C-4** -- Bottom badge sizes (isolated inline style changes)
4. **C-3** -- Flaws stat callout extraction (page.tsx structural change)
5. **C-2** -- Children above video (HomepageDemoHero.tsx layout reorder)
6. **C-5** -- CLI copy button overlay (HomepageDemoHero.tsx, depends on C-6 CSS)

Each change is independently deployable. No change depends on another except C-5 using the CSS class from C-6.

## Domain Skill Delegation

No domain skills needed. This is CSS-only work within existing React components -- no frontend architecture decisions, no new component abstractions, no state management changes. Direct implementation via `sw:do` is appropriate.
