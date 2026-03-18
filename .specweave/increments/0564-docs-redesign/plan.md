# Architecture Plan: 0564-docs-redesign

## Overview

Full redesign of the documentation section at `repositories/anton-abyzov/vskill-platform/src/app/docs/`. Introduces a three-column docs layout (sidebar nav + main content + right TOC), shared documentation components, 4 new pages, and redesigned existing pages -- all preserving the existing monospace/terminal aesthetic.

## Architecture Decisions

### AD-1: DocsLayout via Next.js App Router layout.tsx

**Decision**: Create `docs/layout.tsx` as the layout wrapper for all docs pages. This is the standard Next.js App Router pattern -- the layout wraps all `docs/**` routes automatically.

**Structure**:
```
docs/
  layout.tsx          <-- DocsLayout wrapper (new)
  DocsLayout.tsx      <-- Client component (new)
  nav.ts              <-- Navigation config (new)
  page.tsx            <-- Docs index (redesign)
  getting-started/
    page.tsx          <-- Redesign
  security-guidelines/
    page.tsx          <-- Redesign
  cli-reference/
    page.tsx          <-- NEW
  plugins/
    page.tsx          <-- NEW
  submitting/
    page.tsx          <-- NEW
  faq/
    page.tsx          <-- NEW
```

**Rationale**: App Router layouts persist across navigations within the route segment. The sidebar, TOC, and wrapper chrome render once; only `{children}` (the page content) swaps. This gives instant-feel navigation with zero layout shift.

### AD-2: Three-Column Layout with CSS Grid

**Decision**: Use CSS Grid for the three-column layout, not Flexbox.

```
┌──────────────────────────────────────────────────────┐
│                    Site Header/Nav                    │
├────────────┬──────────────────────┬──────────────────┤
│  Sidebar   │    Main Content      │   TOC (right)    │
│  240px     │    1fr               │   200px          │
│  fixed     │    max-width: 720px  │   sticky         │
│            │    scrollable        │                  │
│  Collaps-  │                      │   Auto-generated │
│  ible      │                      │   from headings  │
│  sections  │                      │   in page        │
│            │                      │                  │
│  Active    │                      │   Scroll-spy     │
│  indicator │                      │   highlight      │
├────────────┴──────────────────────┴──────────────────┤
│                    Site Footer                        │
└──────────────────────────────────────────────────────┘
```

**Grid definition**:
```css
grid-template-columns: 240px minmax(0, 1fr) 200px;
```

**Responsive breakpoints** (matching existing site patterns at 768px and 480px):
- `>1080px`: Full three-column layout
- `768-1080px`: Two columns (sidebar + content), TOC hidden
- `<768px`: Single column, sidebar becomes hamburger overlay (consistent with MobileNav pattern)

**Rationale**: Grid gives explicit column sizing control. The sidebar at 240px matches docs convention (Stripe 250px, Vercel 240px, Next.js 240px). The right TOC at 200px is narrow enough to not compete with content. The existing site uses `maxWidth: 960` for content -- the three-column layout expands the page container to accommodate sidebar + content + TOC while keeping the content area itself around 720px (readable line length for prose).

### AD-3: Client vs Server Component Boundaries

**Decision**: Minimize client components. Use the "client island" pattern where only interactive leaf components are `"use client"`.

| Component | Rendering | Reason |
|-----------|-----------|--------|
| `docs/layout.tsx` | **Server** | Static HTML wrapper, no interactivity |
| `DocsLayout` | **Client** | Sidebar toggle state, TOC scroll-spy, responsive breakpoint detection |
| Individual page.tsx | **Server** | Static content, metadata export (incompatible with `"use client"`) |
| `CodeBlock` | **Client** | Already exists as client component (copy button state) |
| `Callout` | **Server** | Already exists as server component (no state) |
| `SectionDivider` | **Server** | Already a server component |
| `TerminalBlock` | **Server** | Already a server component |
| `TreeList` | **Server** | Already a server component |
| `DocCard` | **Server** | Static links, no interactivity |
| `StepList` | **Server** | Static numbered list rendering |
| `TabGroup` | **Client** | Active tab state management |
| `DocsSidebar` (sub-component) | Part of DocsLayout client boundary | Toggle state for collapsible sections |
| `DocsToc` (sub-component) | Part of DocsLayout client boundary | Scroll-spy IntersectionObserver |

