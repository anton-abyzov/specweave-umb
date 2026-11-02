---
increment: 1177-machines-page-explains-itself
title: Machines page explains itself
status: completed
---

# Machines page explains itself

## Problem

Settings > Machines listed only projects with a copy on more than one machine, so most projects were missing and automated check projects sat among the person's own. "Connected" in Machines does not put a machine in the server's fleet, and adding it took a pasted environment ID and a pasted line, even when one app already reached both machines. How to disconnect was spread over several pages.

## Scope

In: project lists on Machines, adding a visible machine without pasting, naming known main machines in the join dialog, tooltips, and the user guide.

Out: a general product tour (needs a decision), Remove machine on the phone, and any release dispatch.

## Acceptance criteria

- [x] AC-01 A machine's row lists all its projects: the person's own first, then collapsed Automated and Archived, using the sidebar's rules; scratch is never listed.
- [x] AC-02 Names, labels and folders line up in one grid at desktop and phone widths with no horizontal overflow, including long Windows paths.
- [x] AC-03 Each role label explains itself on hover, and a shared copy names its other machines.
- [x] AC-04 A machine this app sees but the server does not list offers Add for agents, which adds it with no pasted ID or line; failures say what to do; workers stay a separate choice.
- [x] AC-05 The join dialog offers machines this app knows by name, and asks for an ID only for another machine, saying why it is needed.
- [x] AC-06 The user guide explains the layers, why the ID exists and every way to disconnect.

## Approach

Reuse `projectOrigin` and the archived flag for the lists, and `ArchivedDisclosure` for collapsing. Add for agents runs the existing invite on the other machine and the existing add here, after a confirmation naming the year of management access it grants. Connect lines only: unused, the one-time credential lapses within the hour; redeemed and then failing, a session stays on that machine under Authorized clients. Other machines accept this request only from the desktop app, so a browser tab is pointed to the manual route. The environment ID stays on lines made by hand: it limits a line to one machine, and the main machine need not share a Connect account.

## Tasks

### T-01 Categorized project lists
- AC: AC-01, AC-02, AC-03 | Files: apps/web/src/components/settings/machinesSettings.logic.ts, apps/web/src/components/settings/MachinesSettings.tsx | Test: pnpm exec vp test run apps/web/src/components/settings/machinesSettings.logic.test.ts apps/web/src/components/settings/MachinesSettings.test.tsx

### T-02 Add for agents and named main machines
- AC: AC-04, AC-05 | Files: apps/web/src/studio/fleet.ts, apps/web/src/components/settings/MachinesSettings.tsx, apps/web/src/components/settings/FleetInvite.tsx, apps/web/src/components/settings/StudioFleetConnections.tsx | Test: pnpm exec vp test run apps/web/src/components/settings/FleetInvite.test.tsx apps/web/src/components/settings/StudioFleetConnections.test.tsx

### T-03 Guide and visual check
- AC: AC-02, AC-06 | Files: docs/user/add-a-machine.md, apps/web/tests/machines-page | Test: node apps/web/tests/machines-page/verify.mjs

### T-04 Verify and close 1177
- AC: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06 | Files: none | Test: specweave verify 1177-machines-page-explains-itself
