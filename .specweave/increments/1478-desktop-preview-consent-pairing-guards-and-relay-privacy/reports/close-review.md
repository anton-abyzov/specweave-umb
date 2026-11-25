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

## Close on m4

Added on m4 on November 25, 2026. The review text above is left as written.

**Code under test:** the SpecWithCode worktree was detached at `origin/main` `868401f77`, which contains #909, #910, #911, #912, #936 and #938.

**Verify:** four `specweave verify` runs. Run 4 passed, at 11:15 UTC under the heavy-check gate, with every command at exit 0. In it, `verify:pr` took 779 s and all six server shards passed (20,512 tests).

Runs 1 to 3 failed at load 13 to 28, while another session's verify used the machine. Every failure was outside 1478's task Files, and each failing file passed when run on its own:

- **`scripts/linux-update-helper.test.ts`:** fails on mode `0o111`. The cause is the worktree checkout under umask 077: `apps/desktop/resources/linux/update-helper` is `100755` in the index but was `0700` on disk. `chmod 755` fixed it with no git diff, and the file then passed alone, 14 of 14.
- **`src/fleet/folderTransfer/twoServer.lan.test.ts`:** failed "ends the generation on both machines within a second". Passed alone, 49 of 49.
- **`src/assets/AssetAccess.test.ts`:** two tests hit the 120 s timeout in runs 2 and 3. Passed alone, 41 of 41.
- **`src/vcs/GitVcsDriverCore.test.ts`:** two tests hit the 120 s timeout in run 3. Passed alone, 171 of 171.
- **`src/project/knowledge/ProjectKnowledge.test.ts`:** three tests hit the 120 s timeout in run 3. Passed alone, 15 of 15.

Run 1 also hit the 20-minute limit on the server shards, so later runs used `--timeout 45`.

**AC-04:** moved out of the checklist in umbrella `96913acaf9`. Its text is kept unchanged under "Deferred to follow-up E-1", marked undelivered and unverified. T-09 stays skipped.

**Final review:** GPT-6.2 Sol on Codex, after Gemini 4 Neon was out of usage on Cursor and on Copilot Enterprise.

- Round 1 gave fix first:
  - Scope and Approach said R4 shipped.
  - AC-12 needed a same-account qualifier, and it overstated tunnel safety on a late refusal.
  - AC-10 missed malformed percent escapes.
  - AC-15 missed the key-change rebuild.

  Fixed in `3489b6feed`.
- Round 2 gave fix first:
  - Scope's red-and-green claim was too broad, since R10 is still pending Android CI and R17's red is by absence.
  - AC-15's skip condition was missing.
  - AC-10's exception was too broad.

  Fixed in `2b0b93fded`.
- Round 3 gave `Verdict: ship`, no findings. It is recorded after verify as `reports/reviews/review-gpt-6.2-sol-1.md`.