**Rationale**: Next.js App Router defaults to server components. Each `"use client"` boundary pulls the entire subtree into the client bundle. By keeping pages as server components and isolating interactivity into leaf components (CodeBlock, TabGroup) and the layout wrapper (DocsLayout), we minimize JS shipped to the client. The page content (which is the heaviest part) stays as zero-JS server-rendered HTML.

**Key constraint**: `docs/layout.tsx` itself exports a Server Component that renders the `<DocsLayout>` client component. This is because `layout.tsx` needs to stay a server component to support `metadata` exports in child pages. The pattern:

```tsx
// docs/layout.tsx (SERVER component)
import DocsLayout from "./DocsLayout";

export default function Layout({ children }) {
  return <DocsLayout>{children}</DocsLayout>;
}
```

```tsx
// docs/DocsLayout.tsx (CLIENT component)
"use client";
export default function DocsLayout({ children }) {
  // sidebar toggle, TOC scroll-spy, etc.
}
```

### AD-4: Navigation Data Structure

**Decision**: Centralized navigation config as a typed constant in a dedicated module `docs/nav.ts`.

```typescript
// docs/nav.ts

export interface NavItem {
  title: string;
  href: string;
  badge?: string;
  badgeColor?: string;
}

export interface NavSection {
  title: string;         // Section heading (e.g., "Getting Started", "Reference")
  items: NavItem[];
  defaultOpen?: boolean; // Whether section starts expanded
}

export const DOCS_NAV: NavSection[] = [
  {
    title: "Getting Started",
    defaultOpen: true,
    items: [
      { title: "Introduction", href: "/docs" },
      { title: "Getting Started", href: "/docs/getting-started", badge: "v0.4.16", badgeColor: "var(--code-green)" },
    ],
  },
  {
    title: "Guides",
    defaultOpen: true,
    items: [
      { title: "Submitting a Skill", href: "/docs/submitting" },
      { title: "Security Guidelines", href: "/docs/security-guidelines" },
    ],
  },
  {
    title: "Reference",
    defaultOpen: true,
    items: [
      { title: "CLI Reference", href: "/docs/cli-reference" },
      { title: "Plugins", href: "/docs/plugins" },
    ],
  },
  {
    title: "Support",
    defaultOpen: false,
    items: [
      { title: "FAQ", href: "/docs/faq" },
    ],
  },
];
```

**Breadcrumbs**: Derived from `DOCS_NAV` at render time. Given a pathname, walk the nav tree to find the matching item and its parent section. No separate breadcrumb config needed.

**Rationale**: A single source of truth for navigation avoids the sidebar and breadcrumbs drifting out of sync. The data is static (no database, no API call), so it lives as a plain TypeScript constant. The `NavSection` grouping with `defaultOpen` drives both sidebar rendering and collapsible section state initialization.

### AD-5: State Management -- Minimal, Component-Local

**Decision**: No external state management library. Use React `useState` for all interactive state.

**State inventory**:

| State | Location | Type | Persistence |
|-------|----------|------|-------------|
| Sidebar open/closed (mobile) | DocsLayout | `boolean` | None (resets on nav) |
| Sidebar section collapse | DocsLayout | `Record<string, boolean>` | None (initialized from `defaultOpen`) |
| TOC active heading | DocsLayout | `string` (heading ID) | None (driven by scroll position) |
| TabGroup active tab | TabGroup | `number` (index) | None (defaults to 0) |
| CodeBlock copied state | CodeBlock | `boolean` | None (auto-resets after 1.5s) |

**Rationale**: All state is UI-ephemeral. No state needs to persist across page loads, sync to a server, or be shared between distant components. `useState` is the simplest correct solution. Adding a state library (Zustand, Jotai) would be overengineering for toggle booleans and scroll position tracking.

### AD-6: TOC Auto-Generation via Heading IDs

