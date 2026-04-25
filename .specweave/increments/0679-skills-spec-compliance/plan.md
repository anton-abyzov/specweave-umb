---
increment: 0679-skills-spec-compliance
title: SKILL.md Spec Compliance — Technical Plan
type: plan
status: draft
created: 2026-04-22
architect: sw:architect
---

# Plan: SKILL.md Spec Compliance

## 1. Architecture Overview

The canonical SKILL.md specification at **https://agentskills.io/specification** defines a frontmatter schema where `tags` and `target-agents` live under a `metadata:` block:

```yaml
---
name: my-skill
description: ...
version: 1.0.0
metadata:
  tags:
    - devtools
    - cli
  target-agents:
    - claude-code
    - cursor
---
```

vSkill currently emits these two fields at the top level. This increment moves them down one level. The migration is a localized YAML refactor — no semantic change to the fields themselves, just placement. The impact is contained because:

1. One primary emitter (`src/eval-server/skill-create-routes.ts`) writes every SKILL.md the product produces.
2. 0670-skill-builder-universal uses templates under `.specweave/increments/0670-skill-builder-universal/`; those templates mirror the emitter's shape.
3. Golden-file fixtures under `src/**/__tests__/fixtures/` anchor the shape and are the exact surface that tells us when something drifted.

The change is completed with a validator integration: external `skills-ref validate` runs post-creation in the CLI (warn-only) and in CI (blocking, via a new `lint:skills-spec` npm script).

## 2. Component Map

| File | Change | Rationale |
|---|---|---|
| `src/eval-server/skill-create-routes.ts` | Move `tags` and `target-agents` from top-level frontmatter into a `metadata:` sub-block | Primary emitter |
| `.specweave/increments/0670-skill-builder-universal/` (template files) | Update template shapes to match | 0670 lockstep |
| `.specweave/increments/0670-skill-builder-universal/tasks.md` (prose only, no state change) | Add a one-line note pointing to 0679 for the new shape | 0670 cross-ref |
| `src/eval-server/__tests__/fixtures/skill-create-frontmatter.golden.md` | Create golden file with compliant shape | Shape lock |
| `src/eval-server/__tests__/skill-create-frontmatter.test.ts` | New golden-file Vitest test | TDD gate |
| `src/cli/skill.ts` (post-creation hook in `vskill skill new`) | Invoke `skills-ref validate`; warn on fail; `--strict` blocks | User-facing validation |
| `src/cli/__tests__/skill-new-post-validation.test.ts` | New CLI test | TDD gate |
| `package.json` | Add `lint:skills-spec` script | CI gate |
| `.github/workflows/*.yml` (if present) or equivalent CI config | Wire the new script into PR checks | CI enforcement |
| `README.md` | Add a "SKILL.md spec compliance" subsection; migration note for downstream | Discoverability |

## 3. Migration Mechanics

The emitter today has a block like:

```ts
const fm = {
  name,
  description,
  version,
  tags,             // <-- moves
  "target-agents": targetAgents,   // <-- moves
  // ...other fields stay
};
```

After the change:

```ts
const fm = {
  name,
  description,
  version,
  // ...other top-level fields stay
  metadata: {
    tags,
    "target-agents": targetAgents,
  },
};
```

No new YAML library is needed — existing serializer handles nested objects natively. Key ordering is stabilized so golden-file diffs stay minimal.

## 4. Validator Integration

`skills-ref` is a separate CLI tool that implements the canonical spec's validator. Integration is a subprocess call:

```ts
const result = spawnSync("skills-ref", ["validate", skillPath], { encoding: "utf-8" });
```

- Happy path (`result.status === 0`): silent success.
- Failure (`result.status !== 0`): print `result.stderr` under a "Validation warnings" header, return from the post-creation step without throwing.
- `--strict` flag: failure returns exit code 1 from the overall CLI.
- Missing binary (`ENOENT`): print a one-line install hint, continue with exit 0.

The CI script (`lint:skills-spec`) runs `skills-ref validate` over every `**/SKILL.md` in the repo. If `skills-ref` is absent in CI, the script fails loudly — CI must have deterministic tooling.

## 5. Testing Strategy

- **Golden-file (Vitest)**: one canonical input → one canonical output. Test file compares emitted frontmatter byte-for-byte to the checked-in golden. Any future shape change requires updating the golden file, which forces the author to acknowledge the change.
- **Unit (Vitest)**: post-creation validation under four scenarios (success, validator fail non-strict, validator fail strict, missing binary).
- **Integration (Vitest + execa)**: actual CLI invocation with a stubbed `skills-ref` binary on PATH (via a test `bin/` folder) — exercises the subprocess plumbing.

## 6. ADRs

### ADR-0679-01: Golden-file tests, not schema-assertion tests

