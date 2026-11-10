# Keep the app alive when memory runs out

## Problem

On November 2, 2026 at 18:47 EST Ministorm ran out of memory while an agent worker ran `vp build` and `tsc --noEmit` together (`tsc` 4.8 GB, the build's `node` 3.1 GB) on top of Chrome (7.3 GB), two LXD VMs (3.4 GB) and swap at 252 kB free.

The kernel killed the SpecWithCode window first, not the compile. The renderer scored 316 (adjust 300) and `tsc` 311 (adjust 200, inherited from the user manager). The window then stayed dead: Electron reports a kernel kill as reason `killed`, and `render-process-gone` recovers only `crashed`, `oom` and `abnormal-exit`, so the journal shows `recovering: false`. Before the kill the machine was thrashing (252 MB/s page-in, 2,790 major faults/s in the 18:40-18:50 sysstat sample). This machine has no systemd-oomd.

## Scope

In: Linux victim ordering for processes the service starts, an early memory guard, window recovery after a kernel kill. Out: macOS memory handling (no kernel OOM killer of this kind; m4 logs are not readable from here), limiting how many builds agents run, and the linked-memory saturation that PR #1229 already fixed.

## Acceptance Criteria

- [x] AC-01: On Linux, every process started below the service, except apps the user opened, gets `oom_score_adj` 800 within one scan, so a kernel kill takes agent work before the app window (300) or the service (200). The service itself and the relay tunnel keep theirs.
- [x] AC-02: With memory critical (available at most 5% and swap at most 10% free, or available at most 10% and full memory pressure at least 30), the guard ends the largest known build (tsc, vite, vitest, cargo and similar, judged by the program or the script it runs, never its other arguments) of at least 1 GiB that sits below a direct child of the service, SIGTERM then SIGKILL after 5 seconds, at most once per 30 seconds. It never ends the service, a direct child, an unrecognised process such as an agent harness at any depth, an app the user opened through the external launcher, or anything outside the service's tree. A process it may not signal, or one that survived, does not stop it trying the next.
- [x] AC-03: With memory not critical, or no qualifying process, the guard ends nothing.
- [x] AC-04: A window whose renderer the kernel killed (reason `killed`) reloads itself within the existing bounded recovery limit.
- [x] AC-05: The guard is a no-op on macOS and Windows, and `STUDIO_MEMORY_GUARD=off` turns it off. (Checked by reading the `layer` branch in `MemoryGuard.ts`; no test covers it.)

## Approach

`apps/server/src/resourceTelemetry/MemoryGuard.ts`: pure parsers and decisions (`/proc/meminfo`, `/proc/pressure/memory`, `/proc/<pid>/stat`), one `runMemoryGuardPass`, and a scoped layer in `layerResourceDiagnostics` reading meminfo every 5 s and scanning the process tree every 15 s or when critical. `apps/desktop/src/window/DesktopWindow.ts`: add `killed` to the recoverable reasons.

Rejected: a systemd `MemoryMax` on the unit (the agent tools share the service's cgroup, so a cap throttles or kills the service with them). Raising the whole unit's `OOMScoreAdjust` (the small service would then die before anything else at the same adjust once its children have gone). Depending on systemd-oomd (not installed here).

Risk: a large known build in a thread's terminal can be ended. Accepted: the kernel would otherwise pick it or the window, and only after minutes of thrashing. Unknown large processes are left to the kernel, marked first; the guard then does not prevent thrashing for them.

## Decisions

### Asked
- none
### Defaulted (change any before sw-do)
- D-01 The guard ends the largest agent-started process at critical memory, without a settings switch → yes, with `STUDIO_MEMORY_GUARD=off` as the off switch (reversible).
### Open
- none

## Tasks

### T-01 Window reloads after a kernel kill
- AC: AC-04 | Files: apps/desktop/src/window/DesktopWindow.ts, apps/desktop/src/window/DesktopWindow.test.ts | Test: pnpm exec vp test run apps/desktop/src/window/DesktopWindow.test.ts

### T-02 Memory guard and victim ordering
- AC: AC-01, AC-02, AC-03, AC-05 | Files: apps/server/src/resourceTelemetry/MemoryGuard.ts, apps/server/src/resourceTelemetry/MemoryGuard.test.ts, apps/server/src/server.ts | Test: pnpm exec vp test run apps/server/src/resourceTelemetry/MemoryGuard.test.ts

### T-03 Verify and close 1261
- AC: AC-01, AC-02, AC-03, AC-04, AC-05 | Files: none | Test: specweave verify 1261-keep-the-app-alive-when-memory-runs-out
