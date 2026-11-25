<!-- specweave review: reviewer=muse-wonder-full-1.0 model=muse-wonder-full-1.0 family=meta author=claude depth=standard repo=repositories/anton-abyzov/specwithcode base=4712523d6ca3f19f70c1eb57bbccba69eee89395 head=3f9209976638b4a312ccc34295d39fb135349024 at=2026-11-25T17:52:41.385Z -->
# PR review round 2: 1490 screen sharing slice 1 (PR 955, branch `remote-desktop`)
Verdict: ship

Reviewer: Muse Wonder Full 1.0 (Meta) on Muse Code, reviewing Claude Fable 5.2's work. Reviewed commit: `3f9209976638b4a312ccc34295d39fb135349024` in `/Users/anton/.specwithcode/worktrees/specweave-umb/remote-desktop/repositories/anton-abyzov/specwithcode`. Read-only: no source file changed, no commit, no installer, nothing captured a screen. The `sw-review` skill could not be loaded (project skills are refused in this untrusted worktree), so this report follows the round 1 reports' shape.

Counts: 0 blockers, 0 majors, 3 minors. All three minors can follow the merge.

Round 1: F1 to F5, F7 and F8 closed; F6 closed except one stale sentence (N3); Q2 and Q3 closed; Q1 partly closed (N2). The authors' correction to F1 is right, and my round 1 sentence about the relay's 12 opens was wrong (see `pr-review-muse-2-round1.md`).

Findings, one line each:

- [minor] N1. A valid knock that arrives in the last instants of its 5 seconds can be refused by the deadline and still open a relay session for a moment, because the stage stays `waiting` while the knock and the host standing are checked. Key holder only, against itself; can follow.
- [minor] N2. Q1 residue: when the primary environment's entry is missing from the loaded list, `otherMachine` falls back to false, so the settings block acts on this Mac. The system dialog still appears on this Mac and names it; can follow.
- [minor] N3. Two sentences overclaim: `plan.md:75` still counts unfinished handshakes toward the quiet time, and the docs' "nothing they do counts against a device once they stop" does not hold for a path adversary that breaks genuine sessions while a person is being asked. Can follow.

What was attacked and held (detail in `pr-review-muse-2-round1.md` and `pr-review-muse-2-findings-1.md`): the knock (replay, reflection, cross-use as a session or DPoP proof, signing-oracle scope, thumbprint binding, counting before the check, the waiting list, CPU and memory), the changed strike rule in both directions, the seal gap rule and counter order, the in-memory strike, the host proof end arithmetic at window edges, the 60 s recheck, the late-display banner and preload check, the merge of main (1488's RPC methods, MCP tool and routes reach nothing of screen sharing; `noAgentPath.test.ts` is stronger, not weaker), and the docs against the code.

Focused tests run by this reviewer, all passing, 240 tests: `packages/shared/src/screenShareChannel.test.ts`, `packages/shared/src/desktopBootstrapToken.test.ts`, `apps/server/src/auth/personDevice.test.ts`, `apps/server/src/screenShare/` (including the real-socket `ScreenShareHttp.test.ts`), `apps/desktop/src/screenShare/`, and from `apps/web`, `src/components/screenShare/`.

Files: this verdict, `pr-review-muse-2-round1.md` (F1 to F8, Q1 to Q3), `pr-review-muse-2-findings-1.md` (N1 to N3, and attacks that held). All under `/Users/anton/.specwithcode/worktrees/specweave-umb/remote-desktop/.specweave/increments/1490-remote-desktop-see-and-control-another-of-your-machines-from-your-own-devices/reports/`.

Nothing in this review found a way for a screen to be seen, or for sharing to be turned on or a grant added, without what the spec requires. Known proof limits stay as the spec states: capture and the banner's Stop on a signed installed release, the system dialog on a Mac without a Touch ID sensor, and three untested Electron seams (the 60 s recheck timer, the late-display banner, the preload check).