**Status**: Accepted
**Context**: Two options to lock the shape: (a) assert-by-schema ("`frontmatter.metadata.tags` is array-of-string"), (b) golden-file comparison (byte-for-byte match against a checked-in fixture).
**Decision**: Use golden files. The readable diff when something drifts is the primary value — schema assertions pass silently when key ordering drifts or when a new field sneaks in.
**Consequences**: Golden files must be regenerated when any intentional emitter change lands; that is the correct friction. `npx vitest -u` updates goldens in one command.

### ADR-0679-02: `skills-ref validate` is warn-only by default in the CLI, blocking in `--strict` and in CI

**Status**: Accepted
**Context**: Three options: (a) always block on `skills-ref` failure, (b) always warn, (c) default-warn, `--strict` blocks, CI always blocks.
**Decision**: (c). Default-warn keeps the happy path fast for solo developers; `--strict` is opt-in for teams that want local enforcement; CI blocks unconditionally because CI is where the line is drawn.
**Consequences**: Developers on a flaky network or without `skills-ref` installed are not blocked locally. CI remains deterministic.

### ADR-0679-03: Keep 0670's tasks.md execution state untouched

**Status**: Accepted
**Context**: 0670 is in flight at 3/35. This increment touches 0670's template files but must not interfere with 0670's task-completion state.
**Decision**: Only edit 0670's template files and add a one-line prose note in 0670's tasks.md pointing to 0679. Do not mark any 0670 task as completed or modify its task structure.
**Consequences**: 0670 continues its execution with updated templates; the prose note is harmless.

## 7. Rollout Order

1. Write the golden file for the new shape (test fails first).
2. Update the primary emitter in `skill-create-routes.ts` (test passes).
3. Update 0670 templates (golden file at 0670's side passes if present, or a new one is added).
4. Wire `skills-ref validate` into the CLI (warn path).
5. Add `--strict` flag.
6. Add the `lint:skills-spec` script.
7. Wire CI.
8. Update README with the migration note.

## 8. Risks

- **`skills-ref` availability**: If the validator is not yet published, the validator-integration steps (US-003, US-004) must defer. The shape-migration steps (US-001, US-002, US-005) are independent and can ship even if the validator is unavailable.
- **Downstream consumers of the old shape**: Anything that reads `frontmatter.tags` at the top level breaks. The README migration note calls this out. Internal consumers in vSkill itself must be audited; the search for `\.tags` access is part of T-002.

## 9. Code-Review Follow-Up (2026-04-25)

The first closure pass surfaced six defects (F-001..F-006). Resolution:

- **F-001** (HIGH, silent reader breakage): production reader `parseSkillFrontmatter` extended to recognize the `metadata:` block and surface its children at the top level (back-compat). Three reader call sites updated: (1) `matchExistingPlugin()` in `skill-create-routes.ts` now uses the parser; (2) `buildSkillMetadata()` in `api-routes.ts` automatically benefits via the parser fix; (3) the activation-test handler at `api-routes.ts:2687` now uses the parser instead of the regex. Round-trip test added: `src/eval-server/__tests__/skill-emitter-roundtrip.test.ts` (7 tests, all GREEN).
- **F-002** (HIGH, AC drift): decision **(b) defer**. 0670 has no SKILL.md template files on disk to update. AC-US2-01 and AC-US2-03 downgraded from `[x]` to `[ ]` with DEFERRED + strikethrough explanation in spec.md. Runtime guardrail: the `lint:skills-spec` CI gate from US-004 globs the entire repo, so 0670's templates are caught the moment they land. AC-US2-02 (the cross-reference prose note that was actually delivered) remains `[x]`.
- **F-003** (MEDIUM, validator UX): built-in fallback in `scripts/validate-skills-spec.ts` now prints two `console.warn` lines that prominently mark coverage as partial when `skills-ref` is missing.
- **F-004** (MEDIUM, narrow test surface): test helpers (`buildSkillMdForTest`, `parseFrontmatterForTest`) now re-exported from `src/eval-server/__tests__/helpers/skill-md-test-helpers.ts`. Underlying exports tagged `@internal`. All test imports moved to the helpers module.
- **F-005** (MEDIUM, missing `name:`): `buildSkillMd` now emits `name: <data.name>` as the first frontmatter key when `data.name` is set. Golden fixtures (`skill-emitter-before.md`, `skill-emitter-after.md`) updated; key-order test in `skill-emitter-spec-compliance.test.ts` extended to lock `name: → description:` ordering. Also: description-emission now collapses CR/LF to spaces before quote-escaping (defensive against AI-generated multi-line descriptions; F-007-adjacent hardening in the same code site).
- **F-006** (MEDIUM, no round-trip test): covered by the new `skill-emitter-roundtrip.test.ts` from F-001.

Pre-existing repo violation surfaced by lint gate: `plugins/skills/skills/skill-builder/SKILL.md` had `tags:` at the root alongside an unrelated `metadata:` block (homepage/version). Moved tags into the metadata block. This is unrelated to 0679's emitter fix; it was a hand-edited file that pre-dated this work.
