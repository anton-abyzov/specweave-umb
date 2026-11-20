# Windows code entry on 1.0.398

On November 19, 2026, the owner reported 1.0.398 on the Windows PC and the Mac it joined. On the Mac, the owner's screenshot showed the Windows machine as reachable through SpecWithCode Connect. The Mac's app still displayed “Connecting…”. The green work-grant row allowed the Mac's agents to run work on Windows. The reverse work-grant row showed “Not set up”.

On Windows, the owner read back the Mac's entry under **Who can work here**. The grant included all projects, all sign-ins and routine management, up to full access. The owner then reported entering the Mac's device code on Windows and asked us to finish. The code was never collected.

A fresh unauthenticated environment-descriptor request from a third machine returned HTTP 200 and identified the same Windows server at version 1.0.398. That verifies the public route and server version. The screenshot predates code entry. Neither it nor the descriptor shows whether the Mac's window established a session afterward. The earlier two-machine photos in the increment are from 1.0.386. The original 1.0.398 screenshot stays in the private thread attachment.

## Card behavior at the release tag

The agent grant, device approval and app connection have separate records. The machine card builds its Connect button from saved direct HTTP origins. A saved Connect relay route has no direct origin, so the card can offer Connect again even while the window already has that route. This explains the extra control. The screenshot alone cannot establish why the window was still connecting. The reverse work-grant button requires a connected window and a loaded grants snapshot.

Source at tag `v1.0.398`: `apps/web/src/studio/fleetAutoConnect.ts` (`savedRouteOrigins`, `fleetMachineSaved`), `packages/client-runtime/src/connection/routes.ts` (`routeHttpBaseUrl`) and `apps/web/src/components/settings/machinesSettings.logic.ts` (`buildMachineRows`, `canAllowBack`).

Windows recorded M5's approval on November 19, 2026 at 11:34:07 PM EST (November 20 at 04:34:07 UTC). The Windows worker confirmed the approved device with the bundled CLI. A worker on M5 also contacted the Windows evidence thread successfully, confirming the work grant in that direction.

The corrected Windows query found no recorded Connect WebSocket timestamp for the approved device. The query alone left the desktop session unconfirmed.

## Desktop connection confirmed on M5

On November 20, 2026, Anton supplied a screenshot from M5's saved connections after entering the code on Windows. The **win** row reads **SpecWithCode Connect · Connected** with **Connect from this device** switched on. That confirms M5's desktop connected to Windows. The **Update status unavailable** message belongs to the separate Updates panel. The screenshot stays in the private thread.

The time of the transition from “Connecting…” to “Connected” and the wording of the join prompts are unverified.
