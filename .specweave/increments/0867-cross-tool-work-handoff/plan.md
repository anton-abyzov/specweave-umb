# Implementation Plan: Cross-Tool Work Handoff

> Architecture is **decided and codebase-verified** (every file:line below was confirmed against the live source on 2026-06-01). This plan does not re-architect; it enumerates the components, the verified reuse surface, the test strategy, and the risks so `/sw:do` (or `/sw:team-lead`) can execute against `spec.md`'s 8 user stories.

## Overview

Stop work in one AI coding tool (typically when out of subscription tokens) and resume in another — Claude Code → Codex / OpenCode / Gemini / Antigravity / Cursor — on **any** project. No tool can read another's session store (proprietary `.jsonl`, SQLite, or encrypted `.pb`), so the only portable thing is a **self-contained handoff document**. SpecWeave already holds every fact a resume needs (active increment, task/AC state, decisions, ambient rules) but never serializes it; non-SpecWeave projects have nothing.

The deliverable is one command (`/sw:handoff` in Claude Code, the installed `handoff` skill elsewhere) that writes a durable, secret-scrubbed doc + a full diff of uncommitted edits, prints absolute-path-first output + clickable link + copy-paste resume prompt, and works on any project. A PreCompact hook auto-writes one so a handoff survives a token crash.

## Approach

A three-part split by responsibility, mirroring the proven `verify` pattern (one deterministic engine → consumed by multiple thin surfaces). A core-only slash command can't run inside Codex/OpenCode; a vskill-only skill can't faithfully read `.specweave/` internals — so:

1. **Engine — `specweave handoff` CLI subcommand (specweave core).** Deterministic, increment-aware. Does all expensive assembly + secret scrub + free full-diff dump. The high-fidelity path when run in a SpecWeave workspace; also the graceful-degrade path for plain git projects.
2. **`/sw:handoff` — thin plugin command + skill (Claude Code + SpecWeave).** Shells to the CLI and surfaces its three outputs. No business logic of its own.
3. **vskill `handoff` skill — self-contained SKILL.md (template inlined).** Distributed by `emitSkill()` to the full agent registry (~54 targets incl. codex, opencode, cursor, gemini-cli, github-copilot, antigravity). It teaches the host agent to call `specweave handoff` **if on PATH**, else build a byte-compatible doc from `git` + a short interview using only shell. **No hard dependency on specweave being installed** (verified: not guaranteed on PATH; the emitter writes a single `SKILL.md` per target and copies NO sibling files, so the template must live inline in the body).

**Invariant across all three paths: the SAME doc format + the SAME paste-prompt.** A handoff written by Claude Code is continuable in Codex unchanged. This is enforced by a single rendering module (`handoff-doc-format.ts`) consumed by the CLI, the hook handler, and vitest; the vskill skill inlines a byte-compatible copy and a pin test guards against drift.

## Components

### specweave core — `repositories/anton-abyzov/specweave/`

