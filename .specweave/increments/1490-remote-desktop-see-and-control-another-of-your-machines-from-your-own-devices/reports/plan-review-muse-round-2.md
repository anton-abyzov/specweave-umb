# Review: 1490 Remote desktop plan and slice-1 server/channel code (round 2)
Verdict: fix first
Reviewer context: new session, muse-wonder-full-1.0 (Meta) on Muse Code, reviewing Claude Fable 5.2's plan and code. Read-only on the code under review; no builds, no app or browser started. The `sw-review` skill could not be loaded: the skill loader refuses project skills in this untrusted worktree (`project-skills-untrusted`), so this report follows the round-1 report's shape exactly. Focused tests were run and pass: 85 tests across `packages/shared/src/screenShareChannel.test.ts`, `apps/server/src/auth/personDevice.test.ts` and `apps/server/src/screenShare/` (run November 25, 2026).

Reviewed: app repository `/Users/anton/.specwithcode/worktrees/specweave-umb/remote-desktop/repositories/anton-abyzov/specwithcode` at `900ff8dd9ab1cea520b38f23859445840a7a35d7` (branch `remote-desktop`, including `cc59db7bce5fc665ebfdf0567768b76f93eb0531`), spec and plan in `/Users/anton/.specwithcode/worktrees/specweave-umb/remote-desktop/.specweave/increments/1490-remote-desktop-see-and-control-another-of-your-machines-from-your-own-devices/`. One correction to the brief: desktop code is not entirely absent. An untracked draft of `apps/desktop/src/screenShare/ScreenShareStore.ts` and its test sits in the worktree; finding A7 and R2-5 judge it because it contradicts the amended AC-02. Everything else desktop and web is unwritten, so "closed" below means closed in the spec, in the channel, or in the server code, as marked.

Counts for round 2's own findings (section B): 1 blocker, 5 majors, 2 minors, plus the ambiguities in section C. Section A restates round 1 verdicts and is not double-counted.

What holds up (checked, no finding): the commit-and-reveal construction itself is sound. The commitment `c = SHA-256(r)` is inside the transcript hash both sides sign (`packages/shared/src/screenShareChannel.ts:189-190`); the target fixes and signs its nonce and session key before it can know `r` (`screenShareChannel.ts:460-479`), and `r` is only checked against `c` when the proof is accepted (`screenShareChannel.ts:542-544`). The code is domain-separated from the session keys (`screenShareChannel.ts:219` against `:246`). The relay's order rules are as claimed: the viewer cannot send a proof before the challenge, the host cannot send a second challenge or anything sealed before the proof went by (`apps/server/src/screenShare/ScreenShareRelay.ts:247-279`), a viewer cannot inject text to the host (viewer text is dropped at `apps/server/src/screenShare/ScreenShareHttp.ts:214-217`), and the relay, not the viewer, stamps the session id on host frames (`ScreenShareRelay.ts:237`). No message reaches the app outside those rules; the relay's own `open` and `closed` texts are the only other host input, and they are server-generated (`ScreenShareRelay.ts:224-227`, `:287-290`).

## A. Round 1 findings, attacked again

### 1. Synthetic clicks answer the prompt and the switch: narrowed

D-13 is the right design (`spec.md:93`, `plan.md:66`) and the threat model now scopes the same-user process honestly (`spec.md:27`). Three limits remain. First, there is no code: a search of `apps/` and `packages/` finds no `promptTouchID` anywhere, so the one gate the whole prompt design rests on is still an unverified API choice. Second, nothing binds an authentication to the exact action it approved (R2-4). Third, the sentence that limits the same-user adversary, "it cannot pass system authentication through the app's own windows" (`spec.md:27`), is true only of windows; the same paragraph says that process can run code as the app, in which case it does not go through a window or an authentication at all (R2-6). A synthetic click can also still press Deny and can still press Allow to *summon* the system dialog at a moment of the agent's choosing; that is a social attack the spec never rates.

### 2. A same-user shell can mint the host's session class: narrowed, with a regression

