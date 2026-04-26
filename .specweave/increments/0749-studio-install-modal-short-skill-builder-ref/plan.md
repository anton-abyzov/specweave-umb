# Implementation Plan: Studio install modal — use short skill-builder ref

## Overview

Two paired hardcoded constants in the vskill repo encode the skill-builder install command — one for what the modal *displays*, one for what the eval-server *spawns*. Both currently use the long disk-path form `anton-abyzov/vskill/plugins/skills/skills/skill-builder`. This plan swaps both (and their lockstep test assertions) to the canonical 3-part shorthand `anton-abyzov/vskill/skill-builder`. No CLI change. No new files. ~4 lines of source delta + 2 test assertions.

## Design

### Affected files

| # | File | Line | Change |
|---|---|---|---|
| 1 | `repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallEngineModal.tsx` | 17 | `COMMAND_BY_ENGINE.vskill` string literal |
| 2 | `repositories/anton-abyzov/vskill/src/eval-server/install-engine-routes.ts` | 55 | `INSTALL_COMMANDS.vskill.args[1]` string literal |
| 3 | `repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/InstallEngineModal.test.tsx` | 114 | expected display string assertion |
| 4 | `repositories/anton-abyzov/vskill/src/eval-server/__tests__/install-engine-routes.test.ts` | 251 | expected argv assertion |

### Display↔spawn parity

The two source constants form a parity pair: `InstallEngineModal.tsx` shows the user what `install-engine-routes.ts` will spawn. They drift independently if edited carelessly. This increment edits both in the same change set; the two corresponding test files pin both ends so future drift fails CI.

### Resolution path (unchanged)

When `vskill install anton-abyzov/vskill/skill-builder` runs, `add.ts:1958-1992` parses 3 parts → calls `detectMarketplaceRepo("anton-abyzov", "vskill")` → finds `.claude-plugin/marketplace.json` → iterates `getAvailablePlugins(manifest)` → for each plugin probes `<pluginPath>/skills/skill-builder/SKILL.md` on the default branch. Plugin `skills` (source `./plugins/skills`) probes `plugins/skills/skills/skill-builder/SKILL.md` → 200 OK → calls `installSingleSkillLegacy(owner, repo, "skill-builder", opts, "plugins/skills/skills/skill-builder/SKILL.md", "skills")`. Final installed bytes are byte-for-byte identical to the long-form path.

## Rationale

**Why the long form was used originally**: when the install-engine modal was first wired (per CHANGELOG: "Bundled `skill-builder` meta-skill with path A/B/C fallback chain"), the simplest correct ref was the literal disk path — no risk of marketplace-probing edge cases, every reader can see exactly what file is being fetched. Bulletproof but ugly.

**Why short form is now safe**: the 3-part marketplace-probe path in `add.ts` has been in production through multiple releases (covered by `add.ts` tests) and is the standard install ref shape used everywhere else in the docs and marketplace UI. The long form was only ever a defensive choice; it's no longer needed.

**Why we don't add a CLI alias for the long form**: the long form already works (the current modal proves it — the install succeeds). We're not removing anything from the CLI; only changing what we *display*. If a user has cached muscle memory for the long form, it keeps working.

**Why we don't extract a shared constant**: tempting (the modal+server pair is a classic shared-string smell), but premature for two engines (`vskill` and `anthropic-skill-creator`) where one has the modal living in `eval-ui/` and the other has the spawn logic in `eval-server/` — packages that don't share build boundaries. Test parity is sufficient enforcement at this scale. Revisit if a third engine appears.

**Why this isn't a CLI fix**: the CLI is correct. The bug is presentational. Fixing it where the constant is hardcoded keeps the change surface tiny and proportional to the user-visible defect.

## Architecture

