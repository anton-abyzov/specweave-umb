# Design systems from code, files and Figma

## Problem

Designs are only useful from code when they use the project's real tokens and components. Claude offers two creation paths ("Using Claude": brand files, connectors, description; "Using Claude Code": the repository's tokens and components) and a per-design picker (claude-design-inventory.md, sections 2 and 8). The user's repositories already hold design systems with exact sources: Weave (`specweave/design/weave/tokens.json`, `weave.css`), the app's runtime theme (`packages/shared/src/themePalettes.ts`, `apps/web/src/index.css`) and EasyChamp's ec-uikit (`src/styles/tokens.css`, 47 primitives) (token-sources.md). Figma desktop 126.4.12 is installed but its local MCP server is off and no agent has a Figma connector, so Figma access cannot be assumed.

## Scope

In: a deterministic extractor with file:line provenance for CSS custom properties (including Tailwind v4 `@theme` and dark variants), DTCG JSON (Figma's variables export, Tokens Studio, Style Dictionary), Weave `tokens.json`, and literal TypeScript theme objects; component discovery from TypeScript barrels and CSS class families; a reviewed import with a diff; an explicit rescan that only reports changed sources; Settings > Design systems; the picker; and Figma through (a) an exported variables file and (b) Figma's own MCP server when the user turns it on.

Out: continuous or background scanning, uploading code or tokens to any third party, installing Figma plugins, a Figma account sign-in flow inside the app, and building component libraries (previews of React components need the project's own build; the inventory lists them with props and stories).

## Acceptance Criteria

- [ ] AC-01: Scanning a project lists candidate sources inside the project root only (token JSON, CSS with custom properties, theme TS files), with token counts per source, before reading anything else. Nothing outside the approved root is read; symlinks that leave the root are skipped.
- [ ] AC-02: The extractor is deterministic: the same files give byte-identical output (sorted, stable ids), every token carries `{path, line, column, sha256 of the file}`, and per-mode values (light, dark, data-theme variants) keep the raw expression next to the resolved value. `var()` resolves within a mode; cycles are reported, not looped.
- [ ] AC-03: Weave imports as one system "Weave" with 18 colors in light and dark, type, spacing, radius, shadow and motion, and its 11 `.wv-*` component class families. The app theme (`themePalettes.ts`, `index.css`) imports as "SpecWithCode app theme" with `derivedFrom` linking Iris to Weave, not as a competing brand. Drift between Weave copies (for example `--wv-scrim` only in the vskill-platform copy) is reported as a finding.
- [ ] AC-04: ec-uikit (read-only, local fixture authorized by the user) imports its theme tokens with light and dark modes from `src/styles/tokens.css` (269: the 312 unique custom-property names minus 43 declared only inside component rules) and lists the 48 components the `src/primitives` barrel exports with their props interfaces and story names. A local-only verify script reads it in place, writes counts and provenance samples to a receipt, and copies no source, brand asset or private content into the app, the Playground or reports.
- [ ] AC-05: Import is a review: the user sees new, changed and removed tokens and components with their sources, can exclude any, and confirms. Only confirmed items are written as a new system version. A rescan compares file hashes first and shows "No changes" without re-parsing when nothing changed.
- [ ] AC-06: Settings > Design systems lists systems with Name, Owner (project or Playground), Sources and Updated, with search. "New design system" offers From this project's code, From a tokens file (DTCG or Figma variables export), From Figma (desktop app), and Describe it (agent thread that writes a system through `design_system_*` tools, reviewed the same way).
- [ ] AC-07: The picker ("Design system") appears in the Design gallery's new-design flow, the editor header and Design from code. Picking another owner's system offers "Copy into <owner>" and never references it across owners.
- [ ] AC-08: Figma file path: importing a Figma variables JSON export (DTCG) maps collections and modes to tokens with provenance `figma-export:<file name>#<variable path>`. Test with a synthetic export fixture.
- [ ] AC-09: Figma desktop path: when Figma's local MCP server answers at `http://127.0.0.1:3845/mcp`, Settings shows "Figma desktop: connected" and the From Figma flow lists the tools it exposes; variables are read only through a tool the server lists (for example `get_variable_defs`) for the frame the user selected in Figma, then go through the same review. When it is off, the flow says how to turn it on in Figma (Preferences > Enable desktop MCP server) and offers the file path instead. Tested against a local fixture MCP server; the live check is a user gate.
- [ ] AC-10: Agent tools `design_system_scan` (returns the candidate list and a proposal id, never writes), `design_system_propose` (agent-described system as a proposal) and the existing `design_system_get`. Writing a system needs the user's review in the UI.
- [ ] AC-11: Headless screenshots of Settings > Design systems, the scan candidates, the import review (Weave and the ec-uikit fixture) and the Figma off state, light and dark.

## Approach

Server: `apps/server/src/design/systems/` with `scanCandidates.ts`, `extractCss.ts` (postcss + postcss-value-parser, already in the dependency tree or added with license check), `extractDtcg.ts` and `extractWeave.ts` (jsonc-parser `parseTree` for offsets), `extractTsTheme.ts` (TypeScript compiler API, literal objects only), `discoverComponents.ts` (TS barrels, CSS class families), `resolveModes.ts`, `DesignSystemService.ts` (proposal store, review, versioned write through the 0972 store). Figma: `apps/server/src/design/figma/FigmaDesktopMcpClient.ts` (MCP over HTTP, tools/list discovery, no hard-coded assumptions beyond the listed tool). Web: `components/settings/DesignSystemsSettings.tsx`, `components/design/DesignSystemReview.tsx`, `DesignSystemPicker.tsx`.

Deterministic parsers over a full scan by a model: exact provenance, no tokens spent, repeatable. A model is used only in the Describe path, and its output is a proposal.

## Decisions

### Asked
- D-01: Reuse existing SpecWeave/SpecWithCode tokens instead of a new system; EasyChamp is an authorized read-only fixture (user, October 20, 2026).
### Defaulted (change any before sw-do)
- D-02: Weave is the SpecWeave/SpecWithCode design system; the app theme links to it.
- D-03: Figma through its own local MCP server and exported files only; no plugin install, no Figma REST token in v1.
### Open
- none

## Tasks

### T-01 Candidate scan inside the root
- AC: AC-01 | Files: apps/server/src/design/systems/scanCandidates.ts | Test: scan tests with symlink escape

### T-02 Extractors and mode resolution
- AC: AC-02, AC-08 | Files: extractCss.ts, extractDtcg.ts, extractWeave.ts, extractTsTheme.ts, resolveModes.ts | Test: determinism and provenance tests per format

### T-03 Weave and app theme import
- AC: AC-03 | Files: fixtures, extractor wiring | Test: tests against a copy of the Weave files

### T-04 Component discovery
- AC: AC-03, AC-04 | Files: discoverComponents.ts | Test: synthetic barrel fixture

### T-05 EasyChamp read-only verification
- AC: AC-04 | Files: scripts/studio-verify/design-systems-easychamp.mjs | Test: local receipt

### T-06 Review, versioned write and rescan
- AC: AC-05, AC-10 | Files: DesignSystemService.ts, design_system_* tools | Test: service tests

### T-07 Settings, picker and review UI
- AC: AC-06, AC-07 | Files: DesignSystemsSettings.tsx, DesignSystemReview.tsx, DesignSystemPicker.tsx | Test: component tests

### T-08 Figma desktop MCP client
- AC: AC-09 | Files: apps/server/src/design/figma/FigmaDesktopMcpClient.ts | Test: fixture MCP server tests

### T-09 Evidence
- AC: AC-11 | Files: apps/web/tests/design-systems/* | Test: headless Playwright light and dark

### T-10 Verify and close 0973
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
