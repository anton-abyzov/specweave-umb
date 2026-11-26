# Review: 1490 Remote desktop plan (design review, pre-build)
Verdict: fix first
Reviewer context: new session, muse-wonder-full-1.0 (Meta) on Muse Code, reviewing Claude Fable 5.2's plan. Read-only; no code edited, no builds run. The `sw-review` skill body was read from `.agents/skills/sw-review/SKILL.md` (the skill loader refuses project skills in this untrusted worktree); this report follows its shape, with severities named blocker, major and minor as briefed.

Reviewed: umbrella HEAD `34fd8ea70d7e20ab7035fb38d3ef376bab02fc4d` ("1490: owner answers for D-01 to D-04"); app checkout `repositories/anton-abyzov/specwithcode` at `61f3e8baad2f771f01bf9bee8546feb26dc29f6e` (origin/main).

One brief correction: the brief says no code for this feature exists yet. The worktree holds uncommitted drafts on branch `remote-desktop`: `apps/server/src/auth/personDevice.ts`, `personDevice.test.ts`, `packages/shared/src/screenShareChannel.ts`, and a `deviceApprover.ts` edit. Findings rest on `spec.md` and `plan.md` checked against origin/main; where a draft already settles a point the finding says so.

What holds up (checked, no finding): the DPoP verifier cannot take the session proof and the reverse is testable as AC-05 says, because `verifyDpopProof` requires the literal `dpop+jwt` typ and an `htm`/`htu`/`jti` payload (`packages/shared/src/dpop.ts:36-54`) while the proof carries `aud`/`sid`/`mode`/`th`. Signing a second JWS shape with the device key is therefore not a DPoP oracle. The draft channel recomputes the transcript from the viewer's own hello (`packages/shared/src/screenShareChannel.ts:313-320`), checks the attested thumbprint before issuing a challenge (:390-391), rejects all-zero X25519 output (:198), and gives each direction its own key with the counter in the AES-GCM nonce and in the AAD (:500-511). The draft person-device guard is stricter than AC-03's text: it refuses bots and a `deviceKey` that is not the session's own. Section 8 of the plan (Touch ID cannot be relayed; the passkey QR flow needs the phone within Bluetooth range of the target Mac) is correct.

## [blocker] 1. The prompt, the switch confirmation and the viewing-machine pause do not bind the agent the threat model names

Files: `spec.md:26` (agent with a shell "must not be able to switch the feature on, add a grant, answer the prompt or read frames"), `spec.md:53` (AC-08 "Only the prompt window's own click answers it"), `spec.md:61` (AC-16 viewing-machine screenshot refused), `plan.md:38` ("computer use refuses the app's own windows"), `reports/capture-spike.md:3`, `apps/desktop/src/permissions/MacPermissionHelper.ts:183` (the sender check the plan copies).

Attack: every refusal cited is a check inside the computer-use tool path (for example the `process.pid` refusal at `MacComputerUse.ts:336-338`). An agent with a shell is not confined to that path. The spike proves a thread shell's `screencapture` is charged to the app's Screen Recording grant; the same responsible-process attribution lets a shell script post synthetic `CGEvent`s through `osascript` or a small Swift binary. A synthetic click on the prompt window is indistinguishable to Electron from a person's click, so it passes the sender check. The same click answers the native turn-on confirmation and presses "Always allow". On the viewing machine the agent ignores the computer-use pause and runs `screencapture` on the viewer window. The fallback capture file is no barrier either: a `0700` folder stops other users, not a process running as the same user, and the file exists between write and delete.

Fix: gates that synthetic input cannot pass, plus honest scoping. Put turn-on and "Always allow" behind `LocalAuthentication` (Touch ID or the account password evaluated by the system, in the main process), and consider the same for "Allow once". State in the threat model that an agent with a shell already has silent screen access through computer use today, governed by the computer-use permission, and that the prompt and banner bound remote devices and people, not local agents. Reword AC-08 and AC-16 to what is actually enforced. Run a synthetic-click spike against a prompt window built on the `MacPermissionHelper` pattern before T-05.