| Module | Responsibility | Stories |
|---|---|---|
| `src/core/session/work-handoff.ts` *(new)* | `buildWorkHandoff(repoRoot, opts)` — the single builder. Detects workspace via `resolveEffectiveRoot()` + reading `.specweave/state/active-increment.json` (NOT a raw `.specweave/`-dir test — avoids the stale-child-repo bug). Handles `getActive(): string[]` cases **0 / 1 / 2+** (0 → git+config-only doc noting "no active increment"; 1 → use it; 2+ → require explicit `incrementId`, else error listing candidates). Reads metadata/spec/plan/tasks/config through the reused parsers; surfaces `acSyncEvents` drift; merges agent-supplied `--decision`s over `plan.md` decisions. | US-001, US-003, US-007 |
| `src/core/session/handoff-git-state.ts` *(new)* | Git capture: branch, short sha, `status --porcelain`, `diff --stat` for the inline doc section; **dumps full `git diff` concatenated with `git diff --cached` to a sibling `.diff` file** — the key in-flight-fidelity artifact, free (no tokens). Degrades gracefully when `git` is absent. | US-004 |
| `src/core/session/handoff-secret-scrub.ts` *(new)* | Regex redaction over **both** free-text fields and the captured diff for: `sk-`, `ghp_`, `gho_`, `ghs_`, `AKIA`, `ASIA`, `-----BEGIN`, `vsk_`, `xox[bap]-`, `Bearer `, `password=`, `api_key=`. Returns scrubbed text + per-pattern counts; replaces matches with `[REDACTED-<type>]`. | US-006 |
| `src/core/session/handoff-doc-format.ts` *(new)* | **Single source of truth** rendering the doc template + paste-prompt, including `--inline` self-contained mode (full scrubbed body between BEGIN/END markers). Emits the `Doc format v1` footer marker (ownership sentinel). Consumed by CLI, hook handler, vitest — so the format never drifts. | US-001, US-002, US-005, US-006 |
| `src/cli/commands/handoff.ts` *(new)* | `handoffCommand(opts)` — `specweave handoff [incrementId] [--reason --summary --next --gotcha --decision] [--inline\|--clipboard] [--non-specweave] [--out <path>] [--json]`. Mirrors the `createIncrementCommand(opts): Promise<void>` shape. **Output order: absolute path (plain text) FIRST → clickable markdown link → `.diff` path → fenced paste-prompt → per-tool "find your session" tips.** Wired into `bin/specweave.js` as a new commander `.command('handoff [incrementId]')` with lazy `import('../dist/src/cli/commands/handoff.js')`, exactly like `create-increment`. | US-001, US-005 |
| `src/core/hooks/handlers/pre-compact.ts` *(new)* + register in `hook-router.ts` | Implement the `pre-compact` handler (currently absent from the `HANDLERS` map → falls through to `getSafeDefault`, i.e. a no-op). On PreCompact, call `buildWorkHandoff` with whatever short fields the agent last stated (may be empty). Register `'pre-compact'` in `HANDLERS`; register a gated `'stop'`/`stop-handoff` variant that fires only under an `--auto`/handoff session flag (PreCompact always; Stop gated, to avoid noisy turn-end writes). | US-007 |
| `src/cli/helpers/init/gitignore-generator.ts` *(edit)* | Append `.handoff/` and `.specweave/state/handoff-latest.*` to `GITIGNORE_ENTRIES.specweave`. | US-006 |
| `src/core/session/handoff-context.ts` → `install-handoff-context.ts` *(rename, recommended)* | Kill the name collision. This file is orphaned plugin-INSTALL code (468 lines, zero git/increment logic, **zero importers** — verified). Do NOT graft onto it. | hygiene |

### specweave plugin — `plugins/specweave/` (in the specweave repo)

| File | Responsibility | Stories |
|---|---|---|
| `commands/handoff.md` *(new)* | Frontmatter (`description`, `argument-hint`) + workflow that runs `specweave handoff` and surfaces the 3 outputs. Mirrors `next.md` / `progress.md`. | US-001 |
| `skills/handoff/SKILL.md` *(new)* | Flat dir (invoked as `/sw:handoff` by directory name; namespace `sw/handoff`). Documents the workflow, the doc format, and the trigger phrases. | US-001 |
| `hooks/hooks.json` | **No structural change.** Verified: the `PreCompact` array already calls `specweave hook pre-compact`, and `Stop` already calls the `specweave hook stop-*` dispatchers. The behavior comes entirely from the new router handler. | US-007 (AC-US7-05) |

### vskill — `repositories/anton-abyzov/vskill/`

| File | Responsibility | Stories |
|---|---|---|
| `skills/handoff/SKILL.md` *(new)* | Self-contained cross-tool skill. **Template inlined in the body** (the emitter copies no sibling files). Recipe: try `specweave handoff`; else `git` capture + a short interview, then write `.handoff/HANDOFF.md` (+ self-created `.handoff/.gitignore`=`*`) + `.handoff/handoff.diff`, byte-compatible with the CLI output. `version: "1.0.0"`. Reserve slug `handoff` / `sw/handoff` without collision. | US-002 |

### docs — `repositories/anton-abyzov/specweave/docs/.../handoff.md`

| File | Responsibility | Stories |
|---|---|---|
| `docs/.../handoff.md` *(new)* | Living-doc page: the cross-tool matrix table (Tool \| session storage path \| find current session \| native resume cmd \| export/transferable) + the verified-skill.com SEO/marketing angle (lead card "Works in 8+ tools", the headline, the four moats, the long-tail keywords). | US-008 |

## Reuse (CRITICAL — verified, do NOT re-implement)

Every reference below was confirmed against the live source on 2026-06-01.