The per-connection proof exists (`ScreenShareHttp.ts:163-183` against `apps/server/src/auth/personDevice.ts:171-187`), and AC-04's limit sentence is honest: a process that rewrites the verifier passes (`spec.md:50`). It should be said plainer: against the exact round-1 attacker, the per-connection check and the recheck at viewer-open add nothing. That attacker wrote the verifier, so both checks read the attacker's own file and pass. The only evictions are the real app rewriting the verifier and attaching, which replaces the fake host (`ScreenShareRelay.ts:142-148`), or the real app rewriting the verifier *without* attaching before the next viewer opens (`ScreenShareHttp.ts:192-196`), a narrow window. The recheck also does not do what AC-04 says for one of the two proof kinds, and that kind is handed to the renderer. That is R2-1, the blocker. Session revocation when the verifier changes was deliberately not done and stays undone: a minted `desktop-bootstrap` bearer survives for its full life for every other purpose; the spec no longer claims otherwise, which is honest, but the residual should be named where AC-04 is read, not only in the threat model.

### 3. The first-use code was never compared: narrowed

The protocol half is closed and tested: per-session code, both sides derive the same one, the code depends on the revealed value (`packages/shared/src/screenShareChannel.test.ts:84-97`, `:132-138`). Steering does not work: the target signs its nonce and key before `r` exists for it, the relay permits exactly one challenge (`ScreenShareRelay.ts:266-270`), and the path attacker cannot compute the code at all because it has neither X25519 secret, even though `r` travels readable inside the proof payload (`screenShareChannel.ts:404-413`). A fake target can compute the code but cannot put it on the real machine's screen, and the sealed state that asks for the code carries no field a fake target could use to show the code on the viewer (`packages/contracts/src/screenShare.ts:189-190`). Six digits with three tries is enough against guessing, because a guesser must already be the sealed endpoint (accepted device signature) and must get a person at the machine to press Allow on every first-use session. What is *not* closed is what the target can conclude. The first-use state is a boolean the viewer asserts, and the confirming code is a value the viewer itself computes; the target enforces neither. AC-06 and D-14 read as target-enforced and they are not. That is R2-2.

### 4. No bounds before a refusal: narrowed

Caps and order are in the relay and tested: 64 KB control, one hello, one challenge, one proof (`packages/contracts/src/screenShare.ts:48-50`, `ScreenShareRelay.ts:247-279`, `apps/server/src/screenShare/ScreenShareRelay.test.ts:148-196`). The time bounds are not anywhere. The relay creates the single session at viewer-open and holds it with no handshake deadline of its own, so AC-08's 15 seconds and the cooldown depend entirely on a host process that is not written yet and that a fake host will simply not run (R2-3). Two size bounds also still leak: viewer-to-target sealed records may be as large as frame records, and viewer text frames are read and discarded with no size bound applied at this layer.

### 5. The device names itself: closed (server code)

The name now comes from the approved list, the claimed name rides along separately (`personDevice.ts:98-121`), and a damaged list approves nobody (`personDevice.ts:114-121`). The contracts carry the same rule to the prompt (`packages/contracts/src/screenShare.ts:111-121`). Two cosmetic residues for T-05, not findings: an empty stored label passes `?? null` and would render as a blank name (`personDevice.ts:117`), and duplicate labels on the list leave the short ID as the only discriminator, as AC-08 intends.

### 6. End causes overstated: narrowed

The bounds are now stated per cause (`spec.md:57`) and the expiry timer exists (`ScreenShareHttp.ts:219-224`). It only fires when `session.expiresAt !== undefined`; the sessions a viewer can hold do carry an expiry, but no test pins that a Connect or phone-link session reaching this route always has one, so the timer's dead branch is one auth refactor away from being the live path. Grant removal during a live session, the 2-hour limit and the 2-minute silence are host-side and unwritten; the relay's belt for switch-off exists (`ScreenShareRelay.ts:169-170`). Round 1 also asked for "sign-in account changed"; it was dropped without a word. If the person at the viewing device signs Connect out and another account in on the same device key, nothing in AC-11 ends the running session.