## [blocker] 2. The host guard rests on a session class a same-user shell can mint

Files: `spec.md:49` (AC-04), `plan.md:32` ("The target's own app (`desktop-bootstrap`, loopback)"), `apps/server/src/auth/deviceApprover.ts:1-9`, `apps/server/src/auth/EnvironmentAuth.ts:1250-1258`, `apps/desktop/src/backend/desktopServiceCredential.ts:162-163` and the `writeDesktopOwnerVerifier` function, `apps/desktop/src/backend/DesktopLocalService.ts:892-907`.

Attack: `desktop-bootstrap` is granted at token exchange when a one-time pair grant arrives with the desktop-owner proof. The proof itself is sealed with `safeStorage`, but its verifier is a plain file the app writes: `<stateDir>/secrets/desktop-owner-verifier.bin`, read fresh by the server at each exchange. `deviceApprover.ts` says the quiet part itself: "it is no boundary against a process that rewrites this user's files", and `pair --scope access:write` mints the scopes the app holds. So an agent shell writes the hash of its own proof into the verifier file, pairs, exchanges over loopback with client metadata saying `desktop`, and holds a 30-day `desktop-bootstrap` bearer that passes AC-04's test by class. As fake host it displaces the real app: no banner, no audit, denial of the real feature, and a fabricated or shell-captured screen for a first-use viewer. AC-04's second sentence ("A second host replaces the first only with the same proof") cannot be implemented as written: the proof is presented once at exchange and is not part of the session, so the server cannot compare two host sessions by it.

Fix: require the owner proof on every host upgrade (the `desktopOwnerProofOf` header check, `deviceApprover.ts:105-121`), not just the session subject; revoke live `desktop-bootstrap` sessions when the verifier changes (the real app rewrites it at launch, which then also evicts a fake); define host displacement in those terms and test it. State the residual same-user limit in the threat model, or move the host trust root to a Keychain item ACL-bound to the app's signature.

## [blocker] 3. Trust on first use has a code to compare and no step that compares it

Files: `plan.md:57`, `spec.md:51` (AC-06), `spec.md:60` (AC-15 viewer states), `packages/shared/src/screenShareChannel.ts:182-190` (draft code) and `:287`.

Failure: the plan says "Trust on first use rests on one comparison", then designs two displays and no comparison. The viewer shows a code, the target prompt shows a code, and either a person clicks Allow or they do not; nothing requires either human to enter or confirm the other side's code, and the moment the viewer pins the key is undefined ("saves `mid` per machine on first use"). The code is also static (`SHA-256` of the machine key and the device thumbprint, both public values, no nonce), so it binds the pair, never this session. In the headline use case the owner is away from the target, so nobody at the target can read its code to the viewer anyway; whoever is at the target just clicks. A path attacker (or the fake host of finding 2) stands in as the target for a first-use viewer, the click goes through, and the viewer pins the attacker's key for every later session, which is exactly the fake-screen risk slice 2 turns into credential capture.

Fix: make the comparison an enforced protocol step, not a display. For example, the target prompt requires typing the code the viewer shows (or the viewer requires the code read at the target) before the host derives keys or sends a frame, the code is derived from the transcript hash so it is per-session, and the viewer pins the machine key only after that step succeeds. Write it into AC-06 and AC-15 with a test where mismatched codes cannot reach a live state even if Allow is pressed.

## [major] 4. No bounds on pending handshakes, prompts or relay messages

Files: `plan.md:48-53` (handshake), `spec.md:53` (AC-08 cooldown), `spec.md:69` (transport pattern), `apps/server/src/preview/ServerBrowserStream.ts:35`.

Failure: the plan sets a 60-second prompt and a cooldown after three refusals or timeouts, but never bounds the work before a refusal exists. There is no handshake expiry, no cap on pending handshakes per device or overall, no rule that a second hello during a pending prompt gets "busy" instead of a second prompt, and no stated message-size cap on the relay before sealing (the copied pattern caps its socket buffer at 8 MB; the draft caps sealed records at 4 MB, but hello and challenge frames pass the relay before the channel exists). An approved device, or malware using its browser-resident key as a signing oracle, can hold a prompt on screen for 3 minutes per 13-minute cycle indefinitely, stack pending target state, or push oversized frames at the relay. Cooldown storage (memory or the sealed store) is also unspecified, so a restart may reset it.

