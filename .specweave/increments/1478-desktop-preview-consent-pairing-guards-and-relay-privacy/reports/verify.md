# Verify — 1478-desktop-preview-consent-pairing-guards-and-relay-privacy

FAIL · 2026-11-25T08:12:32.846Z · commands from config testing.commands

## Commands

- Working directory: . (config testing.commands)
### `python3 scripts/fleet-project-sync.py --self-test` → exit 0 (16s)

```
test_absent_and_idempotent (__main__.SafetyTests) ... ok
test_dirty_and_untracked_preserved (__main__.SafetyTests) ... ok
test_existing_empty_and_atomic_race_preserved (__main__.SafetyTests) ... ok
test_final_readback_detects_descendant_and_staging (__main__.SafetyTests) ... ok
test_incomplete_runtime_and_release_never_pass (__main__.SafetyTests) ... ok
test_legacy_fetch_repair_preserves_dirty_or_custom_checkouts (__main__.SafetyTests) ... ok
test_missing_or_diverged_upstream_is_preserved (__main__.SafetyTests) ... ok
test_new_and_legacy_clones_fetch_and_track_future_feature (__main__.SafetyTests) ... ok
test_offline_bundle_and_bad_digest (__main__.SafetyTests) ... ok
test_remote_drift_preserves_old_checkout (__main__.SafetyTests) ... ok
test_scoped_transport_preserves_identity_and_rejects_redirects (__main__.SafetyTests) ... ok
test_unpushed_commit_preserved (__main__.SafetyTests) ... ok
test_unsafe_paths_urls_and_symlinks (__main__.SafetyTests) ... ok

----------------------------------------------------------------------
Ran 13 tests in 16.370s

OK
```

- Working directory: . (config testing.commands)
### `python3 -m unittest discover -s tests -p test_handoff_evidence.py` → exit 0 (1s)

```
..............................................
----------------------------------------------------------------------
Ran 46 tests in 0.590s

OK
```

- Working directory: . (config testing.commands)
### `python3 scripts/release/timing.py --self-test` → exit 0 (0s)

```
.................
----------------------------------------------------------------------
Ran 17 tests in 0.142s

OK
recorded
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run verify:pr -- --jobs 1 --no-server` → exit 143 (1201s)

```

> verify:pr
> bash scripts/studio-verify/pr-gate.sh --jobs 1 --no-server

PR gate: HEAD 170d1bf79 against origin/main (merge base 2b7f17e8b); logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T//studio-pr-gate.XqOvAO
Stage 1: 18 jobs, 1 at a time
/Users/anton/.specwithcode/worktrees/specweave-umb/preview-pairing-relay-hardening/repositories/anton-abyzov/specwithcode/scripts/studio-verify/jobs.sh: child setpgid (6994 to 6994): Operation not permitted

[timeout after 20 min]
```

- Working directory: repositories/anton-abyzov/specwithcode (config testing.ownerCommands)
### `npm run test:server:sharded -- --shards 6 --out "$(mktemp -d)"` → exit 1 (1037s)

```

> test:server:sharded
> node scripts/release/test-sharded.mjs --shards 6 --out /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.Npw0AS0Sm2

Running the server suite as 6 shards; logs in /var/folders/jx/h60xy9hx45744vg4cqhx842r0000gn/T/tmp.Npw0AS0Sm2
SHARD  EXIT  SECONDS  FILES  TESTS  FAILED
1      0       781.2    232    3260        0
2      1       994.9    246    3728        1
3      0       959.1    247    2910        0
4      0       893.7    247    3635        0
5      0      1036.3    247    3529        0
6      0      1004.7    248    3248        0
failed: src/terminal/elevatedRun.test.ts
  src/terminal/elevatedRun.test.ts > administrator code-block runs ends the block, drops the ticket and removes the folder on SIGTERM: Error: Timed out after 15000ms waiting for runsDir cleanup and block exit
Server shards: shard 2 failed in 1036.3s
```

## Acceptance criteria

