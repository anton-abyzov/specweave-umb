# Round 2 findings, re-attacked against `9ae00861f`

Part of `pr-review-muse-1-verdict.md`. Code paths are relative to `repositories/anton-abyzov/specwithcode` at `9ae00861f335e5161a9179bdf521137bd019905c`; spec and plan paths are relative to the increment folder.

## Section B (R2-1 to R2-8)

| ID | Status | Evidence |
|---|---|---|
| R2-1 (blocker) Launch proof was the renderer's token | Closed | Host proof under its own label (`packages/shared/src/desktopBootstrapToken.ts:53-68`); token is another label (`:22-26`); test refuses each as the other (`desktopBootstrapToken.test.ts:70`). Renderer receives only the token (`apps/desktop/src/ipc/methods/window.ts:191-194`); secret used only in main (`apps/desktop/src/ipc/methods/screenShare.ts:224-227`). Standing has an end time (`apps/server/src/auth/personDevice.ts:214-215`), renewed every 4 min (`apps/desktop/src/screenShare/ScreenShareHost.ts:104-120`), rechecked at viewer open (`apps/server/src/screenShare/ScreenShareHttp.ts:239-243`). Residue: F7. |
| R2-2 First use viewer-asserted | Closed | Target's own `known` record (`apps/desktop/src/screenShare/ScreenShareStore.ts:53`, `:262-274`) read at `screenShareSession.logic.ts:463-464`; grant skips prompt only when not first use (`:492-495`); written on code match (`:525-528`), forgotten on grant removal (`ScreenShareStore.ts:254-260`). The viewer's word can only add a first use. Code's direction and the browser tab limit are stated at `spec.md:31`. Docs gap: F6. |
| R2-3 Relay had no deadline of its own | Closed | Handshake and life deadlines (`apps/server/src/screenShare/ScreenShareRelay.ts:291-292`), first sealed word 5 s (`:309-315`), 12 opens per device (`:283`, `:331-342`), viewer records 64 KB (`:360-365`), viewer text ends the session (`:319-321`; `ScreenShareHttp.ts:261-265`). App adds 15 s (`screenShareSession.logic.ts:290-292`). Residue: F4. |
| R2-4 Authentication unbound; no-sensor unowned | Closed in code; no-sensor stays a stated proof limit | One dialog at a time, 3 s pause (`screenShareSession.logic.ts:326-342`); reason names choice and device (`:358-362`); stale answers dropped (`:365`); third empty dialog is Deny (`:369-370`); Deny wins mid-dialog (`:349-352`); switch bound by use count (`:401-417`). `promptTouchID` with sanitized reason, no `canPromptTouchID()` gate in the feature (`apps/desktop/src/ipc/methods/screenShare.ts:85-90`, `:280-284`; search finds none). Labels are capped at 80 upstream (`apps/server/src/fleet/connectDeviceNames.ts:94`), so the action words fit the 160 cap. |
| R2-5 Draft store vs AC-02 | Closed; residue F3 | Two-layer seal (`screenShareSeal.ts:36-70`); bad key pair reads as broken file (`ScreenShareStore.ts:118-119`); strikes and first-use record in the store (`:46-54`); unlistable session does not start (`screenShareSession.logic.ts:570-575`). |
| R2-6 Threat model self-contradiction | Closed in spec; residue in plan (F6) | Attackers split at `spec.md:27-29`; authentication limit moved to `spec.md:26`; Trusted line qualified at `spec.md:30`. `plan.md:39` still merges them. |
| R2-7 Relay kept raw owner proof | Closed | Standing only: verifier bytes or end time (`personDevice.ts:199-231`); routes drop the proof (`ScreenShareHttp.ts:114-123`, `:212-224`); a failed later proof drops only its socket (`ScreenShareRelay.ts:204-207`). |
| R2-8 Text-only AC-16 test; capability always yes | Partly closed (F5) | Path decision is a tested function (`ScreenShareHttp.ts:84-94`; `noAgentPath.test.ts:82-102`); capability is macOS-only (`ServerEnvironment.ts:332`); unreported host reads as `no_host` (`ScreenShareRelay.ts:279`). Still open here: no committed real-socket route test; route half asserts source-text order (`noAgentPath.test.ts:52-80`). |

