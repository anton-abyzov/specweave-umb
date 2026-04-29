# Rubric — 0803 Studio Tests pill dot + responsive grid

## Quality Gates

| Gate | Criterion | Source of Truth |
|---|---|---|
| Visual correctness | StatusPill renders `--` without leading bullet | Preview MCP `getComputedStyle('.pill','::before').content === 'none'` |
| Indicator preserved | `.pill.pill-installed` retains the bullet | Preview MCP synthetic test |
| Responsive grid | At ≤700px the eval-cases container resolves to one column | Preview MCP `getComputedStyle('.eval-cases-grid').gridTemplateColumns` |
| Desktop unchanged | At ≥701px the grid still resolves to 280px + 1fr | Preview MCP |
| Regression tests | `pill-css.test.ts` and `tests-panel-grid.test.tsx` pass | `npx vitest run` |
| Bundle | Build succeeds, bundle-size guard passes | `npm run build:eval-ui && npm run lint:bundle-size` |
| No console errors | Preview console clean during test-list interaction | `preview_console_logs` |

## Code Quality

- Two CSS edits + one className swap. No new abstractions, no shims.
- Tests are short and focused; no snapshot proliferation.

## Out-of-Scope (do NOT block on)

- Mobile-friendly Studio shell (sidebars, top nav)
- Studio command bar redesign
- U/I badge restyling
