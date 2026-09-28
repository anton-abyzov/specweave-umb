# T030 original recovery and next-page identity conflicts

The original natural-key collision is recovered: its exact hashed identity is accepted, the original page4 batch drained, and the same sweep advanced to page5 without a crawler/scanner restart or history reset. Final Worker504442ec is separately proven at100% with public guards and natural VM3 HTTP200 intake. The exact Worker version that first accepted the original target is not claimed. The failed97e2143c packaging release and rollback remain preserved.

The next page is not healthy yet. A natural retry beginning23:22:58 on final504442ec returned HTTP200 but all22 item logs reported exactly `Submission identity cannot be safely reused`. No P2002/P2025, timeout, quota or missing-content class appeared. The invocation finished23:23:21 with submitted22, created0, skipped0, lost0, errors22;22 items remain unresolved. This is a truthful retryable item failure, not a successful intake receipt.

An exact read-only DB reconciliation of those22 checkpoint identities found22 matching legacy URL/name rows (10 distinct rows), zero canonical-primary matches, and22 mismatched incoming artifact paths. All22 existing rows agree internally: their stored skillPath derives their own stored artifactPath. Allsource types and stable source IDs agree with the incoming repository.19 matches are PUBLISHED with linkedPUBLIC tenantless Skills;3 are DEQUEUED, unlinked and unowned. No user-owned or private/tenant scope denial was found. The19 linked Skills also agree with their existing path and repository, and all19 differ from incoming paths.

These are distinct same-name artifacts under the still-active legacy unique(repoUrl,skillName), not false privacy refusals. Reusing an old row or rewriting its path would conflate artifacts. Keep the guard. A submission-name suffix alone is also insufficient: the actual current slug module derives the same publication slug from all22 incoming/existing path pairs. Current linked Skill names differ from that derived slug in19/19 cases, so this receipt does not claim an actual present Skill.name conflict; it does establish a future convergence hazard that needs an end-to-end identity design.

Evidence, all in this directory:
- t030-natural-verdict-final-v3.json: bounded original-target recovery; latestRunClean=false.
- t030-natural-snapshot-final-v3.json: current22-item retry and preserved history.
- t030-pending-next-tail.json: exact allowlisted final-version failure category counts.
- t030-pending-scope-read.json: canonical/legacy/scope metadata projection.
- t030-pending-linked-consistency-read.json: linked path/repository consistency.
- t030-pending-publication-collision-read.json: actual-module publication derivation.
- t030-packaging-root-cause.json: failed-artifact dependency topology and adapter source hashes.

No manual intake/replay/reset/restart, production data write, source edit or privacy relaxation was performed during this diagnosis. Root and independent reviewer own the next bounded design decision; no whole-sweep completion is claimed.