### 7. `safeStorage` is not authenticated: closed in the spec, still open in the only code

AC-02 and the plan now specify the wrapped-key AES-256-GCM layer, purpose and version as authenticated data, no plaintext fallback, and rollback stated as a limit (`spec.md:29`, `spec.md:48`, `plan.md:64`). The untracked draft store implements none of it: it seals with `safeStorage` alone, its header still claims an edited file "does not open" on that basis (`apps/desktop/src/screenShare/ScreenShareStore.ts:6-10`, `:132-143`), and its schema has no cooldown counts and no store key (`ScreenShareStore.ts:34-40`), both of which AC-08 and `plan.md:64` put in the store. If T-04 grows from this draft, finding 7 ships. R2-5.

### 8. Lock detection unnamed, wake unbacked: closed in the spec

AC-13 names `powerMonitor` events plus `getSystemIdleState` before and after every capture, drops a frame whose capture met a lock or an unknown state, and drops waking the display (`spec.md:59`, `plan.md:92`). The after-capture check is the part that closes the round-1 race: a frame captured across the lock is dropped, and a frame captured before the lock is ordinary desktop content the session was allowed to show. No code exists yet; for a plan review this one is answered.

### 9. Input helper (slice 2): closed for slice 1

The rules and the spike-before-slice-2 are written (`plan.md:91`). One wording to fix when slice 2 is specced: the helper "stops on its own timer after the banner's Stop" cannot know about Stop except over the same inherited pipe, so the *silence* timer is the real self-stop and should be stated as such.

### 10. D-04 over-promises: closed for slice 1

Slice 1 types nothing, and the unkeepable half is recorded as an owner decision before slice 2 (`spec.md:83`, `spec.md:101`, `plan.md:104`). The plan's added rule, no clicks while SecurityAgent or loginwindow has focus, names no detection API; that belongs in the same slice-2 spike as finding 9, and the spec should say so next to the rule rather than leave it as a settled mechanism.

### 11. TURN cap cannot promise no bill: closed

D-03 and `plan.md:98` now say the relay can only stop issuing on its own estimate, set credential life to 10 minutes with one live credential per machine, and put the overage-blocks confirmation on the owner before slice 4.

### 12. Per-OS table rows: closed

Linux stills are now one portal ScreenCast session per screen-sharing session with PipeWire frames, and Windows names the UIPI dead-window state and its viewer wording (`plan.md:82-87`).

### 13. Testability, file sizes, 1488 collision: narrowed

AC-07 and AC-14 are testable as worded now, the relay-cannot-open test exists (`ScreenShareRelay.test.ts:224-229`), the file-size risks name the right files (`spec.md:75`), and the 1488 helper names are agreed (`spec.md:99`). AC-16's test is still weaker than the criterion: it greps source for route strings and asserts the guard's source position precedes `request.upgrade` (`apps/server/src/screenShare/noAgentPath.test.ts:44-68`). A route mounted through the same wildcard registration, or spelled by string composition, passes it. R2-8.

### 14. Channel nits: closed

`iat` must be an integer (`screenShareChannel.ts:536-541`), a failed seal poisons the sealer instead of stranding the opener (`screenShareChannel.ts:604-605`, `:623-625`), and the wording now names `@noble` plus WebCrypto (`spec.md:71`).

## B. New holes the answers opened

## [blocker] R2-1. The `launch` host proof is the renderer's token, is never rechecked, and never expires on the socket

Files: `apps/server/src/auth/personDevice.ts:171-187`, `apps/server/src/screenShare/ScreenShareHttp.ts:179-196`, `packages/shared/src/desktopBootstrapToken.ts:16-45`, `apps/desktop/src/ipc/methods/window.ts:191-194`, `apps/desktop/src/backend/DesktopBackendConfiguration.ts:866-868`, `spec.md:50` (AC-04), `spec.md:69` and `plan.md:24` (the main process is the authority because a render
...[truncated 13588 chars]