**Decision**: Each page assigns `id` attributes to section headings (`<h2 id="...">`, `<h3 id="...">`). The TOC component in DocsLayout reads these from the DOM using `IntersectionObserver` for scroll-spy highlighting.

**Approach**: Since pages are server components that render to static HTML, the headings and their IDs exist in the DOM on mount. DocsLayout (client component) runs a `useEffect` on mount to:
1. Query all `h2[id], h3[id]` elements within the content area
2. Build the TOC list from these elements
3. Set up an `IntersectionObserver` to track which heading is currently in view
4. Highlight the active heading in the right TOC column

**Rationale**: This is the standard approach used by Docusaurus, Nextra, and the Next.js docs site. It avoids requiring page authors to manually pass a TOC data structure -- they just add IDs to headings, which is natural HTML.

**Alternative considered**: Passing a static `toc` prop from each page to the layout. Rejected because: (a) layout.tsx cannot receive props from child pages in App Router, (b) it duplicates information already in the rendered HTML, (c) it creates a maintenance burden where heading text must be kept in sync between the page and the toc array.

### AD-7: Reuse Existing Components, Do Not Duplicate

**Decision**: The existing `CodeBlock`, `Callout`, `SectionDivider`, `TerminalBlock`, `TreeList`, `VerdictBadge`, and `SeverityBadge` components are already implemented and match the design system. Reuse them as-is.

**CodeBlock**: Already exists at `components/CodeBlock.tsx` as a `"use client"` component with copy button, language/filename header, and compact mode. No changes needed.

**Callout**: Already exists at `components/Callout.tsx` as a server component with `info`, `warning`, `danger` variants. No changes needed.

**New components to create**:

| Component | File | Rendering | Description |
|-----------|------|-----------|-------------|
| `DocsLayout` | `docs/DocsLayout.tsx` | Client | Three-column layout with sidebar toggle, section collapse, TOC scroll-spy |
| `DocCard` | `components/DocCard.tsx` | Server | Card link for docs index page (title, description, badge, arrow) |
| `StepList` | `components/StepList.tsx` | Server | Numbered step list with terminal aesthetic (numbered circles, connecting line) |
| `TabGroup` | `components/TabGroup.tsx` | Client | Tabbed content switcher with underline active indicator |

### AD-8: Styling Approach -- Inline Styles with CSS Custom Properties

**Decision**: Continue the existing pattern of inline styles using CSS custom properties. No CSS-in-JS libraries, no CSS modules, no Tailwind.

**Rationale**: The entire vskill-platform codebase uses inline `style={{}}` with `var(--property)` references. Every existing component (SectionDivider, TerminalBlock, TreeList, CodeBlock, Callout, VerdictBadge, LayoutShell, MobileNav) follows this pattern. Introducing a different styling approach would create inconsistency.

**Hover/transition states**: Use CSS classes defined in `globals.css` (matching existing patterns like `.nav-link`, `.doc-card`, `.skill-row`). New classes needed:
- `.docs-sidebar-link` -- hover state for sidebar nav items
- `.docs-sidebar-link.active` -- active page indicator
- `.docs-toc-link` -- hover state for TOC items
- `.docs-toc-link.active` -- scroll-spy active heading
- `.docs-sidebar-section` -- collapsible section toggle

## Component Architecture

### DocsLayout (Client Component)

```
DocsLayout
├── DocsSidebar (inline, not separate component)
│   ├── Logo/heading area
│   ├── NavSection[] (collapsible groups)
│   │   ├── Section title (clickable to toggle)
│   │   └── NavItem[] (links with active indicator)
│   └── Mobile close button
├── Main content area
│   └── {children} (page content from route)
└── DocsToc (inline, not separate component)
    ├── "On this page" heading
    └── Heading list (auto-populated from DOM)
```

**Props**: `{ children: React.ReactNode }`

**Internal state**:
- `sidebarOpen: boolean` -- mobile sidebar visibility
- `sectionState: Record<string, boolean>` -- which nav sections are expanded
- `activeHeading: string` -- ID of currently-visible heading for TOC highlight
- `tocItems: Array<{ id: string; text: string; level: number }>` -- populated on mount from DOM

