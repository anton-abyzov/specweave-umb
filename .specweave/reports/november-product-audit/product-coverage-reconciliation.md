# Product audit coverage reconciliation

The committed umbrella policy at `46079f1642799193059d1a3a58f32406d02acc43` sets unit 60, integration 90 and E2E 100. The measurements below use line coverage. A source verification, hosted CI result, or CLI closure message is not a measurement of package-wide integration or E2E coverage. File-scoped runs are identified separately from the full owning desktop run.

| Increment | Pinned source and real measurement | Limit |
|---|---|---|
| 1197 report headings | `c70a90e702`, 56 shared tests, 92.53% across the two report source files. [Log](1197-release-coverage.log) | Scoped unit |
| 1198 copy preview | `c70a90e702`, 48 owning destination service tests, 92.36% destinationService lines. [Log](1198-release-coverage.log) | Scoped unit |
| 1199 native exact link | `c70a90e702`, full instrumented SWCKit 599 tests. ThreadLinkResolver 96.84%, IncrementProgress 83.33%. [Log](1199-release-swift-coverage.log) | macOS Swift coverage; physical iPhone not exercised |
| 1200 clone destination | `c70a90e702`, owning ProjectRepositoryPresence suite, 95.70%. [Log](1200-scoped-coverage-final.log) | Scoped unit |
| 1202 queued shortcut | `c70a90e702`, owning DOM suite, 68.68%. [Log](1202-release-coverage-vite-plus.log) | Scoped unit |
| 1203 relay display | `c70a90e702`, 56 owning web tests, 94.85%. [Log](1203-release-coverage.log) | Scoped unit |
| 1204 Git sync | `c70a90e702`, both owning Git sync suites, 93.41% across two files. [Log](1204-release-coverage.log) | Scoped unit |
| 1218 transfer finalization | `9334c7ac2a`, owning file transfer suite, 92.22% across files and offers. [Log](1218-scoped-coverage-final.log) | Scoped unit |
| 1219 dictation | `9334c7ac2a`, full owning desktop 2252 pass/44 skip, 79.97% lines. [Log](1219-desktop-owner-coverage-retry.log) | Full desktop unit line target met; packaged Linux microphone not exercised |
| 1220 Chrome upload | `9334c7ac2a`, owning Chrome tool suite, 82.93%. [Coverage](1220-scoped-coverage-final.log), [headless browser](1220-headless-chrome-acceptance.log) | Headless fixture tests transfer isolation, not all end-to-end cases |
| 1221 config-only increment | `9334c7ac2a`, launch/progress owning suites, 92.55%. [Log](1221-scoped-coverage-final.log) | Scoped unit |
| 1222 cached Connect | `9251fe80b3`, fleet transport/update suites, 95.41%. [Log](1222-scoped-coverage-final.log) | Accepted and merged; runtime relay verification remains a release gate |
| 1223 release checks | `861dc55e00`, 97 release self-tests passed including real query path with mocked GitHub. [Log](product-release-gate-final-tests.log) | Shell gate, no Vitest source or line percentage claimed |
| 1225 Gmail approval | `6fd89366d4`, 93 tests across eight files, backend changed modules 90.61%, parser 96% per owning candidate receipt. | Draft, manual auth pending |
| 1226 model routing | `b015bf91bb`, 106 provider tests, 94.31%. [Log](1226-scoped-coverage-final.log) | Scoped unit |
| 1227 spill errors | `b015bf91bb`, 130 owning read/continuity tests, 92.72% lines across the three modules. [Coverage](1227-python-owner-coverage-retry.log). Broader functional run completed 224 cases with two skips. [Test run](1227-python-owner-coverage.log) | Scoped Python line target met; reporter synthetic filename issue was isolated from broad test results |
| 1228 PID safety | `b015bf91bb`, 21 owning tests, 95.07%. [Log](1228-scoped-coverage-final.log) | One Linux live fixture skipped on macOS |
| 1229 photo loading | `ceaa6299eb`, full instrumented SWCKit 642 tests, Router 87.85%. ChatAttachments and ChatView registered 0% on macOS. [Summary](1334-merged-swift-coverage-summary.json) | iPhone view execution and physical acceptance open |
| 1230 attachment route | `ceaa6299eb`, full instrumented SWCKit 642 tests, LiveEngine+Sessions 91.12%. [Log](1334-merged-swift-coverage.log) | macOS Swift coverage; physical relay on iPhone not exercised |
| 1231–1232 title and queue | `5d8e4c9e20`, exact title/fork/queue integration suites pass; 41.50% across entire Orchestrator and fork service in targeted run. [Log](1231-scoped-coverage-final.log) | All five added executable Orchestrator statements hit in the targeted suites. [Changed statements](1231-1232-changed-statement-coverage.json). The 236-file orchestration coverage run was interrupted after 15 minutes without a result while the owner release was active. No package-wide pass is claimed; 1231 and 1232 remain active. |
| 1233 retry approval | `2a52f98eef`, 19 owning tests, FullAccessApprovals 95.73%. [Log](1233-scoped-coverage-final.log) | Draft, manual auth pending |
| 1235 Phase 3 candidate | `b339513efe`, 42 owning tests and 91.72% scoped line coverage per candidate owner. | Candidate-preparation increment completed. Draft stacked PR #1341 remains under the active feature owner's control. |

The first broad desktop attempt had an Electron unpack race. The retry ran the same suite after the repository's normal Electron runtime preflight. Coverage provider links were scoped to the isolated worktree's installed Vitest, pointed to the already installed registry dependency, and were removed at the end of each run. The exact source and thresholds are in the saved logs.
