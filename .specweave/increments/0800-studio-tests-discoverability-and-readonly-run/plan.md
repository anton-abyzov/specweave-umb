---
increment: 0800-studio-tests-discoverability-and-readonly-run
status: planned
---

# Plan — Studio Tests Discoverability + Read-only Run

## Architecture

All changes are React UI inside the vskill Studio bundle (`src/eval-ui/`). No backend, no API, no schema. The eval-runner endpoint already accepts requests for any skill regardless of origin ([api-routes.ts:2948](repositories/anton-abyzov/vskill/src/eval-server/api-routes.ts:2948)).

### Decision: split `isReadOnly` into `canEdit` and `canRun`

The current `isReadOnly = origin === "installed"` flag conflates two distinct capabilities:
- **canEdit**: Can the user mutate eval cases (add / edit / delete)? → `origin === "source"`
- **canRun**: Can the user execute eval cases? → always `true` if cases exist

`TestsPanel.tsx:651` currently gates the Run button on `!isReadOnly`, which is wrong — running tests is safe for any origin. Splitting the flag isolates the bug fix and keeps future intent obvious.

### Decision: 4-tab IA preserved (no 5th Tests tab)

Per 0792 Goals, IA stays at 4 tabs. Discoverability is solved with:
1. Overview chip ("N tests") → links to Run
2. Edit eval-cases section header gets a "Run all" CTA → deep-links to `?tab=run&mode=benchmark&autorun=1`
3. Run tab Benchmark mode is already the default sub-mode

### Decision: autorun via URL param, idempotent

`?autorun=1` triggers exactly one benchmark run on mount, then strips itself from the URL via `history.replaceState`. Idempotency guarded with `useRef` + dependency array — survives React StrictMode double-mount.

## File Targets

### Modify

| File | Change | ACs |
|------|--------|-----|
| `src/eval-ui/src/components/RightPanel.tsx` | Replace `isReadOnly` flag with `canEdit` (origin === "source") + `canRun` (always true). Pass both as context/props. Add autorun URL-param parsing. | AC-US1-04, AC-US2-01, AC-US2-02 |
| `src/eval-ui/src/components/TestsPanel.tsx` | Split gates: line 420 (Add Test Case) → `canEdit`; line 651 (per-case Run) → always show when cases exist; per-case Edit/Delete → `canEdit`. Add read-only banner. | AC-US2-01 to AC-US2-04 |
| `src/eval-ui/src/components/EditorPanel.tsx` | Add "Run all" button to `editor-eval-cases-section` header when `canEdit && cases.length > 0`. Hidden for installed skills. | AC-US1-02, AC-US1-03, AC-US1-05, AC-US2-06 |
| `src/eval-ui/src/components/OverviewPanel.tsx` (or wherever Overview content lives) | Add "N tests" chip when `evals.exists && cases.length > 0`; link to `?tab=run&mode=benchmark`. Visible for both source and installed. | AC-US1-01, AC-US1-06, AC-US2-07 |
| `src/eval-ui/src/components/RunDispatcherPanel.tsx` | Wire autorun: read URL `autorun=1`, dispatch `runAll("benchmark")` once after cases load via WorkspaceContext. Strip param from URL post-dispatch. | AC-US1-04 |

### Create

| File | Purpose |
|------|---------|
| `src/eval-ui/src/components/__tests__/0800-readonly-run.test.tsx` (vitest) | Unit tests for split flags, banner rendering, button visibility per origin |
| `src/eval-ui/src/components/__tests__/0800-autorun.test.tsx` (vitest) | Unit tests for autorun idempotency (StrictMode double-mount), URL stripping |
| `e2e/0800-tests-discoverability.spec.ts` (playwright) | E2E for: Edit "Run all" → Run tab → autorun executes; Overview chip → Run tab; installed-skill read-only Run path |

### Build / Release

| File | Change |
|------|--------|
| `repositories/anton-abyzov/vskill/package.json` | Bump patch version (current `1.0.x` → `1.0.(x+1)`) |
| `repositories/anton-abyzov/vskill/CHANGELOG.md` (if exists) | Add 0800 entry |

Bundle build sequence (must run before publish):
```bash
cd repositories/anton-abyzov/vskill/src/eval-ui && npm run build
cd ../.. && npm run build           # TypeScript compile
npm pack --dry-run                  # verify dist/ shipped
npm publish
```

## Component Diagram

```
RightPanel
├── canEdit: boolean         <-- origin === "source"
├── canRun:  boolean         <-- always true (when cases exist)
└── tabs[]
    ├── Overview  ----->  N-tests chip (US-001 + US-002)
    ├── Edit      ----->  EditorPanel
    │                       └── eval-cases <details>
    │                            └── TestsPanel embedded={true}
    │                                 └── "Run all" CTA (canEdit && cases.length > 0)
    ├── Run       ----->  RunDispatcherPanel
    │                       ├── reads ?autorun=1
    │                       └── Benchmark mode
    │                            └── TestsPanel embedded={false}
    │                                 ├── canRun  → Run buttons (always)
    │                                 ├── canEdit → Add/Edit/Delete (source only)
    │                                 └── !canEdit → read-only banner
    └── History   ----->  (unchanged)
```

## ADR References

No new ADRs required; this is a bug fix + discoverability tweak within an established IA (0792).
Relates to: 0563 (Tests panel), 0792 (IA redesign), 0784 (recent Studio detail work).

## Test Strategy

### TDD (per active warn mode + project convention)
- **RED**: Write failing vitest + playwright tests per AC before implementation.
- **GREEN**: Minimal change to pass each AC. No refactor in this phase.
- **REFACTOR**: Consolidate `canEdit`/`canRun` derivation into a single hook (e.g. `useSkillCapabilities()`) once tests pass.

### Coverage targets (from config.json)
- Unit: ≥60%
- Integration: ≥90%
- E2E: 100% of AC scenarios

## Release Strategy

After `/sw:done` closes the increment with all gates passing:

1. **Build artifacts**: `npm run build` in `src/eval-ui/` → produces `src/eval-ui/dist/`
2. **TypeScript compile**: `npm run build` at repo root
3. **Verify package contents**: `npm pack --dry-run | grep eval-ui/dist`
4. **Bump version**: `npm version patch --no-git-tag-version`
5. **Commit**: `0800: vskill <new-version> — studio tests discoverability + read-only run`
6. **Publish**: `npm publish` (npm registry is the canonical truth)
7. **Verify**: `npx vskill@<new-version> studio` and confirm new behavior in browser
8. **Push**: git push to origin

Memory pointer: `project_vskill_platform_deploy.md` notes that `npm run deploy` skips build for vskill-platform; that's not used here (this is the `vskill` CLI repo, not vskill-platform). Standard `npm run build && npm publish` applies.

## Open Questions (resolved)

- Should the Overview "N tests" chip show test count broken down by type (unit/integration)? → **NO** for v1; single count keeps signal clean.
- Should the read-only banner have a CTA button? → **NO** for v1; banner text mentions `vskill plugin new` which is enough.
