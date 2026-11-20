# Places checked: tasks, machines, assistants and projects

Increment 1352. Repository `anton-abyzov/specwithcode`, branch `overview-tasks-machines`.

"Short name" means the machine's nickname in its color (`useMachineIdentities()` in `apps/web/src/studio/machineIdentity.ts`), with the host label as the tooltip. "Host label" means the saved connection's raw name ("ministorm", "Anton's MacBook M4MAX").

## What was wrong

| Symptom | Cause | Fix |
|---|---|---|
| **Needs you** stays on "Reading your chats…" | `allEnvironmentShellsBootstrappedAtom` held the page for every machine in `connecting` or `backoff`. A saved machine that never answers cycles between the two forever. | `apps/web/src/state/shellBootstrap.ts`: a machine holds the page for 2 attempts only, and the answer latches once true. Overview also shows this machine's chats as soon as its own shell is live. |
| "ministorm" shown, not "linux-mini" | Overview printed `environment.label` (the host label). linux-mini's host label is ministorm. | Overview reads the machine identity (nickname, color, icon). |
| Second "Anton's MacBook Pro · Reconnecting · 0 projects" | A saved connection to a machine that does not answer. It has no server config, so its counts were printed as 0. | The row reads "Can’t reach it · retrying" and "Chats and projects not counted". |
| Status chips show raw shell commands | The chip printed `activeWork.label`, which is the command's first line. | The server sends `activeWork.kind`; the chip says "Running a command · 12m" and keeps the command for the tooltip. Older servers get the same words from the fixed labels. |

## Web and desktop (one codebase)

| Place | File | Before | Now |
|---|---|---|---|
| Overview chat rows (Needs you, Working, Recent) | `apps/web/src/components/studio/OverviewRows.tsx` `ChatRow` | host label, raw command chip | short name in color, status in words |
| Overview project rows | `OverviewRows.tsx` `ProjectRow` | host labels | short names in color |
| Overview Machines list | `OverviewRows.tsx` `MachineRow`, `apps/web/src/studio/overviewMachines.ts` | host label, "Reconnecting · 0 projects" | icon in color, state, activity, version |
| Overview side column order | `apps/web/src/components/studio/StudioOverview.tsx` | Percy, Projects, Machines | Projects, Personal assistant, Machines |
| Overview stale notice and summary | `StudioOverview.tsx` | host label | short name, plus "still reading m5" |
| Capacity fleet card | `apps/web/src/components/studio/CapacityFleet.tsx` (fed by `StudioOverview.tsx`) | host label | short name |
| Slow request notice | `apps/web/src/components/SlowRpcRequestToastCoordinator.tsx` | host label | short name |
| Provider updates list | `apps/web/src/components/ProviderUpdatesAction.tsx` | host label | short name |
| Settings > Machines remote control and "Let this machine manage…" prompt | `apps/web/src/components/settings/MachinesSettings.tsx` | host label | short name |
| Sidebar chat rows, project list | `apps/web/src/components/studio/shell/StudioSidebar.tsx`, `SidebarProjectList.tsx`, `ThreadsPane.tsx` | short name in color | unchanged (the reference) |
| Settings > Machines cards | `MachinesSettings.tsx` | short name, color, host label in details | unchanged |
| Runs on menu under the message box | `apps/web/src/components/BranchToolbar.tsx`, `chat/logicalProjectEnvironments.ts` | short name | unchanged |
| Settings scope pickers, model and provider panels, fleet connections, handoff menus | `apps/web/src/components/settings/useNamedEnvironments.ts` users | short name | unchanged |

Left as they are, on purpose:

| Place | File | Why |
|---|---|---|
| Sidebar order (Overview, Percy rows, Design, Projects, Chats) | `StudioSidebar.tsx:1000-1184` | Decision D-02: Percy is pinned navigation there, not a section competing with projects. |
| Raw step text inside an open thread | `apps/web/src/components/chat/MessagesTimeline.tsx`, `apps/web/src/threadTiming.ts` | Decision D-04: inside the thread the command is the detail you opened it for. |
| Host label in ThreadsPane tooltip | `ThreadsPane.tsx` | It is the full-name tooltip. |
| Host label in pairing and sign-in dialogs, device hosts, scheduled tasks | `settings/DeviceHostsSettings.tsx`, `settings/ScheduledTasksSettings.tsx` | They name a computer before or outside a nickname (pairing has none yet). Not changed in this PR. |

## iPhone app (not changed in this PR)

Read on linux-mini; no Swift toolchain here, so nothing was built.

| Place | File | State |
|---|---|---|
| Drawer and sidebar order | `apps/ios/SWCKit/.../DrawerView.swift:28-31`, `SidebarView.swift:184-187` | Percy, Projects, Recents, Machines. Kept per D-02. |
| Machine nickname decoding | `SWCWire/Settings.swift:75-84` `MachineNicknameEntry` | Decodes name and updatedAt only; drops color, short and icon, so rows cannot wear the machine color. |
| Host label shown raw | `ProjectOverviewView.swift:38`, `MachineViews.swift:240-246`, `PairMachineView.swift:30,160` | Still the host label. |
| Raw command in status | `ShellSummaries.swift:584`, shown by `ThreadInfoSheet.swift:57-60` and the overview note at `:201` | Still the command's first line. The server now sends `activeWork.kind`, so the phone can use the same words. |
| "Reading your chats…" | none | No equivalent; `LiveEngine.swift:542` has a 15 s deadline. |

## Checks

- `apps/web`: `StudioOverview.test.tsx` 38, `overviewMachines.test.ts` 7, `overviewModel.test.ts` 28, `shellBootstrap.test.ts` 5, `i18n.test.ts` 321; the wider run of `src/components/studio`, `src/state`, settings and toolbar tests: 2,045 pass.
- `packages/client-runtime` state tests 953, `packages/shared` run health 49, `packages/contracts` orchestrationV2 53.
- Headless page check `apps/web/tests/overview-1249/verify.mjs`: 115 checks pass at 1440, 1280, 1024 and phone widths, light and dark.
- Screenshots: `/srv/specwithcode/ministorm/scratch/overview-1352/evidence/`.
