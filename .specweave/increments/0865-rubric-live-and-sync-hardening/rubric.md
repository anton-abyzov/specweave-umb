---
increment: 0865-rubric-live-and-sync-hardening
title: Rubric for 0865-rubric-live-and-sync-hardening
generated: 2026-06-01T06:44:19.870Z
source: spec.md (auto-generated from ACs, then refined with real probes)
version: "1.0"
status: active
---

# Rubric: 0865-rubric-live-and-sync-hardening

> Auto-generated from spec.md ACs by `generateRubricFile`, then refined with executable `command` probes.
> US-001 (rubric engine) criteria are **[blocking]** and proven by deterministic probes.
> US-002 (sync hardening) criteria ship **[advisory]** this cycle (advisory-then-promote rollout).
> `command` Verify probes run from the project root; exit 0 = pass, non-zero/timeout = fail (never skip).
> All **[blocking]** criteria must pass before `sw:done` can close the increment.

---

## US-001 — Rubric engine is live and AC-gating

### R-US1-01: Non-template rubric.md generated at the increment root [blocking]
- **Source**: AC-US1-01
- **Evaluator**: command
- **Verify**: `test -f .specweave/increments/0865-rubric-live-and-sync-hardening/rubric.md && ! grep -q "^status: template" .specweave/increments/0865-rubric-live-and-sync-hardening/rubric.md && grep -q "R-US1-01" .specweave/increments/0865-rubric-live-and-sync-hardening/rubric.md`
- **Threshold**: exit 0 (root rubric.md exists, is not a template, has AC-tied criteria)
- **Result**: [ ] PENDING

### R-US1-02: Generator↔parser parity (criteria == ACs + 4 defaults) [blocking]
- **Source**: AC-US1-02
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && npx vitest run src/core/rubric/rubric-generator-parity.test.ts`
- **Threshold**: exit 0
- **Result**: [ ] PENDING

### R-US1-03: `command` evaluator returns pass/fail, never skip [blocking]
- **Source**: AC-US1-03
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && npx vitest run src/core/rubric/rubric-evaluator-command.test.ts`
- **Threshold**: exit 0
- **Result**: [ ] PENDING

### R-US1-04: A failed blocking command-criterion blocks closure [blocking]
- **Source**: AC-US1-04
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && npx vitest run src/core/increment/completion-validator-rubric.test.ts`
- **Threshold**: exit 0
- **Result**: [ ] PENDING

### R-US1-05: Legacy rubrics deleted; scaffolder writes no placeholder [blocking]
- **Source**: AC-US1-05
- **Evaluator**: command
- **Verify**: `[ "$(find .specweave/increments -maxdepth 2 -name rubric.md | wc -l | tr -d ' ')" = "1" ] && cd repositories/anton-abyzov/specweave && npx vitest run src/core/increment/template-creator-rubric.test.ts`
- **Threshold**: exit 0 (only 0865's rubric.md remains AND scaffolder test green)
- **Result**: [ ] PENDING

---

## US-002 — External-sync flow hardened (advisory this cycle)

### R-US2-01: No `config.umbrella` reads remain in src/sync routing [advisory]
- **Source**: AC-US2-01
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && ! grep -rn "config\.umbrella" src/sync`
- **Threshold**: exit 0 (zero matches)
- **Result**: [ ] PENDING

### R-US2-02: sync-health and ADO runtime share one credential resolver [advisory]
- **Source**: AC-US2-02
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && grep -q "resolveAdoPat\|ADO_PAT_ALIASES" src/cli/commands/sync-health.ts && grep -q "resolveAdoPat" src/integrations/ado/ado-pat-provider.ts`
- **Threshold**: exit 0
- **Result**: [ ] PENDING

### R-US2-03: ADO runtime accepts AZURE_DEVOPS_PAT / AZURE_DEVOPS_TOKEN / ADO_PAT [advisory]
- **Source**: AC-US2-03
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && npx vitest run src/integrations/ado/credential-resolver.test.ts`
- **Threshold**: exit 0
- **Result**: [ ] PENDING

