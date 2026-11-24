# SHIP: snapshot context routing and durable restoration

Reviewed exact head `5b44c7a190b000c5d38a748dfa93509350d39784`, base `dd6b00360b`, in `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016`. The worktree was clean before and after review. No blocking source finding remains.

## Prior finding resolved

The prior BLOCK receipt is `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-installed-20261025/review-context-84caf7e64e.md`. Coordinator capture now journals the complete resized source and checks source equality with image id and byte size before native acknowledgment in `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/web/src/components/desktop/SnapShotCoordinator.tsx:211`.

The optional bounded source schema is carried through `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/packages/contracts/src/composerDraft.ts`, RPC spread mappings in `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/server/src/composerDrafts/ComposerDrafts.ts`, and disk metadata in `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/server/src/composerDrafts/draftFiles.ts`.

`/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/web/src/lib/durableComposerDrafts.ts` includes source in change signatures, transport and restored snapshots. `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/web/src/lib/durableComposerDraftBindings.ts` retains it in the coordinator and thread composer bindings. The existing provider attachment serializer in `/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/web/src/lib/attachmentUploadQueue.ts:625` retains the restored source. Old source-less draft records remain accepted.

## Routing and focus

`/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/web/src/components/desktop/snapShotTarget.ts` uses the project pane's thread/environment and the same coordinator checkout selection as the workspace. The snapshot coordinator pins existing targets at request time, remembers the complete prior project URL across Settings, and returns only when the request URL is still current. It refuses an unresolved current project rather than substituting Scratch. Mounted tests cover Settings delivery, unchanged prompt text, no Scratch/new thread and newer navigation preservation.

`/Users/antonabyzov/.specwithcode/m4/worktrees/snapshot-context-1016/apps/desktop/src/snapShot/DesktopSnapShot.ts` skips feedback overlays and application activation when the active window belongs to this process. Foreign-window behavior is retained. This removes the identified app-driven focus path; it is not live proof of every macOS Space transition.

## Validation

Independently reran the seven focused suites using Node 22.20.0 with `PWDEBUG=0` and `PLAYWRIGHT_HTML_OPEN=never`: 199 tests passed. Coverage includes coordinator acknowledgment rejection when metadata is missing, exact accessibility coordinates through local-journal and schema-decoded host restore, metadata-only saves without byte resends, disk round trips, existing provider source serialization and self-capture activation guards.

The supplied logs `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-installed-20261025/context-durable-server-types-base.log` and `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-installed-20261025/context-durable-server-types.log` contain exactly the same 43 server error diagnostics. No new server type diagnostic was introduced. Parent-reported web and contract typechecks passed. The pre-repair regression log `/Users/antonabyzov/.specwithcode/m4/evidence/snapshot-installed-20261025/context-durable-before.log` records five failures against the older production implementation.

## Acceptance boundary

SHIP applies to this source candidate. User-confirmed physical both-Shift capture and native-sized attachments remain user evidence. Patched installed routing and actual native annotation at 150% remain pending. This review did not perform native input, change foreground, access a live database, restart, deploy, edit source, commit or push. It does not close increment 1016 or authorize a release.
