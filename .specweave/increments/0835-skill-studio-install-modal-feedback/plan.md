# Implementation Plan: Skill Studio — in-panel install feedback + escape hotkey

## Overview

Two surgical client-side changes in `vskill-platform` Studio detail surface:

1. **`InstallPanel.tsx`** — promote the existing `toast` string state to a structured `feedback: { state: 'idle' | 'success' | 'error', command: string | null }`, replace the small muted `studio-install-toast` div with a prominent banner positioned directly under the Install button (above the multi-variant terminal block), and switch the success/error visual treatment to platform status tokens.

2. **`page.tsx`** — extract the `← Back to results` link + a new `<kbd>Esc</kbd>` chip into a small client component (`DetailHeader`) that registers a `window` keydown listener for Escape, navigating to `backHref` while deferring to SearchPalette and skipping editable focus targets.

No backend changes. No new dependencies. No schema or API changes.

## Architecture

### Components

| File | Change | Purpose |
|------|--------|---------|
| `src/app/studio/find/[owner]/[repo]/[skill]/InstallPanel.tsx` | Modify | Owns feedback state + banner render |
| `src/app/studio/find/[owner]/[repo]/[skill]/page.tsx` | Modify | Replace inline back-link with `<DetailHeader>` |
| `src/app/studio/find/[owner]/[repo]/[skill]/DetailHeader.tsx` | **New** | Client component: back link + `<kbd>Esc</kbd>` + Escape keydown listener |

### Data flow (UI state only)

```
User clicks Install
  → runInstallAction()
  → copyViaClipboard(command)
    → ok? → setFeedback({ state: 'success', command })
              → focus(backLinkRef)
              → schedule auto-dismiss (6s → 'idle')
    → !ok → setFeedback({ state: 'error', command })
              → schedule auto-dismiss (6s → 'idle')
  → fire-and-forget telemetry POST (unchanged)
```

### Escape key flow (DetailHeader.tsx)

```
window keydown
  → key === 'Escape'?
    → SearchPalette open? (probe DOM via aria-modal=true on palette dialog)
        → bail; palette handles it
    → focus in editable target? (input/textarea/select/contenteditable)
        → bail
    → router.push(backHref)
```

## Technology Stack

- **Language/Framework**: TypeScript, React 19 (already in vskill-platform)
- **Libraries**: `next/navigation` for `useRouter`, no new dependencies
- **Tokens**: `--status-success-{text,bg,border}`, `--status-danger-{text,bg,border}` (already defined in `globals.css:107-115`)
- **Tests**: Vitest + Testing Library (existing), Playwright for the page-level Escape happy path

**Architecture decisions**:

- **Banner over toast**: A persistent in-flow banner at the action site is more discoverable than a small muted message at the bottom of the panel. Position-wise the banner sits directly below the Install button so the eye lands on it without scanning. Alternative considered: floating toast (sonner/react-hot-toast) — rejected because the project already avoids global toast libs (no Toaster mount in the tree) and floating toasts are exactly what the user reported as unreadable.

- **`DetailHeader` extraction**: `page.tsx` is a server component. The Escape handler needs `useRouter` + `useEffect`, both client-only. Extracting a tiny `"use client"` component is cheaper than converting the whole page (which would lose the existing ISR behavior, `revalidate = 3600`).

- **Palette-deference probe**: Using a DOM probe (looking for `[role="dialog"][aria-modal="true"]` rendered by SearchPalette when open) avoids cross-component coupling. Alternative: lift palette state to a context — rejected as a larger blast radius for a single key check.

- **Focus-on-success**: Focusing the back link is a "next-step nudge" without auto-navigation. The user explicitly asked for "do the next step like closing this pop-up" — but the page is a server-rendered page, not a modal, and auto-navigating away would discard the just-copied command. Focusing the back link is the strongest hint we can give without robbing the user of choice.

- **Token-based banner colors**: Reuse the platform's `--status-success-*` and `--status-danger-*` CSS variables so the banner inherits theme behavior (light/dark) automatically.

