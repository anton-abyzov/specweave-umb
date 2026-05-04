---
increment: 0822-vskill-clone-skill-fork
title: "vskill clone — architecture plan"
type: feature
status: planned
created: 2026-05-01
---

# Architecture Plan: `vskill clone`

## 1. Architecture Overview

A new CLI command, `vskill clone <source>`, that deep-copies an installed skill (or whole plugin) from one of three discovery locations (project `.claude/skills/`, personal `~/.claude/skills/`, plugin cache `~/.claude/plugins/cache/...`) into one of three target shapes (standalone skill, addition to an existing user-owned plugin, or a fresh new plugin), rewriting authorship in `SKILL.md` frontmatter and writing fork provenance to `.vskill-meta.json`. Optionally scaffolds a GitHub repo via `gh`. The implementation lives entirely under `src/clone/` and `src/commands/clone.ts`, **introduces no new runtime dependencies**, and reuses three existing primitives (`copyOwnSkillFiltered` from scope-transfer, `ensureFrontmatter`-style regex helpers from `src/installer/frontmatter.ts`, and `writeProvenance` from `src/studio/lib/provenance.ts`) instead of duplicating their logic. Atomicity is achieved via a write-to-`.tmp` → validate → atomic-rename pipeline modelled after the rollback pattern at `src/commands/add.ts:838+`.

This is a CLI-only increment. A studio UI "Fork" affordance is deferred to a follow-up increment.

## 2. Module Map

| Module | Status | Purpose |
|---|---|---|
| `src/clone/types.ts` | NEW | `SkillSource`, `CloneTarget`, `CloneOptions`, `CloneResult`, `ForkProvenance` (re-exports extended `Provenance`) |
| `src/clone/skill-locator.ts` | NEW | Discover a skill across the 3 source locations; return all matches with their source kind |
| `src/clone/reference-scanner.ts` | NEW | Scan SKILL.md body for cross-skill refs (`` `sw:foo` ``, `Skill({ skill: "sw:foo" })`, `/sw:foo`) and self-name occurrences — **report only, no rewrite** |
| `src/clone/target-router.ts` | NEW | `writeStandalone`, `writeToPlugin` (two-phase commit on plugin manifest), `writeNewPlugin` |
| `src/clone/github-scaffold.ts` | NEW | `gh repo create` + initial commit; takes injectable `runGh` for testability |
| `src/clone/provenance-fork.ts` | NEW | Thin helper around `writeProvenance` that merges `forkedFrom` + `originalSource` and extends `forkChain` when source already had a sidecar |
| `src/commands/clone.ts` | NEW | Orchestrator: validate → resolve → copy `.tmp` → rewrite frontmatter → write sidecar → validate → atomic rename(s) → optional gh |
| `src/installer/frontmatter.ts` | EXTEND | Add exported `applyForkMetadata(content, { name, author, version, forkedFrom })` — regex-based, preserves unknown frontmatter fields, idempotent |
| `src/studio/types.ts` | EXTEND | Extend `Provenance` with optional `forkedFrom`, `originalSource`, `forkChain` |
| `src/index.ts` | EXTEND | Register `clone` command with Commander (alongside existing `install`, `add`, `studio`, etc.) |

**No new dependencies.** All work uses the existing toolbox: Commander (already wired), node:fs, node:path, node:child_process for the optional `gh` invocation.

## 3. Provenance Schema (extending `Provenance`)

The current `Provenance` shape (`src/studio/types.ts:34-39`) is preserved as-is. Three optional fields are appended:

```typescript
export type Provenance = {
  // existing — preserved unchanged
  promotedFrom: "installed" | "global";
  sourcePath: string;
  promotedAt: number;
  sourceSkillVersion?: string;

  // NEW — fork provenance
  forkedFrom?: {
    source: string;          // e.g., "sw/ado-mapper"
    version: string;         // version observed at clone time
    clonedAt: string;        // ISO timestamp
  };
  originalSource?: {         // present only when the source itself was already a fork
    repoUrl?: string;
    skillPath?: string;
  };
  forkChain?: string[];      // chain of namespaces if forked-from-fork (depth >= 2)
};
```

