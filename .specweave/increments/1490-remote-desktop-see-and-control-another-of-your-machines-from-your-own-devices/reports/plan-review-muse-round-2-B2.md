# Round 2, section B (part 2): R2-4 to R2-6

Continuation of `plan-review-muse-round-2.md` (review at `900ff8dd9ab1`). Part 1 is `plan-review-muse-round-2-B1.md`.

## [major] R2-4. System authentication is specified as a boolean, not bound to an action, and its one hard case has no owner

Files: `spec.md:48` (AC-02), `spec.md:54` (AC-08), `spec.md:93` (D-13), `spec.md:100` (Open), `spec.md:137-138` (T-05), `plan.md:66`.

Failure: `promptTouchID(reason)` proves user presence, not which button, device, session or switch the person meant. No AC mentions the binding, so the natural T-05 shape, an IPC returning "authenticated" to the asking window which then calls the change, is replayable across actions: authenticate for one prompt, spend it on "Always allow". The spec also never says what `reason` must contain. A generic reason is what an agent using the app's own tools needs: press Allow synthetically at a chosen moment, put its own text on screen explaining the dialog away, and let the person touch the sensor for what they think is something else. It can summon the dialog repeatedly. Nothing requires the main process to create the exact pending change first, consume the authentication once on it, name the action and device in the reason, allow only one authentication in flight, or cool down after a failure. Grant *revocation* by synthetic click (no authentication, by design) is a small denial-of-service AC-02 should at least name.

The no-sensor case is Open (`spec.md:100`) and owned by no task: T-05 builds windows, nothing spikes authentication. The likely target posture, laptop lid closed on an external display or a Mac mini or Studio with a plain keyboard, is the unverified one. On the brief's facts (Electron 44 evaluates `kSecAccessControlUserPresence`, no biometry pre-check) a password sheet should appear where no sensor serves. But one plausible builder step kills it: Electron's documented pattern gates on `canPromptTouchID()`, which reports Touch ID hardware, so following the example makes "unavailable, nothing changes" permanent on sensorless Macs without the password ever being attempted.

Fix: write the binding into AC-02 and AC-08 (main-process pending action, reason naming action and approved-list device, consumed once, seconds to live, never a reusable yes returned to a renderer, one in flight, failure cooldown). Forbid the `canPromptTouchID()` gate or declare sensorless Macs unsupported in AC-17. Add a spike before T-05: no sensor, lid closed, password offered or not, cancel and failure leaving the store byte-identical.

## [major] R2-5. The only desktop code in the tree implements the store AC-02 was amended to forbid

Files: `spec.md:48` (AC-02), `spec.md:54` (AC-08), `spec.md:135` (T-04), `plan.md:64`, `apps/desktop/src/screenShare/ScreenShareStore.ts:6-10`, `:23-31`, `:34-40`, `:132-143` (untracked draft at review time).

Failure: AC-02 requires a random store key wrapped by `safeStorage`, AES-256-GCM over the contents with purpose and version authenticated, and no storage at all where the system cannot encrypt. The draft seals with `safeStorage` directly (`ScreenShareStore.ts:132-143`) and its header rests the edited-file property on that alone: round 1 finding 7 verbatim. Its schema (`:34-40`) has no wrapped key and no cooldown counts, although AC-08 keeps the counts in the store across restarts. Its I/O seam (`:23-31`) passes text through `seal`/`unseal`, fitting `encryptString`, not the two-layer design; T-04's `screenShareSeal.ts` does not exist. Smaller holes in the same draft: the stored machine key is accepted as two strings, never checked for 32 bytes or a matching pair (`:73-84`), so a mismatch surfaces only as an opaque viewer-side handshake failure; and `recordAudit` and `touchGrant` swallow the save result (`:191-199`, `:213-216`), so a failed write still reads as recorded.

This is a plan finding, not a verdict on uncommitted code. It matters because drafts become T-04. Fix: delete the draft or mark it superseded by AC-02 in its header, put the seal module first in T-04 with its own tests (edited byte, replaced file, foreign machine's file, unwrappable key, `canSeal` false), and test the accepted rollback as a stated limit so nobody later fixes the test instead of the claim.

## [major] R2-6. The threat model contradicts itself about the machine key and about what limits a same-user process

Files: `spec.md:26-29`, `spec.md:50` (AC-04 limit), `plan.md:39`.

Failure: three sentences cannot all be true. The threat model says a same-user process "can run code as the app, read the store and stand in as the host" (`spec.md:27`, on the build facts at `scripts/build-desktop-artifact.ts:1467-1471`). AC-04's limit then says that process "still lacks the machine key" (`spec.md:50`), and the plan's table says it can stand in "without the machine key" (`plan.md:39`). A process executing as the app unseals the store as the app and reads the machine key secret. The sentences describe two attackers, one who only rewrites files and one who executes as the app, never separated, so the weaker claim reads as a property of the whole class and pinned viewers look safe against exactly the adversary they are not safe against.

Same shape in "What still limits it: it cannot pass system authentication through the app's own windows" (`spec.md:27`). The execute-as-app attacker bypasses windows instead of passing them; that limit belongs to the previous bullet's adversary, the agent confined to the app's tools (`spec.md:26`), and as placed it invents a residual defence against the undefended class. And "Trusted: ... the app's own code signature" (`spec.md:28`) sits two lines below the admission that library validation is off in the shipped build, so injected code inherits the signature-based Keychain access that `safeStorage` trust rests on. D-15 (`spec.md:95`) may accept that cost; the Trusted line should not omit it.

Fix: split the bullet into "rewrites this user's files" (passes AC-04, lacks the machine key, pinned viewers refuse it) and "executes as the app" (store and machine key read, no prompt, banner, audit or pin means anything). Move the authentication sentence to the app-tools bullet. Qualify the Trusted line with D-15. No design change; the claims stop promising a middle state that does not exist.

End of part 2 (R2-4 to R2-6). Part 3 is `plan-review-muse-round-2-B3.md`.
