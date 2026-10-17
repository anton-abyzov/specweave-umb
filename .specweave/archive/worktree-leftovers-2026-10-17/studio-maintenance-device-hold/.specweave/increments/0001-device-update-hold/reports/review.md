# Review: 0001 Device update hold

Verdict: ship · risk: low · 2 files · 0 findings

Reviewer context: independent fresh subagent; no implementation edits. Reviewed the final uncommitted SpecWithCode lifecycle diff against base `512fb42f9deb10ed8997f32a6cff36275443aa69` on `codex/0889-device-update-hold`.

## Scope and result

No actionable correctness, security, portability, or scoped acceptance-criteria findings survived review.

- The shared optional hold reaches the host through `apps/server/src/server.ts:737`, the device layer at `server.ts:422`, and `apps/server/src/device/LocalDeviceHost.ts:240`. Its existing view includes the install gate.
- Foreground starts refuse promptly. The local process paths use either the guarded runner at `LocalDeviceHost.ts:252` or a direct pre-spawn hold check at `LocalDeviceHost.ts:419` and `LocalDeviceHost.ts:592`. Cached ready endpoints also use the guarded runner; daemon teardown remains permitted.
- The supervisor waits outside the lifecycle lock at `LocalDeviceHost.ts:508`, rechecks hub identity under the lock at `LocalDeviceHost.ts:512`, and retries after a hold acquired during spawn preparation. Replacement publication is protected from interruption at `LocalDeviceHost.ts:515`.
- Supervisors belong to the host scope at `LocalDeviceHost.ts:519` and `LocalDeviceHost.ts:707`. Stop clears the current host under the same lock at `LocalDeviceHost.ts:854`; stale supervisors cannot resurrect it after release. Direct scope closure while paused and explicit stop are both covered by the new tests. No persisted device settings are changed.

## Verification evidence

Final source hashes were independently read back after the parent confirmed the tree stable:

| File | SHA-256 |
| --- | --- |
| `apps/server/src/device/LocalDeviceHost.ts` | `d043ba881a3cfa1eb32aed1b03671021e963072a0d8837785cba4c34c19dcf2f` |
| `apps/server/src/device/LocalDeviceHost.test.ts` | `98e17bd8e93d69a497b25b61b190a814d536e5ae145fb0e36790df881130204d` |

The parent supplied successful Node 22.20.0 command results. This reviewer read the retained logs and verified their hashes:

- Focused run: `node node_modules/vite-plus/bin/vp test run apps/server/src/device/LocalDeviceHost.test.ts apps/server/src/device/DeviceService.test.ts apps/server/src/serviceUpdate/ServiceUpdateHold.test.ts` — 3 files, 65 tests passed. Log: `/Users/antonabyzov/Projects/research/studio-copilot-2026-10-09/current-20261016/device-hold-focused-tests.log`; SHA-256 `6e07079b425ebcc4956344622d45bbe4830301c26e1e67e727057a029db18458`.
- Production server build: `node apps/server/scripts/cli.ts build` — parent-confirmed exit 0; tsdown ran. The absent web bundle was intentionally skipped for this backend-only change. Log: `/Users/antonabyzov/Projects/research/studio-copilot-2026-10-09/current-20261016/device-hold-server-build.log`; SHA-256 `4f01cab5efbdce38e2e215a5acbede24481d8de515be9a48e7b51a17f38525a4`.
- Independent `git diff --check` passed. SpecWeave registry verification returned 3.0.22; the older global 3.0.19 was not used for mutations.

This verdict covers the two changed files and their runtime wiring. The adjacent standalone DeviceService tool-install methods are unchanged and outside this narrow lifecycle repair. No live installation, provider, account, device, database, or browser action was performed; source verification does not establish installed-runtime recovery.

Nits: none.
