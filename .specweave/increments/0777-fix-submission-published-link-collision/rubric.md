---
increment: 0777-fix-submission-published-link-collision
title: "Fix submission published-skill link collision"
generated: "2026-04-26"
source: spec.md + plan.md
version: "1.0"
status: active
---

# Quality Contract

## Functional correctness

- For every published submission with `submission.skillId` set, the "View published skill" link href on `/submit/[id]` is the canonical 3-segment `/skills/<owner>/<repo>/<skill>` URL — never the legacy `/skills/<flat>` form.
- For published submissions where `skillId` is null (legacy/edge case), behaviour is unchanged from today (falls back to `skillUrl(data.skillName)`).
- For ANY hit to `/api/v1/legacy-redirect/[slug]`, the handler returns:
  - `301` with the canonical `Location` when exactly one Skill row matches `legacySlug`.
  - `404` (no special header) when zero rows match.
  - `404` with `X-Legacy-Ambiguous: true` when 2+ rows match. The handler MUST NOT pick one arbitrarily.

## Test coverage

- vitest cases exist for: `getSubmissionFull` (publishedSkillName populated + null), submission API route (response shape), legacy-redirect (all three branches).
- All new tests pass; existing tests in adjacent files are unchanged and still green.
- No test regressions introduced in `src/app/submit/[id]/__tests__/`, `src/app/api/v1/submissions/[id]/__tests__/`, or `src/lib/__tests__/`.

## Non-regression

- `publish.ts` is unchanged.
- The `Submission` and `Skill` Prisma models are unchanged (no migration).
- `Cache-Control: no-cache` on the submissions API response is preserved.
- The 503 catch path on the legacy redirect is preserved.
- No new dependencies, no schema changes, no caching changes.

## Code quality

- Reuses the existing `skillUrl()` helper — no inlined URL construction.
- No duplication: the `data.publishedSkillName ?? data.skillName` fallback is expressed once at the consumption site.
- Field-name `publishedSkillName` is consistent across `getSubmissionFull` return type, API response, and the page consumer.

## Documentation

- spec.md, plan.md, tasks.md, rubric.md complete and consistent (this file).
- No external docs updated — internal bug fix; no user-facing change beyond the link no longer being wrong.
