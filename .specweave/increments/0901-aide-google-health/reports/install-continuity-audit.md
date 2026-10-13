# 0901 historical install-continuity audit

Observed at: 2026-10-13T05:10:35.924205+00:00

## Verdict

The original update receipt remains **update-failed / held-for-safe-review**, with the intended 1.0.7 pointers retained. This independent historical audit does not convert that receipt into a successful install. The preservation failure is explained by newly created recovery-UI audit authentication records; it is not listener drift.

## Evidence and method

- Original receipt: `/Users/antonabyzov/.local/share/specweave-studio/verification/0901/install-live/update-20261013T045742Z.json`.
- Exact pre-restart backup: `/Users/antonabyzov/.specweave-studio/backups/pre-c95d3fd701d2-20261013T045939Z/statev2.sqlite`.
- Current database: `/Users/antonabyzov/.specweave-studio/m4/userdata/statev2.sqlite`.
- Both databases were opened read-only with explicit SQLite transactions. The backup's complete capture (schema, every typed table hash, legacy hashes and sequences) exactly equals the receipt's original complete prestate. The current schema is identical.
- Typed comparison preserves SQLite storage classes, including NULL, INTEGER, REAL, TEXT and BLOB. No credentials, row payloads, native IDs, prompts, client IPs or session IDs were written to this report.
- 46 of 54 tables retain exact typed counts and hashes. Every original row in all four orchestration event/receipt logs is typed-identical at its original row position. New log rows are append-only.
- All 351 original auth sessions remain. Every original non-heartbeat cell, including identity, scopes, method, expiry, revocation and client metadata, is typed-identical. Only 2 original `last_connected_at` values changed. All 229 original pairing-link rows remain typed-identical.
- Project tables and project/thread identities are unchanged. Changes in thread/provider projections belong to streams with appended events; all other projection stream hashes are exact. Projection cursor stable fields are exact; only sequence/time advances occurred. AUTOINCREMENT changes are limited to appended logs.

## Cause of the guard failure

At the helper's attempted-after observation (2026-10-13T05:03:45.251141Z), auth sessions had grown from 351 to 353 and pairing links from 229 to 232. New records are labeled `Read only recovery UI audit`. Subsequent audit activity added further records, recorded in the sanitized readback below. These additions alter both the auth invariant and authority-table counts; they exceed the existing-session heartbeat exception. The parent subsequently reported that the other active recovery chat confirmed these pairing records came from its UI audit and paused further live mutations. This provenance confirmation is relayed from that chat; the record labels/timestamps and preservation comparisons above were independently read from SQLite. These additions are not inferred from a desktop update.

A `provider-runtime.reconcile` receipt at 04:59:40.121Z recorded `provider-thread.updated`: one existing provider thread became `active → idle`, its timestamps advanced, and the enclosing thread timestamp followed. Source `ProviderRuntimeRecoveryService.ts:587-611,693` expressly emits this recovery transition. This is consistent with process-bound runtime recovery; the event alone does not establish whether shutdown or startup invoked reconciliation. Later `thread.metadata-updated` events changed one thread's `limitRecovery` and timestamp; two `thread.visited` events changed only the corresponding `lastVisitedAt` fields. At this audit snapshot there were five appended events and five matching command receipts in total.

The unchanged helper's `append_only_activity`/`carried_since` and `rows_carried_forward` logic allows these event-backed projection changes when original typed log prefixes remain exact, projection stream changes correspond to appended events, identity sets remain intact and auth/other protected tables are unchanged. This audit verifies that stream association and all historical log prefixes directly; it does not normalize auth summaries or bypass the failed guard.

## Pointer checks already observed

The live launcher, installation receipt and CLI wrapper hashes match the failed receipt's intended new hashes. Settings, environment identity and service LaunchAgent hashes remain identical to the original prestate. Installed version/source/archive were 1.0.7 / 54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f / 600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830. Runtime record named PID 47846. This report does not substitute those readings for a successful guarded install receipt.

## Proper retry route

Yes: after the competing audits explicitly confirm provenance and pause live auth/provider/session/metadata mutations, take a **fresh prestate** and reapply the **same immutable 1.0.7 archive using the unchanged released 54aa helper** under the parent's existing exclusive install reservation. The helper's `release_policy.validate_upgrade` permits equal versions (`incoming >= previous`). `publish_release` fully verifies both an existing destination and the newly staged release, then requires equal manifest bytes. The archive SHA-256 remains authoritative.

Retain every original failure receipt, the historical backup, the added auth records and this audit. Use new snapshot/output paths. Do not edit authority rows, relabel the old result, relax preservation comparisons, or enable migration allowances for this retry. Keep the existing bounded heartbeat exception only as already authorized; it permits bounded reconnects of existing supported sessions, not creation/revocation or client-metadata changes. The unchanged helper still requires unrelated listener PID stability, native work idle, exact process ownership/quiescence, full artifact hashes, coherent DB/auth proof, protected pointer/config identity and the same time budgets. A new refusal remains a refusal.

