# Prevent main-process crashes from setTypeOfService and network errors

## Problem

On m4 (`Antons-MacBook-M4MAX.local`, macOS 27.2.1 pending -> installed Nov 22/23, 2026), SpecWithCode desktop `1.0.407` (Electron `44.4.2`, Node `24.21.0`, undici `7.29.1`) displayed a blocking native main-process crash dialog:

```
Uncaught Exception:
Error: setTypeOfService EINVAL
at Socket.setTypeOfService (node:net:913:13)
at writeH1 (node:internal/deps/undici/undici:8021:16)
at Object.write (node:internal/deps/undici/undici:7758:18)
at _resume (node:internal/deps/undici/undici:9691:54)
at resume (node:internal/deps/undici/undici:9624:7)
at Client.<computed> (node:internal/deps/undici/undici:9401:35)
at node:internal/deps/undici/undici:9574:26
at Socket.<anonymous> (node:internal/deps/undici/undici:3342:13)
at Socket.wrapper (node:events:639:12)
at Socket.emit (node:events:514:28)
```

Two layers caused this crash:
1. In Node `24.21.0` / undici `7.29.1`, `writeH1` unconditionally calls `socket.setTypeOfService(request.typeOfService)` (default `0`) without a `try/catch` before writing an HTTP/1.1 request. On macOS/Linux, `Socket.prototype.setTypeOfService` throws synchronously when `setsockopt(IP_TOS/IPV6_TCLASS)` returns an error (such as `EINVAL` on a closing/reset socket or `EBADF` while connecting). Because `writeH1` runs inside a `Socket.emit` callback, the synchronous throw escapes `fetch()`'s Promise rejection and becomes an `uncaughtException`. (While `origin/main` has since bumped Electron to `44.10.1` / Node `24.22.1`, any similar synchronous socket error or undici regression can still crash the main process.)
2. `apps/desktop/src/main.ts` has no `process.on("uncaughtException")` or `process.on("unhandledRejection")` guard in production (only `uncaughtExceptionMonitor` in `DesktopCrashReporter.ts`, which observes without handling). Any escaped network/socket error triggers Electron's default blocking error dialog.
3. Auditing `apps/desktop/src/` also found that `startDesktopAppControlServer` in `apps/desktop/src/app/DesktopAppActivation.ts` removes its `server.once("error", onError)` listener once `"listening"` fires, leaving no persistent `"error"` listener on the `NodeNet.Server` for post-startup socket errors.

## Scope

In:
- Add a main-process `DesktopProcessErrorGuard` module in `apps/desktop/src/electron/DesktopProcessErrorGuard.ts` that:
  1. Wraps `net.Socket.prototype.setTypeOfService` so best-effort TOS/DSCP failures (`EINVAL`, `EBADF`, `ENOTCONN`, `ENOPROTOOPT`, `EOPNOTSUPP`, `ENOTSOCK`) are logged (rate-limited) and ignored instead of throwing synchronously.
  2. Installs `process.on("uncaughtException")` and `process.on("unhandledRejection")` handlers early in `apps/desktop/src/main.ts` (skipped when `STUDIO_DESKTOP_TEST_OFFSCREEN=1` so offscreen test failure assertions remain intact). Non-fatal network/socket errors are logged and recovered without showing a blocking dialog; genuinely fatal non-network uncaught exceptions are logged and exit non-zero (`process.exitCode = 1` + `exit(1)`).
- Attach a persistent `server.on("error", input.onReclaimError)` listener after `"listening"` in `apps/desktop/src/app/DesktopAppActivation.ts`.
- Add unit and regression tests for `DesktopProcessErrorGuard` and `DesktopAppActivation` post-listen server errors.

Out:
- Changing Electron version (already bumped to `44.10.1` / Node `24.22.1` on `origin/main`).
- Silencing fatal non-network programming errors (OOM, corrupted state, startup assertion failures).
- Changes to server-side or renderer-side error handling.

## Acceptance Criteria

