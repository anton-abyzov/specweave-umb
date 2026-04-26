# 0761 — Quality Rubric

Auto-generated at closure (2026-04-26). Each criterion maps to one or more ACs.

## US-001: Resolver source-tree probe

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| R-US1-01 | Source-tree skill resolves to repo's git remote | PASS | TC-05a passes — `<root>/skills/foo` + git remote → `acme/myrepo/foo` |
| R-US1-02 | No source-tree, no lockfile, no plugins → bare name | PASS | TC-05d asserts bare-name fallback |
| R-US1-03 | Source-tree beats lockfile | PASS | TC-05b — lockfile points at `anton-abyzov/greet-anton`, source-tree wins with `anton-abyzov/vskill/greet-anton` |
| R-US1-04 | Source-tree beats plugins/* walk | PASS | TC-05c asserts source-tree precedence over plugins-tree |
| R-US1-05 | Cache hit unchanged | PASS | TC-05f — second call hits cache (no second git shell-out) |

## US-002: VersionHistoryPanel tier label

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| R-US2-01 | formatTierLabel applied | PASS | tier-label.test.tsx — `CERTIFIED` renders as `Trusted Publisher` |
| R-US2-02 | Unknown tier passthrough | PASS | tier-label.test.tsx — `EXPERIMENTAL` renders raw |
| R-US2-03 | LOCAL badge unchanged | PASS | No diff to LOCAL-branch code path; only line 376 `{v.certTier}` → `{formatTierLabel(v.certTier)}` |
| R-US2-04 | CERT_COLORS unchanged | PASS | Diff shows CERT_COLORS map untouched |

## US-003: 503 retry

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| R-US3-01 | One-shot retry on 502/503/504 | PASS | api.test.ts — 'AC-US3-01: retries once on 502 and on 504' green |
| R-US3-02 | 4xx not retried | PASS | api.test.ts — 4xx returns `[]` with single fetch call |
| R-US3-03 | Thrown errors not retried | PASS | api.test.ts — first-call throw → `[]`, fetch called once |
| R-US3-04 | Applied to resolveInstalledSkillIds | PASS | api.ts diff — both `checkSkillUpdates` and `resolveInstalledSkillIds` use `fetchWith5xxRetry` |
| R-US3-05 | Success: no extra fetch | PASS | api.test.ts — happy path asserts `fetch` called exactly once |

## US-004: UpdateBell toast wording

| ID | Criterion | Status | Evidence |
|---|---|---|---|
| R-US4-01 | "Also installed under" when current agent in installLocations | PASS | smartclick.test TC-004 — toast contains "Also installed under" and NOT "switch to" |
| R-US4-02 | Legacy "switch to" wording when current agent NOT in installLocations | PASS | smartclick.test TC-005 — legacy wording preserved |
| R-US4-03 | Empty/undefined installLocations → no toast | PASS | UpdateBell.tsx — `if (installLocations.length > 0)` guards the toast call; existing UpdateBell tests cover empty path |
| R-US4-04 | Toast only fires when no sidebar match | PASS | UpdateBell.tsx — outer `if (!matched)` preserved from existing code |

## Gate Summary

| Gate | Result |
|---|---|
| Code review (severities) | PASS — 0 critical, 0 high, 0 medium, 2 low |
| Grill ship-readiness | READY |
| Judge-LLM | WAIVED (no externalModels consent) |
| Tasks completed | 16/16 |
| ACs checked in spec.md | 18/18 |
| Targeted vitest run | 64/64 green (54 in 0761 files + 10 in adjacent UpdateBell suites) |