### Components touched
- **eval-ui** (Vite-built React app, served by eval-server as a static bundle): the InstallEngineModal component renders the confirm dialog with the command preview.
- **eval-server** (Node Express-style server, ships with `vskill studio`): the install-engine-routes endpoint accepts a POST with `{ engine }`, spawns `vskill install <ref>` via `child_process.spawn`, and streams stdout/stderr over SSE.

### Components NOT touched
- `vskill` CLI (`src/commands/add.ts`, `src/discovery/*`, `src/marketplace/*`) — the resolver is correct and stays as-is.
- vskill-platform — separate repo, separate build, separate install command source (database-driven via Prisma).
- skill-builder itself (`plugins/skills/skills/skill-builder/`) — the artifact being installed is unchanged.

## Technology Stack

- **TypeScript** (existing) — strict ESM with `.js` import extensions in source per project convention.
- **React 18 + Vitest** (existing) — for InstallEngineModal component test.
- **Node child_process + Vitest** (existing) — for install-engine-routes server test.

## Implementation Phases

### Phase 1: RED — pin tests to the new short form (must fail against current source)
- T-001: Update `InstallEngineModal.test.tsx:114` expected string to `vskill install anton-abyzov/vskill/skill-builder`. Run `npx vitest run InstallEngineModal.test.tsx` — assert FAIL.
- T-002: Update `install-engine-routes.test.ts:251` expected argv element to `anton-abyzov/vskill/skill-builder`. Run `npx vitest run install-engine-routes.test.ts` — assert FAIL.

### Phase 2: GREEN — apply source change (tests pass)
- T-003: Edit `InstallEngineModal.tsx:17` — replace string literal.
- T-004: Edit `install-engine-routes.ts:55` — replace argv element.
- T-005: Re-run both vitest files — assert PASS.

### Phase 3: REFACTOR — verify nothing else hardcodes the old form
- T-006: `grep -rn "anton-abyzov/vskill/plugins/skills/skills/skill-builder" repositories/anton-abyzov/vskill/src/ repositories/anton-abyzov/vskill/test/ repositories/anton-abyzov/vskill/e2e/` — must be 0 hits. (Excluded: `coverage/`, `dist/`, `node_modules/`.)

### Phase 4: VERIFY — real install end-to-end
- T-007: From a temporary directory, install the locally-built vskill, run `vskill studio`, click Install on the VSkill skill-builder authoring engine, click Run install, observe SSE stream complete with green checkmark, verify `~/.agents/skills/skill-builder/SKILL.md` exists. (Or equivalent: `vskill install anton-abyzov/vskill/skill-builder` from CLI returns success and emits the skill files.)

## Testing Strategy

- **Unit**: Vitest, two files, two assertion edits. No new test files. Existing tests already exercise the install-engine modal render path and the route's argv-construction path.
- **Integration**: not needed — the only integration risk (display↔spawn drift) is enforced by the parity of the two updated assertions.
- **E2E**: manual real install from `vskill studio` (Phase 4). Playwright coverage for the modal exists for other flows but is not required for this string-only delta.
- **Coverage**: target stays at 90% (config). No coverage delta expected — same lines exercised, just different string content.

## Technical Challenges

### Challenge 1: ensuring the 3-part ref actually resolves end-to-end
**Solution**: rely on existing `add.ts` marketplace probing (verified by reading the resolver in this conversation) plus a real install in Phase 4.
**Risk**: if marketplace.json changed shape since the last `add.ts` integration test, probing might fail. **Mitigation**: read `marketplace.json` before editing — it still has `name: "skills"`, `source: "./plugins/skills"`. Also: Phase 4 manual install is the ground-truth gate; if it fails we revert.

### Challenge 2: preventing future regression to the long form
**Solution**: the two updated tests are the regression gate. If anyone re-introduces the long form in either constant, both vitest assertions fail.
**Risk**: someone bypasses tests with `--no-verify`. **Mitigation**: project CLAUDE.md forbids `--no-verify`; CI runs the same vitest command on every PR.
