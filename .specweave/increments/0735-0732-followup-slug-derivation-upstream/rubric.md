---
increment: 0735-0732-followup-slug-derivation-upstream
title: "0732 follow-up: outbox-time slug derivation + name shape validation"
generated: "2026-04-26"
source: spec-derived
version: "1.0"
status: active
---

# Quality Contract — Increment 0735

## Closure gates

| Gate | Threshold |
|------|-----------|
| Code review (`sw:code-reviewer`) | 0 critical, 0 high, ≤2 medium remaining |
| Simplify | No critical duplication / readability findings |
| Grill (`sw:grill`) | PASS — 0 critical findings; high findings tracked as follow-up |
| Judge-llm | Approve OR waived |
| PM gates | tasks_complete + acs_satisfied + tests_pass |
| Tests (vitest) | 0 failures across `src/lib/skill-update` + `src/app/api/v1/internal/skills/publish` from vskill-platform; existing slug E2E (vskill repo) green |

## Task gate

- All 10 tasks `[x]` — TDD strict (every impl preceded by RED test).
- All 5 ACs (AC-US1-01..05) `[x]`.

## Test gates

- ≥6 net new test cases vs 0732 baseline (skill-name 6 + outbox-writer 2 + publish-route 1 minimum).
- Existing real-SSE slug E2E in vskill repo unchanged + green.

## Spec gates

- spec.md Out-of-Scope reviewed — backfilling stale outbox rows + write-time name validation explicitly out.
- ADR-0735-01 + ADR-0735-02 captured in plan.md.

## Performance gate

- Publish endpoint hot path: ZERO DB queries (down from one per event). Verified by grep `db.skill.findUnique` in `route.ts` returning zero matches post-change.

## Privacy gate

- Warn log on malformed-name path emits `{ segments, length }` only — verified by inspecting the warn-call args. Raw name MUST NOT appear in any log line emitted by outbox-writer's slug-skip branch.

## Closure-blocking severities

`critical, high` — medium and below are tracked as follow-up findings and do not block closure.