| Need | Reuse | File:line | Verified note |
|---|---|---|---|
| Tasks + AC links | `parseTasksWithUSLinks(tasksPath)` → `TasksByUserStory` | `src/generators/spec/task-parser.ts:93` | **Synchronous** (returns the map directly, not a Promise). `calculateProgressFromTasksFile` already `await`s it harmlessly. |
| Done/pending % | `calculateProgressFromTasksFile(tasksPath)` → `Promise<AggregateProgress>` | `src/progress/us-progress-tracker.ts:95` | Async wrapper around `parseTasksWithUSLinks` + `calculateAggregateProgress`. |
| Active increment(s) | `new ActiveIncrementManager(root).getActive()` → **`string[]`** | `src/core/increment/active-increment-manager.ts:59` | Reads `.specweave/state/active-increment.json`; back-compat single-`id` format; returns `[]` on any read/parse error (never throws). Also has `getPrimary()`. |
| Increment metadata + `acSyncEvents` | `MetadataManager.read(incrementId, rootDir?)` → `IncrementMetadata` | `src/core/increment/metadata-manager.ts:120` | Static method; lazy-creates default metadata if missing (so guard with `MetadataManager.exists()` first to avoid side-effecting reads). |
| Workspace root | `resolveEffectiveRoot(startDir?)` → abs path | `src/utils/find-project-root.ts:185` | Umbrella-aware; falls back to `process.cwd()`. (`getSpecweavePath()` at :207 wraps it for `.specweave/` paths.) |
| CLI command shape | `export async function createIncrementCommand(options): Promise<void>` | `src/cli/commands/create-increment.ts:44` | Pattern to copy: typed options object, throws on bad args, lazy-imported from `bin/specweave.js` via commander `.command().action()`. |
| Hook dispatch | `hookRouter(eventType, rawStdin)` + `HANDLERS` map | `src/core/hooks/handlers/hook-router.ts:17` | `HANDLERS` currently registers ONLY `user-prompt-submit` + `pre-tool-use`. **`pre-compact` is NOT registered** → unknown event → `getSafeDefault` no-op. Add `'pre-compact'` (+ gated stop variant) here. CLI entry is `handleHook` in `src/cli/commands/hook.ts:61`. |
| gitignore entries | `GITIGNORE_ENTRIES.specweave` (string array) | `src/cli/helpers/init/gitignore-generator.ts:417` | Append two entries to the existing `specweave:` array. |
| Skill → tool transpile | `emitSkill(generated, options)` | `vskill src/core/skill-emitter.ts:413` | Writes ONE `${agent.localSkillsDir}/${name}/SKILL.md` per target; copies NO sibling files (confirmed — references-dir handling is in the skill-builder doc only). Agent registry: `vskill src/agents/agents-registry.ts` (~54 ids incl. antigravity, opencode, codex, cursor, gemini-cli, github-copilot-ext). |

**`src/core/session/handoff-context.ts` is orphaned plugin-INSTALL code** — zero git/increment logic, zero importers (verified). Build the new modules fresh; do NOT graft onto it. Optionally rename it `install-handoff-context.ts` to kill the name collision with the new `work-handoff.ts`.

## Doc placement & behavior

- **SpecWeave:** `.specweave/increments/{id}/reports/handoff.md` (honors the increment-root-file rule) + stable copy `.specweave/state/handoff-latest.md` + `.specweave/state/handoff-latest.diff`. No active increment → `handoff-latest.md` only, noted.
- **Non-SpecWeave:** `.handoff/HANDOFF.md` + `.handoff/handoff.diff`; self-create `.handoff/.gitignore`=`*`. Ownership sentinel: refuse to overwrite a foreign root `./HANDOFF.md` lacking the `Doc format v1` marker → write to `.handoff/` instead.
- **Default: gitignored, NOT committed.** No `git add` hint printed. `--inline`/`--clipboard` embeds the full scrubbed doc body in the paste-prompt for cross-machine resume.
- **Cheap at token exhaustion:** the agent passes ~5 short strings as args; the CLI does all expensive work + the free diff dump.

## Test Strategy

TDD (RED → GREEN → REFACTOR) per `testing.defaultTestMode: TDD`. Vitest, ESM mocking with `vi.hoisted()` + `vi.mock()`. New test files under the specweave repo:

