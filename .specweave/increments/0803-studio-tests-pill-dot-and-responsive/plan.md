# Plan — 0803 Studio Tests pill dot + responsive grid

## Architecture

Two independent edits in `repositories/anton-abyzov/vskill/src/eval-ui/`:

### 1. CSS contract for `.pill`

Move the `::before` bullet declaration from base `.pill` to the indicator modifiers (`.pill-installed`, `.pill-own`). This preserves the original "text + dot" semantics for status indicators while letting filled badges use `.pill` purely for layout.

```css
/* Base layout only, no bullet */
.pill { display: inline-flex; align-items: center; gap: 6px; … }

/* Bullet is opt-in via indicator modifiers */
.pill-installed::before,
.pill-own::before {
  content: "";
  width: 6px; height: 6px;
  border-radius: 50%;
  background: currentColor;
}
```

### 2. Responsive `.eval-cases-grid`

Replace the inline `style={{ display:"grid", gridTemplateColumns:"280px 1fr" }}` on the TestsPanel container with a class:

```css
.eval-cases-grid {
  display: grid;
  grid-template-columns: 280px 1fr;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

@media (max-width: 700px) {
  .eval-cases-grid { grid-template-columns: 1fr; }
}
```

700px breakpoint chosen because the detail pane needs ~420px to render the prompt/expected blocks legibly; below that we stack.

## Files

| Path | Change |
|---|---|
| `src/eval-ui/src/styles/globals.css` | Scope `.pill::before` to indicator modifiers + add `.eval-cases-grid` |
| `src/eval-ui/src/pages/workspace/TestsPanel.tsx` | Replace inline grid style with `className="eval-cases-grid"` |
| `src/eval-ui/src/styles/__tests__/pill-css.test.ts` | New: CSS contract regression test |
| `src/eval-ui/src/pages/workspace/__tests__/tests-panel-grid.test.tsx` | New: assert eval-cases grid className |

## Build / Distribution

- `npm run build:eval-ui` regenerates the Vite bundle.
- `npm run build` regenerates the CLI tsc output.
- Bump `repositories/anton-abyzov/vskill/package.json` from 1.0.8 → 1.0.9.
- `npm publish` from the vskill repo (registry: npmjs.org, public).

## Risks

- Other consumers of `.pill` losing the dot — mitigated by repo-wide grep showing zero TSX references that visually depend on the bullet (every consumer paints its own background fill).
- Media query collides with embedded studio layouts — mitigated by scoping to a custom class that is only applied in TestsPanel.

## Verification

- vitest: pill CSS contract + grid className tests pass.
- Bundle build succeeds, bundle size guard passes (`npm run lint:bundle-size`).
- Preview MCP: take screenshots at desktop/tablet/mobile widths; confirm dot absence and grid stacking.
- Existing TestsPanel suites continue to pass.
