# Architecture Plan: Skill Detail Page Redesign

## Summary

Single-file refactor of `src/app/skills/[name]/page.tsx` (810 lines -> target <700). Restructures the SkillDetailPage component to establish a clear information hierarchy: hero zone above the fold, duplicate elimination, compact inline stats, and progressive disclosure for secondary content. All changes are scoped to this one file. No shared components, APIs, or dependencies change.

## ADR Review

No new ADRs required. This is a presentational refactor within a single page component. No new architectural patterns, data flows, or dependencies are introduced. Existing inline-style convention (already established throughout the file and the broader vskill-platform codebase) is retained.

## Decision 1: Component Inventory (Delete, Add, Keep)

### Delete

| Component | Lines | Reason |
|-----------|-------|--------|
| `StatCard` | 748-777 | Replaced by inline stat spans in a single flex row |
| `MetaRow` | 733-746 | All meta data moves to hero byline; no remaining callers |

### Add

| Component | Purpose |
|-----------|---------|
| `InlineStat` | Renders `label: value` as a compact mono-font span. Accepts `label: string`, `value: string`. Used in the stats row. Eliminates the bordered-box overhead of StatCard. |

### Keep (unchanged)

- `BlockedSkillView` (lines 594-729) -- out of scope per spec
- All shared imports (`SectionDivider`, `TerminalBlock`, `TierBadge`, `TrustBadge`, `RepoHealthBadge`, `RepoLink`, `ReportProblemModal`, `TaintWarning`)

Note: `SectionDivider` remains imported because it is still used for "Extension Points" and "Security" headings. The header, Popularity, Install, Badge, and Works With usages are removed.

### SectionDivider Usage After Redesign

| Current Usage | After Redesign |
|---------------|----------------|
| `SectionDivider title={skill.displayName}` (header) | Replaced by `h1` element |
| `SectionDivider title="Popularity"` | Removed; section replaced by inline stat row |
| `SectionDivider title="Install"` | Replaced by small mono-font "Install" label |
| `SectionDivider title="Badge"` | Replaced by `details/summary` |
| `SectionDivider title="Security"` | Kept -- security section retains its divider |
| `SectionDivider title="Extension Points"` | Kept -- extension points section unchanged |
| `SectionDivider title="Works with"` | Replaced by `details/summary` (universal) or small label (specific) |

## Decision 2: Section Rendering Order

The new top-to-bottom order maps directly to FR-001 from the spec:

```
1.  Back link              (existing, unchanged)
2.  Hero zone
    2a. h1 row             (skill name + TierBadge + TrustBadge + version)
    2b. Byline row         (author | category | repo+health | source | updated)
3.  Taint warning          (conditional, unchanged logic)
4.  Description            (existing paragraph, unchanged)
5.  Labels/pills row       (filtered displayLabels only -- no category, no extensible, no tier)
6.  Install section        (mono label + TerminalBlock, no SectionDivider)
7.  Extensible one-liner   (conditional, compact replacement)
8.  Security scans         (SectionDivider kept, chips become horizontal flex row)
9.  Compact stats row      (InlineStat spans, pipe-separated)
10. Extension Points       (conditional, unchanged section)
11. Badge embed            (details/summary wrapper)
12. Works With             (details/summary for universal, open for specific)
13. Report a problem       (existing, unchanged)
```

### Key Ordering Changes vs Current

- Install moves from position ~8 (after Meta, Popularity) to position 6 (immediately after description). This satisfies "install above the fold on 1080p" success criterion.
- Popularity (now "Compact stats") moves from position ~5 (before Meta) to position 9 (after security). Stats inform but do not dominate.
- Meta section is eliminated entirely; its data is absorbed into the hero byline.
- Badge moves from position ~7 to position 11 (collapsed).

## Decision 3: Hero Zone Structure

```
+-- Hero Row (flex, align-items: center, gap: 0.75rem, flex-wrap: wrap) ---+
|  h1 (displayName, fontSize 1.5rem)                                       |
|  TierBadge (existing component)                                          |
|  TrustBadge (existing component, conditional)                            |
|  span "v{currentVersion}" (mono, text-faint)                             |
+--------------------------------------------------------------------------+

+-- Byline Row (flex, flex-wrap, gap: 0.5rem, mono, text-faint) -----------+
|  author-link . category-text . RepoLink+RepoHealthBadge . source . date  |
+--------------------------------------------------------------------------+
```

### h1 Styling

```
fontSize: "1.5rem"
fontWeight: 700
fontFamily: MONO
letterSpacing: "-0.02em"
color: "var(--text)"
margin: 0
```

This is semantically correct (h1 for the page title) and visually differentiated from SectionDivider (which renders as a styled div, not a heading element). SectionDivider uses 1.125rem; the h1 uses 1.5rem for clear hierarchy.

### Byline Separator

Middle-dot character (`\u00B7`) in `text-faint` color between each item. Items wrap naturally via `flex-wrap: wrap`. Each item is a `span` (or `a` for links) so the row degrades gracefully on narrow viewports.

### Data Migration from Meta Section

