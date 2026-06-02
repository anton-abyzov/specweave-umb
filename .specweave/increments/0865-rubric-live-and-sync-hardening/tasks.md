# Tasks: Rubric-Live + Sync-Hardening

Test mode: **TDD** (RED → GREEN → REFACTOR). Coverage target 90%.
All paths relative to `repositories/anton-abyzov/specweave/`.
Model: Opus 4.8 default.

## Task Notation
- `[ ]` not started · `[x]` complete · `[P]` parallelizable
- Each task lists **AC**, **Test Plan** (Given/When/Then), **Status**.

---

## Phase A — Rubric engine goes live (US-001)

### T-001: Add `command` evaluator type to the rubric evaluator
**AC**: AC-US1-03 | **Status**: [x] complete
**Description**: Extend the evaluator dispatch (`src/core/rubric/rubric-evaluator.ts:125-145`) with a `command` case that runs the criterion `Verify` probe via `child_process` (cwd = repo root, bounded timeout default 60s, credential env vars stripped, no token injection). Map exit 0 → `pass`, non-zero/timeout → `fail`; capture truncated stdout/stderr as `evidence`. Never return `skip` for a `command` criterion.
**Test Plan**:
- File: `src/core/rubric/rubric-evaluator-command.test.ts`
- **TC-001** Given a criterion whose Verify is `exit 0` · When evaluated · Then status === `"pass"`.
- **TC-002** Given a criterion whose Verify is `exit 1` · When evaluated · Then status === `"fail"` and evidence is captured.
- **TC-003** Given a Verify that sleeps past the timeout · When evaluated · Then status === `"fail"` (timeout), never `"skip"`.
- **TC-004** Given a `command` criterion · When evaluated · Then status is never `"skip"` for any exit path.

### T-002: Wire `generateRubricFile` into planning + add `generate-rubric` CLI
**AC**: AC-US1-01, AC-US1-02 | **Status**: [x] complete
**Description**: Invoke `generateRubricFile` (`rubric-generator.ts:146`) after `spec.md` has ACs (end-of-planning / `tasks.md` write hook), writing to the increment **ROOT** `rubric.md`. Add CLI `specweave generate-rubric <id> [--refresh]` in `src/cli/commands/` — idempotent (no clobber of a non-template rubric) unless `--refresh`. Generator emits one `### R-USx-yy … [blocking]` block per AC + the 4 inherited defaults.
**Test Plan**:
- File: `src/core/rubric/rubric-generator-parity.test.ts`
- **TC-005** Given a fixture spec.md with N ACs · When `generateRubricFile` runs · Then root `rubric.md` exists, is NOT a template, and has exactly `N + 4` criteria (parity; fails on drift).
- **TC-006** Given an existing non-template rubric · When `generate-rubric` without `--refresh` · Then it is not clobbered; with `--refresh` · Then regenerated from current ACs.

### T-003: Closure gating for blocking vs advisory criteria
**AC**: AC-US1-04 | **Status**: [x] complete
**Description**: Confirm/extend `completion-validator.ts` so a failed **blocking** criterion (any evaluator incl. `command`) is pushed into the closure error gate, and a failed **advisory** criterion is reported but does not block.
**Test Plan**:
- File: `src/core/increment/completion-validator-rubric.test.ts`
- **TC-007** Given a rubric with a failing blocking `command` criterion · When closure validates · Then closure is blocked with that criterion in the error gate.
- **TC-008** Given a rubric with a failing **advisory** criterion only · When closure validates · Then closure is NOT blocked (criterion reported).

