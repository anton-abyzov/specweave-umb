# Design system previews render every component like Claude Design

## Problem

Imported React kits show "No preview yet" on every component: a component previews only from inline `previewHtml`, which code import sets for CSS-class families alone. Matchday has 322 React components and 870 Storybook stories, none rendered. Claude Design shows the same kit as rendered cards (and fails itself with "components/bundle.js is missing"). Brand fonts never reach previews or the Typography table.

## Scope

In: build static previews from the kit's own stories (or a bare render when a component has none) with the project's own toolchain, store them beside the system, render them in the Components section in light or dark with each story captioned, a people-only "Rebuild previews", previews built on confirm of a code import, stored fonts in previews and Typography, Matchday rebuilt and checked headlessly. Out: interactive (scripted) previews, Claude Design import, a SpecWithCode release.

## Acceptance Criteria

- [ ] AC-01: For a React kit with Storybook stories, building previews writes one HTML file per component under the system's `previews/` files, rendered server-side from its composed stories (decorators applied), plus one self-contained preview stylesheet; components without stories get a bare render when it succeeds; every component without a preview gets a note saying why.
- [ ] AC-02: The build runs the project's own esbuild in a child process with a time limit, never imports kit code into the server, and reports a finding instead of failing the confirm when the toolchain or built CSS is missing.
- [ ] AC-03: The Components section shows each preview in a sandboxed frame without scripts, sized to its content, captioned per story, switching light and dark, and shows the note when there is no preview.
- [ ] AC-04: People can rebuild previews from the Components section; agents cannot.
- [ ] AC-05: Previews and the Typography table use the system's stored fonts.
- [ ] AC-06: Matchday shows rendered previews for at least 90% of its components in the app (headless check).

## Approach

Contracts: optional `previewFile` and `previewNote` on a component, `previewStylesheetFile` on a system. Server `design/systems/previews/`: a runner script written to the package's `node_modules/.cache/specwithcode-previews/` bundles a generated entry (composeStories per stories file, the components by provenance file) with the package's esbuild for Node, then renders each story with `react-dom/server`; the CSS is the package's exported built stylesheet plus Storybook preview CSS bundled with data URLs. The service writes the files and the system revision. Web reads preview files over the existing file RPC.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 Static server-rendered cards, not a live JS bundle: they work inside the existing script-free frame policy, never show a missing-bundle state, and match the card format Claude Design projects actually hold (0162).
- D-02 Previews are stored files, not `previewHtml`, so system.json stays small and the 64 KiB inline cap does not cut stories.
- D-03 The preview frame gets `sandbox="allow-same-origin"` without `allow-scripts` so the page can size it to its content; no script can run in it.
- D-04 Kit code runs only on a person's confirm or rebuild, in a child process using the project's own toolchain.
- D-05 Components without stories of their own render with props captured from other stories (including stories files that own no component), then sample props from their declared types, then a bare render.
- D-06 Kit fonts reach Typography by registering the preview stylesheet's data-URL @font-face rules through the FontFace API while the system is open, so TypographyTable itself is unchanged.

### Open
- none

## Tasks

### T-01 Preview fields in contracts
- AC: AC-01 | Files: packages/contracts/src/design.ts, packages/contracts/src/designSystemEdit.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/design-system-previews && pnpm --dir packages/contracts exec vp test run

### T-02 Preview builder
- AC: AC-01, AC-02 | Files: apps/server/src/design/systems/previews/buildPreviews.ts, apps/server/src/design/systems/previews/runnerSource.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/design-system-previews && pnpm --dir apps/server exec vp test run src/design/systems/previews

### T-03 Build on confirm and rebuild RPC
- AC: AC-02, AC-04 | Files: apps/server/src/design/systems/DesignSystemService.ts, apps/server/src/design/systems/DesignSystemEditing.ts, apps/server/src/design/systems/DesignSystemRpc.ts, packages/contracts/src/designSystemImport.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/design-system-previews && pnpm --dir apps/server exec vp test run src/design/systems

### T-04 Components section renders preview files
- AC: AC-03, AC-04 | Files: apps/web/src/components/design/systems/workspace/ComponentsSection.tsx, apps/web/src/components/design/systems/workspace/componentCards.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/design-system-previews && pnpm --dir apps/web exec vp test run src/components/design/systems

### T-05 Stored fonts in previews and Typography
- AC: AC-05 | Files: apps/web/src/components/design/systems/workspace/kitFonts.ts, apps/web/src/components/design/systems/workspace/SystemWorkspace.tsx, packages/shared/src/designRender.ts | Test: cd ~/.specwithcode/m4/worktrees/specweave-studio/design-system-previews && pnpm --dir apps/web exec vp test run src/components/design/systems

### T-06 Rebuild Matchday and check in the app
- AC: AC-06 | Files: (EasyChamp .specweave/design) | Test: python3 -c "import json;p=json.load(open('/Users/antonabyzov/Projects/sw-easychamp/.specweave/design/systems/matchday-easy-champ-ui-kit/system.json'))['previews'];print(p);assert p['rendered']/p['total']>=0.9"
