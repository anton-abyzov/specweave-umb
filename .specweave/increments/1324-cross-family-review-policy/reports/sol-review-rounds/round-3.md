# Review: 1324 Cross-family review policy (round 3)
Verdict: ship · risk: medium · 13 files · 2 findings (2 medium, 0 critical, 0 high)

Reviewed heads: SpecWeave `bbbcfb8a3551598b420dd3f41e82fadbe46f04d0`; SpecWithCode `213372d237caf8c41e5ffa8c5534104f8ba71139`. Reviewer: GPT-6.1 Sol (Codex on linux-mini), November 13, 2026.

All 175 focused app tests passed, including the handoff guard suite. Source probes confirm the wildcard, strict-close chronology, pinned-model fallback and underscore fixes. SpecWeave build and unit suites were not rerun.

## [medium] specwithcode packages/shared/src/reviewPolicy.ts:319 Registered sibling repositories and normalized paths still get the wrong owner

A registered checkout at `../outside` is discarded, so Files `../outside/src/a.ts` map to `.` while the CLI maps them to `../outside`. With registered `libs/core`, Files `./libs/core/src/a.ts` map to `.` because task paths are not normalized before prefix matching. Fix: keep sibling and external registrations and normalize both sides as the CLI does.

## [medium] specwithcode apps/server/src/review/incrementReview.ts:208 Legacy task definitions are omitted from per-repository satisfaction

The plan reader uses a legacy tasks file when present, but review satisfaction derives repositories only from spec text. With legacy tasks touching `repositories/acme/api` and `repositories/acme/app` and only an API ship review, the app returns `policySatisfied: true`. Fix: derive owners from the effective task source.