Fix: specify and test the bounds: control-frame cap (64 KB is ample), sealed-record cap enforced at the relay too, one pending handshake and one pending prompt per device, "busy" while either is pending, a 30-second handshake deadline, incomplete handshakes counted toward the cooldown, and the cooldown kept in the sealed store.

## [major] 5. The name in the prompt, banner and audit is whatever the connecting device calls itself

Files: `apps/server/src/fleet/ConnectDeviceTrust.ts:117-124` (`describeSession` from session metadata) and `:163-172` (`gatedDevice`), draft `apps/server/src/auth/personDevice.ts` (`label: gated.label`), `spec.md:53` (AC-08 prompt names the device), `spec.md:57` (AC-12 audit names it).

Failure: `gatedDevice` builds the label from the session's self-declared client metadata. Any approved device can rename itself "Anton's MacBook Pro" and appear under that name in the prompt, the banner and the audit list; only the 4-character short ID differs, and nothing in AC-08 asks the person to check it. The approval decision is made on a spoofable string.

Fix: the server attests the name from the approved-list record for that key (the `label` stored at approval), and the host shows that, with the session's claimed name shown only as a secondary hint when it differs. Cover it in the person-device test with a session whose claimed label differs from the list.

## [major] 6. AC-11's "within 5 seconds" is true for one end cause and unproven for the others

Files: `spec.md:56` (AC-11), `apps/server/src/auth/EnvironmentAuth.ts:142` and `:1731-1750`, `apps/server/src/auth/SessionStore.ts:566` and `:568`.

Failure: device removal is polled every 5 seconds (`untilDeviceRefused`). Session expiry is not watched at all for non-cookie sessions (`watchEnd` gets `expiresAt: undefined`, with a comment saying sockets end on revoke instead), and a revoke committed by another process is re-read every 30 seconds. So "when the device is removed or its sign-in ends (within 5 seconds, the existing socket watch)" overstates two of its three causes, and removing an "Always allow" grant during a live session is not listed as ending it at all. A viewer whose Connect sign-in ends on its own device can keep watching until a revoke happens to land.

Fix: state a bound per cause and test each: device removed, at most 5 s plus close; session revoked, immediate in-process and at most 30 s cross-process; DPoP token expiry, end the screen-share session at the token's expiry since the socket alone will not. Add "grant removed" and "sign-in account changed" to AC-11, and require the host to end the session when the relay closes the viewer side, not only when its own timers fire.

## [major] 7. The sealed store's tamper guarantee is stronger than what `safeStorage` alone promises

Files: `spec.md:47` (AC-02 "A store file that was edited, replaced or copied from another machine reads as off with no grants"), `plan.md:63`, `apps/desktop/src/electron/ElectronSafeStorage.ts:72-96`, `apps/desktop/src/backend/desktopServiceCredential.ts` (header: when encryption is unavailable "nothing is stored").

Failure: `ElectronSafeStorage` is a thin wrapper whose contract in this repo is encryption, not authenticated encryption, and the plan never adds an integrity layer or a strict-schema rule. AC-02's edited-file property depends on undocumented behaviour of the OS encryption. The plan also never says what the store does when `isEncryptionAvailable()` is false; the existing credential store silently stores nothing in that case, and copying that habit here would leave the switch unpersistable or, worse, tempt a plaintext fallback. Finally, the audit list lives in the same single mutable file (AC-12): deleting or replacing the file fails safe for the switch (off, no grants) but erases the only record of past sessions, and nothing in the plan admits the audit is tamper-erasable by any same-user process.

Fix: generate a random store key, wrap it with `safeStorage`, and encrypt the store with AES-256-GCM using the environment id and a schema version as AAD, decoded through a strict schema. When encryption is unavailable the feature cannot be turned on and Settings says so. Either hash-chain audit entries or write in the spec that the audit is erasable by a same-user process and is evidence against remote devices only.

