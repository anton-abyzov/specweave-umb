# Implementation Plan: vskill Studio — First-class plugin authoring paths

## Overview

Four additive lanes inside `repositories/anton-abyzov/vskill/`. No existing code paths change behavior. Schema validation is delegated to `claude plugin validate <path>` so vskill never duplicates Claude Code's plugin schema.

## Architecture

### Components

- **`src/commands/plugin.ts`** *(new)* — Commander subcommand `vskill plugin new`. Mirrors the shape of [`src/commands/skill.ts`](repositories/anton-abyzov/vskill/src/commands/skill.ts). Wired in `bin/vskill.ts`.
- **`src/eval-server/authoring-routes.ts`** *(extended)* — Export `pluginJsonScaffold()` (currently file-private). Add `POST /api/authoring/convert-to-plugin` route.
- **`src/eval-ui/src/components/Sidebar.tsx`** *(extended)* — `partitionByGroupSource()` groups `authoring-project` skills sharing a `plugin` field (≥2 siblings). New empty-state CTA in `AuthoringPluginEmptyState`.
- **`src/eval-ui/src/components/CreateSkillModal.tsx`** *(extended)* — Reorder + relabel modes.
- **`src/eval-ui/src/api.ts`** *(extended)* — Add `convertToPlugin()` client.
- **`plugins/skills/skills/skill-builder/SKILL.md`** *(extended)* — New "Authoring a plugin (multi-skill bundle)" section.

### Data Model

No new entities. `SkillInfo` is unchanged. The Lane B2 endpoint accepts:

```ts
// POST /api/authoring/convert-to-plugin
interface ConvertToPluginRequest {
  // Absolute path to ANY skill in the candidate group. The server derives
  // `pluginDir = dirname(dirname(anchorSkillDir))`. The anchor approach
  // keeps client-side path math out of the wire contract — clients never
  // have to reason about whether the layout is `<root>/<X>/skills/<s>/`
  // (nested) or `<root>/skills/<s>/` (top-level).
  anchorSkillDir: string;
  pluginName: string;    // kebab-case
  description: string;
}
interface ConvertToPluginResponse {
  ok: true;
  pluginDir: string;          // absolute path of the resolved plugin root
  manifestPath: string;       // absolute path to written plugin.json
  validation: 'passed' | 'skipped';  // skipped when `claude` not on PATH
}
```

### API Contracts

