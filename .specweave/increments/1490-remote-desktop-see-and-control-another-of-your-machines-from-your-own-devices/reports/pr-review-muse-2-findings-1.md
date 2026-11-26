# Round 2 findings N1 to N3, and attacks that held

Part of `pr-review-muse-2-verdict.md` (reviewed commit `3f9209976638b4a312ccc34295d39fb135349024`). Code paths are relative to `repositories/anton-abyzov/specwithcode`; spec and plan paths are relative to the increment folder.

## [minor] N1. The knock deadline can refuse a valid knock and still let it open, for a moment

Files: `apps/server/src/screenShare/ScreenShareHttp.ts:301-306`, `:315-359`, `:368-384`. Can follow the merge.

Sequence:

1. A holder of the device key answers at 4.99 s of the 5 s `SCREEN_SHARE_KNOCK_MS`. `onChunk` removes the waiting place (`leave()`, `:322`), checks the knock, then yields at `dropStaleHost` (`:339`), which reads the verifier store. All through this, `stage` is still `"waiting"` (`:301`).
2. The deadline branch (`:374-383`) sees `stage === "waiting"`, calls `refuse`, which sets `stage = "over"` and queues the close.
3. `onChunk` resumes and calls `relay.openViewer` anyway (`:341-354`), overwriting `stage` with the opened session: one of the device's 12 opens is counted and the app is told a session opened, on a socket whose close is already queued ahead of the relay's `open` text.

Why it stays minor: only a valid key holder can be in step 1, against its own device. The close was queued first, so the viewer sees `handshake_failed`; the app's session dies at the hello phase when the socket's close lands (`onClosed`, `:360-364`), which counts no strike. AC-03's "a wrong or missing answer in 5 seconds closes the socket" is not quite what a late-but-right answer gets.

Smallest fix: move `stage` to a "checking" value synchronously when the first chunk starts (beside `leave()`), or re-check `stage` after `dropStaleHost` before `openViewer`.

## [minor] N2. Q1 residue: a missing environment entry makes the settings block act on this Mac

Files: `apps/web/src/components/settings/MachinesSettings.tsx:303-309`; `apps/web/src/components/screenShare/ScreenShareSettings.tsx:308-310`. Can follow the merge.

`otherMachine` is `entry !== undefined && !isThisMachineTarget(entry)`. When the primary environment is not in the loaded `environments` list (not loaded yet, or a stale list), `entry` is `undefined`, the wrapper yields false, and the block wires the desktop bridge: the switch acts on the Mac the window runs on while the page is about the primary machine. `isThisMachineTarget` itself returns false for a missing entry (`apps/web/src/connection/desktopLocal.ts:56-60`); the wrapper undoes that. Still safe in the round 1 sense (the system dialog appears on this Mac and says "this Mac"), so the cost is a person flipping the wrong machine's switch after authenticating at it, which AC-15's "only says where to go" does not quite deliver in that moment.

Smallest fix: treat a missing entry as `otherMachine: true` (unknown is not "here").

## [minor] N3. Two sentences claim more than the code does

Files: `plan.md:75`; `docs/studio/screen-sharing.md:111-113`. Can follow the merge.

- `plan.md:75` still says "Three refusals, timeouts or unfinished handshakes for a device in 10 minutes silence it for 10 minutes." Unfinished handshakes before a proof no longer count (`screenShareSession.logic.ts:188-195`); AC-08 says so and the plan now contradicts the F1 fix it describes elsewhere (`plan.md:50`).
- The docs say of someone on the network path: "nothing they do counts against a device once they stop." True before the knock. Not quite after: an edge that corrupts or drops a genuine session while a person is being asked ends it as `viewer_ended` or `protocol_error`, both counted (`:715-717`); three genuine attempts broken that way buy the device 10 minutes of quiet time that outlasts the edge. The prompts did happen, which is what the count protects, so this is a wording fix (scope the sentence to copies without the key), not a code change. AC-03's limit sentence (`spec.md:51`) is already scoped to that stage.

## Attacks on the new code that held (checked, no finding)

- **Knock replay and reflection.** The nonce is 128 bits per socket (`ScreenShareHttp.ts:299`) and checked against that socket's stored nonce, its machine id and a 60 s `iat` (`packages/shared/src/screenShareChannel.ts:551-584`). A knock made for one socket's nonce fails on another (tested, `ScreenShareHttp.test.ts:642-648`). Reflection needs an active intermediary on the real device's own connection swapping the nonce in `prove`; what it wins is one relay open that cannot pass the session proof and counts no strike, no better than dropping that connection, which AC-03 states as the limit.
- **Knock as another proof.** Three types, three strict checks: knock `swc-screen-share-knock+jws` (`screenShareChannel.ts:510`, `:564`), session proof `swc-screen-share+jws` (`:37`, `:605`), DPoP `dpop+jwt` by schema (`packages/shared/src/dpop.ts:12`, `:40`). Each verifier also demands its own payload fields, so a re-typed knock still fails. Tested both directions (`screenShareChannel.test.ts:554`). The 1488 sign-in view uses no device-key JWS at all (X25519 sealing, `packages/shared/src/signInSeal.ts`), so there is nothing to spend a knock on there. The only generic `jwtVerify` uses are a provider's remote JWKS and the relay's own key; neither takes an embedded device JWK.
- **What the viewer signs.** Only `aud` (the machine it asked for, from its own deps, not from the message), the server's nonce and `iat` (`screenShareChannel.ts:519-544`); the client signs once, only before any session id, and refuses a `prove` naming another machine or an `open` that arrives without a knock (`apps/web/src/components/screenShare/screenShareClient.ts:207-246`). The maker refuses nonces not shaped like the server's, so the device key is not a general signing oracle.
- **Thumbprint binding.** The compared thumbprint is the session's bound `jkt:` key (`personDevice.ts:71-86`), the same key the approved list is read by (`:94-113`) and the same one relay and target later attest against the session proof (`screenShareChannel.ts:467`, `:607`). A knock under another key, or signed by another key under the device's JWK, fails (tested).
- **Before the check.** Nothing is opened, counted or told to the app: `openViewer`, the open count, the host standing recheck and the log line all come after `holds` (`ScreenShareHttp.ts:322-359`), and refusals for `no_host`/`off`/`busy` consume no opens (`ScreenShareRelay.ts:279-283`).
- **Waiting list, CPU, memory.** At most 8 waiting sockets, oldest dropped, and a first chunk removes its own place before any yield, so eviction cannot kill a knock already being checked (`ScreenShareHttp.ts:306-322`). A flood can still evict a socket that has not answered yet, which is AC-03's stated flood limit and leaves nothing behind. Verification is one bounded parse (at most 2048 bytes, `knockOf`, `:136-140`) and at most one P-256 verify per socket, only after the header's thumbprint matches; the whole-message buffering above that is F4 as accepted.
- **Strike rule, both directions.** A key holder cannot prompt without limit: every viewer-caused end while asked (leave, `end` record, nonsense record, wrong code, timeout, Deny) is in the counted set (`screenShareSession.logic.ts:188-195`, `:527-565`), and the relay's 12 opens bound even the uncounted pre-prompt failures. A third party cannot add a strike to someone else's device without that device's key, because "asked" is only reachable after knock and session proof; on the device's own connection the path adversary's case is N3.
- **Host standing edges.** A proof shown in the previous window gets only the rest of that window plus one; a next-window proof (clock skew) gets until the end of the window after its own, exactly as long as it would itself be accepted (`desktopBootstrapToken.ts:76-91`). At the end instant itself the proof no longer matches and `holds` is false, consistently.
