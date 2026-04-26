---
increment: 0737-studio-skill-source-github-link
title: Studio skill detail — clickable GitHub source link
type: feature
priority: P2
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
discovered_during: >-
  User QA on 2026-04-26 — the Studio detail header for an installed skill has no
  clickable path back to the source SKILL.md on GitHub. verified-skill.com (the
  public site) does have this affordance, so the parity gap is jarring.
---

# Feature: Studio skill detail — clickable GitHub source link

## Overview

The Skill Studio detail page (Overview tab header) currently renders the skill name, version, plugin breadcrumb, install method, and absolute local path — but provides **no clickable navigation back to the source SKILL.md on GitHub**. The public site at verified-skill.com renders exactly that affordance (path + ↗ arrow opening `https://github.com/{owner}/{repo}/blob/HEAD/{skillPath}/SKILL.md`). The parity gap is jarring once the user notices it: in Studio you can copy the local path, but you cannot click through to the source-of-truth on GitHub.

The infrastructure already exists end-to-end:

- Studio: `SourceFileLink.tsx` already builds `{repoUrl}/blob/HEAD/{skillPath}` when both fields are present (see `repositories/anton-abyzov/vskill/src/eval-ui/src/components/SourceFileLink.tsx` line 32).
- Studio: `DetailHeader.tsx` already calls `<SourceFileLink>` in the byline row (line 196).
- Platform: `Skill.repoUrl` and `Skill.skillPath` are stored in Prisma and returned by `/api/v1/skills/*`.

The gap is in the wire: the eval-server's `buildSkillMetadata()` (api-routes.ts ~line 755) only exposes `homepage`, and `DetailHeader.tsx` hard-codes `skillPath={null}`. The install receipt that already records `installMethod: "copied"` does NOT capture `repoUrl` + `skillPath`, so locally-installed skills lose this provenance the moment they hit disk.

This increment closes the gap end-to-end: install receipts gain `sourceRepoUrl` + `sourceSkillPath`, the SkillInfo type carries them as `repoUrl` + `skillPath`, and DetailHeader renders both a repo-root anchor (author byline) and a SKILL.md anchor (source file).

## Personas

- **Studio user (skill consumer)** — has installed skills via `vskill install`. Wants to click from the Studio detail header to the SKILL.md on GitHub to read the source, file an issue, or contribute a fix.
- **Studio user (skill author)** — has authored a skill locally (no platform record). Should keep the existing copy-chip fallback — no surprise broken-link behavior.

## User Stories

### US-001: Source-file anchor on installed skills (P1)
**Project**: vskill

**As a** Studio user looking at an installed skill's detail page
**I want** a clickable anchor in the detail header that opens the SKILL.md on GitHub in a new tab
**So that** I can read the source-of-truth, file an issue, or contribute back without leaving my workflow

**Acceptance Criteria**:
- [x] **AC-US1-01**: When a skill's stored receipt contains both `sourceRepoUrl` and `sourceSkillPath`, the Studio detail header byline renders a single anchor with the format `<a href="{repoUrlCanonical}/blob/HEAD/{skillPath}">`, where `repoUrlCanonical` strips trailing `/tree/<branch>` or `/blob/<branch>[/path]` and `skillPath` has its leading and trailing slashes trimmed.
- [x] **AC-US1-02**: The anchor renders with `target="_blank"` and `rel="noopener noreferrer"`, the visible label is the last path segment of `skillPath` (e.g. `analytics-tracking`), followed by a `↗` Unicode marker, and `title={href}` so users can hover to see the full URL.
- [x] **AC-US1-03**: The anchor is reachable from the Overview tab without scrolling on a 768px-tall viewport — i.e. it lives in the always-visible header card, not in any sub-tab or accordion below.

### US-002: Repo-root anchor in author byline (P1)
**Project**: vskill

**As a** Studio user looking at any skill with a known source repo
**I want** the author/byline element to also be clickable, opening the repo root on GitHub
**So that** I can navigate to the publisher's other skills, follow them, or check repo-level metadata