- `POST /api/authoring/convert-to-plugin` — Lane B2.
  - 200: `{ ok, pluginDir, manifestPath, validation }`
  - 400: `anchor-outside-root` (anchorSkillDir not inside workspace root)
       | `invalid-anchor-shape` (anchorSkillDir's parent is not `skills/`)
       | `invalid-plugin-name` (pluginName not kebab-case)
       | `anchor-not-found` (anchorSkillDir does not exist or is not a directory)
       | `no-skills-to-convert` (resolved pluginDir has no `skills/*/SKILL.md`)
  - 409: `plugin-already-exists` — manifest already at `<pluginDir>/.claude-plugin/plugin.json`
  - 422: `validation-failed` — `claude plugin validate` rejected; manifest unlinked; body `{ error, stderr }`
  - 500: `skills-scan-failed` — non-ENOENT error reading `<pluginDir>/skills/` (EACCES, EIO, …)

## Technology Stack

- **CLI**: Commander (existing) + `node:child_process` `spawnSync` for `claude plugin validate`.
- **Backend**: `node:fs` (`writeFileSync`, `mkdirSync`, `unlinkSync`), `node:child_process` `spawnSync`. Same pattern as existing `safeJoin()` workspace guard.
- **Frontend**: existing fetch wrapper in `api.ts`. Existing `PluginTreeGroup` component for grouping render.

**Architecture Decisions**:

- **Delegate schema validation to `claude plugin validate`** instead of duplicating Claude Code's plugin schema in vskill. Rationale: maintainability — when Anthropic evolves the schema, vskill picks it up for free. Trade-off: adds a `claude` PATH dependency (soft-skip if missing).
- **B1 is purely client-side grouping** with `scopeV2` unchanged. Rationale: the backend remains the source of truth ("manifest exists or doesn't"); the sidebar just stops contradicting the URL. Trade-off: a folder with 2+ skills that the user wants to keep flat will show grouped — acceptable since they can collapse the group, and the visual cue ("Not a plugin yet") is honest.
- **Reuse `pluginJsonScaffold()`** from `authoring-routes.ts` rather than copying the JSON template into `commands/plugin.ts`. Requires exporting the helper.
- **Soft-skip validation when `claude` is missing**. Rationale: vskill should still be usable without Claude Code installed (e.g. in CI for skill linting). The CLI prints a warning; the endpoint returns `validation: 'skipped'`.
- **No new `scopeV2` value** for "implicit plugin candidate". Rationale: avoid expanding the union type and the dedupe precedence table for what is purely a UI concern.

## Implementation Phases

### Phase 1: Foundation (Lane A backend reuse)
1. Export `pluginJsonScaffold(pluginName, description)` from `authoring-routes.ts`.
2. Add a thin wrapper `validateClaudePlugin(pluginPath)` (also in `authoring-routes.ts` or a new `src/core/plugin-validator.ts`) that runs `spawnSync('claude', ['plugin', 'validate', pluginPath])` and returns `{ ok, stderr, skipped }`.

### Phase 2: Lane A — `vskill plugin new` CLI
3. Create `src/commands/plugin.ts` with `new <name> [--description] [--with-skill <skill>]`.
4. Wire into `bin/vskill.ts`.
5. Vitest: `src/commands/plugin.test.ts` — happy path, name collision, invalid kebab, `--with-skill`, `claude` missing soft-skip.

### Phase 3: Lane B2 — Convert endpoint
6. Add route handler `POST /api/authoring/convert-to-plugin` to `authoring-routes.ts`.
7. Vitest: extend `src/eval-server/authoring-routes.test.ts` with happy path, 400/409/422 branches, soft-skip path.

### Phase 4: Lane B1 + B2 — Sidebar grouping + Convert UI
8. Modify `partitionByGroupSource()` in `Sidebar.tsx` to bucket `authoring-project` skills by `plugin` field; emit `candidatePluginGroups: { dir, skills[] }[]`.
9. Render groups via existing `PluginTreeGroup` styling with "Not a plugin yet · Convert →" pill.
10. Update `AuthoringPluginEmptyState` to list candidate dirs with a "Promote `<dir>/`" button.
11. Add `convertToPlugin()` to `api.ts`.
12. Add a small `<ConvertToPluginDialog>` component (modal with name + description fields, prefilled).
13. On success, dispatch `refreshSkills()` (the same hook the create-skill flow uses — see [feedback `0788-studio-create-skill-redirect-fix`](.specweave/state/interview-0788-studio-create-skill-redirect-fix.json) for the established pattern).

### Phase 5: Lane C — skill-builder docs
14. Edit `plugins/skills/skills/skill-builder/SKILL.md`: add "Authoring a plugin (multi-skill bundle)" section. Bump version frontmatter 1.0.3 → 1.0.4.

### Phase 6: Lane D — Modal polish
15. Edit `CreateSkillModal.tsx`: reorder mode options to ["Standalone skill", "Add to existing plugin", "Plugin (multi-skill)"] as peer cards, not nested radios. Add captions per AC-US5-02.

### Phase 7: Verification
16. Run unit tests: `npm test` in `repositories/anton-abyzov/vskill/`.
17. Build: `npm run build` (typescript) + `npm run build:ui` (Vite for eval-ui bundle).
18. Live-test against `~/Projects/TestLab/hi-anton/`:
    - Backend smoke: `curl POST /api/authoring/convert-to-plugin`.
    - UI: `npx vskill@<dev-tag> studio` + preview tools (`preview_start`, `preview_click`, `preview_snapshot`) — capture before/after screenshots.
19. Spawn one Explore sub-agent post-fix to independently re-walk `plugin-scanner.ts` + `skill-scanner.ts` and confirm no regression.

## Testing Strategy

- **Unit/Integration (Vitest)**: 2 new specs (`commands/plugin.test.ts`, extend `authoring-routes.test.ts`). Cover all 5 ACs of US-001 + all 6 ACs of US-003.
- **UI smoke (Playwright optional)**: live preview-tool drive against TestLab/hi-anton. Capture sidebar before/after for US-002 and US-003.
- **Regression**: existing `0740-dedupe-by-dir` tests must still pass. Existing Studio create-skill flow (`0698`, `0788`) must still pass.

## Technical Challenges

### Challenge 1: `claude` not on PATH in CI
**Solution**: `validateClaudePlugin()` returns `{ skipped: true }` when `spawnSync` errors with `ENOENT`. CLI prints "warning: claude CLI not found, skipping plugin schema validation"; endpoint returns `validation: 'skipped'`.
**Risk**: User scaffolds an invalid plugin and doesn't notice. **Mitigation**: surface "skipped" status prominently; document that real validation requires `claude` installed.

### Challenge 2: Sidebar grouping for 2+ skills under any shared `skills/` parent
**Solution (revised during implementation)**: group whenever 2+ `authoring-project` skills share the same `plugin` (parent dir) value, including the workspace-root layout `<root>/skills/<a>/SKILL.md`. The original plan proposed restricting grouping to `dir !== <workspaceRoot>`, but the TestLab/hi-anton verification showed that workspace-root candidates (e.g. a project that decided to use `<root>/skills/` directly) are exactly the case the user wants to convert in one click. The convert endpoint explicitly supports this layout (test `converts top-level Root layout` at `authoring-routes.test.ts:371`). The "Convert →" CTA + the "Not a plugin yet" pill make the user's intent explicit, so accidental conversion is unlikely. Single-skill buckets continue to render flat (no spurious group-of-one).
**Risk**: edge case with deeply nested `skills/` folders. **Mitigation**: B1 still only triggers when 2+ skills share the same parent — deeper nesting just produces more buckets, never auto-promotes.

### Challenge 3: Race between Convert endpoint write and discovery scan
**Solution**: endpoint returns synchronously after `writeFileSync` + validate; frontend triggers `refreshSkills()` which re-fetches `/api/skills`. The scanner walks fresh on every request — no caching.
**Risk**: validator takes >1s and the dialog appears stuck. **Mitigation**: the dialog already shows a spinner during the request; `claude plugin validate` is typically <300ms.
