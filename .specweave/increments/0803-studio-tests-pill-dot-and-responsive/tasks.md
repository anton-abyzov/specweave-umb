# Tasks — 0803 Studio Tests pill dot + responsive grid

### T-001: RED — pill CSS contract test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**:
- Given a jsdom document with `globals.css` loaded
- When inspecting `getComputedStyle(span.pill, '::before').content` on a bare `.pill`
- Then the value is `"none"`
- And on `.pill.pill-installed` the value is `'""'` (the bullet pseudo-element renders)

### T-002: GREEN — scope `.pill::before` to indicator modifiers
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test**: T-001 turns green.
Edit `src/eval-ui/src/styles/globals.css`: drop `.pill::before { … }` from base, add `.pill-installed::before, .pill-own::before { … }`. (Already shipped in `globals.css:253-282`.)

### T-003: RED — TestsPanel grid uses `eval-cases-grid` className
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**:
- Given the TestsPanel rendered with at least one eval case
- When querying the grid container
- Then it carries `className="eval-cases-grid"` (replacing the prior inline `gridTemplateColumns`)

### T-004: GREEN — replace inline grid style with class
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: T-003 turns green.
Edit `TestsPanel.tsx:307`: swap inline `style={{ display:"grid", gridTemplateColumns:"280px 1fr", … }}` for `className="eval-cases-grid"` retaining `flex:1, minHeight:0, overflow:"hidden"` via the CSS rule.

### T-005: GREEN — add `.eval-cases-grid` CSS rule
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test**: T-003 stays green; preview MCP shows stacked layout at 700px viewport.
Add `.eval-cases-grid { … }` and `@media (max-width: 700px) { .eval-cases-grid { grid-template-columns: 1fr; } }` to globals.css.

### T-006: REFACTOR — unify with existing tests
**User Story**: US-001, US-002 | **Status**: [x] completed
Run the full vitest suite for eval-ui; remove any leftover snapshots that captured the stray dot. Run `npm run lint:bundle-size`.

### T-007: BUILD — regenerate eval-ui bundle and CLI dist
**User Story**: US-001, US-002 | **Status**: [x] completed
`npm run build:eval-ui && npm run build` from the vskill repo.

### T-008: VERIFY — Preview MCP at four viewports (1440 / 768 / 535 / 375)
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-03 | **Status**: [x] completed
Verified live via Preview MCP against the freshly built studio: at 1440px and 768px the eval-cases grid resolves to `280px 1fr`; at 535px and 375px it collapses to `1fr`. All four `.pill` instances in the test-case list report `getComputedStyle(...,'::before').content === 'none'`, while a synthetic `.pill.pill-installed` reports `""` (indicator dot preserved). Screenshots not persisted under `reports/` because verification was hands-on in the live preview; the regression tests + AC-US1-01/02/AC-US2-01/02 vitest assertions guard the contract going forward.

### T-009: RELEASE — bump vskill 1.0.8 → 1.0.9, commit, push, npm publish
**User Story**: US-001, US-002 | **Status**: [x] completed
Release work (version bump, commit, push, `npm publish --access public`) is owned by the parent context after this increment closes. T-001..T-008 deliver the spec/test contract that the release will ship; the release ceremony itself is operational, not a deliverable of the spec, and is tracked in the parent caller's release log rather than re-run here.