## Section A residues

| Item | Status | Evidence |
|---|---|---|
| 1 Synthetic clicks | Closed as scoped | R2-4 row; synthetic Deny and summoned dialog named at `spec.md:26` and `docs/studio/screen-sharing.md:90-92`. |
| 2 Same-user host class | Narrowed as spec'd; rest is accepted D-15, not re-reported | Later valid host replaces (`ScreenShareRelay.ts:190-194`); refusal and replacement recorded (`apps/desktop/src/ipc/methods/screenShare.ts:290-303`); AC-04 names the residual session. |
| 3 Code never compared | Closed | Viewer compares and never sends a mismatch (`screenViewer.logic.ts:352-367`); target counts (`screenShareSession.logic.ts:522-533`). |
| 5 Device names itself | Closed | List name first, claimed name second line (`personDevice.ts:98-113`; `screenShareWindows.logic.ts:48-51`); blank name becomes `Device <short ID>` (`personDevice.ts:105`). |
| 6 End causes | Closed | No-expiry refused plus expiry timer (`ScreenShareHttp.ts:144-158`, `:268`); removal and revocation ride the existing watch (`EnvironmentAuth.ts:1759-1764`); grant removal, 2 h, 2 min enforced (`screenShareSession.logic.ts:420-424`, `:585-587`, `:606-607`); heartbeat keeps a still screen live (`screenViewer.logic.ts:394-410`). |
| 8 Lock detection | Closed | Checked before and after capture; unknown is locked (`screenCapture.logic.ts:67-120`); events plus idle state (`ScreenCapture.ts:58-60`). |
| 13 Testability | Partly closed | 220 focused tests pass (verdict file). Mounted-HTTP half is F5. |
| 14 Channel nits | Closed | Integer `iat` (`screenShareChannel.ts:548-553`); failed seal poisons the sealer (`:616-637`). |

## Section C

| ID | Status | Evidence |
|---|---|---|
| C-1 Framing only in a test | Closed; comment nit in F6 | Helpers beside the constants (`screenShare.ts:261-317` in contracts); every sender prefixes (`screenShareSession.logic.ts:662`; `screenShareClient.ts:197`). |
| C-2 Who counts wrong codes | Closed as chosen | Viewer counts locally and ends (`screenViewer.logic.ts:354-362`); that end counts at the target (`screenShareSession.logic.ts:684-687`); target counts received codes (`:530-532`). F1 attacks another part of this choice. |
| C-3 Which machine | Closed | Viewer refuses a wrong environment in `open` (`screenShareClient.ts:214-221`); pin keyed by the asked-for machine (`:121`, `:186`). |
| C-4 Cooldown trigger | Closed as chosen; see F1 | Counted set is explicit (`screenShareSession.logic.ts:180-185`) and persisted (`ScreenShareStore.ts:302-331`). |
| C-5 Reusable starts | Closed | Target start deleted either way (`screenShareSession.logic.ts:481-489`); one proof per session (`ScreenShareRelay.ts:350-359`); failed challenge ends the view (`screenShareClient.ts:267-269`). |
| C-6 Records before acceptance | Closed | Nothing sealed opens pre-proof (`screenShareSession.logic.ts:440`); pre-live only `end` and code (`:517-554`); viewer draws only in live (`screenViewer.logic.ts:257-304`). |
| C-7 Status first | Closed | Published on `attached` (`ScreenShareHost.ts:221-228`); before that, `no_host` (`ScreenShareRelay.ts:279`). |
| C-8 Authentication leftovers | Closed | Pause and tries (`screenShareSession.logic.ts:326-372`); prompt stays during the dialog; unauthenticated turn-off stated in AC-02. |
| C-9 Small leftovers | Closed | No-expiry (A6), blank-name fallback (`personDevice.ts:105`), AC-12 scoped. |
