# 0381 — Implementation Plan

## Approach

Fix from the outside in: discovery sources first (stop generating bad candidates), then route-level defense (catch anything that slips through), then restrict the internal fallback.

## Phase 1: Discovery Source Verification

Add GraphQL batch SKILL.md verification to `discoverFromRepoSearch` and `discoverFromNpm`. Follow the existing pattern from `github-events.js` (buildGraphQLQuery with `object(expression: "HEAD:SKILL.md")`). Process repos in batches of 50 (GraphQL alias limit) before returning candidates.

## Phase 2: Route-Level Defense-in-Depth

Add parallel `checkSkillMdExists` validation to the batch submission path in the submissions route. This catches any future discovery source that forgets to validate.

## Phase 3: Internal Fallback Fix

Restrict the body-params fallback (route.ts:481) to only apply for non-internal requests. Internal requests that find nothing should return gracefully with an empty submissions array.

## Phase 4: Tests

Add tests for each fix: discovery verification, batch route validation, and fallback restriction.

## Key Decisions

1. **GraphQL over REST for discovery verification**: Matches existing crawl-worker pattern, batches efficiently (1 API call per 50 repos vs 50 individual HEAD requests).
2. **Defense-in-depth in route**: Even though discovery should filter, the route should never trust unverified paths — fail-safe over fail-fast.
3. **No breaking changes**: Discovery functions keep the same return signature. Route behavior is stricter but compatible (fewer submissions created, not more).
