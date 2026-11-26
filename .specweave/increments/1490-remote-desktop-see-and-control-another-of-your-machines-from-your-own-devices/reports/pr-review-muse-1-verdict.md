# PR review: 1490 screen sharing slice 1 (PR 955, branch `remote-desktop`)
Verdict: fix first

Reviewer: Muse Wonder Full 1.0 (Meta) on Muse Code, reviewing Claude Fable 5.2's work. Reviewed commit: `9ae00861f335e5161a9179bdf521137bd019905c` in `repositories/anton-abyzov/specwithcode`. Read-only: no source file changed, no commit, no installer, nothing captured a screen. The `sw-review` skill could not be loaded (project skills are refused in this untrusted worktree), so this report follows the round 1 and round 2 reports' shape.

Counts: 0 blockers, 1 major, 7 minors, plus 3 questions (in `pr-review-muse-1-findings-3.md`).

Findings, one line each:

- [major] F1. Handshakes that fail before a proof count against the device's cooldown, so a replayed WebSocket ticket can silence a real device for 10 minutes at a time.
- [minor] F2. A frame sealed before Stop can still be sent after the banner is hidden (`sendSealed` never re-checks that the session is current).
- [minor] F3. Failed store writes are swallowed at three call sites: `addGrant`, `touchGrant`, and every strike in `addStrike`.
- [minor] F4. The relay's size bounds are checked only after a whole WebSocket message is read; no smaller `maxPayload` is set anywhere, so the `ws` default of 100 MB is the real bound.
- [minor] F5. AC-16's behaviour half is not in the reviewed commit: the real-socket test the round 2 answers table names landed afterwards (`228569a06`, not reviewed), and the committed test still asserts source-text positions.
- [minor] F6. Docs and comments overclaim in four places: the browser-tab viewer's served-code limit is missing from user docs, `noAgentPath.test.ts` "fails if one is added" is unconditional, `plan.md:39` keeps the R2-6 merged same-user row, and the wire and record number spaces do share values 1 and 2.
- [minor] F7. A launch host proof's standing can outlive the proof by up to one 10-minute window, and a live session is never rechecked after the viewer opens.
- [minor] F8. "View screen" is shown on capability alone; AC-15 also requires this device to be approved there (the server still enforces it, so the cost is a refused click).

What holds up (checked, no finding): the sealed channel's cryptography as used (transcript binding, commit and reveal, directional keys, strict counters, DPoP separation in both directions), the person-device and own-app guards, the target-side first-use record, the authentication binding, the banner and audit ordering in `goLive`, and the lock checks around capture. Focused tests run by this reviewer, all passing: 220 tests across `packages/shared/src/screenShareChannel.test.ts`, `packages/shared/src/desktopBootstrapToken.test.ts`, `apps/server/src/auth/personDevice.test.ts`, `apps/server/src/screenShare/` (relay and no-agent-path; the Http test was excluded because it is not part of the reviewed commit), `apps/desktop/src/screenShare/` and `apps/web/src/components/screenShare/`.

Files: this verdict, `pr-review-muse-1-round2.md` (the round 2 re-attack table), `pr-review-muse-1-findings-1.md` (F1, F2), `pr-review-muse-1-findings-2.md` (F3 to F5), `pr-review-muse-1-findings-3.md` (F6 to F8, test notes, questions). All under `.specweave/increments/1490-remote-desktop-see-and-control-another-of-your-machines-from-your-own-devices/reports/`.

Nothing in this review found a way for a screen to be seen, or for sharing to be turned on or a grant added, without what the spec requires. The verdict is `fix first` because of the one major: an adversary the threat model names (one who can replay a ticket) can keep a legitimate device from ever reaching the prompt, and the fix is small.