A successful retry would prove preservation of the fresh, explicitly accepted current baseline. This audit separately establishes preservation of the original historical data across the failed attempt; it does not erase the fact that concurrent auth additions caused that attempt to fail.

## Sanitized typed readback

```json
{
  "observedAt": "2026-10-13T05:10:35.924205+00:00",
  "tableCount": 54,
  "exactTypedTableCount": 46,
  "changedTables": [
    "auth_pairing_links",
    "auth_sessions",
    "orchestration_command_receipts",
    "orchestration_events",
    "orchestration_v2_projection_metadata",
    "orchestration_v2_projection_provider_threads",
    "orchestration_v2_projection_threads",
    "sqlite_sequence"
  ],
  "backupEqualsOriginalCompletePrestate": true,
  "fullSchemaUnchanged": true,
  "auth": {
    "table": "auth_sessions",
    "originalCount": 351,
    "currentCount": 354,
    "added": 3,
    "removed": 0,
    "originalRowsWithHeartbeatOnlyChange": 2,
    "newRows": [
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "browser-session-cookie",
        "issued_at": "2026-10-13T05:02:06.059Z",
        "last_connected_at": "2026-10-13T05:02:06.297Z",
        "revoked_at": "2026-10-13T05:02:29.431Z",
        "client_surface": null,
        "client_app_version": null
      },
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "browser-session-cookie",
        "issued_at": "2026-10-13T05:03:23.651Z",
        "last_connected_at": "2026-10-13T05:03:45.859Z",
        "revoked_at": "2026-10-13T05:04:32.459Z",
        "client_surface": "web",
        "client_app_version": "1.0.7"
      },
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "browser-session-cookie",
        "issued_at": "2026-10-13T05:05:12.632Z",
        "last_connected_at": "2026-10-13T05:05:32.599Z",
        "revoked_at": null,
        "client_surface": "web",
        "client_app_version": "1.0.7"
      }
    ]
  },
  "pairings": {
    "table": "auth_pairing_links",
    "originalCount": 229,
    "currentCount": 233,
    "added": 4,
    "removed": 0,
    "originalRowsWithHeartbeatOnlyChange": 0,
    "newRows": [
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "one-time-token",
        "created_at": "2026-10-13T04:59:55.495Z",
        "consumed_at": null,
        "revoked_at": "2026-10-13T05:02:00.045Z"
      },
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "one-time-token",
        "created_at": "2026-10-13T05:02:05.767Z",
        "consumed_at": "2026-10-13T05:02:06.045Z",
        "revoked_at": null
      },
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "one-time-token",
        "created_at": "2026-10-13T05:03:23.511Z",
        "consumed_at": "2026-10-13T05:03:23.650Z",
        "revoked_at": null
      },
      {
        "labelCategory": "Read only recovery UI audit",
        "method": "one-time-token",
        "created_at": "2026-10-13T05:05:12.583Z",
        "consumed_at": "2026-10-13T05:05:12.628Z",
        "revoked_at": null
      }
    ]
  },
  "historicalLogs": [
    {
      "table": "orchestration_events",
      "preservedOriginalRows": 17740,
      "appendedRows": 5
    },
    {
      "table": "orchestration_command_receipts",
      "preservedOriginalRows": 2638,
      "appendedRows": 5
    },
    {
      "table": "orchestration_v2_events",
      "preservedOriginalRows": 0,
      "appendedRows": 0
    },
    {
      "table": "orchestration_v2_command_receipts",
      "preservedOriginalRows": 0,
      "appendedRows": 0
    }
  ],
  "changedProjectionStreamsExplainedByAppendedEvents": true,
  "projectionChanges": [
    {
      "table": "orchestration_v2_projection_threads",
      "columns": [
        "updated_at",
        "payload_json"
      ],
      "payloadChangedKeys": [
        "limitRecovery",
        "updatedAt"
      ],
      "safeChanges": {
        "updated_at": [
          "2026-10-13T04:56:05.738Z",
          "2026-10-13T05:09:46.348Z"
        ]
      }
    },
    {
      "table": "orchestration_v2_projection_threads",
      "columns": [
        "updated_at",
        "payload_json"
      ],
      "payloadChangedKeys": [
        "updatedAt"
      ],
      "safeChanges": {
        "updated_at": [
          "2026-10-13T01:18:52.324Z",
          "2026-10-13T04:59:40.121Z"
        ]
      }
    },
    {
      "table": "orchestration_v2_projection_threads",
      "columns": [
        "payload_json"
      ],
      "payloadChangedKeys": [
        "lastVisitedAt"
      ],
      "safeChanges": {}
    },
    {
      "table": "orchestration_v2_projection_threads",
      "columns": [
        "payload_json"
      ],
      "payloadChangedKeys": [
        "lastVisitedAt"
      ],
      "safeChanges": {}
    },
    {
      "table": "orchestration_v2_projection_provider_threads",
      "columns": [
        "status",
        "updated_at",
        "payload_json"
      ],
      "payloadChangedKeys": [
        "status",
        "updatedAt"
      ],
      "safeChanges": {
        "status": [
          "active",
          "idle"
        ],
        "updated_at": [
          "2026-10-13T01:18:50.032Z",
          "2026-10-13T04:59:40.121Z"
        ]
      }
    },
    {
      "table": "orchestration_v2_projection_metadata",
      "columns": [
        "last_sequence",
        "updated_at"
      ],
      "payloadChangedKeys": [],
      "safeChanges": {
        "last_sequence": [
          17740,
          17745
        ],
        "updated_at": [
          "2026-10-13T04:56:05.750Z",
          "2026-10-13T05:09:46.598Z"
        ]
      }
    }
  ],
  "events": [
    {
      "type": "provider-thread.updated",
      "at": "2026-10-13T04:59:40.121Z",
      "actor": "server"
    },
    {
      "type": "thread.metadata-updated",
      "at": "2026-10-13T05:04:34.412Z",
      "actor": "server"
    },
    {
      "type": "thread.visited",
      "at": "2026-10-13T05:05:39.741Z",
      "actor": "server"
    },
    {
      "type": "thread.visited",
      "at": "2026-10-13T05:06:39.334Z",
      "actor": "server"
    },
    {
      "type": "thread.metadata-updated",
      "at": "2026-10-13T05:09:46.348Z",
      "actor": "server"
    }
  ],
  "projectTablesExact": [
    "project_connection_calls",
    "project_connections",
    "project_context_deliveries",
    "project_environment_preparations",
    "project_memory",
    "project_memory_revisions",
    "project_plans",
    "projection_projects"
  ],
  "sqliteSequenceOnlyAppendedLogCounters": true
}
```

