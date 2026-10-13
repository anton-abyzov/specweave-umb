# Desktop 1.0.7 live evidence

Observed read-only at **2026-10-13 05:12:19 UTC**. No app, service, installer, authentication, provider, browser or UI action was performed. The active guarded service installer was left untouched.

## Installed and running desktop

- Main process **PID 5765**, parent PID 1, started **2026-10-13 04:53:01 UTC**; executable `/Applications/SpecWithCode.app/Contents/MacOS/SpecWithCode`. It remained alive at observation, elapsed 19m18s. `lsof` confirmed this process has the installed `Contents/Resources/app.asar` open.
- `/Applications/SpecWithCode.app/Contents/Info.plist`: `CFBundleShortVersionString = 1.0.7`, `CFBundleVersion = 1.0.7`, `CFBundleIdentifier = com.specweave.studio`.
- The installed ASAR's embedded `package.json` independently reports `version = 1.0.7`, `studioBuild.signed = false`. The ASAR is 108,827,132 bytes; its filesystem change timestamp was **2026-10-13 03:49:51.742413 UTC**, before the current process started.

| File | SHA-256 |
|---|---|
| `Contents/Info.plist` | `0e066eabb7b91ab30e7f3df691816fe0ca45528cef39fc857476730786844eee` |
| `Contents/Resources/app.asar` | `d4c1981b7bfe072f65b402f00e8e96a7a1315937841d9399ce8f4d09d647e137` |

These are hashes of the named installed files, not a synthetic whole-bundle hash. No further desktop 1.0.6-to-1.0.7 swap is necessary.

## External M4 attachment

The existing desktop trace `/Users/antonabyzov/.specweave-studio/userdata/logs/desktop.trace.ndjson` records a successful `desktop.bootstrap` event at **2026-10-13 04:53:12.595213 UTC**: `bootstrap attached to the running Studio server`, PID 66041, origin `http://127.0.0.1:8319/`, base directory `/Users/antonabyzov/.specweave-studio/m4`, server version 1.0.5, `serviceManaged = false`. This proves attachment at desktop startup; it does not claim the service's current version or the current installer's outcome.

In reviewed release source `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f`, `apps/desktop/src/app/DesktopApp.ts:216-254` discovers and attaches that existing server, then returns before starting a managed primary backend. `apps/desktop/src/updates/DesktopUpdates.ts:790-806` stops only managed pool instances before desktop installation. The external M4 server is outside that pool.

The standard desktop update path is `desktopBridge.checkForUpdate()`, `downloadUpdate()`, then version-bound `installUpdate({ expectedVersion })`. `ElectronMacSwapUpdater.ts` checks ZIP SHA-512, bundle ID and version; `macSwapInstall.ts` waits for app exit, swaps with rollback on a failed move, then relaunches. This path was inspected, not invoked.

Desktop installation/running proof is separate from guarded server-update success and from real Google consent, grants or Calendar/Gmail/Drive reads. Those remain owned by the coordinator's live verification.
