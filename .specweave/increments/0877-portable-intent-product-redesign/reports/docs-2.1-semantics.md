# Current-guide semantic correction — T-27

Commit `6a2750ac2eefbb4e7ec520e45ca2fe8e4d569d68`, parent `c502b35d6`. Exactly six documentation files changed; no executable code or package metadata. Net reduction: 369 lines.

## Four current guides replaced

- `docs-site/docs/guides/model-selection.md`: execution-context guide replaces default Opus/Haiku routing, mandatory plan-mode and dated price recommendations. Separates harness, model, effort, provider, surface and session; explains explicit intent association and partial metadata coverage.
- `docs-site/docs/guides/analytics-dashboard.md`: Work board is the default; intent state is distinct from increment completion and current verification. Documents optional increment links, drag/drop and accessible selectors, evidence, sessions, live updates and secondary diagnostics. Removes the claim that every command, skill and spawn is automatically tracked through PostToolUse.
- `docs-site/docs/reference/cost-tracking.md`: documents the actual dashboard Claude Code usage source, recent-200-file limit, exact identities, mixed/unsupported/unknown costs, priced subtotal, dated legacy estimates and distinction from invoices. Removes unsupported analytics increment billing/export instructions, invented current rates, and blanket anonymous-data/compliance claims.
- `docs-site/docs/guides/dashboard/hooks.md`: documents the two default hooks, explicit auto activation, explicit handoffs and limited diagnostics coverage. Clarifies that context still occupies an agent's context window and an auto continuation uses normal inference, even though local state reads do not call a model API.

## Two historical guides labeled

`docs-site/docs/academy/specweave-essentials/08-ai-model-selection.md` and `docs-site/docs/glossary/terms/intelligent-model-selection.md` retain their historical content with a prominent top warning: 1.x routing design and dated comparisons are not 2.1 defaults or current prices. Both link directly to current execution-context and cost guidance. No current provider recommendation or new pricing claim was introduced.

## Source verification

Checked behavior against:

- `bin/specweave.js:889` and `:1623`: actual analytics/dashboard options, including `--no-browser` and `--port`.
- `src/cli/commands/dashboard.ts:24`: project requirement, instance reuse, registration and default port behavior.
- `src/dashboard/client/src/pages/WorkPage.tsx` and `components/layout/Sidebar.tsx`: board metrics, state controls, 15-second reconciliation, session association and diagnostics placement.
- `src/dashboard/server/data/work-projection.ts`, `intent-store.ts`, `src/core/intent/types.ts`: canonical task evidence, verification, optional increments and persisted execution fields.
- `src/dashboard/server/data/local-sessions.ts`: project matching, bounded cached reads, exact metadata, partial coverage and no transcript fields returned.
- `src/dashboard/server/data/cost-aggregator.ts:93` and `:190`: latest-file limit, exact price lookup, unpriced/mixed behavior and dated estimate status.
- `plugins/specweave/hooks/hooks.json`, `src/core/hooks/handlers/session-start.ts`, `stop.ts`: two default events, compact context, explicit auto marker, stop guards and explicit handoff pointer.
- `src/dashboard/client/src/pages/HooksPage.tsx`: available event history and historical/optional filter types, not an installation inventory.

## Validation

Final production docs build passed: `docs-2.1-build.log`. Native pre-commit malware/secret scan passed without an override. Headless Chromium explicitly uses `headless: true`, `PWDEBUG=0`, `PLAYWRIGHT_HTML_OPEN=never`; all six routes are checked for HTTP 200 and the new semantic statements, plus their canonical guide links. Evidence: `docs-2.1-entrypoints.json`.

Scope is the current entry guides and two historical notices. This is not a semantic audit of every archived article or a claim that production Pages is already deployed. Root independently reviews the commit.