No live service, auth session, provider turn, listener or database was mutated. The only file written by this audit is this report.


## Successful guarded reapply — independent historical receipt review

Reviewed at 2026-10-13T05:17:11.170905+00:00. The unchanged released helper successfully reapplied the identical 1.0.7 archive against a fresh prestate. The original failed receipt remains unchanged and retained.

- Positive receipt: `/Users/antonabyzov/.local/share/specweave-studio/verification/0901/install-live/update-20261013T051050Z.json`; SHA-256 `f7a17bc5440f971d684bdb94d74ed511dffdcb1f83c0a3ecde09a6216fcfe3f4`. Its `before` observation is 2026-10-13T05:11:29.369576+00:00; restart began 2026-10-13T05:12:44.734303+00:00; `after` observation is 2026-10-13T05:14:14.184612+00:00.
- Independently compared the actual saved values: complete `rows` objects and full `databaseCapture` objects are exactly equal before/after; schema, typed hashes, legacy hashes and sequences therefore match. Settings, environment identity, LaunchAgent and unrelated listener inventories are equal. The receipt is `phase=verified`, `completeDatabaseContinuity=verified`, `rowsByteIdentical=true`; no inference ran.
- Runtime PID changed from 47846 to 8552; source remains `54aa7e7d7ba1c59bb2b7af2f31f7f6ab86a0e06f` and archive remains `600a4c54e381cbaed29c7e530e19ae424e70ac80ba5da7d41104566b97951830`.
- `/Users/antonabyzov/.local/share/specweave-studio/verification/0901/install-live/live-installed.json` at 2026-10-13T05:14:44.207097+00:00 binds to the positive receipt by its verified SHA-256 and records live process/path/runtime checks, HTTP 200, production JavaScript asset HTTP 200, installed desktop bundle version 1.0.7 and a process running from that bundle path. The saved verifier code checks those facts. Its desktop evidence establishes the installed version plus a running process at that path; it does not independently introspect the loaded Electron process version.
- `/Users/antonabyzov/.local/share/specweave-studio/verification/0901/install-live/scheduler-restored.json` at 2026-10-13T05:15:08.400129+00:00 records the restored original scheduler plist/config and normal installed state for version/source above. Its `lastInstall` links to this exact positive receipt, and failed receipts remain retained. This independently verifies receipt consistency; restoration byte equality is reported by that saved restoration receipt.

This establishes a positive guarded install and subsequent runtime readback. Normal activity has resumed; this review deliberately did not query current DB/auth state or assert that the live database remains equal to the historical snapshot. `googleAccessVerified=false` in the runtime readback correctly leaves Google consent/project/API proof to its separate check.