**`work-handoff.test.ts`** — exercises `buildWorkHandoff` against temp fixtures:
- SpecWeave, exactly **1** active increment → doc carries id/status/current+next task/AC counts/`acSyncEvents`/plan decisions/config ambient rules.
- SpecWeave, **0** active → git+config-only doc, "no active increment" noted.
- SpecWeave, **2+** active → requires explicit `incrementId`; absent → error listing candidate ids.
- **Non-SpecWeave** project → `.handoff/HANDOFF.md` + `.handoff/.gitignore`=`*`.
- **Uncommitted edits** → `.diff` captured (full `diff` + `diff --cached`), inline `status --porcelain` + `diff --stat`, uncommitted warning shown.
- **`acSyncEvents`** drift surfaced from `metadata.json`.
- **Secret scrub** redacts planted `sk-` / `ghp_` / `Bearer ` strings in both free-text and diff; per-pattern counts in the Redaction section; heuristic-not-a-guarantee note present.
- **Stale-orphan `.specweave/`** (dir present but no/empty `active-increment.json`) is correctly classified as non-SpecWeave (no increment reads).
- **Ownership sentinel** refuses a foreign root `./HANDOFF.md` lacking the `Doc format v1` marker → falls back to `.handoff/`.

**`cross-tool-commands.test.ts`** — build-time pin test asserting one resume command string + key path per tool so the matrix can't silently drift: Claude `claude -r <uuid>` + the **double-dash munge** rule, Codex `codex resume <uuid>`/`--last` (NO `--continue`), OpenCode `opencode -s <id>` / `--session`, Gemini `/chat resume <tag>`, Antigravity Agent Manager, Aider `aider --restore-chat-history`.

**Format-parity check** — a test asserting the CLI doc and the inlined vskill template render the same structure (the `handoff-doc-format.ts` single-source invariant).

**Manual / smoke gates** (per spec Success Criteria):
- From the umbrella repo, `specweave handoff` picks the right active increment (handling 2+), writes to `reports/`, scrubs a planted `sk-` key, dumps a real `.diff`, prints abs-path-first output + paste-prompt.
- In a non-git/non-specweave temp dir → `.handoff/` fallback + `.gitignore`.
- vskill emits the `handoff` skill, install into a Codex/OpenCode dir → SKILL.md is self-contained (no specweave dependency), inlined template renders.

## Risks

1. **vskill is not a runtime.** The emitted skill must be fully self-contained — template inlined, no shell-out *requirement* on specweave. Mitigation: `specweave handoff` is an optional accelerator only; the shell-only fallback path is the contract. Pin test + manual install smoke confirm self-containment.
2. **`specweave` not guaranteed on PATH** (verified). The skill must detect-and-degrade, never assume the binary. Mitigation: `command -v specweave` guard, identical to the pattern already used throughout `hooks.json`.
3. **PreCompact handler is currently a no-op.** `hooks.json` already dispatches `specweave hook pre-compact`, but `HANDLERS` has no `pre-compact` entry → safe-default pass-through. Mitigation: this increment writes + registers the real handler; format parity guaranteed by sharing `buildWorkHandoff`.
4. **Secret scrub is heuristic** (regex baseline only; gitleaks/trufflehog out of scope for v1). Mitigation: gitignored-by-default + an explicit "scrubbing is heuristic, an empty redaction list is not a clean guarantee, review before sharing" note in the doc.
5. **WIP / file count.** ~16 files across 2 repos + hooks + docs. Mitigation: execute via `/sw:team-lead` (3+ domains), keep modules small and single-responsibility, stay under the 1500-line/file limit.
6. **`MetadataManager.read` lazy-creates** default metadata on a missing file (side effect). Mitigation: guard reads with `MetadataManager.exists()` so a handoff never fabricates increment metadata.

## Release

- Ships across **three** artifacts: specweave **core** (new modules + CLI subcommand + hook handler + gitignore edit), specweave **plugin** (command + skill), and **vskill** (self-contained skill).
- New **specweave npm version** (the engine + CLI + plugin travel together in the package).
- vskill **skill version `1.0.0`** for the `handoff` skill.
- Per project convention: after `git push`, deploy/publish (specweave npm release; vskill skill publish via the emitter pipeline). Skill emitted to the full agent registry (~54 targets).

## Architecture Decision Record

A small ADR is warranted — the core design choice ("the portable handoff *document*, not any tool's transcript, is the cross-tool context boundary; engine in core + self-contained skill in vskill") is a durable, cross-cutting decision future contributors will need the rationale for. Written to:

`.specweave/docs/internal/architecture/adr/0867-01-portable-handoff-document-as-cross-tool-context-boundary.md`