## [major] 8. Lock detection has no named mechanism, and "woken at the start" has no API behind it

Files: `spec.md:58` (AC-13), `plan.md:83`, T-04's file list (`spec.md:113`), `apps/desktop/src/ipc/methods/keepAwake.ts:105`. A search of `apps/desktop/src` finds no lock-state code today.

Failure: AC-13 promises the lock screen itself is never sent, but neither the plan nor any task names how "locked" is known, so the natural implementation (check a flag, then capture) has a race in which the Mac locks between the check and the capture and one lock-screen frame, notifications and all, goes out. "The display is kept awake and is woken at the start" is also unbacked: `powerSaveBlocker` (the only keep-awake mechanism in the app, and it uses `prevent-app-suspension`) prevents sleep but does not wake a sleeping display. Waking the physical display also discloses the screen to anyone in the room, which the plan never weighs.

Fix: name the mechanism in the spec (Electron `powerMonitor` `lock-screen`/`unlock-screen` events plus a session-state query at capture time), check it immediately before each capture, fail closed to the placard when the state is unknown, and end the frame stream on the lock event before the next capture. Either name a wake mechanism (`caffeinate -u`) with its room-disclosure cost stated, or drop "woken at the start" and show "display asleep" as its own viewer state.

## [major] 9. Slice 2's input helper is a new privileged daemon with no channel security, and its permission attribution is assumed

Files: `plan.md:82` ("a small signed Swift helper posting `CGEvent`s ... started by the app so the app's Accessibility grant applies"), `plan.md:95-102`.

Failure: two unproven links. First, attribution: today's grants work because `osascript` and `screencapture` run as children of the app; a separately signed helper inside the bundle may still appear as its own entry in the Accessibility list, and the plan carries no spike. Second, and sharper: nothing says how the app talks to the helper or how the helper knows a command came from the app. A helper that listens on a socket or XPC endpoint without checking its peer's code signature can be driven directly by an agent shell for as long as it runs, giving silent synthetic input with no prompt, no banner and no session.

Fix: before slice 2 is specced, spike the TCC attribution of a bundled helper. Design rules to write now: the helper runs only during a live control session and exits with it; it accepts commands only over an inherited file descriptor or an XPC connection validated by audit token against the app's designated requirement; it takes no listening socket; it refuses input after the banner's Stop or the session's 2-minute silence, on its own timers.

## [major] 10. D-04 now promises more than the detection signal can deliver

Files: `spec.md` Decisions D-04 ("nothing is typed into any secure field; website sign-ins go through the 1488 sign-in view"), `plan.md:99`.

Failure: the only signals slice 2 has are macOS secure event input and a system prompt holding focus. Website password fields in Chrome do not enable secure event input; to the OS they are ordinary text. So remote typing into a web password field will go through unless the owner happens to use 1488, while D-04 as recorded reads as a blanket guarantee. The plan's own last sentence admits the viewer cannot tell a password field except through this signal, but the decision was recorded without that qualifier. Clicks during secure input are also not harmless: they can dismiss or confirm system sheets, so "clicks still work" needs its own limit (no synthetic clicks while a `SecurityAgent` or `loginwindow` surface has focus).

Fix: record D-04 operationally before slice 2: typing is refused during secure event input and system prompts; web password fields are indistinguishable from ordinary fields, so either the owner accepts that remote typing can enter them, or text input into browsers is off and every website sign-in uses 1488. That is an owner choice, not an implementation detail.

## [major] 11. The TURN cap cannot promise "no bill"

Files: `spec.md` Decisions D-03 ("capped at Cloudflare's free 1,000 GB a month; at the cap sessions fall back to frames, no bill"), `plan.md:93`.

Failure: the relay mints credentials; the gigabytes are metered by Cloudflare after use, and a credential valid for an hour is a general-purpose TURN credential that any process on the viewer's device can use for unrelated traffic until it expires. A monthly cap checked at issuance therefore cannot guarantee spend stops at the free tier: already-issued credentials keep relaying, usage reporting lags, and whether overage bills or blocks depends on the Cloudflare plan attached.

