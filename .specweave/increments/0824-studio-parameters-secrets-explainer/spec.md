---
increment: 0824-studio-parameters-secrets-explainer
title: Studio Parameters & Secrets explainer UX + docs page
type: feature
priority: P1
status: completed
created: 2026-05-01T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Studio Parameters & Secrets explainer UX + docs page

## Overview

The "Parameters & Secrets" panel in vskill Studio (right rail of every skill detail page) currently shows the bare empty-state message **"No credentials configured for this skill"** when no params exist. First-time users have no way to understand where values get stored, how the list gets populated, how values are resolved at runtime, or that storage is local-only.

This increment adds inline empty-state explainer copy, a persistent header `(i)` info icon, and a new `/docs/parameters-and-secrets` page on verified-skill.com that the inline copy deep-links to.

## User Stories

### US-001: First-time user understands what Parameters & Secrets does (P1)
**Project**: vskill

**As a** vskill Studio user opening a skill that has no credentials configured
**I want** an explanation of where parameters get stored, how the list gets populated, and that storage is local-only
**So that** I can decide whether to add a parameter without having to read source code or guess

**Acceptance Criteria**:
- [x] **AC-US1-01**: When a skill has zero credentials and the add-form is closed, the Parameters & Secrets panel shows a card with a bold headline ("No parameters yet"), a 2-sentence body explaining `.env.local` storage and the two ways params populate (declared in `evals.json` `requiredCredentials` OR added here), and a "Learn more →" anchor.
- [x] **AC-US1-02**: The "Learn more →" anchor points to `https://verified-skill.com/docs/parameters-and-secrets` and opens in a new tab with `target="_blank"` and `rel="noopener noreferrer"`.
- [x] **AC-US1-03**: When the user clicks "+ Add Parameter" the explainer card hides (existing behavior preserved); when at least one credential is added, the explainer card stays hidden.

### US-002: Returning user can re-check the resolver behavior at any time (P2)
**Project**: vskill

**As a** vskill Studio user revisiting a skill that already has credentials
**I want** quick access to a refresher on the resolver chain without leaving the page
**So that** I do not have to remember whether `process.env` or `.env.local` wins

**Acceptance Criteria**:
- [x] **AC-US2-01**: A small `(i)` info icon renders inline next to the "PARAMETERS & SECRETS" header text and is mounted regardless of whether credentials exist.
- [x] **AC-US2-02**: Hovering the `(i)` icon shows a native browser tooltip whose text describes the resolver chain (mentions both `process.env` and `.env.local`).
- [x] **AC-US2-03**: The `(i)` icon does not interfere with the existing `+ Add Parameter` button layout (no shift, no overlap).

### US-003: Reader can find authoritative documentation on the docs site (P1)
**Project**: vskill

**As a** user (or LLM agent) following the "Learn more →" link
**I want** a single canonical docs page covering storage, resolver order, declared-vs-custom flow, runtime consumption, and security guarantees
**So that** I can answer detailed questions without reading vskill source

**Acceptance Criteria**:
- [x] **AC-US3-01**: A new MDX page exists at `vskill-platform/src/app/docs/parameters-and-secrets/page.mdx` with frontmatter `title`, `description`, `slug: /docs/parameters-and-secrets`, and an `order` integer that does not collide with sibling pages.
- [x] **AC-US3-02**: The page renders 7 named sections: what-it-is, where-stored, resolver-order, two-ways-params-show-up, runtime-consumption, security, common-credentials.
- [x] **AC-US3-03**: The page appears in the docs sidebar nav (auto-harvested into `generated-nav.ts` by `scripts/generate-docs-nav.cjs` at prebuild, or added manually to `docs-nav.ts` as fallback).
- [x] **AC-US3-04**: The vskill-platform Next.js build (`npm run build`) succeeds with the new page in place.

## Functional Requirements

### FR-001: Empty-state explainer block
Replace the existing empty-state `<div>` in `CredentialManager.tsx` (~lines 160-163) with a 3-block stack: bold headline, 2-sentence body referencing `KEY=value`, `.env.local`, `.gitignore`, and the `evals.json` declaration path; "Learn more →" anchor. Keep the existing `var(--surface-2)` rounded card container.

### FR-002: Header info icon
Append an inline `(i)` glyph immediately after the "Parameters & Secrets" `<span>` in `CredentialManager.tsx` (~lines 141-152). Use `var(--text-tertiary)`, ~10px, `cursor: help`, native `title=""` attribute. No new dependency, no Tooltip component.

### FR-003: Docs page
Create `/docs/parameters-and-secrets` MDX page with frontmatter matching the existing pattern from `cli-reference/page.mdx`. Sections cover the resolver chain, `evals.json#requiredCredentials` declaration, gitignore guarantee, and a quick-reference list of common credentials by skill type.

## Success Criteria

- Visual verification: `localhost:3157/#/skills/project/.claude/remotion-best-practices` shows the new explainer + `(i)` icon.
- Build verification: vskill-platform `npm run build` exits 0.
- Unit verification: `CredentialManager` Vitest tests pass (empty-state copy assertion, "Learn more" href assertion, `(i)` icon presence in both empty and populated states).

## Out of Scope

- Changing the storage location for parameters
- Adding encryption at rest
- Schema changes to `evals.json` or `SKILL.md` frontmatter for parameter declaration
- Backend / API endpoint changes (eval-server, integration-routes)
- Internationalization of the new copy
- Adding a custom Tooltip component (native `title=""` is sufficient)

## Dependencies

- Existing `CredentialManager.tsx` component contract (props `plugin: string`, `skill: string`)
- Existing CSS variables: `--text-tertiary`, `--text-secondary`, `--accent`, `--surface-2`
- vskill-platform docs frontmatter conventions from `cli-reference/page.mdx`
- `scripts/generate-docs-nav.cjs` prebuild hook (or manual fallback to `docs-nav.ts`)
