# Review: 1324 Cross-family review policy
Verdict: fix first · risk: high · 46 files · 10 findings (3 high, 7 medium)

Reviewed heads: SpecWeave `5006fc084135e110bdb05e2bbf6aebfb17539172`; SpecWithCode `9cc926d856eb3a5a5c7f9470a41e3dea0b284f19`. Reviewer: GPT-6.1 Sol (Codex on linux-mini), November 13, 2026.

App review suites passed 36 tests and the delegation integration suite 22. SpecWeave build and tests were skipped on the reviewer's machine (npm install failed with ENETUNREACH).

## [high] specweave src/core/review/record.ts:117 Checkout timestamps can make an older approval authorize closure

Records were ordered by file mtime, ignoring their recorded `at`; verification freshness also used mtime. Run 1 ship at 09:00, run 2 fix first at 10:00, equal checkout mtimes at 12:00: run 1 won and `reviewPolicyErrors` returned `[]`. Fix: use validated record timestamps for order and freshness.

## [high] specwithcode apps/server/src/mcp/OrchestratorMcpService.ts:3126 Review constraints disappear after initial reviewer selection

Dispatch persisted the model but no review-family constraint; after a quota rejection, `providerFallbackCommand` continued an OpenAI review on `claude-opus-5-5`. Fix: persist the constraint on the child and enforce it in quota recovery, preswitch and machine handoff.

## [high] specweave src/core/review/policy.ts:181 Unknown and noncanonical family labels satisfy cross-family policy

`family=unknown` passed against a Claude author, and a `fable@machine` author did not match a Claude reviewer. Fix: one canonical family classifier; unclassified reviewer families never count.

## [medium] specweave src/core/tasks/closure-gate.ts:227 A failed Git comparison counts as identical content

`?? ''` turned a git failure into an empty diff. Fix: a null result blocks.

## [medium] specweave src/cli/commands/review.ts:97 Legacy reviewer configuration overrides the spec policy

`review.reviewer: "claude"` won over spec `Reviewer: openai`. Fix: subordinate it to the policy; warn on an explicit conflicting override.

## [medium] specweave src/core/tasks/closure-gate.ts:203 Required deep review accepts a standard-depth record

Fix: a deep policy needs a deep record, in closure and the plan card.

## [medium] specwithcode apps/server/src/review/incrementReview.ts:44 App policy resolution ignores project configuration layers

Fix: layer spec over `review.policy` over `review.crossModel` in the app too.

## [medium] specwithcode apps/server/src/review/incrementReview.ts:153 An obsolete ship review hides an unmet requirement

`records.some(...)` accepted an older ship after a newer fix first, and ignored repositories. Fix: newest matching record per repository.

## [medium] specweave src/core/review/policy.ts:177 Provider model aliases make a valid delegated review impossible to accept

`claude-opus-5.5` did not match `claude-opus-5-5`. Fix: compare canonical model ids.

## [medium] specweave src/core/review/record.ts:46 Header serialization corrupts repository paths containing spaces

Fix: reversible field encoding that still prevents header injection.