- [ ] AC-01: Calling `Socket.prototype.setTypeOfService` when the underlying syscall throws a non-fatal socket errno (`EINVAL`, `EBADF`, `ENOTCONN`, `ENOPROTOOPT`, `EOPNOTSUPP`, `ENOTSOCK`) does not throw after the guard is installed, logs a rate-limited warning, and still delegates normally when no error occurs (and rethrows unrelated non-socket errors).
- [ ] AC-02: Installing the desktop main-process error guard catches non-fatal network/socket errors on `uncaughtException` and `unhandledRejection` (including `setTypeOfService` EINVAL, `ECONNRESET`, `EPIPE`, `ETIMEDOUT`, `ENOTFOUND`, `ECONNREFUSED`, `EHOSTUNREACH`, `ENETUNREACH`, `ECONNABORTED`, `ERR_SOCKET_*`, `UND_ERR_*`, and `TypeError: fetch failed` with a network cause), logs them, and does not exit or show a blocking dialog; fatal non-network `uncaughtException` errors are logged and invoke the fatal exit callback; offscreen test mode (`STUDIO_DESKTOP_TEST_OFFSCREEN=1`) skips installing the guard.
- [ ] AC-03: `startDesktopAppControlServer` in `apps/desktop/src/app/DesktopAppActivation.ts` retains a persistent `"error"` listener on the listening `NodeNet.Server` so post-listen server errors are routed to `onReclaimError` instead of escaping as uncaught exceptions.
- [ ] AC-04: Regression tests in `apps/desktop/src/electron/DesktopProcessErrorGuard.test.ts` and `apps/desktop/src/app/DesktopAppActivation.test.ts` pass, along with desktop typecheck and checks-copy verification.

## Approach

1. Create `repositories/anton-abyzov/specwithcode/apps/desktop/src/electron/DesktopProcessErrorGuard.ts`:
   - `guardSocketSetTypeOfService(options?)`: idempotently wraps `NodeNet.Socket.prototype.setTypeOfService` with `try/catch` for `RECOVERABLE_TOS_ERRNOS` (`EINVAL`, `EBADF`, `ENOTCONN`, `ENOPROTOOPT`, `EOPNOTSUPP`, `ENOTSOCK`), logging with a rate limit and returning `this` on suppressed errors. Returns a disposer for clean testing.
   - `isRecoverableNetworkError(error)`: checks error `code`, `syscall`, `message`, and `cause` chain (bounded depth) for non-fatal network/socket/undici/TLS/DNS errors, including `setTypeOfService` syscall errors.
   - `installDesktopProcessErrorGuards(options?)`: calls `guardSocketSetTypeOfService` and registers `uncaughtException` and `unhandledRejection` listeners on the target process (skipped when `isDesktopOffscreenTest()` is true). Non-fatal network errors log a structured warning and recover. Fatal `uncaughtException` logs the error and calls `onFatalError` (defaulting to `process.exit(1)`). Unhandled rejections that are non-fatal network errors log a warning and recover; non-network unhandled rejections log an error (matching Node's warning behavior without crashing the desktop UI with a modal dialog, while still visible in `DesktopCrashReporter` and logs).
2. Wire `installDesktopProcessErrorGuards()` at the top of `repositories/anton-abyzov/specwithcode/apps/desktop/src/main.ts`, right after the `stdout`/`stderr` `EPIPE` guards and before any network/Electron work.
3. Update `repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopAppActivation.ts` so `listen()` attaches `server.on("error", input.onReclaimError)` inside `onListening` (before removing `onError`), ensuring no gap where an emitted server error has zero listeners.
4. Add focused unit/regression tests in `DesktopProcessErrorGuard.test.ts` and extend `DesktopAppActivation.test.ts`.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01: Treat `Socket.prototype.setTypeOfService` non-fatal socket errnos as best-effort (matching Node's existing Windows behavior) rather than patching undici internals → reversible, clean, works across Node/undici versions.
- D-02: In `uncaughtException`, recover for classified non-fatal network/socket errors and log + exit(1) for fatal non-network errors, while skipping installation when `STUDIO_DESKTOP_TEST_OFFSCREEN=1` → reversible, preserves fail-fast for fatal bugs and offscreen tests while eliminating blocking dialogs for transient network errors.
### Open
- none

## Tasks

### T-01 Add DesktopProcessErrorGuard and wire into desktop main entrypoint
- AC: AC-01, AC-02 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/electron/DesktopProcessErrorGuard.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/main.ts] | Test: pnpm --filter @specweave-studio/desktop test -- src/electron/DesktopProcessErrorGuard.test.ts

### T-02 Keep persistent server error listener in DesktopAppActivation
- AC: AC-03 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopAppActivation.ts] | Test: pnpm --filter @specweave-studio/desktop test -- src/app/DesktopAppActivation.test.ts

### T-03 Add regression tests for setTypeOfService, main-process error guard, and activation server errors
- AC: AC-04 | Files: [repositories/anton-abyzov/specwithcode/apps/desktop/src/electron/DesktopProcessErrorGuard.test.ts, repositories/anton-abyzov/specwithcode/apps/desktop/src/app/DesktopAppActivation.test.ts] | Test: pnpm --filter @specweave-studio/desktop test -- src/electron/DesktopProcessErrorGuard.test.ts src/app/DesktopAppActivation.test.ts