**Forking a fork (chain semantics)**: when the source skill already has a `.vskill-meta.json` with `forkedFrom`, the clone command:
1. Captures the source's previous `forkedFrom.source` (e.g., `sw/ado-mapper`) as the head of the new `forkChain`.
2. Prepends any pre-existing `forkChain` entries after that head (oldest-last order).
3. Sets the new `forkedFrom` to the immediate parent (the source we just copied from, e.g., `anton/ado-mapper`).
4. Carries `originalSource` forward unchanged when present (it always points to the chain's root).

This keeps `forkedFrom` always referring to the immediate parent and `forkChain` always referring to the ancestry — no ambiguity. **Existing skills without sidecars are treated as roots**: their `forkedFrom` becomes the new clone's `forkedFrom`, with no `forkChain`.

## 4. CLI Surface

```
vskill clone <source>                          # source = "ado-mapper" or "sw/ado-mapper"
  --target <kind>                              # standalone | plugin | new-plugin (interactive prompt if omitted)
  --path <dir>                                 # required for --target standalone | new-plugin
  --plugin <name>                              # required for --target plugin; OR (without <source>) clones a whole plugin
  --plugin-name <name>                         # required for --target new-plugin
  --author <name>                              # default: git config user.name
  --namespace <ns>                             # default: slugified --author
  --github                                     # scaffold GitHub repo via gh after files commit
  --force                                      # overwrite existing target (otherwise abort with collision error)
  --source <kind>                              # project | personal | cache (auto-detect; prompt if ambiguous)
  --dry-run                                    # print all planned writes; touch nothing on disk
```

**Validation rules** (enforced before any disk write):
- `--target` value must be one of the three literals (Commander `.choices()`).
- `--path` required when `--target` is standalone or new-plugin.
- `--plugin` required when `--target` is plugin.
- `--plugin-name` required when `--target` is new-plugin.
- `--namespace` defaults to slugified `--author`; both default through git config.
- `--source` auto-detected via `skill-locator`; if multiple matches, interactive prompt unless `--source` is explicit.
- Whole-plugin form: `vskill clone --plugin <name>` (no `<source>`) — clones every skill in the plugin under one new `--namespace`. Confirmation prompt lists every target skill before any write occurs.

## 5. Atomicity Flow

The 9-step atomic pipeline in `src/commands/clone.ts`:

1. **Validate source**: `skill-locator` confirms the source exists; SKILL.md is read and the frontmatter parses.
2. **Resolve target**: route through `target-router`. If the target path already exists, abort unless `--force`. If `--force`, defer the deletion until step 8 (do not delete the live target before the new content is staged).
3. **Copy via `copyOwnSkillFiltered`** (reused from `src/studio/lib/scope-transfer.ts`) into `<target>.tmp`. This already filters `.vskill-meta.json` and `.vskill-source.json` so we start with a clean slate.
4. **Apply `applyForkMetadata`** to `<target>.tmp/SKILL.md` — rewrites `name`, `author`, `version` while preserving every other frontmatter field, idempotent on rerun.
5. **Write provenance** via `provenance-fork.writeForkProvenance(<target>.tmp, { forkedFrom, originalSource })`. Source's existing sidecar (if any) feeds `forkChain` extension.
6. **Validate cloned**: re-parse the rewritten frontmatter; verify any `agents/*.md` referenced files still exist in `<target>.tmp`. Abort and `rm -rf <target>.tmp` on failure.
7. **For `--target plugin`**: also stage the updated `plugin.json` next to the plugin manifest as `<plugin>/plugin.json.tmp`. Both this and step-3's `<target>.tmp` are committed together.
8. **Atomic rename(s)**: `rename(<target>.tmp, <target>)` (and `rename(<plugin>/plugin.json.tmp, <plugin>/plugin.json)` for plugin target). If `--force` was set, the existing target is removed only at this point, immediately before the rename — minimizing the window where the user has neither the old nor the new copy on disk. If any rename fails, surviving `.tmp` paths are removed; no partial state remains.
9. **Optional `gh repo create` + initial commit + push** via `github-scaffold` — runs **only after** files are durably on disk. Failure here surfaces as a warning; the on-disk clone remains intact.

**Reference for the rollback pattern**: `src/commands/add.ts:845-866` (`rollbackInstall` — best-effort `rmSync` per location, swallow errors per call so a partial filesystem state never suppresses the underlying diagnostic). We replicate the same shape for the `<target>.tmp` cleanup paths.

## 6. Reuse Map

| Existing primitive | Reused as-is | Extended | New code that wraps it |
|---|---|---|---|
| `copyOwnSkillFiltered` (scope-transfer.ts) | YES — straight skill-dir copy with `.vskill-meta.json` + `.vskill-source.json` filtering | — | `target-router.writeStandalone`/`writeToPlugin`/`writeNewPlugin` call into it |
| `copyPluginFiltered` (copy-plugin-filtered.ts) | YES — used for whole-plugin clone (`--plugin` without `<source>`) | — | `target-router.writeNewPlugin` (whole-plugin path) |
| `ensureFrontmatter` (installer/frontmatter.ts) | NO — does not rewrite `author`/`version` | — | `applyForkMetadata` is a sibling, not a wrapper |
| `quoteYAMLValue` (installer/frontmatter.ts) | YES | — | `applyForkMetadata` reuses for value escaping |
| `extractDescription` (installer/frontmatter.ts) | YES | — | reused only when source SKILL.md has no description |
| `writeProvenance` (provenance.ts) | YES | — | `provenance-fork.writeForkProvenance` calls into it |
| `readProvenance` (provenance.ts) | YES — to detect chained forks | — | `provenance-fork.writeForkProvenance` reads source sidecar before writing |
| `Provenance` type (studio/types.ts) | NO — needs new optional fields | YES — append `forkedFrom`, `originalSource`, `forkChain` | re-exported from `clone/types.ts` as `ForkProvenance` |
| `rollbackInstall` pattern (add.ts:845) | NO — different shape (rm by skillName + lockfile) | — | `clone.ts` orchestrator borrows the **shape** (best-effort per-path rm) but writes its own loop over `.tmp` paths |
| Commander wiring style (index.ts) | YES — same `.command(...).option(...).action(async (a, opts) => { const { fn } = await import(...); await fn(a, opts); })` template | — | `clone` command added at the appropriate alphabetical-ish slot |

**No primitive is duplicated.** Where an existing helper was close-but-not-quite (e.g., `ensureFrontmatter` only ensures fields exist; it does not rewrite them), a sibling function is added in the same file rather than copying its regex.

## 7. Cross-Cutting Decisions (settled — restated)

| Decision | Rationale |
|---|---|
| **No new runtime dependencies** | Regex-based frontmatter manipulation matches the house style at `src/installer/frontmatter.ts`. No need for gray-matter, js-yaml, or any other parser. |
| **No lockfile entry for cloned skills** | Cloned skills are user-owned, not registry-installed. A lockfile entry would make `vskill outdated` undefined for forks (compared against what?). |
| **No chmod preservation** | Skills are plain text; the existing copy helpers (`copyOwnSkillFiltered`, `copyPluginFiltered`) do not preserve mode and no skill in the corpus depends on the executable bit. |
| **Cross-skill refs are report-only, NEVER auto-rewritten** | Cross-skill refs point to OTHER skills, not the cloned one. Auto-rewriting would silently break dependencies. The reference-scanner appends a human-readable summary to stdout for the user to act on. Self-name occurrences in prose are also reported, never rewritten. |
| **Studio UI deferred** | This increment is CLI-only. The eval-server has no Fork affordance today, and adding one is a UI/UX scope of its own. Tracked as a follow-up increment. |
| **No publish flow** | The cloned skill goes to local disk and (optionally) a GitHub repo via `gh`. Publishing to verified-skill.com is an orthogonal concern with its own UX (versioning, scan, signature). |

## 8. Test Strategy

| Layer | Coverage | New test files |
|---|---|---|
| **Unit (Vitest, `vi.hoisted` style)** | `skill-locator` (mocked fs across the 3 locations); `applyForkMetadata` (preserves unknown fields, idempotent on rerun, malformed-frontmatter handling); `reference-scanner` (detects all 3 patterns with no false positives in fenced code blocks); `target-router` branches with mocked `copyOwnSkillFiltered` | `test/clone/skill-locator.test.ts`, `test/clone/reference-scanner.test.ts`, `test/clone/target-router.test.ts`, `test/clone/provenance-fork.test.ts`, `test/installer/frontmatter-fork.test.ts` (extends existing frontmatter test file) |
| **Integration (mkdtemp + `HOME` override)** | All 9 source × target combinations (3 sources × 3 targets); cloning a skill with `agents/*.md` subdir; cloning into target that already has a `.vskill-meta.json` (collision); chained fork (depth 2); permission-denied target (graceful error, no partial state); malformed plugin manifest at target (error before any copy) | `test/clone/clone.integration.test.ts` |
| **Manifest atomicity** | Failure-injection on `plugin.json` write rolls back the skill copy; failure-injection on the second `rename` rolls back the first | `test/clone/clone.atomicity.test.ts` |
| **github-scaffold** | Injectable `runGh` fake; verifies args passed and graceful skip when fake throws ENOENT (i.e. `gh` not installed) | `test/clone/github-scaffold.test.ts` |
| **CLI smoke (CI)** | `node dist/bin.js clone --help` assertion added to `.github/workflows/ci.yml` | adds one step to existing CI workflow |

**Coverage target**: 90% statement / 90% branch on `src/clone/**`, matching the spec's `coverage_target: 90`. The atomicity tests are the highest-value because they exercise the rollback/rename order that's hardest to spot in code review.

**Existing fixtures reused**: `e2e/fixtures/skills/lint-markdown-files`, `e2e/fixtures/test-plugin/skills/test-skill`, `e2e/fixtures/easychamp/skills/tournament-manager`. No new fixture corpus required.

## 9. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| User clones a skill that depends on another skill (`Skill({ skill: "sw:foo" })`), then can't find the dependency | Medium | `reference-scanner` reports every cross-skill ref to stdout after success. User decides whether to also clone the dependency. **Never auto-rewrite.** |
| `gh repo create` succeeds but `git push` fails (auth/rate-limit), leaving an empty remote | Low | `github-scaffold` is the last step. Failure is logged as a warning; on-disk clone is unaffected. The user can rerun `gh` manually with the same args. |
| Target path partially overwritten if the rename fails mid-pipeline | Low | All work happens in `<target>.tmp`. `--force` deletion of the live target is deferred until immediately before the rename (step 8). On rename failure: `rm -rf <target>.tmp`, no partial state. |
| Idempotence regression in `applyForkMetadata` (running clone twice produces drift) | Medium | Unit test asserts byte-equal output across two consecutive `applyForkMetadata` calls on the same input. |
| Source has malformed YAML frontmatter | Low | `applyForkMetadata` falls back to `ensureFrontmatter`-style regex parse; on parse failure, abort with a clear error before any copy occurs. |
| Plugin manifest JSON corruption mid-write | Low | Two-phase commit: `<plugin>/plugin.json.tmp` written first, then renamed alongside the skill dir rename. Failure on either rename rolls back the other's `.tmp`. |
| Whole-plugin clone partially completes (some skills written, some failed) | Medium | Whole-plugin clone uses one `<plugin-target>.tmp` directory containing every cloned skill, then renames once. All-or-nothing. |
| User runs `--force` on a target with uncommitted local edits, loses work | Low | Out of scope: `vskill clone --force` is documented as overwrite. We don't introspect git state of the target. |

## 10. ADRs to Reference

- **ADR 0688-02** (sidecar vs frontmatter for provenance) — this increment **extends** the sidecar pattern by adding `forkedFrom`/`originalSource`/`forkChain` to the same `.vskill-meta.json` file. No new ADR is needed for that decision; we are operating within its scope.
- **ADR 0809** (source-link sidecar `.vskill-source.json`) — referenced for the precedence behavior (source-link sidecars are never propagated via copy; resolver re-derives them at the destination). The clone command preserves this contract: `copyOwnSkillFiltered` already filters `.vskill-source.json` at copy time. No new behavior here.

**Possible follow-up ADR (NOT created in this increment)**: "Fork chain semantics — `forkedFrom` always immediate, `forkChain` always ancestry". Note as a follow-up if the implementation surfaces an ambiguity. Do **not** author it now; the rules are simple enough to live in `provenance-fork.ts` JSDoc and the `Provenance` type comment.

## 11. Domain Split for Implementation (team-lead spawn plan)

When `sw:do` runs and team-lead detects the appropriate domains, three agents are spawned:

| Agent | Tasks | Parallelism |
|---|---|---|
| **shared-types agent** | T-001 (types contract: `src/clone/types.ts` + `src/studio/types.ts` extension) | Runs first; backend + testing both wait on it |
| **backend agent** | T-002 → T-010 (skill-locator → reference-scanner → applyForkMetadata → provenance-fork → target-router → github-scaffold → clone orchestrator → CLI registration → whole-plugin path) | 9 tasks, fits under the 15-task per-agent cap |
| **testing agent** | T-011 → T-015 (unit tests for clone modules → unit tests for applyForkMetadata extension → integration tests covering 9 source×target combos → atomicity tests → github-scaffold + CLI smoke) | Runs in parallel with the backend agent once T-001 publishes the type contract |

**No frontend agent** is spawned — the studio UI is explicitly out of scope this increment.

**Closure protocol**: per the team-lead rule, agents do not run `/sw:done` themselves. The team-lead handles centralized closure (`code-review` → `simplify` → `grill` → `judge-llm`) once all three agents report green. Per the recent learning, team-lead must activate the master increment to "active" before spawning, and retry closure on transient failures (max 2) rather than silently skipping.

---

**Cross-checks performed against the codebase before writing this plan**:
- `src/installer/frontmatter.ts` — confirmed regex-based, exports `ensureFrontmatter`/`quoteYAMLValue`/`extractDescription` (no gray-matter dep). `applyForkMetadata` will be a sibling export, not a refactor.
- `src/studio/lib/scope-transfer.ts:101-119` — `copyOwnSkillFiltered` already filters `.vskill-meta.json` and `.vskill-source.json` at root. Suitable for direct reuse from `target-router`.
- `src/studio/lib/provenance.ts` — `writeProvenance`/`readProvenance` are best-effort and JSON-based. `provenance-fork` will read the source sidecar (if present), merge fork-chain logic, and write through `writeProvenance` unchanged.
- `src/shared/copy-plugin-filtered.ts` — `copyPluginFiltered` already handles plugin-shape directories with `commands/` and `skills/` flattening; suitable for whole-plugin clone path.
- `src/commands/add.ts:845-866` — `rollbackInstall` is the rollback shape we mirror: best-effort `rmSync` per location, swallow per-call errors so a partial filesystem state never suppresses the underlying diagnostic.
- `src/index.ts:22-99` — Commander registration template (`.command().option().action(async (a, opts) => { const { fn } = await import(...); await fn(a, opts); })`) is consistent across every command. The `clone` registration will follow the same shape.
