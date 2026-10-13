# Product continuation diagnostic: specweave

This is a deliberately partial executable diagnostic for the real M4-to-M1/M3
product handoff. It is not a production-module fix. Both destinations must
start from this same partial source; do not send a completed destination's
code to the other destination.

Decision: `APPEND_ORDER_LATEST_RECOGNIZED_EVENT`.

`unfinishedTaskIds(taskIds, events)` returns unfinished task IDs in the
supplied task-ID order. Events have the ledger shape `{ t, e, at? }`. The latest
recognized event for a known task in array append order wins: `done` and `skip`
settle it; `claim`, `release`, and `block` make it unfinished. A task with no
recognized event is unfinished. Ignore unknown event types and unknown task
IDs. Timestamps are metadata, never a sorting key. Preserve task IDs, input
arrays, and event objects, and always return a fresh result array.

## Source checkpoint

- Source root branch: `codex/0907-product-specweave`.
- Root base commit: `99e16cf4eba879f1b163b894b37ec4cc3908b677`.
- Nested repository: `repositories/anton-abyzov/specweave`.
- Nested base commit: `a7bd43cabd0b241cea9a3c7cd8bc22fbe3ba9c9a`.
- Nested diagnostic commit: 3ec9650a889f1b71f081e63f0471e8503224c507.
- Implementation: `scripts/diagnostics/handoff/0907-product-specweave/case.mjs`.
- Frozen test: `scripts/diagnostics/handoff/0907-product-specweave/case.check.mjs`.
- Frozen test SHA-256: `f2492ebbe484a0926369048ee9519f14f1fa2f21d2e836bbb95a5f4d87d3d55b`.
- Frozen README SHA-256: `8a3be8a89d7193981ed0073c1736647972317ded457276afa874840f43302ac0`.

Actual M4 source execution used Node `v22.20.0` with
`--test --test-reporter=tap scripts/diagnostics/handoff/0907-product-specweave/case.check.mjs` from the nested repository. It exited
`1` with `4` passing tests and `3` failing assertion tests.
Observed failing tests: a later claim reopens a completed task; release and block reopen previously skipped or completed tasks; append order wins over contradictory timestamp metadata.
This red result is intentional source state, not a successful implementation.

## Remaining destination action

Replace the ever-completed set with append-order state evaluation so later claim, release, or block events reopen a task. Edit only `scripts/diagnostics/handoff/0907-product-specweave/case.mjs`. Preserve the test, README,
this durable decision, other project files, and all input objects. Use a fresh
owned branch `codex/0907-product-specweave-m1` on M1 or
`codex/0907-product-specweave-m3` on M3 before editing. After the unchanged tests pass,
commit only the implementation with exact message
`0907: Complete specweave handoff diagnostic`. Do not push or merge from the worker.
The supervising product workflow owns publication and acceptance records.

Discover the existing Node 22 runtime; do not install or change a global runtime:

```sh
SW_DIAGNOSTIC_NODE="$HOME/.local/share/specweave/node22/bin/node"
if [ ! -x "$SW_DIAGNOSTIC_NODE" ]; then
  SW_DIAGNOSTIC_NODE="$HOME/.nvm/versions/node/v22.20.0/bin/node"
fi
"$SW_DIAGNOSTIC_NODE" --version
```

Proceed only if that executable exists and reports major version 22. Run from
the actual product-created nested workspace:

```sh
"$SW_DIAGNOSTIC_NODE" --test --test-reporter=tap scripts/diagnostics/handoff/0907-product-specweave/case.check.mjs
```

Done means the same frozen tests exit zero with every test passing, the test
and README hashes remain unchanged, only `case.mjs` changes in the nested
commit, and the source checkpoint/decision is identified in the continuation
result. Use no secrets, `.env`, account settings, providers, installs, services,
production imports, migrations, or network. No additional local configuration
is required for these pure Node diagnostics. Ignored runtime environments do
not travel with Git; full app worktrees require separate opt-in provisioning.
