# Product source review

No candidate is currently accepted for release. The frozen 1.0.11 source is now `5b1dffae50d4b6ced1ccd9bf499021a072ccbd38`, which combines the preview and consent corrections with the accepted handoff UI alignment. Its build, runtime, six ordinary handoffs and final publication must all bind to that source. Earlier receipts remain candidate-specific.

The actual `product-code` and `product-review` gates passed for that source on October 13: 896 focused tests, 12 external tests, all 12 required failure/consent cases, the signed desktop build and standard TypeScript checks. T-11 and T-12 completed through their declared CLI tests. The configured Effect checker was not rerun on this candidate; its predecessor's failed run remains retained and qualified in the reviewed disposition. Runtime, native UI handoffs, updater and publication remain separate gates. The later headless-only instruction applies to all further browser work; headless service-client evidence will not be labeled native-app acceptance.

The preceding `f12f4a524002470c8263f3895f5d566248981165` candidate passed 883 focused tests, 12 external tests, the desktop build and standard TypeScript checks. The configured Effect checker still failed with 803 diagnostics; the retained source review classified the changed diagnostic locations as nonblocking under the repository's focused-test/build policy. This is not a claim that the configured checker passed. All three backend services were verified on that candidate; the native M4 app remained 1.0.10, and zero ordinary UI routes were accepted before the next source change.

The original preservation audit found that preview could trigger Git's promisor lazy fetch and add filter metadata to existing clones. T-11 adds the correction and a real missing-object regression. The original failed comparison and all prior source/build receipts remain unchanged.

The combined 1.0.11 source at 425a659 was held before building: review found that a destination preview received conversation content before explicit confirmation, and the handoff dialog did not suspend underlying worker keyboard shortcuts. T-12 tracks the metadata-only preview boundary; the release owner also fixes the shortcut interaction. A new frozen source, review, build and runtime proof are required. No 425a659 artifacts or installs are accepted.

## Superseded partial-clone and destination-picker candidate

Historical successful source/build review: SpecWithCode 1.0.10, `133ebdec798acdf5c68754024aea10daedf46de8`. T-10 fixes valid partial-clone remote parsing and derives verified destinations independently of sidebar grouping. The actual `product-code` and `product-review` gates passed, and T-10 completed through its declared CLI test. The subsequently discovered preview side effect prevents release acceptance. Installation, publication and six successful ordinary UI continuations remain separate gates.

The final candidate passed 563 focused assertions plus 12 independent external assertions, server and web typechecks, changed-file lint and fresh source review. The ten required review cases retain all eight earlier cases and add `partial-clone-identity` and `sidebar-independent-destination`. The parser case binds both actual origin and upstream partial-clone tests, including real Git filter annotations; the UI case verifies selection when the sidebar separates matching checkouts. Browser checks passed; the final test-only type correction left that web code unchanged.

The desktop build and local artifact audit passed at the exact candidate. Build evidence retains directly observed child and wrapper arguments, working directories, timestamps, exit status, source bindings and pre-launch reviews. No prior candidate receipt was relabeled. The public evidence verifier passed 208 tests with 99% measured coverage and an independent review. Its native replay accepts one bounded lookup in the calling coordinator's own project and binds the persisted launch to the actual first destination run; those changes do not turn the failed earlier operation into a successful continuation.

## Superseded permission-mode candidate

Live destination refresh found that a26cf5a rejected valid partial-clone remote output and sidebar grouping could hide matching destinations. T-10 corrected both; a26cf5a is not accepted for release.

Historical successful source review: SpecWithCode 1.0.10, `a26cf5a0c5805d9bcc75aa3b44c5adb90430cdc2`. T-09 fixes coordinator launch to honor the resolved project permission mode and records the red-to-green regression. The actual corrected-candidate `product-code` and `product-review` gates passed on October 13; T-09 was completed through its declared CLI test.

The corrected source has 538 passing assertions across 16 suites, plus 12 freshly executed external assertions. Fresh independent review covers the seven failure paths below and the eighth `project-runtime-mode` case, bound to the actual assertion "launches with the project's approval mode instead of the host's full-access default" in `ProjectCoordinatorService.test.ts`. Source typecheck and changed-file lint also passed.

The evidence verifier has 183 passing tests and 99% measured coverage. An independent reviewer replayed the actual code/review fragments and checked the retained build creation and launch records against the original session. Build provenance explicitly distinguishes the observed wrapper execution from child arguments derived from the retained builder. M4 native bundle and M1/M3 service identity checks separately passed against the same candidate. Publication and all six ordinary UI destination executions remain separate acceptance gates.

The first actual SpecWeave-to-M3 operation transferred the expected commits and retained context. Its observer then rejected an implicit current-project thread lookup and safely interrupted the coordinator before any worker or edits. The retained transfer/visual observations do not count as a completed continuation. A narrowly corrected observer was independently tested; all six acceptance routes will start fresh through the next candidate's ordinary UI.

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
