# T-05 and AC-06: the two-Mac, M4-off check

Recorded on November 24, 2026 on m4, at the owner's request from the M5 thread "0970". Outcome: **Skipped (accepted)**, not Verified.

## What was asked

AC-06: "Tested on the simulator and on LAN with two Macs (M4 off, Minis on); the network gap is reported." T-05 was the manual LAN run plus the simulator check.

## What passed in October

On October 20, 2026, cli@antons-macbook-m4max blocked T-05 with this note: "Simulator fault shots and a live two-server run (real LiveEngine, hub and Minis killed and restarted, no duplicate rows) pass. Two physical Macs with the real M4 off needs the user: M4 is the hub running this lane."

On October 21, 2026, codex@antons-macbook-m4max blocked T-10: "Merged #547 and #552; 351 Swift tests pass on 006ed1a08ba4cd155423e3071a4734373e65e71f; merged review clear. Verify refuses AC-06: physical two-Mac M4-off acceptance remains required; release coordinator owns arranging user check."

The simulator fault shots and the two-server run were not re-read today. The m4 evidence entries for this increment are links into the archive drive, which is not mounted on m4:

- `~/.specwithcode/m4/evidence/0970-message-markdown-20261021` points to `/Volumes/SanDisk APFS/Archive/specwithcode/m4-20261028/evidence/0970-message-markdown-20261021`
- `~/.specwithcode/m4/evidence/0970-handoff-clarity-tests.log` points to `/Volumes/SanDisk APFS/Archive/specwithcode/m4-evidence-2026-11-23/0970-handoff-clarity-tests.log`
- `0970-mobile-readability-20261021` and `0970-continue-comparison-20261021/REPORT.md`, named in the October 21 ledger notes, are not on m4's internal disk. They were probably archived to the same drive.
- No `build/fault-shots` folder from the October 20 lane survives on m4. The ledger records only that the C-01 to C-03 follow-up worktree was removed on October 21.

The October evidence links point to `/Volumes/SanDisk APFS/Archive/specwithcode/`, which is not mounted on m4 (November 24, 2026), so they were not re-read and nothing was copied.

The ledger notes are the only readable record of the October runs on m4 today.

## Why the two-physical-Macs LAN run was not run

The check as written cannot be run against the product as it stands, and the conditions it was written for no longer hold. The citations below were re-checked on app commit `29d788d8cc51b30ec619acdb626ad31bebc10460`, origin/main on the morning of November 24, 2026 (main has moved on since; every citation is pinned to this commit).

1. **LAN is not a route between machines.** `apps/server/src/fleet/fleetOrigin.ts:40-68` (`parseFleetOrigin`) accepts a fleet address only as HTTPS, either a `*.ts.net` tailnet host or a Connect managed endpoint. It refuses plain HTTP at line 51 and returns null for anything else at line 67. `apps/server/src/fleet/fleetTransport.ts:167` applies it to every fleet machine address. A hub therefore cannot reach a second machine, or ask it for a phone code, over LAN; the hub-to-machine link needs Tailscale or Connect. The restriction is on that link, not on the phone: the roster gives the phone a tailnet route of its own (`apps/server/src/fleet/phoneLinks.ts:365-370`) and then appends whatever routes the machine's mint answer offers (`phoneLinks.ts:401-402`), which can include a LAN address (`phoneLinks.test.ts:226-229`). The fleet installer binds the service to loopback by default (`scripts/studio-fleet/install.py:216` `STUDIO_HOST` and `:226` `--host 127.0.0.1`). So the setup AC-06 describes, two Macs linked over LAN alone, cannot be built; a phone paired directly with the hub (not through Connect, see point 3) could still learn a second machine's LAN address, if that machine advertises a reachable one, and reach it on the same Wi-Fi. That path was not tested on physical machines either.

2. **The owner decided not to build a LAN mode.** On October 20, 2026, after this spec was written, the owner decided: "Do not build a same-Wi-Fi or LAN mode unless the user asks again" (SpecWithCode project memory `reference_fleet_phone_permissions.md`, section "iPhone pairing needs Tailscale on the phone", read on November 24, 2026).

3. **The hub is no longer the phone's only way in.** Connect became the primary phone route in increment 1139 (AC-05: "SpecWithCode Connect is the primary connection and recovery path; direct LAN/Tailscale pairing is a fallback"; completed October 29, 2026). On a Connect route the phone never asks a hub for a roster: `apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Fleet.swift:79` returns early when `route.issuer == ConnectAuthorizer.issuer`. The hub roster only serves phones paired directly with the hub, not through Connect.

