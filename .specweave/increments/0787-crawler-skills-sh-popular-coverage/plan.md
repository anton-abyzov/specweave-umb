---
increment: 0787-crawler-skills-sh-popular-coverage
title: "Fix skills.sh crawler popular-skills coverage"
---

# Implementation Plan: Fix skills.sh crawler popular-skills coverage

## Architecture

Two-layer fix that keeps the crawler module source-agnostic and reuses existing platform infrastructure:

1. **Crawler layer** (`crawl-worker/sources/skills-sh.js`): emits `skillPathCandidates: string[]` per submission. No new GitHub/HTTP fetching here — the crawler stays thin.
2. **Platform layer** (`src/app/api/v1/submissions/bulk/route.ts`): the existing Phase-2.5 SKILL.md verification (which already does claimed-path → root-SKILL.md fallback via `checkSkillMdExists` from `src/lib/scanner.ts`) is extended to walk an explicit candidate list when provided. Concurrency is already bounded at `PARALLEL_CHECKS = 10`.

Future crawlers (`skillsmp.js`, `sourcegraph.js`, etc.) inherit the multi-candidate fallback for free without per-source code changes.

## Files Modified

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill-platform/crawl-worker/sources/skills-sh.js` | `configStartPage` default 1→0; extract `fetchAndSubmitPage()`; add `candidateSkillPaths()` helper; emit `skillPathCandidates` per submission; backfill page 0 once on existing checkpoints |
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/bulk/route.ts` | Extend Phase-2.5 fallback list to walk `skillPathCandidates` when present (currently: claimed-path → root-SKILL.md only) |
| `repositories/anton-abyzov/vskill-platform/crawl-worker/server.js` | Add `GET /coverage` handler |
| `repositories/anton-abyzov/vskill-platform/crawl-worker/scheduler.js` | Expose `getSourceLastResult(sourceName)` helper |
| `repositories/anton-abyzov/vskill-platform/crawl-worker/__tests__/skills-sh.test.js` | Update default startPage assertion (1→0); add backfill test; add candidate-paths emission test |
| `repositories/anton-abyzov/vskill-platform/crawl-worker/README.md` | Document `/coverage` |

## Files Created

| File | Purpose |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/bulk/__tests__/route.test.ts` | Vitest unit test for multi-candidate Phase-2.5 fallback (only if not already present) |

## Design Decisions

### D1: Candidate-path list (not GitHub trees API)
- **Decision**: Compute candidates client-side in the crawler (`candidateSkillPaths(skillId)`), let the bulk route HEAD-check each one.
- **Why**: Reuses the existing unauthenticated `raw.githubusercontent.com` HEAD primitive in `checkSkillMdExists` — zero GitHub quota cost.
- **Trade-off**: If skills.sh ever adds an unknown convention, we extend `candidateSkillPaths`. The `/coverage` endpoint will detect this within hours.

### D2: Server-side fallback (not crawler-side)
- **Decision**: Resolve the path in `src/app/api/v1/submissions/bulk/route.ts`, not inside `skills-sh.js`.
- **Why**: Phase 2.5 already does fallback; extending the candidate list is a 10-line diff. Future sources inherit it for free.

### D3: Self-healing backfill via checkpoint flag (not standalone script)
- **Decision**: Detect `checkpoint && checkpoint.lastPage >= 1 && !checkpoint.backfilledPage0` and run page 0 once, then set `backfilledPage0: true`.
- **Why**: A standalone script needs separate auth/secret wiring on Hetzner VMs. Checkpoint-flag is self-healing; state file is system of record.

### D4: `/coverage` on crawl-worker server (not CF cron)
- **Decision**: Read from existing `sourceMetrics.get("skills-sh")` last-result `totalSkillsSh`.
- **Why**: skills.sh `total` is harvested every run; piggybacks on cached data.

### D5: Keep `node:test` for crawler tests
- **Decision**: Don't introduce vitest in `crawl-worker/`.
- **Why**: Crawler already uses `node:test` with in-process mock servers. Server-side tests use existing vitest setup in `src/`.

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Existing checkpoint resume logic regresses | Low | Update existing tests, don't replace |
| Phase-2.5 fallback fans out HEAD requests | Low | Existing `PARALLEL_CHECKS = 10` cap |
| skills.sh adds unknown 4th convention | Low | `/coverage` detects within 4h; one-line fix |
| Backfill duplicates submissions | None | InlineSubmitter + bulk endpoint dedup by repo+skill |

## Test Strategy

- **Unit (crawler, node:test)**: default startPage 0; backfill triggers once on `lastPage >= 1`; `candidateSkillPaths()` produces expected list for vendor-prefixed and plain skillIds; submission body includes `skillPathCandidates`.
- **Unit (server, vitest)**: bulk route walks `skillPathCandidates`, persists resolved path, falls back when absent.
- **Smoke (manual, post-deploy)**: curl prod bulk endpoint with vercel-prefixed payload; re-run audit Python script after one full crawl cycle.

## Rollout

1. Land code change (single PR, ~150 LOC net).
2. Deploy crawl-worker via existing `scanner-worker/deploy.sh`.
3. Deploy CF Worker route change via `wrangler deploy`.
4. Within 4 hours: re-run coverage check, confirm ≥48/50.
