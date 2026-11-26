# Findings F1 and F2

Part of `pr-review-muse-1-verdict.md` (reviewed commit `9ae00861f335e5161a9179bdf521137bd019905c`). Code paths are relative to `repositories/anton-abyzov/specwithcode`.

## [major] F1. A handshake that fails before any proof counts against the device, so a replayed ticket can keep a real device in cooldown

Files: `apps/desktop/src/screenShare/screenShareSession.logic.ts:180-185`, `:290-292`, `:448-459`, `:684-687`; `apps/desktop/src/screenShare/ScreenShareStore.ts:293-331`; `apps/server/src/screenShare/ScreenShareHttp.ts:139-146`, `:245-255`; `apps/server/src/auth/SessionStore.ts:1261-1270`; `spec.md:19`, `spec.md:24`, AC-08 (`spec.md:56`).

Attack, step by step:

1. The network adversary in the threat model (Cloudflare's edge included, `spec.md:24`) sees a WebSocket ticket for an approved device's session. A ticket carries only the session id, no path and no single-use marker (`SessionStore.ts:1261-1270`), and the spec records that it "is valid 5 minutes and is not single-use" (`spec.md:19`).
2. The adversary replays it at `GET /api/screen-share/view`. The guard passes: the session behind the ticket is that approved device (`ScreenShareHttp.ts:139-146`). The relay opens the one session and tells the app (`ScreenShareHttp.ts:245-255`).
3. The adversary cannot sign a proof (no device key) and does not need to. Sending a hello naming any other device key ends the session at once as `handshake_failed` (`screenShareSession.logic.ts:448-459`); sending nothing ends it after 15 seconds the same way (`:290-292`).
4. `handshake_failed` is in the strike set, and strikes are recorded for a set member whatever phase the session reached (`:180-185`, `:686-687`). Each replay also holds the single session slot (`busy` for everyone else) until it ends.
5. Three replays inside 10 minutes put the genuine device into its 10-minute quiet time (`ScreenShareStore.ts:310-330`), refused at the door as `cooldown` (`screenShareSession.logic.ts:265`). Each new ticket the device's ordinary connections mint through the same edge renews the supply, so the denial can be kept up indefinitely. Nothing was ever shown and nobody at the machine was ever asked: the prompt appears only after a proof (`screenShareSession.logic.ts:496-503`), so these strikes buy no protection for the person.

This contradicts AC-08's own other sentence, that "a viewer that leaves before its proof costs the person nothing and is bounded by the relay's 12 opens". A silent adversary simply stays 15 seconds, or sends one bad hello, instead of leaving, and the cost lands on the device. The relay's 12-opens bound already limits how long the session slot can be squatted; the strike is what converts a bounded squat into a device-wide, renewable refusal.

Smallest fix: do not strike failures that end before a proof was accepted (phases `hello` and `proof` in `end`), keeping strikes for Deny, prompt timeout, wrong code, and leaving while asked. That needs AC-08's counted set reworded ("a handshake that did not finish" becomes, for example, "a proof the machine refused after a well-formed hello naming this device's key" if the authors want any pre-prompt count at all). Add a session-logic test: three pre-proof failures, then a genuine attempt from the same device still reaches the prompt.

## [minor] F2. A frame sealed before Stop can be sent after the banner has been hidden

Files: `apps/desktop/src/screenShare/screenShareSession.logic.ts:657-669`, `:671-709`, `:635-648`.

Failure: `sendSealed` starts the seal and sends the result whenever encryption finishes, without checking that the session is still the current one (`:661-662`). `end` hides the banner synchronously (`:681`) and only then queues the sealed `ended` state behind any frame already sealing (`:699-707`), with the socket close after that. So a frame captured an instant before Stop (or turn-off, or grant removal) still travels after the banner came down and is drawn by the viewer before the `ended` record lands. One frame only, it was captured while the session was live, and Stop still ends the session well within 1 second; but AC-09's "banner from before the first frame until the session ends" is not literally true for that frame.

Smallest fix: in the seal completion, send only when `this.session === session`, except for the final `ended` state itself (for example a `final` flag on that one call). Add a logic test with a deferred sealer: seal a frame, stop, release the seal, expect no frame on the wire.