**Why inline sub-components rather than separate files**: The sidebar and TOC share state with the layout (sidebar toggle, responsive breakpoint). Extracting them to separate client components would require prop-drilling or context for a small amount of state. Keeping them inline in DocsLayout keeps the component self-contained and avoids unnecessary file/module overhead for what are essentially render functions, not reusable components.

### TabGroup (Client Component)

```tsx
interface TabGroupProps {
  tabs: string[];           // Tab labels
  children: React.ReactNode[]; // One child per tab
}
```

**State**: `activeIndex: number`, defaulting to 0.

**Rendering**: Render tab buttons as a horizontal strip with underline active indicator. Render only `children[activeIndex]`.

**Styling**: Monospace font, terminal aesthetic. Active tab gets `border-bottom: 2px solid var(--text)`. Inactive tabs use `var(--text-muted)`.

### DocCard (Server Component)

```tsx
interface DocCardProps {
  title: string;
  description: string;
  href: string;
  badge?: string;
  badgeColor?: string;
}
```

**Rendering**: A card link (styled `<a>`) with title, description, optional badge, and a right arrow. Uses `.doc-card` class for hover state (already exists in globals.css).

**Difference from current index page inline cards**: Extracted to a reusable component so both the docs index and any future "related pages" sections can use it.

### StepList (Server Component)

```tsx
interface Step {
  title: string;
  content: React.ReactNode;
}

interface StepListProps {
  steps: Step[];
}
```

**Rendering**: Numbered steps with a vertical connecting line. Each step has a numbered circle (monospace, `var(--text-faint)` border) and content area. The line runs behind the circles connecting them vertically.

## File Inventory

### New Files

| File | Type | Size Est. |
|------|------|-----------|
| `docs/layout.tsx` | Server layout wrapper | ~10 lines |
| `docs/DocsLayout.tsx` | Client component | ~300 lines |
| `docs/nav.ts` | Navigation config | ~60 lines |
| `docs/page.tsx` | Redesigned index | ~80 lines (refactored to use DocCard) |
| `docs/cli-reference/page.tsx` | New page | ~250 lines |
| `docs/plugins/page.tsx` | New page | ~200 lines |
| `docs/submitting/page.tsx` | New page | ~180 lines |
| `docs/faq/page.tsx` | New page | ~200 lines |
| `components/DocCard.tsx` | Server component | ~50 lines |
| `components/StepList.tsx` | Server component | ~60 lines |
| `components/TabGroup.tsx` | Client component | ~70 lines |

### Modified Files

| File | Change |
|------|--------|
| `docs/getting-started/page.tsx` | Remove inline breadcrumb/nav, add heading IDs, use shared components |
| `docs/security-guidelines/page.tsx` | Remove inline breadcrumb/nav, add heading IDs, use shared components |
| `globals.css` | Add docs sidebar/TOC hover/active classes, responsive rules for docs layout |

### Preserved (no changes)

| File | Reason |
|------|--------|
| `components/CodeBlock.tsx` | Already complete with copy button |
| `components/Callout.tsx` | Already complete with three variants |
| `components/SectionDivider.tsx` | Terminal-style divider, used as-is |
| `components/TerminalBlock.tsx` | Base code display, used as-is |
| `components/TreeList.tsx` | Tree-style list, used as-is |
| `components/VerdictBadge.tsx` | Badge components, used on security-guidelines page |

## Responsive Design

### Breakpoint Strategy

Aligns with existing site breakpoints in `globals.css`:

| Breakpoint | Layout | Sidebar | TOC | Content Width |
|------------|--------|---------|-----|---------------|
| >1080px | Three-column grid | Fixed 240px | Fixed 200px | Fluid (max ~720px) |
| 768-1080px | Two-column grid | Fixed 240px | Hidden | Fluid |
| <768px | Single column | Hamburger overlay | Hidden | Full width (with padding) |

### Mobile Sidebar Behavior

Mirrors the existing `MobileNav` and `AdminLayout` patterns:
1. Hamburger button appears (fixed position)
2. Click opens sidebar as a full-height overlay
3. Dark backdrop behind sidebar
4. Click outside or click a link closes sidebar
5. Body scroll prevented while sidebar is open

### New CSS Classes for globals.css