| Old Meta Row | New Location |
|---|---|
| Author (link) | Byline item 1 |
| Category | Byline item 2 (plain text from CATEGORY_LABELS) |
| Version | Hero row (after badges) |
| Repository + RepoHealthBadge | Byline item 3 |
| Source (skillPath link) | Byline item 4 |
| Last Updated | Byline item 5 |

## Decision 4: Duplicate Elimination Map

| Data Point | Current Locations | After Redesign |
|---|---|---|
| Category | Badge pill row, MetaRow, (CATEGORY_LABELS) | Byline only |
| Extensible/Semi-Extensible | Callout block (lines 167-225), badge pill | One-liner below install |
| Author | MetaRow | Byline link |
| Version | MetaRow | Hero row inline |
| Repository | MetaRow | Byline |
| Source path | MetaRow | Byline |
| Last Updated | MetaRow | Byline |
| Cert tier | TierBadge (kept) | TierBadge in hero row (single location) |
| Trust tier | TrustBadge (kept) | TrustBadge in hero row (single location) |

### Extensible One-Liner Design

Replaces both the callout block (lines 167-225) and the extensible badge pill (lines 243-255). Renders as a single line below the install section:

```
"Semi-Extensible -- supports customization via skill-memories. Learn more"
```

- Mono font, `fontSize: 0.8125rem`, `color: var(--text-muted)`
- Tier color applied to the tier label prefix
- "Learn more" links to the extensible skills standard docs page
- No border-left, no background -- just a compact text line

## Decision 5: Compact Stats Row (InlineStat)

### InlineStat Component

```typescript
function InlineStat({ label, value }: { label: string; value: string }) {
  return (
    <span style={{
      fontFamily: MONO,
      fontSize: "0.8125rem",
      color: "var(--text-muted)",
    }}>
      <span style={{ color: "var(--text-faint)" }}>{label}</span>{" "}
      <span style={{ color: "var(--text)", fontWeight: 600 }}>{value}</span>
    </span>
  );
}
```

### Deduplication Rules

Applied in-line where stats are rendered:

1. If `npmDownloadsWeekly > 0`, suppress Monthly (`npmDownloads`) -- weekly is more granular
2. If `uniqueInstalls === vskillInstalls`, suppress Unique -- identical to total
3. Keep: Installs, Active 7d, Stars, Forks, Weekly (or Monthly if no weekly), 7d Trend

### Stats Row Layout

Single flex row with `gap: 0.75rem`, `flex-wrap: wrap`. Stats separated visually by the gap (no pipe characters needed -- the gap and the label/value pattern provide sufficient visual separation). The `metricsRefreshedAt` timestamp renders as a small note on a new line below.

## Decision 6: Security Scan Chips (Horizontal Layout)

The existing vertical column layout (`flexDirection: column`) changes to a horizontal flex row:

```
+-- Security Section -------------------------------------------------+
|  SectionDivider title="Security"                                    |
|  [T1 Pattern PASS 92] [T2 LLM PASS] [ExtScan PASS 95] View report  |
+---------------------------------------------------------------------+
```

### Style Changes

- Parent container: `display: flex`, `flexWrap: wrap`, `gap: 0.5rem`, `alignItems: center`
- Remove `flexDirection: column`
- Each scan chip: keep existing pill styling (border-radius 999px, colored background)
- Add scan label as prefix text inside the chip: `"T1 PASS 92/100"` format (compact, no separate label/value layout)
- "View full security report" link renders as the last item in the flex row (after all chips)
- Certified date row remains below the chip row if applicable
- `scanRowStyle` and `scanLabelStyle` constants are replaced by new `chipRowStyle` and `scanChipStyle`

### Chip Internal Structure

Each chip is a single `span`:
```
<span style={scanChipStyle(color)}>
  {label} {status}{score ? ` ${score}/100` : ""}
</span>
```

Label text (e.g., "T1", "T2", provider name) is included inside the chip to keep the layout single-row.

## Decision 7: Progressive Disclosure (details/summary)

### Badge Embed Section

```html
<details>
  <summary style={summaryStyle}>Badge embed</summary>
  <div style={{ marginTop: "0.75rem" }}>
    <img ... />
    <TerminalBlock compact>{badgeMd}</TerminalBlock>
  </div>
</details>
```

### Works With Section

**Universal skills** (`isUniversal === true`):
```html
<details>
  <summary style={summaryStyle}>
    Works with all agents ({visibleAgents.length})
  </summary>
  <div style={{ marginTop: "0.75rem" }}>
    {/* agent pill grid, unchanged */}
  </div>
</details>
```

**Specific skills** (`isUniversal === false`):
```html
<div>
  <span style={sectionLabelStyle}>Works with</span>
  <p style={...}>Verified compatible with:</p>
  {/* agent pill grid, unchanged */}
</div>
```

### Summary Styling

Native `details/summary` with consistent styling:
```
fontFamily: MONO
fontSize: "0.875rem"
fontWeight: 600
color: "var(--text)"
cursor: "pointer"
letterSpacing: "-0.01em"
```

The browser-native disclosure triangle provides the expand/collapse affordance. No custom icons needed.

