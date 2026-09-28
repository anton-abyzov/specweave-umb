# T031: distinct artifact identity through publication

Status: root/reviewer approved direction; implementation awaits serialized T031 claim. T030 original natural-key recovery is complete. This task owns the22 newly exposed same-repository, same-label, different-path collisions. No schema/DDL, production replay, backfill or VM changes.

## Identity and label

Use the complete authoritative tuple `[sourceType, stable sourceId, case-preserving artifactPath]`, serialized unambiguously. Keep its case and root-path semantics. Canonical lookup always precedes legacy fallback.

Only after an exact canonical miss and a confirmed same-repository/different-path legacy collision may intake create a fresh row with the durable human-readable label `original name (full relative artifact path)`. It is intentional disambiguating display text, not an encoded key: no stripping or KV-only label. Persist the same qualified label to DB and initial KV. Keep the original caller path in receipts. Never qualify repeatedly, overwrite the old row, or reuse a generated-name collision belonging to another tuple. Bounded P2002/P2025 handling re-reads actual rows; uncertainty remains retryable. A pathological pre-existing literal qualified-name collision fails closed rather than being recursively renamed.

## Publication

Read the Submission tuple, path, durable label and linked Skill from DB by ID. Queue/KV label and identity are not authoritative. A valid existing linked PUBLIC/tenantless exact-artifact Skill keeps its existing name and all URL slug segments, including legacy names.

For a genuinely new complete-canonical artifact, use a deterministic full-tuple SHA discriminator in the publication URL/slug segment, not the human label. Align Skill.name and the compound(ownerSlug,repoSlug,skillSlug) constraint. Keep the global deriveSkillSlug helper unchanged. This also protects distinct labels whose paths share a basename. Create-only allocation catches only relevant uniqueness conflicts, re-reads the exact target, and never adopts a foreign/private/tenant/path-mismatched row. Existing links or canonical associations are rechecked on retries; an unproven foreign/unlinked target fails closed.

Canonical metadata updates use an atomic exact ID/name/path/public/tenantless predicate. Version creation and in-place/ghost updates must acquire and verify the same identity within their transaction, then write the version/outbox and conditionally link the exact Submission tuple to the same Skill in that transaction. Zero matched rows or changed identity rolls back. Preserve the existing link-after-version guarantee, and do not let canonical identity errors be swallowed into apparent success. Upsert's orphan-PUBLISHED repair shares the target validation or leaves the orphan pending; it may not backfill by basename/public visibility alone.

## Read surfaces

Add optional skillPath to DB/raw-SQL/KV summaries, GET/list and search projections. Shared dedup uses normalized repository plus case-preserving artifact path when known, with a separate legacy fallback for path-missing snapshots. A legacy snapshot must not collapse a known distinct path; duplicate snapshots of the same ID still collapse. No queue page layout changes or global slug changes.

## Exact product files

- src/lib/submission/artifact-identity.ts (new helper)
- src/lib/submission/upsert.ts
- src/lib/submission/publish.ts
- src/lib/submission/types.ts
- src/lib/submission/kv-store.ts
- src/lib/queue/submission-dedup.ts
- src/lib/queue/fetch-submission-list.ts
- src/app/api/v1/submissions/route.ts
- src/app/api/v1/submissions/search/route.ts

## Exact tests

- src/lib/submission/__tests__/artifact-identity.test.ts (new)
- src/lib/submission/__tests__/upsert-distinct-artifact.test.ts (new)
- src/lib/submission/__tests__/publish-artifact-identity.test.ts (new)
- src/lib/submission/__tests__/submission-artifact-flow.test.ts (new)
- src/lib/submission/__tests__/upsert-natural-key.test.ts
- src/lib/queue/__tests__/submission-dedup.test.ts (new)
- src/lib/queue/__tests__/fetch-submission-list.test.ts
- src/app/api/v1/submissions/__tests__/route.artifact-identity.test.ts (new)
- src/app/api/v1/submissions/bulk/__tests__/route.identity-collision.test.ts

Tests cover baseline reproduction; both unique constraints; same/different tuple create races; foreign/private/tenant targets and races; unchanged old rows/URLs/versions; exact label/path after KV loss and original queue label; case-sensitive distinct paths through DB/list/cache/shared-client dedup; canonical version/ghost/link failures with no outbox/search false success. Run explicit Node22 focused/full tests, retain baseline typecheck diagnostics, then checkout-local dependency Worker build with Prisma WASM topology guards. Independent frozen-head review and CI precede root merge/release. Natural read-only snapshots provide final runtime evidence; no synthetic production intake.
