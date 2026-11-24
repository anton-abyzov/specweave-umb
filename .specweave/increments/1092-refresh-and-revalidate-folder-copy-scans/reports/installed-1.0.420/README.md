# 1092 installed check on SpecWithCode 1.0.420 (M5, November 24, 2026)

**Result:** the released build carries the scan-age, refresh and captured-copy code. Its isolated server runs, and the focused tests pass on the exact release commit. The live copy dialog could not be driven to a scan, because that needs a second paired machine. This is a proof limit, not acceptance.

## Delivery

- PR 882 (and 909, 919) were in the retired `specwithcode-dev` repository, which no longer exists. The code reached `anton-abyzov/specwithcode` through release imports: `HandoffCopyScanFreshness.tsx` in 1.0.102, `sourceSnapshot.ts` in 1.0.116, `sourceCaptureFilesystem.ts` in 1.0.126.
- `git ls-tree -r v1.0.420` lists the T-01, T-02 and T-12 files. `v1.0.420` is `bdc54e3ab280b900bcd10e66d7433508efdaadca`. No new release was needed.

## Installed build

- `/Applications/SpecWithCode.app` on M5 is `specwithcode v1.0.420`.
- Its `app.asar` contains the shipped freshness strings: "Measured earlier" (1), "Compare again before copying" (9), "Nothing changed since then, so your choices stay" (1).
- Isolated server: `specwithcode serve --base-dir ~/.specwithcode/m5/scratch/2026-11-24-1092-installed/base --port 47392 --host 127.0.0.1`, paired with a fresh token and opened in headless Chromium. Screenshot: `isolated-1.0.420-overview.png` (one machine, 1.0.420 current). The server was stopped by its own PID afterwards. The live app and its database were not touched.

## Tests on the release commit

`specwithcode checks run -- node node_modules/vite-plus/bin/vp test run` was run in the verification copy `~/.specwithcode/verify/specwithcode`, at `bdc54e3ab280b900bcd10e66d7433508efdaadca`, on these files:

- `sourceSnapshot.test.ts`
- `sourceCaptureFilesystem.test.ts`
- `twoServer.snapshot.test.ts`
- `twoServer.verify.test.ts`
- `manifest.test.ts`
- `sourceService.test.ts`
- `HandoffCopyScanFreshness.test.tsx`

Result: 7 files and 100 tests passed, exit 0. The log is `tests-v1.0.420.log`.

## Proof limits

- The copy dialog's scan, Refresh, stale-refusal and captured-copy states need a destination machine. An isolated server can only add one over Tailscale or Connect, and that would publish it, so this check did not do it. Those states are covered by the two-server tests above, which run in-process. That is not installed UI proof.
- AC-06, the M4 to Ministorm migration, is not covered here.
