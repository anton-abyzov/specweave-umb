---
title: "Cross-machine control from M5: security analysis"
thread: "thread:delegated-task:command%3Amcp%3Ad8a8d4dd-ad11-4f90-8fc4-8d336c844cbc%3Adelegate-task%3Across-machine-control-security-20261113"
threadTitle: "Cross-machine control security review"
savedAt: "2026-11-13T22:10:22.356Z"
date: November 13, 2026
code: anton-abyzov/specwithcode origin/main c0d20a018
status: analysis done, adversarial review pending (Muse Wonder, max)
---

# Cross-machine control from M5: security analysis

## Answer

Not a bypass of M5's machine grants. The M5 app is not acting with M5's authority. It is a person client signed in to Anton's SpecWithCode Connect account, holding its own session on M4's server. M4 then moves its project with M4's own grants (linux-mini and m1 allowed m4). The "m5 -> m4 Not set up" line only governs agents on M5 starting work on M4.

It is a real design weakness, though: the Connect account collapses machine boundaries for people. Any device signed in to the account gets terminal, filesystem read/write, source control and settings on every machine of the account, with no approval on the machine that owns the data. The UI implies a per-machine boundary that does not exist for person clients.

## Trust model (as built)

1. Person clients: the Connect account. M4 mints a `cloud-connect` session after checking a relay-signed proof with `sub == linkedCloudUserId`, audience `studio-env:<m4>`, scope `environment:connect`, DPoP key bound, replay guarded (`apps/server/src/cloud/CloudLink.ts:1785-1830`). The session gets `AuthStandardClientScopes` (`packages/contracts/src/auth.ts:224-238`): orchestration operate, settings write, terminal operate, filesystem read/write, source control write. Not `access:write`.
2. Agents and machine-to-machine: fleet work grants per direction, worker-issued DPoP keys (#1100, principal guard 1.0.268). The handoff peer API only admits a paired machine's worker credential naming the same source (`apps/server/src/handoff/handoffRoute.ts:1-5`).
3. The move dialog lists the source machine's fleet (machines that granted m4), not the viewing device's (`apps/web/src/components/studio/HandoffAccountMachines.tsx:44-80`, `apps/web/src/studio/handoffAccountMachines.ts`).
4. Per-machine kill switch exists only in team rules: `reach.connect = false` refuses Connect person sessions on that machine (`packages/shared/src/teamRules.ts:818-845`, `apps/server/src/teamRules/TeamRulesReach.ts`).

## Findings

| # | Finding | Severity |
|---|---|---|
| F-1 | Same Connect account = owner-equivalent on every account machine (terminal + filesystem). A stolen Connect sign-in or any compromised signed-in device controls all machines. No per-device approval on the owning machine. | High (design) |
| F-2 | Settings > Machines shows "m5 -> m4 Not set up" while M5's app can fully drive M4. The dialog never says which device is acting and on whose authority. | Medium (misleading UI on a security boundary) |
| F-3 | `machineHandoff.copyOffer` does not check the destination against the source's fleet grants; the UI filter is the only check (`apps/server/src/fleet/MachineHandoff.ts:530-570`). Not an escalation for person clients (they already have terminal), but a gap for defence in depth. | Low |
| F-4 | Secret files need `access:write` (`packages/contracts/src/clientRpcPermissions.ts:272-274`), which Connect sessions lack. Good, but nominal: terminal operate can read `.env` directly. | Info |
| F-5 | Copy start is called on the destination by the client with an offer bearer token; the source serves any holder of that bearer (`apps/server/src/fleet/folderTransfer/sourceRoutes.ts:45-60`). Token handling needs review. | Review |

## Recommended fix

1. UI (small): dialog states the actor: "Acting on m4 from this device (your SpecWithCode Connect account). m4 moves its project with its own permissions." Settings > Machines adds a third line per machine: "Devices signed in to your account can control this machine" with the switch, wired to `reach.connect`.
2. Server: `copyOffer` and handoff `prepare` refuse destinations the source has no grant for (`machine_not_authorized`).
3. Auth change, needs Anton: new-device approval. A Connect session from an unseen DPoP key gets read-only until approved on that machine or on an already-approved device; secrets, terminal and moves need an approved device.