**Acceptance Criteria**:
- [x] **AC-US2-01**: When `repoUrl` is a valid HTTPS URL, the byline `AuthorLink` element renders as an `<a>` (existing behavior — verify it's preserved), opening `repoUrlCanonical` in a new tab. When only `homepage` is set, fall back to that.
- [x] **AC-US2-02**: The repo-root anchor and the source-file anchor (US-001) coexist in the same byline row, separated by visible spacing (no overlap, no truncation collapse).

### US-003: Authored-skill fallback unchanged (P1)
**Project**: vskill

**As a** Studio user authoring a skill locally (no platform install)
**I want** the existing copy-to-clipboard chip to keep working when there's no source repo URL
**So that** locally-authored skills don't get a broken link or missing affordance

**Acceptance Criteria**:
- [x] **AC-US3-01**: When a skill has no `repoUrl` (authored, or pre-receipt installed before this change), the existing `SourceFileLink` copy-chip path renders unchanged — same DOM `data-testid="source-file-copy"`, same click-to-copy behavior, same visual styling.
- [x] **AC-US3-02**: A skill with only a `homepage` frontmatter URL (no install receipt `sourceRepoUrl`) still gets a clickable anchor when the homepage URL is a `https://github.com/...` URL, matching pre-existing behavior. We do not regress this.

### US-004: Install receipt captures repo provenance (P1)
**Project**: vskill

**As a** Studio backend
**I want** the install receipt for `vskill install` (and the platform-fetch path that drives it) to record `sourceRepoUrl` and `sourceSkillPath` from the platform's `/api/v1/skills/:owner/:repo/:skill` response
**So that** the Studio frontend can render the source link without a second network round-trip

**Acceptance Criteria**:
- [x] **AC-US4-01**: The install receipt format used by `installMethod: "copied"` (and `"symlinked"`) gains two new optional fields: `sourceRepoUrl?: string` and `sourceSkillPath?: string`. Existing receipts without these fields continue to load (backward compatible).
- [x] **AC-US4-02**: When `vskill install <publisher>/<skill>` runs against the platform, the install code path persists `repoUrl` → `sourceRepoUrl` and `skillPath` → `sourceSkillPath` from the platform response into the receipt before exiting.
- [x] **AC-US4-03**: `buildSkillMetadata()` reads the receipt and exposes the two fields on the `SkillInfo` payload returned by `GET /api/skills` and `GET /api/skills/:plugin/:skill` — under field names `repoUrl` and `skillPath` (frontend names; the receipt internal names are `source*` to disambiguate origin from any frontmatter-declared homepage).

## Functional Requirements

### FR-001: SkillInfo type extension
The `SkillInfo` interface in `repositories/anton-abyzov/vskill/src/eval-ui/src/types.ts` gains two optional fields:
```ts
repoUrl?: string | null;   // canonical repo root (https://github.com/owner/repo)
skillPath?: string | null; // path inside the repo to the skill folder (e.g. "skills/marketing/analytics-tracking")
```
The corresponding server-side payload in `api-routes.ts` returns the same shape.

### FR-002: Install receipt schema
The install receipt JSON (read by the eval-server install-method resolver) gains:
```jsonc
{
  "method": "copied",
  "sourceRepoUrl": "https://github.com/coreyhaines31/marketingskills",
  "sourceSkillPath": "skills/analytics-tracking"
}
```
Both fields are optional. Reads are defensive: missing fields produce `undefined`, never throw.

### FR-003: `buildSkillMetadata` populates new fields
`buildSkillMetadata(dir, origin, root)` reads the install receipt (already loaded for `installMethod`) and threads `sourceRepoUrl` → `repoUrl` and `sourceSkillPath` → `skillPath` into the returned metadata.

### FR-004: DetailHeader wiring
`DetailHeader.tsx` lines 195-200 are updated:
```tsx
<AuthorLink author={skill.author ?? null} repoUrl={skill.repoUrl ?? skill.homepage ?? null} />
<SourceFileLink
  repoUrl={skill.repoUrl ?? skill.homepage ?? null}
  skillPath={skill.skillPath ?? null}
  absolutePath={skill.dir}
/>
```
No new components. Just better data threaded through.

### FR-005: Vskill install path wires receipt fields
The `vskill install` command (or whatever code path writes the install receipt) reads `repoUrl` + `skillPath` from the platform response and writes them into the receipt.

## Non-Functional Requirements

- **NFR-001 (compat)**: All changes are additive. Existing install receipts without the new fields keep working — `SkillInfo.repoUrl` and `.skillPath` are `undefined` and the SourceFileLink falls back to copy-chip / homepage anchor.
- **NFR-002 (perf)**: No new network calls from the Studio frontend. The install receipt already loaded for `installMethod` provides the two new fields synchronously.
- **NFR-003 (test coverage)**: Vitest unit tests for the type extension, the `buildSkillMetadata` change, and the `DetailHeader` byline rendering (parameterised: with `repoUrl+skillPath`, with only `homepage`, with neither).

## Success Criteria

- **SC-001**: After installing a real platform skill (one with `repoUrl` set in the platform DB), opening Studio → that skill → Overview tab shows a clickable `↗` anchor whose href resolves to a 200 GitHub blob page for the SKILL.md file.
- **SC-002**: Authored local skill `greet-anton` (no `repoUrl` in receipt, no `homepage` in frontmatter) keeps showing the existing copy-chip fallback — no broken anchor, no visible regression.
- **SC-003**: Released as `vskill@<next-patch>` and self-verified by running `npx vskill@<v> studio` against the user's existing project — preview-tools snapshot proves the anchor is visible AND clickable.

## Out of Scope

- Backfilling existing on-disk install receipts for skills installed before this change. They will keep showing the copy-chip until reinstalled.
- Migrating SKILL.md frontmatter to a new `source` field. We continue to read `homepage` as a secondary signal.
- Fixing the verified-skill.com `/skills/coreyhaines31/marketingskills/analytics-tracking` 4225981758 server crash. That is a separate vskill-platform DB / error-boundary issue, scoped as a separate increment.
- Any change to vskill-platform — this work is entirely in `vskill` (CLI + Studio).

## Dependencies

- vskill-platform `/api/v1/skills/:owner/:repo/:skill` endpoint must return `repoUrl` and `skillPath` in its payload (already does — confirmed in Prisma schema and page.tsx render path).
- No new third-party dependencies.
