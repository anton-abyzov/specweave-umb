# Product source review

Current accepted source review: SpecWithCode 1.0.10, `a26cf5a0c5805d9bcc75aa3b44c5adb90430cdc2`. T-09 fixes coordinator launch to honor the resolved project permission mode and records the red-to-green regression. The actual corrected-candidate `product-code` and `product-review` gates passed on October 13; T-09 was completed through its declared CLI test.

The corrected source has 538 passing assertions across 16 suites, plus 12 freshly executed external assertions. Fresh independent review covers the seven failure paths below and the eighth `project-runtime-mode` case, bound to the actual assertion "launches with the project's approval mode instead of the host's full-access default" in `ProjectCoordinatorService.test.ts`. Source typecheck and changed-file lint also passed.

The evidence verifier has 183 passing tests and 99% measured coverage. An independent reviewer replayed the actual code/review fragments and checked the retained build creation and launch records against the original session. Build provenance explicitly distinguishes the observed wrapper execution from child arguments derived from the retained builder. M4 native bundle and M1/M3 service identity checks separately passed against the same candidate. Publication and all six ordinary UI destination executions remain separate acceptance gates.

## Superseded first candidate

Historical review, superseded before live UI acceptance: destination inspection found that coordinator launch ignores the scoped project permission mode. T-09 tracks the fix and fresh named regression/review. The d7edbf9 candidate below is not accepted for release; its raw test receipts remain unchanged.

Candidate: SpecWithCode 1.0.10, `d7edbf9c8fc1ac6bad3c24dbb73232e3ca489068`.

Studio implementation: [PR 168](https://github.com/anton-abyzov/specweave-studio/pull/168). Independent source review reports no unresolved findings. The actual `product-code` and `product-review` evidence gates passed on October 13, 2026.

The retained named runs contain 97 unit, 19 component and 12 external assertions, with no failures or skipped assertions. These counts are the named review runs, not a sum to add to the separate combined regression run. The verifier binds each required assertion to its executed report and exact candidate source.

| Case | Observed proof |
| --- | --- |
| wrong-repository | Real nested destination origin changed to root origin; preflight asserts identity-mismatch. The same named test also verifies a removed required nested repository. |
| dirty-destination | Real nested destination file changed; materialization asserts dirty-repository and no fetch. |
| diverged-destination | Destination-only commit diverges from published source; materialization asserts diverged-repository and identical checkout snapshot. |
| missing-source-object | Deletes the exact loose root commit object from a disposable real source repository after inspect, proves cat-file failure, then publication refuses inspect/git-failed before push/fetch/ls-remote/worktree. Remote refs/object counts/config and destination snapshots/bytes remain unchanged; output and publication record remain absent. |
| nested-pin-mismatch | Commits new nested code without updating parent gitlink. Inspect refuses dirty-repository. This proves source gitlink versus initialized nested HEAD mismatch, not a separately named destination-manifest mismatch. |
| active-owner | Real migrated SQLite records exercise another owner running run, pending approval, pending effect and active provider session; all refuse busy. Only terminal records permit preview, without pushes. |
| denied-transfer | Actual WsRpcGroup/RpcTest with production RpcAuthorization middleware rejects missing required transfer grant and proves handler did not execute; eleven cases remove every required publish/start grant individually. |

External reviewer tests bind their production imports to exact candidate Git blobs. The desktop build records successful source-preserving execution and frozen artifact hashes; its argv/cwd are explicitly derived from the unchanged retained builder, because the original receipt did not separately capture them.

Raw evidence stays in the private fleet evidence directory. The release publication and six ordinary UI-driven destination executions remain separate gates. This review does not claim those are complete.
