# 0853 — Verify-runtime for vskill install + create

## Problem

Today the only proof that `vskill install <source>` worked is the shell exit code plus a chatty stdout banner. The only proof that `vskill skill new <prompt>` worked is "a file appeared." Neither is a machine-readable contract. As a result:

- Studio install-state badges (0850) and the CLI disagreed often enough that we shipped a separate `remove-skill` endpoint to clean up after partial installs.
- `sw:grill` and `sw:judge-llm` have no shared truth surface to assert against for these flows — every closure check re-reads ad-hoc files in different ways.
- Agents driving vskill via subagents can't tell a "fresh install ok" from "no-op, already installed" without parsing English output.

Anthropic's cwc-workshops `phase-3-verify` solved the same shape of problem for the React/UI world by emitting a stable contract surface (DOM `data-verify-*` attributes) and running a single runner against three audiences (CI, dashboard, agent). We are porting the pattern to a CLI surface.

## Thesis

> Verification is **runtime observation at the artifact surface**. Tests confirm code paths; verification confirms the deployed unit behaves and is self-describing.

For vskill, the "artifact surface" is not the DOM. It's:

- the filesystem (`~/.claude/skills/<name>/SKILL.md`, `./.claude/skills/...`)
- the lockfile (`.specweave/state/vskill.lock` or `~/.claude/vskill.lock`)
- the Claude Code settings (`enabledPlugins`)
- the emitted skill folder for `skill new` (SKILL.md + agent files + divergence report)

A **VerifiableUnit** for vskill is one CLI command. It declares:

- a Zod **schema** for the surface JSON it produces
- a set of **fixtures** (named reproducible inputs, with `act(ctx)` running the command)
- a set of **invariants** (predicates that must hold on the surface JSON after `act`)
- at least one **probe** fixture (adversarial — re-install, broken frontmatter, conflicting prompt, etc.)

A single **runner** executes a unit×fixture, runs every verifier, and emits one structured `VerifyResult` JSON: `{ verdict: PASS|FAIL|BLOCKED|SKIP, checks: [...], surface: {...}, durationMs, blockedReason? }`.

Three consumers read the same JSON:

1. **CLI** — `node scripts/run-verify.mjs` prints a verdict grid.
2. **CI (vitest)** — `matrix.test.ts` asserts every unit passes and every unit has at least one `probe: true` fixture.
3. **Agent** — `.specweave/state/verify-current.json` is the agent handle (the file replaces `window.__verify` since CLI has no window).

## Scope (this increment)

Two units. No more.

1. **U-INSTALL** — `vskill install <source>` against a known-good local plugin source.
2. **U-SKILL-NEW** — `vskill skill new <prompt>` with offline stub LLM (no API calls in CI).

Each unit ships with: 1 happy fixture + 1 probe fixture, ≥2 invariants, a Zod schema, the runner integration, and a CLI verdict line. That's the MVP. Dashboard HTML + Playwright replay recorder are explicitly **out of scope** here — they're called out in `## Future Increments` so they don't get smuggled in.

## User Stories

### US-001 — As a developer, I run one command to verify install + create still work end-to-end
**Acceptance Criteria**
- [x] AC-US1-01: `node scripts/run-verify.mjs` exits 0 and prints a one-line-per-unit verdict grid.
- [x] AC-US1-02: The same run writes `reports/verify-result.json` matching the documented schema in `scripts/verify-types.ts`.
- [x] AC-US1-03: Re-running the command twice in a row produces a byte-identical surface JSON for the happy fixtures (idempotency).

### US-002 — As CI, I can fail the build if a unit lacks a probe fixture
**Acceptance Criteria**
- [x] AC-US2-01: `matrix.test.mjs` asserts each registered unit has at least one fixture with `probe: true`. Build fails with a clear message if missing.
- [x] AC-US2-02: `matrix.test.mjs` asserts each unit has at least one declared invariant (not just a schema). Build warns (not fails) otherwise.

### US-003 — As an agent / `sw:grill`, I can read the latest verdict without re-running
**Acceptance Criteria**
- [x] AC-US3-01: After any verify run, `.specweave/state/verify-current.json` contains `{ version: "1.0", manifest: [...], current: <result-of-last-runAll> }`.
- [x] AC-US3-02: The file is rewritten atomically (tmp + rename) so an agent reading concurrently sees either the old or the new full result, never a half-written file.

### US-004 — As a probe author, the runner catches lies — not just confirms truths
**Acceptance Criteria**
- [x] AC-US4-01: A deliberately wrong invariant on a probe fixture produces verdict `FAIL` and prints the check name + actual vs expected.
- [x] AC-US4-02: A unit whose `act()` throws produces verdict `BLOCKED` (not FAIL) with the stack in `blockedReason`.

## Out of Scope (explicit)

- HTML dashboard at `/verify` (Anthropic ships one; we don't need it to prove the pattern).
- Playwright replay recorder.
- Promoting harness into `vskill verify` subcommand (separate increment).
- Replacing existing `sw:grill` / `sw:judge-llm` consumers (separate increment — prove the surface first).
- Wiring `verified-skill.com` API into the harness (network coupling).

## Future Increments

- 0854 — Promote harness into `vskill verify` subcommand once JSON shape stabilizes.
- 0855 — HTML dashboard + Playwright replay recorder for Skill Studio.
- 0856 — Refactor `sw:grill` to ingest `verify-current.json` instead of re-reading source files.

## References

- Upstream workshop: https://github.com/anthropics/cwc-workshops/tree/main/how-we-claude-code/phase-3-verify
- "How we Claude Code" video (Ara, Anthropic): https://www.youtube.com/watch?v=IlqJqcl8ONE — verify phase ~12:55, planted-bug demo ~26:00, recording ritual ~28:00.
- Local artifacts: `reports/verify-result.json`, `reports/run-log.md`