Fix: shorten credential lifetime to 5 to 10 minutes, refreshed inside the sealed session; allow one live credential per environment; stop issuing based on a conservative estimate (issued minutes times a worst-case bitrate) well under 1,000 GB; and have the owner confirm on the Cloudflare plan itself that overage blocks rather than bills, since that is an account setting, not something the relay code can enforce.

## [minor] 12. Two rows of the per-OS table will not work as written

File: `plan.md:79-84`.

Linux stills "through the xdg-desktop-portal ScreenCast" via `desktopCapturer`: on Wayland, Electron's capturer goes through the portal picker, which is a consent dialog suited to starting a PipeWire stream, not to three thumbnail calls a second; the restore-token flow belongs to a persistent screencast session. Slice 7 needs a portal ScreenCast session feeding frames from PipeWire from the start, which also changes its file list. Windows: `SendInput` from the app's integrity level is silently dropped for elevated windows (UIPI), not only for UAC's secure desktop, so admin-owned windows will look dead rather than refused; the plan should say the viewer reports that state instead of implying only UAC is excluded.

## [minor] 13. Testability, file-size and 1488-collision problems in the task list

Files: `spec.md:61` (AC-16), `spec.md:52` (AC-07), `spec.md:59` (AC-14), `spec.md:74` (risks), `spec.md:106-122` (tasks).

- AC-16's test "lists the MCP tools and the guarded RPC map and finds none" cannot see the feature itself, which is two HTTP routes, so it can pass vacuously. The test should inventory HTTP route layers too and assert the only screen-share routes are the two guarded ones.
- AC-07's "The server process ... never hold a frame" is untestable as worded: the relay necessarily buffers sealed frame bytes. Say "never holds a plaintext frame" and assert the relay cannot open a fixture record.
- AC-14's pointer mark: `desktopCapturer` thumbnails exclude the cursor, so the pointer position needs its own source (`screen.getCursorScreenPoint`) and a Retina/multi-display mapping rule, neither of which is in the plan; the `screencapture -C` fallback draws the cursor in, so the two paths disagree unless the mark is suppressed for fallback frames.
- The 1,500-line risk note names the wrong files. `apps/server/src/server.ts` is already 1,748 lines and `packages/contracts/src/ipc.ts` is 1,640, and T-03 and T-05 edit both; `MachinesSettings.tsx` at 1,351 stays under only if its edit is an import and a mount. Say so in the tasks: route registration through a `routeLayer` like `ServerBrowserStream.ts`, IPC contract additions kept to the new methods file's surface.
- 1488 collision is closer than "whoever merges second imports the other's" (`spec.md:96`): the guard file already exists as an uncommitted draft here, both increments add a `packages/shared` module (which needs its own explicit `exports` entry in `packages/shared/package.json`), both want a generic device-key signing helper in `apps/web/src/cloud/dpop.ts`, and both add a capability to `packages/contracts/src/environment.ts`. Agree the one `signWithDeviceKey(typ, payload)` helper and the guard's filename before either stack grows.

## [minor] 14. Draft channel nits (only because the draft exists)

File: `packages/shared/src/screenShareChannel.ts:471-476`, `:528-544` (uncommitted).

`payload.iat` accepts any finite number rather than an integer; harmless given the 60-second window. The sealer burns a counter value when an encrypt call rejects, so the opener then waits forever on the missing counter and the session dies on the next record: fail-safe, but it should end the session explicitly on seal failure instead. The plan text (`spec.md:70`) says the channel is WebCrypto; the draft in fact uses `@noble` for X25519 and Ed25519 and WebCrypto only for AES-GCM, which is the more portable choice. Update the wording so the next reviewer does not flag a deliberate deviation.

Nits: `plan.md:59` says 1488's `signInSeal.ts` helpers are reused "once it is on `main`", but no task is blocked on that merge; `spec.md:74` says `MacComputerUse.ts` is near the line limit while no task edits it (the pause lands in `ipc/methods/computerUse.ts`, 295 lines).

