# Accepted Gmail and automatic retry integration

Anton explicitly accepted Gmail #1339 at `1962cad03285859037bbc66feb0c5e91043438a3` and automatic retry #1336 at `4e0d5c79c622c46fe55b71743a0093c5fbed4287` in the campaign root chat. Both reviewed heads were verified and marked ready. The ready events started required Checks 41785600075 and 41785600159, respectively. Prior exact-head draft dispatches 41749320674 and 41751821802 both succeeded.

The designated publisher retains publication. The next release must include these fixes after merge plus already merged Connect-first #1348 (`24a757c9a8d3f771e8ed31006a4af47c3d188d65)). No successor release branch or tag was visible at start. The earlier publisher delivery failure remains recorded in connect-first-rollout-acceptance.md. The owner-held Phase 3 and Ubuntu stacks are separate.

| PR | Required Checks | Squash merge | Main Checks |
|---|---|---|---|
| #1336 | 41785600159 success (14 pass, 6 skip) | `02ceb95e95af8fd3aa4036b25f1c6f0bf4a2fa76` | 41787373474 success |
| #1339 | 41785600075 success (14 pass, 6 skip) | `bfe471250344d19408a34744d2c6684a2c00ab50` | 41787654999 success |

The two changed retry blobs and all 15 Gmail changed blobs matched the approved candidates. The common RPC fixture had already landed on main. No live mail was sent. Gmail increment 1225 passed focused owning verification (4/4 ACs, 6/6 tasks), passed its coverage gate and completed. Its lifecycle hook reported unlinked Jira and ADO providers, so no external item was closed.

The active publisher 1.0.180 candidate at `c8a8af300cea1d5bcb13f3fc315e932cf97a489a` includes #1348 but predates both new merges. Gmail's new production module is absent and the retry production blob differs from the merged implementation. Leave that build with its publisher. The next publisher candidate must include the three merge commits above and in the handoff. The existing publisher contact path has not changed.

Publisher 1.0.180 failed before publication at the bundle gate (exit 1 after 1,108 seconds). The exact failing operation was the retained Google headless verifier, `scripts/studio-google/verify.mjs:639`: it timed out after 15 seconds waiting for the visible label for the work verifier fixture account. The owner log is `.specweave/state/release-logs/studio-20261104T063037Z.log`. The symptom alone does not establish why that control was absent. The candidate excluded the two accepted auth fixes. The publisher retains diagnosis and release recovery. No publisher run was restarted or changed. Both release listings still showed 1.0.179. The Gmail checkout was retired, with the two original-owner stacked checkouts retained.

Automatic retry increment 1233 completed locally via SpecWeave 3.1.21. Its task and acceptance criterion were already done and its verification passed. Both declared blobs matched at the independently reviewed and verified source, accepted head, and squash merge. Scoped line coverage was 95.73% against 60%. No test rerun was needed. Closure reported missing Jira and ADO mappings and closed zero external issues. The shared Files migration and original owner lanes were untouched.
