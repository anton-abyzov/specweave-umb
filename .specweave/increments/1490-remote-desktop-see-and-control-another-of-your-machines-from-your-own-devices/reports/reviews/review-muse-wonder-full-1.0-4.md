<!-- specweave review: reviewer=muse-wonder-full-1.0 model=muse-wonder-full-1.0 family=meta author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=4712523d6ca3f19f70c1eb57bbccba69eee89395 head=6cebf2b64f91dec5e5db84a56f37a5c6474b6bc1 at=2026-11-25T17:59:39.728Z -->
# PR review round 3: 1490 screen sharing slice 1 (PR 955, branch `remote-desktop`)
Verdict: ship

Reviewer: Muse Wonder Full 1.0 (Meta) on Muse Code, reviewing Claude Fable 5.2's work. Reviewed commit: `6cebf2b64f91dec5e5db84a56f37a5c6474b6bc1` in `repositories/anton-abyzov/specwithcode`. Scope: `git diff 3f9209976..6cebf2b64` (three files) plus the Prompt sentence in the increment's `plan.md`. Read-only: no source file changed, no commit, no installer, nothing captured a screen. The `sw-review` skill could not be loaded (project skills are refused in this untrusted worktree), so this report follows the round 1 and 2 reports' shape.

Counts: 0 blockers, 0 majors, 1 minor (R1, a narrowed residue of N1; it can follow the merge).

## N1 to N3

**N1 closed** (the mechanism round 2 reported), with one narrower residue as R1 below. `stage = "checking"` is assigned synchronously beside `leave()` and before the first yield in the chunk handler (`apps/server/src/screenShare/ScreenShareHttp.ts:325-326`; the first yield is the clock read at `:335`), so the 5 s branch, which refuses only `stage === "waiting"` (`:380-389`), can no longer refuse an answer that arrived in time, and an already-refused socket (`"over"`) drops its chunk at `:320`. After `dropStaleHost`, `stageNow() !== "checking"` returns before `relay.openViewer` (`:343-347`), and `onClosed` calls `closed()` only when `stage` is the opened object (`:366-370`), which is also the necessary companion change: the old condition would have called `.closed()` on the `"checking"` string.

**N2 closed.** `otherMachine` is now `!isThisMachineTarget(entry)` (`apps/web/src/components/settings/MachinesSettings.tsx:305-311`), and `isThisMachineTarget` returns false for a missing entry (`apps/web/src/connection/desktopLocal.ts:56-59`), so an unknown machine reads as "not here". For a found entry the value is identical to before.

**N3 closed.** `plan.md:75` now counts only ends after a person was asked and says nothing before the device's proof counts, matching the strike set and its gate (`apps/desktop/src/screenShare/screenShareSession.logic.ts:182-195`). The docs bullet (`docs/studio/screen-sharing.md:111-115`) now scopes "leave nothing behind" to ticket copies without the key and states that a session broken while a person is being asked counts, three in 10 minutes resting the device for 10. Both sentences now say what the code does.

## Attacks on the new `stage` logic (viewer branch)

Held, one line each. Paths are `ScreenShareHttp.ts` unless named.

- **Second message while the first is checked.** The receive loop is sequential (`Effect.forEach(chunks, onChunk)` at `:395-399`), so a second chunk's handler starts only after the first finishes: by then `stage` is the opened session (the chunk is the relay hello, delivered at `:321-322` only after the knock held and `openViewer` succeeded) or `"over"` (dropped). No message can reach a session before the knock held; the `"checking"` guard at `:320` is belt over that.
- **Deadline at the boundary.** Whichever runs first wins whole: the deadline's check at `:383` refuses only `"waiting"`, and the chunk path sets `"checking"` before any yield, so there is no interleaving where both refuse and open. The knock's own time window is read before `dropStaleHost` (`:335`), so a slow standing read cannot expire a knock mid-check either.
- **Waiting list dropping the oldest.** A socket in `"checking"` has already `leave()`d in the same synchronous step (`:325-326`), so eviction (`:314-315`) cannot target it; an evicted `"waiting"` socket has `stage` set to `"over"` by `refuse` (`:305-309`) and drops any chunk already in hand at `:320`.
- **Refused `openViewer`.** `refuse(opened.refused)` (`:359`) sets `"over"` and queues the close; no session exists, `onClosed` calls no `closed()`, and no open is counted, since the relay returns `no_host`/`off`/`busy` before its counter and `cooldown` without adding one (`ScreenShareRelay.ts:279-283`, `:331-341`).
- **Session expiry or revocation.** Both end the handler by interruption (the expiry sleep at `:376`; `serveSocketUntilSessionEnds`, `apps/server/src/auth/http.ts:325-338`). In `"waiting"` nothing exists; in `"checking"` the fiber stops at its yield and `openViewer` is never reached; once opened, `stage` is assigned in the same synchronous run as `openViewer` returns (`:347-360`, no yield between), so the ensuring `onClosed` (`:404`) always finds the object and closes it. Even a hypothetical orphan is ended by the relay's own handshake and life timers (`ScreenShareRelay.ts:291-292`).
- **Stuck in `"checking"` forever.** No: a failed knock refuses (`:337-342`), and the only yield after that is `dropStaleHost` reading the local verifier store, whose errors already read as null (`:159-162`). Only a store read that never returns could park `"checking"`, and even then the session-expiry and session-end bounds above end the socket, which by then holds no waiting place and no relay session. No attacker input controls that read.
- **Counting without a valid knock.** The relay counter is reached only through `openViewer`, which is reached only after `holds` (`:328-347`). Ticket copies without the key still open nothing and count nothing.

## [minor] R1. A viewer that disconnects during the standing read still opens briefly, then closes itself

Files: `apps/server/src/screenShare/ScreenShareHttp.ts:343-347`, `:395-404`. Can follow the merge.

Steps: (1) A valid key holder knocks; `stage` becomes `"checking"` and the handler yields in `dropStaleHost`. (2) The viewer disconnects. Nothing sets `stage` to `"over"`: the close is observed only by the next `reader.pull`, which is queued behind this very chunk (`:395-399`), and `onClosed` runs only as the ensuring action after the handler ends (`:404`). (3) `stageNow()` still reads `"checking"`, so `openViewer` runs: one of the device's 12 opens is counted and the app is told a session opened, on a dead socket. (4) The next pull (or the failed write of the queued `open` text) ends the handler, `onClosed` finds the opened object and calls `closed()`, and the relay forgets the session and tells the app it closed.

Why minor: key holder only, against its own device, in the span of one local store read; the session self-closes at once, never reaches a prompt or a frame, and counts no strike. This is strictly narrower than round 2's N1 (which needed only a late answer). It does mean the authors' "a socket that closed while the app's standing was read opens nothing" holds for expiry, revocation and eviction, but not for a peer-initiated close, which the `stageNow` check cannot see.

Smallest fix: also require the transport to be live before `openViewer` (for example `!transport.destroyed`, from `:227`). A disconnect after that check is indistinguishable from one just after opening, which `closed()` already handles.

## Anything else in the diff

No. Outside the three fixes the diff is the two explanatory comments and formatting in `MachinesSettings.tsx`, and the `stageNow` reader, which at runtime is the same variable and changes no behaviour beyond the guard above.

Focused tests run by this reviewer, all passing, 39 tests: `apps/server/src/screenShare/` (including the real-socket `ScreenShareHttp.test.ts`), run from the reviewed repository with Node 22. No repo-wide runs.

Nothing here reopens round 2's conclusions: no way was found for a screen to be seen, or for sharing to be turned on or a grant added, without what the spec requires.
