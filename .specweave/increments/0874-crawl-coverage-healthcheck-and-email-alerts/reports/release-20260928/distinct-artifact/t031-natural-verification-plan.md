# T031 natural production verification

The frozen helper is `t031-natural-proof.cjs`, schema3, SHA256 `2b3de2a8d38b29673b7d1a4239a099dfa9acfb097208cb0d447c31e17e4b66fc`. Twenty-one offline tests cover positive settlement and identity, privacy, path, old-version target, deprecation, runtime/sweep, counter and incomplete-publication failures. No tests make network calls.

The authoritative baseline is `t031-natural-baseline-v3.json`. It captures the exact existing pending item set:22 incoming tuple hashes,10 existing Submission identities,19 item-to-Skill matches representing7 distinct existing Skills. The earlier schema1/2 baselines and helpers are retained, not rewritten. The baseline is mode0600 and contains no raw repository names, source IDs, paths, labels, user IDs, Skill IDs, version IDs, contents or credentials. All later query inputs are hashes; the pending page is not needed to rediscover those identities after normal advancement.

The reader performs only existing SSH checkpoint/container reads and a bounded PostgreSQL repeatable-read READ ONLY transaction. It verifies the database identity and transaction_read_only, limits rows, sets a15-second statement timeout and30-second-scale SSH/connect boundaries, then rolls back. It does not trigger a scheduler, intake, scanner, evaluator, heartbeat, reset or other mutation. The first schema3 post-baseline read successfully exercised hash-predicate SQL and found0 new canonical rows. The strict verifier exited2 on those real pre-release receipts, correctly withholding success.

Root owns the release, version-specific passive tail and runtime guards. After reviewed source, all required CI and guarded Worker-only release, allow the existing scheduler to retry normally. Read one natural snapshot with a fresh output filename:

```sh
/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /tmp/cc-work-release-20260928/0874/t031-natural-proof.cjs --readback /tmp/cc-work-release-20260928/0874/t031-natural-baseline-v3.json /tmp/cc-work-release-20260928/0874/t031-natural-readback-final.json
```

Then compute the strict verdict:

```sh
/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin/node /tmp/cc-work-release-20260928/0874/t031-natural-proof.cjs --verify /tmp/cc-work-release-20260928/0874/t031-natural-baseline-v3.json /tmp/cc-work-release-20260928/0874/t031-natural-readback-final.json /tmp/cc-work-release-20260928/0874/t031-natural-verdict-final.json
```

All output creation is exclusive: never overwrite an existing receipt. On an incomplete readback, keep it and use a new filename at a later natural cadence. `--compare` produces a report and its exit0 means report generation only. Never wire `--compare` to `task done`. `--verify` exits2 unless all six gates are true:

1. Ten old Submission identity/name/path/user fields remain unchanged; existing links and seven existing Skill identity/name/display-name/path/slug/privacy/tenant/deprecation fields remain unchanged. Every baseline version remains attached to its old Skill. Timestamps, metrics and normal state advancement are outside the protected fingerprints. A newly attached link on one of the originally unlinked rows must match its own artifact and public scope.
2. All22 exact incoming canonical tuples exist once, each in a distinct new Submission rather than one of the10 old rows.
3. All22 durable labels match the author's exact formula: `originalName + " (" + (artifactPath || "SKILL.md") + ")"`, preserving path case.
4. Linked Skills belong to each exact new artifact, are PUBLIC/tenantless, do not reuse any old linked Skill and are not shared between two distinct new tuples.
5. All22 are absent from unresolved payload and have positive accepted-key evidence or same-sweep checkpoint advancement. The crawler/scanner identities and nondecreasing historical loss/error counters remain protected.
6. Each outcome is either PUBLISHED with its actual `Skill.currentVersion` present in a persisted SkillVersion on that same Skill and not deprecated, or an explicit scanner rejection (REJECTED, TIER1_FAILED or BLOCKED). A queued/scanning row proves settled intake separately, but not complete publication. Existing scanner policy is not bypassed to make this gate green.

Final closure additionally requires root's exact merged source/CI receipt, immutable artifact and active Worker identity, unchanged six-consumer/private/public/queue guards, and a natural final-version intake tail showing no continued identity-guard loop. The helper's proof alone cannot establish deployment or version attribution. Public readback of genuinely published results is separate and must remain read-only. No manual replay/reset, content export, DB repair, backfill, privacy change, crawler/scanner restart or old-image rollback is authorized by this plan. T017/T027 full-sweep and corpus-coverage claims remain open.