## Decision 8: Style Constants Organization

### Constants to Remove

| Constant | Reason |
|---|---|
| `basePillStyle` | Only used by category pill and extensible pill, both removed |
| `pillStyle` | Alias of basePillStyle, only used for displayLabels (redefined as labelPillStyle) |
| `scanRowStyle` | Replaced by horizontal chip layout |
| `scanLabelStyle` | Label moves inside chip |

### Constants to Add

| Constant | Purpose |
|---|---|
| `heroRowStyle` | Flex row for h1 + badges + version |
| `bylineStyle` | Flex-wrap row for author/category/repo/source/date items |
| `bylineItemStyle` | Individual byline item (mono, faint, small) |
| `bylineSepStyle` | Middle-dot separator styling |
| `sectionLabelStyle` | Small mono label replacing SectionDivider for Install, etc. |
| `chipRowStyle` | Horizontal flex row for security chips |
| `scanChipStyle` | Function returning chip CSSProperties given a color |
| `statsRowStyle` | Flex-wrap row for InlineStat items |
| `summaryStyle` | Shared details/summary trigger styling |
| `labelPillStyle` | For remaining displayLabels (replaces basePillStyle) |

### Constants to Keep

| Constant | Reason |
|---|---|
| `MONO` | Used throughout |
| `TIER_LABELS` | Used in metadata and badge |

## Decision 9: Responsive Strategy

No new CSS classes or media queries needed. The design relies entirely on `flex-wrap: wrap` for responsive behavior, which is the existing pattern throughout this file.

### Wrapping Behavior by Section

| Section | Mechanism | Narrow Viewport Result |
|---|---|---|
| Hero row (h1 + badges) | `flex-wrap: wrap` | Name on first line, badges wrap to second |
| Byline row | `flex-wrap: wrap` | Items stack into 2-3 lines |
| Security chips | `flex-wrap: wrap` | Chips stack vertically |
| Stats row | `flex-wrap: wrap` | Stats wrap into multiple lines |
| Labels row | `flex-wrap: wrap` | Already wraps (unchanged) |
| Agent pills | `flex-wrap: wrap` | Already wraps (unchanged) |

The existing `globals.css` media queries at `768px` and `480px` do not target this page specifically, and since everything uses inline styles with flex-wrap, no additional breakpoint handling is required.

## Decision 10: Line Count Budget

| Section | Current Lines (approx) | Target Lines |
|---|---|---|
| Imports + types + constants | 30 | 30 |
| Metadata + helpers | 40 | 40 |
| Back link | 10 | 10 |
| Hero zone (h1 + byline) | 0 (new) | 45 |
| Taint warning | 2 | 2 |
| Description | 8 | 8 |
| Labels/pills | 10 | 8 |
| Extensible callout | 60 | 0 (deleted) |
| Meta section | 60 | 0 (deleted) |
| Popularity (StatCards) | 30 | 0 (deleted) |
| Install | 8 | 10 |
| Extensible one-liner | 0 (new) | 15 |
| Security chips | 80 | 45 |
| Stats row | 0 (new) | 25 |
| Extension Points | 50 | 50 |
| Badge embed | 25 | 20 |
| Works With | 65 | 55 |
| Report button | 4 | 4 |
| BlockedSkillView | 135 | 135 |
| MetaRow + StatCard | 50 | 0 (deleted) |
| InlineStat | 0 (new) | 12 |
| Style constants | 30 | 40 |
| **Total** | **~810** | **~604** |

Target is well under the 700-line ceiling.

## Implementation Order

Tasks should be executed in this sequence to minimize conflicts:

1. **Add new style constants and InlineStat component** -- additive, no breakage
2. **Rewrite hero zone** (h1 + byline) -- replaces SectionDivider header and absorbs meta data
3. **Delete meta section** -- byline now renders all meta fields
4. **Move install section up**, replace SectionDivider with mono label
5. **Replace extensible callout + badge pill with one-liner** -- consolidate to single location
6. **Remove category pill from badges row** -- now in byline only
7. **Convert security section to horizontal chips**
8. **Replace StatCard/Popularity with InlineStat row** -- includes dedup logic
9. **Wrap badge embed in details/summary**
10. **Wrap Works With in details/summary** (universal only)
11. **Delete StatCard, MetaRow components and old style constants**
12. **Verify SectionDivider import** is still needed (Extension Points + Security use it)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Native `details/summary` styling inconsistency across browsers | Low | Apply explicit font/color via `summaryStyle`; disclosure triangle is universally supported |
| Removing `basePillStyle` breaks `displayLabels` rendering | Medium | Replace with `labelPillStyle` in the same task that removes `basePillStyle` |
| Byline row too long on desktop | Low | `flex-wrap: wrap` ensures it breaks naturally; middle-dot separators remain legible |
| Security chips unreadable when too many external scans | Low | `flex-wrap` handles overflow; each chip is self-contained |

## Domain Skill Delegation

No domain skills recommended. This is a single-file UI refactor using existing inline styles and React patterns already established in the codebase. No new framework, design system, or build tooling is involved.