### R-US2-04: Terminal write failure enqueues into SyncRetryQueue [advisory]
- **Source**: AC-US2-04
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && npx vitest run src/sync/sync-coordinator-resilience.test.ts`
- **Threshold**: exit 0
- **Result**: [ ] PENDING

### R-US2-05: Deprecated github-sync skill reconciled (no phantom command) [advisory]
- **Source**: AC-US2-05
- **Evaluator**: command
- **Verify**: `cd repositories/anton-abyzov/specweave && grep -q "sw-github:push" plugins/specweave/skills/github-sync/SKILL.md && ! grep -rq "sw-github:sync-spec" plugins/specweave/skills/github-sync/evals/`
- **Threshold**: exit 0 (skill points at the live command; evals carry no phantom command)
- **Result**: [ ] PENDING

### R-US2-06: Increment ships a real AC-tied rubric evaluated at closure [advisory]
- **Source**: AC-US2-06
- **Evaluator**: sw:grill
- **Verify**: grill confirms rubric.md mixes `command` + `sw:grill` + `sw:code-reviewer` evaluators tied to ACs, and closure evaluates them (not only R-D01..R-D04 defaults)
- **Threshold**: acCompliance for AC-US2-06 == pass
- **Result**: [x] PASS — grill 2026-06-01: rubric.md mixes command + sw:grill + sw:code-reviewer evaluators tied to ACs; completion-validator.ts:223-261 evaluates them (no fallback to R-D01..R-D04 defaults). acCompliance AC-US2-06 == pass.

### R-US2-07: No secret/PAT values in any output [advisory]
- **Source**: AC-US2-07
- **Evaluator**: sw:code-reviewer
- **Verify**: code-review-report.json — no secret values; credential-masker remains the last write barrier (blocking coverage provided by R-D02)
- **Threshold**: 0 critical, 0 high
- **Result**: [x] PASS — code-review 2026-06-01: 0 critical, 0 high. No PAT/secret values logged or leaked (F-006).

---

## Test Coverage

### R-D01: Unit test coverage meets target [advisory]
- **Source**: project-default
- **Evaluator**: coverage
- **Verify**: Coverage output on new/modified files (authoritative gate: completion-validator validateCoverage)
- **Threshold**: >= 90% line coverage
- **Result**: [ ] PENDING (advisory — coverage hard-gated by validateCoverage; the `coverage` rubric evaluator is not automated and resolves to skip, so it must not block)

---

## Code Quality

### R-D02: No critical, high, or medium code review findings [blocking]
- **Source**: project-default
- **Evaluator**: sw:code-reviewer
- **Verify**: code-review-report.json summary
- **Threshold**: critical === 0 AND high === 0 AND medium === 0
- **Result**: [x] PASS — code-review 2026-06-01 (iteration 2): 0 critical, 0 high, 0 medium. F-001 resolved: spec.md (Locked Decision 1, AC-US1-03, FR-002) and plan.md (A2, ADR, risk row) no longer claim network isolation — they state credential-stripped env + bounded timeout with the committed/reviewed rubric as the trust boundary, and OS-level network isolation as a documented (intentionally-deferred) follow-up. Implementation matches: rubric-evaluator.ts strips credential env vars + applies a bounded timeout, with no network-isolation primitive.

---

## Independent Evaluation

### R-D03: Ship readiness verified [blocking]
- **Source**: project-default
- **Evaluator**: sw:grill
- **Verify**: grill-report.json shipReadiness
- **Threshold**: shipReadiness !== "NOT READY"
- **Result**: [x] PASS — grill 2026-06-01: shipReadiness = READY (0 critical, 0 high; 12/12 ACs pass on independent verification; tsc clean; 30 targeted + 1478 sync-suite tests green; all command probes executed PASS).

### R-D04: LLM judge verdict acceptable [blocking]
- **Source**: project-default
- **Evaluator**: sw:judge-llm
- **Verify**: judge-llm-report.json verdict
- **Threshold**: verdict !== "REJECTED"
- **Result**: [x] PASS — judge-llm 2026-06-01 (in-session ultrathink, no external API cost): verdict APPROVED (score 90). Correct, well-tested, honestly documented; arbitrary-shell command evaluator is a documented product decision, not a defect.
