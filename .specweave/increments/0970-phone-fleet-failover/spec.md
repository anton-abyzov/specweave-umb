# Phone keeps working when the main machine is off

## Problem

The iPhone app (apps/ios, com.specwithcode.ios) pairs with one Mac and dials it directly. When M4 is closed, the phone has nothing to talk to, even though Minis may be running the same project. The user wants the phone paired once with the main machine and still working when it is off.

## Scope

In: the phone learning the fleet roster from M4 at pairing; each paired machine minting a scoped phone token on M4's request; the home screen merging projects by logicalProjectId with the owning machine shown; offline badges and "Continue on <machine>"; revocation from any machine revoking on all; handoff badges and actions after 0967 merges.

Out: the Expo app apps/mobile unless it still ships; deploying the Connect relay (#444, #469); adding Tailscale to the phone.

## Acceptance Criteria

- [ ] AC-01: Pairing the phone with M4 also gives it the endpoints of every machine paired with M4, and each of those machines mints a phone token scoped to the phone, on M4's request, without the user pairing again.
- [ ] AC-02: The home screen merges a logical project across machines into one row, showing which machine owns each thread.
- [ ] AC-03: When a machine is unreachable, its threads show an offline badge and the project offers "Continue on <machine>" for any reachable member.
- [ ] AC-04: Revoking the phone on any machine revokes it on all of them.
- [ ] AC-05: After 0967 merges: "Handoff ready" badges and "Continue here on <machine>" appear on the phone.
- [ ] AC-06: Tested on the simulator and on LAN with two Macs (M4 off, Minis on); the network gap is reported.
- [ ] AC-07: Each thread row on the phone shows its machine by nickname: "M4" when it lives and runs on one machine, "M4 → Minis" when it lives on M4 and runs on Minis. The names come from 0967's ownerMachineId, executionMachineId and executionState through 0966's machineNickname helper.
- [ ] AC-08: The threads of an unreachable machine stay listed with "Unknown · last seen <time>"; they are never hidden and the list never goes empty because one machine is out.
- [ ] AC-09: The phone can view each machine's orchestrator separately, and a message sent from that view goes only to that machine's coordinator. "Continue on <machine>" runs 0967's handoff with its per-thread preflight result and never runs from switching the view.
- [ ] AC-10: Fault tests with simulator screenshots: M4 goes off mid-session and comes back (the phone reconnects with no duplicate rows), and Minis goes off while its orchestrator is being viewed.

## Approach

apps/ios/SWCKit/Sources/SWCTransport: MachinePairing.swift, MachineConnection.swift, EnvironmentDescriptor.swift, ConnectConfig.swift; SWCSync Connect.swift (#445). Server side: a fleet roster endpoint for paired phones, and a token mint request between paired machines. The network route is the real limit: off the home network the phone needs Tailscale or the Connect relay (#444, #469 are open), so this increment works on LAN and with Tailscale and reports the gap.

## Decisions

### Asked

- Reported to the user: the phone needs Tailscale or the relay to work while M4 is off and away from home.

### Defaulted

- D-01: Native iOS only; the Expo app is out of scope unless it still ships.
- D-02: Tokens are per machine and scoped to the phone, never shared between machines.
- D-03: No releases from this lane (lead, October 20, 2026).

## Tasks

### T-01 Fleet roster and token mint
- AC: AC-01, AC-04 | Files: server pairing, fleet wire | Test: server tests

### T-02 iOS multi-machine connections
- AC: AC-01 | Files: MachinePairing.swift, MachineConnection.swift | Test: swift tests

### T-03 Merged home screen and offline badges
- AC: AC-02, AC-03 | Files: SWCFeatures home | Test: swift tests, simulator screenshots

### T-04 Handoff badges (after 0967)
- AC: AC-05 | Files: SWCFeatures chat | Test: simulator screenshots

### T-05 LAN and simulator verification
- AC: AC-06 | Files: none | Test: manual LAN run, simulator

### T-06 Machine nickname on thread rows
- AC: AC-07 | Files: SWCFeatures home, SWCSync thread model | Test: swift tests, simulator screenshots

### T-07 Unreachable machine threads stay listed
- AC: AC-08 | Files: SWCSync, SWCFeatures home | Test: swift tests

### T-08 Per-machine orchestrator view and send routing
- AC: AC-09 | Files: SWCFeatures orchestrator, SWCSync | Test: swift tests, simulator screenshots

### T-09 Fault tests
- AC: AC-10 | Files: test harness only | Test: simulator screenshots with M4 off and back, Minis off while viewed

### T-10 Verify and close 0970
- AC: all | Files: none | Test: specweave verify, fresh-context review, specweave complete
