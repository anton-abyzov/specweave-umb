# Typed terminal policy receipts

Frozen reviewed candidate before this proposal: 8dea700ec70aa82e8ad6147736ab7e4204e6b5e1 (PR75). Do not enable adaptive while expected permanent validation outcomes can stall a page forever.

Only pure validation/policy branches in bulk intake get additive `terminal: true` and a closed `reasonCode`: INVALID_REPO_URL, INVALID_SKILL_NAME, NOT_SKILL_DOCUMENT, EXCLUDED_SKILL_PATH. Existing status `error`, human-readable error text, aggregate errors, HTTP status and policy remain unchanged. Include the input skillPath (default SKILL.md) on these receipts for unambiguous path binding. No string-error classification.

Missing mutable content, unknown/transient probes, identity deferral, failed retry persistence, failed alias/submission writes, HTTP auth/rate/server failures remain retryable. The historical queue consumer already acknowledges a specific missing-content string; this proposal does not modify that separate behavior or infer terminality from it in the crawler.

InlineSubmitter recognizes only the closed typed policy disposition and only through the same unambiguous receipt binding rules. `settledEntries` may advance such rejected inputs within this sweep. `acceptedKeys` remains limited to submitted/skipped/aliased. Track matched `totalRejected` separately from retryable per-item `totalErrors`; retain the API's existing aggregate errors for older callers. Deferred inputs retain their existing durable-queue behavior.

Tests: real bulk handler rejects a config/framework path with the typed receipt, no probe/upsert; mutable missing content and DB failure have no terminal marker; mixed valid/policy-rejected page progresses across process restart and never caches rejected keys; unknown reasonCode, terminal flag without code, and ambiguous same-name receipt remain unresolved. A subsequent sweep can reevaluate the rejected input because it was never globally cached.

Additional task Files: src/app/api/v1/submissions/bulk/route.ts; its route.skillpath-validation.test.ts and route.intake.test.ts. Existing T027 source/plan/inline/scheduler tests cover the consumer side. Producer changes require a matching Worker build/deploy before crawler enablement. Old workers safely leave these new crawler pages pending rather than pretending they acknowledged a policy rejection.

Ownership: original target paths clean; no original umbrella ledger has a current claim; live Claude project sessions point to EasyChamp, not SpecWeave. Protected dirty roots and SEO owner remain untouched. Receipt: t027-terminal-owner-check.json. Recheck before editing.