## Implementation Phases

### Phase 1: Tests first (RED)
- Vitest: `InstallPanel.test.tsx`
  - Banner renders with success state after clipboard mock resolves true
  - Banner renders with error state after clipboard mock rejects
  - `aria-live="polite"` and `role="status"` present
  - Banner auto-dismisses after 6s (fake timers)
  - Per-variant Copy button drives same banner
- Vitest: `DetailHeader.test.tsx`
  - Escape calls `router.push(backHref)`
  - Escape ignored when `aria-modal="true"` dialog is in the DOM
  - Escape ignored when focus is in `<input>`
  - `removeEventListener` called on unmount
- Playwright (one happy path): `studio-install-feedback.spec.ts`
  - Open detail page → click Install → see success banner with copied command → press Esc → land on `/studio/find?q=<query>`

### Phase 2: Implementation (GREEN)
- Add `DetailHeader.tsx` client component
- Update `page.tsx` to render `<DetailHeader backHref={backHref} />` instead of inline `<Link>`
- Refactor `InstallPanel.tsx`:
  - Replace `toast: string | null` with `feedback: FeedbackState`
  - Replace `studio-install-toast` div with `<FeedbackBanner state={...} command={...} />`
  - Update `runInstallAction` and per-variant Copy handlers to set feedback
  - On `state === 'success'`, call `backLinkRef.current?.focus({ preventScroll: true })`
- Wire `backLinkRef` from `DetailHeader` down or up via a focus-handle ref (simplest: a custom event `studioFocusBack` or — preferred — a lifted ref via a small client component wrapping both, but keeping change minimal: dispatch a custom event from InstallPanel and listen in DetailHeader for `studio-focus-back-link`)

### Phase 3: Refactor + a11y polish
- Ensure banner copy is screen-reader friendly (verb-first)
- Verify reduced-motion: no animations on banner mount
- Verify kbd chip styling matches `SearchPalette`'s convention
- Snapshot-test trim where useful

## Testing Strategy

- **Unit (Vitest + Testing Library)** — covers all banner state transitions, Escape predicate logic, listener lifecycle. Coverage target: 95% on the changed files.
- **E2E (Playwright)** — single happy-path spec asserts the user-visible loop: visit → click Install → banner visible with copied command → Esc → back at results page.
- **Manual (preview_*)** — start the platform dev server, navigate to a real skill detail, click Install, verify banner contrast and position on light + dark themes via `preview_screenshot`. Verify Esc round-trip.

## Technical Challenges

### Challenge 1: Clipboard API behavior in tests
**Solution**: Mock `navigator.clipboard.writeText` via `vi.stubGlobal`. The fallback `document.execCommand` path is exercised by stubbing `navigator.clipboard` undefined and mocking `execCommand`.
**Risk**: jsdom's clipboard mock returning undefined silently pushes us into the fallback path — already handled by the existing pattern in `copyViaClipboard`.

### Challenge 2: Page-level Escape vs SearchPalette Escape
**Solution**: DOM-probe for `[role="dialog"][aria-modal="true"]` (the convention SearchPalette uses for its overlay). When found, the DetailHeader handler bails early.
**Risk**: SearchPalette internals change and stop using `aria-modal`. Mitigation: integration test asserts the DOM probe selector matches when palette is open.

### Challenge 3: Focus management without scroll jank
**Solution**: `backLinkRef.current?.focus({ preventScroll: true })` — modern browsers honor the option and skip scroll-into-view.
**Risk**: Older browsers may ignore `preventScroll` and scroll. Mitigation: project targets evergreen browsers per platform's existing baseline; non-issue.

## ADR notes

No new ADR required. This change is consistent with existing platform conventions:
- Status tokens used elsewhere (e.g., `TaintWarning`)
- Client-component extraction pattern already used in this same folder (`InstallPanel`, `VersionPicker`)
- Window keydown listener pattern already used in `SearchPalette`
