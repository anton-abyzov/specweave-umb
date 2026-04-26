---
increment: 0755-studio-search-discoverability-fixes
title: "Studio search discoverability: ranking + LIST filter + auto-reindex"
generated: "2026-04-26"
source: auto-generated
version: "1.0"
status: planned
---

# Quality Contract — 0755

| ID | Criterion | Evaluator | Result |
|---|---|---|---|
| R-01 | AC-US1-01: After deploy, `q=skill-builder&limit=30` includes `anton-abyzov/vskill/skill-builder` in returned results | manual + curl | [ ] pending |
| R-02 | AC-US1-02: Golden ranking test passes — T4 vendor outranks 30 T2 community competitors with same name token | sw:grill | [ ] pending |
| R-03 | AC-US1-03/04: Ranking change preserves exact-match #1 ranking and popularity-driven ranking for neutral queries | sw:grill | [ ] pending |
| R-04 | AC-US2-01..04: LIST endpoint honors `?author=`, `?source=`, `?q=`, and AND combinations | sw:grill + curl | [ ] pending |
| R-05 | AC-US2-05/06: Empty/missing filters are no-op; sanitization rejects out-of-charset inputs with 400 | sw:grill | [ ] pending |
| R-06 | AC-US3-01..03: Vendor publish writes `submission.isVendor = true`; idempotent; transaction-safe | sw:grill | [ ] pending |
| R-07 | AC-US4-01..02: Publish enqueues a non-blocking KV update (no await on the publish path) | sw:grill | [ ] pending |
| R-08 | AC-US4-03: Live test publish discoverable in `searchSkillsEdge` within 60s without admin rebuild | manual | [ ] pending |
| R-09 | AC-US4-04/05: Manual rebuild endpoint still works; queue/waitUntil failures log warnings, don't roll back publish | sw:grill | [ ] pending |
| R-10 | TDD discipline: each phase has RED-before-GREEN; all new tests pass; existing tests stay green | sw:grill | [ ] pending |
| R-11 | Per-phase deploy + smoke logs captured in `reports/phaseN-smoke.log` | manual | [ ] pending |
| R-12 | Lint + typecheck pass with no new errors attributable to 0755 | sw:grill | [ ] pending |
| R-13 | No scope creep: only files listed in plan.md modified; ranking re-architecture, search-engine swap, historical isVendor backfill, and `/find/...` page route are all deferred | sw:grill | [ ] pending |