### T-004: Delete legacy rubrics + stop scaffolding the placeholder
**AC**: AC-US1-05 | **Status**: [x] complete (scaffolder no longer writes reports/rubric.md placeholder, TC-009 green; 144 legacy per-increment rubric.md deleted, only 0865's remains)
**Description**: Delete the 143 existing `.specweave/increments/*/rubric.md` legacy template/unparseable files (umbrella root). Update `template-creator.ts:357-377` to stop writing the `reports/rubric.md` placeholder; the root `rubric.md` is produced post-planning by T-002.
**Test Plan**:
- File: `src/core/increment/template-creator.test.ts`
- **TC-009** Given a fresh increment scaffold · When created · Then no `reports/rubric.md` placeholder is written.
- **TC-010** Given the umbrella increments dir after migration · When listed · Then no legacy template/unparseable `rubric.md` remains (verified by the migration script's dry-run report).

---

## Phase B — Sync hardening (US-002, proving ground)

### T-005: Remove `config.umbrella` reads from the routing path
**AC**: AC-US2-01 | **Status**: [x] complete
**Description**: Rewrite `src/sync/sync-target-resolver.ts`, `src/sync/story-router.ts`, and `src/cli/commands/sync-progress.ts` to read `config.workspace.repos[]` (via `external-tool-resolver.ts`) only; delete every `config.umbrella` read in `src/sync`.
**Test Plan**:
- File: `src/sync/sync-target-resolver.test.ts`
- **TC-011** Given a config with `workspace.repos[]` and no `umbrella` · When a story with `Project: specweave` resolves · Then it routes to the specweave repo target (not the global fallback).
- **TC-012** Given `grep -rn "config\.umbrella" src/sync` · When run · Then zero matches (command-criterion in the rubric, advisory).

### T-006: Single `CredentialResolver` with aligned ADO aliases
**AC**: AC-US2-02, AC-US2-03 | **Status**: [x] complete
**Description**: Extract one `CredentialResolver` imported by both `src/cli/commands/sync-health.ts` and `src/integrations/ado/ado-pat-provider.ts` (+ Jira/GitHub), with a canonical alias table. ADO runtime accepts `AZURE_DEVOPS_PAT`, `AZURE_DEVOPS_TOKEN`, `ADO_PAT`. Values via `sync-setup`/Obsidian; never logged.
**Test Plan**:
- File: `src/integrations/ado/credential-resolver.test.ts`
- **TC-013** Given only `AZURE_DEVOPS_TOKEN` set · When the ADO runtime resolves the PAT · Then it succeeds (alias accepted).
- **TC-014** Given only `ADO_PAT` set · When resolved · Then it succeeds.
- **TC-015** Given a resolved credential · When logged/serialized · Then the value is masked (no secret in output).

### T-007: Wire retry/enqueue into live external-write path
**AC**: AC-US2-04 | **Status**: [x] complete
**Description**: Wrap `ProviderAdapter` external writes in a retry-wrapper (bounded backoff); on terminal failure auto-enqueue into `SyncRetryQueue` so `sync-retry` drains it. Collapse duplicate circuit breakers to one persistent breaker.
**Test Plan**:
- File: `src/sync/sync-coordinator-resilience.test.ts`
- **TC-016** Given a provider write that returns a terminal 5xx during closure · When the coordinator runs · Then a job is enqueued into `SyncRetryQueue`.
- **TC-017** Given a populated `SyncRetryQueue` · When `sync-retry` runs · Then the job is drained/attempted.
- **TC-018** Given a transient 429 then success · When wrapped · Then it retries with backoff and ultimately succeeds without enqueue.

### T-008: Remove/reconcile the deprecated `github-sync` skill
**AC**: AC-US2-05 | **Status**: [x] complete
**Description**: Remove `plugins/specweave/skills/github-sync/SKILL.md` or reconcile it with the live increment-based github command so guidance is not contradictory.
**Test Plan**:
- **TC-019** Given the plugins skills tree · When checked · Then either `github-sync` is absent or its SKILL.md no longer contains contradictory DEPRECATED guidance (command-criterion).

---

## Phase C — Dogfood + model default

### T-009: Ship this increment's real rubric.md and prove evaluation
**AC**: AC-US2-06 | **Status**: [x] complete (generated via live `generate-rubric`, refined to command+grill+code-reviewer evaluators; probes verified PASS)
**Description**: Generate (via the now-live generator) this increment's root `rubric.md` with AC-tied criteria: `command` criteria for the grep/test invariants (US-002 sync criteria **advisory** per rollout; US-001 engine criteria **blocking**), `sw:grill`/`sw:code-reviewer` criteria for semantics. Confirm `/sw:done` evaluates them (no fallback to the 4 defaults).
**Test Plan**:
- **TC-020** Given closure runs on 0865 · When rubric evaluates · Then the report shows AC-tied criteria (R-US1-*/R-US2-*), not only R-D01..R-D04.

### T-010: Set Opus 4.8 default model
**AC**: AC-US1-01 (supporting) | **Status**: [x] complete (`opus` alias → `claude-opus-4-8` in MODEL_ALIASES single source of truth + bedrock alias + pricing; sw-planner stays sonnet; verified in built dist)
**Description**: Set Opus 4.8 as default model in `.specweave/config.json` / config schema; keep `sw-planner` agent frontmatter on Sonnet.
**Test Plan**:
- **TC-021** Given config · When read · Then default model resolves to `claude-opus-4-8`; sw-planner frontmatter remains sonnet.

### T-011: Secret-safety review
**AC**: AC-US2-07 | **Status**: [x] complete (code-review iteration 2: 0 critical/high/medium; F-006 confirmed no PAT/secret leakage; credential-masker is the last write barrier)
**Description**: Ensure no secret/PAT values appear in logs, `config.json`, specs, or reports. Verified by the code-review gate (zero critical/high) and a redaction pass.
**Test Plan**:
- **TC-022** Given all increment outputs · When scanned for token-like patterns · Then zero secret values present; code-review reports 0 critical/0 high.

---

## Phase D — Verify

- [x] [T-050] Run `npx vitest run` (all new unit/integration tests green — 46 targeted + 1905 sync-suite)
- [x] [T-051] Run the increment's own rubric `command` probes — all green (R-US1-01..05, R-US2-01/02/05 PASS; vitest probes PASS)
- [x] [T-052] Verify every AC is satisfied and `rubric.md` evaluates live at closure (grill re-executed probes; code-review + grill both PASS)