4. **Related offline-machine behaviour was reworked and tested on newer code**: 1139 (iPhone offline recovery and Connect first, completed October 29, 2026) and 1352 (desktop and web "reconnecting" wording, completed November 15, 2026). Neither re-tested hub-off failover.

5. **An agent-run hub-off run would change live routes.** Running it with scratch servers would need Tailscale Serve entries or Connect tunnels on live machines, which this lane must not touch. M5 is on a phone hotspot (172.20.10.7) with no Tailscale, as reported from the M5 thread. It was not run.

## Shipped evidence

The ledger's SHAs (`118849515e`, `ba13ae6465`, `cc0df3b1ce`, `006ed1a08ba4`) and PR numbers (#493, #500, #547, #552, #560) are from the retired `specwithcode-dev` repository. The commit objects exist in the current clone, but none of them is an ancestor of app commit `29d788d8c`. The same PR numbers in anton-abyzov/specwithcode are unrelated PRs.

The code is in the current repository. `apps/server/src/fleet/phoneLinks.ts`, `apps/server/src/fleet/phoneLinks.test.ts`, `apps/ios/SWCKit/Sources/SWCSync/LiveEngine+Fleet.swift` and `apps/ios/SWCKit/Tests/SWCSyncTests/FleetEngineTests.swift` exist at:

- `v1.0.64` (`1c573f89a`, "SpecWithCode 1.0.64", October 20, 2026)
- `v1.0.418` (`db2a70c09`)
- `v1.0.420` (`bdc54e3ab`)
- app commit `29d788d8c` (origin/main on the morning of November 24, 2026)

The tests that still cover this behaviour are in `FleetEngineTests.swift` at `29d788d8c`: `linksTheRestOfTheFleetThroughOneMachine` (line 121), `unreachableMachineKeepsItsSavedThreadsAsUnknown` (line 198) and `machineOffMidSessionThenBackLeavesNoDuplicates` (line 245). The server side is covered by `apps/server/src/fleet/phoneLinks.test.ts`.

## Fresh test run (November 24, 2026)

`specweave verify` passed (`reports/verify.json` `ok: true`, run at 4:00 PM EST on November 24, 2026) against the app checks copy at commit `29d788d8cc51b30ec619acdb626ad31bebc10460`, run under the heavy-check gate on m4:

- `swift test --no-parallel --package-path apps/ios/SWCKit --filter 'FleetEngineTests|FleetSummariesTests|FleetFixtureTests'`: 40 tests in 5 suites passed, among them `FleetEngineTests` (including the three tests named above) and `FleetSummariesTests`.
- `vp test run src/fleet/phoneLinks.test.ts` in `apps/server`: 23 of 23 tests passed.
- The umbrella's three self-tests (`fleet-project-sync.py --self-test`, `test_handoff_evidence.py`, `timing.py --self-test`) passed, and a check confirmed the copy was at the commit above.

The swift run was limited to the fleet suites with the owner's approval on November 24, 2026 ("yes, do what's recommended"). The full SWCKit suite at the same commit ran 940 tests: every fleet suite passed, and 5 issues failed in two suites outside 0970's code. `AccessRequestMappingTests.accessRequestCardOutcomeText` expects "Allowed on this machine" and "Always on this machine" but gets "the agent's machine". `ReplyStyleTests` (`theLiveEngineSendsAPerKeyChangeAndShowsTheSavedValue`, `theLiveEngineRefusesAServerWithoutPerKeyChanges`) gets "This computer was paired without permission to make changes." These are regressions on app main from later iPhone wording and pairing-permission work and need their own fix. Full log: `~/.specwithcode/m4/scratch/2026-11-24-0970-close/swift-full.log`.

These are unit and in-process tests on the merged code. They do not repeat the October live two-server run, and they do not make AC-06 Verified.

## Status

The physical hub-off behaviour (two real Macs, M4 powered off, the phone still working through the other machine) is still untested on physical machines. AC-06 is recorded as **Skipped (accepted)**, not Verified.

Accepted by Anton Abyzov on November 24, 2026, in the M5 thread "0970": "If it's superseded, record it as skipped with the evidence, the way the closure rules allow." and "once T-05's check passes, or is recorded as superseded with evidence, unblock T-10 and close 0970."
