# Findings F3 to F5

Part of `pr-review-muse-1-verdict.md` (reviewed commit `9ae00861f335e5161a9179bdf521137bd019905c`). Code paths are relative to `repositories/anton-abyzov/specwithcode`.

## [minor] F3. Three call sites swallow a failed store write

Files: `apps/desktop/src/screenShare/ScreenShareStore.ts:179-190`, `:228-251`, `:302-331`; `apps/desktop/src/screenShare/screenShareSession.logic.ts:581-583`.

`save` reports failure honestly and leaves state unchanged (`ScreenShareStore.ts:180-190`), and `goLive` correctly refuses to start when the audit entry cannot be written. But `store.addGrant(...)` and `store.touchGrant(...)` at `screenShareSession.logic.ts:582-583` ignore the returned `false`: a person who chose "Always allow" and authenticated gets no notice that nothing was saved, and a grant's last use silently stays old, so it can expire while in regular use. Worst of the three, `addStrike` returns nothing (`ScreenShareStore.ts:302-331`): because `save` only updates in-memory state on success, a failed write loses the strike entirely, so on a machine whose store has stopped writing (full disk, permissions) the cooldown never engages and prompts keep coming, the exact condition AC-08's persistence was added for. The spec's round 2 table says "a failed write of the session list or of a grant's use is reported"; only the session list half is.

Smallest fix: surface the result the way the audit failure is surfaced. For `addStrike`, keep the strike in memory even when the write fails (apply the next state, report `storeHealthy` false). For the grant writes, at minimum log and show the existing store-reset notice in Settings. Add store tests with a failing `write` for all three.

## [minor] F4. Relay size bounds are enforced only after a whole WebSocket message is in memory; the real cap is the `ws` default of 100 MB

Files: `apps/server/src/screenShare/ScreenShareRelay.ts:350-383`; `apps/server/src/screenShare/ScreenShareHttp.ts:277-281`; no `maxPayload` anywhere under `apps/server/src` (searched); `ws@8.22.0` defaults `maxPayload` to `100 * 1024 * 1024` (`node_modules/.pnpm/ws@8.22.0_*/node_modules/ws/lib/websocket-server.js:74`).

The relay's own limits (64 KB control, 64 KB viewer records, about 4 MB host records) are checked on complete messages. Before that, the socket layer has already buffered the whole message, fragments included. An approved device, or the replayed ticket of F1, can therefore make the server allocate on the order of 100 MB per attempt before the session is ended for size, and a host-shaped socket can do the same in text. Bounded in practice (one session at a time, first oversize ends it, 12 opens per device), and AC-08 acknowledges that one message is read whole; but it calls the bound "the server's WebSocket limit", and at 100 MB that limit is not the small bound the rest of the design assumes. The same messages also reach `JSON.parse` in the relay's host text handler.

Smallest fix: set an explicit payload cap for these two sockets at upgrade time (a little over `SCREEN_SHARE_MAX_MESSAGE_BYTES`, `packages/contracts/src/screenShare.ts:48`) if the Effect socket layer allows per-socket options; if it does not, say the real number (100 MB, one message, then the session ends) in AC-08 instead of leaving the limit unnamed.

## [minor] F5. AC-16's behaviour half is not in the reviewed commit; what is committed still asserts source-text position

Files: `apps/server/src/screenShare/noAgentPath.test.ts:44-102`; `spec.md:64` (AC-16), `spec.md:136` (round 2 answers, R2-8 row).

AC-16 now promises the HTTP half "checks by behaviour that only the two socket paths answer (every other path under the prefix, and any non-WebSocket request, is 404 before sign-in is read)", and the round 2 answers table names "a real-socket test drives both routes". At `9ae00861f` the tree contains no such test: `git ls-tree 9ae00861f -- apps/server/src/screenShare/` lists only `ScreenShareHttp.ts`, the relay and its test, and `noAgentPath.test.ts`. That test does exercise the pure path function (`:82-102`), which is real progress; the mounted router is covered only by text assertions, including that the guard's source text precedes the text `request.upgrade` (`:68-75`) and a literal line of code as a string (`:111`). Those fail on an innocent rename and pass a route added inside the same wildcard registration, which is R2-8's original complaint. (While this review was being written, commit `228569a06` added `ScreenShareHttp.test.ts` on the branch; it is outside the reviewed commit, was excluded from this review's test runs, and was not itself reviewed. If it drives real upgrades for both paths and the 404 rule, this finding closes with it.)

Smallest fix: land the real-socket test as part of the reviewed change (or re-review `228569a06`), keep the source half as the tripwire AC-16 now calls it, and drop the full-line string match at `:111` in favour of the behaviour it stands for.
