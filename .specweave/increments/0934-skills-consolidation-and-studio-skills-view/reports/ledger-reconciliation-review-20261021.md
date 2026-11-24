# 0934 ledger reconciliation review

Read-only audit on October 21, 2026. No ledger, metadata, task definition, source, skill tree, backup, deployment or process was changed. This report is the only write. Parent owns T-09 live publication.

## Findings

T-05 is done under the installed SpecWeave 3.1.4 CLI. Running `specweave task list 0934 --json` reports 9 done, 1 stale, 0 blocked, 0 malformed. Importing the installed `foldLedgerFile` independently confirms that the later T-05 block event is ignored with reason `already done`. T-09 is stale under `codex-0934-publication`, pending actual publication proof; stale time alone grants no takeover authority.

The ignored block is present at /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/ledger.jsonl:16. Its existence explains the raw-event audit, but the authoritative fold treats done as terminal for block/claim/release. The implementation is /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/src/core/tasks/ledger.ts:317. The installed implementation at /Users/antonabyzov/.nvm/versions/node/v22.20.0/lib/node_modules/specweave/dist/src/core/tasks/ledger.js:281 behaves identically.

Repeating `specweave task done T-05 0934 --evidence ...` returns before appending or running tests, including with --force. This is explicit at /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/src/cli/commands/task.ts:221. Claim refuses terminal tasks, and release reports nothing to release. There is no need to bypass those safeguards or manually append a fabricated task event. T-08 and T-10 already record the genuine restoration and hygiene work using separate task-done events.

## Supported reconciliation and close path

Append an increment note with `specweave note "T-05 block was ignored by the terminal fold; T-08 restored the used skill and T-10 reconciled hygiene; see <absolute report paths>" 0934`. The supported note command appends an ordinary note without changing task state, as implemented at /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/src/cli/commands/pickup.ts:192. Preserve the older block as historical evidence.

After finishing live byte/version/description/hash validation, record T-09 with `specweave task done T-09 0934 --run "<actual acceptance command>" --evidence "<actual receipt paths>"` under the resuming parent's reconciled identity. Confirm 10/10 done with `specweave task list 0934 --json`, run scoped `specweave verify 0934` using the reviewed command manifest, perform a fresh-context review, then run `specweave complete 0934` without --reason or --skip-validation.

The completed metadata predates T-08/T-09/T-10. `complete` currently returns success immediately when metadata already says completed, before validating the report, at /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/specweave/src/core/increment/status-commands.ts:319. Thus the explicit fresh verify and review are required evidence; a second complete command cannot itself prove them. Do not edit metadata to manufacture a new transition. Retain the successful command output and the explicit fresh verify/review receipts.

## Existing verification scope

The current saved 0932 verify is green from October 21, 2026, 2:50 AM EDT. The current saved 0933 verify is green from October 21, 2026, 2:30 AM EDT. The current saved 0934 verify is from October 20, 2026, 3:20 AM EDT and predates the added tasks; it is not final close evidence for this reconciliation. The prepared scoped manifest is /Users/antonabyzov/Projects/github/specweave-umb/.specweave/increments/0934-skills-consolidation-and-studio-skills-view/reports/scoped-verify-20261021-command-manifest.json. Its corrections preserve the used asc-build-lifecycle skill instead of enforcing the obsolete contrary T-05 Test clause, and preserve the registry's separate auto-version policy.

No source/CI/deployment status is substituted for T-09 live publication proof. No crawler rollout was repeated.

Verify and close 0934
