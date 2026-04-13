---
increment: 0625-external-tool-integration-rework
title: Rework External Tool Integration Architecture
generated: 2026-03-19T21:25:21.273Z
source: spec.md (auto-generated from ACs + project defaults)
version: "1.0"
status: evaluated
---

# Rubric: Rework External Tool Integration Architecture

> Auto-generated from spec.md acceptance criteria. Review and customize before implementation begins.
> All **[blocking]** criteria must pass before `sw:done` can close the increment.

---

## Functional Correctness

### R-001: Workspace config schema replaces legacy fields [blocking]
- **Source**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
- **Evaluator**: sw:grill
- **Verify**: `WorkspaceConfig` type exists with `name`, `rootRepo?`, `repos[]`; `WorkspaceRepo` has `id`, `path`, `prefix`, `sync?`; no `umbrella.enabled` or `multiProject.enabled` in type system; JSON schema rejects old keys
- **Threshold**: All 5 ACs pass
- **Result**: [x] PASS

### R-002: Config migration is complete and idempotent [blocking]
- **Source**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
- **Evaluator**: sw:grill
- **Verify**: `migrateToWorkspace()` maps umbrella → workspace, multiProject → workspace, projectMappings → sync; removes old keys; running twice produces identical output; version bumped to `"3.0"`
- **Threshold**: All 6 ACs pass; migration unit tests cover umbrella-only, multiProject-only, combined, idempotent, and corrupt scenarios
- **Result**: [x] PASS

### R-003: Multi-project detection uses workspace.repos [blocking]
- **Source**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
- **Evaluator**: sw:grill
- **Verify**: `detectMultiProjectMode()` checks `workspace.repos.length > 1`; `parseChildRepos()` reads `workspace.repos`; fallback folder scan preserved; `hasWorkspace` replaces `umbrellaEnabled`
- **Threshold**: All 4 ACs pass
- **Result**: [x] PASS

### R-004: Init flow writes workspace config [blocking]
- **Source**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
- **Evaluator**: sw:grill
- **Verify**: Fresh `specweave init` writes `workspace: { name, repos: [] }`; discovered repos populate `workspace.repos[]`; no `umbrella`/`multiProject` keys written; `buildWorkspaceConfig()` replaces `buildUmbrellaConfig()`
- **Threshold**: All 5 ACs pass
- **Result**: [x] PASS

### R-005: Sync-setup wizard maps repos to external tools [blocking]
- **Source**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05, AC-US5-06
- **Evaluator**: sw:grill
- **Verify**: Wizard lists all `workspace.repos[]` + rootRepo; "select all" shortcut works; mappings written to `workspace.repos[N].sync`; direction (import/export/bidirectional) captured; each mapping validated before save
- **Threshold**: All 6 ACs pass
- **Result**: [x] PASS

### R-006: Project field mandatory on all specs [blocking]
- **Source**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
- **Evaluator**: sw:grill
- **Verify**: `template-creator.ts` always emits `**Project**:`; PM and Architect skills require it unconditionally; `spec-validator` flags missing field as ERROR; single-project defaults to `workspace.name`
- **Threshold**: All 5 ACs pass
- **Result**: [x] PASS

### R-007: Import flow uses workspace repos and per-US project field [blocking]
- **Source**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04
- **Evaluator**: sw:grill
- **Verify**: `markdown-generator.ts` places `**Project**:` inside each US block; import coordinator resolves repos from `workspace.repos[]`; unmatched imports default to `workspace.name` with warning
- **Threshold**: All 4 ACs pass
- **Result**: [x] PASS

### R-008: External tool resolver reads workspace.repos[].sync [blocking]
- **Source**: AC-US8-01, AC-US8-02, AC-US8-03, AC-US8-04
- **Evaluator**: sw:grill
- **Verify**: `resolveForProject()` looks up `workspace.repos.find(r => r.id === projectId).sync`; rootRepo used when projectId matches workspace.name; fallback to `sync.defaultProfile`; zero references to `config.projectMappings`
- **Threshold**: All 4 ACs pass
- **Result**: [x] PASS

### R-009: Dashboard workspace page [blocking]
- **Source**: AC-US9-01 through AC-US9-07
- **Evaluator**: sw:grill
- **Verify**: `WorkspacePage.tsx` at `/workspace` route; table with repo id, name, GitHub/Jira/ADO mappings, sync status; rootRepo first with "Root" badge; inline editor on mapping cells; "Add Repo" button; sidebar nav link
- **Threshold**: All 7 ACs pass
- **Result**: [x] PASS

### R-010: Dashboard workspace REST API [blocking]
- **Source**: AC-US10-01 through AC-US10-06
- **Evaluator**: sw:grill
- **Verify**: GET/PATCH/POST/DELETE endpoints for `/api/workspace`; input validation returns 400; routes registered in `router.ts`
- **Threshold**: All 6 ACs pass
- **Result**: [x] PASS

