# Review: 1324 Cross-family review policy (round 4)
Verdict: ship · risk: medium · 5 files · 1 finding (1 medium, 0 critical, 0 high)

Reviewed app head: `612aa21f381e2ff875f65aafaca679b0be55bdc9`. SpecWeave unchanged at `bbbcfb8a3551598b420dd3f41e82fadbe46f04d0`. Reviewer: GPT-6.1 Sol (Codex on linux-mini), November 13, 2026.

All 84 focused tests passed. Sibling registrations, normalized paths and legacy one-line `Files:` fields now agree with the CLI.

## [medium] specwithcode packages/shared/src/reviewPolicy.ts:371 Legacy "Files Affected" lists still bypass per-repository evaluation

The regex reads only `Files:` fields; the CLI also reads `**Files Affected**:` lists. With two tasks in that format and only an API ship review, the app returns `policySatisfied: true`. Fix: parse those lists too, with a regression test.