```css
/* Docs sidebar link */
.docs-sidebar-link {
  transition: color 200ms ease, background-color 180ms ease;
  text-decoration: none;
}
.docs-sidebar-link:hover {
  color: var(--text);
  background-color: var(--bg-hover);
  text-decoration: none;
}
.docs-sidebar-link.active {
  color: var(--text);
  background-color: var(--bg-hover);
  font-weight: 600;
}

/* Docs TOC link */
.docs-toc-link {
  transition: color 200ms ease;
  text-decoration: none;
}
.docs-toc-link:hover {
  color: var(--text);
  text-decoration: none;
}
.docs-toc-link.active {
  color: var(--text);
}

/* Docs sidebar section toggle */
.docs-sidebar-section {
  cursor: pointer;
  transition: color 200ms ease;
}
.docs-sidebar-section:hover {
  color: var(--text);
}

/* Docs layout responsive */
@media (max-width: 1080px) {
  .docs-toc-col { display: none !important; }
  .docs-grid { grid-template-columns: 240px minmax(0, 1fr) !important; }
}
@media (max-width: 768px) {
  .docs-sidebar-col { display: none !important; }
  .docs-grid { grid-template-columns: 1fr !important; }
  .docs-hamburger { display: flex !important; }
}
```

## Data Flow

```
DOCS_NAV (static config)
    │
    ├──> DocsSidebar: renders nav sections + items
    │       │
    │       └──> usePathname(): determines active link
    │
    ├──> Breadcrumbs: derived from nav tree + current pathname
    │
    └──> (No connection to TOC -- TOC reads from DOM)

Page headings (h2[id], h3[id])
    │
    └──> DocsToc: reads on mount via querySelectorAll
            │
            └──> IntersectionObserver: tracks visible heading
                    │
                    └──> activeHeading state: highlights TOC link
```

## Implementation Order

1. **Phase 1: Infrastructure** -- `nav.ts`, `DocsLayout.tsx`, `docs/layout.tsx`, CSS classes in `globals.css`
2. **Phase 2: New shared components** -- `DocCard.tsx`, `StepList.tsx`, `TabGroup.tsx`
3. **Phase 3: Docs index redesign** -- Refactor `docs/page.tsx` to use DocCard + DocsLayout
4. **Phase 4: Existing page migration** -- Add heading IDs, remove inline breadcrumbs from getting-started and security-guidelines
5. **Phase 5: New pages** -- cli-reference, plugins, submitting, faq
6. **Phase 6: Polish** -- Responsive testing, scroll-spy tuning, visual QA

## Trade-offs

### Inline DocsLayout vs Separate Sidebar/TOC Components

**Chosen**: Keep sidebar and TOC as inline render logic within `DocsLayout.tsx`.

**Pro**: Single file to understand, shared state without prop-drilling or context, fewer imports.
**Con**: `DocsLayout.tsx` will be ~300 lines, which is moderate but manageable.
**Why not split**: Splitting would require either (a) a React context for shared state, adding complexity for 3-4 boolean values, or (b) prop-drilling through a component tree that has no reuse elsewhere. The sidebar and TOC are specific to the docs layout and will never be used independently.

### TOC from DOM vs Static Prop

**Chosen**: Read headings from DOM on mount.

**Pro**: Zero maintenance burden, always in sync with rendered content, no duplication.
**Con**: Requires a `useEffect` + DOM query on mount (minor flash possible if TOC renders before headings are parsed, but since server components render the headings in the initial HTML, they are available immediately).

### No MDX

**Chosen**: Keep pages as plain TSX with inline content.

**Rationale**: The existing docs pages use JSX directly with inline data arrays and component composition. Introducing MDX would require adding `@next/mdx`, configuring the build pipeline, and converting all existing pages. The content is not authored by non-developers, so MDX's markdown-friendliness adds no value here. TSX gives full type-safety and component composition without build tooling changes.

## Delegation

After plan approval, delegate implementation to `sw:architect` for the Next.js frontend domain. Implementation covers all phases listed above as a single cohesive unit -- no need for separate backend/infrastructure skills since this is purely a frontend change within the existing Next.js app.
