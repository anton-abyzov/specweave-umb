---
increment: 0749-studio-install-modal-short-skill-builder-ref
title: "Studio install modal: use short skill-builder ref"
generated: "2026-04-26"
source: auto-generated
version: "1.0"
status: evaluated
---

# Quality Contract — 0749

| ID | Criterion | Evaluator | Result |
|---|---|---|---|
| R-01 | AC-US1-01: InstallEngineModal renders `$ vskill install anton-abyzov/vskill/skill-builder` for the `vskill` engine (no `plugins/skills/skills` segment) | sw:grill | [x] PASS |
| R-02 | AC-US1-02: install-engine-routes spawns argv `["install", "anton-abyzov/vskill/skill-builder"]` for `engine: "vskill"` (display↔spawn parity) | sw:grill | [x] PASS |
| R-03 | AC-US1-03: A real install run via `vskill install anton-abyzov/vskill/skill-builder` (or via the Studio Run-install flow) succeeds end-to-end and produces skill-builder's `SKILL.md` on disk | manual | [x] PASS — live install reproduced during grill, SHA 13e597dae66c0c80836b0a6f2888e3dd0f33edb68340be161b885888854be2c3 |
| R-04 | AC-US1-04: Modal copy outside the command pre block is byte-identical to before (title, security note, buttons, success/failure stages) | sw:grill | [x] PASS |
| R-05 | AC-US2-01, AC-US2-02: Updated test assertions are in place pinning both the displayed string and the spawned argv to the short ref | sw:grill | [x] PASS |
| R-06 | AC-US2-03: TDD discipline followed — test edits (T-001, T-002) committed before source edits (T-003, T-004), with RED proven via failing run | sw:grill | [x] PASS |
| R-07 | Full vskill vitest suite green after all edits (no regression in other tests) | sw:grill | [x] PASS — 4392/4405 pass; 13 unrelated pre-existing failures in submit/update/SSE-real-wire (tracked by 0690), no regression from 0749 |
| R-08 | `grep -rn "anton-abyzov/vskill/plugins/skills/skills/skill-builder" src/ test/ e2e/` in the vskill repo returns 0 matches | sw:grill | [x] PASS |
| R-09 | No scope creep — only the 4 files listed in plan.md modified (no CLI changes, no marketplace.json edits, no platform repo touches) | sw:grill | [x] PASS |
