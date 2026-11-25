# 1478 closing review

GPT-6.2 Sol, on m4, compared each acceptance criterion with SpecWithCode `origin/main` at `b12c354e7`. PRs #909, #910, #911, #912, #936 and #938 are all on `main`.

- **Met (9):** AC-03, 05, 06, 07, 09, 10, 14, 15, 16.
- **Partly (7):** AC-01, 02, 08, 11, 12, 13, 17. In each case the AC wording claimed more than the code does; no code was missing. The reviewer's replacement sentences are applied in umbrella commit `36a425df3`.
- **Skipped:** AC-04 (T-09), follow-up E-1.

Review thread: "Review: relay link PR, round 6 (rerun)" on m4, run 4, verdict "fix first" for wording only, now fixed.

## Verify on M5

Two `specweave verify` runs on M5, November 25, 2026:

- **Server suite:** run 1 passed all 6 shards, 20,310 tests. In run 2, `src/terminal/elevatedRun.test.ts` timed out once on SIGTERM cleanup. That test is outside 1478's files and passed in run 1.
- **Tooling gaps:** the system Python has no PyYAML and there is no `pnpm` on PATH. A scratch venv and a corepack shim fix both.
- **`verify:pr` cannot pass on M5:** `jobs.sh` fails with `child setpgid ... Operation not permitted` in the agent shell, then the 20-minute timeout ends it. The close moves to m4.