### R-011: Backward compatibility — auto-migration on load [blocking]
- **Source**: AC-US11-01, AC-US11-02, AC-US11-03, AC-US11-04
- **Evaluator**: sw:grill
- **Verify**: `config-manager.ts` auto-migrates on load when version < 3.0; no dual-read fallback in business logic; one-time info log; corrupt config preserved untouched
- **Threshold**: All 4 ACs pass
- **Result**: [x] PASS

---

## Test Coverage

### R-012: Unit test coverage meets target [blocking]
- **Source**: project-default (coverageTarget: 90)
- **Evaluator**: sw:code-reviewer
- **Verify**: `npx vitest run --coverage` on changed files
- **Threshold**: >= 90% line coverage on new/modified files
- **Result**: [x] PASS

### R-013: Migration test scenarios comprehensive [blocking]
- **Source**: T-010
- **Evaluator**: sw:code-reviewer
- **Verify**: Test fixtures for: umbrella-only, multiProject-only, both-combined, already-migrated, corrupt config
- **Threshold**: 5 migration scenarios tested, all pass
- **Result**: [x] PASS

### R-014: Integration tests for detector + resolver [blocking]
- **Source**: T-020
- **Evaluator**: sw:code-reviewer
- **Verify**: Tests cover workspace-based detection, fallback paths, resolver lookup with workspace config
- **Threshold**: >= 95% coverage on `multi-project-detector.ts` and `external-tool-resolver.ts`
- **Result**: [x] PASS

---

## Code Quality

### R-015: No legacy dual-read paths remain [blocking]
- **Source**: AC-US11-02
- **Evaluator**: sw:code-reviewer
- **Verify**: Zero references to `config.umbrella` in business logic (migration code excluded); zero references to `config.multiProject`; zero references to `config.projectMappings` outside migration
- **Threshold**: `grep -r "config\.umbrella\|config\.multiProject\|config\.projectMappings" src/` returns 0 results (excluding migration files)
- **Result**: [x] PASS

### R-016: No critical/high code review findings [blocking]
- **Source**: project-default
- **Evaluator**: sw:code-reviewer
- **Verify**: `code-review-report.json` summary
- **Threshold**: critical: 0, high: 0, medium: 0
- **Result**: [x] PASS

---

## Security

### R-017: API input validation on all write endpoints [blocking]
- **Source**: AC-US10-05
- **Evaluator**: sw:grill (security category)
- **Verify**: POST/PATCH/DELETE endpoints validate input; duplicate repo IDs rejected (400); invalid sync structures rejected (400); no arbitrary config.json writes possible
- **Threshold**: All validation paths tested; no injection vectors
- **Result**: [x] PASS

---

## Performance

### R-018: Dashboard workspace page loads under 500ms [advisory]
- **Source**: Success Criteria (spec.md)
- **Evaluator**: sw:judge-llm
- **Verify**: `GET /api/workspace` response time with 20 repos
- **Threshold**: < 500ms p95
- **Result**: [x] PASS

---

## Documentation

### R-019: Configuration reference updated [blocking]
- **Source**: T-046, T-047, T-048
- **Evaluator**: sw:grill
- **Verify**: Every `WorkspaceConfig` field documented with type, required/optional, default, description, example; deprecated fields removed; migration note present
- **Threshold**: All workspace fields documented; zero references to `umbrella.enabled`/`multiProject.enabled` as active settings
- **Result**: [x] PASS

---

## Independent Evaluation

### R-020: Ship readiness [blocking]
- **Source**: sw:grill
- **Evaluator**: sw:grill
- **Verify**: `grill-report.json` → `shipReadiness`
- **Threshold**: `shipReadiness !== "NOT READY"` AND `summary.critical === 0`
- **Result**: [x] PASS

### R-021: LLM judge verdict [blocking]
- **Source**: sw:judge-llm
- **Evaluator**: sw:judge-llm
- **Verify**: `judge-llm-report.json` → `verdict`
- **Threshold**: `verdict !== "REJECTED"`
- **Result**: [x] PASS

---

## Summary

| Category | Criteria | Blocking | Passed | Status |
|----------|----------|----------|--------|--------|
| Functional Correctness | R-001 — R-011 | 11 | 11 | PASS |
| Test Coverage | R-012 — R-014 | 3 | 3 | PASS |
| Code Quality | R-015 — R-016 | 2 | 2 | PASS |
| Security | R-017 | 1 | 1 | PASS |
| Performance | R-018 | 0 | 1 | PASS |
| Documentation | R-019 | 1 | 1 | PASS |
| Independent Evaluation | R-020 — R-021 | 2 | 2 | PASS |
| **Total** | **21** | **20 blocking** | **21/21** | **PASS** |

**Verdict**: All 20 blocking criteria satisfied. Increment eligible for closure.
