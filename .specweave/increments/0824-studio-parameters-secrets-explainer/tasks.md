# Tasks: Studio Parameters & Secrets explainer UX + docs page

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started, `[x]`: Completed
- AC references link tasks to acceptance criteria for traceability

## Phase 1: Tests first (TDD RED)

### T-001: Add Vitest tests for empty-state explainer
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Description**: Write failing tests in `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/__tests__/CredentialManager.test.tsx` (create file if absent) covering the new empty-state structure.
**Test Plan**:
- TC-001: Given `getCredentials` returns `{ credentials: [] }`, When `<CredentialManager plugin="x" skill="y" />` mounts, Then the rendered DOM contains the headline "No parameters yet".
- TC-002: Same setup, Then the body text mentions both `.env.local` and `evals.json`.
- TC-003: Same setup, Then a `<a>` element exists with `href="https://verified-skill.com/docs/parameters-and-secrets"`, `target="_blank"`, and `rel` attribute containing `noopener` and `noreferrer`.
- TC-004: Given the user clicks "+ Add Parameter" (sets `showAddForm=true`), Then the empty-state explainer is no longer in the DOM (existing behavior preserved).

### T-002: Add Vitest tests for header info icon
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Description**: Extend `CredentialManager.test.tsx` with assertions on the persistent `(i)` icon.
**Test Plan**:
- TC-005: Given `getCredentials` returns `{ credentials: [] }`, Then a header info icon is rendered with a `title` attribute whose text contains both "process.env" and ".env.local".
- TC-006: Given `getCredentials` returns one credential, Then the same header info icon is still rendered (not conditional on empty state).
- TC-007: The header info icon does not break the existing right-aligned "+ Add Parameter" button (button still present in DOM at expected position).

## Phase 2: GREEN — implement UI

### T-003: Add header info icon to CredentialManager.tsx
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Description**: In `repositories/anton-abyzov/vskill/src/eval-ui/src/pages/workspace/CredentialManager.tsx` lines ~141-152, append a `<span>` with an info glyph (e.g. `ⓘ`) immediately after the "Parameters & Secrets" `<span>`. Use inline styles matching the existing CSS variables: `color: var(--text-tertiary)`, `cursor: help`, `marginLeft: 6px`, `fontSize: 11px`. Set `title="Stored as KEY=value in this skill's local .env.local. Resolved from process.env first, then .env.local."`.
**Test Plan**: T-002 (TC-005, TC-006, TC-007) all pass.

### T-004: Replace empty state with explainer card in CredentialManager.tsx
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Description**: In `CredentialManager.tsx` lines ~160-163, replace the single-line "No credentials configured for this skill" `<div>` with a 3-block stack inside the existing `var(--surface-2)` rounded card:
1. Bold headline: `No parameters yet` (`var(--text-secondary)`, ~13px, `font-semibold`)
2. Body (2 sentences, `var(--text-tertiary)`, 12px, ~1.5 line-height): "Values are stored as `KEY=value` in this skill's local `.env.local` (auto-added to `.gitignore`). They appear here when declared as `requiredCredentials` in `evals.json`, or when you add custom ones below."
3. Anchor: `<a href="https://verified-skill.com/docs/parameters-and-secrets" target="_blank" rel="noopener noreferrer" style={{color: "var(--accent)"}}>Learn more →</a>`

Preserve the existing `credentials.length === 0 && !showAddForm` guard so populated/add-form states hide the card.
**Test Plan**: T-001 (TC-001..TC-004) all pass.

## Phase 3: Docs page

### T-005: Inspect existing /docs MDX siblings for frontmatter conventions
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Description**: Read `vskill-platform/src/app/docs/cli-reference/page.mdx` and `security-guidelines/page.mdx` to confirm the exact frontmatter shape (title, description, slug, order, optional toc) and pick a non-colliding `order` integer near 35.
**Test Plan**: Manual — note the chosen `order` in commit message.

### T-006: Create /docs/parameters-and-secrets MDX page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Description**: Create `repositories/anton-abyzov/vskill-platform/src/app/docs/parameters-and-secrets/page.mdx` with:
- Frontmatter: `title: "Parameters & Secrets"`, `description: "How vskill stores, resolves, and consumes API keys and parameters for skills."`, `slug: /docs/parameters-and-secrets`, `order: <chosen in T-005>`, optional `toc` listing the 7 sections.
- 7 sections: (1) What this is, (2) Where values are stored, (3) Resolver order, (4) Two ways params show up (declared vs custom), (5) Runtime consumption, (6) Security, (7) Common credentials by skill type.
**Test Plan**:
- TC-008: Given the page file exists, When `npm run build` runs in `vskill-platform`, Then the build succeeds (MDX compiles cleanly).
- TC-009: Given the dev server is running, When navigating to `/docs/parameters-and-secrets`, Then all 7 sections render visibly.

### T-007: Verify nav auto-registration
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Description**: Run `npm run prebuild` (or whichever script invokes `scripts/generate-docs-nav.cjs`) in `vskill-platform`. Confirm `src/app/docs/generated-nav.ts` now contains an entry for the new MDX file. If it does not, add a manual entry to `src/app/docs/docs-nav.ts`.
**Test Plan**:
- TC-010: Given the prebuild script ran, When inspecting the dev sidebar, Then "Parameters & Secrets" appears as a nav entry.

## Phase 4: Build & verification

### T-008: Run vskill-platform full build
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed
**Description**: `cd repositories/anton-abyzov/vskill-platform && npm run build`. Must exit 0.
**Test Plan**: Build exit code 0 + no broken-link warnings in stdout.

### T-009: Run vskill eval-ui Vitest suite
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01..03, AC-US2-01..03 | **Status**: [x] completed
**Description**: `cd repositories/anton-abyzov/vskill && npx vitest run src/eval-ui/src/pages/workspace/__tests__/CredentialManager.test.tsx`. All TC-001..TC-007 must pass.
**Test Plan**: Vitest exit code 0.

### T-010: Visual verification in Studio preview
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01..03, AC-US2-01..03 | **Status**: [x] completed
**Description**: Build the eval-ui bundle, start a Studio session, open `localhost:3157/#/skills/project/.claude/remotion-best-practices`, take a screenshot, confirm: (a) explainer card visible, (b) `(i)` icon visible next to header, (c) hover tooltip shows the resolver-chain text, (d) "Learn more →" link target is correct, (e) clicking "+ Add Parameter" hides the explainer card.
**Test Plan**: Screenshot evidence attached.

### T-011: Visual verification of docs page
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Description**: `cd repositories/anton-abyzov/vskill-platform && npm run dev`. Open `http://localhost:3000/docs/parameters-and-secrets`, confirm all 7 sections render and the page appears in the sidebar nav.
**Test Plan**: Screenshot evidence attached.

## Phase 5: Sync

### T-012: Sync living docs
**User Story**: all | **Status**: [x] completed
**Description**: Run `specweave sync-living-docs 0824-studio-parameters-secrets-explainer` to propagate spec content into `.specweave/docs/internal/specs/`.
**Test Plan**: Command exits 0; new specs appear under living docs tree.