16/17 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-01 | x (tasks) | met | A preview page asking for clipboard read, notifications or location gets it only after the person allows it for that origin (remembered for the session); a frame whose origin is not `http` or `https` (`file:`, `data:`, `about:blank`, `about:srcdoc`) is refused without a prompt. The prompt names the full origin (scheme, host, port). A failed prompt blocks and is not remembered. Permission checks use the frame URL when Electron supplies it and fall back to the reported origin otherwise. Annotation selection, Escape, tool keys and recorded pointer and key input require trusted events. Enter attaches, Ctrl/Cmd+Enter sends when sending is enabled, and a trusted Attach click submits; the trusted-click test remains P-3. Other preview permissions keep their current answer. |
| AC-02 | x (tasks) | met | During annotation, the dispatch guard refuses direct `Input.*` and treats unreadable or more-than-four-level wrappers as input. The relay rejects `Target.sendMessageToTarget` regardless of annotation state. A tab can reach its page and debugger-announced child sessions, including frames and workers. On a tab's page and frame sessions, `Target.*` commands other than `setAutoAttach`, `detachFromTarget` of its own child and `getTargetInfo` of its own targets are refused, and so are `Browser.*` commands. Supported non-input commands and direct input after annotation ends remain available. `Runtime.evaluate` is not held (O-5). |
| AC-03 | x (tasks) | met | Preview guests run with `contextIsolation=true`; page script cannot reach `ipcRenderer`, `require` or the preload's own objects. App-window popups open externally only for http and https links. Editor schemes were allowed before #910 and are now denied, and `mailto:` stays denied as before (opening `mailto:` is owner decision O-8). The popup rule ships in #910, the isolation in #911. Must keep working: element picking, annotations, the human-input and recording channels of the pick preload, and http(s) links opened from the app window. |
| AC-04 |   | open | The desktop app counts its backend ready only when the listener proves it holds this launch's readiness secret; a listener answering 200 without the proof keeps readiness waiting. A normal local launch and a WSL launch still become ready. |
| AC-05 | x (tasks) | met | Push on a clean default branch that is ahead runs `push`, never `commit_push`, with and without an upstream; a dirty default branch keeps its commit actions. |
| AC-06 | x (tasks) | met | Concealed (SGR 8) terminal text is not drawn under the block cursor or decorated; visible text under the cursor still draws. |
| AC-07 | x (tasks) | met | Untargeted SSH onboarding that reports an environment already saved under another address fails with the known-address guard and leaves the registry unchanged; targeted SSH reconnects and new SSH hosts still register. |
| AC-08 | x (tasks) | met | The relay connection-attempt span omits the machine-label attribute. Its scoped tracer masks known machine labels in string attribute and event values, and masks known labels, recognized refusal text and approval codes in failure messages, stacks and causes within its traversal limit. The exporter-wide scrub remains E-6. What the person sees (`detail`, `message`, `deviceApprovalCode`), local spans and logs are unchanged. |
| AC-09 | x (tasks) | met | Hosts under `.lan`, `.localdomain`, `.corp`, `.home`, `.intranet`, `.private` (and the other RFC 6762 Appendix G names) are never sent to the favicon service, and a host whose labels include one of those names anywhere except its last two labels (`build.corp.example.com`) is private too; public hosts still are. Registrable domains spelled the same under a one-part suffix (`corp.com`, `home.page`) and look-alikes (`corporate.example.com`, `lanes.example.co.uk`) stay public. A registrable domain under a two-part public suffix, such as `corp.co.uk`, counts as private: a known false positive that only hides its favicon. The label list is a heuristic: internal zones with other names (`wiki.ops.example.com`) are not caught. |
| AC-10 | x (tasks) | met | On Android, the banner host and cleartext guard read the machine pairing actually contacts (`PairingLink.parse` after the same unwrap Connect does, so `?host=` and nested wrappers count), with hosts read by the same parser. `ws://` counts as cleartext. A link from another app with no readable address is refused, and so is a plain-http link from another app to a name with no dot (`http://build:3773`), since the phone's DNS search domain picks its machine; https, `localhost`, `.local` and private addresses keep their answers. Plain https links and manual entries (typed-in hosts still pair) keep today's answers. |
| AC-11 | x (tasks) | met | On API and hook paths, the request tracer receives a copy without the remote address or the `user-agent`, `forwarded`, `x-forwarded-for`, `x-real-ip`, `x-client-ip`, `x-cluster-client-ip`, `true-client-ip`, `fastly-client-ip`, `cf-connecting-ip`, `cf-connecting-ipv6` and `cf-pseudo-ipv4` headers. Route handlers still receive the original request. |
| AC-12 | x (tasks) | met | The relay refuses to relink an active environment under a different key with `EnvironmentLinkProofInvalid` (`descriptor_mismatch`, stage `validate_existing_link`). After consuming the replay nonces, the relay checks the active key before replacement, provisioning or writing the link. The link write independently rejects a different key on an active row. Before each ingress PUT attempt, the relay checks ownership and skips the PUT if it sees an active link under a different key. A refused link leaves the stored key, other accounts' links and tunnels unchanged. Relinking with the same key, relinking after an unlink and the same-machine replacement path still work. A machine whose key changed while its environment id survived (secret store reset) must be unlinked in Connect first; the server does not yet say so (E-2). |
| AC-13 | x (tasks) | met | When an environment and key link under a new account, the link upsert and the revocation of other accounts' active links for that environment and key run in one D1 batch, and the revocation applies only if the new row holds the proof key and is active. The credential insert follows the batch (E-11). Credentials belong to the key and stay. The previous account's tunnel and hostname stay in place on a move, as on main. Ordinary unlink removes DNS and can leave a tunnel with live connectors for later. Account deletion includes revoked links and disconnects live connectors to finish teardown. Ordering tunnel and DNS writes across accounts is follow-up F-1 (one serialized writer per environment). |
| AC-14 | x (tasks) | met | Account deletion removes a live host's tunnel by dropping its connectors and then deleting it, and frees the allocation; an ordinary unlink of a live host keeps today's behaviour (tunnel left for later). |
| AC-15 | x (tasks) | met | A queued APNs job whose activity recheck fails is skipped, not delivered. A queued Live Activity start is sent only if every machine in its content is still linked to that user under the same key. |
| AC-16 | x (tasks) | met | Android push data sent to Google carries no account user id; it carries `user_hash`, the lowercase hex SHA-256 of `<userId>:<deviceId>`. The phone does not check `user_hash` yet: `apps/android` reads no FCM data key, and the `apps/mobile` receiver still reads `user_id` (follow-up E-5). |
| AC-17 | x (tasks) | met | A Clerk webhook with a bad signature, a timestamp outside 5 minutes or no configured signing secret is refused and deletes nothing; a missing Svix header answers 401 and an unreadable body 400. A valid, fresh signed `user.deleted` runs relay account cleanup and retains the deletion marker. A fresh signed delivery that fails the event schema, or a `user.deleted` with a missing or blank user ID, answers 400. A failed replay check answers 500. A duplicate claimed `(svix-id, svix-timestamp)` answers 204 even if the first attempt failed; its replay record expires at the timestamp plus 300 s plus 60 s. Deletion errors return 500, and a retry signed with a new timestamp can run again. Other event types answer 204. The deletion marker blocks account-authenticated DPoP calls, token exchange and Clerk-bearer routes except `DELETE /v1/client/account`. The proof-only removal-status route checks the key. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-01 | done | clients | cd repositories/anton-abyzov/specwithcode/apps/web && node … |  |
| T-02 | done | clients | cd repositories/anton-abyzov/specwithcode/apps/web && node … |  |
| T-03 | done | clients | cd repositories/anton-abyzov/specwithcode/packages/client-r… |  |
| T-04 | done | clients | cd repositories/anton-abyzov/specwithcode/packages/shared &… |  |
| T-05 | done | clients | grep -q "host=" repositories/anton-abyzov/specwithcode/apps… |  |
| T-06 | done | desktop | cd repositories/anton-abyzov/specwithcode/apps/desktop && n… |  |
| T-07 | done | desktop | cd repositories/anton-abyzov/specwithcode/apps/desktop && n… |  |
| T-08 | done | desktop | cd repositories/anton-abyzov/specwithcode/apps/desktop && n… |  |
| T-09 | skipped | claude@anton-m5max-proled |  | R4 needs a readiness-proof route in apps/server and a contr… |
| T-10 | done | relay | cd repositories/anton-abyzov/specwithcode/infra/relay && np… |  |
| T-11 | done | relay | cd repositories/anton-abyzov/specwithcode/infra/relay && np… |  |
| T-12 | done | relay | cd repositories/anton-abyzov/specwithcode/infra/relay && np… |  |

11/12 done · 1 skipped · 0 claimed · 0 blocked · 0 stale · 0 open

### Skipped

- T-09 — R4 needs a readiness-proof route in apps/server and a contracts field, outside group D's files; follow-up E-1 in reports/follow-ups.md (claude@anton-m5max-proled)
