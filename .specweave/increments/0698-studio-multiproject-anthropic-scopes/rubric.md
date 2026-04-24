---
increment: 0698-studio-multiproject-anthropic-scopes
title: "Skill Studio: multi-project + Anthropic-aligned scopes + plugin visibility (Available/Authoring)"
generated: "2026-04-24"
source: auto-generated
version: "1.0"
status: active
---

# Quality Rubric: 0698-studio-multiproject-anthropic-scopes

## Coverage Targets

| Layer | Framework | Target | Scope |
|---|---|---|---|
| Unit | Vitest 3 | ≥95% | `scope-migration.ts`, `standalone-skill-scanner.ts`, `plugin-scanner.ts`, `workspace-store.ts`, `api.ts` normalizer, `types.ts` |
| Integration (API) | Vitest + in-process HTTP | ≥90% | Workspace endpoints (`GET/POST/DELETE /api/workspace/*`) |
| UI Component | Vitest + @testing-library/react | ≥90% | `ProjectPicker`, `ProjectCommandPalette`, `GroupHeader`, `PluginGroup`, `Sidebar`, `StatusBar`, `StudioLayout` |
| E2E | Playwright | 100% of AC scenarios | All user-visible flows in T-017 |

## Acceptance Criteria Gate

All ACs from spec.md must be green before closure. Specifically:

| AC Block | Critical ACs | Zero-tolerance |
|---|---|---|
| US-001 (multi-project) | AC-US1-01 through AC-US1-07 | AC-US1-03 (switch invalidates cache), AC-US1-06 (stale path handling) |
| US-002 (sidebar layout) | AC-US2-01 through AC-US2-07 | AC-US2-07 (snapshot regression — CC vs non-CC agents) |
| US-003 (scope vocabulary) | AC-US3-01 through AC-US3-06 | AC-US3-04 (migration idempotent), AC-US3-05 (wire normalizer), AC-US3-06 (Enterprise fully removed) |
| US-004 (installed plugins) | AC-US4-01 through AC-US4-05 | AC-US4-02 (CC-only gate) |
| US-005 (authored plugins) | AC-US5-01 through AC-US5-05 | AC-US5-03 (CC-only gate), AC-US5-05 (node_modules excluded) |
| US-006 (standalone authoring) | AC-US6-01 through AC-US6-05 | AC-US6-02 (no double-counting with plugin scanner) |
| US-007 (shadowing) | AC-US7-01 through AC-US7-05 | AC-US7-04 (plugin skills never shadowed by non-plugin) |
| US-008 (statusbar) | AC-US8-01 through AC-US8-03 | AC-US8-03 (snapshot explicitly asserts absence, not incidental) |

## Performance Budgets

| Operation | Budget | Measured by |
|---|---|---|
| Project switch → sidebar repopulates | < 1 second | Playwright timing in T-017 |
| Plugin cache scan (cold) | < 50ms | Vitest perf test in T-004 |
| Plugin-source glob (typical repo) | < 100ms | Vitest perf test in T-005 |
| Sidebar render with 47+ skills | < 16ms | Existing react-virtuoso integration |
| Server per-request scanner aggregation | < 200ms | Integration test in T-012 |

## Code Review Priorities

### Critical (blocks closure)
- `workspace-store.ts`: atomic write (tmp+rename) must be verified; no partial-state possible
- `plugin-scanner.ts`: must gate on `agentId === "claude-code"` — returning skills for non-CC agents is a correctness bug
- `scope-migration.ts`: must be called synchronously before `createRoot()` in `main.tsx`; must be idempotent
- No occurrences of `"own"`, `"installed"`, `"global"`, `"enterprise"`, `"drafts"` in user-facing strings (strings.ts + component render output)
- `SkillScope` union in `types.ts` must have exactly 5 members — no more, no less

### High (blocks closure)
- Path traversal defense in `POST /api/workspace/projects`: `path` must be absolute, existsSync, isDirectory
- `scanAuthoredPluginSkills` glob excludes: `node_modules`, `.git`, `dist`, `build`, `.next`, `.turbo`, `.specweave/cache`
- `scanInstalledPluginSkills` must handle missing `~/.claude/plugins/cache/` gracefully (return `[]`)
- Corrupt `workspace.json` must NOT be deleted — server logs warning and returns empty workspace
- Plugin version dedup: only highest semver per `(marketplace, plugin)` pair emitted

### Medium (fix loop, max 3 iterations)
- `PluginGroup` reused for both AVAILABLE > Plugins and AUTHORING > Plugins — verify props don't bleed
- `useWorkspace` invalidates all three SWR keys on setActive: `"workspace"`, `"skills"`, `"agents"`
- `⌘P` preventDefault only when `document.activeElement` is inside Studio DOM subtree
- `showDirectoryPicker()` fallback implemented for Safari/Firefox (text input)
- Stale projects render muted + "Remove" visible in ProjectPicker popover

## Simplicity Checks (post-code-review)

- `workspace-store.ts` CRUD should have no duplicated read-modify-write logic — single helper for atomic save
- `plugin-scanner.ts` two exported functions share a CC-guard — extract to shared one-liner
- Color dot derivation (sha1 → oklch) should be a pure utility, not embedded in request handler
- Sidebar scope-to-section bucketing: one `groupBy(scope, s => s.group)` call, not multiple filter passes
- No inline `scope.split("-")[0]` calls in UI — always use the `group`/`source` fields from `SkillInfo`

## Grill Report Requirements

`grill-report.json` must be present and must not contain any CRITICAL or HIGH findings before `sw:done` runs. The following failure modes are pre-identified as grill targets:

1. Scanner returns skills for non-CC agents (grill: CC-gate bypass)
2. Migration runs AFTER `createRoot()` (grill: race condition)
3. `shadowedBy` set on AUTHORING rows (grill: spec violation)
4. `workspace.json` written non-atomically (grill: corruption risk)
5. Any route handler closes over `root` instead of reading from `workspaceStore.getActiveRoot()` per-request (grill: stale root bug)

## E2E Scenarios (all must pass before sw:done)

1. Add project → select → sidebar shows project skills
2. Switch between 2 projects → no cross-contamination in sidebar
3. ⌘P → fuzzy filter → Enter → active project switches + sidebar repopulates
4. Remove active project → empty state CTA shown
5. Agent=CC → AVAILABLE > Plugins + AUTHORING > Plugins visible
6. Agent=Cursor → Plugins sub-sections absent from both groups
7. Legacy localStorage keys → reload → keys migrated, state preserved
8. Fresh install (no `--root`) → "Add project" CTA → add → skills load
9. Stale project path → muted row in picker → not selectable → remove works
10. Shadow badge: same skill name in project + personal → project row shows `shadowed → personal` pill
