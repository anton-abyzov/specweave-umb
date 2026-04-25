# Implementation Plan: Fix skill version default + emission

## Overview

Three small, independent fixes in `repositories/anton-abyzov/vskill`:

1. Make `buildSkillMd` always emit `version:` (default `"1.0.0"`).
2. Make the `save-draft` route resolve a version before invoking the emitter.
3. Add a startup-time stale-dist detector to the eval-server so devs see a banner when their compiled bundle predates source changes.

No new abstractions. All helpers already exist in `src/utils/version.ts`. Two existing fixtures get a one-line update; existing roundtrip + spec-compliance tests anchor the regression net.

## Architecture

### Components touched

| Component | File | Change |
|---|---|---|
| Emitter | `src/eval-server/skill-create-routes.ts` (`buildSkillMd`, lines 239–244) | Replace conditional version emission with `data.version?.trim() || "1.0.0"` and remove obsolete comment |
| Save-draft route | `src/eval-server/skill-create-routes.ts` (lines 1259–1342) | Resolve version: prefer `body.version`, else preserve existing on-disk version, else default `"1.0.0"` |
| Eval-server bootstrap | `src/eval-server/eval-server.ts` (around line 148) | Add `checkDistFreshness(rootDir)` call before/after `Skill Studio:` banner |
| New helper | `src/eval-server/check-dist-freshness.ts` (NEW) | Compares newest mtime in `src/eval-server/` + `src/utils/` against `dist/eval-server/` + `dist/utils/`; returns `{ stale: boolean; details?: string }`; all errors swallowed |
| Fixtures | `src/eval-server/__tests__/fixtures/skill-emitter-{before,after}.md` | Add `version: "1.0.0"` line |

### Reused helpers (no duplication)

- `extractFrontmatterVersion` — `src/utils/version.ts:11`
- `bumpPatch` — `src/utils/version.ts:31` (used by create route, not save-draft)
- `setFrontmatterVersion` — `src/utils/version.ts:76` (already inserts when missing)
- `buildSkillMdForTest` — `src/eval-server/__tests__/helpers/skill-md-test-helpers.ts:9`

### Data flow

```
[Studio UI: AI-generate] → POST /api/skills/save-draft
                              │
                              ▼
                  resolveVersion(body, existingFile)
                              │  ← NEW
                              ▼
                  buildSkillMd({ ...body, version }) ──→ writeFileSync(SKILL.md)
                              │  (always emits version)  ← FIXED
                              ▼
[Studio UI: AI-edit] → POST /api/skills/:plugin/:skill/apply-improvement
                              │
                              ▼
                  setFrontmatterVersion(body.content, bumpPatch(prev))
                              │  (already correct in src; needs fresh dist)
                              ▼
                       writeFileSync(SKILL.md)

[Server boot] → eval-server.listen(port, () => {
                  checkDistFreshness(__rootDir__)  ← NEW
                  console.log("Skill Studio: http://...")
                })
```

## Test Strategy

**Strict TDD**: each AC gets a failing test first, then minimum-viable production code to flip it green.

### New test files

1. `src/eval-server/__tests__/skill-emitter-default-version.test.ts` — covers AC-US2-01, AC-US2-02
2. `src/eval-server/__tests__/skill-create-routes-save-draft.test.ts` — covers AC-US1-01, AC-US1-02, AC-US1-03
3. `src/eval-server/__tests__/check-dist-freshness.test.ts` — covers AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04

### Updated fixtures

- `src/eval-server/__tests__/fixtures/skill-emitter-before.md` — add `version: "1.0.0"`
- `src/eval-server/__tests__/fixtures/skill-emitter-after.md` — add `version: "1.0.0"`

### Regression anchors

- `skill-emitter-roundtrip.test.ts` — must still pass after fixture update (AC-US2-04)
- `skill-emitter-spec-compliance.test.ts` — must still pass; add an assertion line that every emitter output contains `version:`
- `skill-update-flow.test.ts` — must still assert `version: "1.0.0"` for create route (untouched logic, but verify path still passes)
- `skill-update-flow.e2e.test.ts` — must still assert version bump on apply-improvement

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Fixture update breaks unrelated golden-file assertions | Run roundtrip + spec-compliance suite after each fixture edit; rollback if ambiguous |
| `setFrontmatterVersion` already inserts version — does the buildSkillMd change duplicate it? | No — different code paths. `buildSkillMd` produces frontmatter from scratch (no SKILL.md exists yet). `setFrontmatterVersion` mutates an existing string. They never both run on the same content. |
| Stale-dist check pollutes production output (e.g. when installed via npm) | Check returns false-on-error and skips when `dist/` mtime is newer or doesn't exist; production installs ship dist newer than src |
| AC-US1-03 (preserve existing version on draft re-save) drifts from create-route's bump-on-update behaviour | Drafts are intentionally distinct from finalized skills — `mode: "update"` on `/api/skills/create` bumps; save-draft is overwrite-in-place during AI iteration. Different semantics, same emitter. |

## ADRs

No new ADRs needed. This is a defect fix that brings runtime behaviour in line with already-documented intent (see comments in `skill-create-routes.ts` and the existing `skill-update-flow` tests).
